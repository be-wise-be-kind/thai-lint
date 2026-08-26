# Comment Antecedents Rule - PR Breakdown

**Purpose**: TDD implementation breakdown for adding a comment-antecedents rule to the existing `file_header` linter package

**Scope**: Complete implementation from BDD specification through dogfooding and documentation, as a second rule inside `src/linters/file_header/`

**Overview**: Breaks the `file-header.comment-antecedents` rule into two atomic pull requests. The rule
    attaches to the package that already owns prose scanning, so no CLI command, output-format, or
    registration work is required — the existing `file-header` command filters on rule id namespace and
    inherits text, json, and SARIF output. PR1 lands the complete behavioural specification as failing
    tests; PR2 makes them pass and dogfoods the result. Contains full Gherkin feature specifications that
    serve as the contract for the pytest suite, file manifests, acceptance criteria, and the measured corpus
    baselines that act as release gates.

**Dependencies**: `src/linters/file_header/` (host package), `src/core/base.py` (BaseLintRule), `src/linter_config/ignore.py`, `.ai/docs/SARIF_STANDARDS.md`

**Exports**: Gherkin specifications, per-PR implementation plans, file manifests, acceptance criteria

**Related**: AI_CONTEXT.md for measured evidence and rejected patterns, PROGRESS_TRACKER.md for status tracking

**Implementation**: Strict TDD with red-green-refactor enforced per PR, BDD scenarios mapped one-to-one onto pytest test functions

---

## Overview

Two atomic PRs. The rule lives in the existing `file_header` package under the rule id
`file-header.comment-antecedents`.

**What is NOT needed**, because the host package already provides it:

| Concern | Why it is free |
|---|---|
| CLI command | `_run_file_header_lint` (`src/cli/linters/documentation.py`) filters on `"file-header" in v.rule_id` |
| text / json / SARIF output | Inherited from the `file-header` command's shared formatting |
| Rule registration | `registry.discover_rules("src.linters")` finds any `BaseLintRule` subclass in the package |
| Header boundary | The package's parsers already know where each language's header ends |
| Suppression | `src/linter_config/ignore.py` is generic across all five scopes |

**The TDD contract.** Both PRs follow three phases, in order, and a PR is not reviewable if they were not:

1. **RED** — write the scenarios named in the PR. Run them. They must fail, and fail for the stated reason
   (assertion failure or `ImportError`, not a typo). Commit the failing tests as the first commit.
2. **GREEN** — the minimum implementation that turns them green. No unspecified behaviour.
3. **REFACTOR** — A-grade complexity and 10.00/10 Pylint with the tests staying green.

The repository uses plain pytest. **Do not add `pytest-bdd`.** Each scenario becomes one test function
named after the scenario in snake_case, body structured Given/When/Then as arrange/act/assert.

---

## Gherkin Specification

This is the contract. PR1 lands all of it as failing tests.

### Feature: Comment block extraction

```gherkin
Feature: Comment block extraction
  As the comment-antecedents rule
  I need contiguous mid-file comment lines grouped into blocks
  So that one prose paragraph produces at most one violation

  Scenario: Contiguous hash comment lines form a single block
    Given a Python file with three consecutive "#" comment lines below the header
    When the extractor runs
    Then exactly one comment block is produced
    And the block text joins the three lines with single spaces
    And the block start line is the line number of the first "#" line

  Scenario: A blank line separates two blocks
    Given a shell file with two "#" comment runs separated by a blank line
    When the extractor runs
    Then exactly two comment blocks are produced

  Scenario: A code line separates two blocks
    Given a Terraform file with a "#" comment, a resource line, then another "#" comment
    When the extractor runs
    Then exactly two comment blocks are produced

  Scenario: Slash comment lines form blocks
    Given a TypeScript file with two consecutive "//" comment lines below the header
    When the extractor runs
    Then exactly one comment block is produced

  Scenario: The leading hash-comment header block is skipped
    Given a shell file whose first six lines are a "#" header block
    And a mid-file "#" comment below it
    When the extractor runs
    Then only the mid-file comment block is produced

  Scenario: A shebang does not start the header block
    Given a shell file beginning with "#!/usr/bin/env bash"
    And a "#" header block after the shebang
    And a mid-file "#" comment
    When the extractor runs
    Then only the mid-file comment block is produced

  Scenario: A Python module docstring is not a comment block
    Given a Python file with a module docstring containing the phrase "used to be"
    And no mid-file comments
    When the extractor runs
    Then no comment blocks are produced

  Scenario: An empty file produces no blocks
    Given an empty file
    When the extractor runs
    Then no comment blocks are produced

  Scenario: A file of only a header produces no blocks
    Given a file containing a "#" header block and nothing else
    When the extractor runs
    Then no comment blocks are produced
```

### Feature: Former-state detection (tier 1)

```gherkin
Feature: Former-state detection
  As a reviewer of AI-generated code
  I want comments describing a former code state to be flagged
  So that no comment depends on a diff the reader cannot reach

  Scenario: A comment stating a former state is flagged
    Given a Python file with the mid-file comment "# The lock used to be held across the status flip"
    When the comment-antecedents rule runs
    Then one violation is reported
    And the violation rule id is "file-header.comment-antecedents"
    And the violation line is the first line of the comment block

  Scenario: The violation message names the offending phrase
    Given a Python file with the mid-file comment "# overlap used to be bool and is now enum"
    When the comment-antecedents rule runs
    Then the violation message contains "used to be"

  Scenario: Two matches in one block report once
    Given a comment block containing "used to be" twice
    When the comment-antecedents rule runs
    Then exactly one violation is reported

  Scenario Outline: Former-state detection spans comment syntaxes
    Given a <extension> file with a mid-file <marker> comment "the flag used to be a boolean"
    When the comment-antecedents rule runs
    Then one violation is reported

    Examples:
      | extension | marker |
      | .py       | #      |
      | .sh       | #      |
      | .yaml     | #      |
      | .tf       | #      |
      | .hcl      | #      |
      | .ts       | //     |
      | .go       | //     |
      | .rs       | //     |

  Scenario: A purpose description is not flagged
    Given a Python file with the mid-file comment "# Flow object used to authenticate with the server"
    When the comment-antecedents rule runs
    Then no violation is reported
```

### Feature: Pre-change-state detection (tier 1)

```gherkin
Feature: Pre-change-state detection
  As a reviewer of AI-generated code
  I want comments anchored to a point before the change to be flagged
  So that the reader is not asked to compare against an unreachable state

  Scenario Outline: A pre-change anchor with an existence verb is flagged
    Given a file with the mid-file comment "# <phrase>"
    When the comment-antecedents rule runs
    Then one violation is reported

    Examples:
      | phrase                                                  |
      | the list every tenant had before this filtering existed |
      | exactly as before this feature existed                  |
      | before this deprecation was instituted                  |
      | before this exception was introduced                    |
      | main() before this change                               |

  Scenario Outline: A runtime ordering reference is not flagged
    Given a file with the mid-file comment "# <phrase>"
    When the comment-antecedents rule runs
    Then no violation is reported

    Examples:
      | phrase                                             |
      | the SERVER span was created before this hook ran   |
      | there is a newline before this position            |
      | the customer can submit before this dialog is sent |
      | a bare enabled-check would pass before this arrived |
```

### Feature: Rejected patterns must stay silent

```gherkin
Feature: Rejected patterns stay silent
  As a maintainer
  I want the measured-and-rejected phrases to remain undetected
  So that a future contributor cannot reintroduce them without new evidence

  Scenario Outline: A rejected phrase produces no violation
    Given a file with the mid-file comment "# <comment>"
    When the comment-antecedents rule runs
    Then no violation is reported

    Examples:
      | comment                                                     |
      | ECS never replaces the task when the target stays healthy   |
      | This file replaces the single generic reviewer              |
      | the withheld-save source this branch sets                   |
      | without this patch is_settings_enabled returns False        |
      | We previously failed to make sense of file as a path        |
      | formerly defined here, reexposed for backward compatibility |
      | stand up the new cert before the old one leaves             |
      | THREE dots, not two                                         |
```

### Feature: Coexistence with header validation

```gherkin
Feature: Coexistence with header validation
  As a user running the file-header command
  I want header prose and body prose reported by distinct rules
  So that a flagged phrase is never reported twice

  Scenario: A phrase in a bash header is not reported by the comment rule
    Given a shell file whose header block contains "used to be"
    And no mid-file comments
    When the file-header command runs
    Then no "file-header.comment-antecedents" violation is reported

  Scenario: A phrase in a Python module docstring is not reported by the comment rule
    Given a Python file whose module docstring contains "used to be"
    And no mid-file comments
    When the file-header command runs
    Then no "file-header.comment-antecedents" violation is reported

  Scenario: Header validation is unaffected by the new rule
    Given a Python file whose header contains "currently"
    When the file-header command runs
    Then a "file-header.validation" violation is reported
    And no "file-header.comment-antecedents" violation is reported

  Scenario: Disabling enforce_atemporal does not disable the comment rule
    Given the config sets "file-header.enforce_atemporal" to false
    And a file with a mid-file comment containing "used to be"
    When the file-header command runs
    Then one "file-header.comment-antecedents" violation is reported
```

### Feature: Suppression

```gherkin
Feature: Suppression
  As a developer with a legitimate comment that matches
  I want the standard ignore mechanisms to work
  So that a chatty rule does not become unusable

  Scenario: A line-level ignore suppresses the violation
    Given a comment block that would produce a violation
    And the block's first line ends with "# thailint: ignore[file-header.comment-antecedents]"
    When the comment-antecedents rule runs
    Then no violation is reported

  Scenario: A preceding-line ignore suppresses the violation
    Given a comment block that would produce a violation
    And the preceding line is "# thailint: ignore-next-line[file-header.comment-antecedents]"
    When the comment-antecedents rule runs
    Then no violation is reported

  Scenario: A file-level ignore suppresses all violations in the file
    Given a file whose first ten lines contain "thailint: ignore-file[file-header.comment-antecedents]"
    And two comment blocks that would each produce a violation
    When the comment-antecedents rule runs
    Then no violation is reported

  Scenario: An unrelated rule id in the ignore does not suppress
    Given a comment block that would produce a violation
    And the block's first line ends with "# thailint: ignore[nesting]"
    When the comment-antecedents rule runs
    Then one violation is reported

  Scenario: A configured ignore pattern excludes a path
    Given the config ignores "vendor/**"
    And a file at "vendor/lib.py" with a comment that would produce a violation
    When the comment-antecedents rule runs
    Then no violation is reported
```

### Feature: File selection

```gherkin
Feature: File selection
  As the rule
  I need to self-gate on file suffix
  So that no change to EXTENSION_MAP is required

  Scenario Outline: Supported suffixes are analysed
    Given a <extension> file with a mid-file comment containing "used to be"
    When the comment-antecedents rule runs
    Then one violation is reported

    Examples:
      | extension |
      | .tf       |
      | .yaml     |
      | .yml      |
      | .hcl      |
      | .just     |

  Scenario: An unsupported suffix is skipped
    Given a ".md" file containing the text "used to be"
    When the comment-antecedents rule runs
    Then no violation is reported

  Scenario: Vendored paths are excluded by default configuration
    Given a file at "node_modules/pkg/index.js" with a comment containing "used to be"
    When the comment-antecedents rule runs with default configuration
    Then no violation is reported
```

### Feature: Strict mode (tier 2, opt-in)

```gherkin
Feature: Strict mode
  As a team willing to trade precision for recall
  I want an opt-in habitual-past detector
  So that I catch change-describing comments the default set misses

  Scenario: Strict mode is disabled by default
    Given a file with the mid-file comment "# This route used to refuse outright. It no longer does"
    When the comment-antecedents rule runs with default configuration
    Then no violation is reported

  Scenario: Strict mode flags habitual past with a nearby contrast word
    Given the config sets "file-header.comment_antecedents_strict" to true
    And a file with the mid-file comment "# This route used to refuse outright. It no longer does"
    When the comment-antecedents rule runs
    Then one violation is reported

  Scenario Outline: Strict mode does not flag the passive or purposive sense
    Given the config sets "file-header.comment_antecedents_strict" to true
    And a file with the mid-file comment "# <comment>"
    When the comment-antecedents rule runs
    Then no violation is reported

    Examples:
      | comment                                                           |
      | This callback is used to reload the user object, not the old one  |
      | Used to iterate over part of the tree instead of the whole        |
      | A structural comparison, used to spot edited fields, now buffered |
      | Can be used to overwrite the toolbar instead of replacing it      |

  Scenario: Strict mode requires the contrast word to be near the phrase
    Given the config sets "file-header.comment_antecedents_strict" to true
    And a comment block where "used to" and "instead" are more than 80 characters apart
    When the comment-antecedents rule runs
    Then no violation is reported
```

### Feature: Output formats

```gherkin
Feature: Output formats
  As a CI pipeline
  I need the inherited text, json, and SARIF output to carry the new rule
  So that the rule integrates with existing tooling

  Scenario: JSON output carries the new rule id
    Given a file producing one comment-antecedents violation
    When the CLI runs "file-header --format json"
    Then the output parses as JSON
    And a violation has rule_id "file-header.comment-antecedents"

  Scenario: SARIF output declares the new rule descriptor
    Given a file producing one comment-antecedents violation
    When the CLI runs "file-header --format sarif"
    Then the "version" field equals "2.1.0"
    And the run declares a rule descriptor whose id is "file-header.comment-antecedents"

  Scenario: A run with violations exits non-zero
    Given a file producing one comment-antecedents violation
    When the CLI runs "file-header"
    Then the exit code is non-zero
```

---

## PR1: BDD specification as failing tests

**Complexity**: Medium
**TDD phase**: RED only. This PR contains no implementation.

**Files**:
```
tests/unit/linters/file_header/test_comment_antecedents.py
tests/unit/linters/file_header/test_comment_antecedents_extraction.py
tests/unit/linters/file_header/test_comment_antecedents_suppression.py
tests/unit/linters/file_header/test_comment_antecedents_coexistence.py
tests/unit/linters/file_header/test_comment_antecedents_strict.py
```

**Steps**:
1. Transcribe every scenario above into one test function each, named after the scenario in snake_case.
2. Add fixtures for writing a temp file of a given suffix and returning violations, plus config overrides.
3. Run `poetry run pytest tests/unit/linters/file_header/ -k comment_antecedents`. Every new test must fail
   on the missing module or the missing rule id — not on a typo.
4. Commit the failing suite as the first commit.

**Acceptance criteria**:
- [ ] Every Gherkin scenario has exactly one corresponding test function
- [ ] Every new test fails, for the stated reason
- [ ] The existing `file_header` suite still passes untouched
- [ ] No file under `src/` is modified by this PR
- [ ] Test file headers follow `.ai/docs/FILE_HEADER_STANDARDS.md`

**Note for the implementing agent**: resist writing implementation here. The value of the red state is that
it proves the tests can fail; a test that has never failed has never been tested.

---

## PR2: Implementation, dogfooding, and documentation

**Complexity**: Medium
**Depends on**: PR1

**Files**:
```
src/linters/file_header/comment_block_extractor.py     (new)
src/linters/file_header/antecedent_detector.py         (new)
src/linters/file_header/comment_antecedent_rule.py     (new)
src/linters/file_header/config.py                      (modified — two fields)
src/linters/file_header/__init__.py                    (modified — export)
docs/file-header-linter.md                             (modified — new section)
.thailint.yaml                                         (modified — dogfood)
tests/smoke/test_comment_antecedents_corpora.py        (new)
```

**Patterns — tier 1, and only these**:

| Detector | Pattern | Measured precision |
|---|---|---|
| former-state | `\bused to be\b` | 100% (18/18) |
| pre-change-state | `\bbefore this \w+ (existed\|exists\|was\|were\|went live\|declared\|landed\|shipped)\b` or `\bbefore this (change\|commit\|PR\|diff)\b` | 100% (12/12) |

**Tier 2 — `comment_antecedents_strict`, default `false`**: `\bused to\b` present, **and** not preceded by
`is|are|was|were|be|been|being|not|also|only|can be|could be|to be`, **and** not clause-initial (block
start or after `.` `;` `:` `—` `(` `-`), **and** not comma-preceded, **and** a contrast word (`now`,
`no longer`, `instead`, `rather than`, `today`, `which meant`) within **80 characters**. Measured 86% on
the open-source corpus, 96% on qbench — below the 5% acceptance bar, hence opt-in.

**Config additions to `FileHeaderConfig`**:
```python
check_comment_antecedents: bool = True
comment_antecedents_strict: bool = False
```

**Steps**:
1. RED — confirm the PR1 suite fails.
2. GREEN, in this order so each step turns a named test module green:
   a. `comment_block_extractor.py` → extraction module passes.
   b. `antecedent_detector.py` + `comment_antecedent_rule.py` → detection, coexistence, and rejected-pattern
      modules pass. Rule id `file-header.comment-antecedents`. Self-gate on `file_path.suffix`. One
      violation per block. Reuse the package's parsers for the header boundary; do **not** re-derive it.
   c. `config.py` fields and ignore wiring → suppression and file-selection modules pass.
   d. Strict detector → strict module passes.
3. REFACTOR — A-grade complexity, 10.00/10 Pylint.
4. Write the corpus gate test. Pin the baselines below. Assert a deliberately wrong baseline once, watch it
   fail, then correct it — a gate that has never failed has not been verified.
5. Enable the rule in `.thailint.yaml` and run `just lint-full`. The measured thai-lint tier-1 count is
   **zero**, so no suppressions should be required. **If a violation appears, fix the comment; do not add a
   suppression without asking.**
6. Extend `docs/file-header-linter.md` with a section covering both tiers, configuration, suppression, the
   measured precision table, and the explicit out-of-scope statement.

**Baselines to pin**:

| Corpus | Blocks | Tier-1 hits | Precision |
|---|---|---|---|
| OSS `site-packages` | 165,952 | 58 | 100% |
| qbench | 23,978 | 23 | 100% |
| thai-lint | 2,422 | 0 | n/a |

The private corpora are not committed. The gate reads a corpus path from an environment variable and skips
when unset, so CI runs the thai-lint baseline and a developer can run the full set locally.

**Acceptance criteria**:
- [ ] Every PR1 test passes
- [ ] `test_comment_antecedents_coexistence.py` proves header and body prose never double-report
- [ ] The rejected-pattern scenarios pass, proving `replaces`, `this branch`, `previously`, and `formerly` stay silent
- [ ] All five suppression scopes pinned by passing tests
- [ ] SARIF output declares the new rule descriptor
- [ ] thai-lint self-lints clean with the rule enabled and zero added suppressions
- [ ] `just lint-full` exits 0 with Pylint at 10.00/10 and no Xenon errors
- [ ] `just test` exits 0

---

## Implementation Guidelines

### Code Standards

- File headers per `.ai/docs/FILE_HEADER_STANDARDS.md` on every new file, using atemporal language.
- Pylint exactly 10.00/10. Xenon A-grade on every block, not on average.
- No suppression comment (`# noqa`, `# type: ignore`, `# pylint: disable`, `# thailint: ignore`) without
  explicit user permission, asked per issue, per file, per phase.

### Testing Requirements

- One test function per Gherkin scenario, named after the scenario.
- Red before green, with the failing state committed first.
- No `xfail` or `skip` on a specified scenario. If a scenario turns out to be wrong, amend this document as
  part of the PR and say why.

### Documentation Standards

- Atemporal language in all headers: no "currently", "now", "new", "old", or dates.
- The measured precision table belongs in the user-facing doc, not only in the roadmap. Users deciding
  whether to enable strict mode need the number.

### Security Considerations

- The rule reads file contents only. No network, no subprocess, no writes.
- Corpus paths come from environment variables and are never committed.

### Performance Targets

- Lexical line scan, no AST and no tree-sitter. Target under 2 seconds for 40,000 comment blocks.
- The rule must not measurably slow `just lint-full` on this repository.

## Rollout Strategy

1. PR1 merges the specification — reviewable on its own as a statement of intent.
2. PR2 implements, dogfoods, and documents, with strict mode default-off.
3. The roadmap moves `planning/` → `in-progress/` at PR1 and → `complete/` at PR2.

**Release note requirement**: `check_comment_antecedents` defaults to `true`, so an existing user running
`file-header` gains body-comment checking on upgrade. The measured false positive rate is 0% across 192,352
comment blocks, but the behaviour change belongs in the CHANGELOG.

## Success Metrics

### Launch Metrics

- Tier-1 false positive rate of 0% reproduced on the open-source corpus gate.
- thai-lint self-lints clean with zero added suppressions.
- SARIF, JSON, and text output all carry the new rule id.

### Ongoing Metrics

- Any pattern addition is accompanied by an open-source corpus measurement in its PR description.
- A baseline movement in the corpus gate fails CI rather than passing silently.
