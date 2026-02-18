---
name: writing-ios-unit-tests
description: Use this skill when writing iOS unit tests, debugging test failures, creating Swift Testing tests, testing SwiftData models, or when the user asks to add tests, fix tests, improve coverage, or test Swift code. Covers Swift Testing framework, ModelContainer lifecycle, and coverage requirements.
---

# iOS Unit Testing (Swift Testing)

**Three core principles ensure reliable unit tests:**

1. **Use Swift Testing framework** - Modern `@Test` and `#expect` syntax for new tests
2. **Keep container alive** - Always capture ModelContainer when using SwiftData contexts
3. **Safe unwrapping patterns** - Never force unwrap; use guard with explicit failures

## Scope

**If input arguments provided:**

Scope / file pattern: $ARGUMENTS

**else:**

Scope:
- Determine what unit tests need to be created or updated based on either:
  A - New or modified code in the current phase/PR (analyze changed files and map to testable components); or
  B - Coverage gaps identified by `./scripts/check-coverage.sh`
- Investigate existing tests to avoid duplicative test classes or methods
- Check coverage tier requirements in `coverage-config.json`

## ⛔️ MANDATORY: When Tests Fail, Debug First

**STOP. Before changing ANY code when a test fails, you MUST analyze the error:**

### Step 1: Read the Full Error Message
```bash
cat logs/latest/raw_output.txt
```

### Step 2: Check Test Isolation
- Is the test failing due to shared state?
- Is ModelContainer being deallocated prematurely?

### Step 3: Add Debug Output
```swift
print("DEBUG: value = \(value)")
#expect(value != nil, "Value was nil - check initialization path")
```

### Step 4: Analyze BEFORE Changing Code
- **Error message shows**: What assertion failed and why
- **Stack trace shows**: Where in the code the failure occurred
- **Debug output shows**: Actual vs expected values

### ❌ DO NOT:
- Guess at why tests fail without reading errors
- Change production code to make tests pass
- Remove or weaken assertions

### ✅ ALWAYS:
- Read the full error output first
- Verify test data setup is correct
- Check ModelContainer lifecycle
- Only then make targeted fixes based on evidence

---

## Framework Overview

- **Framework**: Swift Testing (modern, preferred) + XCTest (legacy)
- **Config**: project.yml (XcodeGen) or .xcodeproj
- **Output Formatter**: xcbeautify
- **Unit Test Directory**: {ProjectName}Tests/
- **Naming Pattern**: *Tests.swift

## Swift Testing vs XCTest

**✅ Swift Testing - Modern, cleaner syntax (USE THIS):**
```swift
import Testing
@testable import AppName

@Test("User creation with valid data")
func testUserCreation() {
    let user = User(email: "test@example.com", name: "Test User")
    #expect(user.email == "test@example.com")
    #expect(user.name == "Test User")
}
```

**❌ XCTest - Legacy syntax (avoid in new tests):**
```swift
func testUserCreation() throws {
    let user = User(email: "test@example.com", name: "Test User")
    XCTAssertEqual(user.email, "test@example.com")
    XCTAssertEqual(user.name, "Test User")
}
```

## Basic Test Structure

```swift
import Testing
@testable import AppName

@Suite("FeatureName Tests")
struct FeatureNameTests {

    @Test("Calculate next scheduled event time")
    @MainActor
    func testGetNextScheduledTime() async {
        // Given
        let (context, container) = createTestContext()
        _ = container  // Keep alive
        let viewModel = ScheduleViewModel()

        // When
        let nextTime = viewModel.getNextScheduledTime()

        // Then
        #expect(nextTime != nil, "Expected non-nil value")
    }
}
```

## SwiftData Testing Patterns (CRITICAL)

**See `./swiftdata-testing-patterns.md` for complete patterns including:**
- Creating test context with proper container lifecycle
- The critical relationship anti-pattern that causes crashes
- Why array assignment to relationships fails in tests

## Safe Unwrapping Patterns

### Avoid Force Unwrapping

```swift
// ❌ Avoid force unwrapping that can crash tests
let result = viewModel.calculateDose()!

// ✅ Use safe unwrapping with explicit test failures
guard let result = viewModel.calculateDose() else {
    #expect(Bool(false), "calculateDose() returned nil unexpectedly")
    return
}

// ✅ Alternative pattern with nil validation
let result = viewModel.calculateDose()
#expect(result != nil, "Expected calculateDose() to return a value")
```

## Tolerance-Based Assertions

### Time/Date Comparisons

```swift
// ❌ Exact time comparisons can be flaky
#expect(nextDose == expectedDate)

// ✅ Use tolerance for time-based assertions
let timeDifference = abs(nextDose.timeIntervalSince(expectedDate))
#expect(timeDifference < 60, "Time should be within 1 minute tolerance")

// ✅ For dose scheduling (more generous tolerance)
let timeDifference = abs(nextDoseTime.timeIntervalSinceNow)
#expect(timeDifference < 24 * 60 * 60, "Next dose should be within 24 hours")
```

## Async Testing Best Practices

### @MainActor for UI Components

```swift
// Always mark async tests with @MainActor when testing UI components
@Test("Verify medication profile selection updates state")
@MainActor
func testMedicationProfileSelection() async {
    let viewModel = OnboardingViewModel()
    let medication = Medication.semaglutide

    // Test async state changes
    await viewModel.selectMedication(medication)

    #expect(viewModel.selectedMedication == medication)
    #expect(viewModel.canProceedToNextStep == true)
}
```

## Common Test Patterns

### Testing Error Handling

```swift
@Test("Invalid dose amount throws appropriate error")
func testInvalidDoseThrowsError() async {
    let validator = DoseValidator()

    await #expect(throws: MedicationError.invalidDose) {
        try validator.validate(dose: -1.0, medication: .semaglutide)
    }
}
```

### Testing State Changes

```swift
@Test("ViewModel updates state correctly on user action")
@MainActor
func testViewModelStateChange() async {
    let viewModel = OnboardingViewModel()

    // Initial state
    #expect(viewModel.currentStep == .welcome)
    #expect(viewModel.canProceedToNextStep == true)

    // Trigger state change
    await viewModel.proceedToNextStep()

    // Verify new state
    #expect(viewModel.currentStep == .medicationSelection)
}
```

### Testing Computed Properties

```swift
@Test("MedicationProfile computes next dose time correctly")
func testNextDoseTimeComputation() {
    let profile = MedicationProfile.testProfile()
    profile.frequency = .weekly
    profile.lastDoseDate = Date().addingTimeInterval(-7 * 24 * 60 * 60) // 1 week ago

    let nextDose = profile.nextDoseTime

    // Should be approximately now (within 1 hour tolerance)
    let timeDifference = abs(nextDose.timeIntervalSinceNow)
    #expect(timeDifference < 3600)
}
```

## Mocking Patterns

### Protocol-Based Mocking

```swift
// Protocol
protocol NotificationCenterProtocol {
    func requestAuthorization(options: UNAuthorizationOptions) async throws -> Bool
    func add(_ request: UNNotificationRequest) async throws
}

// Production
extension UNUserNotificationCenter: NotificationCenterProtocol {}

// Mock
class MockNotificationCenter: NotificationCenterProtocol {
    var authorizationResult = true
    var addedRequests: [UNNotificationRequest] = []

    func requestAuthorization(options: UNAuthorizationOptions) async throws -> Bool {
        return authorizationResult
    }

    func add(_ request: UNNotificationRequest) async throws {
        addedRequests.append(request)
    }
}
```

**What to Mock:**
- External services (NotificationCenter, URLSession)
- System frameworks (HealthKit, StoreKit)
- Time-dependent operations

**What NOT to Mock:**
- Internal services (test with real implementations)
- SwiftData (use in-memory container)
- Pure functions

## Test Factories for Consistency

### Extension-Based Factories

```swift
extension User {
    static func testUser(
        email: String = "test@example.com",
        name: String? = "Test User",
        weight: Double = 70.0
    ) -> User {
        User(email: email, name: name, weight: weight)
    }
}

extension MedicationProfile {
    static func testProfile(
        genericName: String = "semaglutide",
        brandName: String = "Ozempic",
        currentDose: Double = 0.5
    ) -> MedicationProfile {
        MedicationProfile(
            genericName: genericName,
            brandName: brandName,
            currentDose: currentDose
        )
    }
}
```

## Test Data Seeding

### Using Preset Configurations

```swift
@Test("Test with seeded data")
@MainActor
func myTest() throws {
    let container = try TestDataSeeding.createTestContainer()
    let context = container.mainContext

    // Seed data with preset config
    let result = try TestDataSeeding.seedData(
        into: context,
        config: .thirtyDays  // 30 days, ~4-5 doses, 95% adherence
    )

    // Use seeded data
    #expect(result.doses.count > 0)
    #expect(result.adherenceRate >= 0.90)
}
```

### Available Presets

| Preset       | Days | Adherence | Use Case           |
| ------------ | ---- | --------- | ------------------ |
| `.sevenDays` | 7    | 100%      | Quick tests        |
| `.thirtyDays`| 30   | 95%       | Standard tests     |
| `.ninetyDays`| 90   | 93%       | Performance tests  |
| `.oneYear`   | 365  | 92%       | Stress tests       |
| `.twoYears`  | 730  | 90%       | Edge case tests    |

## Coverage Policy (5-Tier System)

**See `./coverage-policy-tiers.md` for complete coverage requirements including:**
- Tier thresholds by category (90% for business logic, 85% for ViewModels, etc.)
- Coverage workflow commands
- Common coverage issues and solutions

## Running Unit Tests

### Using Project Scripts (Recommended)

```bash
# Run all unit tests
./scripts/test.sh unit 1

# Run specific test suite
./scripts/test.sh unit 1 MyServiceTests

# Run with coverage
./scripts/test.sh unit 1 --coverage

# Silent mode (log only, no console output)
./scripts/test.sh unit 1 --coverage --log-only

# View latest test results
cat logs/latest/raw_output.txt
```

### Using xcodebuild Directly

```bash
# Run all unit tests
xcodebuild test \
  -scheme AppName \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro,OS=26.2' \
  -only-testing:AppNameTests \
  | xcbeautify

# Run with coverage enabled
xcodebuild test \
  -scheme AppName \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro,OS=26.2' \
  -enableCodeCoverage YES \
  -resultBundlePath .coverage/coverage.xcresult \
  -only-testing:AppNameTests \
  | xcbeautify
```

### Swift Testing Framework Limitations

**Unit Test Targeting Support:**
- ✅ **Target Level**: `-only-testing:AppNameTests` (all unit tests)
- ✅ **Suite Level**: `-only-testing:AppNameTests/MyServiceTests` (specific test suite)
- ❌ **Method Level**: Swift Testing doesn't support individual method isolation

## Integration Testing Patterns

### Testing Component Interactions

```swift
@Test("AnalyticsService coordinates User, Dose, and MedicationProfile correctly")
@MainActor
func testAnalyticsServiceIntegration() async throws {
    let (context, container) = createTestContext()
    _ = container

    // Seed realistic test data
    let result = try TestDataSeeding.seedData(
        into: context,
        config: .thirtyDays
    )

    let analyticsService = AnalyticsService(context: context)

    // Test cross-model analytics coordination
    let summary = await analyticsService.generateUserSummary(for: result.user)

    #expect(summary.overallAdherence >= 0.90)
    #expect(summary.medicationEffectiveness.count > 0)
}
```

## Complete Example

```swift
import Testing
@testable import AppName

@Suite("PharmacokineticsEngine Tests")
final class PharmacokineticsEngineTests {

    // MARK: - Test Data Setup

    func createTestContext() -> (ModelContext, ModelContainer) {
        let schema = Schema([User.self, MedicationProfile.self, Dose.self])
        let config = ModelConfiguration(
            schema: schema,
            isStoredInMemoryOnly: true,
            cloudKitDatabase: .none
        )
        let container = try! ModelContainer(for: schema, configurations: [config])
        return (ModelContext(container), container)
    }

    // MARK: - Tests

    @Test("Calculate concentration for single dose")
    @MainActor
    func testSingleDoseConcentration() throws {
        let (context, container) = createTestContext()
        _ = container
        let engine = PharmacokineticsEngine()

        // Given: Create test dose
        let dose = Dose(
            amount: 1.0,
            timestamp: Date().addingTimeInterval(-24 * 60 * 60), // 1 day ago
            medication: .semaglutide
        )

        // When: Calculate concentration
        let concentration = engine.calculateConcentration(
            doses: [dose],
            medication: .semaglutide,
            at: Date()
        )

        // Then: Verify calculation
        #expect(concentration > 0.0)
        #expect(concentration < 1.0) // Should have decayed
    }

    @Test("Handle empty dose array gracefully")
    @MainActor
    func testEmptyDoseArray() {
        let engine = PharmacokineticsEngine()

        let concentration = engine.calculateConcentration(
            doses: [],
            medication: .semaglutide,
            at: Date()
        )

        #expect(concentration == 0.0)
    }
}
```

## Common Mistakes and Best Practices

**See `./unit-test-anti-patterns.md` for complete reference including:**
- Common mistakes table with problems and solutions
- Do's and Don'ts for Swift Testing
- SwiftData-specific anti-patterns

## Simulator Conflicts

When running tests, ensure no conflicting simulators are active:

```bash
xcrun simctl list
```

Use 1 of the 3 available iPhone 17 Pro simulators to avoid conflicts:
```bash
./scripts/test.sh unit 1
./scripts/test.sh unit 2
./scripts/test.sh unit 3
```
