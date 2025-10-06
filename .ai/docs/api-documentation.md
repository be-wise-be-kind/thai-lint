# API Documentation Standards

**Purpose**: Best practices and standards for documenting REST APIs, GraphQL APIs, and web service interfaces

**Scope**: All API endpoints, web services, and programmatic interfaces exposed by projects

**Overview**: This document establishes comprehensive standards for API documentation including REST endpoint
    documentation, request/response specifications, authentication and authorization documentation, error handling,
    status codes, rate limiting, and versioning. Covers both human-readable documentation and machine-readable
    specifications (OpenAPI/Swagger). Provides templates for endpoint documentation, examples for different HTTP
    methods, and best practices for maintaining accurate, helpful API documentation that serves both internal
    developers and external API consumers.

**Dependencies**: HTTP protocol knowledge, OpenAPI/Swagger specification (optional), API development experience

**Exports**: API documentation templates, endpoint documentation standards, OpenAPI guidelines, and examples

**Related**: .ai/howto/how-to-document-api.md, file-headers.md, OpenAPI specification

**Implementation**: Template-based API documentation with OpenAPI specification generation

---

## Overview

API documentation is critical for both internal developers and external consumers. Well-documented APIs:
- Enable developers to integrate quickly and correctly
- Reduce support requests and integration issues
- Serve as contracts between frontend and backend teams
- Facilitate testing and validation
- Support automated client generation

## API Documentation Levels

### Level 1: Endpoint Summary

Minimal documentation for internal APIs:
- HTTP method and path
- Brief purpose
- Authentication requirements
- Basic request/response format

### Level 2: Comprehensive Documentation

Standard for most APIs:
- Detailed endpoint description
- Request parameters (path, query, body)
- Response format with examples
- Error responses
- Authentication and authorization
- Rate limiting

### Level 3: Public API Documentation

Required for public-facing APIs:
- All Level 2 content
- SDK examples in multiple languages
- Interactive documentation (Swagger UI)
- Versioning information
- Deprecation notices
- Change logs
- Getting started guides

## Essential Components

### 1. Endpoint Documentation

**Format**:
```markdown
### POST /api/v1/tasks

Create a new task with specified details.

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "title": "string (required, max 200 chars)",
  "description": "string (optional, max 2000 chars)",
  "priority": "string (optional: 'low' | 'medium' | 'high', default: 'medium')",
  "due_date": "string (optional, ISO 8601 format)",
  "assignee_id": "integer (optional)",
  "tags": "array of strings (optional)"
}
```

**Example Request**:
```bash
curl -X POST https://api.example.com/api/v1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete API documentation",
    "description": "Write comprehensive API docs",
    "priority": "high",
    "due_date": "2025-10-15T17:00:00Z"
  }'
```

**Success Response** (201 Created):
```json
{
  "id": 123,
  "title": "Complete API documentation",
  "description": "Write comprehensive API docs",
  "priority": "high",
  "status": "pending",
  "due_date": "2025-10-15T17:00:00Z",
  "assignee_id": null,
  "tags": [],
  "created_at": "2025-10-02T10:30:00Z",
  "updated_at": "2025-10-02T10:30:00Z"
}
```

**Error Responses**:

400 Bad Request - Invalid input:
```json
{
  "error": "validation_error",
  "message": "Invalid request data",
  "details": [
    {
      "field": "title",
      "message": "Title is required and cannot be empty"
    }
  ]
}
```

401 Unauthorized - Missing or invalid token:
```json
{
  "error": "unauthorized",
  "message": "Authentication required"
}
```

429 Too Many Requests - Rate limit exceeded:
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60
}
```
```

**Guidelines**:
- Document HTTP method and full path
- Explain what the endpoint does (purpose)
- List authentication requirements
- Document all request parameters
- Provide realistic examples
- Show all possible responses
- Include error scenarios

### 2. Request Documentation

**Path Parameters**:
```markdown
**Path Parameters**:
- `id` (integer, required): Unique task identifier

**Example**: `/api/v1/tasks/123`
```

**Query Parameters**:
```markdown
**Query Parameters**:
- `status` (string, optional): Filter by status ('pending' | 'in_progress' | 'completed')
- `priority` (string, optional): Filter by priority ('low' | 'medium' | 'high')
- `assignee_id` (integer, optional): Filter by assignee
- `page` (integer, optional, default: 1): Page number for pagination
- `per_page` (integer, optional, default: 20, max: 100): Items per page

**Example**: `/api/v1/tasks?status=pending&priority=high&page=2&per_page=50`
```

**Request Headers**:
```markdown
**Headers**:
- `Authorization` (required): Bearer token for authentication
- `Content-Type` (required): Must be `application/json`
- `Accept` (optional): Response format preference (default: `application/json`)
- `X-Request-ID` (optional): Client-generated request ID for tracing
```

**Request Body**:
```markdown
**Request Body** (JSON):

```json
{
  "field_name": "type (required/optional, constraints)",
  "another_field": "type (required/optional, constraints)"
}
```

**Field Descriptions**:
- `field_name`: Purpose and validation rules
- `another_field`: Purpose and validation rules
```

### 3. Response Documentation

**Success Response**:
```markdown
**Success Response** (200 OK):

```json
{
  "data": {
    "id": 123,
    "field": "value"
  },
  "meta": {
    "timestamp": "2025-10-02T10:30:00Z"
  }
}
```

**Response Headers**:
- `Content-Type`: application/json
- `X-Request-ID`: Request identifier for tracing
- `X-Rate-Limit-Remaining`: Remaining requests in current window
```

**Pagination**:
```markdown
**Paginated Response** (200 OK):

```json
{
  "data": [
    {"id": 1, "title": "Task 1"},
    {"id": 2, "title": "Task 2"}
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "total_pages": 3
  },
  "links": {
    "first": "/api/v1/tasks?page=1",
    "prev": null,
    "next": "/api/v1/tasks?page=2",
    "last": "/api/v1/tasks?page=3"
  }
}
```
```

### 4. Error Documentation

**Error Response Format**:
```markdown
**Error Responses**:

All errors follow this format:
```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {} // Additional context (optional)
}
```

**Common Error Codes**:

| Status | Code | Description |
|--------|------|-------------|
| 400 | `validation_error` | Invalid request data |
| 400 | `invalid_format` | Malformed request body |
| 401 | `unauthorized` | Missing or invalid authentication |
| 403 | `forbidden` | Insufficient permissions |
| 404 | `not_found` | Resource not found |
| 409 | `conflict` | Resource conflict (e.g., duplicate) |
| 422 | `unprocessable_entity` | Business logic validation failed |
| 429 | `rate_limit_exceeded` | Too many requests |
| 500 | `internal_error` | Server error |
| 503 | `service_unavailable` | Temporary service outage |
```

### 5. Authentication Documentation

**Bearer Token Authentication**:
```markdown
## Authentication

All API requests require authentication using Bearer tokens.

**Obtaining a Token**:

```bash
curl -X POST https://api.example.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your-password"
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Using the Token**:

Include the token in the `Authorization` header:

```bash
curl -X GET https://api.example.com/api/v1/tasks \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Token Expiration**:

Tokens expire after 1 hour. Use the refresh token to obtain a new access token:

```bash
curl -X POST https://api.example.com/api/v1/auth/refresh \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN"
```
```

**API Key Authentication**:
```markdown
## Authentication

Authenticate using API keys in request headers.

**Obtaining an API Key**:

1. Log in to the dashboard
2. Navigate to Settings > API Keys
3. Click "Generate New Key"
4. Copy and securely store your key

**Using the API Key**:

```bash
curl -X GET https://api.example.com/api/v1/tasks \
  -H "X-API-Key: your-api-key-here"
```

**Security**:
- Never commit API keys to version control
- Rotate keys regularly
- Use environment variables to store keys
- Restrict key permissions when possible
```

### 6. Rate Limiting

```markdown
## Rate Limiting

API requests are rate limited to ensure fair usage and system stability.

**Limits**:
- **Free tier**: 100 requests per hour
- **Pro tier**: 1,000 requests per hour
- **Enterprise tier**: 10,000 requests per hour

**Rate Limit Headers**:

Every response includes rate limit information:

```http
X-Rate-Limit-Limit: 1000
X-Rate-Limit-Remaining: 847
X-Rate-Limit-Reset: 1633024800
```

- `X-Rate-Limit-Limit`: Total requests allowed per window
- `X-Rate-Limit-Remaining`: Requests remaining in current window
- `X-Rate-Limit-Reset`: Unix timestamp when limit resets

**Handling Rate Limits**:

When rate limit is exceeded (429 status):

```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Try again in 45 seconds.",
  "retry_after": 45
}
```

**Best Practices**:
- Monitor rate limit headers
- Implement exponential backoff
- Cache responses when possible
- Use webhooks instead of polling
```

### 7. Versioning

```markdown
## API Versioning

The API uses URL-based versioning. The current version is `v1`.

**Base URL**: `https://api.example.com/api/v1`

**Version Format**: `/api/{version}/{resource}`

**Example**: `/api/v1/tasks`

**Supported Versions**:
- `v1` - Current (stable)
- `v2` - Beta (preview)

**Deprecation Policy**:

- Deprecated versions are supported for 12 months after deprecation notice
- Breaking changes require a new version
- Non-breaking changes may be added to existing versions
- Deprecation notices are included in response headers:

```http
X-API-Deprecated: true
X-API-Sunset: 2026-10-01T00:00:00Z
Link: <https://api.example.com/api/v2/tasks>; rel="successor-version"
```

**Migration**:

See [Migration Guide](docs/api-migration-v1-to-v2.md) for upgrading to v2.
```

## HTTP Methods Documentation

### GET - Retrieve Resources

```markdown
### GET /api/v1/tasks/{id}

Retrieve a single task by ID.

**Path Parameters**:
- `id` (integer, required): Task ID

**Example Request**:
```bash
curl -X GET https://api.example.com/api/v1/tasks/123 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Success Response** (200 OK):
```json
{
  "id": 123,
  "title": "Complete API documentation",
  "status": "in_progress"
}
```

**Error Responses**:
- `404 Not Found`: Task not found
- `401 Unauthorized`: Authentication required
```

### POST - Create Resources

```markdown
### POST /api/v1/tasks

Create a new task.

**Request Body**:
```json
{
  "title": "string (required)",
  "description": "string (optional)"
}
```

**Example Request**:
```bash
curl -X POST https://api.example.com/api/v1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "New task", "description": "Task details"}'
```

**Success Response** (201 Created):
```json
{
  "id": 124,
  "title": "New task",
  "description": "Task details",
  "status": "pending"
}
```

**Response Headers**:
- `Location`: /api/v1/tasks/124

**Error Responses**:
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Authentication required
- `409 Conflict`: Duplicate task
```

### PUT - Replace Resources

```markdown
### PUT /api/v1/tasks/{id}

Replace an existing task (all fields required).

**Path Parameters**:
- `id` (integer, required): Task ID

**Request Body** (all fields required):
```json
{
  "title": "string (required)",
  "description": "string (required)",
  "status": "string (required)",
  "priority": "string (required)"
}
```

**Success Response** (200 OK):
```json
{
  "id": 123,
  "title": "Updated task",
  "description": "Updated description",
  "status": "in_progress",
  "priority": "high"
}
```
```

### PATCH - Update Resources

```markdown
### PATCH /api/v1/tasks/{id}

Partially update a task (only specified fields).

**Path Parameters**:
- `id` (integer, required): Task ID

**Request Body** (all fields optional):
```json
{
  "status": "string (optional)",
  "priority": "string (optional)"
}
```

**Example Request**:
```bash
curl -X PATCH https://api.example.com/api/v1/tasks/123 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

**Success Response** (200 OK):
```json
{
  "id": 123,
  "title": "Complete API documentation",
  "status": "completed",
  "updated_at": "2025-10-02T15:30:00Z"
}
```
```

### DELETE - Remove Resources

```markdown
### DELETE /api/v1/tasks/{id}

Delete a task permanently.

**Path Parameters**:
- `id` (integer, required): Task ID

**Example Request**:
```bash
curl -X DELETE https://api.example.com/api/v1/tasks/123 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Success Response** (204 No Content):

No response body.

**Error Responses**:
- `404 Not Found`: Task not found
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
```

## OpenAPI/Swagger Documentation

### OpenAPI Specification

```yaml
openapi: 3.0.3
info:
  title: TaskFlow API
  description: Task management API with real-time updates
  version: 1.0.0
  contact:
    email: api@example.com
  license:
    name: MIT

servers:
  - url: https://api.example.com/api/v1
    description: Production server
  - url: https://staging-api.example.com/api/v1
    description: Staging server

paths:
  /tasks:
    get:
      summary: List tasks
      description: Retrieve a paginated list of tasks with optional filtering
      tags:
        - Tasks
      parameters:
        - name: status
          in: query
          description: Filter by task status
          schema:
            type: string
            enum: [pending, in_progress, completed]
        - name: page
          in: query
          description: Page number
          schema:
            type: integer
            default: 1
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/Task'
                  pagination:
                    $ref: '#/components/schemas/Pagination'

components:
  schemas:
    Task:
      type: object
      required:
        - id
        - title
        - status
      properties:
        id:
          type: integer
          example: 123
        title:
          type: string
          maxLength: 200
          example: "Complete API documentation"
        status:
          type: string
          enum: [pending, in_progress, completed]
          example: "in_progress"

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - bearerAuth: []
```

### Interactive Documentation

```markdown
## Interactive API Documentation

Explore and test the API using interactive documentation:

- **Swagger UI**: https://api.example.com/docs
  - Interactive API explorer
  - Try endpoints directly in browser
  - See request/response examples

- **ReDoc**: https://api.example.com/redoc
  - Clean, searchable documentation
  - Better for reading and reference
  - Optimized for printing

**Using Swagger UI**:
1. Click "Authorize" button
2. Enter your Bearer token
3. Click endpoint to expand
4. Click "Try it out"
5. Fill in parameters
6. Click "Execute"
```

## Best Practices

### Documentation Quality

1. **Be complete**: Document all endpoints, parameters, responses
2. **Be accurate**: Test all examples before publishing
3. **Be clear**: Use simple language and explain technical terms
4. **Be consistent**: Follow same format for all endpoints
5. **Be current**: Update docs with API changes

### Examples

1. **Use realistic data**: Not "foo" and "bar"
2. **Show actual responses**: Copy from real API responses
3. **Include edge cases**: Empty results, errors, limits
4. **Provide multiple languages**: Curl, Python, JavaScript, etc.
5. **Test examples**: Ensure they work as shown

### Organization

1. **Group by resource**: All task endpoints together
2. **Logical order**: List, Create, Read, Update, Delete
3. **Clear navigation**: Table of contents, search
4. **Cross-reference**: Link related endpoints
5. **Version clearly**: Indicate API version prominently

### Maintenance

1. **Version documentation**: Keep docs for each API version
2. **Track changes**: Document what changed in each version
3. **Deprecation notices**: Warn before removing endpoints
4. **Migration guides**: Help users upgrade versions
5. **Changelog**: Maintain detailed API changelog

## Common Patterns

### Pagination

```markdown
**Pagination Parameters**:
- `page` (integer, optional, default: 1): Page number
- `per_page` (integer, optional, default: 20, max: 100): Items per page

**Response**:
```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5
  },
  "links": {
    "first": "/api/v1/tasks?page=1",
    "prev": null,
    "next": "/api/v1/tasks?page=2",
    "last": "/api/v1/tasks?page=5"
  }
}
```
```

### Filtering and Sorting

```markdown
**Filtering**:
- `filter[status]` - Filter by status
- `filter[priority]` - Filter by priority

**Sorting**:
- `sort` - Sort field (prefix with `-` for descending)
- Example: `sort=-created_at` (newest first)

**Example**: `/api/v1/tasks?filter[status]=pending&sort=-priority`
```

### Bulk Operations

```markdown
### POST /api/v1/tasks/bulk

Create multiple tasks in a single request.

**Request Body**:
```json
{
  "tasks": [
    {"title": "Task 1"},
    {"title": "Task 2"}
  ]
}
```

**Response** (207 Multi-Status):
```json
{
  "results": [
    {
      "status": 201,
      "data": {"id": 1, "title": "Task 1"}
    },
    {
      "status": 400,
      "error": {"message": "Invalid title"}
    }
  ]
}
```
```

## Validation Checklist

- [ ] All endpoints documented with HTTP method and path
- [ ] Purpose/description for each endpoint
- [ ] Authentication requirements specified
- [ ] All request parameters documented
- [ ] Request body format and examples provided
- [ ] Success response format and examples included
- [ ] All error responses documented
- [ ] Rate limiting information included
- [ ] Versioning strategy explained
- [ ] Examples tested and working
- [ ] OpenAPI spec generated (if applicable)
- [ ] Interactive docs available (if applicable)

## Next Steps

- **Review examples**: Study the patterns in this document
- **Use templates**: Follow the formats provided
- **Generate OpenAPI**: Consider OpenAPI/Swagger for automation
- **Test documentation**: Verify all examples work
- **Maintain regularly**: Update docs with API changes
- **Gather feedback**: Ask users what's unclear
