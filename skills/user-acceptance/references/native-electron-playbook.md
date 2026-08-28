# Native and Electron Evidence Playbook

Use the actual native app window and capture what a human would see. Tests can supplement this walkthrough after evidence is collected.

## Tool choice

- Prefer Agent Browser with Electron's CDP port (`agent-browser --cdp <port>`) to drive the app, inspect DOM/accessibility state, capture screenshots, and record video evidence.
- Use Playwright Electron automation when the repo already uses Playwright, traces are useful, or Agent Browser cannot complete the flow.
- Use the bundled `scripts/cdp-capture-page.mjs` when `agent-browser screenshot` hangs or cannot select the right target.
- Use app logs, OS logs, and process output when they explain behavior or failure.
- For purely native apps without a web view or CDP surface, capture OS screenshots and accessibility snapshots with available tooling and state the limitation in `evidence.md`.

If the needed skill is missing, install it with:

```bash
npx skills add vercel-labs/agent-browser --skill agent-browser -y
npx skills add microsoft/playwright-cli --skill playwright-cli -y
```

Then verify the underlying CLI. Do not install unrelated tools.

## Evidence priority

1. Video of the real app-window feature flow, when practical, especially for UI changes involving interaction, layout, transitions, state changes, or error handling.
2. Screenshots at start, key interaction, and final result.
3. Accessibility snapshots or visible text from the real app window.
4. CDP DOM, console, network, or app logs when they explain behavior.
5. Negative evidence for bugfixes: saved searches showing the old crash, error, flag, or stale wording is absent from logs and active source/docs.

If video is skipped, record the reason in `evidence.md`. If Agent Browser or Playwright cannot drive the app, state the limitation and use the strongest available app-window evidence.

## Product smoke path

1. Quit stale app instances that would confuse the proof.
2. Run the product command a human would run, such as `pnpm desktop:dev`, `npm run electron:dev`, or opening the built app.
3. Save the full app/dev-server log and exit code.
4. Use Agent Browser (Electron CDP) or Playwright to interact through the visible app window.
5. Capture video plus screenshots at meaningful checkpoints.
6. For bugfixes, search the log for the old crash/error and save the zero-match output.
7. Save logs and clean up every process started for UAT, unless the user asked to keep the app running.

## Electron CDP evidence path

Use this path when CDP proof adds value or the normal product command cannot expose the needed state cleanly.

1. Check whether the default dev server and CDP ports are already occupied. Save listener output under `logs/`.
2. Choose a free CDP port. Avoid assuming `9222`.
3. Launch Electron with the remote debugging flag and the same app build/dev server used by the product path.
4. Connect with `agent-browser --cdp <port>` and select the app window target, not the DevTools target.
5. Use Agent Browser for visible app-window actions. Use CDP for DOM, console, network, or deterministic capture.
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

## End-to-end tests

After the walkthrough, create end-to-end tests that cover the new feature product area. These tests are the primary acceptance evidence.

- Prefer Playwright Electron automation, or the repo's existing e2e framework when present.
- Map each acceptance slice to at least one e2e test exercising the user-visible flow through the real app window.
- Save tests under `uat-evidence/electron-<timestamp>/tests/` or the repo's e2e directory per project convention; record the path in `evidence.md`.
- Run the tests and save per-test pass/fail, exit code, and trace or HTML report under `logs/` or `tests/`.
- The walkthrough proves the path; the tests lock it in as primary evidence.

## Adversarial evidence review

After collecting artifacts, ask an adversarial review subagent to compare the evidence against the spec, acceptance criteria, requirements, PR description, or ticket when subagents are available. The review must return `Pass` or `Fail` for each criterion and cite exact artifact paths or log lines. Treat missing video, missing screenshots, inaccessible files, or ambiguous proof as a failed criterion until corrected or explicitly documented as blocked.

If subagents are unavailable, perform the same check inline and label it `Inline adversarial review`.

## Manual instructions

Write normal user steps first:

```markdown
Manual Run Instructions:
1. Start the app with `<command>` or open `<app name>`.
   Expected: the app opens at `<window/screen>`.
2. Go to `<screen>`.
   Expected: `<visible state>`.
3. Click `<control>` and enter `<sample input>`.
   Expected: `<result>`.
```

Keep automation commands, seeded data, CDP commands, and test harnesses out of the primary UI path. If unavoidable, place them under `Fallback (Engineering Only)` and explain why.
