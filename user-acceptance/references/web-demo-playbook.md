# Web / Electron Demo Playbook

Use the `agent-browser` skill (or `electron` skill for Electron apps) to run a live end-to-end demo.

## Core Loop

For each acceptance slice:

1. **Navigate** to the starting point of the user flow
2. **Snapshot** to discover interactive elements (`agent-browser snapshot -i`)
3. **Interact** using element refs to walk through the scenario
4. **Screenshot** at each checkpoint to capture evidence
5. **Re-snapshot** after navigation or state changes to verify expected result

## Web App Example

```bash
# Navigate and inspect
agent-browser open http://localhost:3000/login
agent-browser snapshot -i

# Execute the scenario
agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --load networkidle
agent-browser screenshot /tmp/uat-login-result.png

# Verify outcome
agent-browser snapshot -i
# Confirm expected elements are present on the post-login page
```

## Electron App Example

```bash
# Launch with remote debugging
open -a "MyApp" --args --remote-debugging-port=9222

# Connect and inspect
agent-browser connect 9222
agent-browser snapshot -i

# Execute scenario
agent-browser click @e5
agent-browser fill @e8 "sample input"
agent-browser click @e10
agent-browser wait 1500
agent-browser screenshot /tmp/uat-electron-scenario.png
```

## Guidance

- Guide one scenario at a time: user action, expected result, what to report.
- Wait for user confirmation before moving to next scenario.
- Ask at least one "does this feel right?" UX confidence question per walkthrough.
- Provide instructions for the user to run the same demo themselves.
- Prefer hands-on preview over abstract summary.
- Capture screenshots at minimum; include recording when useful.
