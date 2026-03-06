# Web / Electron Demo Playbook

Launch the actual app and use the feature as a real user would. This is not running tests — it is opening the app, navigating to the feature, and interacting with it live.

Use the `agent-browser` skill (or `electron` skill for Electron apps) to control the running app.

## Preflight

Before the first browser command in a session, confirm the automation path is healthy:

1. Run `agent-browser session list`
2. If it returns normally, proceed
3. If it fails with `Daemon failed to start`, assume stale daemon/socket state first, not product breakage

Stale daemon recovery:

```bash
ps aux | rg 'agent-browser/.*/dist/daemon.js'
kill <pid1> <pid2> ...
rm -f ~/.agent-browser/default.sock
agent-browser session list
```

Recovery is complete only when `agent-browser session list` returns normally.

Electron/web overlay check:

- If the app uses Agentation or similar dev overlays, verify the overlay is actually disabled before blaming `agent-browser`
- In Vite apps, check the real local env file the app loads, commonly `.env.local`
- For repos using `VITE_DISABLE_AGENTATION`, `1` means disabled and `0` means enabled
- Restart the dev process after changing the env file

Only fall back to a different tool after this preflight and recovery path has been attempted.

## Required Deliverable

After completing validation for a user-facing slice, the final user response must include:

- evidence from the run (screenshot/video/log excerpt), and
- a `Manual Run Instructions` section with numbered in-app steps

This is mandatory even when automated tests pass and the user did not explicitly ask for manual steps.

Primary manual instructions must use normal product-user flow.
Do not put test harness, seed state, or automation commands in primary manual steps.
If a fallback is needed, label it `Fallback (Engineering Only)`.

## Core Loop

For each acceptance slice:

1. **Start the app** — launch the dev server or Electron app (this must happen first)
2. **Verify agent-browser health** — `agent-browser session list`
3. **Navigate** to the screen where the feature lives
4. **Snapshot** to discover interactive elements (`agent-browser snapshot -i`)
5. **Use the feature** — click, fill, select, scroll as a real user would
6. **Screenshot** at each checkpoint to capture what the user sees
7. **Re-snapshot** after state changes to verify the expected outcome appeared
8. **Give the user run instructions** — after demoing each slice, tell the user exactly how to run the same demo themselves (what to start, what URL to open, what to click)

## Web App Example

```bash
# Step 1: Start the app (check package.json for the dev command)
npm run dev
# Wait for the dev server to be ready

# Step 2: Open the app in the browser and navigate to the feature
agent-browser open http://localhost:3000/login
agent-browser snapshot -i

# Step 3: Use the feature — fill the form and submit
agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --load networkidle

# Step 4: See what happened — screenshot the result
agent-browser screenshot /tmp/uat-login-result.png
agent-browser snapshot -i
# Confirm expected elements are present on the post-login page
```

## Electron App Example

```bash
# Step 1: Launch the Electron app with remote debugging
open -a "MyApp" --args --remote-debugging-port=9222

# Step 2: Confirm daemon health first
agent-browser session list

# Step 3: Connect agent-browser to the running app
agent-browser --cdp 9222 get url
agent-browser snapshot -i

# Step 4: Use the feature
agent-browser click @e5
agent-browser fill @e8 "sample input"
agent-browser click @e10
agent-browser wait 1500

# Step 5: See what happened
agent-browser screenshot /tmp/uat-electron-scenario.png
```

If Step 2 fails:

```bash
ps aux | rg 'agent-browser/.*/dist/daemon.js'
kill <pid1> <pid2> ...
rm -f ~/.agent-browser/default.sock
agent-browser session list
agent-browser --cdp 9222 get url
```

## Guidance

- Guide one scenario at a time: user action, expected result, what to report.
- Wait for user confirmation before moving to next scenario.
- Ask at least one "does this feel right?" UX confidence question per walkthrough.
- Provide instructions for the user to run the same demo themselves.
- Write manual instructions as normal UI clicks/inputs first; keep any engineering fallback separate.
- Prefer hands-on preview over abstract summary.
- Capture screenshots at minimum; include recording when useful.
