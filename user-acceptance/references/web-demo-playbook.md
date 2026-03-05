# Web / Electron Demo Playbook

Launch the actual app and use the feature as a real user would. This is not running tests — it is opening the app, navigating to the feature, and interacting with it live.

Use the `agent-browser` skill (or `electron` skill for Electron apps) to control the running app.

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
2. **Navigate** to the screen where the feature lives
3. **Snapshot** to discover interactive elements (`agent-browser snapshot -i`)
4. **Use the feature** — click, fill, select, scroll as a real user would
5. **Screenshot** at each checkpoint to capture what the user sees
6. **Re-snapshot** after state changes to verify the expected outcome appeared
7. **Give the user run instructions** — after demoing each slice, tell the user exactly how to run the same demo themselves (what to start, what URL to open, what to click)

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

# Step 2: Connect agent-browser to the running app
agent-browser connect 9222
agent-browser snapshot -i

# Step 3: Use the feature
agent-browser click @e5
agent-browser fill @e8 "sample input"
agent-browser click @e10
agent-browser wait 1500

# Step 4: See what happened
agent-browser screenshot /tmp/uat-electron-scenario.png
```

## Guidance

- Guide one scenario at a time: user action, expected result, what to report.
- Wait for user confirmation before moving to next scenario.
- Ask at least one "does this feel right?" UX confidence question per walkthrough.
- Provide instructions for the user to run the same demo themselves.
- Write manual instructions as normal UI clicks/inputs first; keep any engineering fallback separate.
- Prefer hands-on preview over abstract summary.
- Capture screenshots at minimum; include recording when useful.
