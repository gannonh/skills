# Web and Electron Evidence Playbook

Use the actual app and capture what a human would see. Tests can supplement this walkthrough after evidence is collected.

## Tool choice

- Prefer `agent-browser` for web apps and browser automation. Verify the installed CLI with `agent-browser --help` because command sets vary by version.
- Use Electron's CDP port plus `agent-browser --cdp <port>` for native Electron apps.
- Use the bundled `scripts/cdp-capture-page.mjs` when `agent-browser screenshot` hangs or cannot select the right target.
- Use `playwright` when the repo already uses Playwright, when traces are useful, or when `agent-browser` cannot complete the flow.
- Use `chrome-cdp` only when the user explicitly approved inspection of an already-open Chrome page.
- Use `pp-agent-capture` for app-window or browser-window recordings, screenshots, GIFs, and evidence bundles, especially for Electron or TUI-like visual states. On macOS, `screencapture -v` is an acceptable fallback when `pp-agent-capture` is unavailable.

If the needed skill or CLI is missing, install it with `npx agents install <skill-name>`, then follow that skill's installation instructions. Do not rely on `agent-browser skills get ...` unless the installed CLI confirms that command exists.

## Evidence priority

1. Video of the feature flow, when practical.
2. Screenshots at start, key interaction, and final result.
3. Accessibility, DOM, or body-text snapshots that confirm the state.
4. Console, network, or app logs when they explain behavior.
5. Negative evidence for bugfixes: saved searches showing the old error, flag, or stale wording is absent from logs and active source/docs.

If video is skipped, record the reason in `evidence.md`. If a preferred screenshot tool fails, use the next fallback and save a note in `logs/`.

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

Run Electron UAT in two lanes when the normal dev command cannot expose CDP cleanly.

### Lane A: product smoke path

1. Quit any stale app instance that would confuse the proof.
2. Run the product command a human would run, such as `pnpm desktop:dev`.
3. Save the full app/dev-server log and exit code.
4. Capture visible evidence if the app opens normally.
5. For bugfixes, search the log for the old crash/error and save the zero-match output.

### Lane B: instrumented evidence path

1. Check whether the default dev server and CDP ports are already occupied. Save listener output under `logs/`.
2. Choose a free CDP port. Avoid assuming `9222`.
3. Launch Electron with the remote debugging flag and the same app build/dev server used by the product path.
4. Connect with `agent-browser --cdp <port>` and select the app window target, not the DevTools target.
5. Use the feature as a desktop user would.
6. Capture video first when practical, then screenshots and text/DOM snapshots.
7. Save logs and clean up every process started for UAT.

Example shape:

```bash
node <skill-dir>/scripts/init-evidence.mjs --target electron --scope "Preferences dark mode persistence"
# Save normal product-command logs first.
node <skill-dir>/scripts/run-capture-command.mjs --evidence <dir> --name desktop-dev --allow-fail --timeout-ms 15000 -- pnpm --dir apps/desktop desktop:dev

# If CDP is needed, launch an instrumented app instance on a free port.
VITE_DEV_SERVER_URL=http://127.0.0.1:5174 pnpm --dir apps/desktop exec electron . --remote-debugging-port=9322 \
  > <dir>/logs/electron.log 2>&1 & echo $! > <dir>/logs/electron.pid
agent-browser --cdp 9322 tab list --json > <dir>/logs/cdp-tabs.json
agent-browser --cdp 9322 tab 1 --json
node <skill-dir>/scripts/cdp-capture-page.mjs --evidence <dir> --cdp http://127.0.0.1:9322 --title "Kata Desktop" --screenshot screenshots/01-start.png --text logs/01-start-text.txt
```

For video evidence, use `pp-agent-capture` when available. On macOS, `screencapture -v -V <seconds> -x -m <dir>/recordings/<name>.mov` can capture a short fallback recording. If display recording is unavailable or too broad, say so and rely on screenshot plus DOM/text evidence.

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
