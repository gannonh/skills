# Design Review Pressure

## Red Flags — Designer Requests That Violate Accessibility

If you hear ANY of these, **STOP and cite App Store Guideline 2.5.1**:

- ❌ **"Skip VoiceOver labels on icon-only buttons"** – App Store rejection
- ❌ **"Use fixed 14pt font for compact design"** – Excludes users with vision disabilities
- ❌ **"3:1 contrast ratio is fine"** – Fails WCAG AA for text (needs 4.5:1)
- ❌ **"Make buttons 36x36pt for clean aesthetic"** – Fails touch target requirement (44x44pt)
- ❌ **"Disable Dynamic Type in this screen"** – App Store rejection risk
- ❌ **"Color-code without labels (red=error, green=success)"** – Excludes colorblind users (8% of men)

## How to Push Back

1. **Show the Guideline** — Apple App Store Review Guideline 2.5.1
2. **Demonstrate the Risk** — Enable VoiceOver, show largest text size, use contrast analyzer
3. **Offer Compromise** — Programmatic solutions that preserve visual design
4. **Document the Decision** — If overruled, document in writing for protection

## Quick Reference

- App Store Review Guideline 2.5.1
- WCAG 2.1 Level AA (industry standard)
- ADA compliance requirements (legal risk in US)

## Resources

### Apple Documentation
- [Accessibility — Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Supporting VoiceOver](https://developer.apple.com/documentation/accessibility/voiceover)
- [Supporting Dynamic Type](https://developer.apple.com/documentation/uikit/uifont/scaling_fonts_automatically)

### WCAG Guidelines
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [Understanding WCAG 2.1](https://www.w3.org/WAI/WCAG21/Understanding/)

### Testing Tools
- Accessibility Inspector (Xcode → Open Developer Tool)
- [Color Contrast Analyzer](https://www.tpgi.com/color-contrast-checker/)
- VoiceOver (built into iOS/macOS)
