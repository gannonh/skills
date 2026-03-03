# CLI / API / Non-GUI Demo Playbook

For changes with no graphical interface: CLI tools, APIs, backend services, infrastructure, data pipelines.

## Core Loop

For each acceptance slice:

1. **Run** the command or request that exercises the changed behavior
2. **Capture** the exact command and key output lines (not raw dump)
3. **Translate** the technical output into user impact
4. **Provide** a one-liner the user can run independently to verify

## CLI Tool Example

```bash
# Before: show the old behavior (if relevant)
mytool process --input sample.csv 2>&1 | head -20

# After: show the new behavior
mytool process --input sample.csv --new-flag 2>&1 | head -20

# Verify: confirm expected output
mytool process --input sample.csv --new-flag | grep "expected_pattern"
echo "Exit code: $?"
```

## API Example

```bash
# Exercise the endpoint
curl -s -X POST http://localhost:8080/api/v1/resource \
  -H "Content-Type: application/json" \
  -d '{"field": "value"}' | jq .

# Verify response structure
curl -s http://localhost:8080/api/v1/resource/123 | jq '.status'

# Check error handling
curl -s -X POST http://localhost:8080/api/v1/resource \
  -d '{"invalid": true}' -w "\nHTTP Status: %{http_code}\n"
```

## Infrastructure / Config Example

```bash
# Show the change took effect
cat config/production.yml | grep relevant_setting

# Run targeted tests that exercise the change
npm test -- --grep "feature under test"

# Show logs/metrics if applicable
tail -20 /tmp/app.log | grep "relevant_event"
```

## Manual Proof Plan

When automated demo isn't possible (e.g., change requires deployed environment, third-party service, or hardware):

1. Describe what changed and why in 2-3 sentences
2. List exact steps the user can take to verify, numbered
3. State what they should see at each step
4. State what would indicate failure

Example:
```
## Verification Steps
1. Deploy to staging: `git push staging HEAD`
2. Open https://staging.example.com/settings
3. Click "Export Data" — should now show CSV format option
4. Select CSV and export — file should download with .csv extension
5. If export button is missing or file is .json, the change did not apply
```

## Guidance

- Show exact commands and key result lines, not raw output dumps.
- Translate every technical result into what it means for the user.
- Offer at least one short trust-check the user can run independently.
- For before/after comparisons, show both to make the change visible.
- Guide one scenario at a time: what you're proving, expected result, what to report.
