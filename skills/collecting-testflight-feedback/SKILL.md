---
name: collecting-testflight-feedback
description: Use this skill when collecting TestFlight feedback, gathering beta tester screenshots, reviewing App Store Connect feedback, or when the user asks to collect TestFlight comments, compile beta feedback, or create a feedback report. Creates consolidated markdown reports from App Store Connect.
---

# Collect TestFlight Screenshot Feedback

You are a browser automation assistant that collects TestFlight screenshot feedback from App Store Connect and creates a consolidated markdown report.

## Prerequisites

Before starting, ensure:
1. The user has the Claude browser extension installed and running
2. The user is logged into App Store Connect
3. The user has navigated to or can provide the TestFlight Screenshots Feedback page URL

## Workflow

### Step 1: Connect to Browser

1. Call `mcp__claude-in-chrome__tabs_context_mcp` to check for existing tabs
2. If no MCP tab group exists, call with `createIfEmpty: true`
3. Take a screenshot to see the current page state

### Step 2: Navigate to Feedback Page

If not already on the TestFlight Screenshot Feedback page:
1. Ask the user for the App Store Connect URL or app name
2. Navigate to: `https://appstoreconnect.apple.com/teams/{teamId}/apps/{appId}/testflight/screenshots`
3. Take a screenshot to confirm you're on the correct page

### Step 3: Collect Feedback Overview

1. Take a screenshot of the feedback list page
2. Count the total number of feedback items visible
3. Note the testers who submitted feedback
4. Create a todo list to track progress through each item

### Step 4: Iterate Through Each Feedback Item

For EACH feedback item on the page:

1. **Click on the feedback card** to open the detail modal
2. **Wait for modal to load** - take a screenshot to capture the modal view
3. **Extract ALL information** from the modal:
   - **Feedback text** (the user's comment - capture COMPLETELY)
   - **Submitted date and time**
   - **Reporter email**
   - **App Version** (e.g., "0.1.1 (3)")
   - **App Type**
   - **Uptime**
   - **Device** (e.g., "iPhone 14", "iPhone 16 Pro")
   - **iOS Version**
   - **Battery level**
   - **Time Zone**
   - **Architecture**
   - **Connection Type**
   - **Disk Free**
   - **Screen Resolution**
4. **Capture the screenshot**:
   - **Primary method**: Save the browser screenshot ID (from the screenshot action) - this captures the modal with the device screenshot visible
   - **Alternative**: If user provides image URLs (from right-click > Copy Image Address), download via curl
5. **Note the screenshot content** visible in the modal (describe what app screen is shown)
6. **Extract the feedback URL** from the browser address bar - this is the direct link to this feedback item
7. **Navigate to next item** using the right arrow button, or close modal and click next card

**CRITICAL**: Use `read_page` with `filter: interactive` to find navigation buttons. Look for refs like:
- `ref_193` or similar for "next" arrow
- `ref_192` or similar for "previous" arrow
- `ref_191` or similar for "OK" button to close modal

### Step 5: Screenshot Handling

**Method A: Browser Screenshots (Default - Fully Automated)**
- Each time you take a screenshot of a modal, you get a screenshot ID (e.g., `ss_1234abcd`)
- These screenshots are captured in the conversation and show the modal with the device screenshot
- Reference these in the report

**Method B: Direct Image Download (Higher Quality - Requires User Input)**
- User right-clicks on image in modal and selects "Copy Image Address"
- User provides the URL which looks like:
  ```
  https://tf-feedback.itunes.apple.com/eimg/{path}/fits1024x1024.jpg?...
  ```
- Download using curl:
  ```bash
  curl -s -o "{output_dir}/screenshots/{feedback_id}.jpg" "{image_url}"
  ```
- These are the original device screenshots at full resolution

### Step 6: Categorize Each Feedback Item

As you collect each item, categorize it as:
- **Bug**: Something is broken or not working as expected
- **Feature Request**: User wants new functionality
- **UX Feedback**: Suggestions about user experience, flow, or design
- **Unclear**: Feedback is incomplete or ambiguous

### Step 7: Generate Consolidated Report

Create a SINGLE markdown file with ALL feedback:

```markdown
---
collected: {CURRENT_DATETIME_UTC}
source: App Store Connect TestFlight
app: {APP_NAME}
feedback_count: {TOTAL_COUNT}
---

# TestFlight Feedback Report

**Collected:** {DATE}
**App:** {APP_NAME}
**Source:** [App Store Connect TestFlight Screenshots]({BASE_URL})

## Summary

| #   | Type    | Screen   | Reporter | Date   | Link          |
| --- | ------- | -------- | -------- | ------ | ------------- |
| 1   | Bug     | {Screen} | {Name}   | {Date} | [View]({URL}) |
| 2   | Feature | {Screen} | {Name}   | {Date} | [View]({URL}) |
...

---

## Bugs ({COUNT})

### #{N}: {Brief Title}

| Field           | Value                         |
| --------------- | ----------------------------- |
| **Reporter**    | {Name} ({email})              |
| **Submitted**   | {Date and Time}               |
| **Screen**      | {Screen name from screenshot} |
| **App Version** | {Version}                     |
| **Device**      | {Device}, {iOS Version}       |
| **Link**        | [{Feedback ID}]({FULL_URL})   |

**Feedback:**
> {Complete feedback text}

**Screenshot:**
![{Brief description}](screenshots/{feedback_id}.jpg)

---

## Feature Requests ({COUNT})

### #{N}: {Brief Title}
...

## UX Feedback ({COUNT})

### #{N}: {Brief Title}
...

## Unclear/Incomplete ({COUNT})

### #{N}: {Brief Title}
...

---

## Testers

| Tester | Email   | Count   |
| ------ | ------- | ------- |
| {Name} | {email} | {count} |

## App Versions Tested

| Version   | Build   | Feedback Count |
| --------- | ------- | -------------- |
| {version} | {build} | {count}        |

## Action Items

1. **Critical**: {Any high-priority bugs}
2. **Follow-up**: {Any incomplete feedback needing clarification}
3. **Consider**: {Notable feature requests}
```

### Step 8: Save the Report

1. Get the current datetime:
   ```bash
   date -u +"%Y-%m-%dT%H:%M:%SZ"
   ```
2. Determine the output location:
   - If the project has a `.planning/` directory, save to `.planning/feedback/`
   - Otherwise, save to the project root or ask the user
3. Create the directory structure:
   ```bash
   mkdir -p {output_dir}/screenshots
   ```
4. Name the file with date: `testflight-feedback-{YYYY-MM-DD}.md`

## URL Format Reference

**App Store Connect feedback URLs:**
```
https://appstoreconnect.apple.com/teams/{TEAM_ID}/apps/{APP_ID}/testflight/screenshots/{FEEDBACK_ID}
```

**TestFlight image URLs (for direct download):**
```
https://tf-feedback.itunes.apple.com/eimg/{PATH}/fits1024x1024.jpg?i_for={APP_ID}&AWSAccessKeyId=...&Expires=...&Signature=...
```

The `{FEEDBACK_ID}` is a unique identifier for each feedback item (e.g., `AFtdvEDGlXvlplPWXMe3CKQ`).

## Error Handling

- **Browser extension disconnects**: Call `tabs_context_mcp` to reconnect, then continue from where you left off
- **Modal won't close**: Try pressing `Escape` key, or use `read_page` to find the OK/Close button reference
- **Can't find next button**: Use `read_page` with `filter: interactive` to list all clickable elements in the modal
- **Page not loading**: Wait 2-3 seconds with `computer` action `wait`, then take a screenshot
- **Image URL blocked**: Fall back to browser screenshots (the modal screenshot captures the device screenshot visually)

## Important Notes

1. **Be thorough**: Capture ALL feedback text, even if it's long
2. **Preserve context**: Note what screen is shown in each screenshot
3. **Track URLs**: Every feedback item should have its direct App Store Connect link
4. **Categorize thoughtfully**: A bug is something broken; a feature request is something new
5. **Don't skip items**: Process every single feedback item on the page
6. **Update progress**: Use TodoWrite to track which items you've processed
7. **Screenshots**: Browser screenshots are automatic; direct image URLs require user to copy from context menu

## Example Session

User: `/collect-testflight-feedback`

1. Connect to browser → Take screenshot of current page
2. Confirm on TestFlight Screenshots page (or navigate there)
3. Count items: "I can see 11 feedback items from 2 testers"
4. Create todo list with 11 items
5. Click first feedback card → Take screenshot (captures modal with device screenshot) → Extract all info → Mark todo complete
6. Click next arrow → Take screenshot → Extract all info → Mark todo complete
7. ... repeat for all items ...
8. Generate consolidated markdown report with:
   - All feedback organized by type
   - Links back to App Store Connect for each item
   - Screenshots referenced (browser screenshots or downloaded images)
9. Save to `.planning/feedback/testflight-feedback-2026-01-08.md`
10. Report completion with summary of bugs/features found
