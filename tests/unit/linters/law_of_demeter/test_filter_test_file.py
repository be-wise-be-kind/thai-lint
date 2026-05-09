"""
Purpose: Test test-file detection for Law of Demeter linter

Scope: Filtering chains in test files via linter-level _is_test_filepath

Overview: Validates the test file detection that skips test files when
    check_test_files is false (default). Test code commonly has deep assertion
    chains and mock setup chains that aren't actionable LoD violations.
    Test file detection is handled at the linter level (not the classifier)
    to respect the check_test_files configuration option.

Dependencies: pytest, src.linters.law_of_demeter.linter

Exports: TestTestFileFilter (5 tests)

Interfaces: Tests _is_test_filepath() for file path patterns

Implementation: Calls _is_test_filepath() with various paths,
    verifies correct detection of test files by filename and directory
"""

from src.linters.law_of_demeter.linter import _is_test_filepath


class TestTestFileFilter:
    """Test test-file detection at linter level."""

    def test_test_prefix_file(self) -> None:
        """Files named test_*.py should be detected as test files."""
        assert _is_test_filepath("test_api.py") is True

    def test_tests_directory(self) -> None:
        """Files in tests/ directory should be detected as test files."""
        assert _is_test_filepath("tests/test_service.py") is True

    def test_conftest_file(self) -> None:
        """conftest.py should be detected as a test file."""
        assert _is_test_filepath("conftest.py") is True

    def test_test_suffix_file(self) -> None:
        """Files named *_test.py should be detected as test files."""
        assert _is_test_filepath("api_test.py") is True

    def test_non_test_file_not_filtered(self) -> None:
        """Regular files should not be detected as test files."""
        assert _is_test_filepath("app.py") is False

    def test_singular_test_directory(self) -> None:
        """Files in test/ (singular) directory should be detected."""
        assert _is_test_filepath("test/service.py") is True

    def test_nested_singular_test_directory(self) -> None:
        """Files deep in a test/ directory should be detected."""
        assert _is_test_filepath("src/project/test/utils/helper.py") is True

    def test_fixtures_directory(self) -> None:
        """Files in fixtures/ directory should be detected."""
        assert _is_test_filepath("tests/fixtures/broken_syntax.py") is True

    def test_test_data_directory(self) -> None:
        """Files in test_data/ directory should be detected."""
        assert _is_test_filepath("test_data/sample.py") is True

    def test_testdata_directory(self) -> None:
        """Files in testdata/ directory should be detected."""
        assert _is_test_filepath("testdata/sample.py") is True

    def test_pytest_tmp_path_not_detected(self) -> None:
        """Files in pytest tmp directories should not be false-positived."""
        # pytest creates dirs like /tmp/pytest-of-user/pytest-NN/test_name0/
        assert _is_test_filepath("/tmp/pytest-of-user/pytest-1/test_foo0/bad.py") is False
