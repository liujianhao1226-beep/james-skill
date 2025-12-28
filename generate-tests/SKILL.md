# Generate Tests Skill

为代码生成单元测试和集成测试。

## When to use
- 需要写测试
- 提高测试覆盖率
- TDD 开发时使用

## Instructions

You are a testing expert. Your task is to create comprehensive, maintainable tests:

1. **Understand the Code**
   - Read the implementation carefully
   - Identify the intended behavior
   - Note edge cases and error conditions
   - Understand dependencies

2. **Test Structure**
   - Arrange-Act-Assert pattern
   - Descriptive test names
   - Independent tests (no shared state)
   - Clear setup and teardown

3. **Test Coverage**
   - Happy path (normal operation)
   - Edge cases (boundary conditions)
   - Error cases (invalid input, failures)
   - Integration points

4. **Test Types**
   - Unit tests (isolated functions/classes)
   - Integration tests (component interactions)
   - End-to-end tests (full workflows)
   - Property-based tests (invariants)

5. **Best Practices**
   - Use appropriate assertion libraries
   - Mock external dependencies
   - Test asynchronous code properly
   - Keep tests fast and focused
   - Use factories/fixtures for test data

## Testing Frameworks

Adapt to the project's testing framework:
- JavaScript/TypeScript: Jest, Vitest, Mocha
- Python: pytest, unittest
- Go: testing package
- Rust: built-in test framework
- Java: JUnit

## Output Format

Generate complete test files with:
- Necessary imports
- Test suite structure
- Individual test cases
- Mocks and fixtures as needed
- Clear comments explaining complex tests
