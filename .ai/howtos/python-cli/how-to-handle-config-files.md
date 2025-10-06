# How to Handle Configuration Files

**Purpose**: Guide for managing configuration files in Python CLI applications using YAML and JSON

**Scope**: Config loading, validation, defaults, merging, persistence, and schema management

**Overview**: This guide demonstrates configuration file management patterns for CLI applications including
    loading from multiple sources, providing defaults, schema validation, merging strategies, and persistence.
    Examples cover YAML and JSON formats, environment-specific configs, and configuration hierarchies with
    best practices for user-friendly configuration management.

**Prerequisites**: Python CLI application installed, basic understanding of YAML/JSON formats

**Related**: .ai/docs/python-cli-architecture.md, .ai/templates/python-cli/config-loader.py.template

---

## Overview

Configuration management involves:
1. Defining configuration schema and defaults
2. Loading configuration from files
3. Validating configuration values
4. Merging configs from multiple sources
5. Saving configuration changes
6. Handling missing or invalid configs

## Basic Configuration Loading

### Step 1: Define Configuration Schema

Create or edit `src/config.py`:

```python
"""
Purpose: Configuration management for CLI application

Scope: Load, validate, and save YAML/JSON configuration files

Overview: Provides configuration management with multiple source support, schema validation,
    defaults, and persistence. Handles config file location discovery, format detection,
    merging strategies, and safe updates with atomic writes.

Dependencies: PyYAML for YAML parsing, pathlib for path handling, json for JSON parsing

Exports: load_config(), save_config(), validate_config(), merge_configs(), ConfigSchema

Interfaces: Configuration file paths, config dictionaries, validation results
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml
import json
import logging

logger = logging.getLogger(__name__)

# Default configuration values
DEFAULT_CONFIG = {
    'app_name': 'my-cli-tool',
    'version': '1.0.0',
    'log_level': 'INFO',
    'output_format': 'text',
    'max_retries': 3,
    'timeout': 30,
}

# Configuration file search paths (in priority order)
CONFIG_LOCATIONS = [
    Path.cwd() / 'config.yaml',  # Current directory
    Path.cwd() / 'config.json',
    Path.home() / '.config' / 'my-cli-tool' / 'config.yaml',  # User config
    Path.home() / '.config' / 'my-cli-tool' / 'config.json',
    Path('/etc/my-cli-tool/config.yaml'),  # System config
]


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration with fallback to defaults.

    Args:
        config_path: Explicit path to config file. If None, searches default locations.

    Returns:
        Configuration dictionary with defaults merged in.

    Raises:
        ConfigError: If config file exists but cannot be parsed.
    """
    # Start with defaults
    config = DEFAULT_CONFIG.copy()

    # If explicit path provided, use it
    if config_path:
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return config

        user_config = _load_config_file(config_path)
        config.update(user_config)
        logger.info(f"Loaded config from: {config_path}")
        return config

    # Search default locations
    for location in CONFIG_LOCATIONS:
        if location.exists():
            user_config = _load_config_file(location)
            config.update(user_config)
            logger.info(f"Loaded config from: {location}")
            return config

    logger.info("No config file found, using defaults")
    return config


def _load_config_file(path: Path) -> Dict[str, Any]:
    """Load config from YAML or JSON file based on extension."""
    try:
        with open(path, 'r') as f:
            if path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f) or {}
            elif path.suffix == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported config format: {path.suffix}")
    except Exception as e:
        raise ConfigError(f"Failed to load config from {path}: {e}")


def save_config(config: Dict[str, Any], config_path: Optional[Path] = None):
    """
    Save configuration to file.

    Args:
        config: Configuration dictionary to save.
        config_path: Path to save config. If None, uses first default location.
    """
    path = config_path or CONFIG_LOCATIONS[0]

    # Create parent directory if needed
    path.parent.mkdir(parents=True, exist_ok=True)

    # Save based on extension
    try:
        with open(path, 'w') as f:
            if path.suffix in ['.yaml', '.yml']:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            elif path.suffix == '.json':
                json.dump(config, f, indent=2)
            else:
                raise ValueError(f"Unsupported config format: {path.suffix}")

        logger.info(f"Saved config to: {path}")
    except Exception as e:
        raise ConfigError(f"Failed to save config to {path}: {e}")


class ConfigError(Exception):
    """Configuration-related errors."""
    pass
```

### Step 2: Use Configuration in CLI

Edit `src/cli.py` to load and use configuration:

```python
import click
from src.config import load_config, save_config

@click.group()
@click.option('--config', '-c', type=click.Path(), help='Config file path')
@click.pass_context
def cli(ctx, config):
    """CLI with configuration support."""
    ctx.ensure_object(dict)

    # Load configuration
    if config:
        ctx.obj['config'] = load_config(Path(config))
    else:
        ctx.obj['config'] = load_config()

    ctx.obj['config_path'] = config


@cli.command()
@click.pass_context
def info(ctx):
    """Display current configuration."""
    config = ctx.obj['config']

    for key, value in config.items():
        click.echo(f"{key}: {value}")
```

### Step 3: Test Configuration Loading

```bash
# Use default config
python -m src.cli info

# Use specific config file
python -m src.cli --config myconfig.yaml info
```

## Configuration Validation

### Step 1: Add Validation

Add validation function to `src/config.py`:

```python
from typing import List, Tuple

def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate configuration schema and values.

    Args:
        config: Configuration dictionary to validate.

    Returns:
        Tuple of (is_valid, error_messages).
    """
    errors = []

    # Check required keys
    required_keys = ['app_name', 'log_level']
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required key: {key}")

    # Validate log level
    valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if 'log_level' in config:
        if config['log_level'] not in valid_log_levels:
            errors.append(
                f"Invalid log_level: {config['log_level']}. "
                f"Must be one of: {', '.join(valid_log_levels)}"
            )

    # Validate output format
    valid_formats = ['text', 'json', 'yaml']
    if 'output_format' in config:
        if config['output_format'] not in valid_formats:
            errors.append(
                f"Invalid output_format: {config['output_format']}. "
                f"Must be one of: {', '.join(valid_formats)}"
            )

    # Validate numeric values
    if 'max_retries' in config:
        if not isinstance(config['max_retries'], int) or config['max_retries'] < 0:
            errors.append("max_retries must be a non-negative integer")

    if 'timeout' in config:
        if not isinstance(config['timeout'], (int, float)) or config['timeout'] <= 0:
            errors.append("timeout must be a positive number")

    return len(errors) == 0, errors


# Update load_config to validate
def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load and validate configuration."""
    config = DEFAULT_CONFIG.copy()

    # Load user config...
    # (previous loading logic)

    # Validate configuration
    is_valid, errors = validate_config(config)
    if not is_valid:
        error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ConfigError(error_msg)

    return config
```

### Step 2: Test Validation

Create invalid config file `invalid.yaml`:

```yaml
log_level: INVALID
max_retries: -5
output_format: pdf
```

Test validation:

```bash
python -m src.cli --config invalid.yaml info
# Should show validation errors
```

## Configuration Commands

### Step 1: Add Config Management Commands

Add config commands to `src/cli.py`:

```python
@cli.group()
def config():
    """Configuration management commands."""
    pass


@config.command('show')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'yaml']), default='text')
@click.pass_context
def config_show(ctx, format):
    """Display current configuration."""
    cfg = ctx.obj['config']

    if format == 'json':
        import json
        click.echo(json.dumps(cfg, indent=2))
    elif format == 'yaml':
        import yaml
        click.echo(yaml.dump(cfg, default_flow_style=False))
    else:
        # Text format
        for key, value in cfg.items():
            click.echo(f"{key}: {value}")


@config.command('get')
@click.argument('key')
@click.pass_context
def config_get(ctx, key):
    """Get specific configuration value."""
    cfg = ctx.obj['config']

    if key not in cfg:
        raise click.ClickException(f"Configuration key not found: {key}")

    click.echo(cfg[key])


@config.command('set')
@click.argument('key')
@click.argument('value')
@click.pass_context
def config_set(ctx, key, value):
    """Set configuration value."""
    cfg = ctx.obj['config']

    # Type conversion for common types
    if value.lower() == 'true':
        value = True
    elif value.lower() == 'false':
        value = False
    elif value.isdigit():
        value = int(value)
    elif value.replace('.', '', 1).isdigit():
        value = float(value)

    # Update config
    cfg[key] = value

    # Validate
    is_valid, errors = validate_config(cfg)
    if not is_valid:
        raise click.ClickException("Invalid configuration:\n" + "\n".join(errors))

    # Save
    config_path = ctx.obj.get('config_path')
    if config_path:
        save_config(cfg, Path(config_path))
    else:
        save_config(cfg)

    click.echo(f"Set {key} = {value}")


@config.command('reset')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@click.pass_context
def config_reset(ctx, yes):
    """Reset configuration to defaults."""
    if not yes:
        click.confirm('Reset configuration to defaults?', abort=True)

    from src.config import DEFAULT_CONFIG

    config_path = ctx.obj.get('config_path')
    if config_path:
        save_config(DEFAULT_CONFIG.copy(), Path(config_path))
    else:
        save_config(DEFAULT_CONFIG.copy())

    click.echo("Configuration reset to defaults")
```

### Step 2: Test Config Commands

```bash
# Show current config
python -m src.cli config show

# Show as JSON
python -m src.cli config show --format json

# Get specific value
python -m src.cli config get log_level

# Set value
python -m src.cli config set log_level DEBUG

# Verify change
python -m src.cli config get log_level

# Reset to defaults
python -m src.cli config reset --yes
```

## Environment-Specific Configurations

### Step 1: Support Multiple Environments

Extend `src/config.py`:

```python
def load_config_for_environment(
    env: str = 'development',
    config_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Load environment-specific configuration.

    Args:
        env: Environment name (development, staging, production).
        config_path: Optional base config path.

    Returns:
        Merged configuration for specified environment.
    """
    # Load base config
    base_config = load_config(config_path)

    # Look for environment-specific config
    env_config_name = f"config.{env}.yaml"
    env_locations = [
        Path.cwd() / env_config_name,
        Path.home() / '.config' / 'my-cli-tool' / env_config_name,
    ]

    # Merge environment-specific settings
    for location in env_locations:
        if location.exists():
            env_config = _load_config_file(location)
            base_config = merge_configs(base_config, env_config)
            logger.info(f"Loaded {env} config from: {location}")
            break

    return base_config


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configurations, with override taking precedence.

    Args:
        base: Base configuration.
        override: Override configuration.

    Returns:
        Merged configuration.
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dicts
            result[key] = merge_configs(result[key], value)
        else:
            # Override value
            result[key] = value

    return result
```

### Step 2: Use Environment Configs

```bash
# Create environment-specific configs
cat > config.development.yaml <<EOF
log_level: DEBUG
max_retries: 1
EOF

cat > config.production.yaml <<EOF
log_level: WARNING
max_retries: 5
timeout: 60
EOF

# Load for specific environment
export APP_ENV=production
python -m src.cli --config config.yaml info
```

## Advanced Patterns

### Configuration with Pydantic

For stronger validation, use Pydantic:

```python
from pydantic import BaseModel, Field, validator
from typing import Literal

class ConfigSchema(BaseModel):
    """Configuration schema with validation."""

    app_name: str = Field(default='my-cli-tool', description='Application name')
    version: str = Field(default='1.0.0', pattern=r'^\d+\.\d+\.\d+$')
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'
    output_format: Literal['text', 'json', 'yaml'] = 'text'
    max_retries: int = Field(default=3, ge=0)
    timeout: float = Field(default=30.0, gt=0)

    @validator('app_name')
    def validate_app_name(cls, v):
        if not v or not v.strip():
            raise ValueError('app_name cannot be empty')
        return v

    class Config:
        extra = 'forbid'  # Reject unknown fields


def load_config(config_path: Optional[Path] = None) -> ConfigSchema:
    """Load and validate configuration using Pydantic."""
    config_data = DEFAULT_CONFIG.copy()

    # Load from file...
    # (loading logic)

    # Validate with Pydantic
    try:
        return ConfigSchema(**config_data)
    except ValidationError as e:
        raise ConfigError(f"Configuration validation failed:\n{e}")
```

### Encrypted Configuration Values

For sensitive values:

```python
from cryptography.fernet import Fernet
import base64

class SecureConfig:
    """Configuration with encryption support."""

    def __init__(self, key: Optional[bytes] = None):
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt_value(self, value: str) -> str:
        """Encrypt a configuration value."""
        encrypted = self.cipher.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a configuration value."""
        encrypted = base64.b64decode(encrypted_value.encode())
        return self.cipher.decrypt(encrypted).decode()

    def load_secure_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load config and decrypt secure values."""
        secure_config = config.copy()

        # Decrypt values marked as encrypted
        for key, value in config.items():
            if key.startswith('encrypted_'):
                actual_key = key.replace('encrypted_', '')
                secure_config[actual_key] = self.decrypt_value(value)
                del secure_config[key]

        return secure_config
```

## Testing Configuration

### Step 1: Write Config Tests

Create `tests/test_config.py`:

```python
import pytest
from pathlib import Path
from src.config import (
    load_config,
    save_config,
    validate_config,
    merge_configs,
    ConfigError,
)

def test_load_default_config():
    """Test loading default configuration."""
    config = load_config()
    assert config['app_name'] == 'my-cli-tool'
    assert config['log_level'] == 'INFO'


def test_load_config_from_file(tmp_path):
    """Test loading config from YAML file."""
    config_file = tmp_path / 'config.yaml'
    config_file.write_text('log_level: DEBUG\nmax_retries: 5\n')

    config = load_config(config_file)
    assert config['log_level'] == 'DEBUG'
    assert config['max_retries'] == 5


def test_save_config(tmp_path):
    """Test saving configuration."""
    config_file = tmp_path / 'config.yaml'
    config = {'log_level': 'DEBUG', 'max_retries': 5}

    save_config(config, config_file)

    assert config_file.exists()
    loaded = load_config(config_file)
    assert loaded['log_level'] == 'DEBUG'


def test_validate_valid_config():
    """Test validation of valid config."""
    config = {
        'app_name': 'test-app',
        'log_level': 'INFO',
        'max_retries': 3,
        'timeout': 30,
    }

    is_valid, errors = validate_config(config)
    assert is_valid
    assert len(errors) == 0


def test_validate_invalid_log_level():
    """Test validation catches invalid log level."""
    config = {
        'app_name': 'test-app',
        'log_level': 'INVALID',
    }

    is_valid, errors = validate_config(config)
    assert not is_valid
    assert any('log_level' in error for error in errors)


def test_merge_configs():
    """Test config merging."""
    base = {'a': 1, 'b': {'c': 2, 'd': 3}}
    override = {'b': {'d': 4}, 'e': 5}

    merged = merge_configs(base, override)

    assert merged['a'] == 1
    assert merged['b']['c'] == 2
    assert merged['b']['d'] == 4
    assert merged['e'] == 5
```

### Step 2: Run Tests

```bash
pytest tests/test_config.py -v
```

## Best Practices

1. **Provide Defaults**: Always have working default values
2. **Validate Early**: Validate config on load, not during use
3. **Clear Errors**: Provide helpful validation error messages
4. **Multiple Sources**: Support multiple config file locations
5. **Merge Strategy**: Clear precedence for config merging
6. **Type Safety**: Use type hints and validation
7. **Documentation**: Document all configuration options
8. **Security**: Never commit secrets to version control

## Troubleshooting

### Issue: Config file not found
**Solution**: Check CONFIG_LOCATIONS list and file permissions

### Issue: YAML parsing errors
**Solution**: Validate YAML syntax with `yamllint`

### Issue: Type conversion issues
**Solution**: Add explicit type hints and use Pydantic for validation

### Issue: Merged configs unexpected
**Solution**: Test merge strategy with unit tests

## Next Steps

- **Commands**: See `how-to-add-cli-command.md` for using config in commands
- **Packaging**: See `how-to-package-cli-tool.md` for distributing with configs
- **Architecture**: See `.ai/docs/python-cli-architecture.md` for patterns

## References

- [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [JSON Schema](https://json-schema.org/)
- [Python ConfigParser](https://docs.python.org/3/library/configparser.html)
