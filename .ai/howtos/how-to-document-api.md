# How to: Document an API

**Purpose**: Step-by-step guide for documenting REST APIs, endpoints, and web service interfaces

**Scope**: All API endpoints, web services, and programmatic interfaces

**Overview**: This practical guide walks through comprehensive API documentation including endpoint documentation,
    request/response specifications, authentication, error handling, rate limiting, and versioning. Covers both
    human-readable documentation and machine-readable OpenAPI/Swagger specifications. Provides templates for
    documenting different HTTP methods, examples for common patterns, and best practices for maintaining accurate,
    helpful API documentation. Suitable for backend developers documenting APIs and teams creating public API
    documentation.

**Dependencies**: API documentation standards (.ai/docs/api-documentation.md), HTTP protocol knowledge, API development experience

**Exports**: Practical API documentation process, endpoint templates, OpenAPI examples, and verification checklist

**Related**: api-documentation.md, file-headers.md, OpenAPI specification

**Implementation**: Step-by-step process with templates and examples for REST API documentation

---

## Prerequisites

Before starting, ensure you have:
- [ ] Understanding of your API's purpose and audience
- [ ] List of all endpoints to document
- [ ] Knowledge of authentication mechanism
- [ ] Example requests and responses (tested)
- [ ] Understanding of error responses
- [ ] Rate limiting and versioning strategy

**Estimated Time**: 45-60 minutes (for complete API)

**Difficulty**: Intermediate

## Step 1: Plan Your Documentation Structure

Decide on documentation organization:

### Internal API Documentation
**Audience**: Internal developers, frontend team
**Format**: Markdown in repository
**Sections**: Endpoints, authentication, errors
**Tools**: Simple markdown files

### Public API Documentation
**Audience**: External developers, API consumers
**Format**: Interactive documentation
**Sections**: Full reference, SDKs, tutorials
**Tools**: OpenAPI/Swagger, dedicated docs site

### Choose Documentation Level

**Level 1 - Minimal** (Internal APIs):
- Endpoint list with HTTP methods
- Basic request/response format
- Authentication requirements

**Level 2 - Standard** (Most APIs):
- Detailed endpoint documentation
- Request parameters with types
- Response examples
- Error responses
- Authentication details

**Level 3 - Comprehensive** (Public APIs):
- All Level 2 content
- Interactive documentation
- Multiple language examples
- SDKs and client libraries
- Versioning and migration guides
- Change logs

## Step 2: Document API Overview

Start with high-level API information:

### Format
```markdown
# API Documentation

## Overview

The TaskFlow API provides programmatic access to task management, team collaboration, and workflow automation features.

**Base URL**: `https://api.taskflow.com/api/v1`

**Current Version**: v1

**Authentication**: Bearer token (JWT)

**Response Format**: JSON

**Rate Limiting**: 1000 requests/hour

## Quick Start

1. Obtain API key from dashboard
2. Make authenticated request:

```bash
curl https://api.taskflow.com/api/v1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN"
```
```

### Guidelines
- Explain what the API does
- Provide base URL
- State current version
- Mention authentication method
- Include simple example

## Step 3: Document Authentication

Explain how to authenticate with your API:

### Bearer Token Authentication

```markdown
## Authentication

All API requests require authentication using Bearer tokens in the `Authorization` header.

### Obtaining a Token

**Request**:
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Using the Token

Include the token in all requests:

```bash
curl https://api.taskflow.com/api/v1/tasks \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Token Refresh

Tokens expire after 1 hour. Refresh using:

```bash
POST /api/v1/auth/refresh
Authorization: Bearer YOUR_REFRESH_TOKEN
```
```

### API Key Authentication

```markdown
## Authentication

Authenticate using API keys in the `X-API-Key` header.

### Obtaining an API Key

1. Log in to dashboard
2. Navigate to Settings > API Keys
3. Click "Generate New Key"
4. Copy and securely store your key

### Using the API Key

```bash
curl https://api.taskflow.com/api/v1/tasks \
  -H "X-API-Key: your-api-key-here"
```

**Security Best Practices**:
- Never commit API keys to version control
- Rotate keys regularly
- Use environment variables
- Restrict key permissions when possible
```

## Step 4: Document Endpoints

Document each endpoint thoroughly:

### Endpoint Template

```markdown
### POST /api/v1/tasks

Create a new task with specified details.

**Authentication**: Required

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

**Field Descriptions**:
- `title`: Task title, must be unique within project
- `description`: Detailed task description, supports markdown
- `priority`: Task priority level affecting sort order
- `due_date`: Task deadline in ISO 8601 format
- `assignee_id`: User ID of assigned team member
- `tags`: Array of tag strings for categorization

**Example Request**:
```bash
curl -X POST https://api.taskflow.com/api/v1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete API documentation",
    "description": "Write comprehensive API docs",
    "priority": "high",
    "due_date": "2025-10-15T17:00:00Z",
    "tags": ["documentation", "api"]
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
  "tags": ["documentation", "api"],
  "created_at": "2025-10-02T10:30:00Z",
  "updated_at": "2025-10-02T10:30:00Z",
  "created_by": {
    "id": 45,
    "name": "John Doe"
  }
}
```

**Response Headers**:
```
Content-Type: application/json
Location: /api/v1/tasks/123
X-Rate-Limit-Remaining: 998
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
    },
    {
      "field": "due_date",
      "message": "Invalid date format. Use ISO 8601 format."
    }
  ]
}
```

401 Unauthorized - Missing or invalid token:
```json
{
  "error": "unauthorized",
  "message": "Authentication required. Provide valid Bearer token."
}
```

409 Conflict - Duplicate task:
```json
{
  "error": "conflict",
  "message": "Task with this title already exists in project"
}
```

429 Too Many Requests - Rate limit exceeded:
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Retry after 45 seconds.",
  "retry_after": 45
}
```
```

### Step-by-Step for Each Endpoint

1. **HTTP Method and Path**: `POST /api/v1/tasks`
2. **Brief Description**: What the endpoint does
3. **Authentication**: Required or optional
4. **Parameters**: Path, query, or body parameters
5. **Field Descriptions**: Explain each parameter
6. **Example Request**: Working curl command
7. **Success Response**: Expected response with status code
8. **Response Headers**: Important headers
9. **Error Responses**: All possible errors with examples

## Step 5: Document Common Patterns

### GET - List Resources

```markdown
### GET /api/v1/tasks

Retrieve a paginated list of tasks with optional filtering and sorting.

**Authentication**: Required

**Query Parameters**:
- `status` (string, optional): Filter by status ('pending' | 'in_progress' | 'completed')
- `priority` (string, optional): Filter by priority ('low' | 'medium' | 'high')
- `assignee_id` (integer, optional): Filter by assignee
- `tags` (string, optional): Comma-separated list of tags
- `page` (integer, optional, default: 1, min: 1): Page number
- `per_page` (integer, optional, default: 20, min: 1, max: 100): Items per page
- `sort` (string, optional, default: '-created_at'): Sort field (prefix with '-' for descending)

**Example Request**:
```bash
curl "https://api.taskflow.com/api/v1/tasks?status=pending&priority=high&page=1&per_page=20&sort=-priority" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Success Response** (200 OK):
```json
{
  "data": [
    {
      "id": 123,
      "title": "Complete API documentation",
      "status": "pending",
      "priority": "high"
    },
    {
      "id": 124,
      "title": "Review pull request",
      "status": "pending",
      "priority": "high"
    }
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

### GET - Single Resource

```markdown
### GET /api/v1/tasks/{id}

Retrieve details of a specific task.

**Authentication**: Required

**Path Parameters**:
- `id` (integer, required): Task ID

**Example Request**:
```bash
curl https://api.taskflow.com/api/v1/tasks/123 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Success Response** (200 OK):
```json
{
  "id": 123,
  "title": "Complete API documentation",
  "description": "Write comprehensive API docs",
  "status": "in_progress",
  "priority": "high",
  "due_date": "2025-10-15T17:00:00Z",
  "assignee": {
    "id": 45,
    "name": "John Doe",
    "email": "john@example.com"
  },
  "tags": ["documentation", "api"],
  "created_at": "2025-10-02T10:30:00Z",
  "updated_at": "2025-10-02T15:45:00Z"
}
```

**Error Responses**:

404 Not Found:
```json
{
  "error": "not_found",
  "message": "Task with ID 123 not found"
}
```
```

### PATCH - Update Resource

```markdown
### PATCH /api/v1/tasks/{id}

Partially update a task. Only provided fields will be updated.

**Authentication**: Required

**Path Parameters**:
- `id` (integer, required): Task ID

**Request Body** (all fields optional):
```json
{
  "title": "string (optional)",
  "status": "string (optional: 'pending' | 'in_progress' | 'completed')",
  "priority": "string (optional: 'low' | 'medium' | 'high')",
  "assignee_id": "integer (optional, null to unassign)"
}
```

**Example Request**:
```bash
curl -X PATCH https://api.taskflow.com/api/v1/tasks/123 \
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
  "priority": "high",
  "updated_at": "2025-10-02T16:00:00Z"
}
```
```

### DELETE - Remove Resource

```markdown
### DELETE /api/v1/tasks/{id}

Permanently delete a task.

**Authentication**: Required

**Path Parameters**:
- `id` (integer, required): Task ID

**Example Request**:
```bash
curl -X DELETE https://api.taskflow.com/api/v1/tasks/123 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Success Response** (204 No Content):

No response body.

**Error Responses**:

404 Not Found:
```json
{
  "error": "not_found",
  "message": "Task with ID 123 not found"
}
```

403 Forbidden:
```json
{
  "error": "forbidden",
  "message": "You don't have permission to delete this task"
}
```
```

## Step 6: Document Rate Limiting

```markdown
## Rate Limiting

API requests are rate limited to ensure fair usage.

**Limits**:
- Free tier: 100 requests/hour
- Pro tier: 1,000 requests/hour
- Enterprise tier: 10,000 requests/hour

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

## Step 7: Document Error Responses

```markdown
## Error Handling

All errors follow a consistent format:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {} // Optional additional context
}
```

### HTTP Status Codes

| Status | Description | When Used |
|--------|-------------|-----------|
| 200 | OK | Successful GET, PATCH, PUT |
| 201 | Created | Successful POST creating resource |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid request data, validation errors |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Valid auth but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource conflict (duplicate, state) |
| 422 | Unprocessable Entity | Business logic validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Temporary service outage |

### Common Error Codes

**`validation_error`** (400):
```json
{
  "error": "validation_error",
  "message": "Invalid request data",
  "details": [
    {"field": "email", "message": "Invalid email format"},
    {"field": "password", "message": "Password must be at least 8 characters"}
  ]
}
```

**`unauthorized`** (401):
```json
{
  "error": "unauthorized",
  "message": "Authentication required"
}
```

**`forbidden`** (403):
```json
{
  "error": "forbidden",
  "message": "Insufficient permissions to perform this action"
}
```

**`not_found`** (404):
```json
{
  "error": "not_found",
  "message": "Resource not found"
}
```

**`rate_limit_exceeded`** (429):
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded",
  "retry_after": 60
}
```
```

## Step 8: Create OpenAPI Specification (Optional)

For public APIs, create OpenAPI/Swagger specification:

```yaml
openapi: 3.0.3
info:
  title: TaskFlow API
  description: Task management API with real-time updates
  version: 1.0.0
  contact:
    email: api@taskflow.com
  license:
    name: MIT

servers:
  - url: https://api.taskflow.com/api/v1
    description: Production server

paths:
  /tasks:
    post:
      summary: Create task
      description: Create a new task with specified details
      tags:
        - Tasks
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TaskCreate'
            example:
              title: "Complete API documentation"
              priority: "high"
              due_date: "2025-10-15T17:00:00Z"
      responses:
        '201':
          description: Task created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
        '400':
          description: Validation error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

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
        priority:
          type: string
          enum: [low, medium, high]
          example: "high"
        due_date:
          type: string
          format: date-time
          example: "2025-10-15T17:00:00Z"

    TaskCreate:
      type: object
      required:
        - title
      properties:
        title:
          type: string
          maxLength: 200
        description:
          type: string
          maxLength: 2000
        priority:
          type: string
          enum: [low, medium, high]
          default: medium

    Error:
      type: object
      required:
        - error
        - message
      properties:
        error:
          type: string
          example: "validation_error"
        message:
          type: string
          example: "Invalid request data"
        details:
          type: array
          items:
            type: object

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - bearerAuth: []
```

## Step 9: Verify Your Documentation

Use this checklist:

### Completeness
- [ ] All endpoints documented
- [ ] HTTP methods specified
- [ ] Authentication requirements clear
- [ ] Request parameters documented with types
- [ ] Response formats documented
- [ ] Success responses with examples
- [ ] All error responses documented
- [ ] Rate limiting explained
- [ ] Versioning strategy documented

### Quality
- [ ] All examples tested and working
- [ ] Field types and constraints specified
- [ ] Error messages helpful
- [ ] Consistent terminology
- [ ] No broken links
- [ ] No typos or errors

### User Experience
- [ ] Quick start guide provided
- [ ] Common use cases covered
- [ ] Interactive docs available (if applicable)
- [ ] SDKs mentioned (if available)
- [ ] Migration guides for versions

## Common Mistakes and Solutions

### Mistake 1: No Request Examples

**Problem**: Only showing request format, no working examples

**Solution**: Provide complete curl commands users can copy-paste

### Mistake 2: Missing Error Responses

**Problem**: Only documenting success responses

**Solution**: Document all possible error responses with examples

### Mistake 3: Unclear Parameter Types

**Problem**: Not specifying types, constraints, or required/optional

**Solution**: Document type, constraints, required status, defaults

### Mistake 4: Outdated Examples

**Problem**: Examples don't match current API

**Solution**: Test all examples, keep updated with API changes

### Mistake 5: No Authentication Guide

**Problem**: Users don't know how to authenticate

**Solution**: Clear authentication section with examples

## Quick Reference

### Essential Documentation
1. API overview and base URL
2. Authentication method and examples
3. All endpoints with examples
4. Error response format
5. Rate limiting information

### Endpoint Documentation Template
1. HTTP method and path
2. Brief description
3. Authentication requirement
4. Request parameters/body
5. Example request
6. Success response
7. Error responses

### Testing Documentation
1. Test all curl examples
2. Verify response formats
3. Check error responses
4. Test rate limiting behavior
5. Validate OpenAPI spec (if using)

## Next Steps

After documenting your API:
1. **Test all examples** - Ensure they work
2. **Generate OpenAPI spec** - For interactive docs
3. **Create SDK examples** - Multiple languages
4. **Set up interactive docs** - Swagger UI or similar
5. **Gather feedback** - Ask users what's unclear
6. **Keep updated** - Update with API changes
7. **Version docs** - Maintain docs for each version

## Additional Resources

- **API documentation reference**: `.ai/docs/api-documentation.md`
- **File headers**: `.ai/howto/how-to-write-file-headers.md`
- **OpenAPI Specification**: https://swagger.io/specification/
- **Swagger UI**: https://swagger.io/tools/swagger-ui/
