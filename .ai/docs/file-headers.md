# File Header Standards

**Purpose**: Comprehensive reference guide for file header standards across all file types

**Scope**: All code, configuration, and documentation files in any project using ai-projen

**Overview**: This document provides detailed file header standards for all file types including markdown,
    Python, TypeScript, JavaScript, YAML, Terraform, Docker, HTML, CSS, and scripts. Establishes the
    atemporal documentation principle, defines mandatory and optional fields, provides file-type specific
    formatting guidelines, and includes comprehensive examples. This reference ensures consistent, clear,
    and maintainable documentation across all files in the codebase, focusing on operational information
    that Git doesn't already track.

**Dependencies**: Git version control, text editors, optional header linter tools

**Exports**: Header format standards, formatting rules, field definitions, validation guidelines, and examples

**Related**: .ai/templates/file-header-*.template, DOCUMENTATION_STANDARDS.md, how-to-write-file-headers.md

**Implementation**: Template-based header creation with atemporal documentation and file-type specific formatting

---

## Overview

File headers provide essential documentation at the top of every file, explaining its purpose, scope, and role in the system. This standard establishes a unified approach to file headers across all file types, ensuring consistent documentation while avoiding redundancy with Git-tracked information.

## Core Principles

### 1. Atemporal Documentation

File headers must be written in an atemporal manner - avoiding language that references specific points in time, historical changes, or future plans. This ensures documentation remains accurate and relevant without requiring updates when circumstances change.

**Avoid These Temporal Patterns**:

**Explicit Timestamps**:
- ❌ "Created: 2025-09-12"
- ❌ "Updated: 2025-09-16"
- ❌ "Last modified: September 2025"

**State Change Language**:
- ❌ "This replaces the old implementation"
- ❌ "Changed from X to Y"
- ❌ "New implementation of..."
- ❌ "Formerly known as..."
- ❌ "Migrated from the legacy system"

**Temporal Qualifiers**:
- ❌ "Currently supports..."
- ❌ "Now includes..."
- ❌ "Recently added..."
- ❌ "Previously used for..."
- ❌ "Temporarily disabled"
- ❌ "For now, this handles..."

**Future References**:
- ❌ "Will be implemented"
- ❌ "Planned features include..."
- ❌ "To be added later"
- ❌ "Future improvements"

**Write Instead**:

**Present-tense, factual descriptions**:
- ✅ "Handles user authentication"
- ✅ "Provides data validation"
- ✅ "Implements the circuit breaker pattern"
- ✅ "Manages WebSocket connections"

**Feature descriptions without temporal context**:
- ✅ "Supports JSON and XML formats"
- ✅ "Includes error handling and retry logic"
- ✅ "Provides type-safe API interfaces"

**Capability statements**:
- ✅ "Validates input according to business rules"
- ✅ "Exports reusable UI components"
- ✅ "Integrates with the authentication service"

### 2. Focus on Operational Information

Headers should document information that helps developers understand and work with the file:

**Include**:
- What the file does (functionality)
- How it fits into the system (architecture)
- What it depends on (dependencies)
- What it provides (exports/interfaces)
- Important implementation details
- Special considerations or warnings

**Don't Include** (Git already tracks this):
- Creation dates
- Modification history
- Author names
- Version numbers
- Change logs

### 3. Mandatory vs Optional Fields

**Mandatory Fields** (All files):
- **Purpose**: Brief description of file's functionality (1-2 lines)
- **Scope**: What areas/components this file covers
- **Overview**: Comprehensive summary (3-5+ lines)

**Recommended Fields** (Code files):
- **Dependencies**: Key dependencies
- **Exports**: What this file provides
- **Interfaces/Props**: APIs exposed or accepted

**Optional Fields**:
- **Implementation**: Notable patterns or decisions
- **State/Behavior**: State management patterns
- **Related**: Cross-references to related files
- **Configuration**: Environment variables or config

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

**Formatting Rules**:
- **Double line breaks**: After each header field for visual separation
- **Horizontal rule (---)**: Separates header from main content
- **Single line breaks**: Within multi-line field descriptions for natural reading
- **Consistent spacing**: Maintains readability across markdown viewers

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

**Formatting Rules**:
- **Triple quotes** (""") for docstring
- **Blank lines**: Between field sections for visual organization
- **Multi-line descriptions**: Use proper indentation for continuation
- **First docstring** in file, before imports (after shebang if present)

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

**Formatting Rules**:
- **JSDoc format** (/** */)
- **Asterisk continuation**: Each line starts with ` * `
- **Blank lines**: Between field sections within comment
- **First comment** in file, before imports

### YAML Configuration Files (.yml, .yaml)

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

**Formatting Rules**:
- **Hash comments** (#) at top of file
- **Single space** after # and after field colon
- **Multi-line continuation**: Indent continuation lines with spaces
- **Before any YAML content**

### Terraform/HCL Files (.tf, .hcl)

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

**Formatting Rules**:
- **Hash comments** (#) for HCL
- **Multi-line continuation**: Proper indentation
- **At top of file**, before terraform blocks

### Docker Files (Dockerfile, docker-compose.yml)

```dockerfile
# Purpose: Brief description of container build, orchestration, and deployment configuration
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

**Formatting Rules**:
- **Hash comments** (#) at top
- **Multi-line descriptions**: Indented for continuation
- **Before FROM** in Dockerfile or **before version** in docker-compose.yml

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

**Formatting Rules**:
- **HTML comment** (<!-- -->) after DOCTYPE
- **Multi-line**: Each field on separate line
- **Before <html> tag**

### CSS/SCSS Files (.css, .scss)

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

**Formatting Rules**:
- **Block comment** (/* */)
- **Multi-line**: Each field on separate line
- **At top of file**, before any CSS rules

### Shell Scripts (.sh, .ps1, .bat)

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

**Formatting Rules**:
- **Shebang** (#!/bin/bash) first line
- **Hash comments** (#) after shebang
- **Multi-line**: Indented continuation

### JSON Configuration Files (.json)

For JSON files with comment support:

```json
{
  "_header": {
    "purpose": "Brief description of JSON file's purpose, data structure, and primary use cases",
    "scope": "What this JSON file configures or contains (app settings, data schema, API responses, etc.)",
    "overview": "Comprehensive explanation of the JSON structure, how it's consumed by applications, data validation requirements, update procedures, and integration patterns. Should include information about data types, required vs optional fields, and relationship to other configuration files.",
    "dependencies": "Applications, systems, or services that consume or generate this JSON data",
    "exports": "Key configuration sections, data structures, or settings this file provides",
    "interfaces": "APIs, applications, or systems that interact with this JSON structure",
    "environment": "Target environments and environment-specific data variations",
    "related": "Links to related configuration files, schemas, or documentation",
    "implementation": "Data validation rules, schema location, or update/migration procedures"
  }
}
```

For JSON without comment support, create adjacent README or use documentation file.

## Template Files (.template)

Template files require special headers that document placeholders and usage instructions.

### Markdown Templates

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

### Code Templates

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

## Line Break and Formatting Guidelines

### Universal Readability Rules

1. **Double Line Breaks**: Between major sections and header fields for visual separation
2. **Single Line Breaks**: Within multi-line field descriptions for natural reading
3. **Consistent Indentation**: Proper indentation for continuation lines
4. **Line Length**: Under 100 characters when possible for readability

### File-Type Specific Formatting

**Markdown Documents**:
- Double line breaks after each header field
- Horizontal rule (---) separates header from content
- Consistent spacing across markdown viewers

**Code File Comments** (Python, TypeScript, JavaScript):
- Blank lines between field sections within comment blocks
- Consistent indentation for language-appropriate formatting
- Multi-line descriptions with proper continuation

**Configuration Files** (YAML, Terraform, Docker):
- Line continuation with proper indentation
- Visual alignment for continuation lines
- Single space after comment character and field colon

## Required Header Fields

### Mandatory Fields (All Files)

**Purpose**: Brief description of file's functionality (1-2 lines)
- What does this file do?
- What is its primary responsibility?

**Scope**: What areas/components this file covers or affects (1-2 lines)
- Where is this file used?
- What parts of the system does it affect?

**Overview**: Comprehensive summary explaining the file's role and operation (3-5+ lines)
- How does it contribute to the system?
- What are its key responsibilities and workflows?
- How does it fit into the larger architecture?
- Should be sufficient to understand the file without reading code

### Code Files Additional Fields

**Dependencies**: Key dependencies, libraries, or related files
- External libraries
- Internal modules
- System requirements

**Exports**: Main classes, functions, components, or constants this file provides
- What does this file make available to others?
- What are the primary exports?

**Interfaces/Props**: Key APIs, interfaces, or props this file exposes or accepts
- What interfaces does it expose?
- What props does it accept (React components)?
- What APIs does it provide?

### Recommended Fields (Code Files)

**Implementation**: Notable algorithms, patterns, or architectural decisions
- Special algorithms used
- Design patterns applied
- Architectural decisions

**State/Behavior**: Important state management or behavioral patterns used
- State management approach
- Event handling patterns
- Behavioral characteristics

**Notes**: Special considerations, warnings, or important operational details
- Security considerations
- Performance notes
- Known limitations

### Optional Fields (All Files)

**Related**: Links to related files, documentation, or external resources
**Configuration**: Environment variables or config this file uses
**Environment**: Target environments (dev, staging, prod)

## Implementation Guidelines

### Header Placement

- **Markdown**: Header immediately after the main title
- **Code files**: Header as the first comment block (after shebang if present)
- **HTML**: Header in HTML comment after DOCTYPE
- **Configuration**: Header as comment at top of file

### Content Guidelines

1. **Keep Purpose field concise** but descriptive (1-3 sentences)
2. **Focus on operational details**: what the file does and how it works
3. **Include key dependencies** that aren't obvious from imports
4. **Mention special considerations** or operational notes
5. **Use atemporal language**: Describe current capabilities without referencing time

## Examples

### Good Header Example - Python Module

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

### Good Header Example - React Component

```typescript
/**
 * Purpose: Reusable loading spinner component with customizable styling
 *
 * Scope: UI components across the application for async state management
 *
 * Overview: Displays animated spinner during async operations and data fetching with full
 *     accessibility support. Provides multiple size variants and color themes that integrate
 *     with the design system. Handles loading states for API calls, file uploads, and other
 *     asynchronous operations. Includes proper ARIA labeling and reduced motion support for
 *     accessibility compliance.
 *
 * Dependencies: React, CSS modules for styling, clsx for conditional classes
 *
 * Exports: LoadingSpinner component as default export
 *
 * Props/Interfaces: LoadingSpinnerProps { size?: 'sm' | 'md' | 'lg', color?: string, label?: string }
 *
 * State/Behavior: No internal state, purely presentational component with CSS animations
 */
```

### Good Header Example - Markdown Documentation

```markdown
# API Documentation Standards

**Purpose**: Define REST API documentation requirements and standards for consistent API docs across all backend services

**Scope**: All API endpoints in the backend application

**Overview**: This document establishes comprehensive standards for documenting REST APIs including endpoint
    documentation format, request/response examples, authentication documentation, error handling, and status codes.
    Provides templates and best practices for creating clear, comprehensive API documentation that serves both
    internal developers and external API consumers. Covers OpenAPI/Swagger integration, code examples, and SDK documentation.

**Dependencies**: OpenAPI 3.0 specification, Swagger UI, API development standards

**Exports**: API documentation templates, endpoint documentation standards, example formats

**Related**: .ai/howto/how-to-document-api.md, OpenAPI specification, Swagger documentation

**Implementation**: Template-based documentation with automated OpenAPI spec generation

---
```

### Bad Header Example

```python
"""
This file does stuff with files.
"""
```

**Problems**:
- Missing Purpose, Scope, Overview fields
- No dependencies or exports documented
- Vague description ("does stuff")
- Not helpful for understanding the file

## Validation

### Manual Validation Checklist

- [ ] Purpose field present and descriptive (1-2 lines)
- [ ] Scope field present and clear
- [ ] Overview field present and comprehensive (3-5+ lines)
- [ ] No temporal language (currently, now, recently, etc.)
- [ ] Proper formatting for file type
- [ ] All mandatory fields included
- [ ] Dependencies documented (if applicable)
- [ ] Exports documented (if applicable)

### Automated Validation

If header linter is available:

```bash
# Validate all files
python tools/design_linters/header_linter.py --path .

# Validate specific file
python tools/design_linters/header_linter.py --file src/module.py
```

**Linter checks**:
- Presence of mandatory Purpose field
- Header structure and placement
- Field completeness and format
- Absence of temporal language patterns
- Consistent formatting across file types

## Benefits

1. **Clarity**: Easy to understand what each file does and how it operates
2. **Maintainability**: Clear operational descriptions help with maintenance
3. **Onboarding**: New developers can quickly understand file purposes and dependencies
4. **Documentation**: Headers serve as minimal, always-current documentation
5. **Git Integration**: No redundant metadata that Git already tracks
6. **AI-Friendly**: AI agents can better understand and work with well-documented code
7. **Self-Documenting**: Code documents itself without external documentation

## Common Mistakes to Avoid

1. **Using temporal language**: "Currently", "now", "recently", "will be"
2. **Including timestamps**: Creation dates, modification dates
3. **Too brief Overview**: One sentence is not enough
4. **Missing mandatory fields**: Purpose, Scope, or Overview
5. **Redundant Git info**: Author names, version numbers, change history
6. **Vague descriptions**: "Handles stuff", "Does things"
7. **No dependencies**: Not documenting what the file depends on
8. **No exports**: Not documenting what the file provides

## Next Steps

- **Use templates**: Start with .ai/templates/file-header-*.template
- **Review examples**: Study good examples in this document
- **Follow how-to**: Reference .ai/howto/how-to-write-file-headers.md
- **Validate headers**: Use manual checklist or automated linter
- **Apply to new files**: Use headers for all new files
- **Backfill existing**: Add headers to critical existing files
