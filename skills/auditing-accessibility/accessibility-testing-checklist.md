# Accessibility Inspector and Manual Testing

## Launch Accessibility Inspector
```bash
# Open Accessibility Inspector
open -a "Accessibility Inspector"
```

## Automated Audit Steps
1. Select your running simulator or connected device in the dropdown
2. Select your app as the target
3. Click "Audit" tab
4. Click "Run Audit" button
5. Review findings for each category:
   - **Contrast** — Color contrast issues
   - **Hit Region** — Touch target size issues
   - **Clipped Text** — Text truncation with Dynamic Type
   - **Element Description** — Missing labels/hints
   - **Traits** — Wrong accessibility traits

## Manual VoiceOver Testing

Enable VoiceOver: `Cmd+F5` (simulator) or Settings → Accessibility → VoiceOver

### Navigation Testing
1. ☐ Swipe right/left - moves logically through UI elements
2. ☐ Each element announces purpose clearly
3. ☐ No unlabeled elements (except decorative)
4. ☐ Heading navigation works (swipe up/down with 2 fingers)
5. ☐ Container navigation works (swipe left/right with 3 fingers)

### Interaction Testing
1. ☐ Double-tap activates buttons
2. ☐ Swipe up/down adjusts sliders/pickers
3. ☐ Custom gestures have VoiceOver equivalents
4. ☐ Text fields announce keyboard type
5. ☐ State changes are announced

### Content Testing
1. ☐ Images have descriptive labels or are hidden
2. ☐ Error messages are announced
3. ☐ Loading states are announced
4. ☐ Modal sheets announce role
5. ☐ Alerts announce automatically

---

# Audit Report Template

```markdown
# Accessibility Audit Report

**Target:** {target_path}
**Date:** {current_date}
**Auditor:** Claude Code

## Summary

| Category            | Issues | Severity |
| ------------------- | ------ | -------- |
| VoiceOver Labels    | X      | CRITICAL |
| Dynamic Type        | X      | HIGH     |
| Color Contrast      | X      | HIGH     |
| Touch Targets       | X      | MEDIUM   |
| Keyboard Navigation | X      | MEDIUM   |
| Reduce Motion       | X      | MEDIUM   |
| Common Violations   | X      | HIGH     |

## Critical Issues (Must Fix for App Store)

### VoiceOver
{list of VoiceOver issues}

### Dynamic Type
{list of Dynamic Type issues}

### Color Contrast
{list of color contrast issues}

## Medium Priority Issues

### Touch Targets
{list of touch target issues}

### Keyboard Navigation
{list of keyboard navigation issues}

### Reduce Motion
{list of reduce motion issues}

## Recommendations

1. {prioritized recommendation}
2. {prioritized recommendation}
3. {prioritized recommendation}

## WCAG Compliance Summary

- **Level A (Required):** {PASS/FAIL}
- **Level AA (Recommended):** {PASS/FAIL}
- **Level AAA (Enhanced):** {PASS/FAIL}
```
