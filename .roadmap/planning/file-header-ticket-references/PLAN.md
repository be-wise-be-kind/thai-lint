# Planning Document: Ticket-ID Reference Detection for the `file-header` Linter

**Status**: planning (no implementation yet)
**Repo**: thai-lint (`~/Projects/thai-lint`) — public, project-agnostic; all project conventions arrive via YAML config, zero downstream-project names in source.
**Scope of this change**: extend the existing `file-header` atemporal-language enforcement to flag issue-tracker ticket references in headers. Single linter, single PR.

---

## 1. Context and research

thai-lint's `file-header` linter already enforces **atemporal language** in file headers (`enforce_atemporal`, default on): dates, temporal qualifiers ("currently", "now"), state-change phrasing ("replaces", "migrated from"), and future references ("will be", "planned"). The principle is documented in `.ai/docs/FILE_HEADER_STANDARDS.md` and `AGENTS.md`: a header should describe what the code *does*, atemporally, because headers rot when they pin themselves to a moment in time.

**Issue-tracker ticket IDs in headers are the same class of defect.** A header that says "Implements the validation flow from QCORE-18086" is a pointer to a system thai-lint cannot see and the codebase does not own: trackers get migrated (Jira→Linear→ClickUp), projects get re-keyed, tickets get deleted or renumbered, and the reference degrades into noise. The durable home for "which ticket prompted this change" is the **commit message**, which is immutable, travels with the diff, and is what tracker integrations (Jira Smart Commits, GitHub closes-#N) are built around.

### Research findings

**For "ticket IDs do not belong in code" (the anti-pattern side):**

- *"No ticket numbers in comments"* — Reasonable Code (https://sveljko.github.io/no_ticket_numbers_in_comments/): "ticketing systems are very 'fragile'. They are often changed, which usually means that tickets don't get transferred"; "Think of ticket IDs in comments as pointers to memory you don't own." Remedy: explain the *why* in the comment; references to durable artifacts (RFCs, papers) are fine.
- *Clean Code* (Robert C. Martin): named anti-patterns "journal comments" and "attributions/bylines" — change-history metadata belongs in version control ("the source code control system still remembers it"); comments referencing things outside adjacent code "will soon become outdated, and therefore misleading."
- Atlassian Community guidance: ticket numbers in source are "distracting, become outdated, and basically a maintenance nightmare"; put them in commit messages where Jira links commits to issues automatically.
- OpenStack `GitCommitMessages` wiki: change context belongs in the commit message and must be self-contained — a patch "should be reviewable for correctness without needing to read the bug ticket."

**Counterpoint, honored in the design — TODO/FIXME comments are the established exception:**

- Google Python/C++ style guides: a TODO should carry "a link to a resource that contains the context, ideally a bug reference… because bugs are tracked and have follow-up comments" (e.g. `# TODO: crbug.com/192795 - …`). Google *deprecated* `TODO(username)` in favor of bug links.
- Ruff `TD003` (missing-todo-link) actively *requires* an issue link on TODOs; accepts `#123` and Jira-style `[A-Z]+-\d+`. `eslint-plugin-todo-plz` and `eslint-plugin-jira-ticket-todo-comment` do the same.

So the defensible rule is **not a blanket ban**: ticket IDs in prose/headers are an anti-pattern; ticket IDs in TODO/FIXME markers are conventional and sometimes mandated. The rule flags the former and exempts the latter (configurable).

**Novelty:** existing linters either *require* ticket IDs in TODOs (Ruff TD003, eslint plugins) or flag TODO comments wholesale (ESLint `no-warning-comments`, godox, SonarQube S1135). **No existing linter forbids ticket IDs outside TODOs.** This rule is new.

**Regulated-traceability caveat:** DO-178C / ISO 26262 / IEC 62304 workflows intentionally embed requirement IDs in code. Those teams set `ticket_prefixes` to an empty-but-explicit posture or use per-path `ignore` globs; the feature does not force the convention on them.

---

## 2. Measured viability

Viability was established empirically with throwaway analyzers over QBench (~2,400 app files) and over thai-lint itself, using the exact final rule semantics.

### 2.1 Naive pattern is unusable — justifies the design

A bare `[A-Z]{2,}-\d+` over QBench is swamped by false positives from durable technical identifiers:

| Token | Hits | Token | Hits |
|---|---|---|---|
| UTF-8 | 80 | UTF-16 | 15 |
| LICENSE-2 | 65 | UTF-32 | 12 |
| ISO-8859 | 51 | ISO-2022 | 12 |
| UCS-4 | 16 | ISO-10646 | 8 |

This is why the generic pattern must be **case-sensitive** (uppercase-only — `utf-8` lowercase must not match) **and** filtered through a **built-in exempt-prefix list** (UTF, ISO, SHA, AES, RFC, PEP, UCS, GB, GMT, TIS, UTC, CVE, SSL, TLS, HTTP, MD, CRC, RSA, GPT, LICENSE, ADR).

### 2.2 Final rule semantics — headers only, exemptions + TODO-exempt applied

Measured over **module docstrings (the "header" surface)** across QBench, generic mode:

- **17 files flagged, 100% true positives, 0 false positives.** All are real ticket refs (`QCORE-14103`, `QCORE-18577`, `ENGREQ-2604`, `SB-4`/`SB-6`, …) sitting in header docstrings — exactly the rot the rule targets. All 17 happen to be test files referencing the ticket that motivated the test.
- CVE-style tokens (`CVE-2024-1234`) are safe — `CVE` is a built-in exempt prefix.

This 17-file / 0-FP result is the expected QBench smoke-test baseline (§7).

### 2.3 thai-lint self-lint (dogfood)

The only tokens matching the generic pattern anywhere in thai-lint's own `src/` and `tests/` headers are `UTF-8` and `GPT-4` — both exempt. **Expected dogfood result: 0 violations**, so `just lint-full` / `just lint-file-header` stay green after the feature lands.

### 2.4 Residual false-positive class (documented, not eliminated)

Generic mode will flag domain placeholder IDs that share the shape — e.g. `PO-12345` (purchase orders), part numbers. Mitigations, both first-class and documented:
- `ticket_exempt_prefixes: ["PO"]` — extend the built-in exempt list.
- `ticket_prefixes: ["QCORE", "ENGREQ"]` — zero-FP mode: match *only* configured keys.

---

## 3. Design

Validated against the current code. Key decision: **a new sibling detector class, not an extension of `AtemporalDetector`.**

### 3.1 Why a sibling class

`AtemporalDetector` (`src/linters/file_header/atemporal_detector.py:34`) is built entirely on class-attribute pattern lists pre-compiled at import via `_compile_patterns` (line 29), which forces `re.IGNORECASE`. Ticket detection needs the opposite: **case-sensitive** matching (so `utf-8` lowercase is ignored) and **config-driven, instance-level** compilation (`ticket_prefixes`, extra exemptions can't be class constants). Mixing both compilation models into one class would break its design and push `detect_violations` — which already carries a `nesting` suppression (line 81) — past the Xenon A-grade ceiling. A sibling class with the identical return shape `list[tuple[str, str, int]]` lets the linter reuse the existing violation-building flow.

### 3.2 New file: `src/linters/file_header/ticket_detector.py`

Module-level constants (config-independent, compiled at import):

- `DEFAULT_EXEMPT_PREFIXES: frozenset[str]` = `{UTF, ISO, SHA, AES, RFC, PEP, UCS, GB, GMT, TIS, UTC, CVE, SSL, TLS, HTTP, MD, CRC, RSA, GPT, LICENSE, ADR}`
- `_GENERIC_TICKET = re.compile(r"\b([A-Z]{2,})-\d+\b")` — **no `re.IGNORECASE`**; group 1 = prefix for exemption lookup. Do **not** reuse `_compile_patterns` (it forces IGNORECASE).
- `_TODO_MARKER = re.compile(r"\b(?:TODO|FIXME|HACK|XXX)\b")` — case-sensitive.
- `TRACKER_URL_PATTERNS: list[tuple[Pattern, str]]` (compiled with `re.IGNORECASE` — hosts are case-insensitive):
  - `atlassian\.net/browse/[A-Za-z][A-Za-z0-9]*-\d+` → "JIRA issue URL"
  - `app\.clickup\.com/t/[\w-]+` → "ClickUp task URL"
  - `linear\.app/[\w-]+/issue/[\w-]+` → "Linear issue URL"
  - `github\.com/[\w.-]+/[\w.-]+/issues/\d+` → "GitHub issue URL"
  - `gitlab\.com/[\w./-]+/-/issues/\d+` → "GitLab issue URL"

Class:

```python
class TicketReferenceDetector:
    def __init__(self, ticket_prefixes=None, extra_exempt_prefixes=None, allow_in_todos=True):
        # ticket_prefixes truthy => zero-FP mode:
        #   self._id_pattern = re.compile(rf"\b(?:{'|'.join(re.escape(p) for p in ticket_prefixes)})-\d+\b")
        #   (exemptions irrelevant in this mode)
        # else generic mode:
        #   self._id_pattern = _GENERIC_TICKET
        #   self._exempt = DEFAULT_EXEMPT_PREFIXES | set(extra_exempt_prefixes or [])

    def detect_violations(self, text: str) -> list[tuple[str, str, int]]:
        # enumerate lines (start=1) like AtemporalDetector; delegate per-line work to stay A-grade
```

Private helpers, each trivially A-grade: `_line_violations(line, n)`, `_id_matches(line)` (uses `finditer`, skips `_is_exempt(prefix)` and `_in_todo_context`), `_url_matches(line)`, `_is_exempt(prefix)`, `_in_todo_context(line, start)` = `allow_in_todos and _TODO_MARKER.search(line[:start])`. Returned tuples `(matched_text, description, line_num)` with descriptions like `'ticket ID "QCORE-18086"'` and `'tracker URL (JIRA issue URL)'`.

**Self-lint note:** this new file's own header must avoid literal ticket-shaped tokens (say "ticket-style identifiers", not `PROJ-123`) so the dogfood run in §7 stays clean.

### 3.3 Config — `src/linters/file_header/config.py`

Four flat fields on `FileHeaderConfig`, after `enforce_atemporal` (line 68), matching the existing flat style; mirror each in `from_dict` (line 80):

```python
check_ticket_references: bool = True          # sub-toggle (gated by enforce_atemporal)
ticket_prefixes: list[str] = []               # non-empty => zero-FP mode
ticket_exempt_prefixes: list[str] = []        # merged with built-ins (generic mode)
allow_ticket_refs_in_todos: bool = True       # TODO/FIXME/HACK/XXX exemption
```

User-facing `.thailint.yaml`:

```yaml
file-header:
  enforce_atemporal: true            # master switch; also gates ticket checks
  check_ticket_references: true      # detect ticket IDs / tracker URLs in headers
  ticket_prefixes: []                # e.g. ["QCORE", "ENGREQ"] — match ONLY these (zero FP)
  ticket_exempt_prefixes: []         # e.g. ["PO"] — extra non-ticket prefixes (built-ins: UTF, ISO, SHA, RFC, ...)
  allow_ticket_refs_in_todos: true   # don't flag refs on TODO/FIXME/HACK/XXX lines
```

### 3.4 Wiring — `src/linters/file_header/linter.py`

- Import `TicketReferenceDetector` next to `AtemporalDetector`.
- Single integration point: extend `_check_atemporal_violations` (line 266-283). Its existing early-return on `not config.enforce_atemporal` (line 270) gives the **master-switch interplay for free**. After the existing loop, append `violations.extend(self._check_ticket_violations(header, context, config))`.
- New method `_check_ticket_violations(header, context, config)`: early-return `[]` if `not config.check_ticket_references`; instantiate the detector from the three config fields; map matches → `self._violation_builder.build_ticket_reference(...)`. Keeps both methods A-grade and requires **no change** to the call sites (lines 141, 159), so Markdown automatically inherits prose-fields-only scope (frontmatter keys like `related:` stay unchecked — consistent with existing atemporal behavior).
- Update the class docstring method-count note (line 67-71).

### 3.5 Violation — `src/linters/file_header/violation_builder.py`

New `build_ticket_reference(reference, description, file_path, line) -> Violation`, modeled on `build_atemporal_violation` (line 78):
- message: `f"Ticket reference detected: {description}"`
- suggestion: `"Move ticket references to the commit message; describe what the code does, not which ticket prompted it"`

**Rule ID: reuse `file-header.validation`.** The linter already multiplexes missing-field, invalid-tag, and atemporal violations under this single id (the `ViolationBuilder` takes one `rule_id` at construction). A distinct id would ripple through ignore-directive matching (`_check_specific_rule_ignore`), rule registration, and CLI behavior for no benefit — the distinct `"Ticket reference detected:"` message prefix already gives filterability, and `# thailint: ignore[file-header.validation]` / `thailint-ignore-line` escapes work unchanged.

### 3.6 Line-number convention

`detect_violations` receives the *extracted header text* (e.g. `ast.get_docstring` output), and existing atemporal violations already report header-relative line numbers via `violation.line`; `_has_line_level_ignore` indexes full-file lines with that number — a pre-existing quirk. The new detector **follows the same convention** for consistency; do not "fix" the offset in this feature.

---

## 4. BDD specifications

The contract. The repo uses **plain pytest — do NOT add pytest-bdd.** Each scenario becomes one test named after the scenario, body structured Given/When/Then as arrange/act/assert. New file: `tests/unit/linters/file_header/test_ticket_references.py` (rule-level via `create_mock_context` from `conftest.py`, classes per category like `test_atemporal_language.py`). The test file's own docstring header must avoid literal ticket-shaped tokens (dogfood).

```gherkin
Feature: Ticket-ID reference detection in file headers
  As a maintainer enforcing atemporal headers
  I want ticket references flagged in headers but allowed in TODO markers
  So that headers describe behavior, while TODO debt can still link its tracker

  Background:
    Given the file-header linter with default configuration
    And enforce_atemporal is true and check_ticket_references is true

  # --- Generic detection across header contexts ---

  Scenario: Ticket ID in a Python docstring header is flagged
    Given a Python file whose module docstring Overview cites "PROJ-1234"
    When the file is linted
    Then a violation with message containing "Ticket reference detected" and "PROJ-1234" is reported

  Scenario: Ticket ID in a TypeScript block-comment header is flagged
    Given a TypeScript file whose header block comment cites a ticket ID
    When the file is linted
    Then a ticket-reference violation is reported

  Scenario: Ticket ID in a Bash comment header is flagged
    Given a Bash file whose comment header cites a ticket ID
    When the file is linted
    Then a ticket-reference violation is reported

  Scenario: Ticket ID in a Markdown frontmatter prose field is flagged
    Given a Markdown file whose frontmatter "overview" field cites a ticket ID
    When the file is linted
    Then a ticket-reference violation is reported

  Scenario: Ticket ID in a Markdown frontmatter non-prose field is not flagged
    Given a Markdown file whose frontmatter "related" field cites a ticket ID
    When the file is linted
    Then no ticket-reference violation is reported

  Scenario: Ticket ID in a Jinja/HTML comment header is flagged
    Given a Jinja template whose "{# #}" header cites a ticket ID
    When the file is linted
    Then a ticket-reference violation is reported

  Scenario: Ticket IDs on two header lines report two violations with correct line numbers
    Given a header citing one ticket ID on each of two distinct lines
    When the file is linted
    Then two ticket-reference violations are reported with the header-relative line numbers of those lines

  # --- Built-in exemptions ---

  Scenario: Durable technical identifiers are not flagged
    Given a header mentioning "UTF-8", "SHA-256", "ISO-8601", and "RFC-2616"
    When the file is linted
    Then no ticket-reference violation is reported

  Scenario: Lowercase technical identifiers are not flagged
    Given a header mentioning "utf-8" and "sha-256"
    When the file is linted
    Then no ticket-reference violation is reported

  Scenario: Configured extra exempt prefix suppresses its IDs
    Given ticket_exempt_prefixes is ["PO"]
    And a header containing "PO-12345"
    When the file is linted
    Then no ticket-reference violation is reported

  Scenario: In default generic mode a PO-style ID is flagged
    Given default configuration
    And a header containing "PO-12345"
    When the file is linted
    Then a ticket-reference violation is reported

  # --- Explicit ticket_prefixes (zero-FP) mode ---

  Scenario: Configured ticket prefix is flagged
    Given ticket_prefixes is ["QCORE"]
    And a header containing "QCORE-18086"
    When the file is linted
    Then a ticket-reference violation is reported

  Scenario: A non-configured prefix is ignored in zero-FP mode
    Given ticket_prefixes is ["QCORE"]
    And a header containing "OTHER-123"
    When the file is linted
    Then no ticket-reference violation is reported

  Scenario: Built-in exemptions are irrelevant in zero-FP mode
    Given ticket_prefixes is ["QCORE"]
    And a header containing "UTF-8"
    When the file is linted
    Then no ticket-reference violation is reported

  # --- Tracker URLs ---

  Scenario: A JIRA issue URL is flagged
    Given a header containing an "atlassian.net/browse/PROJ-1" URL
    When the file is linted
    Then a ticket-reference violation describing a JIRA issue URL is reported

  Scenario: A ClickUp task URL is flagged
    Given a header containing an "app.clickup.com/t/abc123" URL
    When the file is linted
    Then a ticket-reference violation is reported

  Scenario: A Linear issue URL is flagged
    Given a header containing a "linear.app/team/issue/ABC-1" URL
    When the file is linted
    Then a ticket-reference violation is reported

  Scenario: GitHub and GitLab issue URLs are flagged
    Given a header containing a GitHub issue URL and a GitLab issue URL
    When the file is linted
    Then a ticket-reference violation is reported for each

  Scenario: A non-issue GitHub URL is not flagged
    Given a header containing a GitHub repository README link
    When the file is linted
    Then no ticket-reference violation is reported

  # --- TODO exemption ---

  Scenario: A ticket ID inside a TODO marker is allowed by default
    Given a header line "TODO(QCORE-18086): tighten validation"
    When the file is linted with defaults
    Then no ticket-reference violation is reported

  Scenario Outline: A ticket ID after a debt marker is allowed
    Given a header line where "<marker>" precedes a ticket ID
    When the file is linted with defaults
    Then no ticket-reference violation is reported
    Examples:
      | marker |
      | FIXME  |
      | HACK   |
      | XXX    |

  Scenario: A ticket ID appearing before the marker is still flagged
    Given a header line where the ticket ID appears before a TODO marker
    When the file is linted
    Then a ticket-reference violation is reported

  Scenario: A tracker URL on a TODO line is allowed
    Given a header line "TODO: see app.clickup.com/t/abc123"
    When the file is linted with defaults
    Then no ticket-reference violation is reported

  Scenario: TODO exemption can be disabled
    Given allow_ticket_refs_in_todos is false
    And a header line "TODO(QCORE-18086): tighten validation"
    When the file is linted
    Then a ticket-reference violation is reported

  # --- Toggles and interplay ---

  Scenario: Disabling ticket checks leaves other atemporal checks running
    Given check_ticket_references is false
    And a header containing both a ticket ID and the qualifier "currently"
    When the file is linted
    Then no ticket-reference violation is reported
    And an atemporal violation for "currently" is still reported

  Scenario: The atemporal master switch overrides the ticket sub-toggle
    Given enforce_atemporal is false and check_ticket_references is true
    And a header containing a ticket ID
    When the file is linted
    Then no ticket-reference violation is reported

  Scenario: A clean header reports no ticket violations
    Given a header with no ticket references or tracker URLs
    When the file is linted
    Then no ticket-reference violation is reported

  Scenario: A line-level ignore directive suppresses a ticket violation
    Given a header line citing a ticket ID and carrying a "thailint-ignore-line" directive
    When the file is linted
    Then the ticket-reference violation is suppressed
```

---

## 5. Build order (TDD)

1. Study `git show a3e4fee` (the Jinja/HTML + Tags feature) as the end-to-end shape template — config field → detector → builder → linter wiring → tests → docs.
2. **Red**: write `tests/unit/linters/file_header/test_ticket_references.py` for all §4 scenarios (config-driven scenarios pass `metadata={"file_header": {...}}` per the existing `test_configuration.py` pattern). Run; all new tests fail.
3. **Green — detector**: implement `src/linters/file_header/ticket_detector.py`.
4. **Green — config**: add the four `FileHeaderConfig` fields + `from_dict` entries.
5. **Green — builder**: add `ViolationBuilder.build_ticket_reference`.
6. **Green — wiring**: extend `_check_atemporal_violations` + add `_check_ticket_violations`; update the header docstrings of the three touched source files.
7. Run the suite (`pytest tests/unit/linters/file_header/`, then full). **Expected existing-test breakage: none** — repo-wide the generic pattern hits only exempt `UTF-8`/`GPT-4` in `src/`/`tests/` headers; existing atemporal tests assert with `>=` counts and message substrings that ticket violations cannot disturb.
8. `just lint-full` quality gates: Pylint 10.00/10, Xenon A-grade everywhere (if the per-line loop trips `nesting`, split `_id_matches` further rather than suppress), MyPy clean, and the dogfood `file-header` pass over `src/`/`tests/`.
9. Docs + CHANGELOG (§6).

---

## 6. Documentation updates

- **`docs/file-header-linter.md`**: add a "Ticket References" category to the atemporal-patterns section (IDs, tracker URLs, TODO exception, built-in exemptions); add the four config keys to the configuration example and options table; add a before/after example ("Implements QCORE-18086" → describe behavior; ticket belongs in the commit message).
- **`.ai/docs/FILE_HEADER_STANDARDS.md`**: under the atemporal principle, add that ticket IDs / tracker URLs are temporal references whose durable home is the commit message, with the explicit TODO/FIXME exception (Google style / Ruff TD003).
- **`CHANGELOG.md`**: Unreleased feature entry (Keep a Changelog format).
- `docs/configuration.md` and `README.md` reference the linter generically — no change needed.

---

## 7. Release gates (smoke tests)

1. **Dogfood** — `just lint-file-header src/ tests/` ⇒ **0 ticket violations** (only exempt `UTF-8`/`GPT-4` present). `just lint-full` exits 0.
2. **QBench headers** — re-run the §2.2 measurement script over QBench module docstrings ⇒ **17 files flagged, 0 false positives**. Spot-check that flagged tokens are all real tracker keys.
3. **Generic-mode FP documentation** — confirm `PO-12345`-style IDs are flagged in default mode and suppressed via `ticket_exempt_prefixes`/`ticket_prefixes`, matching the §4 scenarios.

---

## 8. Edge cases and risks

- **Case sensitivity is load-bearing**: the generic ID pattern must compile WITHOUT `re.IGNORECASE`; reusing `_compile_patterns` would make `utf-8`/`sha-256` match. Call this out in the detector's header `Implementation:` line.
- **`CVE-2024-1234`**: the generic pattern matches the `CVE-2024` portion, but `CVE` is built-in exempt → safe.
- **Domain placeholder IDs** (`PO-12345`, part numbers): false positives in generic mode; mitigated by config (documented, not silently eliminated).
- **Multi-line TODO continuations**: a tracker URL on the wrapped continuation line of a TODO is *not* exempt (exemption is same-line, marker-before-match). Documented limitation; remedy is keeping the ref on the TODO line or a line-level ignore.
- **Empty `ticket_prefixes` means generic mode**, not "match nothing" — guard with truthiness; `re.escape` configured prefixes.
- **Markdown scope**: ticket checks inherit prose-fields-only behavior; non-prose frontmatter keys (`related:`) are intentionally unchecked, matching existing atemporal scope.
- **Dogfood self-lint**: the new source and test file headers must themselves avoid ticket-shaped literals and satisfy `FILE_HEADER_STANDARDS` fields, or the §7 gate fails.

---

## Critical files

- `src/linters/file_header/ticket_detector.py` (new)
- `src/linters/file_header/config.py`
- `src/linters/file_header/linter.py`
- `src/linters/file_header/violation_builder.py`
- `tests/unit/linters/file_header/test_ticket_references.py` (new)
- `docs/file-header-linter.md`, `.ai/docs/FILE_HEADER_STANDARDS.md`, `CHANGELOG.md`
