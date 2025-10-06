# How to: Write File Headers

**Purpose**: Step-by-step guide for writing compliant file headers for all file types

**Scope**: All code, configuration, and documentation files in any project

**Overview**: This practical guide walks through the process of writing effective file headers for markdown,
    Python, TypeScript, YAML, and other file types. Covers the atemporal documentation principle, mandatory
    fields, file-type specific formatting, template usage, and common mistakes. Provides concrete examples
    and a verification checklist to ensure headers meet standards. Suitable for beginners learning documentation
    standards and experienced developers looking for a quick reference.

**Dependencies**: File header standards (.ai/docs/file-headers.md), templates (.ai/templates/file-header-*.template)

**Exports**: Practical file header creation process, examples, and verification checklist

**Related**: file-headers.md, DOCUMENTATION_STANDARDS.md, file header templates

**Implementation**: Step-by-step process with examples and checklists for each file type

---

## Prerequisites

Before starting, ensure you have:
- [ ] Access to file header templates (`.ai/templates/file-header-*.template`)
- [ ] Understanding of the file type you're documenting
- [ ] Basic knowledge of the file's purpose in the project

**Estimated Time**: 15-20 minutes per file

**Difficulty**: Beginner

## Step 1: Choose the Right Template

Select the appropriate template based on file type:

| File Type | Template | Comment Style |
|-----------|----------|---------------|
| Markdown (.md) | `file-header-markdown.template` | `**Field**:` format |
| Python (.py) | `file-header-python.template` | `"""` docstring |
| TypeScript/JavaScript (.ts, .tsx, .js, .jsx) | `file-header-typescript.template` | `/** */` JSDoc |
| YAML (.yml, .yaml) | `file-header-yaml.template` | `# Field:` comment |
| JSON (.json) | Special format | `_header` object or adjacent doc |
| Terraform (.tf, .hcl) | Adapt YAML template | `# Field:` comment |
| Docker (Dockerfile, compose) | Adapt YAML template | `# Field:` comment |
| HTML (.html) | Special format | `<!-- -->` comment |
| CSS (.css, .scss) | Special format | `/* */` comment |
| Shell (.sh, .ps1, .bat) | Adapt YAML template | `# Field:` comment |

**Action**: Open the appropriate template:
```bash
cat .ai/templates/file-header-python.template
```

## Step 2: Understand Mandatory Fields

Every file header must include these three fields:

### Purpose
**What**: Brief description of file's functionality (1-2 lines)
**Why**: Tells readers immediately what this file does
**Example**: "Validates user input according to business rules and security requirements"

### Scope
**What**: What areas/components this file covers
**Why**: Defines boundaries and applicability
**Example**: "User registration and authentication flows across all API endpoints"

### Overview
**What**: Comprehensive summary (3-5+ lines)
**Why**: Provides detailed understanding without reading code
**Example**:
```
This module handles all user authentication including password validation,
token generation, session management, and OAuth2 integration. Implements
JWT-based authentication with refresh tokens, rate limiting, and brute-force
protection. Integrates with the user service for account verification and
supports multiple authentication providers (local, Google, GitHub).
```

## Step 3: Apply the Atemporal Principle

**Key Rule**: Never reference time, dates, or changes.

### What to Avoid

❌ **Temporal Language**:
- "Currently supports..."
- "Recently added..."
- "Will implement..."
- "Changed from X to Y"
- "Created: 2025-09-12"
- "Now includes..."
- "Temporarily disabled"

### What to Use Instead

✅ **Present-Tense Descriptions**:
- "Supports..."
- "Provides..."
- "Implements..."
- "Handles..."
- "Manages..."
- "Validates..."

### Examples

**Bad**:
```
Purpose: Recently updated to handle user authentication. Currently supports JWT tokens.
```

**Good**:
```
Purpose: Handles user authentication using JWT tokens
```

**Bad**:
```
Overview: This was changed from using session cookies to JWT tokens. Will add OAuth2 support later.
```

**Good**:
```
Overview: Implements JWT token-based authentication with session management.
    Provides token generation, validation, and refresh functionality. Integrates
    with the user service for account verification and authorization.
```

## Step 4: Write the Header (File-Type Specific)

### For Markdown Files

**Template**:
```markdown
# Document Title

**Purpose**: Brief description

**Scope**: Coverage area

**Overview**: Comprehensive explanation (3-5+ lines)

**Dependencies**: Related documents or prerequisites

**Exports**: Key information this document provides

**Related**: Links to related documentation

**Implementation**: Notable patterns or approaches

---

## Overview

Content starts here...
```

**Example**:
```markdown
# User Authentication Guide

**Purpose**: Complete guide for implementing user authentication in the application

**Scope**: All authentication flows including registration, login, password reset, and OAuth2 integration

**Overview**: This guide covers the complete user authentication system including password-based
    authentication, JWT token management, refresh token handling, and OAuth2 integration with
    external providers. Explains the authentication flow, security considerations, token expiration
    handling, and integration with the user service. Includes code examples, best practices, and
    troubleshooting common authentication issues.

**Dependencies**: User service API documentation, JWT library documentation, OAuth2 provider setup guides

**Exports**: Authentication implementation patterns, security best practices, integration examples

**Related**: API documentation for auth endpoints, user service documentation, security standards

**Implementation**: JWT-based authentication with RSA signing, OAuth2 authorization code flow

---

## Overview

User authentication in this application uses...
```

### For Python Files

**Template**:
```python
"""
Purpose: Brief description

Scope: What this module handles

Overview: Comprehensive summary (3-5+ lines)

Dependencies: Key dependencies

Exports: Main classes, functions, constants

Interfaces: Key APIs or methods

Implementation: Notable algorithms or patterns
"""
```

**Example**:
```python
"""
Purpose: Validates and processes user registration requests

Scope: User registration flow including validation, password hashing, and account creation

Overview: Handles all aspects of user registration including email validation, password strength
    checking, username uniqueness verification, and account creation. Implements secure password
    hashing using bcrypt, email verification token generation, and rate limiting for registration
    attempts. Integrates with the email service for verification emails and the user database for
    account storage. Includes comprehensive validation with detailed error messages.

Dependencies: bcrypt for password hashing, email_validator for email validation, SQLAlchemy for database

Exports: UserRegistrationService class, RegistrationRequest dataclass, RegistrationError exception

Interfaces: register_user(email, password, username) -> User, verify_email(token) -> bool

Implementation: Bcrypt password hashing with cost factor 12, JWT tokens for email verification
"""

import bcrypt
from email_validator import validate_email
```

### For TypeScript/JavaScript Files

**Template**:
```typescript
/**
 * Purpose: Brief description
 *
 * Scope: What this file handles
 *
 * Overview: Comprehensive summary (3-5+ lines)
 *
 * Dependencies: Key libraries and components
 *
 * Exports: Main components, functions, types
 *
 * Props/Interfaces: Key interfaces
 *
 * State/Behavior: State management patterns
 */
```

**Example**:
```typescript
/**
 * Purpose: User authentication form component with validation and error handling
 *
 * Scope: Login and registration forms across the application
 *
 * Overview: Provides reusable authentication form component with real-time validation,
 *     password strength indicator, and accessible error messaging. Handles form submission,
 *     loading states, and error display for both login and registration flows. Integrates
 *     with the authentication service for API calls and implements proper form accessibility
 *     with ARIA labels and keyboard navigation. Includes password visibility toggle and
 *     remember me functionality.
 *
 * Dependencies: React, react-hook-form for validation, auth service for API calls, zod for schema validation
 *
 * Exports: AuthForm component as default, AuthFormProps interface, AuthFormSchema type
 *
 * Props/Interfaces: AuthFormProps { mode: 'login' | 'register', onSuccess: (user) => void, onError: (error) => void }
 *
 * State/Behavior: Form state managed by react-hook-form, loading state for async operations, error state for API errors
 */

import React from 'react';
import { useForm } from 'react-hook-form';
```

### For YAML Configuration Files

**Template**:
```yaml
# Purpose: Brief description
# Scope: What this configuration applies to
# Overview: Comprehensive explanation (3-5+ lines)
# Dependencies: Related configurations or services
# Exports: Key configuration sections
# Environment: Target environments
# Related: Related configuration files
# Implementation: Configuration patterns
```

**Example**:
```yaml
# Purpose: Docker Compose configuration for development environment
# Scope: All application services for local development including backend, frontend, database, and Redis
# Overview: Orchestrates multi-container Docker application for local development with hot-reloading
#     support, volume mounts for source code, and service networking. Configures backend API service,
#     frontend development server, PostgreSQL database, Redis cache, and nginx reverse proxy. Includes
#     health checks, restart policies, and proper service dependencies. Optimized for development with
#     exposed ports and debug configurations.
# Dependencies: Dockerfiles in .docker/dockerfiles/, environment variables in .env
# Exports: Docker Compose services for development, networks, volumes, and service orchestration
# Environment: Local development only (not for production use)
# Related: Dockerfile.backend, Dockerfile.frontend, production docker-compose.prod.yml
# Implementation: Docker Compose v3.8, healthcheck-based service dependencies, named volumes for persistence

version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: .docker/dockerfiles/Dockerfile.backend
```

## Step 5: Fill in Additional Fields (Code Files)

For code files (Python, TypeScript, etc.), include these additional fields:

### Dependencies
List key dependencies that aren't obvious from imports:
- External libraries
- Internal modules
- System requirements

**Example**:
```
Dependencies: Redis for caching, PostgreSQL for persistence, boto3 for AWS S3 integration
```

### Exports
Document what this file provides to other parts of the system:
- Main classes
- Public functions
- Constants
- Types/interfaces

**Example**:
```
Exports: UserService class, User dataclass, UserNotFoundError exception, get_current_user() helper
```

### Interfaces
Describe key APIs this file exposes:
- Public methods
- API endpoints
- Event handlers

**Example**:
```
Interfaces: authenticate(username, password) -> Token, validate_token(token) -> User, refresh_token(refresh_token) -> Token
```

### Implementation (Optional but Recommended)
Note important technical decisions:
- Algorithms used
- Design patterns
- Architectural choices

**Example**:
```
Implementation: Uses bcrypt for password hashing, JWT with RS256 for tokens, Redis for token blacklisting
```

## Step 6: Format According to File Type

### Markdown
- Double line breaks after each field
- Horizontal rule (`---`) separates header from content
- Use `**Field**:` format

### Python
- Triple quotes (`"""`) for docstring
- Blank lines between field sections
- First thing in file (after shebang if present)

### TypeScript/JavaScript
- JSDoc format (`/** */`)
- Asterisk (`*`) at start of each line
- Blank lines between field sections

### YAML/Configuration
- Hash (`#`) comments
- Single space after `#` and after field colon
- Multi-line continuation with indentation

## Step 7: Verify Your Header

Use this checklist to verify header completeness:

### Mandatory Fields
- [ ] **Purpose** field present (1-2 lines)
- [ ] **Scope** field present and clear
- [ ] **Overview** field present (3-5+ lines minimum)

### Atemporal Language
- [ ] No temporal words ("currently", "now", "recently", "will")
- [ ] No dates or timestamps
- [ ] No state change language ("changed from", "replaced")
- [ ] No future references ("planned", "to be added")

### Content Quality
- [ ] Purpose is specific and clear
- [ ] Scope defines boundaries
- [ ] Overview provides comprehensive understanding
- [ ] Dependencies listed (if applicable)
- [ ] Exports documented (if applicable)

### Formatting
- [ ] Correct comment style for file type
- [ ] Proper line breaks and spacing
- [ ] Consistent indentation
- [ ] Header at top of file (correct position)

## Common Mistakes and Solutions

### Mistake 1: Too Brief Overview

**Problem**:
```python
"""
Purpose: User service
Scope: Users
Overview: Handles users
"""
```

**Solution**:
```python
"""
Purpose: Manages user account operations and authentication

Scope: User registration, authentication, profile management, and account settings

Overview: Provides comprehensive user management including account creation, authentication,
    profile updates, and account deletion. Implements secure password hashing, email verification,
    and session management. Integrates with the database for user persistence and the email
    service for notifications. Handles user permissions and role-based access control.

Dependencies: SQLAlchemy for database, bcrypt for password hashing, email service for notifications

Exports: UserService class, User model, UserNotFoundError exception
"""
```

### Mistake 2: Using Temporal Language

**Problem**:
```python
"""
Purpose: Recently updated authentication module that currently handles login

Overview: This was changed from using sessions to JWT tokens. Will add OAuth2 support soon.
"""
```

**Solution**:
```python
"""
Purpose: Handles user authentication using JWT tokens

Overview: Implements JWT-based authentication with token generation, validation, and refresh
    functionality. Provides login and logout operations with secure password verification.
    Supports token expiration and refresh token rotation for enhanced security.
"""
```

### Mistake 3: Wrong Comment Format

**Problem** (Python file with markdown-style header):
```python
**Purpose**: User service
**Scope**: User management
```

**Solution**:
```python
"""
Purpose: User service managing account operations

Scope: User management including registration, authentication, and profiles
"""
```

### Mistake 4: Missing Mandatory Fields

**Problem**:
```typescript
/**
 * User authentication component
 */
```

**Solution**:
```typescript
/**
 * Purpose: User authentication form component with validation
 *
 * Scope: Login and registration forms across the application
 *
 * Overview: Provides reusable authentication form with real-time validation, error handling,
 *     and accessible design. Handles both login and registration modes with password strength
 *     checking and email validation. Integrates with authentication service for API calls.
 *
 * Dependencies: React, react-hook-form, auth service
 *
 * Exports: AuthForm component, AuthFormProps interface
 */
```

### Mistake 5: Header in Wrong Location

**Problem** (Python - header after imports):
```python
import os
import sys

"""
Purpose: Configuration loader
"""
```

**Solution**:
```python
"""
Purpose: Configuration loader managing application settings

Scope: Application-wide configuration from environment variables and files

Overview: Loads and validates application configuration from multiple sources including
    environment variables, .env files, and default settings. Provides type-safe access
    to configuration values with validation and default fallbacks.
"""

import os
import sys
```

## Examples by File Type

### Complete Markdown Header

```markdown
# FastAPI Development Guide

**Purpose**: Comprehensive guide for developing FastAPI applications following project standards

**Scope**: FastAPI application development including routing, dependencies, testing, and deployment

**Overview**: This guide covers complete FastAPI development workflow including project setup,
    creating API endpoints with proper validation, implementing authentication, database integration,
    testing strategies, and deployment best practices. Explains the project structure, dependency
    injection patterns, async/await usage, and integration with SQLAlchemy. Includes examples for
    common patterns like CRUD operations, file uploads, background tasks, and WebSocket connections.

**Dependencies**: FastAPI framework documentation, Python standards guide, database integration guide

**Exports**: FastAPI development patterns, code examples, testing strategies, deployment procedures

**Related**: Python standards, API documentation guide, database migration guide

**Implementation**: FastAPI with Pydantic validation, SQLAlchemy async, pytest for testing

---

## Overview

FastAPI is a modern, high-performance web framework...
```

### Complete Python Header

```python
"""
Purpose: Centralized configuration management for application settings

Scope: Application-wide configuration loading, validation, and access across all modules

Overview: Provides type-safe configuration management loading settings from environment variables,
    .env files, and default values. Implements validation for all configuration values, handles
    environment-specific settings (development, staging, production), and provides secure handling
    of sensitive values like API keys and database credentials. Integrates with Pydantic Settings
    for automatic validation and type conversion. Supports configuration reloading and change detection.

Dependencies: pydantic-settings for validation, python-dotenv for .env files, typing for type hints

Exports: Settings class (singleton), get_settings() function, ConfigurationError exception

Interfaces: get_settings() -> Settings, reload_settings() -> None

Implementation: Pydantic BaseSettings with env file support, singleton pattern for settings instance
"""

from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional
```

### Complete TypeScript Header

```typescript
/**
 * Purpose: API client service for backend communication with authentication and error handling
 *
 * Scope: All HTTP requests to backend API across the entire application
 *
 * Overview: Provides centralized API client with automatic authentication token handling, request/response
 *     interceptors, error normalization, and retry logic. Implements typed interfaces for all API endpoints
 *     including user management, task operations, and file uploads. Handles authentication token refresh,
 *     request cancellation, and loading state management. Includes comprehensive error handling with typed
 *     error responses and automatic error logging. Supports file uploads with progress tracking.
 *
 * Dependencies: axios for HTTP requests, jwt-decode for token parsing, custom types from @/types/api
 *
 * Exports: ApiClient class, apiClient instance (singleton), ApiError class, ApiResponse type
 *
 * Props/Interfaces: ApiClientConfig, ApiError, ApiResponse<T>, RequestOptions
 *
 * State/Behavior: Maintains authentication state, implements retry logic with exponential backoff,
 *     tracks request cancellation tokens, manages loading states for concurrent requests
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import jwtDecode from 'jwt-decode';
```

### Complete YAML Header

```yaml
# Purpose: Production deployment configuration for AWS ECS with auto-scaling and monitoring
# Scope: Production environment services including application, database, Redis, and monitoring stack
# Overview: Docker Compose configuration for production deployment on AWS ECS with high availability,
#     auto-scaling, health monitoring, and centralized logging. Configures multi-container application
#     with load balancing, database replication, Redis clustering, and Prometheus monitoring. Implements
#     proper resource limits, restart policies, health checks, and dependency management for production
#     resilience. Includes security configurations with secrets management and network isolation.
# Dependencies: AWS ECS environment, Docker images from ECR, environment variables from AWS Secrets Manager
# Exports: Production-ready Docker Compose services with HA configuration, monitoring, and logging
# Environment: Production only - requires AWS infrastructure and proper security configurations
# Related: docker-compose.dev.yml for development, AWS ECS task definitions, CloudFormation templates
# Implementation: Docker Compose v3.8, ECS-compatible configurations, health-check based orchestration

version: '3.8'

services:
  app:
    image: ${ECR_REGISTRY}/app:${IMAGE_TAG}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
```

## Quick Reference

### Essential Steps
1. Choose right template
2. Fill in Purpose (1-2 lines)
3. Fill in Scope (1-2 lines)
4. Fill in Overview (3-5+ lines)
5. Add dependencies (code files)
6. Add exports (code files)
7. Use atemporal language
8. Verify with checklist

### Atemporal Language Quick Check
- ❌ currently, now, recently, will, was, changed, new, old
- ✅ provides, handles, implements, supports, manages, validates

### Mandatory Fields
1. Purpose
2. Scope
3. Overview

### Recommended Fields (Code)
4. Dependencies
5. Exports
6. Interfaces

## Next Steps

After writing file headers:
1. **Verify completeness** using the checklist
2. **Review examples** for your file type
3. **Test if code files** still parse/compile correctly
4. **Commit changes** with descriptive commit message
5. **Apply to new files** going forward
6. **Share with team** to maintain consistency

## Additional Resources

- **Complete reference**: `.ai/docs/file-headers.md`
- **Templates**: `.ai/templates/file-header-*.template`
- **Standards**: `.ai/docs/FILE_HEADER_STANDARDS.md`
- **README guide**: `.ai/howto/how-to-create-readme.md`
