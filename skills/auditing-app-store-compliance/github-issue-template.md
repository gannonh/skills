# GitHub Issue Template for App Store Audit

Create a GitHub issue with the following command:

```bash
gh issue create --title "[App Store Audit] Compliance Review - $(date +%Y-%m-%d)" --label "app-store,compliance,audit" --body "$(cat <<'EOF'
## Summary

| Category          | Critical | Warnings | Info  |
| ----------------- | -------- | -------- | ----- |
| Safety (1.x)      | X        | X        | X     |
| Performance (2.x) | X        | X        | X     |
| Business (3.x)    | X        | X        | X     |
| Design (4.x)      | X        | X        | X     |
| Legal (5.x)       | X        | X        | X     |
| Build/Binary      | X        | X        | X     |
| Third-Party SDKs  | X        | X        | X     |
| **Total**         | **X**    | **X**    | **X** |

## Critical Issues (Must Fix Before Submission)

### Privacy Manifest (Guideline 5.1)
- [ ] **[Certain]** Missing PrivacyInfo.xcprivacy
  - Location: Bundle root
  - Problem: Privacy manifest required since May 1, 2024
  - Resolution: Create PrivacyInfo.xcprivacy with required keys

### [Category]
- [ ] **[Confidence]** Issue title
  - Location: `path/file.swift:123`
  - Problem: Specific description
  - Resolution: Actionable fix

## Warnings (Should Address)

### [Category]
- [ ] **[Confidence]** Issue title
  - Location: `path/file.swift:123`
  - Problem: Specific description
  - Resolution: Actionable fix

## Recommendations

### [Category]
- [ ] **[Possible]** Issue title
  - Location: `path/file.swift:123`
  - Problem: Specific description
  - Resolution: Suggested improvement

## Verified Compliant

- [x] **Safety (1.x)** - No objectionable content, appropriate content moderation
- [x] **Performance (2.x)** - No placeholder content, accurate metadata
- [x] **Business (3.x)** - IAP properly implemented with restore mechanism
- [x] **Design (4.x)** - Sufficient functionality, SIWA present with social logins
- [x] **Legal (5.x)** - Privacy manifest complete, usage descriptions present
- [x] **Build** - Valid signature, correct architecture, proper entitlements

## Pre-Submission Checklist

- [ ] All critical issues resolved
- [ ] All warnings addressed or documented
- [ ] Privacy manifest includes all Required Reason APIs
- [ ] All usage descriptions are specific and meaningful
- [ ] Export compliance question answered in App Store Connect
- [ ] Age rating questionnaire completed
- [ ] App Store screenshots show actual app functionality
- [ ] Privacy policy URL is valid and accessible
- [ ] Account deletion mechanism tested
- [ ] Built with Xcode 16+ (required after April 2025)

## Confidence Levels

| Level        | Meaning                                              |
| ------------ | ---------------------------------------------------- |
| **Certain**  | Will cause rejection - clear guideline violation     |
| **Likely**   | Probably rejected - matches known rejection patterns |
| **Possible** | May be flagged - edge case, reviewer dependent       |

EOF
)"
```
