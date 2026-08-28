# App Store Reference Tables

## Confidence Levels

| Level        | Meaning              | Use When                                |
| ------------ | -------------------- | --------------------------------------- |
| **Certain**  | Will cause rejection | Clear guideline violation found in code |
| **Likely**   | Probably rejected    | Pattern matches known rejection reasons |
| **Possible** | May be flagged       | Edge case, depends on reviewer          |

---

## Common Rejection Causes

### Privacy (Most Common - ~25% of rejections)

| Issue                          | Detection                         | Resolution                               |
| ------------------------------ | --------------------------------- | ---------------------------------------- |
| Missing privacy manifest       | No PrivacyInfo.xcprivacy          | Create manifest with all 4 required keys |
| Undeclared Required Reason API | grep for API, missing in manifest | Add API type and reason codes            |
| Missing usage description      | API used without Info.plist key   | Add specific, meaningful description     |
| Generic usage description      | "This app needs camera"           | Explain why in context of app            |
| Missing privacy policy         | No URL in Info.plist/Settings     | Add privacy policy URL                   |
| No account deletion            | Settings missing delete option    | Add account deletion mechanism           |

### Performance

| Issue                   | Detection                               | Resolution                  |
| ----------------------- | --------------------------------------- | --------------------------- |
| Placeholder content     | grep for "lorem", "placeholder"         | Replace with real content   |
| Test code in production | grep for "test", "debug" outside Tests/ | Remove or wrap in #if DEBUG |
| TODO/FIXME markers      | grep for "TODO", "FIXME"                | Resolve or remove markers   |
| Incomplete features     | Disabled buttons, empty views           | Complete or remove features |

### Design

| Issue                      | Detection                  | Resolution                         |
| -------------------------- | -------------------------- | ---------------------------------- |
| Missing Sign in with Apple | Social logins without SIWA | Add ASAuthorizationAppleIDProvider |
| Minimum functionality      | App is just a web wrapper  | Add native features                |

### Business

| Issue                | Detection                     | Resolution                      |
| -------------------- | ----------------------------- | ------------------------------- |
| No restore purchases | IAP without restore mechanism | Add currentEntitlements/restore |
| StoreKit 1 usage     | SKPaymentQueue usage          | Migrate to StoreKit 2           |

---

## 2024-2025 Policy Timeline

| Date                  | Change                              |
| --------------------- | ----------------------------------- |
| **May 1, 2024**       | Privacy manifest enforcement begins |
| **April 24, 2025**    | Xcode 16 and iOS 18 SDK required    |
| **February 17, 2025** | EU trader status required           |
| **February 24, 2025** | New APNs server certificate         |
| **November 13, 2025** | Third-party AI disclosure required  |
| **January 31, 2026**  | Updated age rating questionnaire    |

---

## Binary Size Limits

| Constraint                      | Limit  |
| ------------------------------- | ------ |
| Maximum app size (uncompressed) | 4 GB   |
| Maximum executable (__TEXT)     | 500 MB |
| Cellular download threshold     | 200 MB |
| watchOS app limit               | 75 MB  |
| App Clip (digital, iOS 17+)     | 50 MB  |
| App Clip (physical, iOS 16+)    | 15 MB  |

---

## Screenshot Requirements

| Display     | Dimensions (Portrait) | Required               |
| ----------- | --------------------- | ---------------------- |
| 6.9" iPhone | 1320 × 2868 px        | Required if no 6.5"    |
| 6.5" iPhone | 1284 × 2778 px        | Fallback option        |
| 13" iPad    | 2064 × 2752 px        | Required for iPad apps |

**Metadata limits:**
- App name: 30 characters
- Subtitle: 30 characters
- Description: 4,000 characters
- Keywords: 100 characters
- Promotional text: 170 characters

---

## Entitlements Requiring Justification

- `com.apple.developer.healthkit`
- `com.apple.developer.homekit`
- `com.apple.developer.kernel.increased-memory-limit`
- `com.apple.developer.push-to-talk`
- `com.apple.developer.networking.HotspotConfiguration`

**Background modes requiring justification:**
- `audio`, `location`, `voip`, `fetch`, `remote-notification`
- `bluetooth-central`, `bluetooth-peripheral`, `processing`

---

## Required Reason API Codes

### UserDefaults (`NSPrivacyAccessedAPICategoryUserDefaults`)
- `CA92.1` - App-only access
- `1C8F.1` - App Group shared access

### File Timestamps (`NSPrivacyAccessedAPICategoryFileTimestamp`)
- `DDA9.1` - Displaying to user
- `C617.1` - App container access
- `3B52.1` - User-selected files via document picker

### System Boot Time (`NSPrivacyAccessedAPICategorySystemBootTime`)
- `35F9.1` - Elapsed time measurement
- `8FFB.1` - Calculating absolute timestamps

### Disk Space (`NSPrivacyAccessedAPICategoryDiskSpace`)
- `85F4.1` - Displaying disk space to users
- `E174.1` - Checking space for file operations

### Active Keyboards (`NSPrivacyAccessedAPICategoryActiveKeyboards`)
- `3EC4.1` - Custom keyboard apps
- `54BD.1` - UI customization based on keyboards
