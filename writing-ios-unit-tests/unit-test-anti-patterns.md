# Unit Test Anti-Patterns and Best Practices

## Common Mistakes

| Mistake                              | Problem                         | Solution                                        |
| ------------------------------------ | ------------------------------- | ----------------------------------------------- |
| Not capturing ModelContainer         | Context becomes invalid         | Always capture both context AND container       |
| Assigning arrays to relationships    | Crashes in SwiftData macros     | Use individual property setters                 |
| Force unwrapping in tests            | Test crashes on failure         | Use guard with explicit failures                |
| Exact time comparisons               | Flaky tests                     | Use tolerance-based assertions                  |
| Missing @MainActor                   | Thread safety violations        | Always use for UI/SwiftData tests               |
| Testing with CloudKit enabled        | Relationship validation errors  | Set `cloudKitDatabase: .none`                   |
| Mocking internal services            | Tests don't reflect reality     | Test with real implementations                  |
| Not checking coverage thresholds     | PR coverage gate failures       | Run `./scripts/check-coverage.sh` first         |

## Best Practices Summary

### ✅ Do This

1. **Use Swift Testing for new tests** - `@Test` and `#expect` syntax
2. **Use @MainActor for UI components** - Ensures proper thread safety
3. **Safe unwrapping with guard** - Avoid force unwrapping
4. **Capture ModelContainer in tests** - Prevents context invalidation
5. **Tolerance-based time assertions** - Account for timing variability
6. **Disable CloudKit in test config** - Prevents relationship crashes
7. **Test factories for consistency** - Reusable test data creation
8. **Coverage-driven development** - Meet tier requirements

### ❌ Don't Do This

1. **Don't use XCTest for new tests** - Legacy pattern
2. **Don't assign arrays to SwiftData relationships** - Causes crashes
3. **Don't force unwrap in tests** - Use safe unwrapping patterns
4. **Don't use exact time comparisons** - Always use tolerance
5. **Don't skip @MainActor** - Required for UI component testing
6. **Don't enable CloudKit in tests** - Causes validation errors
7. **Don't mock internal services** - Reduces test realism
