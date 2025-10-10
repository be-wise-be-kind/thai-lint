"""
Purpose: Tests for DRY linter minimum occurrences configuration

Scope: Language-specific minimum occurrence thresholds for duplicate code detection

Overview: Test suite for configurable minimum occurrences of duplicate code blocks.
    By default, DRY linter reports duplicates when code appears 2+ times. The min_occurrences
    setting allows requiring code to appear N times before reporting (e.g., 3 occurrences
    means code must appear in 3 different locations). This is useful for reducing noise
    from pairs of duplicates that may be acceptable. Supports language-specific thresholds
    (python, typescript, javascript) to account for different code patterns and team preferences.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: Test functions for min_occurrences configuration

Interfaces: Uses Linter class with config file

Implementation: TDD approach - tests written before implementation. Tests use cache_enabled: false
    for isolation. Validates that duplicates are only reported when occurrence count meets
    or exceeds the configured threshold.
"""
