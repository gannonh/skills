# Coverage Policy (5-Tier System)

## Coverage Requirements

| Tier | Category                  | Threshold | Examples                                    |
| ---- | ------------------------- | --------- | ------------------------------------------- |
| 1    | Pure Business Logic       | 90%       | Models, calculators, pure functions         |
| 2    | Infrastructure            | 60%       | Services, data management                   |
| 3    | Framework Integration     | 42%       | Auth, Biometrics, Notifications wrappers    |
| 4    | View Models               | 85%       | ObservableObject classes                    |
| 5    | Utilities                 | 75%       | Helper functions, extensions                |
| -    | SwiftUI Views             | Exempt    | View bodies cannot be unit tested           |

## Coverage Workflow

```bash
# Step 1: Generate coverage data
./scripts/check-coverage.sh

# Or run tests first, then check coverage
./scripts/test.sh unit 1 --coverage
./scripts/check-coverage.sh --use-existing

# Step 2: Analyze coverage
./scripts/coverage-detail.sh                    # Full report
./scripts/coverage-detail.sh DateNightService   # Filter by pattern
./scripts/coverage-json.sh --summary            # File overview sorted by %
./scripts/coverage-json.sh --functions          # Show uncovered functions only
```

## Common Coverage Issues

| Issue                      | Symptom                               | Solution                                                  |
| -------------------------- | ------------------------------------- | --------------------------------------------------------- |
| Tests pass but 0% coverage | `executionCount: 0` for all functions | Verify tests call production code, not mocks              |
| Private method not covered | Can't test directly                   | Test via public methods that invoke them                  |
| Async method low coverage  | Race conditions                       | Add `try await Task.sleep(for: .milliseconds(100))` waits |
| Extension file 0% coverage | Swift coverage attribution            | Check if tests call the correct module/class              |
| Result bundle not found    | Missing `.coverage/`                  | Run tests with `--coverage` or `-enableCodeCoverage YES`  |
