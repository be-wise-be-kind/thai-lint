# thai-lint

The AI Linter - Lint and governance for AI-generated code

A professional command-line tool built with Python and Click framework.

## Features

- Modern CLI with Click framework
- YAML/JSON configuration support
- Comprehensive error handling
- Structured logging
- Docker containerization
- Complete test suite with pytest
- Type hints throughout
- Code quality with Ruff

## Installation

### From Source

```bash
# Clone repository
git clone https://github.com/{{GITHUB_USERNAME}}/thai-lint.git
cd thai-lint

# Install dependencies
pip install -e ".[dev]"
```

### From PyPI (once published)

```bash
pip install thai-lint
```

### With Docker

```bash
# Build image
docker-compose -f docker-compose.cli.yml build

# Run CLI
docker-compose -f docker-compose.cli.yml run cli --help
```

## Quick Start

```bash
# View available commands
thai-lint --help

# Run hello command
thai-lint hello --name "World"

# Show configuration
thai-lint config show

# Set configuration
thai-lint config set greeting "Hi"
```

## Configuration

Configuration is loaded from (in order of precedence):

1. `./config.yaml` or `./config.json` (current directory)
2. `~/.config/thai-lint/config.yaml` (user config)
3. `/etc/thai-lint/config.yaml` (system config, Unix/Linux)

### Configuration Options

```yaml
# Default configuration
app_name: thai-lint
log_level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
output_format: text  # text, json, yaml
greeting: Hello
max_retries: 3
timeout: 30
```

## Usage

### Hello Command

```bash
# Basic greeting
thai-lint hello
# Output: Hello, World!

# Custom name
thai-lint hello --name Alice
# Output: Hello, Alice!

# Uppercase output
thai-lint hello --name Bob --uppercase
# Output: HELLO, BOB!
```

### Configuration Management

```bash
# Show current configuration
thai-lint config show

# Show as JSON
thai-lint config show --format json

# Get specific value
thai-lint config get log_level

# Set value
thai-lint config set log_level DEBUG

# Reset to defaults
thai-lint config reset --yes
```

### With Custom Config

```bash
# Use specific config file
thai-lint --config myconfig.yaml hello --name Test

# Verbose output
thai-lint --verbose hello --name Test
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (if using)
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_cli.py::test_hello_command
```

### Code Quality

```bash
# Lint code
ruff check src tests

# Format code
ruff format src tests

# Type checking
mypy src/
```

### Building

```bash
# Build Python package
python -m build

# Build Docker image
docker-compose -f docker-compose.cli.yml build
```

## Docker Usage

```bash
# Build image
docker-compose -f docker-compose.cli.yml build

# Run CLI help
docker-compose -f docker-compose.cli.yml run cli --help

# Run hello command
docker-compose -f docker-compose.cli.yml run cli hello --name Docker

# With config volume
docker-compose -f docker-compose.cli.yml run \
    -v $(pwd)/config:/config:ro \
    cli --config /config/config.yaml hello
```

## Project Structure

```
thai-lint/
├── src/                    # Application source code
│   ├── __init__.py        # Package initialization
│   ├── cli.py             # CLI commands
│   └── config.py          # Configuration management
├── tests/                  # Test suite
│   ├── __init__.py
│   └── test_cli.py        # CLI tests
├── .ai/                    # AI agent documentation
│   ├── docs/
│   ├── howtos/
│   └── templates/
├── pyproject.toml          # Project configuration
├── docker-compose.cli.yml  # Docker configuration
└── README.md               # This file
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Write tests for new features
- Follow existing code style (enforced by Ruff)
- Add type hints to all functions
- Update documentation for user-facing changes
- Run `pytest` and `ruff check` before committing

## How-To Guides

Check `.ai/howtos/python-cli/` for detailed guides:

- **how-to-add-cli-command.md** - Adding new CLI commands
- **how-to-handle-config-files.md** - Configuration management
- **how-to-package-cli-tool.md** - Packaging and distribution

## Architecture

See `.ai/docs/python-cli-architecture.md` for detailed architecture documentation.

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: https://github.com/{{GITHUB_USERNAME}}/thai-lint/issues
- **Documentation**: `.ai/docs/` and `.ai/howtos/`

## Acknowledgments

Built with:
- [Click](https://click.palletsprojects.com/) - CLI framework
- [pytest](https://pytest.org/) - Testing framework
- [Ruff](https://docs.astral.sh/ruff/) - Linting and formatting
- [Docker](https://www.docker.com/) - Containerization

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
