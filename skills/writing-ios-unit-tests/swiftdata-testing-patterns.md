# SwiftData Testing Patterns (CRITICAL)

## Creating Test Context

```swift
// ✅ CORRECT: Return both context AND container
func createTestContext() -> (context: ModelContext, container: ModelContainer) {
    let schema = Schema([User.self, Dose.self, Food.self])
    let config = ModelConfiguration(
        schema: schema,
        isStoredInMemoryOnly: true,
        cloudKitDatabase: .none  // Critical: Disable CloudKit for tests
    )
    let container = try! ModelContainer(for: schema, configurations: [config])
    return (container.mainContext, container)
}

// In test - MUST capture container
@Test func testExample() {
    let (context, container) = createTestContext()
    _ = container  // Keep alive for duration of test

    // Now context.insert() will work
}

// ❌ WRONG: Container deallocates, context becomes invalid
func createTestContext() -> ModelContext {
    let container = try! ModelContainer(...)
    return container.mainContext  // Crash on insert!
}
```

## ⚠️ CRITICAL: SwiftData Relationship Anti-Pattern

**NEVER assign arrays to SwiftData relationships in tests:**

```swift
// ❌ THIS WILL CRASH THE APP - NEVER DO THIS
medicationProfile.doses = existingDoses
user.medicationProfiles = [profile1, profile2]

// ✅ CORRECT - Use individual property setters instead
for dose in existingDoses {
    dose.medication = medicationProfile  // Sets individual relationship
}
// OR avoid relationships entirely in test-only code
_ = existingDoses  // Keep for test setup but don't assign to relationship
```

**Why this crashes:**
- SwiftData uses computed properties with complex setter logic
- Direct array assignment bypasses SwiftData's relationship management
- Causes crashes in `@__swiftmacro_` generated code
- Test environment makes this worse due to lack of proper ModelContext
