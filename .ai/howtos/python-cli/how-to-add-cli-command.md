# How to Add CLI Commands

**Purpose**: Step-by-step guide for adding new commands to Python CLI applications using Click framework

**Scope**: Command creation, options, arguments, groups, and testing

**Overview**: This guide demonstrates how to add new commands to your CLI application using Click decorators.
    It covers simple commands, command groups, options and arguments, error handling, and testing. Examples
    show Click best practices including type validation, help text, and context management for professional
    command-line interfaces.

**Prerequisites**: Python CLI application installed, basic Python knowledge, familiarity with decorators

**Related**: .ai/docs/python-cli-architecture.md, .ai/templates/python-cli/cli-entrypoint.py.template

---

## Overview

Adding commands to your CLI involves:
1. Defining command function with Click decorators
2. Adding options and arguments
3. Implementing command logic
4. Adding error handling
5. Writing tests
6. Updating documentation

## Simple Command

### Step 1: Add Basic Command

Edit `src/cli.py` and add a new command:

```python
@cli.command()
def status():
    """Display application status."""
    click.echo("Application is running")
    click.echo("Version: 1.0.0")
```

### Step 2: Test the Command

```bash
# View help
python -m src.cli status --help

# Run command
python -m src.cli status
```

**Output**:
```
Application is running
Version: 1.0.0
```

## Command with Options

### Step 1: Add Options

Options are optional flags that modify command behavior:

```python
@cli.command()
@click.option('--name', '-n', default='World', help='Name to greet')
@click.option('--uppercase', '-u', is_flag=True, help='Convert to uppercase')
def greet(name, uppercase):
    """Greet someone with optional formatting."""
    greeting = f"Hello, {name}!"

    if uppercase:
        greeting = greeting.upper()

    click.echo(greeting)
```

### Step 2: Test with Options

```bash
# Default behavior
python -m src.cli greet
# Output: Hello, World!

# With name option
python -m src.cli greet --name Alice
# Output: Hello, Alice!

# With short form
python -m src.cli greet -n Bob
# Output: Hello, Bob!

# With uppercase flag
python -m src.cli greet --name Charlie --uppercase
# Output: HELLO, CHARLIE!

# Short form combined
python -m src.cli greet -n Dave -u
# Output: HELLO, DAVE!
```

## Command with Arguments

### Step 1: Add Required Arguments

Arguments are positional parameters (required by default):

```python
@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--format', '-f', type=click.Choice(['json', 'yaml', 'text']), default='text')
def convert(input_file, output_file, format):
    """Convert INPUT_FILE to OUTPUT_FILE in specified format."""
    click.echo(f"Converting {input_file} to {output_file}")
    click.echo(f"Output format: {format}")

    # Your conversion logic here
    with open(input_file, 'r') as infile:
        content = infile.read()

    # Process content based on format
    # ... conversion logic ...

    with open(output_file, 'w') as outfile:
        outfile.write(content)

    click.echo("Conversion complete!")
```

### Step 2: Test with Arguments

```bash
# Create test file
echo "test content" > input.txt

# Run conversion
python -m src.cli convert input.txt output.txt --format json

# Output:
# Converting input.txt to output.txt
# Output format: json
# Conversion complete!
```

## Command Groups

### Step 1: Create Command Group

Organize related commands into groups:

```python
@cli.group()
def database():
    """Database management commands."""
    pass

@database.command('init')
@click.option('--path', type=click.Path(), default='./data.db')
def database_init(path):
    """Initialize a new database."""
    click.echo(f"Initializing database at {path}")
    # Database initialization logic
    click.echo("Database initialized successfully!")

@database.command('backup')
@click.argument('destination', type=click.Path())
def database_backup(destination):
    """Backup database to DESTINATION."""
    click.echo(f"Backing up database to {destination}")
    # Backup logic
    click.echo("Backup complete!")

@database.command('restore')
@click.argument('source', type=click.Path(exists=True))
def database_restore(source):
    """Restore database from SOURCE."""
    click.echo(f"Restoring database from {source}")
    # Restore logic
    click.echo("Restore complete!")
```

### Step 2: Test Command Group

```bash
# View group help
python -m src.cli database --help

# Output:
# Usage: cli database [OPTIONS] COMMAND [ARGS]...
#
# Database management commands.
#
# Commands:
#   backup   Backup database to DESTINATION.
#   init     Initialize a new database.
#   restore  Restore database from SOURCE.

# Run subcommands
python -m src.cli database init
python -m src.cli database backup backup.db
python -m src.cli database restore backup.db
```

## Advanced Options

### Multiple Values

Accept multiple values for an option:

```python
@cli.command()
@click.option('--tag', '-t', multiple=True, help='Tags to add')
@click.argument('filename')
def tag_file(filename, tag):
    """Add tags to a file."""
    click.echo(f"Tagging {filename} with: {', '.join(tag)}")
```

**Usage**:
```bash
python -m src.cli tag-file document.txt -t important -t urgent -t review
# Output: Tagging document.txt with: important, urgent, review
```

### Prompts for Input

Prompt user for input if option not provided:

```python
@cli.command()
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def login(password):
    """Login with password."""
    click.echo("Login successful!")
```

**Usage**:
```bash
python -m src.cli login
# Password:
# Repeat for confirmation:
# Login successful!
```

### Environment Variables

Read options from environment variables:

```python
@cli.command()
@click.option('--api-key', envvar='API_KEY', required=True, help='API key from env')
def api_call(api_key):
    """Make API call with key."""
    click.echo(f"Using API key: {api_key[:4]}...")
```

**Usage**:
```bash
export API_KEY="secret-key-12345"
python -m src.cli api-call
# Output: Using API key: secr...
```

## Using Click Context

### Step 1: Set Up Context

Share data between commands using Click context:

```python
@cli.group()
@click.option('--config', type=click.Path(), default='config.yaml')
@click.pass_context
def app(ctx, config):
    """Main application with shared config."""
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Load and store config in context
    ctx.obj['config'] = load_config(config)
    ctx.obj['started_at'] = datetime.now()

@app.command()
@click.pass_context
def info(ctx):
    """Display application info."""
    config = ctx.obj['config']
    started = ctx.obj['started_at']

    click.echo(f"Config loaded from: {config.get('path', 'default')}")
    click.echo(f"Started at: {started}")
```

### Step 2: Test Context Passing

```bash
python -m src.cli app --config myconfig.yaml info
```

## Error Handling

### Step 1: Add Error Handling

Handle errors gracefully with informative messages:

```python
@cli.command()
@click.argument('filename', type=click.Path(exists=True))
def process_file(filename):
    """Process a file."""
    try:
        with open(filename, 'r') as f:
            content = f.read()

        # Processing logic
        if not content.strip():
            raise click.ClickException("File is empty")

        # Process content
        result = process_content(content)

        click.echo("File processed successfully!")
        click.echo(f"Result: {result}")

    except PermissionError:
        raise click.ClickException(f"Permission denied: {filename}")
    except UnicodeDecodeError:
        raise click.ClickException(f"Invalid file encoding: {filename}")
    except Exception as e:
        raise click.ClickException(f"Processing failed: {str(e)}")
```

### Custom Exit Codes

Use different exit codes for different errors:

```python
@cli.command()
def validate():
    """Validate application state."""
    try:
        # Validation logic
        if not config_valid:
            click.echo("Configuration is invalid", err=True)
            raise click.Abort()

        if not data_exists:
            click.echo("Required data not found", err=True)
            ctx.exit(2)  # Custom exit code

        click.echo("Validation passed!")

    except Exception as e:
        click.echo(f"Validation failed: {e}", err=True)
        ctx.exit(1)
```

## Testing Commands

### Step 1: Write Command Tests

Create tests in `tests/test_cli.py`:

```python
from click.testing import CliRunner
import pytest
from src.cli import cli

@pytest.fixture
def runner():
    """Provide Click test runner."""
    return CliRunner()

def test_greet_default(runner):
    """Test greet command with default name."""
    result = runner.invoke(cli, ['greet'])
    assert result.exit_code == 0
    assert 'Hello, World!' in result.output

def test_greet_with_name(runner):
    """Test greet command with custom name."""
    result = runner.invoke(cli, ['greet', '--name', 'Alice'])
    assert result.exit_code == 0
    assert 'Hello, Alice!' in result.output

def test_greet_uppercase(runner):
    """Test greet command with uppercase flag."""
    result = runner.invoke(cli, ['greet', '-n', 'Bob', '-u'])
    assert result.exit_code == 0
    assert 'HELLO, BOB!' in result.output

def test_convert_command(runner, tmp_path):
    """Test convert command with temp files."""
    # Create input file
    input_file = tmp_path / "input.txt"
    input_file.write_text("test content")

    output_file = tmp_path / "output.txt"

    # Run command
    result = runner.invoke(cli, [
        'convert',
        str(input_file),
        str(output_file),
        '--format', 'json'
    ])

    assert result.exit_code == 0
    assert 'Conversion complete!' in result.output
    assert output_file.exists()

def test_database_init(runner, tmp_path):
    """Test database init command."""
    db_path = tmp_path / "test.db"

    result = runner.invoke(cli, [
        'database', 'init',
        '--path', str(db_path)
    ])

    assert result.exit_code == 0
    assert 'initialized successfully' in result.output

def test_error_handling(runner):
    """Test command error handling."""
    result = runner.invoke(cli, ['process-file', 'nonexistent.txt'])
    assert result.exit_code != 0
    assert 'Error' in result.output or 'does not exist' in result.output
```

### Step 2: Run Tests

```bash
# Run all CLI tests
pytest tests/test_cli.py -v

# Run specific test
pytest tests/test_cli.py::test_greet_with_name -v

# Run with coverage
pytest tests/test_cli.py --cov=src.cli
```

## Command Documentation

### Step 1: Write Good Help Text

Provide comprehensive help for commands:

```python
@cli.command()
@click.argument('source', type=click.Path(exists=True))
@click.argument('destination', type=click.Path())
@click.option('--overwrite', is_flag=True, help='Overwrite destination if exists')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed progress')
def copy(source, destination, overwrite, verbose):
    """
    Copy SOURCE file to DESTINATION.

    This command copies a file from SOURCE to DESTINATION with optional
    overwrite protection. Use --verbose for detailed progress information.

    Examples:

        \b
        # Simple copy
        cli copy file.txt backup.txt

        \b
        # Copy with overwrite
        cli copy file.txt backup.txt --overwrite

        \b
        # Copy with verbose output
        cli copy file.txt backup.txt -v
    """
    if verbose:
        click.echo(f"Copying {source} to {destination}...")

    # Copy logic here

    if verbose:
        click.echo("Copy complete!")
```

**Note**: Use `\b` to prevent Click from reformatting code blocks in help text.

### Step 2: View Help

```bash
python -m src.cli copy --help
```

## Best Practices

### 1. Command Naming

- Use lowercase with hyphens: `process-data` not `processData`
- Be descriptive but concise: `backup` not `b`
- Group related commands: `database init`, `database backup`

### 2. Options and Arguments

- Use short forms for common options: `-v` for `--verbose`
- Make arguments positional and required
- Make options optional with sensible defaults
- Use type validation: `type=click.Path()`, `type=click.Choice(['a', 'b'])`

### 3. Help Text

- Write clear, concise descriptions
- Include usage examples
- Document all options and arguments
- Use `\b` to preserve formatting in examples

### 4. Error Handling

- Validate inputs early
- Provide informative error messages
- Use appropriate exit codes
- Don't expose stack traces to users (unless --debug)

### 5. Testing

- Test all commands
- Test with various option combinations
- Test error conditions
- Use fixtures for test data

## Common Patterns

### Confirmation Prompts

```python
@cli.command()
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
def delete_all(yes):
    """Delete all data."""
    if not yes:
        click.confirm('This will delete all data. Continue?', abort=True)

    click.echo("Deleting all data...")
    # Deletion logic
```

### Progress Bars

```python
import time

@cli.command()
@click.option('--count', type=int, default=100)
def process_items(count):
    """Process multiple items with progress."""
    with click.progressbar(range(count), label='Processing items') as bar:
        for item in bar:
            # Process item
            time.sleep(0.01)

    click.echo("Processing complete!")
```

### Colored Output

```python
@cli.command()
def status():
    """Display colored status."""
    click.secho("Success!", fg='green', bold=True)
    click.secho("Warning!", fg='yellow')
    click.secho("Error!", fg='red', bold=True)
```

## Troubleshooting

### Issue: Command not found
**Solution**: Ensure command is decorated with `@cli.command()` or added to a group

### Issue: Options not working
**Solution**: Check decorator order - options should be above the function definition

### Issue: Tests failing
**Solution**: Use `CliRunner` and invoke commands in isolated mode

### Issue: Help text not formatting correctly
**Solution**: Use `\b` to preserve formatting in docstrings

## Next Steps

- **Configuration**: See `how-to-handle-config-files.md` for config management
- **Packaging**: See `how-to-package-cli-tool.md` for distribution
- **Architecture**: See `.ai/docs/python-cli-architecture.md` for design patterns

## References

- [Click Documentation](https://click.palletsprojects.com/)
- [Click Testing](https://click.palletsprojects.com/en/8.1.x/testing/)
- [Click Options](https://click.palletsprojects.com/en/8.1.x/options/)
- [Click Arguments](https://click.palletsprojects.com/en/8.1.x/arguments/)
