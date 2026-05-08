---
name: user-acceptance
description: Use when finishing a ticket, feature branch, or pull request and the user asks to validate, demo, verify, sign off, show that it works, run UAT, provide acceptance evidence, or decide whether work is ready to merge. This skill gathers tangible evidence that completed work functions as intended, with videos, screenshots, terminal recordings, JSON responses, output files, logs, and a concise human test guide. Use for web apps, CLI and TUI apps, APIs and SDKs, and native Electron apps. Trigger on phrases like "UAT", "verify", "show me it works", "demo this", "walk me through", "ready to merge", "can we merge?", "acceptance test", "validate the changes", "sign off", or any request for proof that a feature branch or PR works.
---

# User Acceptance Evidence

## Operating brief

When this skill triggers, gather real evidence that the feature branch, ticket, or PR works. Treat the request as: "prove the completed work by exercising it and producing artifacts a human can inspect."

Acceptance evidence should be experiential and reproducible:

- For front ends, capture video when practical, then screenshots.
- For CLI and TUI apps, capture terminal transcripts, screenshots, recordings, generated files, and exit codes.
- For APIs and SDKs, capture requests, responses, output files, logs, and small runnable examples.
- For Electron apps, drive the real desktop app and capture visual evidence from the app window.

Automated tests can supplement UAT, but they do not replace an in-app walkthrough, command run, API call, or SDK example.

## Supported targets

Use this skill for:

1. Web apps
2. CLI and TUI apps
3. APIs and SDKs
4. Native Electron apps

If the requested target is outside this list, ask whether to proceed with a best-effort evidence plan.

## Hard gates

1. **Scope lock first**
   - Start with `UAT Scope: <ticket/PR/branch scope only>`.
   - If the scope is unclear, inspect the branch diff, PR, ticket, or ask the user.

2. **Evidence before recommendation**
   - Do not recommend merge based only on summaries, static code review, or green tests.
   - Exercise the changed behavior and save artifacts.

3. **Visible evidence for front ends**
   - For web and Electron work, capture video when practical.
   - If video is not practical, capture screenshots at meaningful checkpoints and state why video was skipped.

4. **Manual run instructions are mandatory**
   - Always include steps the human can run themselves.
   - For UI work, primary instructions must use normal product-user actions.
   - For CLI, TUI, API, or SDK work, include copy-pasteable commands or code snippets with expected outcomes.

5. **No GO verdict without explicit human acceptance**
   - Before user confirmation, use `Recommendation: Pending user sign-off`.
   - Use `GO` or `GO with follow-ups` only after the user explicitly accepts.

6. **Do not claim acceptance completion unilaterally**
   - Evidence collection supports acceptance.
   - The human grants acceptance.

## Tool selection

Load and use the best available skill or CLI for the target. If a required skill or CLI is unavailable, install it with `npx agents install <skill-name>`, then follow that skill's installation instructions for its underlying CLI.

| Target | Preferred tools | Evidence to capture |
| --- | --- | --- |
| Web app | `agent-browser`; `playwright` when the repo already uses Playwright or traces are useful; `chrome-cdp` only for an already-open Chrome page with user approval | Video, screenshots, DOM/accessibility snapshots, console/network notes |
| CLI app | Shell commands, `script`, generated output files; `pp-agent-capture` for terminal video/GIF when visual proof helps | Terminal transcript, exit codes, output files, JSON, screenshots/video for interactive flows |
| TUI app | `pp-agent-capture` for terminal recording or screenshots; terminal transcript where possible | Video/GIF, screenshots, transcript, config/output files |
| API | `curl`, HTTP client, repo scripts, logs | Request/response JSON, status codes, logs, saved payloads |
| SDK | Minimal runnable example in the target language, repo examples/tests only as supplement | Source snippet, command output, generated files, logs |
| Electron app | `electron` skill and `agent-browser` CDP automation; `pp-agent-capture` for app-window recording | Window video, screenshots, accessibility snapshots, logs |

Installation checks:

```bash
# Skill install pattern when a skill is missing
npx agents install agent-browser
npx agents install playwright
npx agents install chrome-cdp
npx agents install electron
npx agents install pp-agent-capture

# Then verify the underlying CLI required by the chosen skill
command -v agent-browser || true
command -v agent-capture-pp-cli || true
```

Do not install tools that are unrelated to the target.

## Evidence workspace

Write generated evidence under a repo-local folder:

```text
uat-evidence/<target>-<YYYYMMDD-HHMMSS>/
```

Create artifacts as appropriate:

```text
evidence.json          # machine-readable manifest
evidence.md            # concise human report
screenshots/           # PNG/JPG checkpoints
recordings/            # MP4/GIF terminal or UI recordings
responses/             # JSON/API/SDK outputs
logs/                  # command logs, server logs, console excerpts
outputs/               # generated files from the feature
```

Keep evidence paths stable and report them in the final answer. If `uat-evidence/` is not ignored by git, mention that it should be ignored before committing unless the user explicitly wants artifacts committed.

A minimal `evidence.json` should include:

```json
{
  "scope": "validated behavior",
  "target": "web|cli|tui|api|sdk|electron",
  "timestamp": "ISO-8601",
  "git_commit": "short sha",
  "artifacts": [
    {"type": "video|screenshot|json|log|output", "path": "relative/path", "description": "what it proves"}
  ],
  "commands": [
    {"command": "command run", "exit_code": 0, "output_path": "logs/example.log"}
  ],
  "slices": [
    {"name": "slice name", "result": "Pass|Fail", "evidence": ["relative/path"]}
  ]
}
```

## Workflow

### 1. Identify scope, target, and acceptance slices

- Inspect branch diff, PR description, ticket, README, package scripts, and app entry points as needed.
- Declare `UAT Scope: ...`.
- Declare `Target: web | cli | tui | api | sdk | electron | mixed`.
- Break the scope into 2 to 5 acceptance slices.
- Define visible pass/fail criteria for each slice.

### 2. Prepare the app or service

- Start the dev server, service, CLI, TUI, API, SDK fixture, or Electron app needed for the walkthrough.
- Prefer real local behavior over mocks.
- If credentials, services, hardware, or permissions block proof, record the blocker and provide the closest reproducible plan. Do not mark blocked slices as passed.

### 3. Execute the feature path

Use the matching playbook:

- Web and Electron: `references/web-electron-playbook.md`
- CLI, TUI, API, and SDK: `references/cli-api-sdk-playbook.md`

For mixed work, run the user-facing path first, then the technical proof tied to the same outcome.

### 4. Capture durable evidence

- Save artifacts under `uat-evidence/<target>-<timestamp>/`.
- Capture video for web/Electron/TUI when practical.
- Capture screenshots at the start, key state changes, and final success state.
- Capture command output with `tee` or saved logs.
- Save API/SDK JSON responses and generated output files.
- Write `evidence.json` and `evidence.md`.

### 5. Report results

Use this order:

1. `UAT Scope: ...`
2. `Target: ...`
3. `Slice-by-slice result`
4. `Evidence`
5. `Manual Run Instructions`
6. `Recommendation: Pending user sign-off`
7. `Please reply: accept / reject`

Keep the report concise. Link to artifact paths and explain what each artifact proves.

## Output contract

For every UAT response, include:

```markdown
UAT Scope: <scope>
Target: <web|cli|tui|api|sdk|electron|mixed>

Slice-by-slice result:
- Pass/Fail: <slice> - <one-line evidence summary>

Evidence:
- <artifact path> - <what it proves>

Manual Run Instructions:
1. <human step or command>
   Expected: <visible result or output>

Recommendation: Pending user sign-off
Please reply: accept / reject
```

For UI targets, manual instructions must start with normal user actions in the running app. Put automation commands or test harnesses only in a clearly labeled `Fallback (Engineering Only)` section.

For CLI, TUI, API, and SDK targets, manual instructions may be commands or code snippets, but they must include expected output and any required environment variables.

## Ticket update guidance

If a ticket or PR is known, offer or perform a status update with:

- Scope validated
- Target and tools used
- Slice pass/fail summary
- Evidence paths or links
- Manual run instructions
- Current recommendation

Before explicit user acceptance, label the update `Pending user sign-off`. After explicit acceptance, record the final verdict if the project workflow requires it.

## Pre-response self-check

Before responding, verify:

- Scope is stated.
- Target is stated.
- Each slice has pass/fail status.
- Evidence artifacts exist or blockers are clearly labeled.
- Front-end evidence includes video or a stated reason video was skipped.
- Manual run instructions are included.
- Recommendation remains `Pending user sign-off` unless the user has accepted.

## Common mistakes

- Running only tests and calling it UAT.
- Reporting a code summary without artifacts.
- Skipping video or screenshots for a front end without explanation.
- Providing Playwright or test commands as the primary manual UI path.
- Forgetting TUI visual evidence.
- Omitting API request and response files.
- Declaring `GO` before the user accepts.
- Installing every tool instead of selecting the best tool for the target.
