# iOS / macOS Demo Playbook

Build and launch the actual app in the iOS Simulator, then use the feature as a real user would. This is not running XCTest or XCUITest — it is opening the app, navigating to the feature, and interacting with it live.

Use the `automating-ios-simulator` skill to control the running app.

## Core Loop

For each acceptance slice:

1. **Build and launch the app** in the simulator (this must happen first)
2. **Map** the screen to discover interactive elements
3. **Use the feature** — tap, type, swipe, scroll as a real user would
4. **Screenshot** at each checkpoint to capture what the user sees
5. **Re-map** after navigation or state changes to verify the expected outcome appeared
6. **Give the user run instructions** — after demoing each slice, tell the user exactly how to launch the app and reproduce the same walkthrough on their own device/simulator

## Example

```bash
# Step 1: Verify environment and build/launch the app
bash scripts/sim_health_check.sh
python scripts/app_launcher.py --launch com.example.myapp

# Step 2: See what's on screen
python scripts/screen_mapper.py

# Step 3: Use the feature — navigate to login, fill fields, submit
python scripts/navigator.py --find-text "Login" --tap
python scripts/navigator.py --find-type TextField --enter-text "user@example.com"
python scripts/navigator.py --find-text "Submit" --tap

# Step 4: See what happened
python scripts/screen_mapper.py
xcrun simctl io booted screenshot /tmp/uat-ios-scenario.png
```

## Guidance

- Use semantic navigation (find by text, type, accessibility ID) rather than coordinates. This survives UI changes.
- Use `screen_mapper.py` after each navigation step to verify the expected screen appeared.
- Use `app_state_capture.py` to create comprehensive debugging snapshots if something looks wrong.
- Use `test_recorder.py` to auto-document the walkthrough with screenshots and timing per step.
- Guide one scenario at a time: user action, expected result, what to report.
- Wait for user confirmation before moving to next scenario.
- Ask at least one "does this feel right?" UX confidence question per walkthrough.
- Provide instructions for the user to run the same demo on their own device/simulator.
