#!/usr/bin/env python3
"""Copy Cursor Pstack into standards-compliant, harness-neutral Agent Skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile


PORT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PORT_ROOT.parent
MANIFEST_PATH = PORT_ROOT / "manifest.json"
OVERLAYS = PORT_ROOT / "overlays"
PORTABILITY_TRIGGERS = (
    "AskQuestion",
    "Task tool",
    "`Task`",
    "subagent_type",
    "run_in_background",
    ".cursor",
    "Cursor",
    "subagent",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True, help="Cursor Pstack plugin root")
    parser.add_argument("--destination", type=Path, default=REPO_ROOT)
    parser.add_argument("--check", action="store_true", help="Report drift without writing")
    parser.add_argument("--force", action="store_true", help="Replace an unmarked ps-* target")
    return parser.parse_args()


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text())


def tree_hash(source: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(
        path
        for root in (source / "skills", source / "agents")
        if root.exists()
        for path in root.rglob("*")
        if path.is_file()
    )
    for path in files:
        relative = path.relative_to(source).as_posix()
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode())
        digest.update(b"\n")
    return digest.hexdigest()


def discovered_skills(source: Path) -> set[str]:
    return {
        path.parent.relative_to(source / "skills").as_posix()
        for path in (source / "skills").rglob("SKILL.md")
    }


def validate_source(source: Path, manifest: dict) -> None:
    manifest_path = source / ".cursor-plugin" / "plugin.json"
    if not manifest_path.exists():
        raise SystemExit(f"missing Cursor plugin manifest: {manifest_path}")
    upstream = json.loads(manifest_path.read_text())
    expected_version = manifest["upstream"]["version"]
    if upstream.get("version") != expected_version:
        raise SystemExit(f"expected Pstack {expected_version}, found {upstream.get('version')}")
    actual_hash = tree_hash(source)
    expected_hash = manifest["upstream"]["tree_sha256"]
    if actual_hash != expected_hash:
        raise SystemExit(f"upstream tree hash mismatch\nexpected {expected_hash}\nactual   {actual_hash}")
    expected = {item["source"] for item in manifest["skills"]}
    actual = discovered_skills(source)
    if actual != expected:
        raise SystemExit(
            "manifest skill set differs from source\n"
            f"missing from manifest: {sorted(actual - expected)}\n"
            f"missing from source: {sorted(expected - actual)}"
        )


def rewrite_frontmatter(text: str, target: str, version: str, source_name: str) -> str:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md has no frontmatter")
    frontmatter = match.group(1)
    description = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if not description:
        raise ValueError("SKILL.md has no description")
    rendered = (
        "---\n"
        f"name: {target}\n"
        f"description: {description.group(1)}\n"
        "license: MIT. See LICENSE.txt\n"
        "metadata:\n"
        f"  ps-upstream-name: {source_name}\n"
        f"  ps-upstream-version: \"{version}\"\n"
        "---\n"
    )
    return rendered + text[match.end() :]


def general_replacements(text: str) -> str:
    replacements = (
        ("~/.cursor/rules/pstack-models.mdc", ".agents/pstack/models.json"),
        ("~/.cursor/skills/", "~/.agents/skills/"),
        (".cursor/skills/", ".agents/skills/"),
        ("~/.cursor/plugins/", "the active harness's installed skill directory/"),
        ("~/.cursor/projects/*/", "unrelated global transcript directories/"),
        ("~/.cursor/", "the active harness's state directory/"),
        (".cursor/", ".agents/"),
        ("Cursor cloud agents", "isolated subagents"),
        ("Cursor cloud agent", "isolated subagent"),
        ("Cursor dashboard", "harness's task-status view"),
        ("Cursor restart", "harness restart"),
        ("Cursor environment", "active harness"),
        ("Cursor's built-in", "the harness's built-in"),
        ("restart Cursor", "restart the harness"),
        ("AskQuestion tool", "available user-question interface"),
        ("`AskQuestion`", "asking the user"),
        ("AskQuestion", "ask the user"),
        ("Task tool", "subagent mechanism"),
        ("`Task` calls", "subagent launches"),
        ("`Task` call", "subagent launch"),
        ("`Task`", "a subagent"),
        ("Task calls", "subagent launches"),
        ("Task response body", "subagent result"),
        ("Task subagent", "subagent"),
        ("full Task schema including `environment`", "full delegation interface, including any available isolation controls"),
        ("`generalPurpose`", "a general-purpose subagent"),
        ("`subagent_type: generalPurpose`", "a general-purpose subagent"),
        ("`subagent_type: \"poteto-agent\"`", "a subagent following `ps-poteto-mode`"),
        ("`subagent_type: \"Comment Sicko\"`", "a subagent following the bundled comment-review prompt"),
        ("`run_in_background: true`", "start it concurrently when supported"),
        ("`environment: \"cloud\"`", "an isolated environment"),
        ("`environment: \"local\"`", "the local environment"),
        ("`readonly: true`", "read-only access"),
        ("`readonly: false`", "the access needed for configured tools"),
        ("cursor-team-kit", "the available app-driving tools"),
        ("`control-ui`", "a UI-driving capability"),
        ("`control-cli`", "a CLI-driving capability"),
        (".cursor/worktrees/", ".worktrees/"),
        ("grok-4.6-fast-xhigh", "large"),
        ("gpt-5.6-sol-max", "large"),
        ("claude-fable-5-thinking-max", "large"),
        ("claude-opus-5-thinking-xhigh", "large"),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    text = text.replace("Cursor", "the harness")
    text = text.replace("cloud workers", "subagents").replace("cloud worker", "subagent")
    text = text.replace("Cloud agents", "Remote subagents").replace("cloud agents", "remote subagents")
    text = text.replace("cloud agent", "remote subagent")
    text = text.replace("cloud environment", "isolated environment")
    text = text.replace("cloud VM", "isolated environment")
    text = text.replace("`cloud_base_branch`", "the required base branch")
    text = re.sub(
        r"^- `subagent_type`: (?:`generalPurpose`|a general-purpose subagent)$",
        "- Use a general-purpose subagent.",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(r"^- `model`: (.+)$", r"- Assign the model from \1", text, flags=re.MULTILINE)
    text = re.sub(r"^- `readonly`: `true`$", "- Give it read-only access.", text, flags=re.MULTILINE)
    text = re.sub(r"^- `readonly`: `false`(.+)$", r"- Give it the tool access required for the task.\1", text, flags=re.MULTILINE)
    text = text.replace("About to asking the user", "About to ask the user")
    text = text.replace("the `the available app-driving tools` plugin", "the available app-driving tools")
    text = text.replace("`the available app-driving tools`", "the available app-driving tools")
    text = text.replace("the a subagent response body", "the subagent result")
    text = text.replace("`principle-*`", "`ps-principle-*`")
    return text


def rewrite_skill_references(text: str, mapping: dict[str, str]) -> str:
    for source, target in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
        short = source.rsplit("/", 1)[-1]
        text = text.replace(f"../{short}/", f"../{target}/")
        text = text.replace(f"../../{short}/", f"../../{target}/")
        text = text.replace(f"pstack/skills/{short}/", f".agents/skills/{target}/")
        text = text.replace(f".cursor/skills/{short}/", f".agents/skills/{target}/")
        text = re.sub(
            rf"(?<![A-Za-z0-9_./-])skills/{re.escape(short)}/",
            f".agents/skills/{target}/",
            text,
        )
        text = text.replace(f"**{short}**", f"**{target}**")
        text = text.replace(f"`{short}` skill", f"`{target}` skill")
        text = text.replace(f"`{short}`", f"`{target}`")
        text = re.sub(rf"(?<![A-Za-z0-9_.-])/{re.escape(short)}\b", target, text)
    text = text.replace("pstack/skills/", ".agents/skills/")
    return text


def exact_semantic_replacements(text: str) -> str:
    replacements = {
        "1. Spawn a subagent with a subagent following the bundled comment-review prompt. Pass the scope. Do not restate its rules.":
            "1. Spawn a subagent to complete this task. Have it read `references/comment-sicko.md`, then pass the scope. Do not restate its rules.",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(
        r"\*\*Use .*?poteto-agent.*?\n",
        "For a general playbook delegation, ask the subagent to read and follow `ps-poteto-mode`. Routed workflow skills such as `ps-how`, `ps-why`, `ps-interrogate`, `ps-reflect`, and `ps-swarm` define their own roles. Keep those role and access choices.\n",
        text,
    )
    text = re.sub(
        r"\*\*Defaults for every subagent launch\.\*\*.*?\n",
        "**Defaults for every delegation.** Read `.agents/pstack/models.json` when present and resolve the workflow role to a configured tier. Start independent lanes concurrently when supported. Pass file pointers instead of large inline dumps. Give writers isolated destinations. Use the parent model when the harness cannot apply a child override, and record that limitation.\n",
        text,
    )
    text = text.replace(
        "Spawn all N workers in one message with a general-purpose subagent, an isolated environment, start it concurrently when supported, and the configured model. Use the local environment only when the worker needs access to something on the user's computer.",
        "Spawn all N workers through the harness's delegation mechanism. Start them concurrently when supported, use the configured tier, and isolate them from each other's writes. Keep a worker local only when it needs resources on the user's computer.",
    )
    text = text.replace(
        "Spawn all N subagents in one message with start it concurrently when supported, each with the task, the path to the shared grounding, its own output path, and instructions to produce both the artifact and a short rationale.",
        "Spawn all N subagents through the harness's delegation mechanism and start them concurrently when supported. Give each the task, shared grounding path, a unique output path, and instructions to produce the artifact plus a short rationale.",
    )
    text = re.sub(
        r"Otherwise default to one each on `large`, `large`, `large`, `large`\.",
        "Otherwise use the configured `small`, `medium`, and `large` tiers, with a second `large` candidate when four perspectives are useful.",
        text,
    )
    text = re.sub(
        r"Otherwise use `large`, `large`, `large`, `large`\.",
        "Otherwise choose from the configured `small`, `medium`, and `large` tiers.",
        text,
    )
    text = re.sub(
        r"\(defaults `large`, `large`, `large`, `large`\)",
        "(defaults to the configured `small`, `medium`, and `large` tiers)",
        text,
    )
    text = text.replace(
        "Use your configured architect runners (defaults `large`, `large`, `large`, `large`).",
        "Use the configured architect runner tiers. Default to `small`, `medium`, and `large`, with a second `large` candidate when useful.",
    )
    text = text.replace(
        "Before commit → the `deslop` skill from the available app-driving tools (`/deslop`).",
        "Before commit → use an installed code-cleanup skill when available, then inspect the diff yourself.",
    )
    text = text.replace(
        "Shipping UI / IDE / CLI → the matching control skill. the available app-driving tools publishes a CLI-driving capability (CLIs and TUIs) and a UI-driving capability (browser / Electron / web UIs).",
        "Shipping UI / IDE / CLI → use the harness's available UI, CLI, browser, or simulator-driving capability.",
    )
    text = text.replace("`/deslop`", "an installed code-cleanup skill")
    text = text.replace("/deslop", "an installed code-cleanup skill")
    text = text.replace("fails the the ", "fails the ")
    text = text.replace("each a isolated subagent", "each in an isolated environment")
    text = text.replace("Spawn one readonly judge subagent", "Spawn one read-only judge subagent")
    text = re.sub(
        r"- Give it the tool access required for the task\. \(agent mode\)\. \*\*Do not use readonly/Ask mode\.\*\* It strips MCP access, which disables MCP-backed investigators entirely\. The source control investigator would be safe in readonly, but keep modes uniform\. Investigators still shouldn't write anything\. That's a posture, not a sandbox\.",
        "- Give it access to the connected evidence tools. Keep the investigator read-only in its task brief, but do not select a harness access mode that disables those tools.",
        text,
    )
    text = re.sub(
        r"One message, three subagent launches, a general-purpose subagent, explicit `model:` on each, agent mode \(the access needed for configured tools\)\. Reviewers need MCP access for context lookups \(tickets, chat threads, observability traces referenced in the transcript\); readonly strips MCPs\. The prompt forbids file writes; the parent applies edits\.",
        "Spawn three general-purpose reviewer subagents concurrently. Resolve each model from the configured tiers and give each reviewer access to connected evidence tools. The prompts forbid file writes; the parent applies edits.",
        text,
    )
    text = re.sub(
        r"One subagent launch, a general-purpose subagent, using your configured reflect-judgment model \(default `large`\), agent mode \(the access needed for configured tools\)\. The synthesizer's quality check includes spot-verifying citations, which can require MCP access; readonly strips MCPs\.",
        "Spawn one general-purpose synthesizer subagent with the configured reflect-judgment tier. Give it access to connected evidence tools because it spot-checks citations.",
        text,
    )
    role_lines = {
        "- Assign the model from your configured how-explorer model (default `large`)":
            "- Resolve `how explorer` through `role_tiers` (default `small`).",
        "- Assign the model from your configured how-explainer model (default `large`)":
            "- Resolve `how explainer` through `role_tiers` (default `large`).",
        "- Assign the model from your configured why-investigators model (default `large`)":
            "- Resolve `why investigators` through `role_tiers` (default `small`).",
        "- Assign the model from your configured why-synthesizer model (default `large`)":
            "- Resolve `why synthesizer` through `role_tiers` (default `large`).",
    }
    for old, new in role_lines.items():
        text = text.replace(old, new)
    text = text.replace(
        "Use your configured architect runners (defaults to the configured `small`, `medium`, and `large` tiers).",
        "Use `architect runners` from `.agents/pstack/models.json` when present. Otherwise use the configured `small`, `medium`, and `large` tiers.",
    )
    text = text.replace(
        "your configured how-critics list",
        "the `how critics` list in `.agents/pstack/models.json`",
    )
    text = text.replace(
        "the configured how-critics list",
        "the configured `how critics` list",
    )
    text = text.replace("your configured reflect-judgment model", "`reflect judgment` from `role_tiers`")
    text = text.replace("your configured reflect-tooling model", "`reflect tooling` from `role_tiers`")
    text = text.replace("the configured reflect-judgment tier", "`reflect synthesizer` from `role_tiers`")
    text = text.replace(
        "| Tooling | `reflect tooling` from `role_tiers` (default `large`) |",
        "| Tooling | `reflect tooling` from `role_tiers` (default `medium`) |",
    )
    text = text.replace(
        "| Divergent | `reflect judgment` from `role_tiers` (default `large`) |",
        "| Divergent | `reflect divergent` from `role_tiers` (default `large`) |",
    )
    text = text.replace(
        "Assign the model from one model from the configured `how critics` list.",
        "Assign one model from the configured `how critics` list.",
    )
    text = text.replace(
        "Pick the worker model from `swarm workers` in `.agents/pstack/models.json` when present. Otherwise use `large`.",
        "Pick the worker model from `swarm workers` in `.agents/pstack/models.json` when present. Otherwise use `medium`.",
    )
    text = text.replace("| Reviewer A | `large` |", "| Reviewer A | `small` |")
    text = text.replace("| Reviewer B | `large` |", "| Reviewer B | `medium` |")
    text = re.sub(
        r"If a model slug is rejected as unresolvable when you try to spawn the subagent,.*?fallback for them\.",
        "If the harness rejects a configured model or reasoning level, stop that review lane and report the stale identifier. Do not substitute another model silently.",
        text,
    )
    text = text.replace(
        "a slop-strip (the `deslop` skill from the available app-driving tools (an installed code-cleanup skill))",
        "an installed code-cleanup skill",
    )
    text = text.replace(
        "Run an installed code-cleanup skill from the available app-driving tools over the diff before commit.",
        "Run an installed code-cleanup skill over the diff before commit.",
    )
    return text


def rewrite_agent_reference(text: str, filename: str) -> str:
    if filename != "poteto-agent.md":
        return text
    text = re.sub(r"\A---\n.*?\n---\n+", "", text, flags=re.DOTALL)
    text = text.replace(
        "# Poteto subagent\n",
        "# Poteto subagent prompt\n\nUse this prompt for a general playbook delegation. Ask the subagent to read `ps-poteto-mode/SKILL.md` in full before it starts.\n",
    )
    return text


def insert_adaptation(text: str, target: str) -> str:
    if target == "ps-setup-pstack" or not any(token in text for token in PORTABILITY_TRIGGERS):
        return text
    link = (
        "references/harness-adaptation.md"
        if target == "ps-poteto-mode"
        else "../ps-poteto-mode/references/harness-adaptation.md"
    )
    marker = "\n## Harness adaptation\n"
    if marker in text:
        return text
    heading = re.search(r"^# .+$", text, re.MULTILINE)
    if not heading:
        return text
    block = (
        "\n\n## Harness adaptation\n\n"
        f"Read [the harness adaptation contract]({link}) before delegating work, asking structured questions, selecting models, or locating harness state.\n"
    )
    return text[: heading.end()] + block + text[heading.end() :]


def transform_markdown(path: Path, target: str, source_name: str, manifest: dict, mapping: dict[str, str]) -> None:
    text = path.read_text()
    original = text
    if path.name == "SKILL.md" and path.parent.name == target:
        text = rewrite_frontmatter(text, target, manifest["upstream"]["version"], source_name)
    text = rewrite_skill_references(text, mapping)
    text = general_replacements(text)
    text = exact_semantic_replacements(text)
    text = rewrite_agent_reference(text, path.name)
    if path.name == "SKILL.md" and path.parent.name == target:
        text = insert_adaptation(text, target)
    if text != original:
        path.write_text(text)


def copy_overlay(name: str, target_dir: Path) -> None:
    overlay = OVERLAYS / name
    if not overlay.exists():
        return
    for source in sorted(overlay.rglob("*")):
        relative = source.relative_to(overlay)
        destination = target_dir / relative
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)


def add_attribution(target_dir: Path, source_name: str, manifest: dict, source: Path) -> None:
    shutil.copy2(source / "LICENSE", target_dir / "LICENSE.txt")
    notice = (
        f"# {target_dir.name} attribution\n\n"
        f"Derived from `{source_name}` in Cursor Pstack {manifest['upstream']['version']} by Lauren Tan.\n\n"
        f"Upstream: {manifest['upstream']['repository']}\n\n"
        "This directory was generated by `pstack-port/scripts/port_pstack.py`. Edit the port transforms or overlays, then regenerate.\n"
    )
    (target_dir / "NOTICE.md").write_text(notice)
    marker = {
        "schema_version": 1,
        "source": source_name,
        "source_version": manifest["upstream"]["version"],
        "source_tree_sha256": manifest["upstream"]["tree_sha256"],
    }
    (target_dir / ".ps-port.json").write_text(json.dumps(marker, indent=2, sort_keys=True) + "\n")


def stage_port(source: Path, staging: Path, manifest: dict) -> list[str]:
    mapping = {item["source"].rsplit("/", 1)[-1]: item["target"] for item in manifest["skills"]}
    targets = []
    for item in manifest["skills"]:
        source_name = item["source"]
        target = item["target"]
        target_dir = staging / target
        shutil.copytree(source / "skills" / source_name, target_dir, copy_function=shutil.copy2)
        for markdown in sorted(target_dir.rglob("*.md")):
            transform_markdown(markdown, target, source_name, manifest, mapping)
        if target == "ps-no-comments":
            references = target_dir / "references"
            references.mkdir(exist_ok=True)
            copied = references / "comment-sicko.md"
            shutil.copy2(source / "agents" / "comment-sicko.md", copied)
            transform_markdown(copied, target, source_name, manifest, mapping)
        if target == "ps-poteto-mode":
            references = target_dir / "references"
            references.mkdir(exist_ok=True)
            copied = references / "poteto-agent.md"
            shutil.copy2(source / "agents" / "poteto-agent.md", copied)
            transform_markdown(copied, target, source_name, manifest, mapping)
        copy_overlay(source_name.rsplit("/", 1)[-1], target_dir)
        add_attribution(target_dir, source_name, manifest, source)
        targets.append(target)
    return targets


def directory_hash(path: Path) -> str:
    digest = hashlib.sha256()
    for file in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(file.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        digest.update(file.read_bytes())
    return digest.hexdigest()


def validate_staging(staging: Path, targets: list[str]) -> None:
    name_pattern = re.compile(r"^ps-[a-z0-9]+(?:-[a-z0-9]+)*$")
    for target in targets:
        skill = staging / target / "SKILL.md"
        if not skill.exists() or not name_pattern.fullmatch(target):
            raise ValueError(f"invalid generated target: {target}")
        match = re.search(r"^name:\s*(\S+)$", skill.read_text(), re.MULTILINE)
        if not match or match.group(1) != target:
            raise ValueError(f"frontmatter name mismatch: {target}")
    forbidden = re.compile(
        r"AskQuestion|subagent_type|run_in_background|~?/?.cursor/|\bCursor\b|"
        r"Task tool|Task subagent|Task schema|generalPurpose|is_background|readonly/Ask"
    )
    problems = []
    for target in targets:
        for markdown in (staging / target).rglob("*.md"):
            if markdown.name == "NOTICE.md" or target == "ps-setup-pstack":
                continue
            if forbidden.search(markdown.read_text()):
                matches = sorted(set(forbidden.findall(markdown.read_text())))
                problems.append(f"{markdown.relative_to(staging)} ({', '.join(matches)})")
    if problems:
        raise ValueError("harness-specific mechanics remain in: " + ", ".join(problems))


def apply_or_check(staging: Path, destination: Path, targets: list[str], check: bool, force: bool) -> int:
    drift = []
    for target in targets:
        generated = staging / target
        existing = destination / target
        if not existing.exists() or directory_hash(generated) != directory_hash(existing):
            drift.append(target)
    if check:
        if drift:
            print("generated drift: " + ", ".join(drift))
            return 1
        print(f"P-Stack port is current ({len(targets)} skills)")
        return 0
    unowned = [
        target
        for target in drift
        if (destination / target).exists()
        and not (destination / target / ".ps-port.json").exists()
        and not force
    ]
    if unowned:
        raise SystemExit("refusing to replace unmarked targets: " + ", ".join(unowned))
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ps-port-backup-", dir=destination) as backup_name:
        backup = Path(backup_name)
        installed = []
        try:
            for target in drift:
                existing = destination / target
                if existing.exists():
                    os.replace(existing, backup / target)
                os.replace(staging / target, existing)
                installed.append(target)
        except Exception:
            for target in reversed(installed):
                current = destination / target
                if current.exists():
                    shutil.rmtree(current)
                saved = backup / target
                if saved.exists():
                    os.replace(saved, current)
            raise
    print(f"generated {len(targets)} P-Stack skills; changed {len(drift)}")
    return 0


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    destination = args.destination.resolve()
    manifest = load_manifest()
    validate_source(source, manifest)
    with tempfile.TemporaryDirectory(prefix="ps-port-stage-", dir=destination.parent) as staging_name:
        staging = Path(staging_name)
        targets = stage_port(source, staging, manifest)
        validate_staging(staging, targets)
        return apply_or_check(staging, destination, targets, args.check, args.force)


if __name__ == "__main__":
    raise SystemExit(main())
