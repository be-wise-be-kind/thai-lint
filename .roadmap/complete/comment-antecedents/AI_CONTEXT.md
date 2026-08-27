# Comment Antecedents Linter - AI Context

**Purpose**: Architectural context and measured evidence for the `comment-antecedents` linter

**Scope**: Detection of mid-file code comments whose referent is the change that produced the code rather than the code itself, across hash-comment and slash-comment languages

**Overview**: Establishes why the `comment-antecedents` rule exists, what it detects, and — most importantly —
    which candidate detection patterns survived empirical validation and which were rejected. Every pattern in
    the shipping set carries a measured precision figure from three independent corpora totalling 188,450
    mid-file comment blocks. Two patterns that scored well on a single private codebase collapsed under
    open-source validation and are documented here as rejected, so that a later contributor does not
    re-propose them. Also records the framework findings that make this rule cheap to build: no extension-map
    change is required, the ignore engine is already generic, and the header-scoped `file-header` rule cannot
    double-report.

**Dependencies**: `src/linters/file_header/` (host package, header-boundary parsers, CLI namespace), `src/orchestrator/core.py` (file walk and rule routing), `src/linter_config/ignore.py` (suppression engine), `src/core/types.py` (severity model)

**Exports**: Detection rationale, measured precision baselines, rejected-pattern record, architectural findings, risk register

**Related**: PR_BREAKDOWN.md for implementation tasks, PROGRESS_TRACKER.md for status, GitHub issue #253 for the originating proposal

**Implementation**: Lexical comment-block scan with grammar gating and phrase pairing, validated against private and open-source corpora before any code is written

---

## Overview

A comment that describes the change instead of the code leaves the reader holding a sentence that cannot
resolve. Whoever opens the merged file has no diff, so a phrase like "the two-dot form" or "this PR" points
at something that is not in the tree.

```hcl
# THREE dots, not two. The two-dot form compared the wrong pair of commits.
```

```python
# This PR drops the retry wrapper; dedup is a future hardening pass, not this PR's scope.
```

The reader is left with a constraint they cannot evaluate, which is worse than no comment, because they
will not delete something that sounds load-bearing.

This rule detects the phrase-matchable half of that class. It does not attempt the semantic half.

## Project Background

Issue #253 proposed the rule with a candidate pattern set of roughly fourteen phrases. Before writing the
roadmap, every proposed phrase was measured against real code. Most of them do not survive. The value of
this document is the record of which ones did.

## What Is Explicitly Out Of Scope

A comment can carry the same defect with no matchable phrase at all, by stating the defect the change
removed in the present tense as the reason the code exists:

```yaml
# `resolve` is gated to a push, so on a dispatch the step that links the plan
# never runs at all and the approver sees the target's name and nothing else.
```

Every term there resolves. Nothing dangles. The sentence is simply false, and the job beneath it is what
makes it false. Detecting that requires the diff and a semantic judgement about the code. A file-at-a-time
linter cannot have that and must not pretend to. That half stays with a human or model reviewer.

## Measured Evidence

### Corpora

| Corpus | Files | Mid-file comment blocks | Character |
|---|---|---|---|
| OSS `site-packages` | 25,525 | 162,542 | Real open-source libraries (numpy, pandas, scipy, mypy, sqlalchemy, requests, matplotlib, pygments, …) |
| qbench | 8,962 | 23,555 | Private application code, mixed legacy and AI-assisted |
| thai-lint | 594 | 2,353 | This repository |
| **Total** | **35,081** | **188,450** | |

Generated and minified trees were excluded (`.min.js`, `.terragrunt-cache`, vendored asset bundles,
`pip`'s own vendored tree). Bundled third-party libraries inside the private corpus were left in, so the
counts reflect what an unconfigured run reports rather than a curated best case.

268 comment blocks were hand-labelled to produce the precision figures below.

### Criterion 2 evidence: the defect tracks AI authorship

Strict-set hit density by codebase area, per 1,000 comment blocks:

| Area | Blocks | Hits | Per 1k |
|---|---|---|---|
| qleap (AI-assisted frontend) | 4,952 | 25 | **5.05** |
| qbench tests | 4,488 | 13 | 2.90 |
| qbench app (legacy) | 7,155 | 9 | 1.26 |
| qbench static JS (hand-written, pre-AI) | 3,475 | 0 | **0.00** |

Four times denser in AI-written code than in legacy, and zero in the hand-written JavaScript that predates
the tooling. The gradient, not the absolute count, is the argument for the rule.

### Criterion 3 evidence: the shipping set

Tier 1 is the default-on set. Measured across all three corpora:

| Corpus | Tier-1 hits | True | False | Precision |
|---|---|---|---|---|
| OSS `site-packages` | 57 | 57 | 0 | 100% |
| qbench | 19 | 19 | 0 | 100% |
| thai-lint | 0 | — | — | — |
| **Total** | **76** | **76** | **0** | **100%** |

False positive rate 0%, against an acceptance bar of 5%.

The counts are pinned by `tests/smoke/test_comment_antecedents_corpora.py` as a **ceiling**, not an
equality. Only the thai-lint baseline runs in CI; the external gates read a corpus path from an
environment variable and skip when it is unset, so they catch drift for a developer running them locally
rather than for every push.

The ceiling form was not the first design, and the reason it changed is worth recording. The gate was
originally an exact-equality assertion, and it broke within a day: qbench landed 55 commits, one of which
deleted a comment the baseline counted, taking it from 19 to 18. An equality assertion reads that as
identical to the rule widening, which is the only thing the gate exists to catch. A ceiling separates
them — deleting a comment cannot trip it, adding a pattern still does. Verified by red-flip: swapping
`used to be` for the rejected `previously` takes qbench to 40 and the open-source corpus to 223, and the
gate fails on both. A second assertion caps firing density at 1.5 hits per 1,000 blocks, so a widened rule
cannot hide behind a corpus that shrank.

One false positive was found during implementation and eliminated rather than tolerated. In
`joblib/numpy_pickle.py`, "16 bytes are used to be sure to cover all the possible dtypes' alignments" reads
as "used in order to be", not as habitual past. Applying the passive-voice gate — already present in the
strict tier — to the default tier removes it at no cost to recall. A clause-initial gate was measured for
the same purpose and rejected: it would discard genuine findings that open a comment, such as "Used to be
mask, now it's recordmask".

## Key Decisions Made

### Decision 1: One tier, default-on, and no opt-in second tier

`used to be` and `before this <noun> existed` measure 100% precision on 188,450 blocks. They ship enabled.

A second tier detecting the bare habitual past was built and shipped disabled, then removed. The reasoning
for removing it is worth keeping, because the same idea will look attractive again. thai-lint has no
warning severity — `src/core/types.py:28` defines `Severity.ERROR` alone — so an 82%-precision tier could
only ship as a config flag. Documenting that flag honestly meant writing "this reports a wrong answer
roughly one time in five", which is advice not to enable it. A flag nobody should turn on is code and
documentation with no reader. If the precision problem is ever solved, the tier can come back; the
measurement above is what it has to beat.

### Decision 2: Report per comment block, not per line

All measured figures are block-level, where a block is a run of contiguous comment lines. Line-level
reporting inflates the same findings by roughly 60% and fires repeatedly inside a single prose paragraph.
Block-level is a correctness requirement, not a preference.

### Decision 3: Patterns rejected, with measurements

These were proposed and must not be reintroduced without new evidence.

| Pattern | Best measured precision | Why rejected |
|---|---|---|
| `replaces?` | 21% (qbench), 24% (sampled) | Dominated by runtime referents ("ECS never replaces the task") and code tokens (`.replace(`, `errors="replace"`). Its best variant, 83%, only works because one private repo has a house comment convention. Generalises to nothing. |
| `this <change>` incl. `branch`, `patch` | 29% (OSS) vs 91% (qbench) | Overfit. `this branch` overwhelmingly means an `if`/`else` branch and `this patch` an HTTP PATCH or monkeypatch. Scored 91% on one codebase and collapsed on open source. |
| `previously` | 46% (OSS) vs 70–100% (qbench) | Overfit. Open-source code uses `We previously <verb>` as runtime narrative inside exception handlers (plotly and psutil supply seven such false positives). Lexically indistinguishable from the true case. |
| `formerly` | Untestable | Zero first-party occurrences across 205,900 blocks. Its only hits were four vendored copies of `requests`. Dead weight. |
| `the old one` | 0% | Always a runtime referent ("stand up the new cert before the old one leaves"). |
| `not two`, `REVERSED` | 0% | Prose coincidence. |
| `before this` (unpaired) | 41% | Runtime ordering ("before this hook runs"). Requires the existence-verb pairing to be usable. |
| Bare habitual past — `used to` with a contrast word within 80 characters | **82%** OSS, 89% qbench | Built, measured, and then removed rather than shipped disabled. 18% false positives on an ERROR-only linter, all of them the purposive sense the grammar gates narrow but cannot close: "colons are more frequently used to separate field names from their types". Documenting it honestly amounted to telling users not to enable it, which makes a config flag dead weight. Adds 17 hits on the open-source corpus and 9 on qbench beyond the shipped set — the recall is real, the precision is not good enough to act on. |
| `add`, `remove`, `strip`, `drop` (imperative) | Rejected on volume | `add` fires 2,444 times in one open-source dependency tree, `remove` 1,282. Tier 1 fires 12 times in the same corpus. Imperative prose: "add the line to the output", "TODO add cookie handling". |
| `adds`, `removes`, `strips`, `drops` (third person) | **0%** | Twenty times rarer than the imperative form (120 vs 2,444 for `adds`), which makes the split worth knowing, but every form measures at zero. Clause-initial `Adds …` is **0/20** across both corpora; plain `adds` with a subject is 0/16 sampled. |
| `this\|we` + `removes\|strips\|adds\|drops` | **5% OSS** vs 75% private | Overfit, and the worst of the family. Of 39 open-source hits, 37 are runtime: `this adds retry and timeout information` describes what the wrapper does, `We added this symbol on previous iteration` describes an algorithm's own loop. |

The `this <change>`, `previously`, and change-verb results are the most important entries in this table.
All three looked shippable after validation on a single codebase — 91%, 70–100%, and 75% respectively —
and all three collapsed on open source, to 29%, 46%, and 5%. **Any future pattern addition must be
validated on at least one open-source corpus before it ships.**

### The selection principle behind the table

Read down the two lists and one distinction separates them completely.

**Every rejected phrase names something code can do at run time.** `replaces`, `removes`, `strips`, `adds`,
`drops` are transitive verbs a program executes; `previously` and `before this` are adverbials that modify
runtime actions as readily as authorship. So the dominant sense in a code comment is the runtime one, and
the diff-deictic sense is the rare exception competing against it.

**Neither surviving phrase can describe a runtime action.** `used to be` is a past-tense copula — code
cannot "used to be" anything while executing. `before this <noun> existed` anchors to the existence of a
construct rather than to the order of operations. Both are statements only an author can make about the
history of the file.

This predicts the measurements retroactively and is the cheapest available filter: **if a candidate phrase
could plausibly complete the sentence "at run time, this code ___", expect it to fail.** The principle does
not replace measurement for plausible candidates, but it does explain why the obvious change verbs are not
worth measuring twice.

**A corollary worth stating, because it inverts an intuition.** Splitting a change verb into its imperative
and third-person forms looks promising — `adds` is twenty times rarer than `add` — and for `replaces` the
clause-initial third-person form did reach 83%. It does not generalise. Clause-initial third person is the
docstring summary convention: "Removes dots from the name", "Strips comments from a line", "Adds methods
which do not depend on cls" are how a Python docstring's first line is written. So for a verb code can
perform, that form is the **most** runtime-bound reading available, not the rarest. Measured 0 true of 20
across both corpora. The `replaces` result was not the same construction — it came from one private
repository's house convention of naming a superseded code location by path and line, which nothing else
shares.

### Decision 4: A second rule inside `file_header`, sharing the package but not the detector

Issue #253 left the packaging open. The rule lands in `src/linters/file_header/` as a second rule with its
own rule id, `file-header.comment-antecedents`.

The reasoning is the issue's own observation. `AtemporalDetector`'s `STATE_CHANGE` category —
`replaces?`, `migrated from`, `formerly`, `old implementation`, `new implementation` — holds antecedent
patterns, not temporal ones. The prose-scanning concern already lives in this package; it is merely aimed
at the extracted header instead of the body. This rule points the same concern at the rest of the file.

What that buys, verified against the codebase:

- **No CLI work.** `_run_file_header_lint` (`src/cli/linters/documentation.py`) filters on
  `"file-header" in v.rule_id`, so a rule under that namespace inherits the command, `--format
  text|json|sarif`, `--recursive`, `--parallel`, and config loading with no new registration.
- **The header boundary is already solved.** `bash_parser.py` holds hash-comment extraction and every
  parser knows where its header ends — the one thing a body scan must not re-derive.
- **Multi-rule packages are established.** `print_statements/` carries `improper-logging.print-statement`
  and `improper-logging.conditional-verbose`; `performance/` carries two rules across two files.

**The detector is not shared.** `AtemporalDetector` keeps its patterns; the new detector is a separate
module. Three of the five `STATE_CHANGE` patterns are rejected here on measured grounds, and header prose
and body prose have different false-positive profiles, so the two sets must be free to diverge.

**A separate rule id, not a widened `enforce_atemporal`.** Widening `enforce_atemporal` would change what
an established, default-on setting means for existing users. A distinct rule id keeps the body scan
independently suppressible, independently configurable, and independently reportable in SARIF.

## Architectural Findings

These were probed against the codebase, not assumed. They reduce the build considerably.

### No `EXTENSION_MAP` change is required

Issue #253 states that `.yaml`, `.tf`, `.hcl`, and `.just` must be added to `EXTENSION_MAP`
(`src/orchestrator/language_detector.py:31`) because they resolve to `unknown`. They do resolve to
`unknown` — but that does not gate anything:

- `_collect_files_from_walk` (`src/orchestrator/core.py:133`) collects every file whose suffix is not one
  of nine binary types. `.tf`, `.yaml`, `.hcl`, and `.just` are all walked.
- `_get_rules_for_file` (`src/orchestrator/core.py:530`) returns `self.registry.list_all()` with no
  language filter. Every rule sees every file.

Existing rules self-gate by looking up a parser or analyzer by language and returning early. This rule
self-gates on `file_path.suffix` instead. **Changing `EXTENSION_MAP` would alter what every other
registered rule sees and must not be done for this feature.**

### The host rule is header-scoped, so the two cannot double-report

`_check_atemporal_violations` (`src/linters/file_header/linter.py:243`) is passed the extracted header
block only. Verified: a Python file whose mid-file comment reads
`# This PR replaces the old implementation; formerly it will be handled currently.` produces zero
violations from `file-header`. Further, `.tf`/`.yaml`/`.hcl` have no registered header parser at all, and
Python headers are docstrings rather than `#` comments, so a hash-comment scan never touches them. Only
`.sh`/`.bash` genuinely overlaps, and skipping the leading contiguous comment block resolves it.

### The ignore engine is already generic

`src/linter_config/ignore.py` supports repository, directory, file, block, and line scopes and is not
language-specific. No new suppression mechanism is needed. The ergonomic wrinkle is real though:
suppressing a comment means writing a comment next to it.

## Technical Constraints

- **Severity is ERROR-only.** `src/core/types.py:28`. Issue #253 asks for warning severity; it does not exist.
- **Quality gates.** `just lint-full` exit 0, Pylint exactly 10.00/10, Xenon A-grade on every block, zero test failures.
- **Three output formats mandatory.** text, json, and SARIF v2.1.0 per `.ai/docs/SARIF_STANDARDS.md`.

## Risk Mitigation

| Risk | Mitigation |
|---|---|
| Suppression path proves unreliable, making a chatty rule unusable | The suppression path is pinned by tests in PR1 **before** any pattern ships. Issue #253 reports a `dry` suppression that stopped being honoured once its file joined an indexed duplicate group; block-scope and line-scope suppression for this rule get explicit regression tests. |
| Pattern set grows and precision silently degrades | Smoke-test gates in PR2 pin the measured baselines per corpus. A pattern addition that moves a baseline fails the gate. |
| Vendored code produces noise | Default ignore patterns ship with the rule. Measured need: qbench alone bundles four copies of `requests` under non-obvious paths. |
| String literals containing `#` are misread as comments | Accepted for hash-comment languages. A string literal that also contains `used to be` is vanishingly rare; the alternative is per-language parsing, which defeats the point of a lexical scan. Documented, with a test asserting the known limitation. |

## Future Enhancements

- Tier-2 promotion, if a proximity or grammar refinement gets it under 5% on an open-source corpus.
- Additional comment syntaxes (`--` for SQL and Lua, `%` for LaTeX) once the hash and slash families are proven.
