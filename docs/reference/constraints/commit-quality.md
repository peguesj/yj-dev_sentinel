# Commit Quality Constraints

Commit quality constraints ensure that version control commits follow best practices for clarity, traceability, and maintainability.

## Available Constraints

### CQ001: Commit Message Format

- **ID**: `commit-message-format`
- **Severity**: Warning
- **Description**: Ensures that commit messages follow the defined format.
- **Rule**: Commit messages should follow the Conventional Commits specification.
- **Auto-fixable**: No

### CQ002: Commit Message Length

- **ID**: `commit-message-length`
- **Severity**: Warning
- **Description**: Ensures that commit message subjects are not too long.
- **Rule**: Commit message subjects should be less than 72 characters long.
- **Auto-fixable**: No

### CQ003: Commit Size

- **ID**: `commit-size`
- **Severity**: Warning
- **Description**: Ensures that commits are not too large.
- **Rule**: Commits should change fewer than 500 lines of code.
- **Auto-fixable**: No

### CQ004: Related Issue Reference

- **ID**: `commit-issue-reference`
- **Severity**: Info
- **Description**: Encourages referencing related issues in commit messages.
- **Rule**: Commit messages should reference related issues when applicable.
- **Auto-fixable**: No

### CQ005: Single Responsibility

- **ID**: `commit-single-responsibility`
- **Severity**: Warning
- **Description**: Ensures that commits address a single responsibility or fix.
- **Rule**: Commits should not mix unrelated changes.
- **Auto-fixable**: No

### CQ006: No Broken Commits

- **ID**: `commit-no-broken-code`
- **Severity**: Error
- **Description**: Ensures that commits do not introduce broken code.
- **Rule**: Code should compile and pass tests after each commit.
- **Auto-fixable**: No

## Example Violations

Here are some examples of commit message constraint violations:

```bash
# CQ001: Invalid commit message format
Fixed bug  # Missing type, scope, and proper format

# CQ002: Commit message too long
feat(authentication): implement new user authentication system with OAuth2 integration and social media login options

# CQ004: Missing issue reference
fix(login): correct validation logic in login form
```

## Correct Commit Messages

Here are examples of correctly formatted commit messages:

```bash
# Valid conventional commit format
feat(auth): add OAuth2 authentication

# With issue reference
fix(login): correct validation logic in login form (#123)

# With breaking change
feat(api)!: change response format for user endpoints

# With a body
fix(navigation): correct routing for nested paths

The previous implementation incorrectly handled nested routes
when parameters contained special characters.

Closes #456
```

## Conventional Commits Specification

The FORCE system enforces the [Conventional Commits](https://www.conventionalcommits.org/) specification, which defines a structured format for commit messages:

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Common types include:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Formatting changes
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

## Enforcement

Commit quality constraints are typically enforced during:

- **Pre-commit hooks**: Check commit messages before allowing commits
- **Pull request validation**: Ensure commit quality before allowing merges
- **Continuous Integration**: Verify commit quality as part of the CI pipeline

## Configuration

Commit quality constraints can be configured in the project's `.force/config.json` file:

```json
{
  "constraints": {
    "commit-quality": {
      "message-format": {
        "enabled": true,
        "severity": "warning",
        "pattern": "^(feat|fix|docs|style|refactor|test|chore)(\\([a-z0-9-]+\\))?(!)?: .+$"
      },
      "message-max-length": 72,
      "commit-max-size": 500,
      "require-issue-reference": {
        "enabled": true,
        "severity": "info"
      }
    }
  }
}
```

## Related Constraints

- [Branch Naming Constraints](branch-naming.md)

## Related Patterns

- [Version Control Pattern](../patterns/version-control.md)
