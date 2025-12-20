"""
Purpose: Provides pytest configuration and reusable test fixtures

Scope: Project-wide pytest configuration and shared test utilities

Overview: Defines shared pytest fixtures for creating mock project structures in tests.
    Provides make_project factory fixture for flexible project creation with configurable
    .git directories, .thailint.yaml configs, and file structures. Includes legacy fixtures
    for backward compatibility and cache clearing for singleton patterns. Serves as single
    source of truth for test project setup across all test suites.

Dependencies: pytest, pathlib, collections.abc for fixture creation, linter_config.ignore for cache

Exports: make_project factory fixture, mock_project_root fixture, mock_project_with_config fixture,
    clear_ignore_parser_cache autouse fixture

Interfaces: make_project(git, config_type, thailint_yaml, files) returns Path to project root

Implementation: Factory pattern for test project creation with preset configurations and custom YAML
"""

from collections.abc import Callable
from pathlib import Path

import pytest

from src.linter_config.ignore import clear_ignore_parser_cache


@pytest.fixture(autouse=True)
def _clear_caches():
    """Clear singleton caches before and after each test for isolation.

    This fixture runs automatically for every test to ensure that:
    1. Tests don't inherit cached state from previous tests
    2. Tests don't leak their cached state to subsequent tests

    The IgnoreDirectiveParser singleton is cleared to ensure each test
    gets a fresh parser instance with proper project root configuration.
    """
    clear_ignore_parser_cache()
    yield
    clear_ignore_parser_cache()


@pytest.fixture
def make_project(tmp_path) -> Callable:
    """Factory fixture to create customized project structures.

    This is a factory fixture that returns a function to create project structures
    with various configurations. Single source of truth for all folder structure setup.

    Args:
        tmp_path: Pytest's tmp_path fixture

    Returns:
        Callable: Function that creates and returns a project root Path

    Example - Basic project with .git:
        def test_something(make_project):
            project = make_project()
            # Has .git already

    Example - Project with deny-all config:
        def test_linting(make_project):
            project = make_project(config_type="deny_all_python")
            test_file = project / "test.py"
            test_file.write_text("...")

    Example - Project with custom config:
        def test_custom(make_project):
            project = make_project(
                thailint_yaml="file-placement:\\n  global_allow:\\n    - pattern: '.*\\\\.ts$'"
            )

    Example - Project with .thailint.yaml:
        def test_thailint_yaml(make_project):
            project = make_project(
                thailint_yaml="file-placement:\\n  global_allow:\\n    - pattern: '.*\\\\.py$'"
            )

    Example - Project with files:
        def test_with_files(make_project):
            project = make_project(
                files={
                    "src/test.py": "print('test')",
                    "src/nested/deep.py": "print('deep')"
                }
            )

    Example - Project without .git (testing non-git projects):
        def test_no_git(make_project):
            project = make_project(git=False)
    """

    def _create_project(
        git: bool = True,
        config_type: str | None = None,
        thailint_yaml: str | None = None,
        files: dict[str, str] | None = None,
    ) -> Path:
        """Create a project structure with specified configuration.

        Args:
            git: If True, create .git directory (default: True)
            config_type: Preset config type ("deny_all_python", "allow_all_python")
            thailint_yaml: Custom YAML content for .thailint.yaml
            files: Dict of {filepath: content} to create

        Returns:
            Path: Path to the project root directory

        Note:
            - config_type and thailint_yaml are mutually exclusive
            - Both create .thailint.yaml at project root
        """
        # Create .git marker if requested
        if git:
            (tmp_path / ".git").mkdir()

        # Handle config presets
        if config_type:
            if thailint_yaml:
                raise ValueError("Cannot specify both config_type and thailint_yaml")

            presets = {
                "deny_all_python": """file-placement:
  global_deny:
    - pattern: '.*\\.py$'
      reason: 'No Python files'
""",
                "allow_all_python": """file-placement:
  global_allow:
    - pattern: '.*\\.py$'
""",
            }

            if config_type not in presets:
                raise ValueError(
                    f"Unknown config_type: {config_type}. Choose from: {list(presets.keys())}"
                )

            thailint_yaml = presets[config_type]

        # Create .thailint.yaml if config specified
        if thailint_yaml:
            thailint_file = tmp_path / ".thailint.yaml"
            thailint_file.write_text(thailint_yaml)

        # Create files if specified
        if files:
            for filepath, content in files.items():
                file_path = tmp_path / filepath
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)

        return tmp_path

    return _create_project


# Backward compatibility: Keep old fixtures for tests that use them
@pytest.fixture
def mock_project_root(make_project):
    """Legacy fixture - use make_project() instead.

    Creates a mock project root with .git marker.
    Kept for backward compatibility with existing tests.
    """
    return make_project(git=True)


@pytest.fixture
def mock_project_with_config(make_project):
    """Legacy fixture - use make_project(config_type='deny_all_python') instead.

    Creates a mock project root with .thailint.yaml.
    Kept for backward compatibility with existing tests.
    """
    project = make_project(git=True, config_type="deny_all_python")
    config_content = """file-placement:
  global_deny:
    - pattern: '.*\\.py$'
      reason: 'No Python files'
"""
    return project, config_content
