---
name: tdd-workflow
description: Use when implementing new features or fixing bugs in code. Enforces test-first development with the RED-GREEN-REFACTOR cycle to ensure all code is verified before implementation.
---

# Test-Driven Development (TDD)

## Core Principle
**"If you didn't watch the test fail, you don't know if it tests the right thing."**

Write tests before implementation code. Watch tests fail with the right error message, then write minimal code to pass them.

## Iron Law
**NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**

Any implementation written before its corresponding test must be deleted and restarted from scratch.

## The RED-GREEN-REFACTOR Cycle

### RED Phase: Write a Failing Test
1. Write ONE focused test demonstrating desired behavior
2. Use clear, descriptive test names
3. Write real assertions, not just "it works"
4. RUN the test and verify it fails for the RIGHT reason
5. If test passes immediately, delete code and restart

**Never skip verifying the failure.** A passing test proves nothing.

### GREEN Phase: Make It Pass
1. Write the SIMPLEST code that makes the test pass
2. Don't over-engineer or add features not tested
3. Don't worry about code quality yet
4. Run test - it must pass
5. Run ALL tests - none should break

### REFACTOR Phase: Clean Up
1. Improve code structure while staying GREEN
2. Eliminate duplication
3. Improve naming and clarity
4. Extract helper functions
5. Run tests after each change
6. NEVER add new behavior in this phase

## When to Use TDD

✅ **Always use for:**
- New feature implementation
- Bug fixes (write test that reproduces bug first)
- API endpoint creation
- Business logic functions
- Data transformations
- Edge case handling

⚠️ **Consider skipping for:**
- Prototyping/spike solutions (delete after)
- Pure configuration files
- Simple data structures with no logic

## Common Rationalizations to Reject

| Excuse | Reality |
|--------|---------|
| "Too simple to need a test" | Simple code breaks; testing is fast |
| "I'll add tests after" | Post-implementation tests prove nothing |
| "Already manually tested it" | Manual tests aren't reproducible |
| "This took 3 hours, wasteful to delete" | Unverified code creates technical debt |
| "I'll keep as reference" | Leads to testing-after, defeats purpose |
| "Just a quick fix" | Quick fixes cause bugs |

## Red Flags Requiring IMMEDIATE Restart

🚩 Test passes on first run
🚩 Writing code before test exists
🚩 Adding tests after implementation
🚩 "I know it works" without test proof
🚩 Any rationalization to skip the cycle

**Consult your human before deviating from TDD.**

## Backend Example (Python/FastAPI)

```python
# RED: Write failing test first
def test_create_user_returns_201():
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "name": "Test User"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

# Run test - VERIFY IT FAILS (endpoint doesn't exist yet)
# Output: 404 Not Found - GOOD!

# GREEN: Minimal implementation
@router.post("/users/", status_code=201)
async def create_user(user: UserCreate):
    return {"email": user.email, "name": user.name}

# Run test - VERIFY IT PASSES

# REFACTOR: Add database, proper response model
@router.post("/users/", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# Run tests - ALL STILL PASS
```

## Frontend Example (Angular/TypeScript)

```typescript
// RED: Write failing test
it('should emit userSelected when card is clicked', () => {
  const user: User = { id: 1, name: 'Test', email: 'test@test.com' };
  component.user = user;

  let emitted: User | undefined;
  component.userSelected.subscribe(u => emitted = u);

  component.onSelect();

  expect(emitted).toEqual(user);
});

// Run test - VERIFY IT FAILS (onSelect doesn't exist)
// Output: TypeError: component.onSelect is not a function - GOOD!

// GREEN: Minimal code
@Output() userSelected = new EventEmitter<User>();

onSelect(): void {
  this.userSelected.emit(this.user);
}

// Run test - VERIFY IT PASSES

// REFACTOR: Add validation, improve structure
onSelect(): void {
  if (!this.user) {
    throw new Error('User is required');
  }
  this.userSelected.emit(this.user);
}

// Run tests - ALL STILL PASS
```

## Testing Anti-Patterns to Avoid

```python
# Bad: Test that always passes
def test_user_creation():
    result = create_user("test", "test@test.com")
    assert result  # Too vague!

# Good: Specific assertions
def test_user_creation_returns_user_with_id():
    result = create_user("test", "test@test.com")
    assert result.id is not None
    assert result.name == "test"
    assert result.email == "test@test.com"
```

```python
# Bad: Testing implementation details
def test_user_service_calls_database():
    mock_db = Mock()
    service = UserService(mock_db)
    service.create_user(...)
    mock_db.add.assert_called_once()  # Fragile!

# Good: Testing behavior
def test_user_service_returns_created_user():
    service = UserService(test_db)
    user = service.create_user("Test", "test@test.com")
    assert user.name == "Test"
    assert user.id is not None
```

## Key Principles

1. **Test first, always**: No exceptions for "quick fixes"
2. **Watch it fail**: Verify the test fails for the right reason
3. **Minimal GREEN**: Write simplest code to pass
4. **Refactor fearlessly**: Tests provide safety net
5. **One behavior per test**: Focused, clear tests
6. **Real assertions**: Test actual behavior, not mocks
7. **Delete untested code**: No compromises on unverified code

## The TDD Mindset

TDD is not about testing - it's about design. Writing tests first:
- Forces you to think about API before implementation
- Reveals design problems early
- Creates executable specifications
- Provides instant regression detection
- Enables fearless refactoring

**TDD done right means every line of code is verified before it exists.**
