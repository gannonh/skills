#!/usr/bin/env python3
"""Validate an Open Knowledge Format bundle.

Usage:
    python okf/scripts/validate_okf.py [repo_root]
    python okf/scripts/validate_okf.py --docs path/to/docs
    python okf/scripts/validate_okf.py . --level editorial --profile documentation
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - exercised only when PyYAML is absent
    yaml = None


RESERVED_NAMES = {"index.md", "log.md"}
LEVELS = ("conformance", "repository", "editorial")
PROFILES = ("documentation", "software-project", "research", "custom")
STATUS_VALUES = {"draft", "stable", "deprecated"}
DATE_HEADING_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})(?:\s|$)")
ANY_DATE_HEADING_RE = re.compile(r"^##\s+(\S+)")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
FOOTNOTE_REF_RE = re.compile(r"\[\^([^\]]+)\]")
FOOTNOTE_DEF_RE = re.compile(r"^\[\^([^\]]+)\]:", re.MULTILINE)
URL_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
CITATIONS_HEADING_RE = re.compile(r"^#{1,6}\s+Citations\s*$", re.MULTILINE | re.IGNORECASE)


@dataclass
class ValidationResult:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass
class Concept:
    path: Path
    rel: str
    frontmatter: dict[str, Any]
    body: str


def validate_bundle(
    docs_dir: Path,
    *,
    strict_links: bool = False,
    level: str = "repository",
    profile: str = "documentation",
    today: date | None = None,
) -> ValidationResult:
    if level not in LEVELS:
        raise ValueError(f"Unknown validation level: {level}")
    if profile not in PROFILES:
        raise ValueError(f"Unknown repository profile: {profile}")

    docs_dir = docs_dir.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    concepts: list[Concept] = []
    current_date = today or date.today()

    if not docs_dir.exists():
        return ValidationResult([f"Missing OKF docs directory: {docs_dir}"], warnings)
    if not docs_dir.is_dir():
        return ValidationResult([f"OKF docs path is not a directory: {docs_dir}"], warnings)

    if level in {"repository", "editorial"} and not (docs_dir / "index.md").exists():
        errors.append("Missing repository index: index.md")

    for path in sorted(docs_dir.rglob("*.md")):
        rel = _rel(path, docs_dir)
        if path.name in RESERVED_NAMES:
            _validate_reserved_file(path, docs_dir, rel, errors, warnings, level)
            continue
        concept = _validate_concept_file(path, docs_dir, rel, errors, warnings, level)
        if concept is not None:
            concepts.append(concept)

    broken_links, inbound = _inspect_local_links(docs_dir)
    if strict_links:
        errors.extend(broken_links)
    else:
        warnings.extend(broken_links)

    if level == "editorial":
        _run_editorial_checks(concepts, inbound, current_date, warnings)

    return ValidationResult(errors, warnings)


def _validate_concept_file(
    path: Path,
    docs_dir: Path,
    rel: str,
    errors: list[str],
    warnings: list[str],
    level: str,
) -> Concept | None:
    text = path.read_text(encoding="utf-8")
    frontmatter, body, parse_error = _split_frontmatter(text)
    if parse_error:
        errors.append(f"{rel}: {parse_error}")
        return None
    if frontmatter is None:
        errors.append(f"{rel}: missing YAML frontmatter")
        return None

    concept_type = frontmatter.get("type")
    if not isinstance(concept_type, str) or not concept_type.strip():
        errors.append(f"{rel}: missing non-empty frontmatter field 'type'")

    _validate_v02_families(frontmatter, concept_type, rel, errors)

    if level in {"repository", "editorial"}:
        generated = frontmatter.get("generated")
        if "timestamp" in frontmatter and generated is None:
            warnings.append(f"{rel}: legacy v0.1 'timestamp' is superseded by generated.at")

    return Concept(path=path, rel=rel, frontmatter=frontmatter, body=body)


def _validate_v02_families(
    frontmatter: dict[str, Any],
    concept_type: Any,
    rel: str,
    errors: list[str],
) -> None:
    generated = frontmatter.get("generated")
    if generated is not None:
        if not isinstance(generated, dict):
            errors.append(f"{rel}: 'generated' must be a mapping")
        else:
            _require_nonempty_string(generated, "by", rel, "generated", errors)
            if "at" in generated and not _is_iso_datetime(generated["at"]):
                errors.append(f"{rel}: generated.at must be an ISO 8601 datetime")

    verified = frontmatter.get("verified")
    if verified is not None:
        events = verified if isinstance(verified, list) else [verified]
        if not isinstance(verified, (dict, list)):
            errors.append(f"{rel}: 'verified' must be a mapping or list of mappings")
        else:
            for index, event in enumerate(events):
                label = f"verified[{index}]"
                if not isinstance(event, dict):
                    errors.append(f"{rel}: {label} must be a mapping")
                    continue
                _require_nonempty_string(event, "by", rel, label, errors)
                if "at" not in event or not _is_iso_datetime(event.get("at")):
                    errors.append(f"{rel}: {label}.at must be an ISO 8601 datetime")

    status = frontmatter.get("status")
    if status is not None and status not in STATUS_VALUES:
        errors.append(f"{rel}: status must be one of draft, stable, deprecated")

    stale_after = frontmatter.get("stale_after")
    if stale_after is not None and not _is_iso_date(stale_after):
        errors.append(f"{rel}: stale_after must use YYYY-MM-DD")

    sources = frontmatter.get("sources")
    if sources is not None:
        if not isinstance(sources, list):
            errors.append(f"{rel}: 'sources' must be a list")
        else:
            source_ids: set[str] = set()
            for index, source in enumerate(sources):
                label = f"sources[{index}]"
                if not isinstance(source, dict):
                    errors.append(f"{rel}: {label} must be a mapping")
                    continue
                _require_nonempty_string(source, "resource", rel, label, errors)
                source_id = source.get("id")
                if source_id is not None:
                    if not isinstance(source_id, str) or not source_id.strip():
                        errors.append(f"{rel}: {label}.id must be a non-empty string")
                    elif source_id in source_ids:
                        errors.append(f"{rel}: duplicate source id '{source_id}'")
                    else:
                        source_ids.add(source_id)
                if "last_modified" in source and not _is_iso_date(source["last_modified"]):
                    errors.append(f"{rel}: {label}.last_modified must use YYYY-MM-DD")
                if "usage_count" in source and not isinstance(source["usage_count"], int):
                    errors.append(f"{rel}: {label}.usage_count must be an integer")
                if "usage_window" in source:
                    _validate_usage_window(source["usage_window"], rel, f"{label}.usage_window", errors)

    if "usage_window" in frontmatter:
        _validate_usage_window(frontmatter["usage_window"], rel, "usage_window", errors)

    if concept_type == "Attested Computation":
        _require_nonempty_string(frontmatter, "runtime", rel, "frontmatter", errors)
        parameters = frontmatter.get("parameters")
        if parameters is not None:
            if not isinstance(parameters, list):
                errors.append(f"{rel}: parameters must be a list")
            else:
                for index, parameter in enumerate(parameters):
                    if not isinstance(parameter, dict):
                        errors.append(f"{rel}: parameters[{index}] must be a mapping")
                        continue
                    _require_nonempty_string(parameter, "name", rel, f"parameters[{index}]", errors)
                    _require_nonempty_string(parameter, "type", rel, f"parameters[{index}]", errors)
                    if "required" in parameter and not isinstance(parameter["required"], bool):
                        errors.append(f"{rel}: parameters[{index}].required must be boolean")
        for field in ("executor", "attester"):
            value = frontmatter.get(field)
            if value is not None:
                if not isinstance(value, dict):
                    errors.append(f"{rel}: {field} must be a mapping")
                else:
                    _require_nonempty_string(value, "resource", rel, field, errors)


def _validate_usage_window(value: Any, rel: str, label: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{rel}: {label} must be a mapping")
        return
    for key in ("from", "to"):
        if key not in value or not _is_iso_date(value.get(key)):
            errors.append(f"{rel}: {label}.{key} must use YYYY-MM-DD")


def _require_nonempty_string(
    mapping: dict[str, Any],
    key: str,
    rel: str,
    label: str,
    errors: list[str],
) -> None:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{rel}: {label}.{key} must be a non-empty string")


def _validate_reserved_file(
    path: Path,
    docs_dir: Path,
    rel: str,
    errors: list[str],
    warnings: list[str],
    level: str,
) -> None:
    text = path.read_text(encoding="utf-8")

    if path.name == "index.md":
        frontmatter, _body, parse_error = _split_frontmatter(text)
        if parse_error:
            errors.append(f"{rel}: {parse_error}")
            return
        if frontmatter is not None:
            allowed_root_index = path == docs_dir / "index.md" and set(frontmatter.keys()) <= {"okf_version"}
            if not allowed_root_index:
                errors.append(f"{rel}: reserved index.md may contain only root-level okf_version frontmatter")
            elif level in {"repository", "editorial"}:
                version = frontmatter.get("okf_version")
                if version is not None and str(version) != "0.2":
                    warnings.append(f"{rel}: declares OKF {version}; this skill targets v0.2")
        elif path == docs_dir / "index.md" and level in {"repository", "editorial"}:
            warnings.append("index.md: consider declaring okf_version: \"0.2\"")
        return

    if path.name == "log.md":
        _validate_log_file(path, rel, errors)


def _validate_log_file(path: Path, rel: str, errors: list[str]) -> None:
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = ANY_DATE_HEADING_RE.match(line)
        if match and not DATE_HEADING_RE.match(line):
            errors.append(f"{rel}:{line_number}: log date headings must use YYYY-MM-DD")


def _run_editorial_checks(
    concepts: list[Concept],
    inbound: dict[str, int],
    current_date: date,
    warnings: list[str],
) -> None:
    titles: dict[str, list[str]] = {}

    for concept in concepts:
        frontmatter = concept.frontmatter
        title = frontmatter.get("title")
        description = frontmatter.get("description")

        if not isinstance(title, str) or not title.strip():
            warnings.append(f"{concept.rel}: missing recommended title")
        else:
            titles.setdefault(title.strip().casefold(), []).append(concept.rel)

        if not isinstance(description, str) or not description.strip():
            warnings.append(f"{concept.rel}: missing recommended description")

        if not concept.body.strip():
            warnings.append(f"{concept.rel}: concept body is empty")

        if "timestamp" in frontmatter:
            warnings.append(f"{concept.rel}: migrate legacy timestamp to generated.at when provenance is known")

        if CITATIONS_HEADING_RE.search(concept.body):
            warnings.append(f"{concept.rel}: legacy # Citations section is superseded by sources and keyed footnotes")

        stale_after = frontmatter.get("stale_after")
        stale_date = _as_date(stale_after)
        if stale_date is not None and current_date >= stale_date:
            warnings.append(f"{concept.rel}: stale_after {stale_date.isoformat()} has passed")

        source_ids = {
            source.get("id")
            for source in frontmatter.get("sources", [])
            if isinstance(source, dict) and isinstance(source.get("id"), str)
        }
        footnote_ids = set(FOOTNOTE_REF_RE.findall(concept.body)) | set(FOOTNOTE_DEF_RE.findall(concept.body))
        for footnote_id in sorted(footnote_ids - source_ids):
            warnings.append(f"{concept.rel}: footnote '{footnote_id}' has no matching sources[].id")

        if inbound.get(concept.rel, 0) == 0:
            warnings.append(f"{concept.rel}: concept has no inbound local links")

    for duplicate_paths in titles.values():
        if len(duplicate_paths) > 1:
            warnings.append(f"Duplicate title across concepts: {', '.join(sorted(duplicate_paths))}")


def _split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str, str | None]:
    if not text.startswith("---\n") and text.strip() != "---":
        return None, text, None

    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None, text, None

    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line == "---":
            end_index = index
            break

    if end_index is None:
        return None, text, "unterminated YAML frontmatter"

    raw = "\n".join(lines[1:end_index])
    body = "\n".join(lines[end_index + 1 :])
    if yaml is not None:
        try:
            parsed = yaml.safe_load(raw) if raw.strip() else {}
        except Exception as exc:
            return None, body, f"invalid YAML frontmatter: {exc}"
        if parsed is None:
            parsed = {}
        if not isinstance(parsed, dict):
            return None, body, "frontmatter must be a YAML mapping"
        return parsed, body, None

    parsed, error = _parse_minimal_yaml_mapping(raw)
    return parsed, body, error


def _parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str | None]:
    """Backward-compatible helper retained for callers of the original validator."""
    parsed, _body, error = _split_frontmatter(text)
    return parsed, error


def _parse_minimal_yaml_mapping(raw: str) -> tuple[dict[str, Any] | None, str | None]:
    parsed: dict[str, Any] = {}
    for line_number, line in enumerate(raw.splitlines(), start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith((" ", "\t", "-")):
            return None, "nested YAML requires PyYAML"
        if ":" not in line:
            return None, f"invalid YAML frontmatter near line {line_number}"
        key, value = line.split(":", 1)
        key = key.strip()
        if not key:
            return None, f"invalid YAML frontmatter near line {line_number}"
        parsed[key] = value.strip().strip('"\'')
    return parsed, None


def _inspect_local_links(docs_dir: Path) -> tuple[list[str], dict[str, int]]:
    warnings: list[str] = []
    inbound: dict[str, int] = {}
    for path in sorted(docs_dir.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for href in MARKDOWN_LINK_RE.findall(text):
            target = href.strip().split()[0]
            if not target or target.startswith("#") or URL_RE.match(target):
                continue
            target = unquote(target.split("#", 1)[0])
            if not target:
                continue
            resolved = _resolve_markdown_target(docs_dir, path, target)
            if resolved is None:
                warnings.append(f"{_rel(path, docs_dir)}: broken local link: {href}")
                continue
            if resolved.suffix == ".md" and resolved.name not in RESERVED_NAMES:
                target_rel = _rel(resolved, docs_dir)
                inbound[target_rel] = inbound.get(target_rel, 0) + 1
    return warnings, inbound


def _resolve_markdown_target(docs_dir: Path, source: Path, target: str) -> Path | None:
    if target.startswith("/"):
        candidate = docs_dir / target.lstrip("/")
    else:
        candidate = source.parent / target

    candidates = [candidate]
    if candidate.suffix == "":
        candidates.append(candidate.with_suffix(".md"))
    if target.endswith("/") or candidate.is_dir():
        candidates.append(candidate / "index.md")

    docs_root = docs_dir.resolve()
    for item in candidates:
        try:
            resolved = item.resolve()
        except OSError:
            continue
        if docs_root not in (resolved, *resolved.parents):
            continue
        if resolved.exists():
            return resolved
    return None


def _is_iso_date(value: Any) -> bool:
    return _as_date(value) is not None


def _as_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _is_iso_datetime(value: Any) -> bool:
    if isinstance(value, datetime):
        return True
    if not isinstance(value, str):
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        datetime.fromisoformat(normalized)
        return True
    except ValueError:
        return False


def _rel(path: Path, docs_dir: Path) -> str:
    return path.relative_to(docs_dir).as_posix()


def _print_result(result: ValidationResult) -> None:
    if result.errors:
        print("OKF validation failed:", file=sys.stderr)
        for error in result.errors:
            print(f"  ERROR: {error}", file=sys.stderr)
    if result.warnings:
        if not result.errors:
            print("OKF validation warnings:", file=sys.stderr)
        for warning in result.warnings:
            print(f"  WARNING: {warning}", file=sys.stderr)
    if result.ok:
        print("OKF validation passed")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an OKF v0.2 bundle under ./docs")
    parser.add_argument("repo_root", nargs="?", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--docs", help="Path to the OKF docs directory. Overrides repo_root/docs.")
    parser.add_argument("--level", choices=LEVELS, default="repository", help="Validation policy level.")
    parser.add_argument("--profile", choices=PROFILES, default="documentation", help="Repository profile.")
    parser.add_argument("--strict-links", action="store_true", help="Treat broken local Markdown links as errors.")
    parser.add_argument("--today", help="Override today's date for deterministic stale_after checks (YYYY-MM-DD).")
    args = parser.parse_args(list(argv) if argv is not None else None)

    docs_dir = Path(args.docs) if args.docs else Path(args.repo_root) / "docs"
    today_value = date.fromisoformat(args.today) if args.today else None
    result = validate_bundle(
        docs_dir,
        strict_links=args.strict_links,
        level=args.level,
        profile=args.profile,
        today=today_value,
    )
    _print_result(result)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
