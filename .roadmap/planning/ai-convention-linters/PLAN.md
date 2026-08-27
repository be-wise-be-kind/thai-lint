# Planning Document: `restricted-calls` and `manual-discriminator` Linters

**Status**: planning (no implementation yet)
**Repo**: thai-lint (`~/Projects/thai-lint`) — public, project-agnostic; all project conventions arrive via YAML config, zero downstream-project names in source.

## 1. Context and evidence

A code review of AI-generated code in a downstream layered codebase (QBench) surfaced three conventions AI agents violate:

1. Manual string type-discrimination (`data_type` + `entity_id` columns, filtered by string) instead of the codebase's subclass-per-entity-type model pattern.
2. Raw `Model(...)` instantiation instead of service factory helpers (`create_entity_from_dict()`).
3. Saving lifecycle entities via `update_entity_from_dict()` directly instead of through their Action classes, skipping mandatory before/after hooks.

Viability was established empirically with throwaway AST analyzers run over QBench (~2,400 app files):

- **Finding 2** is cleanly detectable via import-resolution: 523 raw ORM instantiations measured; the sanctioned converter site accounts for 308; core entities outside sanctioned paths: ~6 genuine violations. FP source (non-class imports) measured at 12/535 calls, eliminated by class patterns.
- **Finding 3** is detectable only with **narrow receiver scoping**: a blanket "lifecycle methods only from actions/" rule would flag ~400 accepted calls (the convention is per-entity, not per-method); the narrow rule (explicit `TestService(`-style receivers) measured 8 legacy hits, 0 FPs. Known blind spot: dynamic receivers (`self._get_entity_service()`) — the shape of the actual reviewed violation — require type inference; partially mitigable via an explicit receiver-text rule (measured: 1 legacy hit).
- **Finding 1** is only partially lintable. A loose heuristic (any `*_type` string column without polymorphism) matched 28/609 models — ~27 false positives; pair-corroboration with any `*_id` still left ~8 FPs. **Tightened to exact name-sets** (`data_type`-style discriminator paired with `entity_id`-style non-FK column, no `polymorphic_on`): exactly 1 current hit (`ScheduledTask`) and it **would have fired on the real pre-fix defect**. The full "mirror the existing hierarchy precedent" convention is project knowledge no generic linter can have — that part belongs in the downstream project's AI-context docs.

**Plan**: two linters.

| Linter | Covers | Rule IDs |
|---|---|---|
| `restricted-calls` | findings 2 & 3 | `restricted-calls.instantiation`, `restricted-calls.method-call` |
| `manual-discriminator` | finding 1 (structural smell only) | `manual-discriminator.polymorphic-association` |

**Process**: BDD-first — the feature specs below are the contract; each scenario becomes one pytest test (the repo uses plain pytest; do not add pytest-bdd) named after the scenario, body structured Given/When/Then as arrange/act/assert. Then TDD in the build order of §4, then the smoke-test gates of §5.

---

## 2. Linter: `restricted-calls`

**Purpose**: enforce "code constructs matching pattern X may only appear in files matching paths Y" with a project-supplied remediation message. Two rule types (instantiation, method-call) share one engine, one config section, one CLI command.

### 2.1 Config schema

```yaml
restricted-calls:
  enabled: true
  rules:
    - name: entity-direct-instantiation        # required, unique per config
      type: instantiation                       # 'instantiation' | 'method-call'
      from_module: "models\\.models"            # regex, fullmatch on resolved import module
      class_pattern: "^(Test|Sample|Order)$"    # optional regex on class name; default "^[A-Z]"
      allowed_paths: ["database/**", "service/converter.py", "migrations/**", "tests/**"]
      message: "Create entities via the service factory, not raw constructors."
      ignore: []                                # optional per-rule glob exemptions (legacy adoption)

    - name: lifecycle-saves
      type: method-call
      method_pattern: "^(update_entity_from_dict|save_entity)$"   # regex on attribute name
      receiver_pattern: "^(Test|Sample|Order)Service\\("          # optional regex on receiver source text
      allowed_paths: ["actions/**"]
      message: "Lifecycle entities must be saved through their Action class."
```

- Exactly one of `allowed_paths` / `forbidden_paths` per rule (validated at load).
- Paths are globs (`**` supported) against the project-root-relative POSIX path; code patterns are regex, compiled at load.
- No severity key — thai-lint is ERROR-only by design (`src/core/types.py`).

### 2.2 Module design

```
src/linters/restricted_calls/
├── __init__.py            # exports rule class, config types, lint() convenience function
├── config.py              # RestrictedCallsConfig + RuleSpec dataclasses, from_dict, validation
├── path_matcher.py        # allowed/forbidden glob evaluation
├── import_tracker.py      # AST pass 1: name→(module, symbol), alias→module bindings
├── python_analyzer.py     # AST pass 2: candidate constructs (kind, module, name, receiver_text, line, col)
├── violation_builder.py
└── linter.py              # RestrictedCallsRule(MultiLanguageLintRule); _check_typescript → [] in v1
```

Structural templates: `src/linters/magic_numbers/` (AST coordinator, config loading, ignore handling), `src/linters/file_placement/` (path-pattern config). Performance: evaluate path scoping before parsing; if no rule applies to the file, skip `ast.parse` entirely.

### 2.3 BDD specification

#### Feature: Restricted instantiation detection

```gherkin
Feature: Restricted instantiation detection
  As a team with layered architecture conventions
  I want instantiation of designated classes restricted to designated layers
  So that entities are only created through sanctioned factory paths

  Background:
    Given a config with rule "no-raw-models":
      | type          | instantiation      |
      | from_module   | myapp\.models      |
      | allowed_paths | ["db/**"]          |
      | message       | Use the factory.   |

  Scenario: Direct-import instantiation outside allowed paths is flagged
    Given a file "service/foo.py" containing:
      """
      from myapp.models import Widget
      w = Widget(size=1)
      """
    When the linter checks the file
    Then exactly one violation with rule ID "restricted-calls.instantiation" is reported
    And the violation is on the line of "Widget(size=1)"
    And the violation message contains "no-raw-models" and "Use the factory."

  Scenario: Instantiation inside an allowed path is silent
    Given the file from the previous scenario located at "db/loader.py"
    When the linter checks the file
    Then no violations are reported

  Scenario: Aliased class import is resolved
    Given a file "service/foo.py" containing:
      """
      from myapp.models import Widget as W
      w = W(1)
      """
    When the linter checks the file
    Then exactly one "restricted-calls.instantiation" violation is reported

  Scenario: Module alias instantiation is resolved
    Given a file "service/foo.py" containing:
      """
      import myapp.models as m
      w = m.Widget(1)
      """
    When the linter checks the file
    Then exactly one "restricted-calls.instantiation" violation is reported

  Scenario: Fully-dotted module instantiation is resolved
    Given a file "service/foo.py" containing:
      """
      import myapp.models
      w = myapp.models.Widget(1)
      """
    When the linter checks the file
    Then exactly one "restricted-calls.instantiation" violation is reported

  Scenario: Same class name imported from an unrelated module is not flagged
    Given a file "service/foo.py" containing:
      """
      from other.place import Widget
      w = Widget(1)
      """
    When the linter checks the file
    Then no violations are reported

  Scenario: class_pattern limits which classes are restricted
    Given the rule additionally has class_pattern "^Widget$"
    And a file "service/foo.py" containing:
      """
      from myapp.models import Widget, Gadget
      a = Widget(1)
      b = Gadget(1)
      """
    When the linter checks the file
    Then exactly one violation is reported, on the "Widget(1)" line

  Scenario: Default class_pattern skips lowercase (function) imports
    Given the rule has no class_pattern configured
    And a file "service/foo.py" containing:
      """
      from myapp.models import build_widget
      w = build_widget(1)
      """
    When the linter checks the file
    Then no violations are reported

  Scenario: Multiple instantiations produce one violation each
    Given a file "service/foo.py" with three separate "Widget(...)" calls
    When the linter checks the file
    Then exactly three violations are reported, each at its own line

  Scenario: Instantiation inside a function body, comprehension, and class body are all detected
    Given a file "service/foo.py" containing:
      """
      from myapp.models import Widget
      def make(): return Widget(1)
      items = [Widget(i) for i in range(3)]
      class Holder:
          default = Widget(0)
      """
    When the linter checks the file
    Then exactly three violations are reported
```

#### Feature: Restricted method-call detection

```gherkin
Feature: Restricted method-call detection
  As a team whose lifecycle entities must be saved through an action layer
  I want calls to designated methods restricted to designated layers
  So that mandatory before/after hooks always run

  Background:
    Given a config with rule "lifecycle-saves":
      | type            | method-call                          |
      | method_pattern  | ^(update_entity_from_dict|save_entity)$ |
      | allowed_paths   | ["actions/**"]                       |
      | message         | Save through the Action class.       |

  Scenario: Restricted method called outside allowed paths is flagged
    Given a file "service/foo.py" containing:
      """
      FooService().save_entity(x)
      """
    When the linter checks the file
    Then exactly one violation with rule ID "restricted-calls.method-call" is reported
    And the message contains "lifecycle-saves" and "Save through the Action class."

  Scenario: Restricted method called inside the allowed path is silent
    Given the same call in a file "actions/foo_action.py"
    When the linter checks the file
    Then no violations are reported

  Scenario: Non-matching method names are silent
    Given a file "service/foo.py" containing "FooService().retrieve_entity_by_id(1)"
    When the linter checks the file
    Then no violations are reported

  Scenario: receiver_pattern constrains matches to designated receivers
    Given the rule additionally has receiver_pattern "^(Test|Sample)Service\("
    And a file "blueprints/views.py" containing:
      """
      TestService().update_entity_from_dict(d)
      PaymentTypeService().update_entity_from_dict(d)
      """
    When the linter checks the file
    Then exactly one violation is reported, on the "TestService()" line

  Scenario: Dynamic receiver text is matchable when the pattern targets it
    Given the rule has receiver_pattern "_get_entity_service\(\)"
    And a file "service/workflows.py" containing:
      """
      self._get_entity_service().update_entity_from_dict(update_dict)
      """
    When the linter checks the file
    Then exactly one "restricted-calls.method-call" violation is reported
    # This mirrors the real-world motivating violation; document the recipe.

  Scenario: Without receiver_pattern, any receiver matches
    Given the rule has no receiver_pattern
    And a file "service/foo.py" containing "anything.save_entity(x)"
    When the linter checks the file
    Then exactly one violation is reported

  Scenario: Bare attribute access without a call is not flagged
    Given a file "service/foo.py" containing:
      """
      f = FooService().save_entity
      """
    When the linter checks the file
    Then no violations are reported
    # Aliased-then-called is an accepted false negative; document it.

  Scenario: Chained receiver text is preserved for matching
    Given the rule has receiver_pattern "registry\.get\("
    And a file "service/foo.py" containing "registry.get('test').save_entity(x)"
    When the linter checks the file
    Then exactly one violation is reported
```

#### Feature: Path scoping and rule directionality

```gherkin
Feature: Path scoping and rule directionality

  Scenario: forbidden_paths mode flags only inside listed paths
    Given a rule with type "method-call", method_pattern "^commit$",
      forbidden_paths ["api/routes/**"] and no allowed_paths
    And the call "db.session.commit()" in "api/routes/users.py" and in "service/foo.py"
    When the linter checks both files
    Then a violation is reported for "api/routes/users.py" only

  Scenario: A rule with both allowed_paths and forbidden_paths is rejected at config load
    When the config is loaded
    Then a configuration error names the rule and states the two keys are mutually exclusive

  Scenario: A rule with neither allowed_paths nor forbidden_paths is rejected at config load

  Scenario: Recursive glob matches nested directories
    Given a rule with allowed_paths ["db/**"]
    And a restricted instantiation in "db/sub/deep/loader.py"
    When the linter checks the file
    Then no violations are reported

  Scenario: Single-file allowed path matches exactly that file
    Given a rule with allowed_paths ["service/converter.py"]
    And restricted instantiations in "service/converter.py" and "service/other.py"
    When the linter checks both files
    Then a violation is reported for "service/other.py" only

  Scenario: Per-rule ignore globs exempt legacy paths
    Given a rule with allowed_paths ["db/**"] and ignore ["legacy/**"]
    And a restricted instantiation in "legacy/old_loader.py"
    When the linter checks the file
    Then no violations are reported

  Scenario: Paths are matched relative to the project root, not absolute
    Given the project root is a temporary directory
    And a restricted instantiation in "<root>/service/foo.py"
    When the linter checks the file with allowed_paths ["service/**"] on another rule's pattern
    Then path comparison uses "service/foo.py"
```

#### Feature: Configuration loading

```gherkin
Feature: Configuration loading

  Scenario: Rules load from the "restricted-calls" key
  Scenario: Rules load from the "restricted_calls" key (underscore alias)
  Scenario: Disabled linter reports nothing and does not parse files
  Scenario: Missing or empty rules list reports nothing
  Scenario: Invalid regex is rejected at load, naming the rule and the offending field
    Given a rule with from_module "models\.(("
    When the config is loaded
    Then a configuration error identifies rule "…" field "from_module"
  Scenario: Unknown rule type is rejected at load
    Given a rule with type "decorator"
    Then a configuration error lists the supported types
  Scenario: Duplicate rule names are rejected at load
  Scenario: instantiation rule missing from_module is rejected; method-call rule missing method_pattern is rejected
```

#### Feature: Ignore directives (5-level suppression)

```gherkin
Feature: Ignore directives

  Scenario: Line-level ignore with matching sub-rule ID suppresses the violation
    Given a flagged line ending with "# thailint: ignore[restricted-calls.instantiation]"
    Then no violation is reported for that line

  Scenario: Line-level ignore with the umbrella ID suppresses both sub-rules
    Given a flagged line ending with "# thailint: ignore[restricted-calls]"
    Then no violation is reported

  Scenario: Line-level ignore with a different rule ID does not suppress
    Given a flagged line ending with "# thailint: ignore[magic-numbers]"
    Then the violation is still reported

  Scenario: File-level ignore in the header suppresses all violations in the file
    Given "# thailint: ignore-file[restricted-calls]" within the first lines of the file
    Then no violations are reported for the file
```

#### Feature: Outputs, CLI, and library API

```gherkin
Feature: Outputs, CLI, and library API

  Scenario: CLI exits 0 on a clean tree, non-zero when violations exist
  Scenario: Text output includes file path, line, rule ID, rule name, and message
  Scenario: JSON output is machine-parseable and contains the same fields
  Scenario: SARIF output validates against SARIF v2.1.0 expectations in .ai/docs/SARIF_STANDARDS.md
    # ruleId = "restricted-calls.instantiation" / ".method-call"; physicalLocation with line
  Scenario: Library API restricted_calls.lint(path, config=...) returns Violation objects
    # mirrors the file_header.lint() convenience-function precedent
  Scenario: Violations from both sub-rules in one file are all reported in one run
```

#### Feature: Robustness

```gherkin
Feature: Robustness

  Scenario: A file with a syntax error produces no violations and no crash
  Scenario: An empty file produces no violations
  Scenario: Imports declared inside function bodies are tracked
  Scenario: Non-Python files are not analyzed in v1
  Scenario: Unicode identifiers and string contents do not break analysis
  Scenario: A file in allowed paths for every rule is never parsed (performance contract)
    # assert via monkeypatched ast.parse call counter
```

### 2.4 Documented precision limits (must appear in `docs/restricted-calls-linter.md`)

- No type inference. Method-call matching = attribute name + receiver source text. Dynamic receivers are caught only when `receiver_pattern` is written for the dynamic text (include the `_get_entity_service` recipe — it matches the real reviewed violation).
- Accepted false negatives: re-exported imports, `getattr`/registry dispatch, `type(x)(...)`, bound-method aliasing.
- Instantiation false positives (functions imported from a restricted module): measured 12/535 in the reference codebase; mitigated by `class_pattern`.

---

## 3. Linter: `manual-discriminator`

**Purpose**: opt-in tripwire for the **polymorphic-association signature** in SQLAlchemy models — a string type-discriminator column paired with a generic non-FK id column on a class lacking `polymorphic_on` — the structural form of "manually discriminated types that should be subclass-per-type."

**Calibration warning (empirical, do not loosen defaults)**: loose `*_type` matching = ~27/28 FP on a 609-model codebase; pair-with-any-`*_id` = ~8/9 FP; the exact name-set defaults below = 1 hit / ~0 FP while still catching the real pre-fix defect.

### 3.1 Config schema

```yaml
manual-discriminator:
  enabled: true
  discriminator_names: ["data_type", "entity_type", "object_type", "target_type", "record_type"]
  generic_id_names: ["entity_id", "object_id", "target_id", "record_id"]
  allowed_models: []      # class names exempted (accepted designs)
  ignore: []              # path globs
```

Fires only when ALL hold: class defines `__tablename__` (ORM model); has a String/Text/Enum column whose name is in `discriminator_names`; has an Integer-or-any non-`ForeignKey` column whose name is in `generic_id_names`; lacks `polymorphic_on` in `__mapper_args__`; not in `allowed_models`. Exact name match, not patterns — that is the calibration.

### 3.2 Module design

`src/linters/manual_discriminator/{__init__,config,python_analyzer,violation_builder,linter}.py`, mirroring `stringly_typed` structure; single-file analysis in v1 (no cross-file storage); `_check_typescript` → `[]`. SQLAlchemy-aware but framework-generic across projects (precedent: `blocking_async` is asyncio-aware). Confirm non-overlap with `stringly_typed` (which prescribes enums — the wrong remediation for this pattern).

### 3.3 BDD specification

```gherkin
Feature: Polymorphic-association detection
  As a team using subclass-per-type model conventions
  I want models that manually discriminate types via string+id column pairs flagged
  So that new models follow framework polymorphism or per-type subclassing

  Scenario: Discriminator + generic id without polymorphism is flagged
    Given a file "models.py" containing:
      """
      class PendingThing(Base):
          __tablename__ = 'pending_thing'
          id = Column(Integer, primary_key=True)
          data_type = Column('data_type_discriminator', String(45), nullable=False)
          entity_id = Column('entity_id', Integer, nullable=False)
      """
    When the linter checks the file
    Then exactly one violation "manual-discriminator.polymorphic-association" is reported on the class line
    And the message names both columns and suggests polymorphic_on / subclass-per-type
    # This reconstructs the real pre-fix defect; keep as a permanent regression fixture.

  Scenario: The same model with polymorphic mapper args is silent
    Given the class additionally contains:
      """
      __mapper_args__ = {'polymorphic_on': data_type, 'polymorphic_identity': 'base'}
      """
    When the linter checks the file
    Then no violations are reported
    # Reconstructs the post-fix state; sanctioned framework polymorphism is the remedy, not a smell.

  Scenario: Discriminator column alone is silent
    Given a model with data_type = Column(String(45)) and no generic id column
    Then no violations are reported

  Scenario: Generic id column alone is silent
    Given a model with entity_id = Column(Integer) and no discriminator column
    Then no violations are reported

  Scenario: A generic-id-named column WITH ForeignKey is silent
    Given a model with data_type = Column(String) and
      entity_id = Column(Integer, ForeignKey('entities.id'))
    Then no violations are reported

  Scenario: A non-string discriminator-named column is silent
    Given a model with data_type = Column(Integer) and entity_id = Column(Integer)
    Then no violations are reported

  Scenario: A class without __tablename__ is silent
    Given a plain class with data_type and entity_id attribute assignments
    Then no violations are reported

  Scenario: SQLAlchemy 2.0 mapped_column and Mapped annotations are recognized
    Given a file containing:
      """
      class PendingThing(Base):
          __tablename__ = 'pending_thing'
          data_type: Mapped[str] = mapped_column(String(45))
          entity_id: Mapped[int] = mapped_column(Integer)
      """
    When the linter checks the file
    Then exactly one violation is reported

  Scenario: Names outside the configured sets are silent
    Given a model with sample_type = Column(String) and lab_id = Column(Integer)
    Then no violations are reported
    # The empirically measured FP class (e.g. Sample.sample_type + lab_id); the exact-name
    # calibration exists to keep this silent.

  Scenario: Custom name sets from config are honored
    Given config discriminator_names ["row_kind"] and generic_id_names ["subject_id"]
    And a model with row_kind = Column(String) and subject_id = Column(Integer)
    Then exactly one violation is reported

  Scenario: A model listed in allowed_models is silent
    Given config allowed_models ["ScheduledTask"]
    And a matching model class named ScheduledTask
    Then no violations are reported

  Scenario: Path globs in ignore exempt files
  Scenario: Inline ignore "# thailint: ignore[manual-discriminator]" on the class line suppresses
  Scenario: File-level ignore-file directive suppresses
  Scenario: Multiple offending models in one file produce one violation each
  Scenario: Syntax-error and empty files produce no violations and no crash
  Scenario: Text, JSON, and SARIF outputs carry the rule ID and class location
  Scenario: Library API manual_discriminator.lint(path, config=...) returns violations
```

### 3.4 Documentation requirements

`docs/manual-discriminator-linter.md` must state plainly: this rule is an opt-in tripwire for one specific architectural mistake; it cannot verify project-specific mirrored-hierarchy conventions ("every Foo subclass needs a FooDataService") — that knowledge belongs in the downstream project's AI-context docs (see §6).

---

## 4. Implementation sequencing (TDD, after the BDD specs are committed)

Read first (AGENTS.md mandate): `.ai/index.yaml`, `.ai/howtos/how-to-add-linter.md`, `.ai/howtos/how-to-roadmap.md`, `.ai/docs/FILE_HEADER_STANDARDS.md`, `.ai/docs/SARIF_STANDARDS.md`. Quality gates per commit: `just lint-full` exit 0, Pylint 10.00/10, Xenon all-A, `just test` exit 0.

Roadmap: create `.roadmap/planning/restricted-calls-linter/` (PROGRESS_TRACKER.md, PR_BREAKDOWN.md, AI_CONTEXT.md) from `.ai/templates/roadmap-*.md.template`.

**PR1 — `restricted-calls` core.** Convert §2.3 features Config/PathScoping/Instantiation/MethodCall/Ignores/Robustness to failing pytest tests in `tests/unit/linters/restricted_calls/` (~45 tests), then implement in this order: `config.py` → `path_matcher.py` → `import_tracker.py` → `python_analyzer.py` → `linter.py`. Include the lifecycle-bypass regression fixture (§5.1).

**PR2 — `restricted-calls` integration.** Outputs/CLI/LibraryAPI feature → tests (~20); CLI command via `create_linter_command` in `src/cli/linters/structure.py` + import in `src/cli/linters/__init__.py`; exports in `src/__init__.py`; config-template section in `src/templates/thailint_config_template.yaml`; `docs/restricted-calls-linter.md` (incl. §2.4 limits + legacy-adoption playbook: inventory via `--format json` → per-rule `ignore:` globs → burn down; inline ignores kept honest by the existing `lazy-ignores` linter); README entry.

**PR3 — `restricted-calls` real-codebase validation.** Execute §5.2 against QBench; record results in the PR; dogfood (§5.4).

**PR4 — `manual-discriminator` (full vertical, small surface).** §3.3 spec → tests (incl. §5.1 model fixtures) → `config.py` → `python_analyzer.py` → `linter.py` → CLI in `src/cli/linters/code_smells.py` → template/docs/exports → §5.2 QBench expectation + §5.3 OSS FP audit recorded in the PR.

**Explicit non-goals (record in roadmap):** TypeScript support for restricted-calls (config schema already accommodates it; analyzer work only); cross-file filter-usage corroboration for manual-discriminator; any baseline-file mechanism (the existing 5-level ignore system suffices).

---

## 5. Smoke-test plan on actual codebases (release gates)

### 5.1 Regression fixtures from the real defects (in-repo, permanent tests)

- **Pre-fix model fixture** (manual-discriminator MUST fire) and post-fix variant with `polymorphic_on` (MUST be silent) — already specified as the first two scenarios of §3.3.
- **Lifecycle-bypass fixture** (restricted-calls MUST fire): service-layer file ending a method with `self._get_entity_service().update_entity_from_dict(update_dict)`, checked with `method_pattern: "^update_entity_from_dict$"`, `receiver_pattern: "_get_entity_service"`, `allowed_paths: ["actions/**"]` — specified as the "Dynamic receiver" scenario of §2.3.

### 5.2 QBench validation run (manual, read-only, `~/Projects/qbench` @ qbench-dev)

Run the built linters with the configs below; compare to these measured baselines (counts from the planning-phase analysis — small drift from ongoing development is fine; order-of-magnitude drift indicates a detection bug):

| Rule config | Expected result |
|---|---|
| instantiation: `from_module "models\\.models"`, class_pattern `^(Test|Sample|Order|Batch|Invoice|Worksheet|Assay|Panel|Source|Location)$`, allowed: `service/converter.py`, `database/**`, `migration/**`, `tests/**`, `test/**` | **~6 hits**, incl. `service/serv_invoice_items.py:1132,1154` (Test), `listeners/test_listeners.py:816,855` (Order) |
| same with class_pattern `^[A-Z]` | **~215 hits / ~75 files**; `service/converter.py` (308 instantiations) fully exempt |
| method-call: `^(update_entity_from_dict|create_entity_from_dict|save_entity|save_entities|update_entities_from_dict_list|create_entities_from_dict_list)$`, receiver `^(Test|Sample|Order|Batch|Invoice|Worksheet|Location)Service\\(`, allowed `actions/**` | **8 hits**: `blueprints/batches.py:1417`; `service/serv_customer_portal.py:44,50`; `listeners/sample_listeners.py:799,995,1002`; `listeners/order_listeners.py:981`; `listeners/test_listeners.py:1946` |
| method-call companion: receiver `_get_entity_service\\(\\)|_get_service\\(\\)`, allowed `actions/**` | **1 hit**: `service/serv_automations_import.py:53` |
| manual-discriminator, default config | **exactly 1 hit**: `ScheduledTask` in `models/models.py` (`data_type` + `entity_id`). More hits = FP regression; investigate before release |

Also verify: acceptable runtime over ~2,400 app files (path prefilter working), and valid `--format json` / `--format sarif` on the full run.

### 5.3 False-positive audit on an unrelated OSS codebase

Run `manual-discriminator` with defaults against a large SQLAlchemy-based OSS project (Apache Airflow or Redash). Expected zero-to-few hits; manually adjudicate each (genuine pattern vs FP → tighten defaults). Record the audit in the PR description.

### 5.4 Dogfood

Run both linters over thai-lint itself with a sample config (e.g., restrict instantiation of classes from `src.core.types` to `src/**`): expect clean, crash-free runs in all three output formats.

---

## 6. Follow-up outside thai-lint (hand to the downstream project)

1. Adopt both rules in QBench's `.thailint.yaml` (configs of §5.2); triage the ~15 measured legacy hits (fix or justified inline ignore).
2. Add the subclass-per-entity-type convention exemplar (`ObjectHistory` → `TestHistory`/... with mirrored data services) to QBench's AI-context docs — the portion of finding 1 no generic linter can enforce.
