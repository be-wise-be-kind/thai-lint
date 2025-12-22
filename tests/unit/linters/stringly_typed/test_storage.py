"""
Purpose: Unit tests for stringly-typed pattern storage

Scope: Test SQLite storage operations for cross-file pattern detection

Overview: Tests the StringlyTypedStorage class that manages SQLite storage for
    stringly-typed pattern detection. Verifies pattern insertion, retrieval,
    duplicate hash detection, and storage lifecycle operations. Covers both
    memory and tempfile storage modes.

Dependencies: pytest, pathlib.Path, storage module

Exports: Test functions for storage validation

Interfaces: pytest test functions

Implementation: Unit tests with isolated storage instances per test
"""

from pathlib import Path

import pytest

from src.linters.stringly_typed.storage import StoredPattern, StringlyTypedStorage


@pytest.fixture
def storage() -> StringlyTypedStorage:
    """Create a fresh storage instance for each test."""
    store = StringlyTypedStorage(storage_mode="memory")
    yield store
    store.close()


@pytest.fixture
def sample_pattern() -> StoredPattern:
    """Create a sample pattern for testing."""
    return StoredPattern(
        file_path=Path("/test/module1.py"),
        line_number=10,
        column=4,
        variable_name="env",
        string_set_hash=hash(("production", "staging")),
        string_values=["production", "staging"],
        pattern_type="membership_validation",
        details="Membership validation on 'env' with 2 values",
    )


class TestStoredPatternDataclass:
    """Tests for StoredPattern dataclass."""

    def test_stored_pattern_creation(self) -> None:
        """Test creating a StoredPattern with all fields."""
        pattern = StoredPattern(
            file_path=Path("/test/file.py"),
            line_number=5,
            column=0,
            variable_name="status",
            string_set_hash=12345,
            string_values=["active", "inactive"],
            pattern_type="equality_chain",
            details="Equality chain with 2 values",
        )

        assert pattern.file_path == Path("/test/file.py")
        assert pattern.line_number == 5
        assert pattern.column == 0
        assert pattern.variable_name == "status"
        assert pattern.string_set_hash == 12345
        assert pattern.string_values == ["active", "inactive"]
        assert pattern.pattern_type == "equality_chain"
        assert pattern.details == "Equality chain with 2 values"

    def test_stored_pattern_with_none_variable(self) -> None:
        """Test pattern with None variable name."""
        pattern = StoredPattern(
            file_path=Path("/test/file.py"),
            line_number=5,
            column=0,
            variable_name=None,
            string_set_hash=12345,
            string_values=["a", "b"],
            pattern_type="membership_validation",
            details="Pattern details",
        )

        assert pattern.variable_name is None


class TestStringlyTypedStorageInit:
    """Tests for storage initialization."""

    def test_memory_mode_initialization(self) -> None:
        """Test storage initializes with memory mode."""
        store = StringlyTypedStorage(storage_mode="memory")
        assert store._storage_mode == "memory"
        store.close()

    def test_tempfile_mode_initialization(self) -> None:
        """Test storage initializes with tempfile mode."""
        store = StringlyTypedStorage(storage_mode="tempfile")
        assert store._storage_mode == "tempfile"
        assert store._tempfile is not None
        store.close()

    def test_invalid_mode_raises_error(self) -> None:
        """Test invalid storage mode raises ValueError."""
        with pytest.raises(ValueError, match="Invalid storage_mode"):
            StringlyTypedStorage(storage_mode="invalid")


class TestAddPattern:
    """Tests for adding patterns to storage."""

    def test_add_single_pattern(
        self, storage: StringlyTypedStorage, sample_pattern: StoredPattern
    ) -> None:
        """Test adding a single pattern."""
        storage.add_pattern(sample_pattern)

        patterns = storage.get_all_patterns()
        assert len(patterns) == 1
        assert patterns[0].file_path == sample_pattern.file_path
        assert patterns[0].line_number == sample_pattern.line_number

    def test_add_multiple_patterns_individually(self, storage: StringlyTypedStorage) -> None:
        """Test adding multiple patterns one at a time."""
        pattern1 = StoredPattern(
            file_path=Path("/test/file1.py"),
            line_number=10,
            column=0,
            variable_name="status",
            string_set_hash=111,
            string_values=["a", "b"],
            pattern_type="membership_validation",
            details="Details 1",
        )
        pattern2 = StoredPattern(
            file_path=Path("/test/file2.py"),
            line_number=20,
            column=4,
            variable_name="mode",
            string_set_hash=222,
            string_values=["x", "y"],
            pattern_type="equality_chain",
            details="Details 2",
        )

        storage.add_pattern(pattern1)
        storage.add_pattern(pattern2)

        patterns = storage.get_all_patterns()
        assert len(patterns) == 2

    def test_add_patterns_batch(self, storage: StringlyTypedStorage) -> None:
        """Test adding patterns in a batch."""
        patterns = [
            StoredPattern(
                file_path=Path(f"/test/file{i}.py"),
                line_number=i * 10,
                column=0,
                variable_name=f"var{i}",
                string_set_hash=i * 100,
                string_values=["a", "b"],
                pattern_type="membership_validation",
                details=f"Details {i}",
            )
            for i in range(5)
        ]

        storage.add_patterns(patterns)

        stored = storage.get_all_patterns()
        assert len(stored) == 5

    def test_add_empty_patterns_list(self, storage: StringlyTypedStorage) -> None:
        """Test adding empty list does nothing."""
        storage.add_patterns([])

        patterns = storage.get_all_patterns()
        assert len(patterns) == 0

    def test_replace_pattern_on_same_location(self, storage: StringlyTypedStorage) -> None:
        """Test pattern is replaced when same file/line/column."""
        pattern1 = StoredPattern(
            file_path=Path("/test/file.py"),
            line_number=10,
            column=0,
            variable_name="status",
            string_set_hash=111,
            string_values=["a", "b"],
            pattern_type="membership_validation",
            details="First pattern",
        )
        pattern2 = StoredPattern(
            file_path=Path("/test/file.py"),
            line_number=10,
            column=0,
            variable_name="status",
            string_set_hash=222,
            string_values=["x", "y", "z"],
            pattern_type="equality_chain",
            details="Replaced pattern",
        )

        storage.add_pattern(pattern1)
        storage.add_pattern(pattern2)

        patterns = storage.get_all_patterns()
        assert len(patterns) == 1
        assert patterns[0].details == "Replaced pattern"
        assert patterns[0].string_set_hash == 222


class TestGetDuplicateHashes:
    """Tests for finding duplicate hashes across files."""

    def test_no_duplicates_returns_empty(self, storage: StringlyTypedStorage) -> None:
        """Test empty storage returns no duplicates."""
        hashes = storage.get_duplicate_hashes()
        assert hashes == []

    def test_single_pattern_no_duplicate(
        self, storage: StringlyTypedStorage, sample_pattern: StoredPattern
    ) -> None:
        """Test single pattern is not considered duplicate."""
        storage.add_pattern(sample_pattern)

        hashes = storage.get_duplicate_hashes()
        assert hashes == []

    def test_same_hash_in_two_files_is_duplicate(self, storage: StringlyTypedStorage) -> None:
        """Test same hash in different files is flagged as duplicate."""
        common_hash = hash(("staging", "production"))
        pattern1 = StoredPattern(
            file_path=Path("/test/file1.py"),
            line_number=10,
            column=0,
            variable_name="env",
            string_set_hash=common_hash,
            string_values=["production", "staging"],
            pattern_type="membership_validation",
            details="Pattern in file 1",
        )
        pattern2 = StoredPattern(
            file_path=Path("/test/file2.py"),
            line_number=20,
            column=0,
            variable_name="environment",
            string_set_hash=common_hash,
            string_values=["production", "staging"],
            pattern_type="membership_validation",
            details="Pattern in file 2",
        )

        storage.add_patterns([pattern1, pattern2])

        hashes = storage.get_duplicate_hashes()
        assert len(hashes) == 1
        assert common_hash in hashes

    def test_same_hash_same_file_not_duplicate(self, storage: StringlyTypedStorage) -> None:
        """Test same hash in same file on different lines is not a cross-file duplicate."""
        common_hash = hash(("a", "b"))
        pattern1 = StoredPattern(
            file_path=Path("/test/file1.py"),
            line_number=10,
            column=0,
            variable_name="x",
            string_set_hash=common_hash,
            string_values=["a", "b"],
            pattern_type="membership_validation",
            details="First pattern",
        )
        pattern2 = StoredPattern(
            file_path=Path("/test/file1.py"),
            line_number=20,
            column=0,
            variable_name="y",
            string_set_hash=common_hash,
            string_values=["a", "b"],
            pattern_type="membership_validation",
            details="Second pattern",
        )

        storage.add_patterns([pattern1, pattern2])

        # Both patterns are in same file, so not a cross-file duplicate
        hashes = storage.get_duplicate_hashes(min_files=2)
        assert hashes == []

    def test_min_files_threshold(self, storage: StringlyTypedStorage) -> None:
        """Test min_files parameter filters correctly."""
        common_hash = 12345
        patterns = [
            StoredPattern(
                file_path=Path(f"/test/file{i}.py"),
                line_number=10,
                column=0,
                variable_name="x",
                string_set_hash=common_hash,
                string_values=["a", "b"],
                pattern_type="membership_validation",
                details=f"Pattern {i}",
            )
            for i in range(2)  # Only 2 files
        ]

        storage.add_patterns(patterns)

        # With min_files=3, should not be considered duplicate
        assert storage.get_duplicate_hashes(min_files=3) == []

        # With min_files=2, should be considered duplicate
        assert storage.get_duplicate_hashes(min_files=2) == [common_hash]


class TestGetPatternsByHash:
    """Tests for retrieving patterns by hash value."""

    def test_get_patterns_no_matches(self, storage: StringlyTypedStorage) -> None:
        """Test getting patterns with non-existent hash."""
        patterns = storage.get_patterns_by_hash(99999)
        assert patterns == []

    def test_get_patterns_single_match(
        self, storage: StringlyTypedStorage, sample_pattern: StoredPattern
    ) -> None:
        """Test getting patterns with single match."""
        storage.add_pattern(sample_pattern)

        patterns = storage.get_patterns_by_hash(sample_pattern.string_set_hash)
        assert len(patterns) == 1
        assert patterns[0].file_path == sample_pattern.file_path

    def test_get_patterns_multiple_matches(self, storage: StringlyTypedStorage) -> None:
        """Test getting patterns with multiple matches."""
        common_hash = 12345
        pattern1 = StoredPattern(
            file_path=Path("/test/file1.py"),
            line_number=10,
            column=0,
            variable_name="x",
            string_set_hash=common_hash,
            string_values=["a", "b"],
            pattern_type="membership_validation",
            details="Pattern 1",
        )
        pattern2 = StoredPattern(
            file_path=Path("/test/file2.py"),
            line_number=20,
            column=0,
            variable_name="y",
            string_set_hash=common_hash,
            string_values=["a", "b"],
            pattern_type="equality_chain",
            details="Pattern 2",
        )

        storage.add_patterns([pattern1, pattern2])

        patterns = storage.get_patterns_by_hash(common_hash)
        assert len(patterns) == 2

    def test_patterns_ordered_by_file_and_line(self, storage: StringlyTypedStorage) -> None:
        """Test patterns are returned ordered by file path and line number."""
        common_hash = 12345
        patterns_to_add = [
            StoredPattern(
                file_path=Path("/test/z_file.py"),
                line_number=30,
                column=0,
                variable_name="x",
                string_set_hash=common_hash,
                string_values=["a", "b"],
                pattern_type="membership_validation",
                details="Last",
            ),
            StoredPattern(
                file_path=Path("/test/a_file.py"),
                line_number=10,
                column=0,
                variable_name="x",
                string_set_hash=common_hash,
                string_values=["a", "b"],
                pattern_type="membership_validation",
                details="First",
            ),
            StoredPattern(
                file_path=Path("/test/a_file.py"),
                line_number=5,
                column=0,
                variable_name="x",
                string_set_hash=common_hash,
                string_values=["a", "b"],
                pattern_type="membership_validation",
                details="Actually first",
            ),
        ]

        storage.add_patterns(patterns_to_add)

        patterns = storage.get_patterns_by_hash(common_hash)
        assert len(patterns) == 3
        assert patterns[0].details == "Actually first"
        assert patterns[1].details == "First"
        assert patterns[2].details == "Last"


class TestClearAndClose:
    """Tests for storage cleanup operations."""

    def test_clear_removes_all_patterns(
        self, storage: StringlyTypedStorage, sample_pattern: StoredPattern
    ) -> None:
        """Test clear removes all stored patterns."""
        storage.add_pattern(sample_pattern)
        assert len(storage.get_all_patterns()) == 1

        storage.clear()

        assert len(storage.get_all_patterns()) == 0

    def test_clear_allows_reuse(
        self, storage: StringlyTypedStorage, sample_pattern: StoredPattern
    ) -> None:
        """Test storage can be reused after clear."""
        storage.add_pattern(sample_pattern)
        storage.clear()

        # Add new pattern after clear
        new_pattern = StoredPattern(
            file_path=Path("/test/new.py"),
            line_number=1,
            column=0,
            variable_name="new",
            string_set_hash=999,
            string_values=["new"],
            pattern_type="membership_validation",
            details="New pattern",
        )
        storage.add_pattern(new_pattern)

        patterns = storage.get_all_patterns()
        assert len(patterns) == 1
        assert patterns[0].variable_name == "new"


class TestStringValuesSerialization:
    """Tests for JSON serialization of string values."""

    def test_string_values_roundtrip(self, storage: StringlyTypedStorage) -> None:
        """Test string values are correctly serialized and deserialized."""
        pattern = StoredPattern(
            file_path=Path("/test/file.py"),
            line_number=10,
            column=0,
            variable_name="status",
            string_set_hash=12345,
            string_values=["active", "inactive", "pending"],
            pattern_type="membership_validation",
            details="Test pattern",
        )

        storage.add_pattern(pattern)

        retrieved = storage.get_all_patterns()[0]
        assert retrieved.string_values == ["active", "inactive", "pending"]

    def test_empty_string_values(self, storage: StringlyTypedStorage) -> None:
        """Test empty string values list."""
        pattern = StoredPattern(
            file_path=Path("/test/file.py"),
            line_number=10,
            column=0,
            variable_name=None,
            string_set_hash=0,
            string_values=[],
            pattern_type="membership_validation",
            details="Empty values",
        )

        storage.add_pattern(pattern)

        retrieved = storage.get_all_patterns()[0]
        assert retrieved.string_values == []

    def test_special_characters_in_values(self, storage: StringlyTypedStorage) -> None:
        """Test string values with special characters."""
        pattern = StoredPattern(
            file_path=Path("/test/file.py"),
            line_number=10,
            column=0,
            variable_name="mode",
            string_set_hash=12345,
            string_values=['value with "quotes"', "value with\nnewline", "emoji: 🎉"],
            pattern_type="membership_validation",
            details="Special chars",
        )

        storage.add_pattern(pattern)

        retrieved = storage.get_all_patterns()[0]
        assert retrieved.string_values == [
            'value with "quotes"',
            "value with\nnewline",
            "emoji: 🎉",
        ]
