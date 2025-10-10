"""
Purpose: Test programmatic library API for nesting linter

Scope: Python API usage via Linter class and direct rule instantiation

Overview: Validates programmatic library API for the nesting depth linter enabling programmatic
    usage from Python code without CLI. Tests verify direct rule instantiation and checking,
    Linter class integration with rule filtering, violation object structure and metadata,
    custom configuration support through config files, and orchestrator integration. Ensures
    library API provides clean, Pythonic interface for embedding nesting depth checks in other
    tools, scripts, or CI/CD pipelines.

Dependencies: pytest for testing framework, src.linters.nesting.linter for NestingDepthRule,
    pathlib for Path handling, unittest.mock for Mock objects

Exports: TestNestingLibraryAPI (4 tests) covering direct usage, rule filtering, violation objects,
    and custom config

Interfaces: Tests NestingDepthRule class and integration with Linter API

Implementation: Creates rule instances directly, builds mock contexts, verifies violation
    detection and metadata structure
"""


class TestNestingLibraryAPI:
    """Test programmatic library API."""
