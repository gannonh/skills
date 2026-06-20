---
name: validate-kata-code-nightly-release
description: Validate Kata Code nightly releases on macOS with the @Computer plugin. Start and update the nightly app, use its New Project flow to create a timestamp-suffixed nightly UAT project under `/Volumes/EVO/dev`, then execute explicit acceptance criteria for a Codex GPT-5.4-Mini chat, Browser and Files panels, and git commit flow; capture criterion-level screenshots and write an evidence-linked report in the created project. Use when validating or documenting the Kata Code nightly release flow.
---

# Validate Kata Nightly

## Workflow

Use [@Computer](plugin://computer-use@openai-bundled) for every Kata Code UI action and visual check. Capture screenshots with the Computer plugin and copy each capture into the created project immediately.

1. Launch `/Applications/Kata Code (Nightly).app`. If the bundle is missing, download the latest nightly from the GitHub tags page.
2. Use `Check for Updates…` in the app menu and complete the update flow.
3. Use the app's New Project flow to create `/Volumes/EVO/dev/nightly-uat-<timestamp>`. Use the exact project name `nightly-uat-<timestamp>` and a timestamp unique to this run.
4. Copy [assets/report.md](assets/report.md) to the created project as `report.md`. Save all screenshots and any video recording in the created project.
5. Evaluate every acceptance criterion below. Capture a screenshot for each criterion, even when it fails, and save it as `AC##-<short-name>.png` in the created project.
6. Complete `report.md`. Mark each criterion `Pass`, `Fail`, or `Blocked`, include the exact evidence filename, and list all failures and blockers in the final summary.

## Acceptance Criteria

| ID | Criterion | Required screenshot |
| --- | --- | --- |
| AC01 | Kata Code (Nightly) opens successfully. | `AC01-app-launched.png` shows the running nightly app. |
| AC02 | `Check for Updates…` completes and the app reports the latest nightly is installed or restarts after installing it. | `AC02-update-check.png` shows the update result. |
| AC03 | The New Project flow creates and opens `/Volumes/EVO/dev/nightly-uat-<timestamp>`. | `AC03-new-project.png` shows the created project name or path. |
| AC04 | A new chat uses Codex with `GPT-5.4-Mini` and receives a response. | `AC04-codex-response.png` shows the selected model and response. |
| AC05 | The right-panel Browser loads `http://127.0.0.1:3774`. | `AC05-browser.png` shows the loaded local page. |
| AC06 | The right-panel Files view shows the created UAT project tree. | `AC06-files-panel.png` shows the project files. |
| AC07 | `nightly-uat.txt` appears as an untracked change before commit. | `AC07-untracked-file.png` shows the file in Files or Changes. |
| AC08 | The new file is committed and `git status` is clean. | `AC08-commit-clean.png` shows the commit result and clean status. |

## Notes

- Refresh Computer state after every UI change before selecting the next element.
- Use `osascript` for the app menu when needed.
- Use `open -n` for the nightly bundle if another Kata Code app is already running.
- Use the required filename for every acceptance-criteria screenshot.
- Save all evidence files and `report.md` inside the created `nightly-uat-<timestamp>` project.
- Record video only when the Computer plugin supports it for the active environment; save it in the created project.
