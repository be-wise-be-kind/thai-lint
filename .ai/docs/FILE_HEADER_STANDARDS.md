# File Header Standards

**Purpose**: Define comprehensive header standards for all document types ensuring consistent documentation across the entire repository

**Scope**: All documentation, configuration, and code files throughout the project

**Overview**: Establishes unified header standards for all file types in the repository, providing consistent documentation patterns across markdown, configuration files, code files, and all other document types. Includes detailed formatting guidelines, line break rules, field requirements, and file-type specific templates. Ensures every file is self-documenting with proper readability optimization while focusing on essential operational information that Git doesn't track.

**Dependencies**: Existing file header linter, design linter framework, and CI/CD validation tools

**Exports**: Header format standards, validation rules, formatting guidelines, and implementation templates

**Related**: Links to file placement standards, development standards, and automated linting documentation

**Implementation**: Comprehensive field definitions, line break guidelines, and automated validation integration

---

## Overview

This document establishes unified header standards for all file types in the repository, providing consistent documentation patterns across markdown, configuration files, code files, and all other document types. The goal is to ensure every file is self-documenting with proper line breaks for readability and consistent formatting, while focusing on essential operational information that Git doesn't already track.

## Atemporal Documentation Principle

File headers must be written in an atemporal manner - avoiding language that references specific points in time, historical changes, or future plans. This ensures documentation remains accurate and relevant without requiring updates when circumstances change.

### Avoid These Temporal Patterns

**Explicit Timestamps:**
- ❌ "Created: 2025-09-12"
- ❌ "Updated: 2025-09-16"
- ❌ "Last modified: September 2025"

**State Change Language:**
- ❌ "This replaces the old implementation"
- ❌ "Changed from X to Y"
- ❌ "New implementation of..."
- ❌ "Formerly known as..."
- ❌ "Migrated from the legacy system"

**Temporal Qualifiers:**
- ❌ "Currently supports..."
- ❌ "Now includes..."
- ❌ "Recently added..."
- ❌ "Previously used for..."
- ❌ "Temporarily disabled"
- ❌ "For now, this handles..."

**Future References:**
- ❌ "Will be implemented"
- ❌ "Planned features include..."
- ❌ "To be added later"
- ❌ "Future improvements"

### Write Instead

**Present-tense, factual descriptions:**
- ✅ "Handles user authentication"
- ✅ "Provides data validation"
- ✅ "Implements the circuit breaker pattern"
- ✅ "Manages WebSocket connections"

**Feature descriptions without temporal context:**
- ✅ "Supports JSON and XML formats"
- ✅ "Includes error handling and retry logic"
- ✅ "Provides type-safe API interfaces"

**Capability statements:**
- ✅ "Validates input according to business rules"
- ✅ "Exports reusable UI components"
- ✅ "Integrates with the authentication service"

## Standard Header Formats

### Markdown Documentation Files (.md)

```markdown
# Document Title

**Purpose**: Brief description of what this document covers and its primary function

**Scope**: What areas/components this document applies to and target audience

**Overview**: Comprehensive explanation of the document's content, structure, and purpose.
    Detailed description of what readers will learn, how the document fits into the larger
    documentation ecosystem, key topics covered, and important concepts explained.
    This should be sufficient for readers to understand the document's value and relevance
    without reading the entire content.

**Dependencies**: Related documents, external resources, or prerequisite knowledge required

**Exports**: Key information, standards, procedures, or guidelines this document provides

**Related**: Links to related documentation, external resources, or cross-references

**Implementation**: Notable documentation patterns, structures, or organizational approaches used
---

## Overview

Document content starts here with proper spacing and structure...
```

**Line Break Rules for Markdown:**
- **Double line breaks**: After each header field for visual separation and readability
- **Horizontal rule (---)**: Separates header from main content
- **Single line breaks**: Within multi-line field descriptions for natural reading flow
- **Consistent spacing**: Maintains readability across different markdown viewers

### HTML Files (.html)

```html
<!DOCTYPE html>
<!--
Purpose: Brief description of this HTML file's purpose, target users, and primary functionality
Scope: What this file is used for (UI component, documentation page, landing page, etc.)
Overview: Comprehensive description of the HTML file's content, user interactions,
    accessibility features, responsive behavior, and integration with stylesheets
    or JavaScript. Should include information about key sections, navigation patterns,
    and content organization. This should help developers understand the page structure
    and functionality without examining all markup.
Dependencies: Key libraries, frameworks, stylesheets, or JavaScript files used
Exports: Web page, component, or interface for specific use case and target audience
Interfaces: User interactions, form submissions, API integrations, or navigation patterns
Related: Links to related pages, stylesheets, or documentation
Implementation: Notable accessibility features, responsive design patterns, or performance optimizations
-->
<html lang="en">
```

### Python Files (.py)

```python
"""
Purpose: Brief description of module/script functionality (1-2 lines)

Scope: What this module handles (API endpoints, data models, business logic, etc.)

Overview: Comprehensive summary of what this module does and its role in the system.
    Detailed explanation of the module's responsibilities, how it fits into the larger
    architecture, key workflows it supports, and important behavioral characteristics.
    This should be sufficient for a developer to understand the module without reading code.

Dependencies: Key external dependencies or internal modules required

Exports: Main classes, functions, or constants this module provides

Interfaces: Key APIs, endpoints, or methods this module exposes

Implementation: Notable algorithms, patterns, or architectural decisions
"""
```

### TypeScript/JavaScript Files (.ts, .tsx, .js, .jsx)

```typescript
/**
 * Purpose: Brief description of component/module functionality (1-2 lines)
 *
 * Scope: What this file handles (React component, utility functions, API service, etc.)
 *
 * Overview: Comprehensive summary of what this component/module does and its role in the application.
 *     Detailed explanation of the component's responsibilities, how it fits into the UI/system,
 *     key user interactions it supports, and important behavioral characteristics.
 *     This should be sufficient for a developer to understand the component without reading code.
 *
 * Dependencies: Key libraries, components, or services this file depends on
 *
 * Exports: Main components, functions, types, or constants this file provides
 *
 * Props/Interfaces: Key interfaces this component accepts or module provides
 *
 * State/Behavior: Important state management or behavioral patterns used
 */
```

### Configuration Files (.yml, .yaml, .json, .toml)

```yaml
# Purpose: Brief description of configuration file and what it configures in the system
# Scope: What this configuration applies to (development, production, specific services, global settings)
# Overview: Comprehensive explanation of the configuration's role in the system,
#     what services consume these settings, how it integrates with other configurations,
#     key behavioral characteristics it controls, and operational impact of changes.
#     Should include information about configuration validation, reload behavior,
#     and any special handling requirements. This should help developers and operators
#     understand the configuration's importance without examining all individual values.
# Dependencies: Services, tools, or other configuration files that depend on or use this configuration
# Exports: Key configuration sections, environment variables, or settings this file provides
# Environment: Target deployment environments (dev, staging, prod, all) and environment-specific behavior
# Related: Links to related configuration files, documentation, or external configuration sources
# Implementation: Configuration management patterns, validation rules, or update procedures used
```

### Infrastructure as Code (.tf, .hcl)

```hcl
# Purpose: Brief description of infrastructure component and its primary function in the architecture
# Scope: What infrastructure this manages (networking, storage, compute, security, monitoring, etc.)
# Overview: Comprehensive explanation of the infrastructure component's role in the overall architecture,
#     how it integrates with other AWS/cloud resources, scaling characteristics, security considerations,
#     cost implications, and operational requirements. Should include information about resource
#     dependencies, state management, and deployment patterns. This should help infrastructure engineers
#     and operators understand the component's importance without examining all resource configurations.
# Dependencies: Required configuration files, modules, providers, or external resources
# Exports: Key infrastructure outputs, resource IDs, or configuration values this module provides
# Configuration: Variable sources, environment-specific settings, and configuration patterns used
# Environment: Target deployment environments and environment-specific behavior or optimizations
# Related: Links to related Terraform modules, AWS documentation, or infrastructure diagrams
# Implementation: Key architectural decisions, resource organization patterns, or deployment strategies
```

### Docker and Container Files (.dockerfile, docker-compose.yml)

```yaml
# Purpose: Brief description of container orchestration, build configuration, and deployment setup
# Scope: What services/containers this manages (backend, frontend, databases, caching, monitoring, etc.)
# Overview: Comprehensive explanation of the containerization strategy, service dependencies,
#     networking topology, volume mount strategies, environment variable handling, scaling
#     characteristics, and deployment patterns. Should include information about health checks,
#     restart policies, resource limits, and security configurations. This should help DevOps
#     engineers and developers understand the complete containerization approach without
#     examining all individual service definitions and configurations.
# Dependencies: Docker engine, Docker Compose, service Dockerfiles, external images, or registries
# Exports: Docker services configuration, networks, volumes, and orchestration for target environment
# Interfaces: Service ports, networking configuration, API endpoints, and inter-service communication
# Environment: Target deployment environments and environment-specific container configurations
# Related: Links to Dockerfiles, container registries, monitoring configurations, or deployment guides
# Implementation: Container orchestration patterns, security practices, and performance optimizations
```

### Script Files (.sh, .ps1, .bat)

```bash
#!/bin/bash
# Purpose: Brief description of script functionality, primary use cases, and automation purpose
# Scope: What operations this script performs (deployment, testing, utilities, monitoring, setup, etc.)
# Overview: Comprehensive explanation of the script's operations, workflow steps, prerequisites,
#     expected inputs and outputs, error handling strategies, and integration with other scripts
#     or systems. Should include information about execution context, required permissions,
#     logging behavior, and failure scenarios. This should help operators and developers
#     understand the script's role and requirements without examining all implementation details.
# Dependencies: Required tools, runtime environments, system permissions, or external services
# Exports: Generated files, environment changes, or system state modifications this script produces
# Usage: Script invocation examples, parameter descriptions, and common usage patterns
# Environment: Target execution environments and environment-specific behavior or requirements
# Related: Links to related scripts, documentation, or system components
# Implementation: Key operational patterns, error handling approaches, and automation strategies
```

### CSS/SCSS Style Files (.css, .scss, .sass)

```css
/*
Purpose: Brief description of stylesheet's scope, target components, and styling objectives
Scope: What UI elements this stylesheet covers (global styles, component-specific, theme, layout, utilities, etc.)
Overview: Comprehensive explanation of the styling approach, responsive design strategy,
    design system integration, accessibility considerations, browser support requirements,
    and maintenance patterns. Should include information about CSS architecture, naming
    conventions, performance optimizations, and interaction with JavaScript. This should
    help designers and developers understand the styling strategy without examining all rules.
Dependencies: CSS frameworks, design tokens, parent stylesheets, or build tools
Exports: Styling for specific components, utility classes, or global design system elements
Interfaces: CSS custom properties, class naming conventions, or component APIs
Environment: Target browsers, device types, and environment-specific styling considerations
Related: Links to design system documentation, component libraries, or style guides
Implementation: CSS methodologies (BEM, OOCSS), naming conventions, or optimization techniques
*/
```

### JSON Configuration and Data Files (.json)

For JSON files that support comments:
```json
{
  "_header": {
    "purpose": "Brief description of JSON file's purpose, data structure, and primary use cases",
    "scope": "What this JSON file configures or contains (app settings, data schema, API responses, etc.)",
    "overview": "Comprehensive explanation of the JSON structure, how it's consumed by applications, data validation requirements, update procedures, and integration patterns. Should include information about data types, required vs optional fields, and relationship to other configuration files. This should help developers understand the data structure and usage without examining all properties.",
    "dependencies": "Applications, systems, or services that consume or generate this JSON data",
    "exports": "Key configuration sections, data structures, or settings this file provides",
    "interfaces": "APIs, applications, or systems that interact with this JSON structure",
    "environment": "Target environments and environment-specific data variations",
    "related": "Links to related configuration files, schemas, or documentation",
    "implementation": "Data validation rules, schema location, or update/migration procedures"
  }
}
```

For JSON files without comment support, place header in adjacent README or documentation file with the same comprehensive structure.

### Template Files (.template)

Template files require special headers that document placeholders and usage instructions. Templates are used to generate new files with consistent structure and variable substitution.

**For Markdown Templates** (use HTML comments):
```markdown
<!--
Purpose: Brief description of what this template generates
Scope: Where/when this template should be used (e.g., "All new Python modules")
Overview: Detailed explanation of the template's purpose, structure, and what the generated
    file will contain. Should include information about when to use this template, what it
    provides, and how it fits into the project structure.

Placeholders:
  {{VARIABLE_NAME}}: Description of what this should be replaced with
    - Type: string | number | boolean | path | url
    - Example: "user_service" or "/api/v1/users"
    - Required: yes | no
    - Default: value (if optional)

  {{ANOTHER_VAR}}: Description of another placeholder
    - Type: string
    - Example: "Handles user authentication"
    - Required: yes

Usage:
  1. Copy template to destination:
     cp .ai/templates/template-name.md.template path/to/destination.md

  2. Replace all placeholders with actual values:
     - {{VARIABLE_NAME}}: Replace with X
     - {{ANOTHER_VAR}}: Replace with Y

  3. Remove this template header

  4. Validate generated file:
     markdownlint path/to/destination.md

Related: Links to documentation, standards, or examples
-->

# {{DOCUMENT_TITLE}}

Template content with {{PLACEHOLDERS}} starts here...
```

**For Code Templates** (Python, TypeScript, etc. - use language comments):
```python
"""
Purpose: Brief description of what this template generates
Scope: Where/when this template should be used
Overview: Detailed explanation of the template's purpose and generated file structure.

Placeholders:
  {{MODULE_NAME}}: Python module name in snake_case
    - Type: string (valid Python identifier)
    - Example: "user_service"
    - Required: yes

  {{ClassName}}: Class name in PascalCase
    - Type: string (valid Python class name)
    - Example: "UserService"
    - Required: no

Usage:
  1. Copy: cp template.py.template src/{{MODULE_NAME}}.py
  2. Replace placeholders with actual values
  3. Remove this header
  4. Validate: python -m py_compile src/{{MODULE_NAME}}.py

Related: FILE_HEADER_STANDARDS.md, Python plugin docs
"""

# Template content with {{PLACEHOLDERS}}
```

**For YAML/Config Templates** (use # comments):
```yaml
# Purpose: Brief description of what this template generates
# Scope: Where/when this template should be used
# Overview: Detailed explanation of template purpose and configuration structure.
#
# Placeholders:
#   {{CONFIG_NAME}}: Name of the configuration
#     - Type: string
#     - Example: "production-settings"
#     - Required: yes
#
#   {{SETTING_VALUE}}: Configuration value
#     - Type: string | number | boolean
#     - Example: 100 or "high"
#     - Required: yes
#
# Usage:
#   1. Copy: cp template.yaml.template config/{{CONFIG_NAME}}.yaml
#   2. Replace all placeholders
#   3. Remove header (lines 1-XX)
#   4. Validate: yamllint config/{{CONFIG_NAME}}.yaml
#
# Related: Configuration standards, related templates

{{CONFIG_SECTION}}:
  {{SETTING_KEY}}: {{SETTING_VALUE}}
```

**Template Header Requirements:**

1. **Mandatory Fields for Templates:**
   - **Purpose**: What this template generates (not what it is)
   - **Scope**: When/where to use this template
   - **Overview**: Detailed explanation of template and generated output
   - **Placeholders**: Complete list of all placeholders with:
     - Description
     - Type (string, number, boolean, path, etc.)
     - Example value
     - Required/optional status
     - Default value (if optional)
   - **Usage**: Step-by-step instructions including:
     - Copy command with paths
     - Placeholder replacement steps
     - Header removal instruction
     - Validation command
   - **Related**: Links to relevant docs

2. **Placeholder Naming Conventions:**
   - `{{SNAKE_CASE}}` - File names, module names, variables
   - `{{PascalCase}}` - Class names, component names, types
   - `{{camelCase}}` - Function names, methods, properties
   - `{{SCREAMING_SNAKE_CASE}}` - Constants, environment variables
   - `{{kebab-case}}` - URLs, CSS classes, file paths

3. **Placeholder Documentation Format:**
   ```
   {{PLACEHOLDER_NAME}}: Clear description
     - Type: expected value type
     - Example: concrete example
     - Required: yes/no
     - Default: value (if optional)
   ```

4. **Template Validation:**
   - All placeholders in template body must be documented in header
   - Usage instructions must include validation command
   - Template must generate syntactically valid files
   - Template file must have `.template` extension

**Template Examples:**

See `.ai/templates/TEMPLATE_FILE_TEMPLATE.md` for complete template examples and `.ai/howto/how-to-create-a-template.md` for template creation guide.

## Line Break and Formatting Guidelines

### Universal Readability Rules

1. **Double Line Breaks**: Use between major sections and header fields for visual separation
2. **Single Line Breaks**: Use within multi-line field descriptions for natural reading flow
3. **Consistent Indentation**: Maintain proper indentation for continuation lines
4. **Line Length**: Keep lines under 100 characters when possible for readability across different viewers

### File-Type Specific Formatting

#### Markdown Documents
- **Double line breaks**: After each header field (Purpose, Scope, etc.)
- **Horizontal rule (---)**: Separates header from main content
- **Consistent spacing**: Maintains readability across different markdown viewers
- **Natural flow**: Single line breaks within field descriptions for easy reading

#### Code File Comments (Python, TypeScript, JavaScript)
- **Blank lines**: Between field sections within comment blocks for visual organization
- **Consistent indentation**: Maintain language-appropriate comment formatting
- **Multi-line descriptions**: Use proper continuation indentation for readability

#### Configuration Files (YAML, Terraform, Docker)
- **Line continuation**: Use proper indentation with continuation characters for multi-line descriptions
- **Visual alignment**: Align continuation lines for consistent formatting
- **Comment spacing**: Single space after comment character (#) and field colon (:)

#### Example of Proper Line Breaks in Markdown:
```markdown
# Document Title

**Purpose**: Clear, concise description of what this document covers

**Scope**: What areas/components this document applies to

---

## Overview

Document content begins here with proper spacing...
```

#### Example of Proper Line Breaks in Python:
```python
"""
Purpose: Brief description of module functionality

Scope: What this module handles in the system

Overview: Comprehensive explanation of the module's role and responsibilities.
    Multi-line descriptions use proper indentation for continuation lines
    and maintain readability across different development environments.

Dependencies: Key external dependencies or internal modules required

Exports: Main classes, functions, or constants this module provides
"""
```

## Required Header Fields

### Mandatory Fields (All Files)
- **Purpose**: Brief description of file's functionality (1-2 lines)
  - What does this file do?
  - What is its primary responsibility?
- **Scope**: What areas/components this file covers or affects (1-2 lines)
- **Overview**: Comprehensive summary explaining the file's role and operation
  - How does it contribute to the system?
  - What are its key responsibilities and workflows?
  - How does it fit into the larger architecture?
  - Should be sufficient to understand the file without reading code

### Code Files Additional Fields (Python, TypeScript, JavaScript)
- **Dependencies**: Key dependencies, libraries, or related files
- **Exports**: Main classes, functions, components, or constants this file provides
- **Interfaces/Props**: Key APIs, interfaces, or props this file exposes or accepts

### Recommended Fields (Code Files)
- **Implementation**: Notable algorithms, patterns, or architectural decisions
- **State/Behavior**: Important state management or behavioral patterns used
- **Notes**: Any special considerations, warnings, or important operational details

### Optional Fields (All Files)
- **Related**: Links to related files, documentation, or external resources
- **Configuration**: Environment variables or config this file uses

## Implementation Guidelines

### 1. Header Placement
- **Markdown**: Header immediately after the main title
- **Code files**: Header as the first comment block (after shebang if present)
- **HTML**: Header in HTML comment after DOCTYPE
- **Configuration**: Header as comment at top of file

### 2. Content Guidelines
- Keep Purpose field concise but descriptive (1-3 sentences)
- Focus on operational details: what the file does and how it works
- Include key dependencies that aren't obvious from imports
- Mention any special considerations or operational notes
- **Use atemporal language**: Describe current capabilities without referencing time or changes

### 3. Automated Validation
The header linter tool validates:
- Presence of mandatory Purpose field
- Header structure and placement
- Field completeness and format
- Consistent formatting across file types
- Absence of temporal language patterns (dates, "currently", "now", "replaces", etc.)

## Examples

### Good Header Example (Python Linter)
```python
"""
Purpose: Validates file placement according to project structure standards
Scope: Project-wide file organization enforcement across all directories
Overview: This linter analyzes Python, HTML, TypeScript, and configuration files to ensure
    they are located in appropriate directories as defined in STANDARDS.md. It enforces
    project organization rules by checking files against configurable placement rules,
    detecting violations, and providing suggested corrections. The linter supports multiple
    file types and can be integrated into CI/CD pipelines to maintain consistent project structure.
Dependencies: pathlib for file operations, fnmatch for pattern matching, argparse for CLI interface
Exports: FilePlacementLinter class, ViolationType enum, PlacementRule dataclass
Interfaces: main() CLI function, analyze_project() returns List[FilePlacementViolation]
Implementation: Uses rule-based pattern matching with configurable directory allowlists/blocklists
"""
```

### Good Header Example (React Component)
```typescript
/**
 * Purpose: Reusable loading spinner component with customizable styling
 * Scope: UI components across the application for async state management
 * Overview: Displays animated spinner during async operations and data fetching with full
 *     accessibility support. Provides multiple size variants and color themes that integrate
 *     with the design system. Handles loading states for API calls, file uploads, and other
 *     asynchronous operations. Includes proper ARIA labeling and reduced motion support for
 *     accessibility compliance.
 * Dependencies: React, CSS modules for styling, clsx for conditional classes
 * Exports: LoadingSpinner component as default export
 * Props/Interfaces: LoadingSpinnerProps { size?: 'sm' | 'md' | 'lg', color?: string, label?: string }
 * State/Behavior: No internal state, purely presentational component with CSS animations
 */
```

### Good Header Example (API Service)
```typescript
/**
 * Purpose: Handles all HTTP requests to the backend API with authentication
 * Scope: Frontend API integration layer, used by all components needing backend data
 * Overview: Provides typed interfaces for user management, data fetching, and file uploads.
 *     Implements automatic authentication token handling, request/response interceptors,
 *     error normalization, and retry logic for failed requests. Centralizes all backend
 *     communication to ensure consistent error handling, loading states, and data formatting
 *     across the application. Supports file uploads with progress tracking and CRUD operations
 *     for all major entities.
 * Dependencies: axios for HTTP requests, jwt-decode for token handling, custom types from @/types
 * Exports: ApiService class, apiClient instance, ApiError class, RequestConfig type
 * Interfaces: CRUD operations for User, Project, File entities; uploadFile(), downloadFile()
 * Implementation: Uses axios interceptors for auth tokens, implements retry logic and error normalization
 */
```

### Good Header Example (Markdown)
```markdown
# API Documentation Standards

**Purpose**: Define REST API documentation requirements and standards for consistent API docs across all backend services
**Scope**: All API endpoints in the backend application

---
```

### Bad Header Example
```python
"""
This file does stuff with files.
"""
```

## Migration Strategy

### Phase 1: Update Existing Files
1. Add headers to all existing documentation files in `.ai/docs`
2. Update core configuration files (YAML, Terraform)
3. Update plugin AGENT_INSTRUCTIONS.md and README.md files
4. Ensure all mandatory Purpose fields are present and descriptive

### Phase 2: Implement Enhanced Linter
1. Create automated header validation tool
2. Integrate into pre-commit hooks
3. Add to CI/CD pipeline

### Phase 3: Enforce Standards
1. Make header linter blocking in CI/CD
2. Update contribution guidelines
3. Train team on new standards

## Tools and Automation

### Header Linter
- Location: `/tools/design_linters/header_linter.py` (to be created)
- Usage: `python tools/design_linters/header_linter.py --path .`
- Validates: Purpose field presence, header structure, formatting
- Exit codes: 0 (pass), 1 (warnings), 2 (failures)

### Pre-commit Integration
```yaml
- repo: local
  hooks:
    - id: header-check
      name: Check file headers
      entry: python tools/design_linters/header_linter.py
      language: system
      files: \.(md|py|ts|tsx|js|jsx|html|yml|yaml)$
```

## Benefits

1. **Clarity**: Easy to understand what each file does and how it operates
2. **Maintainability**: Clear operational descriptions help with maintenance
3. **Onboarding**: New developers can quickly understand file purposes and dependencies
4. **Documentation**: Headers serve as minimal, always-current documentation
5. **Git Integration**: No redundant metadata that git already tracks

## Exceptions

Files that may not need headers:
- Auto-generated files (clearly marked as such)
- Very small configuration files (<10 lines)
- Template files used by generators
- Third-party files (should be clearly identified)
- Test fixture files that only contain data
