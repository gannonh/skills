# App Store Review Preparation

## Required Accessibility Features (iOS)

1. **VoiceOver Support**
   - All UI elements must have labels
   - Navigation must be logical
   - All actions must be performable

2. **Dynamic Type**
   - Text must scale from -3 to +12 sizes
   - Layout must adapt without clipping

3. **Sufficient Contrast**
   - Minimum 4.5:1 for normal text
   - Minimum 3:1 for large text (≥18pt)

## App Store Connect Metadata

When submitting, select supported accessibility features:
- ☑ VoiceOver
- ☑ Dynamic Type
- ☑ Increased Contrast
- ☑ Reduce Motion (if supported)

## Common Rejection Reasons

1. **"App is not fully functional with VoiceOver"**
   - Missing labels on images/buttons
   - Unlabeled custom controls
   - Actions not performable with VoiceOver

2. **"Text is not readable at all Dynamic Type sizes"**
   - Fixed font sizes
   - Text clipping at large sizes
   - Layout breaks at accessibility sizes

3. **"Insufficient color contrast"**
   - Text fails 4.5:1 ratio
   - UI elements fail 3:1 ratio
   - Color-only indicators
