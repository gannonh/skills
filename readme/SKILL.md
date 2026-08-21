---
name: readme
description: Write or rewrite a project README that leads with the problem, shows the tool working, and respects both skimmers and deep readers. Use when the user asks to create, write, rewrite, improve, or review a README, complains their README is too long, too marketing-heavy, or buries the install instructions, or says "make a README" / "fix my README".
---

# Readme

Write READMEs that answer three questions in order: what pain does this solve, how do I try it, how does it work. Readers arrive skeptical and busy; every sentence either moves them toward installing or loses them.

## Patterns

1. **Lead with the problem, not the framework.** "Coding agents forget everything between sessions. This fixes that." beats "A DevOps layer implementing the Three Ways." No jargon in the first line. Framework names and design rationale belong in the body.
2. **Acknowledge prior art.** If the approach resembles agile, CI/CD, spec-driven dev, or an existing tool, say so: "If you've used X, you know the problem. What's new here is Y." Experienced readers dismiss anything claiming to reinvent the wheel; claim only what's genuinely novel.
3. **Show, don't claim.** A terminal transcript or code snippet demonstrating the tool beats any adjective. Assertions without evidence read as marketing. If it can't be shown in a code block, it isn't ready for the README.
4. **State the differentiator once.** One explanation, one demonstration, done. Repeating the value proposition across sections turns documentation into ad copy.
5. **Trust block near install.** Anything that runs code, hooks, or modifies config needs, next to the install command: what files/hooks it touches, network calls or telemetry (or explicit local-only statement), permission surface, and how to disable/uninstall. Not buried in an FAQ.
6. **Collapse depth, don't delete it.** Architecture, theory, and reference material go in `<details>` blocks with markdown inside (blank line after `<summary>`, trailing blank line before `</details>`). Skimmers get the fast path; deep readers still get everything.
7. **No guru tone.** Strip "What N months taught me", "This is what makes X different", first-person journey narratives. Let the tool speak for itself.
8. **Order serves adoption.** Problem → Install/Trust → See It Work → Getting Started → How It Works (collapsed) → Reference → FAQ → Contributing/License. Theory comes after examples.

## Workflow

### 1. Gather context silently

Read what exists before asking anything: `README.md`, manifest (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`), `PRODUCT.md`, `LICENSE`, top-level source dirs. Infer name, language, install command, license, existing description.

### 2. Ask only what you can't infer

Batch remaining gaps into one round of questions, at most:
- The problem, one sentence (offer a suggestion from context if derivable)
- The simplest demo after install (command, snippet, or transcript)
- Trust concerns if the tool runs shell commands/hooks, touches config outside the project, or makes network calls

Skip any question the repo already answers.

### 3. Generate

Write the README using the patterns above. Structure serves the patterns, not a fixed template — a tiny CLI needs a fraction of what a framework needs. No emoji unless existing content uses them. Badges only if the repo already has them or the user asks.

For rewrites: keep accurate content, fix anti-patterns, preserve anything the current README gets right.

### 4. Self-review before finishing

Check the result against the anti-pattern table and fix violations:

| Anti-pattern | Fix |
|---|---|
| Value prop stated 3+ times | State once in the problem section, demonstrate once |
| Opens with methodology/framework name | Rewrite lead as problem statement |
| "What I learned", "this is what makes X different" | Delete; let the tool speak |
| Jargon before definition | Define on first use or use plain language |
| Security/permissions info below the fold | Move near install |
| Uninstall not findable | Add to trust block |
| Same install command in 3+ places | One hero install, one canonical reference |
| Architecture before examples | Move theory into collapsed details below demos |
| "Best"/"unique"/"powerful" without demo | Replace with example or delete |

Report which anti-patterns you found and fixed, so the user can veto intentional choices.
