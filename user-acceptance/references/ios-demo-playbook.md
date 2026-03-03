# iOS / macOS Demo Playbook

Use the `automating-ios-simulator` skill to run a live end-to-end demo in the iOS Simulator.

## Core Loop

For each acceptance slice:

1. **Launch** the app in the simulator
2. **Map** the screen to discover interactive elements
3. **Interact** using semantic navigation (text, type, accessibility ID)
4. **Screenshot** at each checkpoint to capture evidence
5. **Re-map** after navigation or state changes to verify expected result

## Example

```bash
# Verify environment
bash scripts/sim_health_check.sh

# Launch app
python scripts/app_launcher.py --launch com.example.myapp

# Map screen to see interactive elements
python scripts/screen_mapper.py

# Execute the scenario
python scripts/navigator.py --find-text "Login" --tap
python scripts/navigator.py --find-type TextField --enter-text "user@example.com"
python scripts/navigator.py --find-text "Submit" --tap

# Capture evidence
python scripts/screen_mapper.py
# Screenshot is taken automatically; or use xcrun simctl io booted screenshot /tmp/uat-ios-scenario.png
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
