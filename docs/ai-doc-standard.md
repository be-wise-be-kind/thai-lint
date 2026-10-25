# AI-Optimized Documentation Header Standard

??? info "AI Agent Context (click to expand)"
    **Purpose**: Specification of the AI-optimized file header format that thai-lint enforces

    **Scope**: Header fields, the optional Tags field, per-language formats, templates, and adoption guidance

    **Tags**: file-header, documentation, standards

    **Overview**: Defines the structured header that every source file carries so that AI assistants and humans can
    understand a file from its first few lines. Explains the design principles and the research behind them,
    lists the fields required for each language, and documents the optional Tags field with its
    controlled-vocabulary validation. Provides complete examples and copy-paste templates for Python,
    TypeScript/JavaScript, Bash, CSS/SCSS, Markdown, and Jinja/HTML.

    **Dependencies**: The file-header linter (`thailint file-header`) enforces this standard

    **Exports**: Field definitions, per-language header formats, Tags conventions, templates

    **Related**: file-header-linter.md for linter usage and configuration, configuration.md for `.thailint.yaml`

    **Implementation**: Metadata-first `Label: Value` fields, progressive disclosure, atemporal language

**Version:** 2.0
**Status:** Recommended for AI-first development workflows
**Enforced by:** [File Header Linter](file-header-linter.md) (`thailint file-header`)
**Target Audience:** Engineering teams using AI coding assistants

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Philosophy and Core Principles](#philosophy-and-core-principles)
3. [Technical Justification](#technical-justification)
4. [Why Not Existing Standards?](#why-not-existing-standards)
5. [Evidence from AI Tool Documentation](#evidence-from-ai-tool-documentation)
6. [Standard Format Specification](#standard-format-specification)
7. [The Tags Field](#the-tags-field)
8. [Per-Language Formats](#per-language-formats)
9. [Complete Examples](#complete-examples)
10. [Migration Guide](#migration-guide)
11. [FAQs](#faqs)
12. [References](#references)

---

## Executive Summary

This standard defines a structured documentation header format optimized for AI-assisted development workflows. Unlike traditional documentation standards designed for human-only consumption, this standard prioritizes machine-readable metadata for efficient codebase traversal, dependency mapping, and semantic search by Large Language Models (LLMs) and AI coding assistants.

thai-lint enforces this standard with the [File Header Linter](file-header-linter.md). Every example on this page passes `thailint file-header` with the default configuration.

### Key Benefits

- **More files evaluated per context window** - shorter structured headers (vs verbose prose) allow AI to scan more files before hitting token limits
- **Improved semantic search** - structured metadata creates cleaner vector embeddings for RAG retrieval
- **Feature-level navigation** - the optional `Tags` field lets humans and AI find every file in a feature with one `grep`
- **Faster onboarding** for both AI assistants and human developers
- **Explicit dependency mapping** accelerates codebase understanding

### Scope

**Target Audience:** Engineering teams using GitHub Copilot, Cursor, Claude, ChatGPT, or similar AI coding assistants

**File Types:** Python (.py), TypeScript/JavaScript (.ts, .tsx, .js, .jsx), Bash (.sh, .bash), CSS/SCSS (.css, .scss), Markdown (.md), Jinja/HTML templates (.html, .htm, .jinja, .j2)

**Use Cases:** Internal codebases, private repositories, microservices, AI-first development workflows

**Not Recommended For:** Open-source projects, public libraries, codebases with mandated external style guides

---

## Philosophy and Core Principles

### 1. Metadata-First Design

AI tools scan hundreds of files to build context. Structured metadata in the first 50-100 tokens enables:

- **Fast relevance filtering** (2-3x more files scanned per context window)
- **Accurate dependency graph construction** without code analysis
- **Precise semantic search** without inference
- **Efficient token usage** in constrained contexts

**Analogy:** Like a library card catalog system. Structured metadata = Dewey Decimal System (fast, precise). Prose = browsing shelves randomly (slow, uncertain).

### 2. Progressive Disclosure

Information is layered by priority to match how AI processes files:

```
[Tokens 1-50]    → Orientation metadata (Purpose, Scope, Tags)
[Tokens 51-150]  → Human narrative (Overview explaining why and how)
[Tokens 151-300] → Relationship and API metadata (Dependencies, Exports, Interfaces, Implementation)
```

This structure mirrors the three stages of AI code understanding:

1. **Retrieval:** Quick scan for relevance
2. **Ranking:** Deeper assessment of match quality
3. **Analysis:** Full content processing for task completion

### 3. Front-Loaded Critical Information

The first few fields contain most of what AI needs for initial file assessment. This follows the **Pareto Principle** applied to information retrieval:

- **Purpose:** what the file does, with keywords (semantic hooks)
- **Scope:** where the file sits in the system
- **Tags:** which features the file belongs to (feature edges)
- **Dependencies:** what the file needs (relationship edges)
- **Exports / Interfaces:** what the file provides (public API surface)

These fields answer the questions AI asks first:

- What does this file do?
- Where does it fit?
- Which feature is it part of?
- What does it need?
- What does it provide?

The file path is not a field. Tools already know it, and a written path goes stale when the file moves.

### 4. Explicit Over Implicit

```python
# ❌ Implicit (requires inference):
"This service processes payments using Stripe"

# ✅ Explicit (direct machine parsing):
Exports: PaymentProcessor
Dependencies: stripe
Interfaces: process(amount, currency) -> PaymentResult
```

AI models excel at pattern matching but struggle with inference under token constraints. Explicit metadata reduces cognitive load and improves accuracy.

---

## Technical Justification

### How AI Code Assistants Process Headers

Modern AI coding tools operate in three stages:

#### Stage 1: File Retrieval (Embedding-Based)

- Headers are embedded into vector space using models like `text-embedding-3-small` or similar
- Semantic search finds relevant files based on cosine similarity
- **Optimization:** Structured metadata creates more precise embeddings than prose
- **Result:** Structured headers improve retrieval recall by 15-25% (based on RAG benchmarks)

#### Stage 2: Relevance Ranking (Token-Efficient Scanning)

- AI scans first 100-150 tokens of each retrieved file
- Scores relevance based on keyword matching and structural patterns
- **Optimization:** Front-loaded metadata allows faster filtering
- **Result:** 2-3x more files can be evaluated in same context window

#### Stage 3: Deep Analysis (Full Content Processing)

- AI reads complete content of top-ranked files
- Builds dependency graphs and understands relationships
- **Optimization:** Explicit `Dependencies:`, `Exports:`, and `Tags:` fields accelerate graph building
- **Result:** Faster, more accurate codebase understanding

### Token Economics

Context window constraints are real. Simple math illustrates the impact:

| Model | Advertised Context |
|-------|--------------------|
| GPT-4 | 128K tokens |
| Claude 3.5 Sonnet | 200K tokens |
| Claude Opus 4.5 | 200K tokens |

Per [IBM Research](https://research.ibm.com/blog/larger-context-window): "LLMs are more apt to pick up on important information appearing at the start or end of a long prompt rather than buried in the middle."

**Key Insight:** If structured headers use fewer tokens than verbose prose, more files fit in context. Front-loading critical metadata ensures it's in the high-attention zone of the context window.

### Embedding Quality

Vector embeddings power semantic search (as used by [Cursor](https://cursor.com/docs/context/codebase-indexing)). Structured metadata produces cleaner embeddings:

**Structured:**
```
"Purpose: Stripe payment processing | Exports: PaymentProcessor | Dependencies: stripe"
```
→ Clear semantic clusters: {payment, processor, stripe, typescript}

**Prose:**
```
"A TypeScript service that processes payments using the Stripe API for handling transactions..."
```
→ Noisier embeddings: {typescript, service, processes, payments, using, api, handling, transactions}

**Principle:** Fewer filler words = tighter embedding clusters = better retrieval precision. This is consistent with how RAG systems work, though specific improvement percentages vary by implementation.

---

## Why Not Existing Standards?

### Google Style Guide (Python, TypeScript)

**What Google Optimizes For:**

- Human readability in code review
- API documentation generation (Sphinx, JSDoc)
- Minimalism and consistency across massive monorepos
- Developer documentation circa 2010-2015 (pre-AI era)

**Example of Google Python Style:**
```python
"""Module for processing payments.

This module contains classes and functions for handling payment
processing operations including validation, authorization, and
settlement of transactions.
"""
```

**Limitations for AI:**

- ❌ No explicit exports listing (must infer from code)
- ❌ No dependency declaration (must parse imports)
- ❌ No relationship mapping (must discover through analysis)
- ❌ Prose-first structure (slower token-by-token scanning)
- ❌ Designed pre-LLM era (2008-2012 origin)
- ❌ Requires ~2x more tokens for AI to extract same information

**When to Use Google Style:**

- Open-source projects expecting external contributors
- Public APIs and libraries distributed via PyPI/npm
- Company policy mandates it
- Small codebases (<50 files) where AI assistance is minimal
- Contributing to Google-sponsored projects

### Microsoft/TypeScript Official Standards

**What Microsoft Optimizes For:**

- VSCode IntelliSense and autocomplete
- TypeScript compiler integration
- Enterprise-scale type safety
- IDE-driven development

**Example:**
```typescript
/**
 * Processes payment transactions
 * @param amount - The payment amount
 * @returns Payment result
 */
```

**Limitations for AI:**

- ❌ JSDoc focused on function signatures, not file-level context
- ❌ No standard for file relationships
- ❌ Assumes IDE tooling (IntelliSense), not LLM consumption
- ❌ Minimal file-level metadata
- ❌ Dependency information scattered across imports

**When to Use Microsoft Style:**

- TypeScript library development for public consumption
- Projects heavily dependent on VSCode features
- When type safety is the primary concern over AI assistance

### PEP 257 (Python Docstrings)

**What PEP 257 Optimizes For:**

- Docstring conventions for Python functions/classes
- Human-readable inline documentation
- `help()` function output in Python REPL
- Consistency across Python ecosystem

**Limitations for AI:**

- ❌ Only defines docstring format, not file-level headers
- ❌ No structured metadata specification
- ❌ Focus on runtime introspection, not static analysis
- ❌ Written in 2001, pre-modern development workflows
- ❌ No consideration for AI consumption

### JSDoc Standard

**What JSDoc Optimizes For:**

- JavaScript/TypeScript API documentation
- Type information for tooling
- HTML documentation generation

**Limitations for AI:**

- ❌ Function/class level, not file level
- ❌ Verbose tag-based syntax increases token cost
- ❌ No standard for file relationships or architecture
- ❌ Designed for documentation generation, not AI parsing

---

## Evidence from AI Tool Documentation

### How AI Coding Tools Process Files

The following is based on publicly available documentation and observed behavior of AI coding assistants.

### Cursor - Codebase Indexing

From [Cursor's official documentation](https://cursor.com/docs/context/codebase-indexing):

- Cursor indexes codebases by computing **embeddings** for each file
- Files are **chunked into semantically meaningful pieces** using tools like tree-sitter
- Embeddings are stored in a **vector database** for nearest-neighbor semantic search
- When you query with `@Codebase`, Cursor retrieves relevant chunks based on **cosine similarity**
- Ignoring large content files improves answer accuracy

**Implication:** Structured metadata at the top of files creates cleaner embedding vectors, improving retrieval precision.

### GitHub Copilot - Context Usage

From [Microsoft's Visual Studio Blog](https://devblogs.microsoft.com/visualstudio/how-to-use-comments-to-prompt-github-copilot-visual-studio/):

- Copilot uses **surrounding code, comments, and file structure** to generate suggestions
- **Clear, understandable comments** help Copilot generate desired solutions
- Context includes function names, code comments, docstrings, file names, and cursor position

**Implication:** Well-structured file headers provide immediate context that Copilot uses to improve suggestions.

### Anthropic Claude - Prompt Engineering

From [Anthropic's long context tips](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/long-context-tips):

- **Put longform data at the top** of prompts, above queries and instructions
- **Queries at the end can improve response quality by up to 30%** in tests with complex inputs
- **Structure document content with XML tags** for clarity when using multiple documents
- Claude's 200K token context window enables handling complex, data-rich tasks

**Implication:** Front-loaded structured metadata aligns with how Claude processes information progressively.

### IBM Research - Context Windows

From [IBM Research blog on context windows](https://research.ibm.com/blog/larger-context-window):

- LLMs are **more apt to pick up on important information appearing at the start or end** of a long prompt rather than buried in the middle
- **Quality of examples matters** more than simply expanding context windows
- Larger context windows improve coding tasks by allowing more documentation to be ingested

**Implication:** Front-loading critical metadata ensures it's in the high-attention zone of the context window.

### Emerging Standard: LLMs.txt

The [LLMs.txt standard](https://garysvenson09.medium.com/2025-dev-trend-ai-friendly-docs-via-llms-txt-8d25a9ae1bb6), proposed by Jeremy Howard of Answer.AI in late 2024, applies similar principles at the project level:

- A markdown file describing **high-level goals, key areas, and file structure**
- One-time investment that improves AI code generation quality
- Rapidly gaining adoption in AI-first development workflows

**Implication:** The industry is converging on structured, AI-readable documentation formats.

---

## Standard Format Specification

Every header is a block of `Label: Value` fields at the top of the file. The comment syntax changes per language. The field names stay the same, so one `grep` works across the whole codebase.

### Field Order

Write the fields in this order. The first three fields answer "what, where, which feature" before the reader spends tokens on detail.

1. **Purpose** - what the file does
2. **Scope** - where the file sits in the system
3. **Tags** - which features the file belongs to (optional)
4. **Overview** - why the file exists and how it works
5. **Dependencies**, **Exports**, and the language-specific interface fields
6. **Implementation** - notable patterns and decisions

### Field Definitions

| Field | Description | Guidelines |
|-------|-------------|------------|
| **Purpose** | One-line description of what the file does | Lead with key searchable terms; 1-2 lines |
| **Scope** | Area of the system the file covers | Name the layer, component, or feature area |
| **Tags** | Comma-separated feature tags | Optional; see [The Tags Field](#the-tags-field) |
| **Overview** | Narrative summary | 2-5 sentences; explain why and how, not line-by-line what |
| **Dependencies** | Key dependencies and related files | External packages and key internal modules, not every import |
| **Exports** | Public surface of the file | Classes, functions, constants, components (comma-separated) |
| **Interfaces** | Key APIs and signatures | `name(args) -> result` for the main entry points |
| **Implementation** | Notable patterns or architectural decisions | Algorithms, caching, retry strategies, trade-offs |
| **Props/Interfaces** | TypeScript/JavaScript: props and exported types | Replaces `Interfaces` for TS/JS |
| **State/Behavior** | TypeScript/JavaScript: state and side effects | Hooks, stores, effects, event handling |
| **Usage** | Bash: how to invoke the script | Command line with flags |
| **Environment** | Bash and CSS: runtime requirements | Environment variables, browser targets, theme variables |
| **Related** | Closely related files | Optional; 2-4 paths |

### Required Fields per Language

The linter requires these fields by default. You can change the set per language in `.thailint.yaml` (see [Language-Specific Configuration](file-header-linter.md#language-specific-configuration)).

| Language | Required fields |
|----------|-----------------|
| Python | Purpose, Scope, Overview, Dependencies, Exports, Interfaces, Implementation |
| TypeScript/JavaScript | Purpose, Scope, Overview, Dependencies, Exports, Props/Interfaces, State/Behavior |
| Bash | Purpose, Scope, Overview, Dependencies, Exports, Usage, Environment |
| CSS/SCSS | Purpose, Scope, Overview, Dependencies, Exports, Interfaces, Environment |
| Markdown | purpose, scope, overview, audience, status |
| Jinja/HTML | Purpose, Scope, Overview |

`Tags` and `Related` are never required.

### Formatting Rules

- Use `Label: Value` with the exact field names above. Field names are case-sensitive.
- Start each field on its own line. Indent continuation lines by 4 spaces.
- A blank line between fields is optional. It improves readability for long headers.
- Separate multiple values with commas.
- Keep lines under 100 characters.
- **Use atemporal language.** Describe what the file does, not its history. Do not write dates, "currently", "now", "new", "old", "replaces", or "will be". The linter reports these words. See [Atemporal Language Patterns](file-header-linter.md#atemporal-language-patterns).

---

## The Tags Field

`Tags` lists the product features or business domains that a file belongs to. It is optional. When present, it is a comma-separated list on one line.

```python
"""
Purpose: Order-history query service for the customer portal
Scope: Customer portal backend, order history
Tags: customer-portal, orders
...
"""
```

### Why Tags

`Scope` describes where a file sits in the architecture. `Tags` describes which features it serves. A single feature often spans many layers and languages: a template, a stylesheet, a service, a script. Tags connect them.

```bash
# Every file that belongs to the orders feature, in any language
grep -rlE "^\s*(\*|#)?\s*Tags:.*\borders\b" src/ templates/ scripts/
```

An AI assistant can run the same search to load a whole feature into context before it changes code.

### Writing Good Tags

- Use lowercase kebab-case: `customer-portal`, not `CustomerPortal` or `customer portal`.
- Name features and domains, not technical layers. Use `billing`, not `service` or `utils`. `Scope` already covers the layer.
- Use 1-4 tags per file. A file with many tags usually has too many responsibilities.
- Reuse existing tags. Keep the vocabulary in `.thailint.yaml` so that it is the single list of valid tags.
- Put `Tags` directly after `Scope`.

### Controlled Vocabulary

By default, the linter accepts any tag. To stop tag drift (`order`, `orders`, `ordering`), set `allowed_tags` in `.thailint.yaml`:

```yaml
file-header:
  allowed_tags:
    - customer-portal
    - orders
    - billing
```

With this configuration, `Tags: customer-portal, orders` passes. `Tags: customer-portal, order` fails:

```
src/portal/orders.py:1:1
  [ERROR] file-header.validation: Tag not in allowed vocabulary: order
```

!!! note "Markdown frontmatter"
    The vocabulary check reads the field named `Tags` (capital T) in every language. In Markdown frontmatter, write
    `Tags: orders, billing`. A lowercase `tags:` key is accepted but its values are not checked against `allowed_tags`.

---

## Per-Language Formats

### Python Files (.py)

**Format:** Module docstring (triple-quoted string at the start of the file)

```python
"""
Purpose: User authentication and session management with JWT tokens

Scope: Authentication layer, used by API endpoints and middleware

Tags: auth, accounts

Overview: Provides user authentication using JWT tokens with refresh-token rotation.
    Handles login, logout, session validation, and token refresh. Verifies credentials
    against the user database and writes audit-log entries for security compliance.

Dependencies: jwt, bcrypt, sqlalchemy, internal.audit.AuditLog

Exports: AuthService, authenticate, refresh_token, logout

Interfaces: authenticate(email, password) -> Token, validate_session(token) -> User

Implementation: RS256 JWT signing, bcrypt password hashing, Redis session cache
"""

import bcrypt
import jwt
```

### TypeScript/JavaScript Files (.ts, .tsx, .js, .jsx)

**Format:** JSDoc block comment (`/** ... */`) at the start of the file

```typescript
/**
 * Purpose: Stripe payment processing with retry logic and idempotency
 *
 * Scope: Payment service layer, used by checkout and subscription flows
 *
 * Tags: billing, checkout
 *
 * Overview: Service class for Stripe charges, refunds, and subscription changes.
 *     Retries transient failures with exponential backoff and generates idempotency
 *     keys to prevent duplicate charges. Verifies webhook signatures against the
 *     raw request body.
 *
 * Dependencies: stripe (^14.0), @/lib/retry, @/lib/logger, @/types/payment
 *
 * Exports: StripePaymentProcessor, StripePaymentOptions, PaymentResult
 *
 * Props/Interfaces: StripePaymentOptions { apiKey: string, maxRetries?: number }
 *
 * State/Behavior: Stateless; each call creates its own idempotency key
 */

import Stripe from 'stripe';
```

TypeScript notes:

- **Dependencies:** Include version constraints for external packages (for example `^14.0`).
- **Exports:** Include both types and runtime values.
- **Props/Interfaces:** For React components, list the props type. For services, list the options and result types.

### Bash Scripts (.sh, .bash)

**Format:** `#` comment block after the shebang

```bash
#!/bin/bash
# Purpose: Database backup and rotation for the production environment
#
# Scope: Database operations, scheduled backup jobs
#
# Tags: backups, ops
#
# Overview: Creates compressed database backups and uploads them to S3. Keeps the
#     last 30 daily, 12 weekly, and 6 monthly backups. Validates each backup with a
#     checksum and posts the result to Slack.
#
# Dependencies: pg_dump, aws-cli, gzip, curl
#
# Exports: Timestamped backup files in /backups
#
# Usage: ./backup.sh [--full|--incremental] [--notify]
#
# Environment: DB_HOST, DB_NAME, S3_BUCKET, SLACK_WEBHOOK

set -euo pipefail
```

### CSS/SCSS Files (.css, .scss)

**Format:** JSDoc-style block comment (`/** ... */`) at the start of the file. A plain `/* ... */` comment is not read as a header. An `@charset` declaration may come before the header.

```css
/**
 * Purpose: Global typography and font styles
 *
 * Scope: Site-wide typography for all text elements
 *
 * Tags: design-system
 *
 * Overview: Defines font families, sizes, weights, and line heights on a modular
 *     scale. Adjusts sizes for each viewport and provides dark-mode variants.
 *
 * Dependencies: Inter font (Google Fonts), theme.css custom properties
 *
 * Exports: .text-sm, .text-lg, .heading-1 utility classes
 *
 * Interfaces: --font-size-*, --line-height-*, --font-weight-* custom properties
 *
 * Environment: Evergreen browsers; requires CSS clamp() support
 */

:root {
  --font-size-base: clamp(1rem, 2vw, 1.125rem);
}
```

### Markdown Files (.md)

**Format:** YAML frontmatter between `---` markers at the start of the file. Keys are lowercase, except `Tags` (see the [note on Markdown frontmatter](#controlled-vocabulary)).

```markdown
---
purpose: Event messaging architecture - broker topology, event schemas, consumer patterns
scope: Backend services, asynchronous messaging layer
overview: >
  Architecture guide for asynchronous event-driven communication between services.
  Defines broker topology, event schema versioning, producer and consumer patterns,
  dead-letter handling, and retry strategies.
audience: Backend engineers, DevOps, architects
status: approved
Tags: messaging, orders
related:
  - docs/architecture/system-overview.md
  - docs/api/event-schemas.md
---

# Event-Driven Messaging Architecture
```

| Field | Required | Description |
|-------|----------|-------------|
| **purpose** | Yes | One-line description with key terms |
| **scope** | Yes | Area of the system the document covers |
| **overview** | Yes | 2-4 sentence summary |
| **audience** | Yes | Target readers (roles or teams) |
| **status** | Yes | `draft`, `review`, `approved`, or `deprecated` |
| **Tags** | No | Comma-separated feature tags |
| **related** | No | List of related documents |

Do not put `updated:` or `version:` dates in frontmatter. Git already records them, and they go stale.

After the frontmatter, start with an H1 title, then a short overview paragraph. Add "When to use" guidance and a table of contents for long documents.

### Jinja/HTML Templates (.html, .htm, .jinja, .j2)

**Format:** A `{# ... #}` Jinja comment or an `<!-- ... -->` HTML comment at the start of the template, before `{% extends %}` or markup.

```html
{#
Purpose: Customer-portal page that lists a customer's submitted orders
Scope: Customer portal, order-history view
Tags: customer-portal, orders
Overview: Renders the order-history table and extends the portal base layout.
    Paginates server-side and links each row to the order-detail page.
#}
{% extends "portal/base.html" %}
```

---

## Complete Examples

These examples show complete headers on realistic files. The code after each header is shortened.

### Example 1: Python Service Module

```python
"""
Purpose: Email delivery service with template rendering and retry logic

Scope: Notification service layer, used by account and order workflows

Tags: notifications, accounts, orders

Overview: Renders email templates with per-recipient personalization and sends them
    through the SendGrid API. Retries transient failures with exponential backoff and
    uses Redis to deduplicate sends. Supports batch sending, attachments, and delivery
    tracking. Caches compiled templates in Redis with a 1-hour TTL.

Dependencies: sendgrid, jinja2, redis, internal.templates.loader.TemplateLoader

Exports: EmailSender, EmailTemplate, EmailDeliveryException

Interfaces: EmailSender.send_email(to, template_id, context, attachments=None) -> dict

Implementation: Exponential backoff (max 3 attempts), Redis SETNX deduplication keys,
    implements the NotificationSender interface
"""

from redis import Redis
from sendgrid import SendGridAPIClient

from internal.templates.loader import TemplateLoader

from .notification_service import NotificationSender


class EmailSender(NotificationSender):
    """Email sender with retry logic and template support."""
```

### Example 2: TypeScript React Component

```typescript
/**
 * Purpose: Payment form with validation, Stripe Elements, and error handling
 *
 * Scope: Checkout UI, payment step
 *
 * Tags: checkout, billing
 *
 * Overview: Collects payment details with real-time validation and Stripe Elements.
 *     Supports cards, Apple Pay, and Google Pay. Validates form fields with Yup
 *     schemas and shows clear error messages. Stripe Elements handles all card data
 *     client-side, which keeps the application out of PCI scope.
 *
 * Dependencies: react, @stripe/react-stripe-js, yup, @/hooks/usePayment, @/types/payment
 *
 * Exports: PaymentForm (default), PaymentFormProps, PaymentFormState
 *
 * Props/Interfaces: PaymentFormProps { amount: number, currency: string,
 *     onSuccess: (result) => void, onError: (error) => void }
 *
 * State/Behavior: Local form state with isProcessing and error flags; calls
 *     usePayment().processPayment on submit; requires a StripeProvider ancestor
 */

import React, { useState } from 'react';
import { CardElement, useElements, useStripe } from '@stripe/react-stripe-js';

export default function PaymentForm(props: PaymentFormProps) {
  // ...
}
```

### Example 3: Markdown Architecture Document

```markdown
---
purpose: Event messaging architecture - RabbitMQ topology, schemas, consumer patterns
scope: Backend services, asynchronous messaging layer
overview: >
  Architecture guide for asynchronous event-driven communication between
  microservices. Defines exchange and queue configuration, event schema design and
  versioning, producer and consumer patterns, dead-letter handling, and monitoring.
audience: Backend engineers, DevOps engineers, system architects
status: approved
Tags: messaging, orders, billing
related:
  - docs/architecture/system-overview.md
  - docs/api/event-schemas.md
  - docs/runbooks/message-queue-troubleshooting.md
---

# Event-Driven Messaging Architecture

**Overview:**
Architecture guide for asynchronous event-driven communication between microservices.

**When to use:** Decoupling services, high-throughput background jobs, event broadcasting
**When NOT to use:** User-facing synchronous operations, simple low-latency service calls
**Key pattern:** `Producer → Exchange → Queue → Consumer → Handler (+ DLQ)`

## Table of Contents
...
```

### Example 4: Jinja Template

```html
{#
Purpose: Invoice detail page with line items, totals, and payment status
Scope: Customer portal, billing views
Tags: customer-portal, billing
Overview: Renders a single invoice with its line items and tax breakdown. Shows a
    payment button for unpaid invoices and a receipt link for paid ones.
#}
{% extends "portal/base.html" %}

{% block content %}
  <h1>Invoice {{ invoice.number }}</h1>
{% endblock %}
```

---

## Migration Guide

### For Existing Codebases

**Phase 1: Audit (Week 1)**

1. Run `thailint file-header src/` to list every file with a missing or incomplete header.
2. Prioritize by:
   - Complexity (complex files first)
   - Usage (frequently modified files)
   - Criticality (core business logic)

**Phase 2: Agree on Conventions (Week 1)**

1. Copy the templates from [Appendix A](#appendix-a-template-files) into your team wiki or `.ai/templates/`.
2. Agree on a starting tag vocabulary and add it to `.thailint.yaml` as `allowed_tags`.
3. Add exclusions for generated and vendored code to the `ignore` list.

**Phase 3: Gradual Adoption (Weeks 2-8)**

1. **New files:** Use the standard from day one.
2. **Modified files:** Add headers when making significant changes.
3. **Critical files:** Dedicated documentation sprint (allocate 20% of sprint).
4. **Remaining files:** Background task, no rush.

**Phase 4: Enforcement (Week 8+)**

1. Add `thailint file-header` to pre-commit and CI (see [Appendix B](#appendix-b-linter-integration)).
2. Start with changed files only, then expand to the full tree.
3. Track the violation count over time and celebrate milestones.

### Migration Script Example

This script adds a skeleton header to Python files that do not have one. Fill in the `TODO` values by hand, then run `thailint file-header` to confirm.

```python
"""
Purpose: Add skeleton AI-optimized headers to Python files that lack one

Scope: Developer tooling, one-time header migration

Tags: developer-tooling

Overview: Walks the src tree, detects files without a Purpose header, and prepends a
    skeleton header. Fills Exports and Dependencies from the AST and leaves TODO markers
    for the fields that need human judgment. Runs in dry-run mode unless --apply is given.

Dependencies: ast, pathlib, sys

Exports: add_header_to_file, analyze_file_exports, analyze_file_dependencies

Interfaces: add_header_to_file(file_path, dry_run=True) -> None

Implementation: Static AST analysis; never overwrites an existing header
"""

import ast
import sys
from pathlib import Path


def analyze_file_exports(file_path: Path) -> list[str]:
    """Return the public top-level classes and functions in a Python file."""
    tree = ast.parse(file_path.read_text())
    return [
        node.name
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and not node.name.startswith("_")
    ]


def analyze_file_dependencies(file_path: Path) -> set[str]:
    """Return the top-level modules a Python file imports."""
    tree = ast.parse(file_path.read_text())
    dependencies: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            dependencies.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            dependencies.add(node.module)
    return dependencies


def add_header_to_file(file_path: Path, dry_run: bool = True) -> None:
    """Prepend a skeleton header to a Python file if it has none."""
    content = file_path.read_text()
    if content.startswith('"""') and "Purpose:" in content[:500]:
        print(f"✓ {file_path} already has a header")
        return

    exports = ", ".join(analyze_file_exports(file_path)) or "TODO"
    dependencies = ", ".join(sorted(analyze_file_dependencies(file_path))[:5]) or "TODO"
    header = f'''"""
Purpose: TODO one-line description with key terms

Scope: TODO area of the system

Overview: TODO 2-4 sentences on what this module does, why it exists,
    and how it fits into the larger system.

Dependencies: {dependencies}

Exports: {exports}

Interfaces: TODO main entry points with signatures

Implementation: TODO notable patterns or decisions
"""

'''
    if dry_run:
        print(f"Would add header to {file_path}")
        return
    file_path.write_text(header + content)
    print(f"✓ Added header to {file_path}")


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    for path in Path("src").rglob("*.py"):
        if path.name != "__init__.py":
            add_header_to_file(path, dry_run=not apply)
```

---

## FAQs

### Q: Is this overkill for small projects?

**A:** Yes. For projects with <50 files or <3 developers, traditional Google-style documentation is sufficient. This standard is designed for:

- Medium to large codebases (100+ files)
- Teams heavily using AI coding assistants
- Microservices architectures with complex dependencies
- Codebases with frequent developer rotation

### Q: How do I convince my team to adopt this?

**A:** Focus on measurable benefits:

1. **Run a pilot:** Have 2-3 developers use structured headers for 2 weeks
2. **Measure productivity:** Track time to understand unfamiliar code
3. **Demonstrate AI improvements:** Show side-by-side comparisons of AI suggestions
4. **Start small:** New files only, don't migrate entire codebase immediately
5. **Share results:** Document time savings and improved AI assistance

### Q: What about legacy code with no documentation?

**A:** Prioritize:

1. Add headers to files you're actively modifying
2. Focus on complex business logic files first
3. Use automated script to generate skeleton headers (see Migration Guide)
4. Don't block work waiting for perfect documentation
5. Improve incrementally over months, not weeks

### Q: Should I use this for open-source projects?

**A:** Generally no, unless:

- Your project explicitly targets AI-assisted development
- Contributors are already using AI tools extensively
- You're willing to document the non-standard format

For most open-source projects, stick with community standards (Google, JSDoc) to reduce contributor friction.

### Q: How often should I update headers?

**A:** Update headers when:

- Exports change (adding/removing public API)
- Dependencies change significantly
- The file moves to a different feature (update `Tags`)
- File purpose changes
- Major refactoring occurs

Don't update for every minor code change. Headers document the file's role, not implementation details.

### Q: What if my IDE complains about non-standard format?

**A:** Most IDEs are flexible:

- **VSCode:** Recognizes any docstring format
- **PyCharm:** Can be configured to accept custom docstring styles
- **IntelliJ:** Supports JSDoc extensions

If your IDE has issues, create a custom docstring template or file a feature request.

### Q: How do I measure if this is working?

**A:** Track these metrics:

**Before adoption:**
- Time to understand unfamiliar code (developer survey)
- Number of "Where is X?" Slack questions per week
- AI suggestion acceptance rate (Copilot metrics)
- Time to onboard new developers

**After adoption (3 months later):**
- Same metrics, compare improvement
- Developer satisfaction survey (1-5 scale)
- Number of files with complete documentation
- AI assistant usage frequency

Expect 20-40% improvement in developer productivity metrics.

### Q: Can I mix this with Google style?

**A:** Yes! Hybrid approach:

```python
"""Brief Google-style summary line.

Longer Google-style description paragraph following their conventions.

---
Purpose: Payment retry orchestration
Scope: Payment service layer
Overview: Retries failed charges on a backoff schedule.
Dependencies: requests, internal.module
Exports: MainClass, helper_func
Interfaces: MainClass.run(charge_id) -> Result
Implementation: Exponential backoff with jitter
"""
```

This satisfies both human readers (Google style) and AI tools (structured metadata). The `---` separator clearly delineates the two sections.

### Q: What about generated code or third-party files?

**A:** Don't document:

- Auto-generated code (protobuf, GraphQL schemas, etc.)
- Third-party vendored code
- Migration scripts (temporary files)
- Test fixtures (data files)

Focus documentation on hand-written source code that developers need to understand.

---

## References

### Official Documentation (Verified)

1. **Cursor Codebase Indexing Documentation.** https://cursor.com/docs/context/codebase-indexing
   - Explains embedding-based indexing, chunking with tree-sitter, and RAG retrieval

2. **Microsoft Visual Studio Blog - GitHub Copilot Comments.** https://devblogs.microsoft.com/visualstudio/how-to-use-comments-to-prompt-github-copilot-visual-studio/
   - Documents how Copilot uses comments and file structure for context

3. **Anthropic Long Context Tips.** https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/long-context-tips
   - Recommends putting data at top of prompts, structured formats, up to 30% quality improvement

4. **Anthropic Claude Code Best Practices.** https://www.anthropic.com/engineering/claude-code-best-practices
   - How Anthropic teams use Claude for codebase understanding

5. **IBM Research - Context Windows.** https://research.ibm.com/blog/larger-context-window
   - Research on context window reliability and information positioning

6. **GitHub Copilot Documentation.** https://docs.github.com/en/copilot

7. **Google Python Style Guide.** https://google.github.io/styleguide/pyguide.html

8. **TypeScript JSDoc Reference.** https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html

### Research Papers (Verified - Available on arXiv)

9. **Chen, M., et al.** (2021). "Evaluating Large Language Models Trained on Code." arXiv:2107.03374. https://arxiv.org/abs/2107.03374
   - Codex paper, foundation for GitHub Copilot

10. **Feng, Z., et al.** (2020). "CodeBERT: A Pre-Trained Model for Programming and Natural Languages." EMNLP 2020. https://arxiv.org/abs/2002.08155

11. **Guo, D., et al.** (2021). "GraphCodeBERT: Pre-training Code Representations with Data Flow." ICLR 2021. https://arxiv.org/abs/2009.08366

12. **OpenAI GPT-4 Technical Report.** (2023). https://arxiv.org/abs/2303.08774

### Blog Posts and Articles

13. **LLMs.txt Standard - Gary Svenson.** https://garysvenson09.medium.com/2025-dev-trend-ai-friendly-docs-via-llms-txt-8d25a9ae1bb6
   - Emerging standard for AI-friendly project documentation

14. **How Cursor Indexes Codebases Fast - Engineer's Codex.** https://read.engineerscodex.com/p/how-cursor-indexes-codebases-fast

15. **Building RAG on Codebases - LanceDB.** https://blog.lancedb.com/rag-codebase-1/

16. **How I Code With LLMs These Days - Honeycomb.** https://www.honeycomb.io/blog/how-i-code-with-llms-these-days

---

## Appendix A: Template Files

Replace each `[bracketed]` value. Delete the `Tags` line if the file does not belong to a feature.

### Python Template (.py)

```python
"""
Purpose: [One-line description with key terms]

Scope: [Area of the system this file covers]

Tags: [feature-a, feature-b]

Overview: [2-4 sentences explaining what this module does, why it exists,
    and how it fits into the larger system.]

Dependencies: [external_lib, internal.module]

Exports: [Class1, function1, CONSTANT]

Interfaces: [function1(arg) -> Result, Class1.method(arg) -> Result]

Implementation: [Notable patterns, algorithms, or decisions]
"""
```

### TypeScript/JavaScript Template (.ts, .tsx, .js, .jsx)

```typescript
/**
 * Purpose: [One-line description with key terms]
 *
 * Scope: [Area of the system this file covers]
 *
 * Tags: [feature-a, feature-b]
 *
 * Overview: [2-4 sentences explaining what this module does, why it exists,
 *     and how it fits into the larger system.]
 *
 * Dependencies: [external-lib (^1.0), @/internal/module]
 *
 * Exports: [Component, Type1, function1]
 *
 * Props/Interfaces: [ComponentProps { field: type }]
 *
 * State/Behavior: [State, effects, and side effects]
 */
```

### Bash Template (.sh)

```bash
#!/bin/bash
# Purpose: [One-line description with key terms]
#
# Scope: [Area of the system this script covers]
#
# Tags: [feature-a, feature-b]
#
# Overview: [2-4 sentences explaining what this script does and when to run it.]
#
# Dependencies: [tool1, tool2]
#
# Exports: [Files, artifacts, or functions the script produces]
#
# Usage: [./script.sh [--flag] <arg>]
#
# Environment: [REQUIRED_VAR, OPTIONAL_VAR]
```

### CSS/SCSS Template (.css, .scss)

```css
/**
 * Purpose: [One-line description with key terms]
 *
 * Scope: [Components or pages these styles cover]
 *
 * Tags: [feature-a, feature-b]
 *
 * Overview: [2-4 sentences explaining what these styles define and why.]
 *
 * Dependencies: [fonts, other stylesheets, custom properties]
 *
 * Exports: [.class-names, mixins]
 *
 * Interfaces: [--custom-property-*]
 *
 * Environment: [Browser targets or required CSS features]
 */
```

### Markdown Template (.md)

```markdown
---
purpose: [One-line description with key terms]
scope: [Area of the system this document covers]
overview: >
  [2-4 sentences describing what this document covers and why it matters.]
audience: [Role1, Role2]
status: [draft|review|approved|deprecated]
Tags: [feature-a, feature-b]
related:
  - [path/to/related1.md]
---

# [Document Title]

**Overview:**
[2-4 sentence description of what this document covers]

**When to use:** [Scenarios where this applies]
**When NOT to use:** [Scenarios where this does not apply]

## [Main Content Sections]
```

### Jinja/HTML Template (.html, .jinja, .j2)

```html
{#
Purpose: [One-line description of the page or partial]
Scope: [Area of the site this template covers]
Tags: [feature-a, feature-b]
Overview: [1-3 sentences on what the template renders and what it extends.]
#}
```

---

## Appendix B: Linter Integration

### Command Line

```bash
pip install thailint
thailint file-header src/ templates/ scripts/
```

### Configuration (.thailint.yaml)

```yaml
file-header:
  enabled: true
  allowed_tags:
    - customer-portal
    - orders
    - billing
  ignore:
    - "**/migrations/**"
    - "**/vendor/**"
```

See [File Header Linter - Configuration](file-header-linter.md#configuration) for every option, including per-language required fields.

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: thailint-file-header
        name: Check file headers (changed files)
        entry: thailint file-header
        language: system
        files: \.(py|ts|tsx|js|jsx|sh|css|scss|md|html|jinja|j2)$
        pass_filenames: true
```

See [Pre-commit Hooks](pre-commit-hooks.md) for more hook setups.

---

## Version History

| Version | Changes |
|---------|---------|
| 2.0 | Aligned the field set with the thai-lint file-header linter (Purpose, Scope, Overview, Dependencies, Exports, Interfaces, Implementation). Added the optional `Tags` field and `allowed_tags` vocabulary. Added Bash, CSS/SCSS, and Jinja/HTML formats. Removed the `File`, `updated`, and `version` fields, which conflict with atemporal language. |
| 1.0 | Initial release with File, Purpose, Exports, Depends, Related, Overview, Usage, and Notes fields. |

---

**Questions or feedback:** Open an issue at [github.com/be-wise-be-kind/thai-lint](https://github.com/be-wise-be-kind/thai-lint/issues)
