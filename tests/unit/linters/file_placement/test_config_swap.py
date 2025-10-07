"""
Purpose: Test configuration swap behavior for file placement linter validation

Scope: Validates that the file placement linter is truly configuration-driven by swapping rules

Overview: Comprehensive test suite that validates the file placement linter responds dynamically
    to configuration changes. Tests create temporary directory structures with multiple file types,
    apply initial configuration rules that identify specific violations, then swap the configuration
    to reverse which files are considered valid vs invalid. This ensures the linter is not relying
    on hardcoded logic but is fully driven by configuration rules. Validates both allow and deny
    patterns work bidirectionally and that violation messages accurately reflect current config.

Dependencies: pytest (testing framework), pathlib (file operations), tmp_path fixture, FilePlacementLinter

Exports: TestConfigurationSwap test class with comprehensive bidirectional validation tests

Interfaces: Tests FilePlacementLinter with dynamic config loading via config_obj parameter

Implementation: Uses pytest fixtures for temporary directories, creates real file structures with
    multiple file types, applies YAML-style config dictionaries, validates violation detection
    before and after config swaps, ensures violation messages match current configuration
"""


class TestConfigurationSwap:
    """Test that linter behavior changes when configuration is swapped."""

    def test_config_swap_reverses_violations(self, tmp_path):
        """
        Comprehensive test validating all 6 criteria:
        1. Create temp directory structure
        2. Create mock YAML config
        3. Populate with empty files (some belong, some don't)
        4. Verify non-belonging files identified
        5. Swap config (belonging now violate, violations now belong)
        6. Verify results match new config
        """
        from src.linters.file_placement import FilePlacementLinter

        # STEP 1: Create temporary directory structure
        src_dir = tmp_path / "src"
        tests_dir = tmp_path / "tests"
        docs_dir = tmp_path / "docs"
        src_dir.mkdir()
        tests_dir.mkdir()
        docs_dir.mkdir()

        # STEP 2 & 3: Create initial config and files
        # Initial config: Python files only in src/, markdown only in docs/
        # Need to set project_root so linter can create relative paths correctly
        initial_config = {
            "file-placement": {
                "directories": {
                    "src/": {"allow": [r".*\.py$"]},  # Pattern without ^src/ prefix
                    "docs/": {"allow": [r".*\.md$"]},  # Pattern without ^docs/ prefix
                }
            }
        }

        # Create test files
        # Files that SHOULD belong with initial config
        src_main = src_dir / "main.py"
        src_main.write_text("# Python file in src/")

        docs_guide = docs_dir / "guide.md"
        docs_guide.write_text("# Markdown in docs/")

        # Files that SHOULD violate initial config
        src_readme = src_dir / "README.md"  # Markdown in src/ (not allowed)
        src_readme.write_text("# Markdown in wrong place")

        docs_utils = docs_dir / "utils.py"  # Python in docs/ (not allowed)
        docs_utils.write_text("# Python in wrong place")

        # STEP 4: Verify non-belonging files are identified with initial config
        # Set project_root so paths are relative to tmp_path
        linter = FilePlacementLinter(config_obj=initial_config, project_root=tmp_path)

        # Check files that SHOULD be allowed
        violations_main = linter.lint_path(src_main)
        violations_guide = linter.lint_path(docs_guide)
        assert len(violations_main) == 0, "src/main.py should be allowed with initial config"
        assert len(violations_guide) == 0, "docs/guide.md should be allowed with initial config"

        # Check files that SHOULD violate
        violations_readme = linter.lint_path(src_readme)
        violations_utils = linter.lint_path(docs_utils)
        assert len(violations_readme) > 0, (
            "src/README.md should violate initial config (markdown not allowed in src/)"
        )
        assert len(violations_utils) > 0, (
            "docs/utils.py should violate initial config (python not allowed in docs/)"
        )

        # Verify violation messages reference the correct patterns
        assert "does not match allowed patterns" in violations_readme[0].message.lower()
        assert "does not match allowed patterns" in violations_utils[0].message.lower()

        # STEP 5: SWAP CONFIG - reverse the rules
        # New config: Python files only in docs/, markdown only in src/
        swapped_config = {
            "file-placement": {
                "directories": {
                    "src/": {"allow": [r".*\.md$"]},  # Now MARKDOWN in src/
                    "docs/": {"allow": [r".*\.py$"]},  # Now PYTHON in docs/
                }
            }
        }

        # Create NEW linter instance with swapped config and same project_root
        linter_swapped = FilePlacementLinter(config_obj=swapped_config, project_root=tmp_path)

        # STEP 6: Verify results match NEW config (violations reversed)

        # Files that were ALLOWED should now VIOLATE
        violations_main_swapped = linter_swapped.lint_path(src_main)
        violations_guide_swapped = linter_swapped.lint_path(docs_guide)
        assert len(violations_main_swapped) > 0, (
            "src/main.py should NOW violate (python no longer allowed in src/)"
        )
        assert len(violations_guide_swapped) > 0, (
            "docs/guide.md should NOW violate (markdown no longer allowed in docs/)"
        )

        # Files that were VIOLATING should now be ALLOWED
        violations_readme_swapped = linter_swapped.lint_path(src_readme)
        violations_utils_swapped = linter_swapped.lint_path(docs_utils)
        assert len(violations_readme_swapped) == 0, (
            "src/README.md should NOW be allowed (markdown now allowed in src/)"
        )
        assert len(violations_utils_swapped) == 0, (
            "docs/utils.py should NOW be allowed (python now allowed in docs/)"
        )

        # Verify new violation messages reference the NEW patterns
        assert "does not match allowed patterns" in violations_main_swapped[0].message.lower()
        assert "does not match allowed patterns" in violations_guide_swapped[0].message.lower()

    def test_config_swap_with_deny_patterns(self, tmp_path):
        """Test config swap works with deny patterns (not just allow)."""
        from src.linters.file_placement import FilePlacementLinter

        # Create directory structure
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Create test files
        test_file = src_dir / "test_module.py"
        test_file.write_text("# Test file")

        debug_file = src_dir / "debug_utils.py"
        debug_file.write_text("# Debug file")

        # Initial config: Deny test files in src/
        initial_config = {
            "file-placement": {
                "directories": {
                    "src/": {
                        "allow": [r".*\.py$"],  # All Python files allowed
                        "deny": [{"pattern": r".*test.*", "reason": "No test files in src/"}],
                    }
                }
            }
        }

        linter = FilePlacementLinter(config_obj=initial_config, project_root=tmp_path)

        # test_module.py should violate (denied)
        violations_test = linter.lint_path(test_file)
        assert len(violations_test) > 0
        assert "test" in violations_test[0].message.lower()

        # debug_utils.py should be allowed
        violations_debug = linter.lint_path(debug_file)
        assert len(violations_debug) == 0

        # SWAP CONFIG: Now deny debug files instead
        swapped_config = {
            "file-placement": {
                "directories": {
                    "src/": {
                        "allow": [r".*\.py$"],  # All Python files allowed
                        "deny": [{"pattern": r".*debug.*", "reason": "No debug files in src/"}],
                    }
                }
            }
        }

        linter_swapped = FilePlacementLinter(config_obj=swapped_config, project_root=tmp_path)

        # test_module.py should NOW be allowed
        violations_test_swapped = linter_swapped.lint_path(test_file)
        assert len(violations_test_swapped) == 0

        # debug_utils.py should NOW violate
        violations_debug_swapped = linter_swapped.lint_path(debug_file)
        assert len(violations_debug_swapped) > 0
        assert "debug" in violations_debug_swapped[0].message.lower()

    def test_config_swap_with_global_patterns(self, tmp_path):
        """Test config swap works with global patterns."""
        from src.linters.file_placement import FilePlacementLinter

        # Create files at different levels
        root_file = tmp_path / "config.yaml"
        root_file.write_text("config: value")

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        src_file = src_dir / "main.py"
        src_file.write_text("# Python")

        # Initial config: Allow YAML files anywhere, deny Python anywhere
        initial_config = {
            "file-placement": {
                "global_patterns": {
                    "allow": [r".*\.yaml$"],
                    "deny": [{"pattern": r".*\.py$", "reason": "No Python files"}],
                }
            }
        }

        linter = FilePlacementLinter(config_obj=initial_config)

        # config.yaml should be allowed
        violations_yaml = linter.lint_path(root_file)
        assert len(violations_yaml) == 0

        # main.py should violate
        violations_py = linter.lint_path(src_file)
        assert len(violations_py) > 0

        # SWAP CONFIG: Allow Python anywhere, deny YAML anywhere
        swapped_config = {
            "file-placement": {
                "global_patterns": {
                    "allow": [r".*\.py$"],
                    "deny": [{"pattern": r".*\.yaml$", "reason": "No YAML files"}],
                }
            }
        }

        linter_swapped = FilePlacementLinter(config_obj=swapped_config)

        # config.yaml should NOW violate
        violations_yaml_swapped = linter_swapped.lint_path(root_file)
        assert len(violations_yaml_swapped) > 0

        # main.py should NOW be allowed
        violations_py_swapped = linter_swapped.lint_path(src_file)
        assert len(violations_py_swapped) == 0

    def test_multiple_config_swaps(self, tmp_path):
        """Test multiple sequential config swaps work correctly."""
        from src.linters.file_placement import FilePlacementLinter

        src_dir = tmp_path / "src"
        src_dir.mkdir()

        test_file = src_dir / "module.py"
        test_file.write_text("# Module")

        # Config 1: Allow all Python
        config1 = {"file-placement": {"directories": {"src/": {"allow": [r"^src/.*\.py$"]}}}}
        linter1 = FilePlacementLinter(config_obj=config1)
        assert len(linter1.lint_path(test_file)) == 0

        # Config 2: Deny all files
        config2 = {"file-placement": {"global_deny": [{"pattern": r".*", "reason": "Deny all"}]}}
        linter2 = FilePlacementLinter(config_obj=config2)
        assert len(linter2.lint_path(test_file)) > 0

        # Config 3: Allow again
        config3 = {"file-placement": {"global_patterns": {"allow": [r".*"]}}}
        linter3 = FilePlacementLinter(config_obj=config3)
        assert len(linter3.lint_path(test_file)) == 0

        # Verify each config produces different results
        # This proves the linter adapts to each configuration independently

    def test_single_file_lint_without_directory_scan(self, tmp_path):
        """
        Test pre-commit hook scenario: lint a single file without scanning directory.

        This validates that the linter can detect violations for individual files
        by looking at the directory path the file is in, without needing to scan
        all files in that directory. This is critical for pre-commit hooks that
        only pass changed files to the linter.
        """
        from src.linters.file_placement import FilePlacementLinter

        # Create directory structure but DON'T scan it
        src_dir = tmp_path / "src"
        docs_dir = tmp_path / "docs"
        src_dir.mkdir()
        docs_dir.mkdir()

        # Create multiple files, but we'll only lint ONE
        src_main = src_dir / "main.py"
        src_main.write_text("# Belongs here")

        src_readme = src_dir / "README.md"
        src_readme.write_text("# Does NOT belong here")

        docs_guide = docs_dir / "guide.md"
        docs_guide.write_text("# Belongs here")

        # Config: Python only in src/, Markdown only in docs/
        config = {
            "file-placement": {
                "directories": {
                    "src/": {"allow": [r".*\.py$"]},
                    "docs/": {"allow": [r".*\.md$"]},
                }
            }
        }

        linter = FilePlacementLinter(config_obj=config, project_root=tmp_path)

        # PRE-COMMIT SCENARIO: Only lint the single file that was changed
        # The linter should be smart enough to:
        # 1. Look at the file path (src/README.md)
        # 2. Match it to the directory rule (src/)
        # 3. Check if .md files are allowed in src/ (they're not)
        # 4. Report violation - WITHOUT scanning other files

        violations = linter.lint_path(src_readme)

        # Should detect violation for README.md in src/
        assert len(violations) > 0, "Should detect README.md doesn't belong in src/"
        assert "does not match allowed patterns" in violations[0].message.lower()
        assert "src/" in violations[0].message or "src" in violations[0].file_path

        # Verify it correctly allows a file that DOES belong
        violations_main = linter.lint_path(src_main)
        assert len(violations_main) == 0, "Should allow main.py in src/"

        # Verify it works for docs/ directory too
        violations_guide = linter.lint_path(docs_guide)
        assert len(violations_guide) == 0, "Should allow guide.md in docs/"

        # Now test the opposite: try to add a Python file to docs/
        docs_utils = docs_dir / "utils.py"
        docs_utils.write_text("# Does NOT belong here")

        violations_utils = linter.lint_path(docs_utils)
        assert len(violations_utils) > 0, "Should detect utils.py doesn't belong in docs/"
        assert "does not match allowed patterns" in violations_utils[0].message.lower()
