"""
Purpose: Core data structures for CQS (Command-Query Separation) linter

Scope: Type definitions for INPUT operations, OUTPUT operations, and CQS patterns

Overview: Defines the fundamental data structures used by the CQS linter to represent
    and analyze code patterns. InputOperation represents query-like operations that
    assign call results to variables. OutputOperation represents command-like operations
    that are statement-level calls without capturing return values. CQSPattern aggregates
    these operations for a single function and provides methods to detect CQS violations
    (functions that mix INPUTs and OUTPUTs).

Dependencies: dataclasses for structured data representation

Exports: InputOperation, OutputOperation, CQSPattern

Interfaces: CQSPattern.has_violation(), CQSPattern.get_full_name()

Implementation: Immutable dataclasses with computed methods for violation detection

Suppressions:
    too-many-instance-attributes: CQSPattern requires 9 attributes to fully describe
        a function's CQS analysis (name, location, file, inputs, outputs, flags)
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class InputOperation:
    """Represents an INPUT (query) operation in code.

    An INPUT operation is one where a function call result is captured and used,
    typically through assignment: x = func().
    """

    line: int
    column: int
    expression: str  # e.g., "fetch_data()"
    target: str  # e.g., "x" or "self.data"


@dataclass(frozen=True)
class OutputOperation:
    """Represents an OUTPUT (command) operation in code.

    An OUTPUT operation is a statement-level call where the return value is
    discarded: func() as a standalone statement.
    """

    line: int
    column: int
    expression: str  # e.g., "save_data(result)"


@dataclass
class CQSPattern:  # pylint: disable=too-many-instance-attributes
    """Represents a function's CQS analysis results.

    Aggregates all INPUT and OUTPUT operations found within a function body
    and provides methods to determine if the function violates CQS principles.
    """

    function_name: str
    line: int
    column: int
    file_path: str
    inputs: list[InputOperation] = field(default_factory=list)
    outputs: list[OutputOperation] = field(default_factory=list)
    is_method: bool = False
    is_async: bool = False
    class_name: str | None = None

    def has_violation(self) -> bool:
        """Return True if function mixes INPUTs and OUTPUTs (CQS violation)."""
        return len(self.inputs) > 0 and len(self.outputs) > 0

    def get_full_name(self) -> str:
        """Return fully qualified name (ClassName.method or function)."""
        if self.class_name:
            return f"{self.class_name}.{self.function_name}"
        return self.function_name
