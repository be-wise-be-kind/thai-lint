# Documentation How-To Guides

**Purpose**: Index of step-by-step documentation guides for writing file headers, creating READMEs, and documenting APIs

**Scope**: Practical how-to guides for all documentation tasks in the Documentation Standards Plugin

**Overview**: This document provides a quick reference index to all documentation how-to guides including
    writing file headers, creating README files, and documenting APIs. Each guide includes step-by-step instructions,
    examples, templates, verification steps, and troubleshooting help. Guides are organized by difficulty level
    and estimated time commitment to help users find the right guide for their needs.

**Dependencies**: Documentation standards, templates in .ai/templates/

**Exports**: Guide index, quick reference by use case, difficulty levels, and time estimates

**Related**: file-headers.md, readme-standards.md, api-documentation.md, .ai/templates/

**Implementation**: Organized index with multiple access patterns (by difficulty, by use case, by time)

---

## Available Guides

### 1. How to Write File Headers

**File**: `how-to-write-file-headers.md`
**Difficulty**: Beginner
**Time**: 15-20 minutes
**Prerequisites**: Understanding of file types

Step-by-step guide for writing compliant file headers for all file types including markdown, Python, TypeScript, YAML, and configuration files.

**What you'll learn**:
- Atemporal documentation principles
- Mandatory vs optional header fields
- File-type specific formatting
- How to use header templates
- Common mistakes to avoid

**Templates used**:
- file-header-markdown.template
- file-header-python.template
- file-header-typescript.template
- file-header-yaml.template

**When to use this guide**:
- Creating new files in any language
- Adding headers to existing files
- Understanding header requirements
- Learning documentation standards

---

### 2. How to Create a README

**File**: `how-to-create-readme.md`
**Difficulty**: Intermediate
**Time**: 30-45 minutes
**Prerequisites**: Project understanding, basic markdown

Comprehensive guide for creating effective README documentation that serves as the primary entry point for your project.

**What you'll learn**:
- Essential README sections
- Optional enhancements
- Tech stack documentation
- Installation instructions
- Usage examples and project structure
- Best practices and anti-patterns

**Templates used**:
- README.template

**When to use this guide**:
- Starting a new project
- Improving existing README
- Standardizing project documentation
- Onboarding new team members

---

### 3. How to Document an API

**File**: `how-to-document-api.md`
**Difficulty**: Intermediate
**Time**: 45-60 minutes
**Prerequisites**: API development experience, understanding of HTTP methods

Best practices for documenting REST APIs, endpoints, and web service interfaces comprehensively.

**What you'll learn**:
- Endpoint documentation structure
- Request/response documentation
- Authentication documentation
- Error handling and status codes
- Rate limiting and versioning
- OpenAPI/Swagger integration

**Templates used**:
- file-header-python.template (for API modules)
- file-header-typescript.template (for API services)

**When to use this guide**:
- Building new API endpoints
- Documenting existing APIs
- Creating API reference documentation
- Generating OpenAPI specifications

---

## Quick Reference by Use Case

### Creating New Files

**Need**: Add proper headers to new files
**Guide**: How to Write File Headers
**Time**: 15-20 minutes
**Difficulty**: Beginner

### Starting a New Project

**Need**: Create comprehensive README
**Guide**: How to Create a README
**Time**: 30-45 minutes
**Difficulty**: Intermediate

### Building an API

**Need**: Document API endpoints properly
**Guide**: How to Document an API
**Time**: 45-60 minutes
**Difficulty**: Intermediate

### Improving Documentation

**Need**: Enhance existing docs
**Guides**:
1. How to Write File Headers (for better headers)
2. How to Create a README (for better README)
3. How to Document an API (for better API docs)

### Team Onboarding

**Need**: Train team on documentation standards
**Guides**: Read all three guides in order
1. File Headers (foundation)
2. README (project overview)
3. API Documentation (if applicable)

## Quick Reference by Difficulty

### Beginner (15-20 minutes)

**How to Write File Headers**
- Learn basic documentation principles
- Use header templates
- Apply to new files

### Intermediate (30-60 minutes)

**How to Create a README**
- Structure project documentation
- Write comprehensive installation guides
- Document usage and development

**How to Document an API**
- Document REST endpoints
- Create request/response examples
- Implement OpenAPI specs

## Quick Reference by Time Available

### 15-20 Minutes

**How to Write File Headers**
- Quick wins for better documentation
- Apply to immediate needs
- Learn core principles

### 30-45 Minutes

**How to Create a README**
- Improve project documentation
- Create or enhance README
- Follow proven structure

### 45-60 Minutes

**How to Document an API**
- Comprehensive API documentation
- Generate OpenAPI specs
- Create interactive docs

## What's Included in Each Guide

All how-to guides include:

### 1. Prerequisites
What you need to know or have before starting

### 2. Step-by-Step Instructions
Clear, actionable steps from start to finish

### 3. Examples
Real-world examples demonstrating concepts

### 4. Templates
Ready-to-use templates with placeholders

### 5. Verification Steps
How to check your work is correct

### 6. Common Issues
Troubleshooting common problems

### 7. Best Practices
Industry-standard patterns and tips

### 8. Checklist
Ensure nothing is missed

## How to Use These Guides

### For Learning

1. **Start with prerequisites**: Ensure you have required knowledge
2. **Read through once**: Understand the full process
3. **Follow step-by-step**: Work through each step
4. **Check examples**: Compare your work with examples
5. **Verify completion**: Use checklist to validate

### For Reference

1. **Scan the checklist**: See what's required
2. **Jump to specific sections**: Find what you need
3. **Copy templates**: Use provided templates
4. **Check examples**: Verify format

### For Team Training

1. **Assign guides by role**:
   - All developers: File Headers
   - Project leads: README
   - API developers: API Documentation

2. **Schedule learning time**:
   - Beginner guide: 30-minute session
   - Intermediate guides: 1-hour sessions

3. **Practice together**:
   - Walk through examples as team
   - Apply to actual project files
   - Review each other's work

## Guide Dependencies

```
File Headers (Beginner)
    ↓
    ├─→ README (Intermediate)
    │      ↓
    │      └─→ Complete Project Docs
    │
    └─→ API Documentation (Intermediate)
           ↓
           └─→ Comprehensive API Reference
```

**Recommended Learning Path**:
1. Start with "How to Write File Headers" (foundation)
2. Then "How to Create a README" (if creating project)
3. Then "How to Document an API" (if building APIs)

## Additional Resources

### Documentation Standards
- `file-headers.md` - Complete header reference
- `readme-standards.md` - README structure guide
- `api-documentation.md` - API documentation reference

### Templates
- `.ai/templates/file-header-*.template` - Header templates
- `.ai/templates/README.template` - README template

### Related Plugins
- **Python Plugin**: Python-specific documentation
- **TypeScript Plugin**: TypeScript/JavaScript documentation
- **Docker Plugin**: Docker configuration documentation

## Support

### Getting Help

**For specific questions**:
- Review the relevant standards document
- Check examples in the guide
- Consult troubleshooting sections

**For complex issues**:
- Review related standards documents
- Check plugin documentation
- Consult team leads or documentation maintainers

### Contributing

Found an issue or have improvements?
- Report to ai-projen repository
- Suggest guide enhancements
- Share examples and patterns

## Next Steps

1. **Choose a guide**: Based on your immediate need
2. **Review prerequisites**: Ensure you're ready
3. **Follow the guide**: Step-by-step instructions
4. **Verify your work**: Use checklists
5. **Apply learnings**: To your project files
6. **Share knowledge**: Help team members
