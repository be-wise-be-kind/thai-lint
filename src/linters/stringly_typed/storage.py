# pylint: disable=too-many-lines
"""
Purpose: SQLite storage manager for stringly-typed pattern detection

Scope: String validation pattern storage, function call tracking, comparison tracking, and
    cross-file detection

Overview: Implements in-memory or temporary-file SQLite storage for stringly-typed pattern
    detection. Stores string validation patterns with hash values computed from the string
    values, enabling cross-file duplicate detection during a single linter run. Also tracks
    function calls with string arguments to detect parameters that should be enums. Tracks
    scattered string comparisons (`var == "string"`) to detect variables compared to multiple
    string values across files. Supports both :memory: mode (fast, RAM-only) and tempfile mode
    (disk-backed for large projects). No persistence between runs - storage is cleared when
    linter completes. Includes indexes for fast hash lookups enabling efficient cross-file
    detection.

Dependencies: Python sqlite3 module (stdlib), tempfile module (stdlib), pathlib.Path,
    dataclasses, json module (stdlib)

Exports: StoredPattern dataclass, StoredFunctionCall dataclass, StoredComparison dataclass,
    StringlyTypedStorage class

Interfaces: StringlyTypedStorage.__init__(storage_mode), add_pattern(pattern),
    add_patterns(patterns), get_duplicate_hashes(min_files), get_patterns_by_hash(hash_value),
    add_function_call(call), add_function_calls(calls), get_limited_value_functions(min_values,
    max_values, min_files), get_calls_by_function(function_name, param_index),
    add_comparison(comparison), add_comparisons(comparisons),
    get_variables_with_multiple_values(min_values, min_files),
    get_comparisons_by_variable(variable_name), get_all_comparisons(), clear(), close()

Implementation: SQLite with string_validations, function_calls, and string_comparisons tables,
    indexed on string_set_hash, function_name+param_index, and variable_name for performance

Suppressions:
    - too-many-lines: Storage module for three related data types with dataclasses, SQL schemas, and CRUD methods
    - too-many-instance-attributes: StoredPattern is a pure DTO with 8 necessary fields for SQLite storage
    - consider-using-with: NamedTemporaryFile must remain open for SQLite connection lifetime (closed in close())
    - srp: Storage class manages SQLite for three pattern types (validations, calls, comparisons).
        Splitting would fragment related storage operations.
"""

from __future__ import annotations

import json
import sqlite3
import tempfile
from dataclasses import dataclass
from pathlib import Path

from src.core.constants import StorageMode

# Row index constants for SQLite query results
_COL_FILE_PATH = 0
_COL_LINE_NUMBER = 1
_COL_COLUMN = 2
_COL_VARIABLE_NAME = 3
_COL_STRING_SET_HASH = 4
_COL_STRING_VALUES = 5
_COL_PATTERN_TYPE = 6
_COL_DETAILS = 7

# Schema SQL for table creation
_CREATE_TABLE_SQL = """CREATE TABLE IF NOT EXISTS string_validations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    column_number INTEGER NOT NULL,
    variable_name TEXT,
    string_set_hash INTEGER NOT NULL,
    string_values TEXT NOT NULL,
    pattern_type TEXT NOT NULL,
    details TEXT NOT NULL,
    UNIQUE(file_path, line_number, column_number)
)"""

_CREATE_HASH_INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_string_hash ON string_validations(string_set_hash)"
)

_CREATE_FILE_INDEX_SQL = "CREATE INDEX IF NOT EXISTS idx_file_path ON string_validations(file_path)"

# Function calls table schema
_CREATE_FUNCTION_CALLS_TABLE_SQL = """CREATE TABLE IF NOT EXISTS function_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    column_number INTEGER NOT NULL,
    function_name TEXT NOT NULL,
    param_index INTEGER NOT NULL,
    string_value TEXT NOT NULL
)"""

_CREATE_FUNCTION_PARAM_INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_function_param ON function_calls(function_name, param_index)"
)

_CREATE_FUNCTION_FILE_INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_function_file ON function_calls(file_path)"
)

# String comparisons table schema (for scattered comparison detection)
_CREATE_COMPARISONS_TABLE_SQL = """CREATE TABLE IF NOT EXISTS string_comparisons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    column_number INTEGER NOT NULL,
    variable_name TEXT NOT NULL,
    compared_value TEXT NOT NULL,
    operator TEXT NOT NULL
)"""

_CREATE_COMPARISONS_VAR_INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_comparison_var ON string_comparisons(variable_name)"
)

_CREATE_COMPARISONS_FILE_INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_comparison_file ON string_comparisons(file_path)"
)

# Row index constants for function_calls query results
_CALL_COL_FILE_PATH = 0
_CALL_COL_LINE_NUMBER = 1
_CALL_COL_COLUMN = 2
_CALL_COL_FUNCTION_NAME = 3
_CALL_COL_PARAM_INDEX = 4
_CALL_COL_STRING_VALUE = 5

# Row index constants for string_comparisons query results
_COMP_COL_FILE_PATH = 0
_COMP_COL_LINE_NUMBER = 1
_COMP_COL_COLUMN = 2
_COMP_COL_VARIABLE_NAME = 3
_COMP_COL_COMPARED_VALUE = 4
_COMP_COL_OPERATOR = 5


@dataclass
class StoredFunctionCall:
    """Represents a function call with a string argument stored in SQLite.

    Captures information about a function or method call where a string literal
    is passed as an argument, enabling cross-file analysis to detect limited
    value sets that should be enums.
    """

    file_path: Path
    """Path to the file containing the call."""

    line_number: int
    """Line number where the call occurs (1-indexed)."""

    column: int
    """Column number where the call starts (0-indexed)."""

    function_name: str
    """Fully qualified function name (e.g., 'process' or 'obj.method')."""

    param_index: int
    """Index of the parameter receiving the string value (0-indexed)."""

    string_value: str
    """The string literal value passed to the function."""


@dataclass
class StoredComparison:
    """Represents a string comparison stored in SQLite.

    Captures information about a comparison like `if (env == "production")` to
    enable cross-file analysis for detecting scattered string comparisons that
    suggest missing enums.
    """

    file_path: Path
    """Path to the file containing the comparison."""

    line_number: int
    """Line number where the comparison occurs (1-indexed)."""

    column: int
    """Column number where the comparison starts (0-indexed)."""

    variable_name: str
    """Variable name being compared (e.g., 'env' or 'self.status')."""

    compared_value: str
    """The string literal value being compared to."""

    operator: str
    """The comparison operator ('==', '!=', '===', '!==')."""


def _row_to_comparison(row: tuple) -> StoredComparison:
    """Convert a database row tuple to StoredComparison.

    Args:
        row: Tuple from SQLite query result

    Returns:
        StoredComparison instance
    """
    return StoredComparison(
        file_path=Path(row[_COMP_COL_FILE_PATH]),
        line_number=row[_COMP_COL_LINE_NUMBER],
        column=row[_COMP_COL_COLUMN],
        variable_name=row[_COMP_COL_VARIABLE_NAME],
        compared_value=row[_COMP_COL_COMPARED_VALUE],
        operator=row[_COMP_COL_OPERATOR],
    )


def _row_to_pattern(row: tuple) -> StoredPattern:
    """Convert a database row tuple to StoredPattern.

    Args:
        row: Tuple from SQLite query result

    Returns:
        StoredPattern instance
    """
    return StoredPattern(
        file_path=Path(row[_COL_FILE_PATH]),
        line_number=row[_COL_LINE_NUMBER],
        column=row[_COL_COLUMN],
        variable_name=row[_COL_VARIABLE_NAME],
        string_set_hash=row[_COL_STRING_SET_HASH],
        string_values=json.loads(row[_COL_STRING_VALUES]),
        pattern_type=row[_COL_PATTERN_TYPE],
        details=row[_COL_DETAILS],
    )


def _row_to_function_call(row: tuple) -> StoredFunctionCall:
    """Convert a database row tuple to StoredFunctionCall.

    Args:
        row: Tuple from SQLite query result

    Returns:
        StoredFunctionCall instance
    """
    return StoredFunctionCall(
        file_path=Path(row[_CALL_COL_FILE_PATH]),
        line_number=row[_CALL_COL_LINE_NUMBER],
        column=row[_CALL_COL_COLUMN],
        function_name=row[_CALL_COL_FUNCTION_NAME],
        param_index=row[_CALL_COL_PARAM_INDEX],
        string_value=row[_CALL_COL_STRING_VALUE],
    )


@dataclass
class StoredPattern:  # pylint: disable=too-many-instance-attributes
    """Represents a stringly-typed pattern stored in SQLite.

    Captures all information needed to detect cross-file duplicates and generate
    violations with meaningful context.
    """

    file_path: Path
    """Path to the file containing the pattern."""

    line_number: int
    """Line number where the pattern occurs (1-indexed)."""

    column: int
    """Column number where the pattern starts (0-indexed)."""

    variable_name: str | None
    """Variable name involved in the pattern, if identifiable."""

    string_set_hash: int
    """Hash of the normalized string values for cross-file matching."""

    string_values: list[str]
    """Sorted list of string values in the pattern."""

    pattern_type: str
    """Type of pattern: membership_validation, equality_chain, etc."""

    details: str
    """Human-readable description of the detected pattern."""


class StringlyTypedStorage:  # thailint: ignore[srp]
    """SQLite-backed storage for stringly-typed pattern detection.

    Stores patterns from analyzed files and provides queries to find patterns
    that appear across multiple files, enabling cross-file duplicate detection.
    """

    def __init__(self, storage_mode: str = "memory") -> None:
        """Initialize storage with SQLite database.

        Args:
            storage_mode: Storage mode - "memory" (default) or "tempfile"
        """
        self._storage_mode = storage_mode
        self._tempfile = None

        # Create SQLite connection based on storage mode
        if storage_mode == StorageMode.MEMORY:
            self._db = sqlite3.connect(":memory:")
        elif storage_mode == StorageMode.TEMPFILE:
            self._tempfile = tempfile.NamedTemporaryFile(suffix=".db", delete=True)  # pylint: disable=consider-using-with
            self._db = sqlite3.connect(self._tempfile.name)
        else:
            raise ValueError(f"Invalid storage_mode: {storage_mode}")

        # Create schema inline
        self._db.execute(_CREATE_TABLE_SQL)
        self._db.execute(_CREATE_HASH_INDEX_SQL)
        self._db.execute(_CREATE_FILE_INDEX_SQL)
        self._db.execute(_CREATE_FUNCTION_CALLS_TABLE_SQL)
        self._db.execute(_CREATE_FUNCTION_PARAM_INDEX_SQL)
        self._db.execute(_CREATE_FUNCTION_FILE_INDEX_SQL)
        self._db.execute(_CREATE_COMPARISONS_TABLE_SQL)
        self._db.execute(_CREATE_COMPARISONS_VAR_INDEX_SQL)
        self._db.execute(_CREATE_COMPARISONS_FILE_INDEX_SQL)
        self._db.commit()

    def add_pattern(self, pattern: StoredPattern) -> None:
        """Add a single pattern to storage.

        Args:
            pattern: StoredPattern instance to store
        """
        self.add_patterns([pattern])

    def add_patterns(self, patterns: list[StoredPattern]) -> None:
        """Add multiple patterns to storage in a batch.

        Args:
            patterns: List of StoredPattern instances to store
        """
        if not patterns:
            return

        for pattern in patterns:
            self._db.execute(
                """INSERT OR REPLACE INTO string_validations
                   (file_path, line_number, column_number, variable_name,
                    string_set_hash, string_values, pattern_type, details)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(pattern.file_path),
                    pattern.line_number,
                    pattern.column,
                    pattern.variable_name,
                    pattern.string_set_hash,
                    json.dumps(pattern.string_values),
                    pattern.pattern_type,
                    pattern.details,
                ),
            )

        self._db.commit()

    def get_duplicate_hashes(self, min_files: int = 2) -> list[int]:
        """Get hash values that appear in min_files or more files.

        Args:
            min_files: Minimum number of distinct files (default: 2)

        Returns:
            List of hash values appearing in at least min_files files
        """
        cursor = self._db.execute(
            """SELECT string_set_hash FROM string_validations
               GROUP BY string_set_hash
               HAVING COUNT(DISTINCT file_path) >= ?""",
            (min_files,),
        )
        return [row[0] for row in cursor.fetchall()]

    def get_patterns_by_hash(self, hash_value: int) -> list[StoredPattern]:
        """Get all patterns with the given hash value.

        Args:
            hash_value: Hash value to search for

        Returns:
            List of StoredPattern instances with this hash
        """
        cursor = self._db.execute(
            """SELECT file_path, line_number, column_number, variable_name,
                      string_set_hash, string_values, pattern_type, details
               FROM string_validations
               WHERE string_set_hash = ?
               ORDER BY file_path, line_number""",
            (hash_value,),
        )

        return [_row_to_pattern(row) for row in cursor.fetchall()]

    def get_all_patterns(self) -> list[StoredPattern]:
        """Get all stored patterns.

        Returns:
            List of all StoredPattern instances in storage
        """
        cursor = self._db.execute(
            """SELECT file_path, line_number, column_number, variable_name,
                      string_set_hash, string_values, pattern_type, details
               FROM string_validations
               ORDER BY file_path, line_number"""
        )

        return [_row_to_pattern(row) for row in cursor.fetchall()]

    def add_function_call(self, call: StoredFunctionCall) -> None:
        """Add a single function call to storage.

        Args:
            call: StoredFunctionCall instance to store
        """
        self.add_function_calls([call])

    def add_function_calls(self, calls: list[StoredFunctionCall]) -> None:
        """Add multiple function calls to storage in a batch.

        Args:
            calls: List of StoredFunctionCall instances to store
        """
        if not calls:
            return

        for call in calls:
            self._db.execute(
                """INSERT INTO function_calls
                   (file_path, line_number, column_number, function_name,
                    param_index, string_value)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    str(call.file_path),
                    call.line_number,
                    call.column,
                    call.function_name,
                    call.param_index,
                    call.string_value,
                ),
            )

        self._db.commit()

    def get_limited_value_functions(
        self, min_values: int, max_values: int, min_files: int = 1
    ) -> list[tuple[str, int, set[str]]]:
        """Get function+param combinations with limited unique string values.

        Finds function parameters that are called with a limited set of string
        values, suggesting they should be enums.

        Args:
            min_values: Minimum unique values to consider (default: 2)
            max_values: Maximum unique values to consider (default: 6)
            min_files: Minimum files the pattern must appear in (default: 1)

        Returns:
            List of (function_name, param_index, unique_values) tuples
        """
        cursor = self._db.execute(
            """SELECT function_name, param_index, GROUP_CONCAT(DISTINCT string_value)
               FROM function_calls
               GROUP BY function_name, param_index
               HAVING COUNT(DISTINCT string_value) >= ?
                  AND COUNT(DISTINCT string_value) <= ?
                  AND COUNT(DISTINCT file_path) >= ?""",
            (min_values, max_values, min_files),
        )

        results: list[tuple[str, int, set[str]]] = []
        for row in cursor.fetchall():
            values = set(row[2].split(",")) if row[2] else set()
            results.append((row[0], row[1], values))

        return results

    def get_calls_by_function(
        self, function_name: str, param_index: int
    ) -> list[StoredFunctionCall]:
        """Get all calls for a specific function and parameter.

        Args:
            function_name: Name of the function
            param_index: Index of the parameter

        Returns:
            List of StoredFunctionCall instances for this function+param
        """
        cursor = self._db.execute(
            """SELECT file_path, line_number, column_number, function_name,
                      param_index, string_value
               FROM function_calls
               WHERE function_name = ? AND param_index = ?
               ORDER BY file_path, line_number""",
            (function_name, param_index),
        )

        return [_row_to_function_call(row) for row in cursor.fetchall()]

    def get_all_function_calls(self) -> list[StoredFunctionCall]:
        """Get all stored function calls.

        Returns:
            List of all StoredFunctionCall instances in storage
        """
        cursor = self._db.execute(
            """SELECT file_path, line_number, column_number, function_name,
                      param_index, string_value
               FROM function_calls
               ORDER BY file_path, line_number"""
        )

        return [_row_to_function_call(row) for row in cursor.fetchall()]

    def add_comparison(self, comparison: StoredComparison) -> None:
        """Add a single comparison to storage.

        Args:
            comparison: StoredComparison instance to store
        """
        self.add_comparisons([comparison])

    def add_comparisons(self, comparisons: list[StoredComparison]) -> None:
        """Add multiple comparisons to storage in a batch.

        Args:
            comparisons: List of StoredComparison instances to store
        """
        if not comparisons:
            return

        for comparison in comparisons:
            self._db.execute(
                """INSERT INTO string_comparisons
                   (file_path, line_number, column_number, variable_name,
                    compared_value, operator)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    str(comparison.file_path),
                    comparison.line_number,
                    comparison.column,
                    comparison.variable_name,
                    comparison.compared_value,
                    comparison.operator,
                ),
            )

        self._db.commit()

    def get_variables_with_multiple_values(
        self, min_values: int = 2, min_files: int = 1
    ) -> list[tuple[str, set[str]]]:
        """Get variables compared to multiple unique string values.

        Finds variables that are compared to at least min_values unique strings,
        suggesting they should be enums.

        Args:
            min_values: Minimum unique values to consider (default: 2)
            min_files: Minimum files the pattern must appear in (default: 1)

        Returns:
            List of (variable_name, unique_values) tuples
        """
        cursor = self._db.execute(
            """SELECT variable_name, GROUP_CONCAT(DISTINCT compared_value)
               FROM string_comparisons
               GROUP BY variable_name
               HAVING COUNT(DISTINCT compared_value) >= ?
                  AND COUNT(DISTINCT file_path) >= ?""",
            (min_values, min_files),
        )

        results: list[tuple[str, set[str]]] = []
        for row in cursor.fetchall():
            values = set(row[1].split(",")) if row[1] else set()
            results.append((row[0], values))

        return results

    def get_comparisons_by_variable(self, variable_name: str) -> list[StoredComparison]:
        """Get all comparisons for a specific variable.

        Args:
            variable_name: Name of the variable

        Returns:
            List of StoredComparison instances for this variable
        """
        cursor = self._db.execute(
            """SELECT file_path, line_number, column_number, variable_name,
                      compared_value, operator
               FROM string_comparisons
               WHERE variable_name = ?
               ORDER BY file_path, line_number""",
            (variable_name,),
        )

        return [_row_to_comparison(row) for row in cursor.fetchall()]

    def get_all_comparisons(self) -> list[StoredComparison]:
        """Get all stored comparisons.

        Returns:
            List of all StoredComparison instances in storage
        """
        cursor = self._db.execute(
            """SELECT file_path, line_number, column_number, variable_name,
                      compared_value, operator
               FROM string_comparisons
               ORDER BY file_path, line_number"""
        )

        return [_row_to_comparison(row) for row in cursor.fetchall()]

    def clear(self) -> None:
        """Clear all stored patterns, function calls, and comparisons."""
        self._db.execute("DELETE FROM string_validations")
        self._db.execute("DELETE FROM function_calls")
        self._db.execute("DELETE FROM string_comparisons")
        self._db.commit()

    def close(self) -> None:
        """Close database connection and cleanup tempfile if used."""
        self._db.close()
        if self._tempfile:
            self._tempfile.close()
