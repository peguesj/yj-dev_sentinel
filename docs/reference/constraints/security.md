# Security Constraints

Security constraints ensure that code adheres to security best practices and avoids common security vulnerabilities.

## Available Constraints

### SEC001: SQL Injection Prevention

- **ID**: `security-sql-injection`
- **Severity**: Error
- **Description**: Ensures that code is protected against SQL injection attacks.
- **Rule**: SQL queries should use parameterized queries or ORM methods instead of string concatenation.
- **Auto-fixable**: Sometimes

### SEC002: Cross-Site Scripting (XSS) Prevention

- **ID**: `security-xss-prevention`
- **Severity**: Error
- **Description**: Ensures that web applications are protected against cross-site scripting attacks.
- **Rule**: User input should be properly escaped before being output to HTML.
- **Auto-fixable**: Sometimes

### SEC003: Authentication Requirements

- **ID**: `security-authentication`
- **Severity**: Error
- **Description**: Ensures that sensitive routes and operations require proper authentication.
- **Rule**: Sensitive routes and operations must have authentication checks.
- **Auto-fixable**: No

### SEC004: CSRF Protection

- **ID**: `security-csrf-protection`
- **Severity**: Error
- **Description**: Ensures that web applications are protected against Cross-Site Request Forgery attacks.
- **Rule**: Forms and APIs that change state must include CSRF tokens.
- **Auto-fixable**: Sometimes

### SEC005: Secure Password Storage

- **ID**: `security-password-storage`
- **Severity**: Error
- **Description**: Ensures that passwords are stored securely.
- **Rule**: Passwords must be hashed using strong, modern algorithms (like bcrypt, Argon2) and never stored in plaintext.
- **Auto-fixable**: Sometimes

### SEC006: Hardcoded Secrets

- **ID**: `security-hardcoded-secrets`
- **Severity**: Error
- **Description**: Identifies and prevents the use of hardcoded secrets in code.
- **Rule**: Code should not contain hardcoded API keys, passwords, or other secrets.
- **Auto-fixable**: No

### SEC007: Secure Headers

- **ID**: `security-secure-headers`
- **Severity**: Warning
- **Description**: Ensures that web applications set appropriate security headers.
- **Rule**: Applications should set headers like Content-Security-Policy, X-XSS-Protection, etc.
- **Auto-fixable**: Yes

### SEC008: Input Validation

- **ID**: `security-input-validation`
- **Severity**: Error
- **Description**: Ensures that all user input is properly validated.
- **Rule**: User input should be validated before processing.
- **Auto-fixable**: Sometimes

## Example Violations

Here are some examples of security constraint violations:

```python
# SEC001: SQL Injection Vulnerability
def get_user(user_id):
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # Vulnerable to SQL injection
    return cursor.fetchone()

# SEC006: Hardcoded Secret
API_KEY = "1234abcd5678efgh"  # Hardcoded secret

def authenticate_api_request(request):
    if request.headers.get('api-key') == API_KEY:
        return True
    return False
```

## Secure Alternatives

```python
# SEC001: Safe alternative using parameterized queries
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))  # Safe from SQL injection
    return cursor.fetchone()

# SEC006: Safe alternative using environment variables
import os
API_KEY = os.environ.get("API_KEY")  # Retrieves secret from environment variable

def authenticate_api_request(request):
    if request.headers.get('api-key') == API_KEY:
        return True
    return False
```

## Enforcement

Security constraints are typically enforced during:

- **Pre-commit checks**: Automatically check before committing code
- **Pull request validation**: Ensure code meets security standards before merging
- **Continuous Integration**: Regular security checks as part of the CI pipeline
- **Scheduled security scans**: Regular deep scans of the entire codebase

## Configuration

Security constraints can be configured in the project's `.force/config.json` file:

```json
{
  "constraints": {
    "security": {
      "hardcoded-secrets": {
        "enabled": true,
        "severity": "error",
        "exclude_patterns": ["test/mock_data.py"]
      },
      "sql-injection": {
        "enabled": true,
        "severity": "error"
      }
    }
  }
}
```

## Related Constraints

- [Code Quality Constraints](code-quality.md)

## Related Patterns

- [Code Analysis Pattern](../patterns/code-analysis.md)
- [Refactoring Pattern](../patterns/refactoring.md)
