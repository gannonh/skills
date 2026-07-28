#!/usr/bin/env python3
"""Generate an interactive HTML graph viewer for an OKF bundle.

This is a standalone skill helper inspired by the proof-of-concept viewer in
GoogleCloudPlatform/knowledge-catalog. It depends only on Python and PyYAML;
the generated HTML loads Cytoscape.js and marked from jsDelivr.

Usage:
    python visualize_okf.py [repo_root]
    python visualize_okf.py --bundle path/to/docs
    python visualize_okf.py --bundle path/to/docs --out /tmp/docs.html --name "Docs"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

RESERVED_NAMES = {"index.md", "log.md"}
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
URL_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
KNOWN_TYPE_COLORS = {
    "BigQuery Dataset": "#8b5cf6",
    "BigQuery Table": "#3b82f6",
    "Reference": "#10b981",
    "Guide": "#2563eb",
    "Policy": "#dc2626",
    "Domain Concept": "#7c3aed",
    "Research Note": "#0891b2",
    "Spec": "#ea580c",
    "ADR": "#9333ea",
    "Runbook": "#059669",
}
FALLBACK_COLORS = (
    "#475569", "#0369a1", "#0f766e", "#4d7c0f", "#a16207",
    "#b91c1c", "#be185d", "#7e22ce", "#4338ca",
)


@dataclass
class Concept:
    id: str
    type: str
    title: str
    description: str
    resource: str
    tags: list[str]
    body: str
    status: str = "stable"
    generated: dict[str, Any] = field(default_factory=dict)
    verified: list[dict[str, Any]] = field(default_factory=list)
    stale_after: str = ""
    sources: list[dict[str, Any]] = field(default_factory=list)
    trust_tier: str = "unverified"
    stale: bool = False
    links_to: list[str] = field(default_factory=list)


def generate_visualization(
    bundle_root: Path,
    out_path: Path,
    *,
    bundle_name: str | None = None,
) -> dict[str, int]:
    """Walk an OKF bundle and write a single interactive HTML file."""
    bundle_root = Path(bundle_root).resolve()
    out_path = Path(out_path)
    if not bundle_root.is_dir():
        raise FileNotFoundError(f"Bundle directory not found: {bundle_root}")

    concepts, warnings = _walk_concepts(bundle_root)
    graph = _build_graph(concepts)
    name = bundle_name or bundle_root.name
    html = _render_html(name, graph)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)

    return {
        "concepts": len(concepts),
        "edges": len(graph["edges"]),
        "bytes": len(html.encode("utf-8")),
        "warnings": len(warnings),
    }


def _walk_concepts(bundle_root: Path) -> tuple[list[Concept], list[str]]:
    concepts: list[Concept] = []
    warnings: list[str] = []
    for md_path in sorted(bundle_root.rglob("*.md")):
        if md_path.name in RESERVED_NAMES:
            continue
        rel = md_path.relative_to(bundle_root).as_posix()
        text = md_path.read_text(encoding="utf-8")
        frontmatter, body, error = _parse_document(text)
        if error:
            warnings.append(f"{rel}: {error}; skipped")
            continue
        if frontmatter is None:
            warnings.append(f"{rel}: missing YAML frontmatter; skipped")
            continue
        concept_type = frontmatter.get("type")
        if not isinstance(concept_type, str) or not concept_type.strip():
            warnings.append(f"{rel}: missing non-empty type; skipped")
            continue

        tags = frontmatter.get("tags") or []
        if not isinstance(tags, list):
            tags = [tags]
        generated = frontmatter.get("generated")
        if not isinstance(generated, dict):
            generated = {}
        verified = _normalize_verified(frontmatter.get("verified"))
        sources = frontmatter.get("sources") or []
        if isinstance(sources, dict):
            sources = [sources]
        if not isinstance(sources, list):
            sources = []
        stale_after = _format_scalar(frontmatter.get("stale_after"))

        concept_id = md_path.relative_to(bundle_root).with_suffix("").as_posix()
        concepts.append(
            Concept(
                id=concept_id,
                type=concept_type.strip(),
                title=str(frontmatter.get("title") or concept_id),
                description=str(frontmatter.get("description") or ""),
                resource=str(frontmatter.get("resource") or ""),
                tags=[str(tag) for tag in tags],
                body=body,
                status=str(frontmatter.get("status") or "stable"),
                generated=generated,
                verified=verified,
                stale_after=stale_after,
                sources=[source for source in sources if isinstance(source, dict)],
                trust_tier=_trust_tier(verified),
                stale=_is_stale(frontmatter.get("stale_after")),
                links_to=_extract_links(body, md_path, bundle_root),
            )
        )
    return concepts, warnings


def _build_graph(concepts: list[Concept]) -> dict[str, Any]:
    ids = {concept.id for concept in concepts}
    types = sorted({concept.type for concept in concepts})
    colors = _type_colors(types)
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str]] = set()

    for concept in concepts:
        nodes.append({
            "data": {
                "id": concept.id,
                "label": concept.title,
                "type": concept.type,
                "description": concept.description,
                "resource": concept.resource,
                "tags": concept.tags,
                "status": concept.status,
                "generated": concept.generated,
                "verified": concept.verified,
                "stale_after": concept.stale_after,
                "sources": concept.sources,
                "trust_tier": concept.trust_tier,
                "stale": concept.stale,
                "color": colors[concept.type],
                "size": 30 + min(60, len(concept.body) // 200),
            }
        })
        for target in concept.links_to:
            if target == concept.id or target not in ids:
                continue
            edge_key = (concept.id, target)
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)
            edges.append({
                "data": {
                    "id": f"{concept.id}__{target}",
                    "source": concept.id,
                    "target": target,
                }
            })

    return {
        "nodes": nodes,
        "edges": edges,
        "bodies": {concept.id: concept.body for concept in concepts},
        "types": types,
    }


def _type_colors(types: list[str]) -> dict[str, str]:
    colors: dict[str, str] = {}
    fallback_index = 0
    for concept_type in types:
        known = KNOWN_TYPE_COLORS.get(concept_type)
        if known:
            colors[concept_type] = known
        else:
            colors[concept_type] = FALLBACK_COLORS[fallback_index % len(FALLBACK_COLORS)]
            fallback_index += 1
    return colors


def _extract_links(body: str, source_path: Path, bundle_root: Path) -> list[str]:
    targets: list[str] = []
    seen: set[str] = set()
    for match in MARKDOWN_LINK_RE.finditer(body):
        href = _markdown_href(match.group(1))
        concept_id = _resolve_concept_id(href, source_path, bundle_root)
        if concept_id and concept_id not in seen:
            seen.add(concept_id)
            targets.append(concept_id)
    return targets


def _markdown_href(raw: str) -> str:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        return value[1:value.index(">")]
    return value.split(maxsplit=1)[0] if value else ""


def _resolve_concept_id(href: str, source_path: Path, bundle_root: Path) -> str | None:
    if not href or href.startswith("#") or URL_SCHEME_RE.match(href):
        return None
    split = urlsplit(href)
    target = unquote(split.path)
    if not target:
        return None
    candidate = bundle_root / target.lstrip("/") if target.startswith("/") else source_path.parent / target
    candidates = [candidate]
    if candidate.suffix == "":
        candidates.append(candidate.with_suffix(".md"))
    if target.endswith("/"):
        candidates.append(candidate / "index.md")

    root = bundle_root.resolve()
    for item in candidates:
        try:
            resolved = item.resolve()
            resolved.relative_to(root)
        except (OSError, ValueError):
            continue
        if not resolved.exists() or resolved.suffix != ".md" or resolved.name in RESERVED_NAMES:
            continue
        return resolved.relative_to(root).with_suffix("").as_posix()
    return None


def _parse_document(text: str) -> tuple[dict[str, Any] | None, str, str | None]:
    if not text.startswith("---\n"):
        return None, text, None
    lines = text.splitlines()
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return None, text, "unterminated YAML frontmatter"
    raw = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1:])
    if yaml is None:
        return None, body, "PyYAML is required to parse OKF frontmatter"
    try:
        parsed = yaml.safe_load(raw) if raw.strip() else {}
    except Exception as exc:
        return None, body, f"invalid YAML frontmatter: {exc}"
    if parsed is None:
        parsed = {}
    if not isinstance(parsed, dict):
        return None, body, "frontmatter must be a YAML mapping"
    return parsed, body, None


def _normalize_verified(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def _trust_tier(verified: list[dict[str, Any]]) -> str:
    if not verified:
        return "unverified"
    for event in verified:
        actor = event.get("by")
        if isinstance(actor, str) and actor.startswith("human:"):
            return "human-reviewed"
    return "machine-confirmed"


def _is_stale(value: Any) -> bool:
    stale_date = _as_date(value)
    return stale_date is not None and date.today() >= stale_date


def _as_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).date() if value.tzinfo else value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value.strip():
        text = value.strip()
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            return None
    return None


def _format_scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def _safe_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str).replace("</", "<\\/")


def _render_html(bundle_name: str, graph: dict[str, Any]) -> str:
    return HTML_TEMPLATE.replace("__BUNDLE_NAME__", _safe_json(bundle_name)).replace(
        "__BUNDLE_DATA__", _safe_json(graph)
    )


HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OKF Bundle Viewer</title>
<script src="https://cdn.jsdelivr.net/npm/cytoscape@3.28.1/dist/cytoscape.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js"></script>
<style>
*{box-sizing:border-box} body{margin:0;font:14px -apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;color:#0f172a;background:#f8fafc;height:100vh;display:flex;flex-direction:column}
body>header{display:flex;align-items:center;justify-content:space-between;padding:10px 16px;background:#fff;border-bottom:1px solid #e2e8f0;gap:12px}.title strong{font-size:16px;margin-right:8px}.muted{color:#64748b;font-size:12px}.controls{display:flex;gap:8px;flex-wrap:wrap}.controls input,.controls select,.controls button{font-size:13px;padding:5px 8px;border:1px solid #cbd5e1;border-radius:4px;background:#fff}.controls input{width:220px}.controls button{cursor:pointer;background:#f1f5f9}
main{display:flex;flex:1;min-height:0}#graph{flex:1 1 60%;background:#fff;border-right:1px solid #e2e8f0;min-width:0}#detail{flex:0 0 40%;overflow:auto;padding:18px 22px;background:#fff}#detail-empty{text-align:center;margin-top:40px}.detail-header{display:block;padding:0;border:0;margin-bottom:12px}.detail-header h1{font-size:18px;margin:4px 0 2px}.type-chip,.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600}.type-chip{color:#fff;text-transform:uppercase;letter-spacing:.4px}.badges{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}.badge{border:1px solid transparent}.status-stable,.fresh{background:#ecfdf5;color:#047857;border-color:#a7f3d0}.status-draft{background:#fefce8;color:#a16207;border-color:#fde68a}.status-deprecated,.trust-unverified{background:#f1f5f9;color:#64748b;border-color:#cbd5e1}.trust-machine-confirmed{background:#eff6ff;color:#1d4ed8;border-color:#bfdbfe}.trust-human-reviewed{background:#f5f3ff;color:#6d28d9;border-color:#ddd6fe}.stale{background:#fef2f2;color:#b91c1c;border-color:#fecaca}
dl{display:grid;grid-template-columns:90px 1fr;gap:4px 12px;margin:8px 0 12px;font-size:13px}dt{color:#64748b;font-weight:500}dd{margin:0;min-width:0}dd a{color:#2563eb;word-break:break-all}.tag{display:inline-block;padding:1px 6px;margin:0 4px 2px 0;border-radius:4px;background:#f1f5f9;color:#475569;font-size:11px}.sources-list{padding-left:18px;margin:0}hr{border:0;border-top:1px solid #e2e8f0;margin:14px 0}#detail-body{font-size:13px;line-height:1.55}#detail-body h1{font-size:16px;margin:18px 0 6px;padding-bottom:4px;border-bottom:1px solid #e2e8f0}#detail-body h2{font-size:14px}#detail-body h3{font-size:13px}#detail-body code{background:#f1f5f9;padding:1px 4px;border-radius:3px;font:12px ui-monospace,"SF Mono",Consolas,monospace}#detail-body pre{background:#0f172a;color:#e2e8f0;padding:10px 12px;border-radius:6px;overflow:auto}#detail-body pre code{background:transparent;color:inherit;padding:0}#detail-body table{border-collapse:collapse}#detail-body th,#detail-body td{border:1px solid #e2e8f0;padding:4px 8px;font-size:12px}a.internal,a.backlink{color:#2563eb;cursor:pointer}a.external{color:#2563eb}#detail-backlinks{margin-top:18px}#detail-backlinks h2{font-size:13px;color:#64748b}
@media(max-width:900px){body{height:auto;min-height:100vh}body>header{align-items:flex-start;flex-direction:column}.controls input{width:100%}main{flex-direction:column}#graph{height:55vh;flex:none;border-right:0;border-bottom:1px solid #e2e8f0}#detail{flex:none}}
</style>
</head>
<body>
<header><div class="title"><strong id="bundle-name"></strong><span class="muted">OKF bundle</span></div><div class="controls"><input id="search" type="search" placeholder="Search title / id / tag"><select id="filter-type"><option value="">All types</option></select><select id="layout"><option value="cose">cose (force)</option><option value="concentric">concentric</option><option value="breadthfirst">breadth-first</option><option value="circle">circle</option><option value="grid">grid</option></select><button id="reset">Reset view</button></div></header>
<main><section id="graph"></section><section id="detail"><div id="detail-empty" class="muted">Click a node to see its details.</div><article id="detail-content" hidden><header class="detail-header"><span class="type-chip" id="detail-type"></span><h1 id="detail-title"></h1><div class="muted" id="detail-id"></div></header><div class="badges" id="detail-badges"></div><dl><dt>Description</dt><dd id="detail-description"></dd><dt>Resource</dt><dd id="detail-resource"></dd><dt>Tags</dt><dd id="detail-tags"></dd><dt>Generated</dt><dd id="detail-generated"></dd><dt>Verified</dt><dd id="detail-verified"></dd><dt>Sources</dt><dd id="detail-sources"></dd></dl><hr><div id="detail-body"></div><section id="detail-backlinks" hidden><h2>Cited by</h2><ul id="backlinks-list"></ul></section></article></section></main>
<script>window.BUNDLE_NAME=__BUNDLE_NAME__;window.BUNDLE=__BUNDLE_DATA__;</script>
<script>
(()=>{const bundle=window.BUNDLE,name=window.BUNDLE_NAME;document.title=`${name} — OKF Viewer`;document.getElementById('bundle-name').textContent=name;const byId=Object.fromEntries(bundle.nodes.map(n=>[n.data.id,n.data]));const backlinks={};for(const e of bundle.edges)(backlinks[e.data.target]??=[]).push(e.data.source);const typeSelect=document.getElementById('filter-type');for(const t of bundle.types){const o=document.createElement('option');o.value=t;o.textContent=t;typeSelect.appendChild(o)}
const cy=cytoscape({container:document.getElementById('graph'),elements:[...bundle.nodes,...bundle.edges],style:[{selector:'node',style:{'background-color':'data(color)',label:'data(label)',color:'#0f172a','font-size':11,'text-valign':'bottom','text-margin-y':4,'text-wrap':'wrap','text-max-width':120,width:'data(size)',height:'data(size)','border-width':1,'border-color':'#0f172a'}},{selector:'node[?stale]',style:{'border-width':2,'border-color':'#b91c1c','border-style':'dashed'}},{selector:'node[status = "deprecated"]',style:{opacity:.55}},{selector:'node:selected',style:{'border-width':3,'border-color':'#f59e0b'}},{selector:'edge',style:{width:1.5,'line-color':'#cbd5e1','target-arrow-color':'#cbd5e1','target-arrow-shape':'triangle','curve-style':'bezier','arrow-scale':.9}},{selector:'.dim',style:{opacity:.15}}],layout:{name:'cose',animate:false,padding:30},wheelSensitivity:.2});
const $=id=>document.getElementById(id);cy.on('tap','node',e=>show(e.target.id()));cy.on('tap',e=>{if(e.target===cy)clear()});$('layout').addEventListener('change',e=>cy.layout({name:e.target.value,animate:false,padding:30}).run());$('reset').addEventListener('click',()=>{cy.fit(null,30);clear()});
function applyFilter(){const q=$('search').value.trim().toLowerCase(),t=typeSelect.value;cy.nodes().forEach(n=>{const d=n.data(),hay=`${d.label||''} ${d.id} ${(d.tags||[]).join(' ')}`.toLowerCase();n.toggleClass('dim',(q&&!hay.includes(q))||(t&&d.type!==t))});cy.edges().forEach(e=>e.toggleClass('dim',e.source().hasClass('dim')||e.target().hasClass('dim')))}$('search').addEventListener('input',applyFilter);typeSelect.addEventListener('change',applyFilter);
function clear(){cy.elements().unselect();$('detail-empty').hidden=false;$('detail-content').hidden=true}function badge(text,cls){const s=document.createElement('span');s.className=`badge ${cls}`;s.textContent=text;return s}function actor(e){return e&&e.by?(e.at?`${e.by} · ${e.at}`:String(e.by)):'—'}
function show(id){const d=byId[id];if(!d)return;cy.elements().unselect();const node=cy.getElementById(id);node.select();$('detail-empty').hidden=true;$('detail-content').hidden=false;$('detail-type').textContent=d.type;$('detail-type').style.background=d.color;$('detail-title').textContent=d.label;$('detail-id').textContent=id;$('detail-description').textContent=d.description||'—';
const r=$('detail-resource');r.replaceChildren();if(d.resource){const a=document.createElement('a');a.href=d.resource;a.textContent=d.resource;a.target='_blank';a.rel='noopener';a.className='external';r.appendChild(a)}else r.textContent='—';const tags=$('detail-tags');tags.replaceChildren();if(d.tags?.length)for(const t of d.tags){const s=document.createElement('span');s.className='tag';s.textContent=t;tags.appendChild(s)}else tags.textContent='—';
const b=$('detail-badges');b.replaceChildren();const status=d.status||'stable';b.appendChild(badge(status,`status-${status}`));const tier=d.trust_tier||'unverified';b.appendChild(badge(tier.replaceAll('-',' '),`trust-${tier}`));if(d.stale)b.appendChild(badge(d.stale_after?`stale (since ${d.stale_after})`:'stale','stale'));else if(d.stale_after)b.appendChild(badge(`stale after ${d.stale_after}`,'fresh');$('detail-generated').textContent=actor(d.generated);$('detail-verified').textContent=d.verified?.length?d.verified.map(actor).join('; '):'—';
const se=$('detail-sources');se.replaceChildren();if(d.sources?.length){const ul=document.createElement('ul');ul.className='sources-list';for(const src of d.sources){const li=document.createElement('li'),label=src.title||src.resource||src.id||'source';if(src.resource&&/^https?:\/\//.test(src.resource)){const a=document.createElement('a');a.href=src.resource;a.textContent=label;a.target='_blank';a.rel='noopener';a.className='external';li.appendChild(a)}else li.textContent=src.resource?`${label} (${src.resource})`:label;ul.appendChild(li)}se.appendChild(ul)}else se.textContent='—';
const body=$('detail-body');body.innerHTML=marked.parse(bundle.bodies[id]||'',{gfm:true});rewriteLinks(body,id);const bl=backlinks[id]||[],sec=$('detail-backlinks'),list=$('backlinks-list');list.replaceChildren();sec.hidden=!bl.length;for(const src of bl){const li=document.createElement('li'),a=document.createElement('a');a.className='backlink';a.textContent=byId[src]?.label||src;a.addEventListener('click',()=>show(src));li.append(a,document.createTextNode(` (${src})`));list.appendChild(li)}cy.animate({center:{eles:node},zoom:Math.max(cy.zoom(),1)},{duration:200})}
function normalize(path){const out=[];for(const p of path.split('/')){if(!p||p==='.')continue;if(p==='..')out.pop();else out.push(p)}return out.join('/')}function targetId(href,current){if(!href||href.startsWith('#')||/^[A-Za-z][A-Za-z0-9+.-]*:/.test(href))return null;const clean=decodeURIComponent(href.split('#')[0].split('?')[0]);if(!clean.endsWith('.md'))return null;const base=current.includes('/')?current.slice(0,current.lastIndexOf('/')+1):'';return normalize((clean.startsWith('/')?'':base)+clean.replace(/^\//,'').slice(0,-3))}function rewriteLinks(root,current){root.querySelectorAll('a[href]').forEach(a=>{const id=targetId(a.getAttribute('href'),current);if(id&&byId[id]){a.className='internal';a.href='#';a.addEventListener('click',e=>{e.preventDefault();show(id)})}else{a.className='external';a.target='_blank';a.rel='noopener'}})}const initial=bundle.nodes[0];if(initial)show(initial.data.id)})();
</script>
</body></html>'''


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate an interactive HTML graph for an OKF bundle")
    parser.add_argument("repo_root", nargs="?", default=".", help="Repository root; defaults to current directory")
    parser.add_argument("--bundle", help="Bundle root; defaults to <repo_root>/docs")
    parser.add_argument("--out", help="Output HTML path; defaults to <bundle>/viz.html")
    parser.add_argument("--name", help="Display name; defaults to the bundle directory name")
    args = parser.parse_args(list(argv) if argv is not None else None)

    bundle = Path(args.bundle) if args.bundle else Path(args.repo_root) / "docs"
    out = Path(args.out) if args.out else bundle / "viz.html"
    try:
        stats = generate_visualization(bundle, out, bundle_name=args.name)
    except (FileNotFoundError, OSError) as exc:
        print(f"OKF visualization failed: {exc}", file=sys.stderr)
        return 1
    print(
        f"Wrote {stats['concepts']} concept(s), {stats['edges']} edge(s), "
        f"{stats['bytes']} bytes to {out}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
