# thai-lint

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/thai-lint)](https://pypi.org/project/thai-lint/)
[![Documentation](https://readthedocs.org/projects/thai-lint/badge/?version=latest)](https://thai-lint.readthedocs.io/)

**The AI Linter** - Catch the mistakes AI coding assistants keep making.

thailint detects anti-patterns that AI tools frequently introduce: duplicate code, excessive nesting, magic numbers, SRP violations, and more. It works across Python, TypeScript, and JavaScript with unified rules - filling gaps that existing linters miss.

## Installation

```bash
pip install thai-lint
```

Or with Docker:
```bash
docker run --rm -v $(pwd):/data washad/thailint:latest --help
```

## Quick Start

```bash
# Generate a config file (optional)
thailint init-config

# Run any linter
thailint dry src/
```

That's it. See violations, fix them, ship better code.

## Available Linters

| Linter | What It Catches | Command | Docs |
|--------|-----------------|---------|------|
| **DRY** | Duplicate code across files | `thailint dry src/` | [Guide](https://thai-lint.readthedocs.io/en/latest/dry-linter/) |
| **Nesting** | Deeply nested if/for/while blocks | `thailint nesting src/` | [Guide](https://thai-lint.readthedocs.io/en/latest/nesting-linter/) |
| **Magic Numbers** | Unnamed numeric literals | `thailint magic-numbers src/` | [Guide](https://thai-lint.readthedocs.io/en/latest/magic-numbers-linter/) |
| **SRP** | Classes doing too much | `thailint srp src/` | [Guide](https://thai-lint.readthedocs.io/en/latest/srp-linter/) |
| **File Header** | Missing documentation headers | `thailint file-header src/` | [Guide](https://thai-lint.readthedocs.io/en/latest/file-header-linter/) |
| **Stateless Class** | Classes that should be functions | `thailint stateless-class src/` | [Guide](https://thai-lint.readthedocs.io/en/latest/stateless-class-linter/) |
| **Collection Pipeline** | Loops with embedded filtering | `thailint pipeline src/` | [Guide](https://thai-lint.readthedocs.io/en/latest/collection-pipeline-linter/) |
| **Method Property** | Methods that should be @property | `thailint method-property src/` | [Guide](https://thai-lint.readthedocs.io/en/latest/method-property-linter/) |
| **File Placement** | Files in wrong directories | `thailint file-placement src/` | [Guide](https://thai-lint.readthedocs.io/en/latest/file-placement-linter/) |
| **Lazy Ignores** | Unjustified linting suppressions | `thailint lazy-ignores src/` | [Guide](https://thai-lint.readthedocs.io/en/latest/lazy-ignores-linter/) |
| **Print Statements** | Debug prints left in code | `thailint print-statements src/` | [Guide](https://thai-lint.readthedocs.io/en/latest/print-statements-linter/) |
| **Stringly Typed** | Strings that should be enums | `thailint stringly-typed src/` | [Guide](https://thai-lint.readthedocs.io/en/latest/stringly-typed-linter/) |

## Configuration

Create `.thailint.yaml` in your project root:

```yaml
dry:
  enabled: true
  min_duplicate_lines: 4

nesting:
  enabled: true
  max_nesting_depth: 3

magic-numbers:
  enabled: true
  allowed_numbers: [-1, 0, 1, 2, 10, 100]
```

Or generate one automatically:
```bash
thailint init-config --preset lenient  # or: strict, standard
```

See [Configuration Reference](https://thai-lint.readthedocs.io/en/latest/configuration/) for all options.

## Output Formats

```bash
# Human-readable (default)
thailint dry src/

# JSON for CI/CD
thailint dry --format json src/

# SARIF for GitHub Code Scanning
thailint dry --format sarif src/ > results.sarif
```

## Ignoring Violations

```python
# Line-level
timeout = 3600  # thailint: ignore[magic-numbers]

# File-level
# thailint: ignore-file[dry]
```

Or in config:
```yaml
dry:
  ignore:
    - "tests/"
    - "**/generated/**"
```

See [How to Ignore Violations](https://thai-lint.readthedocs.io/en/latest/how-to-ignore-violations/) for all 5 ignore levels.

## CI/CD Integration

```yaml
# GitHub Actions
- name: Run thailint
  run: |
    pip install thai-lint
    thailint dry src/
    thailint nesting src/
```

Exit codes: `0` = success, `1` = violations found, `2` = error.

## Documentation

- **[Quick Start Guide](https://thai-lint.readthedocs.io/en/latest/quick-start/)** - Get running in 5 minutes
- **[Configuration Reference](https://thai-lint.readthedocs.io/en/latest/configuration/)** - All config options
- **[Troubleshooting](https://thai-lint.readthedocs.io/en/latest/troubleshooting/)** - Common issues
- **[Full Documentation](https://thai-lint.readthedocs.io/)** - Everything else

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
git clone https://github.com/be-wise-be-kind/thai-lint.git
cd thai-lint
poetry install
just test
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Issues**: [github.com/be-wise-be-kind/thai-lint/issues](https://github.com/be-wise-be-kind/thai-lint/issues)
- **Docs**: [thai-lint.readthedocs.io](https://thai-lint.readthedocs.io/)
