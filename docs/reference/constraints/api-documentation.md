# API Documentation Constraints

API documentation constraints ensure that APIs are properly documented, allowing for easy integration and usage by other developers.

## Available Constraints

### APIDOC001: Endpoint Documentation

- **ID**: `api-endpoint-documentation`
- **Severity**: Error
- **Description**: Ensures that API endpoints are properly documented.
- **Rule**: Each API endpoint should have documentation describing its purpose, request format, and response format.
- **Auto-fixable**: No

### APIDOC002: Request Parameter Documentation

- **ID**: `api-request-parameter-documentation`
- **Severity**: Warning
- **Description**: Ensures that API request parameters are properly documented.
- **Rule**: Each request parameter should be documented with its name, type, and description.
- **Auto-fixable**: No

### APIDOC003: Response Schema Documentation

- **ID**: `api-response-schema-documentation`
- **Severity**: Warning
- **Description**: Ensures that API response schemas are properly documented.
- **Rule**: Each API endpoint should document its response schema, including status codes and data formats.
- **Auto-fixable**: No

### APIDOC004: Error Response Documentation

- **ID**: `api-error-response-documentation`
- **Severity**: Warning
- **Description**: Ensures that API error responses are properly documented.
- **Rule**: Each API endpoint should document possible error responses, including status codes and error messages.
- **Auto-fixable**: No

### APIDOC005: Authentication Documentation

- **ID**: `api-authentication-documentation`
- **Severity**: Warning
- **Description**: Ensures that API authentication requirements are properly documented.
- **Rule**: API documentation should describe authentication methods and requirements.
- **Auto-fixable**: No

### APIDOC006: API Version Documentation

- **ID**: `api-version-documentation`
- **Severity**: Warning
- **Description**: Ensures that API versioning is properly documented.
- **Rule**: API documentation should include version information and compatibility notes.
- **Auto-fixable**: No

### APIDOC007: Example Requests and Responses

- **ID**: `api-example-requests-responses`
- **Severity**: Info
- **Description**: Encourages the inclusion of example requests and responses in API documentation.
- **Rule**: API documentation should include example requests and responses for each endpoint.
- **Auto-fixable**: No

### APIDOC008: Rate Limit Documentation

- **ID**: `api-rate-limit-documentation`
- **Severity**: Info
- **Description**: Ensures that API rate limits are properly documented.
- **Rule**: API documentation should describe any rate limits and throttling policies.
- **Auto-fixable**: No

## Example Violations

Here are some examples of API documentation constraint violations:

```python
# APIDOC001: Missing endpoint documentation
@app.route('/api/users', methods=['GET'])
def get_users():
    # Implementation...
    return jsonify(users)

# APIDOC002: Missing request parameter documentation
@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    # Implementation...
    return jsonify(user)

# APIDOC003: Missing response schema documentation
@app.route('/api/users', methods=['POST'])
def create_user():
    user_data = request.json
    # Implementation...
    return jsonify(new_user), 201
```

## Properly Documented Examples

```python
@app.route('/api/users', methods=['GET'])
def get_users():
    """
    Get a list of all users.
    
    ---
    tags:
      - Users
    parameters:
      - name: page
        in: query
        type: integer
        description: Page number for pagination
        default: 1
      - name: limit
        in: query
        type: integer
        description: Number of users per page
        default: 10
    responses:
      200:
        description: A list of users
        schema:
          type: object
          properties:
            users:
              type: array
              items:
                $ref: '#/definitions/User'
            total:
              type: integer
              description: Total number of users
            page:
              type: integer
              description: Current page number
    """
    # Implementation...
    return jsonify(users)

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get details for a specific user.
    
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: The ID of the user to retrieve
    responses:
      200:
        description: User details
        schema:
          $ref: '#/definitions/User'
      404:
        description: User not found
        schema:
          $ref: '#/definitions/Error'
    """
    # Implementation...
    return jsonify(user)
```

## Enforcement

API documentation constraints are typically enforced during:

- **Pre-commit checks**: Automatically check before committing code
- **Pull request validation**: Ensure API documentation meets standards before merging
- **Continuous Integration**: Regular API documentation checks as part of the CI pipeline
- **API documentation generation**: During generation of OpenAPI/Swagger documentation

## Configuration

API documentation constraints can be configured in the project's `.force/config.json` file:

```json
{
  "constraints": {
    "api-documentation": {
      "endpoint-documentation": {
        "enabled": true,
        "severity": "error"
      },
      "example-requests-responses": {
        "enabled": true,
        "severity": "warning"
      },
      "frameworks": {
        "flask": true,
        "fastapi": true,
        "django": true
      }
    }
  }
}
```

## Related Constraints

- [Documentation Completeness Constraints](documentation-completeness.md)

## Related Patterns

- [Documentation Generation Pattern](../patterns/documentation-generation.md)
