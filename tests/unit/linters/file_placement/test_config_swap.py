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
