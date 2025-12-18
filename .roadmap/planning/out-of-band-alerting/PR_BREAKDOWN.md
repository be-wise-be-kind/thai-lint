# Out-of-Band Alerting System - PR Breakdown

**Purpose**: Detailed implementation breakdown of out-of-band alerting into manageable, atomic pull requests

**Scope**: Complete feature implementation from alerting infrastructure through hook integrity linter

**Overview**: Comprehensive breakdown of the out-of-band alerting feature into 8 manageable, atomic
    pull requests. Each PR is designed to be self-contained, testable, and maintains application functionality
    while incrementally building toward the complete feature. Includes detailed implementation steps, file
    structures, testing requirements, and success criteria for each PR.

**Dependencies**: plyer (desktop notifications), requests (Slack webhook), PyYAML

**Exports**: PR implementation plans, file structures, testing strategies, and success criteria for each development phase

**Related**: AI_CONTEXT.md for feature overview, PROGRESS_TRACKER.md for status tracking

**Implementation**: Atomic PR approach with detailed step-by-step implementation guidance and comprehensive testing validation

---

## Overview
This document breaks down the out-of-band alerting feature into manageable, atomic PRs. Each PR is designed to be:
- Self-contained and testable
- Maintains a working application
- Incrementally builds toward the complete feature
- Revertible if needed

---

## Phase 1: Alerting Infrastructure

### PR1: Core Alerting Types and Interfaces

**Scope**: Create foundational types, protocols, and dispatcher for the alerting system

**Files to Create**:
```
src/alerting/
├── __init__.py
├── types.py          # AlertConfig, AlertRule dataclasses
├── base.py           # AlertChannel protocol
└── dispatcher.py     # Routes violations to channels
```

**Files to Modify**:
- `src/core/base.py` - Add `alert_by_default: bool` property to BaseLintRule

**Steps**:

1. Create `src/alerting/__init__.py`:
   ```python
   """Out-of-band alerting system for thai-lint."""
   from .types import AlertConfig, AlertRule
   from .base import AlertChannel
   from .dispatcher import AlertDispatcher

   __all__ = ["AlertConfig", "AlertRule", "AlertChannel", "AlertDispatcher"]
   ```

2. Create `src/alerting/types.py`:
   - `AlertRule` dataclass: `rule_pattern: str`, `alert: bool`
   - `AlertConfig` dataclass: `enabled: bool`, `rules: list[AlertRule]`
   - `SlackConfig` dataclass: `webhook_url: str`, `channel: str | None`
   - `DesktopConfig` dataclass: `enabled: bool`

3. Create `src/alerting/base.py`:
   - `AlertChannel` Protocol with `send(violation: Violation) -> bool` method
   - `is_available() -> bool` method for graceful degradation

4. Create `src/alerting/dispatcher.py`:
   - `AlertDispatcher` class
   - `register_channel(channel: AlertChannel)` method
   - `should_alert(violation: Violation, rule: BaseLintRule, config: AlertConfig) -> bool`
   - `dispatch(violation: Violation, rule: BaseLintRule, config: AlertConfig)` method

5. Modify `src/core/base.py`:
   - Add `alert_by_default: bool` property to `BaseLintRule` (default: `False`)

**Testing**:
- Unit tests for AlertConfig parsing
- Unit tests for dispatcher routing logic
- Unit tests for should_alert with various rule patterns

**Success Criteria**:
- [ ] All new files have proper headers per FILE_HEADER_STANDARDS.md
- [ ] AlertDispatcher can register channels and dispatch
- [ ] should_alert correctly matches rule patterns
- [ ] BaseLintRule has alert_by_default property
- [ ] All tests pass
- [ ] Pylint 10.00/10, Xenon A-grade

---

### PR2: Slack Webhook Integration

**Scope**: Implement Slack channel for alerting

**Files to Create**:
```
src/alerting/channels/
├── __init__.py
└── slack.py
```

**Steps**:

1. Create `src/alerting/channels/__init__.py`

2. Create `src/alerting/channels/slack.py`:
   - `SlackChannel` class implementing `AlertChannel` protocol
   - `__init__(config: SlackConfig)` - store webhook URL
   - `is_available() -> bool` - check if webhook URL is configured
   - `send(violation: Violation) -> bool` - POST to Slack webhook
   - Format message with violation details (file, line, rule, message)
   - Support env var interpolation in webhook URL (`${SLACK_WEBHOOK_URL}`)
   - Add rate limiting (max 1 message per second, batch if needed)

3. Add error handling:
   - Timeout handling (5 second timeout)
   - Retry logic (1 retry on failure)
   - Log failures but don't crash

**Testing**:
- Unit tests with mocked requests
- Test env var interpolation
- Test rate limiting behavior
- Test error handling

**Success Criteria**:
- [ ] Slack messages delivered with proper formatting
- [ ] Env var interpolation works
- [ ] Rate limiting prevents spam
- [ ] Graceful handling of webhook failures
- [ ] All tests pass

---

### PR3: Desktop Notification Integration

**Scope**: Implement cross-platform desktop notifications

**Files to Create**:
```
src/alerting/channels/
└── desktop.py
```

**Files to Modify**:
- `pyproject.toml` - Add `plyer` dependency

**Steps**:

1. Add `plyer` to pyproject.toml dependencies

2. Create `src/alerting/channels/desktop.py`:
   - `DesktopChannel` class implementing `AlertChannel` protocol
   - `is_available() -> bool` - check if running in desktop environment (not CI)
   - `send(violation: Violation) -> bool` - show notification via plyer
   - Title: "Thai-Lint Alert"
   - Message: violation summary
   - Graceful degradation if plyer unavailable or in CI

3. CI detection:
   - Check for `CI`, `GITHUB_ACTIONS`, `JENKINS_URL` env vars
   - If detected, `is_available()` returns False

**Testing**:
- Unit tests with mocked plyer
- Test CI detection
- Test graceful degradation

**Success Criteria**:
- [ ] Desktop notifications appear on Linux, macOS, Windows
- [ ] Graceful no-op in CI environments
- [ ] No crashes if plyer unavailable
- [ ] All tests pass

---

## Phase 2: Hook Integrity Linter

### PR4: Core Linter with No-Op Detection

**Scope**: Create hook integrity linter detecting sneaky no-ops in pre-commit config

**Files to Create**:
```
src/linters/hook_integrity/
├── __init__.py
├── linter.py              # HookIntegrityRule
├── config.py              # HookIntegrityConfig
├── precommit_analyzer.py  # YAML parsing
├── noop_detector.py       # Pattern matching
└── violation_builder.py   # Violation construction

tests/unit/linters/hook_integrity/
├── __init__.py
├── test_linter.py
├── test_noop_detector.py
└── test_precommit_analyzer.py
```

**Steps**:

1. Create `src/linters/hook_integrity/config.py`:
   - `HookIntegrityConfig` dataclass
   - `enabled: bool = True`
   - `check_precommit: bool = True`
   - `ignore: list[str] = []`

2. Create `src/linters/hook_integrity/noop_detector.py`:
   - `NoopDetector` class
   - `is_noop(entry: str) -> bool` - detect no-op commands
   - Patterns: `true`, `exit 0`, `:`, `""`, `/bin/true`, `echo` without command
   - `get_noop_reason(entry: str) -> str` - explain why it's a no-op

3. Create `src/linters/hook_integrity/precommit_analyzer.py`:
   - `PrecommitAnalyzer` class
   - `parse(content: str) -> dict` - parse YAML
   - `get_hooks() -> list[Hook]` - extract hook definitions
   - `Hook` dataclass: `id`, `entry`, `always_run`, `pass_filenames`

4. Create `src/linters/hook_integrity/violation_builder.py`:
   - `ViolationBuilder` class
   - `build_noop_violation(hook: Hook, reason: str, file_path: str, line: int)`

5. Create `src/linters/hook_integrity/linter.py`:
   - `HookIntegrityRule` extending `BaseLintRule`
   - `rule_id = "hook-integrity.noop-bypass"`
   - `alert_by_default = True`
   - `check()` - orchestrate analysis

**Testing**:
- Test detection of all no-op patterns
- Test YAML parsing with various configs
- Test violation generation
- Integration test with sample .pre-commit-config.yaml

**Success Criteria**:
- [ ] Detects `entry: "true"`, `"exit 0"`, `":"`, `""`
- [ ] Detects `/bin/true`, `echo` no-ops
- [ ] Proper YAML parsing
- [ ] `alert_by_default = True`
- [ ] All tests pass

---

### PR5: Significant Change Detection

**Scope**: Detect hook removals and weakening

**Files to Modify**:
- `src/linters/hook_integrity/linter.py`
- `src/linters/hook_integrity/precommit_analyzer.py`

**Steps**:

1. Add baseline comparison to `precommit_analyzer.py`:
   - `compare_to_baseline(current: dict, baseline: dict) -> list[Change]`
   - `Change` dataclass: `type` (removed, weakened), `hook_id`, `details`

2. Add new rule to linter:
   - `rule_id = "hook-integrity.hook-weakened"` for weakening
   - `rule_id = "hook-integrity.hook-removed"` for removal
   - Both have `alert_by_default = True`

3. Detect weakening:
   - `always_run: true` → `false`
   - `pass_filenames: true` → `false` (on certain hooks)

4. Detect removal:
   - Hook present in git history but not in current file
   - Use `git show HEAD~1:.pre-commit-config.yaml` for baseline

**Testing**:
- Test removal detection
- Test weakening detection
- Test baseline comparison

**Success Criteria**:
- [ ] Detects hook removal
- [ ] Detects `always_run` weakening
- [ ] Proper git baseline comparison
- [ ] All tests pass

---

### PR6: CLI Integration

**Scope**: Add `thailint hook-integrity` command

**Files to Modify**:
- `src/cli.py`

**Steps**:

1. Add `hook-integrity` command following existing patterns:
   ```python
   @cli.command("hook-integrity")
   @click.argument("paths", nargs=-1, type=click.Path())
   @click.option("--config", "-c", "config_file", type=click.Path())
   @format_option
   @click.pass_context
   def hook_integrity(ctx, paths, config_file, format):
       """Check pre-commit hooks for sneaky bypasses."""
   ```

2. Filter violations to `hook-integrity.*` pattern

3. Support text, JSON, SARIF output formats

**Testing**:
- CLI integration tests
- Test all output formats
- Test with sample configs

**Success Criteria**:
- [ ] `thailint hook-integrity` works
- [ ] All output formats supported
- [ ] Proper exit codes (0 clean, 1 violations)
- [ ] All tests pass

---

## Phase 3: Integration & Polish

### PR7: Wire Alerting to Orchestrator

**Scope**: Integrate alerting system with orchestrator

**Files to Modify**:
- `src/orchestrator/core.py`
- `src/cli.py`

**Steps**:

1. Modify `src/orchestrator/core.py`:
   - Add `AlertDispatcher` as optional component
   - After collecting violations, check each for alerting
   - Call `dispatcher.dispatch()` for violations that should alert

2. Add CLI flags:
   - `--alert` / `--no-alert` to override config
   - Default: use config settings

3. Load alerting config from `.thailint.yaml`:
   ```yaml
   alerting:
     enabled: true
     slack:
       webhook_url: ${SLACK_WEBHOOK_URL}
     desktop:
       enabled: true
     rules:
       hook-integrity.noop-bypass: true
   ```

**Testing**:
- Integration tests with mocked channels
- Test CLI flag overrides
- Test config loading

**Success Criteria**:
- [ ] Alerts dispatched for matching violations
- [ ] CLI flags work
- [ ] Config loading works
- [ ] All tests pass

---

### PR8: Documentation and Examples

**Scope**: Document the feature and provide examples

**Files to Create**:
- `docs/alerting.md`
- `examples/alerting-config.yaml`

**Files to Modify**:
- `README.md` or main docs

**Steps**:

1. Create `docs/alerting.md`:
   - Feature overview
   - Configuration reference
   - Slack setup instructions
   - Desktop notification setup
   - Per-rule configuration
   - Alert defaults philosophy

2. Create example config:
   ```yaml
   alerting:
     enabled: true
     slack:
       webhook_url: ${SLACK_WEBHOOK_URL}
       channel: "#dev-alerts"
     desktop:
       enabled: true
     rules:
       hook-integrity.noop-bypass: true
       hook-integrity.hook-removed: true
   ```

3. Update main documentation with alerting section

**Success Criteria**:
- [ ] Clear documentation
- [ ] Working example config
- [ ] Slack setup instructions complete
- [ ] All docs follow standards

---

## Implementation Guidelines

### Code Standards
- All files must have proper headers per FILE_HEADER_STANDARDS.md
- Pylint score exactly 10.00/10
- Xenon complexity all A-grade
- Type hints required for all functions
- Google-style docstrings

### Testing Requirements
- Unit tests for all new classes
- Integration tests for CLI commands
- Mock external services (Slack, desktop)
- >80% coverage for new code

### Documentation Standards
- All public functions documented
- Configuration options documented
- Examples provided

### Security Considerations
- Webhook URLs should support env vars (not hardcoded secrets)
- Rate limiting to prevent abuse
- No sensitive data in notifications

### Performance Targets
- Alerting should not slow down linting (<100ms overhead)
- Slack timeout 5 seconds
- Desktop notifications async if possible

## Rollout Strategy

1. **Phase 1**: Alerting infrastructure merged, no active consumers
2. **Phase 2**: Hook integrity linter available, alerting opt-in
3. **Phase 3**: Full integration, documentation complete

## Success Metrics

### Launch Metrics
- All 8 PRs merged
- Feature documented
- No regressions in existing linters

### Ongoing Metrics
- Slack delivery success rate
- Desktop notification reliability
- User adoption of hook integrity linter
