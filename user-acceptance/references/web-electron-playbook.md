# Web and Electron Evidence Playbook

Use the actual app and capture what a human would see. Tests can supplement this walkthrough after evidence is collected.

## Tool choice

- Prefer `agent-browser` for web apps and browser automation.
- Use `electron` plus `agent-browser` CDP for native Electron apps.
- Use `playwright` when the repo already uses Playwright, when traces are useful, or when `agent-browser` cannot complete the flow.
- Use `chrome-cdp` only when the user explicitly approved inspection of an already-open Chrome page.
- Use `pp-agent-capture` for app-window or browser-window recordings, screenshots, GIFs, and evidence bundles, especially for Electron or TUI-like visual states.

If the needed skill or CLI is missing, install it with `npx agents install <skill-name>`, then follow that skill's CLI install instructions.

## Evidence priority

1. Video of the feature flow, when practical.
2. Screenshots at start, key interaction, and final result.
3. Accessibility or DOM snapshots that confirm the state.
4. Console, network, or app logs when they explain behavior.

If video is skipped, record the reason in `evidence.md`.

## Web app workflow

1. Start the app with the repo's documented dev command.
2. Open the app in a real browser.
3. Navigate to the feature through the normal user path.
4. Capture a starting screenshot.
5. Perform the user actions: click, fill, select, scroll, upload, download, or navigate.
6. Capture video or screenshots through the meaningful checkpoints.
7. Confirm the final visible state with a fresh snapshot or screenshot.
8. Save logs or generated files that prove the result.

Example shape:

```bash
npm run dev 2>&1 | tee uat-evidence/web-<timestamp>/logs/dev-server.log
agent-browser open http://localhost:3000
agent-browser snapshot -i > uat-evidence/web-<timestamp>/logs/start-snapshot.txt
agent-browser screenshot uat-evidence/web-<timestamp>/screenshots/01-start.png
# interact with the feature using current element refs
agent-browser screenshot uat-evidence/web-<timestamp>/screenshots/02-result.png
agent-browser snapshot -i > uat-evidence/web-<timestamp>/logs/result-snapshot.txt
```

## Electron workflow

1. Quit any already-running instance if remote debugging flags must be applied at launch.
2. Launch the app with a remote debugging port.
3. Connect with `agent-browser`.
4. Select the correct Electron window or webview target.
5. Use the feature as a desktop user would.
6. Capture the app window with `pp-agent-capture` when window-level video is practical.
7. Save screenshots, snapshots, and logs.

Example shape:

```bash
open -a "MyApp" --args --remote-debugging-port=9222
agent-browser connect 9222
agent-browser tab
agent-browser snapshot -i > uat-evidence/electron-<timestamp>/logs/start-snapshot.txt
agent-browser screenshot uat-evidence/electron-<timestamp>/screenshots/01-start.png
# interact with the feature
agent-browser screenshot uat-evidence/electron-<timestamp>/screenshots/02-result.png
```

For video evidence, use the `pp-agent-capture` skill and target the app or browser window. Run its health and permission checks before recording.

## Manual instructions

Write normal user steps first:

```markdown
Manual Run Instructions:
1. Start the app with `<command>`.
   Expected: the app opens at `<url or window>`.
2. Go to `<screen>`.
   Expected: `<visible state>`.
3. Click `<control>` and enter `<sample input>`.
   Expected: `<result>`.
```

Keep automation commands, seeded data, and test harnesses out of the primary UI path. If unavoidable, place them under `Fallback (Engineering Only)` and explain why.
