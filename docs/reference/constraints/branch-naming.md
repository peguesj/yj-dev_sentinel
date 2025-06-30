# Branch Naming Constraints

Branch naming constraints ensure that version control branches follow consistent naming conventions, making repository management more efficient and organized.

## Available Constraints

### BN001: Branch Naming Convention

- **ID**: `branch-naming-convention`
- **Severity**: Warning
- **Description**: Ensures that branch names follow the defined naming convention.
- **Rule**: Branch names should follow the pattern `<type>/<description>`, where type is one of: feature, bugfix, hotfix, release, or docs.
- **Auto-fixable**: No

### BN002: Branch Name Length

- **ID**: `branch-name-length`
- **Severity**: Warning
- **Description**: Ensures that branch names are not too long.
- **Rule**: Branch names should be less than 50 characters long.
- **Auto-fixable**: No

### BN003: Branch Name Characters

- **ID**: `branch-name-characters`
- **Severity**: Warning
- **Description**: Ensures that branch names use allowed characters only.
- **Rule**: Branch names should use only lowercase letters, numbers, hyphens, and slashes.
- **Auto-fixable**: Yes

### BN004: Branch Prefix Requirement

- **ID**: `branch-prefix-requirement`
- **Severity**: Warning
- **Description**: Ensures that branch names start with a valid prefix.
- **Rule**: Branch names should start with one of the allowed prefixes.
- **Auto-fixable**: No

## Example Violations

Here are some examples of branch naming constraint violations:

```bash
# BN001: Incorrect branch naming format
my-new-feature        # Missing type prefix

# BN002: Branch name too long
feature/implement-extremely-long-and-detailed-description-of-the-feature-that-is-being-built-right-now

# BN003: Invalid characters in branch name
feature/NEW_FEATURE!  # Contains uppercase letters and special characters

# BN004: Invalid branch prefix
improvement/login     # 'improvement' is not a valid prefix
```

## Correct Branch Names

Here are examples of correctly formatted branch names:

```bash
feature/user-authentication
bugfix/login-form-validation
hotfix/security-vulnerability
release/v1.2.0
docs/api-documentation
```

## Enforcement

Branch naming constraints are typically enforced during:

- **Pre-commit hooks**: Check branch name before allowing commits
- **Pull request validation**: Ensure branch naming conventions before allowing merges
- **Continuous Integration**: Check branch names as part of the CI pipeline

## Configuration

Branch naming constraints can be configured in the project's `.force/config.json` file:

```json
{
  "constraints": {
    "branch-naming": {
      "convention": {
        "enabled": true,
        "severity": "warning",
        "pattern": "^(feature|bugfix|hotfix|release|docs)/[a-z0-9-]+$"
      },
      "max-length": 50,
      "allowed-prefixes": ["feature/", "bugfix/", "hotfix/", "release/", "docs/"]
    }
  }
}
```

## Related Constraints

- [Commit Quality Constraints](commit-quality.md)

## Related Patterns

- [Version Control Pattern](../patterns/version-control.md)
