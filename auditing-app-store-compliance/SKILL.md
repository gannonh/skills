---
name: auditing-app-store-compliance
description: Comprehensive App Store compliance audit covering all 5 Apple guideline categories (Safety, Performance, Business, Design, Legal) with mandatory GitHub issue output
---

# App Store Compliance Audit

Perform a systematic App Store compliance audit covering all 5 Apple guideline categories. Produces actionable GitHub issue with specific findings, file paths, and confidence levels.

**Scope (optional)**: $ARGUMENTS

If no scope is provided, "all" is assumed.

**Core principle:** Thorough audit regardless of time pressure, scope narrowing, or past approval history. All 5 categories. GitHub issue output. No shortcuts.

---

## Step 1: Audit Scope Validation

**Mandatory requirements that CANNOT be skipped:**

1. All 5 categories: Safety, Performance, Business, Design, Legal
2. GitHub issue output: Structured issue with checkboxes
3. Specific locations: File paths and line numbers for all findings
4. Confidence levels: Certain/Likely/Possible for each finding

**Red flags - if you catch yourself thinking any of these, STOP:**
- "Quick check is fine given the timeline" → Full audit. Same process.
- "They just want privacy checked" → All 5 categories. Always.
- "They passed review before" → Previous approval is irrelevant.
- "Don't need GitHub issue, just tell them" → Issue is mandatory.
- "This seems simple" → Follow checklist completely.

---

## Step 2: Audit Safety Guidelines (1.x)

**Guideline Categories:**
- 1.1 Objectionable Content
- 1.2 User Generated Content
- 1.3 Kids Category
- 1.4 Physical Harm
- 1.5 Developer Information
- 1.6 Data Security

### 2.1 Search for content moderation mechanisms
```bash
# Check for content reporting/moderation
grep -ri "report\|block\|moderate\|flag" --include="*.swift" | head -20

# Check for UGC features without moderation
grep -ri "comment\|post\|upload\|share" --include="*.swift" | head -20
```

### 2.2 Check Kids Category requirements (if applicable)
```bash
# Check for advertising SDKs (not allowed in Kids)
grep -ri "AdMob\|Facebook.*Ad\|Unity.*Ads" --include="*.swift" | head -10

# Check for analytics that collect data
grep -ri "Analytics\|tracking\|IDFA" --include="*.swift" | head -10

# Check for external links (restricted in Kids)
grep -ri "openURL\|SFSafariViewController\|WKWebView" --include="*.swift" | head -10
```

### 2.3 Check for physical harm content
```bash
# Medical/health claims that need verification
grep -ri "cure\|treat\|diagnose\|medical\|health" --include="*.swift" | head -10

# Check for drug-related content
grep -ri "drug\|medication\|dose\|prescription" --include="*.swift" | head -10
```

### 2.4 Verify developer information
- Check Info.plist for valid support URL
- Verify App Store Connect contact information is complete

**Report findings as:**
```
Safety (1.x) Issues:
- [ ] **[Confidence]** {Issue} (Guideline 1.X.X)
  - Location: `path/file.swift:123`
  - Problem: {Specific issue}
  - Resolution: {Actionable fix}
```

---

## Step 3: Audit Performance Guidelines (2.x)

**Guideline Categories:**
- 2.1 App Completeness
- 2.2 Beta, Demo, Trial, and Test Versions
- 2.3 Accurate Metadata
- 2.4 Hardware Compatibility
- 2.5 Software Requirements

### 3.1 Search for placeholder/test content
```bash
# Placeholder content
grep -ri "lorem\|placeholder\|coming soon\|TBD\|TODO" --include="*.swift" | head -20

# Test/debug indicators in production code
grep -ri "test" --include="*.swift" | grep -v "Tests/" | grep -v "XCTest" | head -20

# Debug code
grep -ri "debug\|#if DEBUG" --include="*.swift" | head -20

# TODO/FIXME markers
grep -ri "TODO\|FIXME\|XXX\|HACK" --include="*.swift" | head -20

# Console logging that should be removed
grep -ri "print(\|NSLog\|debugPrint" --include="*.swift" | grep -v "Tests/" | head -20
```

### 3.2 Check for incomplete features
```bash
# Disabled buttons or features
grep -ri "isEnabled.*false\|disabled\|NotImplemented" --include="*.swift" | head -10

# Empty implementations
grep -ri "fatalError\|preconditionFailure\|assertionFailure" --include="*.swift" | head -10
```

### 3.3 Verify metadata accuracy
- Screenshots must show actual app functionality
- App description must match actual features
- No references to other platforms (Android, Windows)

### 3.4 Check hardware requirements
```bash
# Verify UIRequiredDeviceCapabilities
grep -A5 "UIRequiredDeviceCapabilities" */Info.plist
```

### 3.5 Software requirements check
```bash
# Check for deprecated APIs
grep -ri "@available.*deprecated" --include="*.swift" | head -10

# Check minimum deployment target
grep "IPHONEOS_DEPLOYMENT_TARGET" project.yml *.xcconfig 2>/dev/null
```

**Report findings as:**
```
Performance (2.x) Issues:
- [ ] **[Confidence]** {Issue} (Guideline 2.X.X)
  - Location: `path/file.swift:123`
  - Problem: {Specific issue}
  - Resolution: {Actionable fix}
```

---

## Step 4: Audit Business Guidelines (3.x)

**Guideline Categories:**
- 3.1 Payments (In-App Purchase)
- 3.2 Other Business Model Issues

### 4.1 Check In-App Purchase implementation
```bash
# StoreKit usage
grep -ri "StoreKit\|SKProduct\|Product\|purchase\|subscription" --include="*.swift" | head -20

# Check for StoreKit 2 (preferred) vs StoreKit 1 (deprecated)
grep -ri "SKPaymentQueue\|SKProductsRequest" --include="*.swift" | head -10

# Restore purchases mechanism
grep -ri "restore\|currentEntitlements\|AppStore.sync" --include="*.swift" | head -10
```

### 4.2 Verify subscription requirements
```bash
# Subscription disclosure
grep -ri "subscription\|renew\|billing\|cancel" --include="*.swift" | head -10

# Check for subscription terms display
grep -ri "terms\|conditions\|privacy.*policy" --include="*.swift" | head -10
```

### 4.3 Check for cryptocurrency/NFT features
```bash
# Crypto/NFT content
grep -ri "crypto\|bitcoin\|ethereum\|NFT\|blockchain\|wallet" --include="*.swift" | head -10
```

### 4.4 Verify advertising implementation
```bash
# Ad SDK usage
grep -ri "AdMob\|GAD\|Facebook.*Ad\|Unity.*Ads\|AppLovin" --include="*.swift" | head -10

# IDFA/ATT usage
grep -ri "IDFA\|advertisingIdentifier\|ATTrackingManager" --include="*.swift" | head -10
```

**Report findings as:**
```
Business (3.x) Issues:
- [ ] **[Confidence]** {Issue} (Guideline 3.X.X)
  - Location: `path/file.swift:123`
  - Problem: {Specific issue}
  - Resolution: {Actionable fix}
```

---

## Step 5: Audit Design Guidelines (4.x)

**Guideline Categories:**
- 4.1 Copycats
- 4.2 Minimum Functionality
- 4.3 Spam
- 4.4 Extensions
- 4.5 Apple Sites and Services
- 4.6 Alternate App Icons
- 4.7 HTML5 Games, Bots, etc.

### 5.1 Check for minimum functionality
- App must provide value beyond a simple website wrapper
- Must have sufficient features for standalone app
- No placeholder or "coming soon" screens

### 5.2 Check extension guidelines
```bash
# App extensions
grep -ri "NSExtension" */Info.plist
ls -la */Extensions/ 2>/dev/null

# Widget configuration
grep -ri "WidgetKit\|TimelineProvider" --include="*.swift" | head -10
```

### 5.3 Check Apple service usage
```bash
# Sign in with Apple (required if social logins present)
grep -ri "ASAuthorization\|SignInWithApple\|ASAuthorizationAppleIDProvider" --include="*.swift" | head -10

# Other social logins (SIWA required if these exist)
grep -ri "Google.*SignIn\|Facebook.*Login\|Twitter.*Login" --include="*.swift" | head -10
```

### 5.4 Check for App Clip requirements (if applicable)
```bash
# App Clip target
grep -ri "app-clip\|AppClip" project.yml *.xcconfig 2>/dev/null

# App Clip size (must be under 50MB for digital, 15MB for physical)
```

**Report findings as:**
```
Design (4.x) Issues:
- [ ] **[Confidence]** {Issue} (Guideline 4.X.X)
  - Location: `path/file.swift:123`
  - Problem: {Specific issue}
  - Resolution: {Actionable fix}
```

---

## Step 6: Audit Legal Guidelines (5.x)

**Guideline Categories:**
- 5.1 Privacy (CRITICAL - Most common rejection cause)
- 5.2 Intellectual Property
- 5.3 Gaming, Gambling, and Lotteries
- 5.4 VPN Apps
- 5.5 Mobile Device Management
- 5.6 Developer Code of Conduct

### 6.1 Privacy Manifest Validation (CRITICAL)

Check for `PrivacyInfo.xcprivacy` at bundle root:
```bash
# Find privacy manifest
find . -name "PrivacyInfo.xcprivacy" -type f

# Verify required keys exist
grep -E "NSPrivacyTracking|NSPrivacyTrackingDomains|NSPrivacyCollectedDataTypes|NSPrivacyAccessedAPITypes" */PrivacyInfo.xcprivacy
```

**Required privacy manifest structure:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
    <key>NSPrivacyTracking</key>
    <false/>
    <key>NSPrivacyTrackingDomains</key>
    <array/>
    <key>NSPrivacyCollectedDataTypes</key>
    <array/>
    <key>NSPrivacyAccessedAPITypes</key>
    <array>
        <!-- Each API type with reasons -->
    </array>
</dict>
</plist>
```

### 6.2 Required Reason API Detection

Search for APIs that require declaration in privacy manifest:

```bash
# UserDefaults (requires CA92.1 or 1C8F.1)
grep -r "UserDefaults" --include="*.swift" --include="*.m" | head -10

# File Timestamps (requires DDA9.1, C617.1, or 3B52.1)
grep -rE "(creationDate|modificationDate|getattrlist|stat\(|fstat\(|lstat\()" --include="*.swift" | head -10

# System Boot Time (requires 35F9.1 or 8FFB.1)
grep -rE "(systemUptime|mach_absolute_time)" --include="*.swift" | head -10

# Disk Space (requires 85F4.1 or E174.1)
grep -rE "(volumeAvailableCapacity|systemFreeSize|statfs|statvfs)" --include="*.swift" | head -10

# Active Keyboards (requires 3EC4.1 or 54BD.1)
grep -rE "activeInputModes" --include="*.swift" | head -10
```

### 6.3 Info.plist Usage Description Verification

Check all required usage descriptions:
```bash
# Extract all NS*UsageDescription keys
grep -E "NS.*UsageDescription" */Info.plist
```

**Required keys based on API usage:**

| API/Framework         | Required Key                                   | Example Description                  |
| --------------------- | ---------------------------------------------- | ------------------------------------ |
| Camera                | `NSCameraUsageDescription`                     | "Take photos for your profile"       |
| Microphone            | `NSMicrophoneUsageDescription`                 | "Record voice messages"              |
| Photo Library (read)  | `NSPhotoLibraryUsageDescription`               | "Select photos to share"             |
| Photo Library (write) | `NSPhotoLibraryAddUsageDescription`            | "Save edited images"                 |
| Location (foreground) | `NSLocationWhenInUseUsageDescription`          | "Find nearby restaurants"            |
| Location (background) | `NSLocationAlwaysAndWhenInUseUsageDescription` | "Track your workout route"           |
| Contacts              | `NSContactsUsageDescription`                   | "Find friends already using the app" |
| Calendar              | `NSCalendarsUsageDescription`                  | "Add events to your calendar"        |
| Bluetooth             | `NSBluetoothAlwaysUsageDescription`            | "Connect to fitness devices"         |
| Motion                | `NSMotionUsageDescription`                     | "Count your steps"                   |
| HealthKit (read)      | `NSHealthShareUsageDescription`                | "View your health data"              |
| HealthKit (write)     | `NSHealthUpdateUsageDescription`               | "Save workout data"                  |
| Face ID               | `NSFaceIDUsageDescription`                     | "Unlock securely with Face ID"       |
| Speech Recognition    | `NSSpeechRecognitionUsageDescription`          | "Transcribe voice notes"             |
| Local Network         | `NSLocalNetworkUsageDescription`               | "Discover devices on your network"   |
| Tracking (ATT)        | `NSUserTrackingUsageDescription`               | "Deliver personalized ads"           |

```bash
# Check for APIs without corresponding usage descriptions
# Camera
grep -ri "AVCaptureSession\|UIImagePickerController.*camera" --include="*.swift" | head -5

# Microphone
grep -ri "AVAudioRecorder\|AVAudioSession.*record" --include="*.swift" | head -5

# Photos
grep -ri "PHPhotoLibrary\|UIImagePickerController" --include="*.swift" | head -5

# Location
grep -ri "CLLocationManager\|CoreLocation" --include="*.swift" | head -5

# Contacts
grep -ri "CNContactStore\|Contacts" --include="*.swift" | head -5

# HealthKit
grep -ri "HKHealthStore\|HealthKit" --include="*.swift" | head -5

# Face ID
grep -ri "LAContext\|LocalAuthentication" --include="*.swift" | head -5
```

### 6.4 Privacy Policy Verification
```bash
# Check for privacy policy URL
grep -ri "privacy.*policy\|privacyPolicy" */Info.plist --include="*.swift" | head -5

# Check App Store Connect metadata (manual verification required)
```

### 6.5 Account Deletion Requirement (Mandatory since 2022)
```bash
# Check for account deletion mechanism
grep -ri "delete.*account\|deleteAccount\|removeAccount" --include="*.swift" | head -10
```

### 6.6 App Tracking Transparency (if tracking)
```bash
# Check ATT implementation
grep -ri "ATTrackingManager\|requestTrackingAuthorization" --include="*.swift" | head -10

# Check IDFA usage
grep -ri "advertisingIdentifier\|IDFA" --include="*.swift" | head -10
```

### 6.7 Data Collection Disclosure
```bash
# Check for analytics SDKs
grep -ri "Firebase.*Analytics\|Mixpanel\|Amplitude\|Segment" --include="*.swift" | head -10

# Check for third-party SDKs requiring disclosure
grep -ri "Facebook\|Google\|Twitter\|TikTok" --include="*.swift" | head -10
```

**Report findings as:**
```
Legal (5.x) Issues:
- [ ] **[Confidence]** {Issue} (Guideline 5.X.X)
  - Location: `path/file.swift:123`
  - Problem: {Specific issue}
  - Resolution: {Actionable fix}
```

---

## Step 7: Build and Binary Verification

### 7.1 Check Xcode version requirement
```bash
# After April 24, 2025: Xcode 16+ and iOS 18 SDK required
xcodebuild -version
```

### 7.2 Verify code signing
```bash
# Verify code signature (run on built app)
codesign -vvv --deep --strict *.app 2>&1 | head -20

# View entitlements
codesign -d --entitlements - *.app 2>&1 | head -30

# Check provisioning profile
security cms -D -i */embedded.mobileprovision 2>&1 | head -50
```

### 7.3 Validate Info.plist
```bash
# Lint Info.plist
plutil -lint */Info.plist

# Check export compliance
grep "ITSAppUsesNonExemptEncryption" */Info.plist
```

### 7.4 Check architectures
```bash
# Verify arm64 architecture
lipo -info *.app/* 2>/dev/null | grep -v "is not an object" | head -10
```

### 7.5 Check app size constraints
```bash
# Maximum app size: 4 GB uncompressed
# Maximum executable: 500 MB
# Cellular download threshold: 200 MB

# Check bundle size
du -sh *.app 2>/dev/null
```

### 7.6 Check APNs environment
```bash
# Verify production (not development) for release
grep "aps-environment" *.entitlements */embedded.mobileprovision 2>/dev/null
```

**Report findings as:**
```
Build/Binary Issues:
- [ ] **[Confidence]** {Issue}
  - Problem: {Specific issue}
  - Resolution: {Actionable fix}
```

---

## Step 8: Third-Party SDK Compliance

### 8.1 Check for SDKs requiring privacy manifests

Apple's list of 86+ SDKs requiring privacy manifests includes:

**Facebook/Meta:**
- FBSDKCoreKit, FBSDKLoginKit, FBSDKShareKit, FBAEMKit

**Firebase:**
- FirebaseCore, FirebaseAuth, FirebaseCrashlytics, FirebaseMessaging, FirebaseAnalytics

**Google:**
- GoogleSignIn, GoogleUtilities, GTMSessionFetcher

**Popular Libraries:**
- Alamofire, AFNetworking, SDWebImage, Kingfisher, Lottie, SnapKit, RealmSwift, RxSwift

```bash
# Check Podfile for common SDKs
grep -E "Firebase|Facebook|Google|Alamofire|SDWebImage|Kingfisher|Lottie|SnapKit|Realm|RxSwift" Podfile 2>/dev/null

# Check Package.swift
grep -E "firebase|facebook|google|alamofire|sdwebimage|kingfisher|lottie|snapkit|realm|rxswift" Package.swift 2>/dev/null

# Check for privacy manifests in Pods
find Pods -name "PrivacyInfo.xcprivacy" 2>/dev/null | head -20
```

### 8.2 Generate privacy report
```
After archiving in Xcode:
Product → Archive → Right-click archive → Generate Privacy Report
```

**Report findings as:**
```
Third-Party SDK Issues:
- [ ] **[Confidence]** {SDK} missing privacy manifest
  - Resolution: Update to version X.X.X or later
```

---

## Step 9: Create GitHub Issue

**See `./github-issue-template.md` for the complete issue template with:**
- Summary table by category
- Critical issues, warnings, recommendations sections
- Pre-submission checklist
- Confidence levels reference

---

## Reference Documents

For detailed reference material, see:
- `./app-store-reference-tables.md` — Confidence levels, rejection causes, policy timeline, binary limits, screenshot requirements, entitlements, and Required Reason API codes
- `./github-issue-template.md` — GitHub issue template for audit results
