# Out-of-Band Alerting System - AI Context

**Purpose**: AI agent context document for implementing out-of-band alerting system

**Scope**: Alerting infrastructure, hook integrity linter, and integration with existing thai-lint architecture

**Overview**: Comprehensive context document for AI agents working on the out-of-band alerting feature.
    This feature addresses a fundamental problem with AI agents and automated checks: agents can satisfy
    any automated requirement by modifying code/config to make it pass. Out-of-band alerting breaks this
    loop by notifying humans through channels the agent cannot control (Slack, desktop notifications).

**Dependencies**: plyer (desktop notifications), requests (Slack webhook), PyYAML, existing thai-lint core

**Exports**: AlertDispatcher, AlertChannel protocol, HookIntegrityRule, configuration system

**Related**: PR_BREAKDOWN.md for implementation tasks, PROGRESS_TRACKER.md for current status

**Implementation**: Plugin-based alerting channels with per-rule alert defaults and user-configurable overrides

---

## Overview

The out-of-band alerting system adds a new dimension to thai-lint: the ability to notify humans through channels that cannot be controlled by automated agents. This is critical for detecting when an agent might be "gaming" the linting system rather than actually fixing issues.

The feature has two main components:
1. **Alerting Infrastructure** - A general-purpose system any linter can use
2. **Hook Integrity Linter** - The first consumer, detecting sneaky pre-commit bypasses

## Project Background

### The Problem

AI agents are increasingly capable of satisfying automated checks. When a linter reports a violation, an agent can:
- Fix the actual issue (desired behavior)
- Add an ignore comment to suppress the violation
- Modify the linter configuration to exclude the file
- Modify the pre-commit hook to not run the linter
- Make the hook a no-op (`entry: "true"`)

The last two are particularly insidious because they compromise the entire linting pipeline, not just one violation.

### The Solution

Out-of-band alerting notifies humans through channels the agent cannot control:
- **Slack webhook** - Posts to a channel the agent has no access to
- **Desktop popup** - Appears on the developer's screen

Even if the agent makes all checks "pass", the human still gets notified about suspicious activity.

## Feature Vision

1. **Break the automation loop** - Humans get notified regardless of what the agent does
2. **Configurable per-rule** - Not everything needs an alert, just pipeline-compromising changes
3. **General infrastructure** - Any linter can opt into alerting, not just hook-integrity
4. **Graceful degradation** - Works in CI (Slack only) and local dev (both)

## Current Application Context

### Existing Architecture

Thai-lint uses a plugin-based architecture:
- `BaseLintRule` - Abstract base class for all linters
- `Orchestrator` - Coordinates linter execution
- `Violation` - Standard violation type with severity
- CLI commands per linter with text/JSON/SARIF output

### Key Files

| Purpose | Path |
|---------|------|
| Base rule class | `src/core/base.py` |
| Violation type | `src/core/types.py` |
| Orchestrator | `src/orchestrator/core.py` |
| CLI | `src/cli.py` |
| Example linter | `src/linters/srp/` |

### Existing Patterns

**Linter structure**:
```
src/linters/{name}/
├── __init__.py
├── linter.py           # Main rule class
├── config.py           # Configuration dataclass
├── {lang}_analyzer.py  # Language-specific analysis
└── violation_builder.py
```

**Rule registration**: Automatic via rule discovery in `src/core/rule_discovery.py`

**Configuration**: Loaded from `.thailint.yaml` via `load_linter_config()`

## Target Architecture

### Core Components

**AlertChannel Protocol** (`src/alerting/base.py`):
```python
class AlertChannel(Protocol):
    def is_available(self) -> bool: ...
    def send(self, violation: Violation) -> bool: ...
```

**AlertDispatcher** (`src/alerting/dispatcher.py`):
- Registers multiple channels
- Checks if violation should alert (rule default + config override)
- Dispatches to all available channels

**BaseLintRule Extension** (`src/core/base.py`):
```python
class BaseLintRule(ABC):
    @property
    def alert_by_default(self) -> bool:
        return False  # Override in subclasses
```

### User Journey

1. User configures Slack webhook URL in `.thailint.yaml`
2. User runs `thailint hook-integrity` or `thailint lint`
3. Linter finds a no-op in `.pre-commit-config.yaml`
4. Violation created with `alert_by_default = True`
5. AlertDispatcher checks config, sees alert enabled
6. Slack message sent, desktop notification shown
7. Human sees notification regardless of exit code

### Configuration Model

```yaml
alerting:
  enabled: true
  slack:
    webhook_url: ${SLACK_WEBHOOK_URL}
  desktop:
    enabled: true
  rules:
    hook-integrity.noop-bypass: true    # default: true
    hook-integrity.hook-removed: true   # default: true
    srp.violation: false                # default: false
```

**Alert decision flow**:
1. Check if `alerting.enabled` is true
2. Check if rule has explicit override in `alerting.rules`
3. If no override, use rule's `alert_by_default`
4. If should alert, dispatch to all available channels

## Key Decisions Made

### Severity vs Alert

**Decision**: Severity and alert are orthogonal concerns.

**Rationale**:
- Severity (ERROR/WARNING) determines if build fails
- Alert (yes/no) determines if human gets notified
- A violation can be ERROR + no alert (normal linting)
- A violation can be ERROR + alert (pipeline compromise)

### Per-Rule Defaults

**Decision**: Each rule defines its own `alert_by_default`.

**Rationale**:
- Rules know best if they detect "gaming" vs "normal violations"
- Users can override, but sensible defaults matter
- Hook integrity rules default to alert; SRP/magic-numbers don't

### Graceful Degradation

**Decision**: Desktop notifications no-op in CI environments.

**Rationale**:
- CI has no desktop to notify
- Slack is the primary channel in CI
- No crashes or errors if plyer unavailable

## Integration Points

### With Existing Features

**Orchestrator**: After collecting violations, check for alerting:
```python
for violation in violations:
    rule = self._get_rule_for_violation(violation)
    if self._dispatcher.should_alert(violation, rule, config):
        self._dispatcher.dispatch(violation, rule, config)
```

**CLI**: Add `--alert` / `--no-alert` flags to override config.

**Configuration**: Add `alerting` section to `.thailint.yaml` schema.

### With Pre-Commit

The hook integrity linter analyzes `.pre-commit-config.yaml` but doesn't integrate with pre-commit directly. It's a static analysis tool that can run:
- As a CLI command
- In CI
- As part of `thailint lint`

## Success Metrics

1. **Delivery reliability** - >99% Slack message delivery
2. **Latency** - <5 second alerting overhead
3. **Detection accuracy** - All no-op patterns detected
4. **User experience** - Clear, actionable notifications

## Technical Constraints

1. **No network in tests** - Mock all HTTP requests
2. **Cross-platform** - Desktop notifications must work on Linux, macOS, Windows
3. **CI detection** - Must reliably detect CI environments
4. **Rate limiting** - Prevent Slack spam on large codebases

## AI Agent Guidance

### When Implementing Alerting Infrastructure

1. Start with types and interfaces (PR1)
2. Use Protocol for AlertChannel, not ABC
3. Make dispatcher stateless where possible
4. Support env var interpolation for webhook URLs

### When Implementing Hook Integrity Linter

1. Follow existing linter patterns in `src/linters/`
2. Parse YAML with `yaml.safe_load()`
3. Set `alert_by_default = True` for all rules
4. Use git to get baseline for removal detection

### Common Patterns

**Config loading**:
```python
config = load_linter_config(context, "hook_integrity", HookIntegrityConfig)
```

**Violation creation**:
```python
Violation(
    rule_id="hook-integrity.noop-bypass",
    file_path=str(context.file_path),
    line=line_number,
    column=0,
    message="Hook entry is a no-op: 'true'",
    suggestion="Replace with actual command like 'just lint'"
)
```

**Rule property**:
```python
@property
def alert_by_default(self) -> bool:
    return True  # This rule detects pipeline compromise
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Slack rate limits | Batch messages, add delays |
| Desktop notification spam | Aggregate violations into single notification |
| False positives | Careful no-op pattern matching |
| Git not available | Graceful degradation for baseline comparison |

## Future Enhancements

1. **Justfile analysis** - Detect no-ops in justfile recipes
2. **Ignore directive tracking** - Alert on new inline ignores
3. **Email channel** - For teams not using Slack
4. **Webhook channel** - Generic webhook for custom integrations
5. **Alert history** - Track alerts over time for patterns
