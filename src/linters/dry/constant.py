"""
Purpose: Dataclasses for duplicate constants detection in DRY linter

Scope: Data structures for constant extraction and cross-file detection

Overview: Provides dataclasses for representing constants extracted from source code and their
    locations across multiple files. ConstantInfo stores extracted constant metadata (name, line,
    value) from a single file. ConstantLocation represents where a constant appears across the
    project. ConstantGroup represents a group of related constants (exact or fuzzy matches) for
    violation reporting. These structures support the duplicate constants detection feature that
    identifies when the same constant name appears in multiple files.

Dependencies: Python dataclasses module, pathlib for Path types

Exports: ConstantInfo, ConstantLocation, ConstantGroup dataclasses

Interfaces: Dataclass constructors with named fields

Implementation: Immutable dataclasses with optional fields for extracted value context
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

# Shared pattern for ALL_CAPS constant names (public only, no leading underscore)
# Used by both Python and TypeScript constant extractors
# Requires at least 2 characters to exclude single-letter type params (P, T, K, V)
CONSTANT_NAME_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]+$")


@dataclass
class ConstantInfo:
    """Information about a constant extracted from source code.

    Represents a single constant definition found during file analysis.
    Used during the collection phase before cross-file matching.
    """

    name: str  # Constant name (e.g., "API_TIMEOUT")
    line_number: int  # Line where constant is defined
    value: str | None = None  # Optional: the value (for violation message context)


@dataclass
class ConstantLocation:
    """Location of a constant in the project.

    Represents where a specific constant appears, including file path,
    line number, and the value assigned. Used for cross-file reporting.
    """

    file_path: Path
    line_number: int
    name: str
    value: str | None = None


@dataclass
class ConstantGroup:
    """A group of related constants for violation reporting.

    Groups constants that match (either exactly or via fuzzy matching)
    across multiple files. Used by the violation builder to generate
    comprehensive violation messages.
    """

    # The canonical name (first seen or most common)
    canonical_name: str

    # All locations where this constant (or fuzzy match) appears
    locations: list[ConstantLocation] = field(default_factory=list)

    # All names in this group (for fuzzy matches, may include variants)
    all_names: set[str] = field(default_factory=set)

    # Whether this is a fuzzy match (True) or exact match (False)
    is_fuzzy_match: bool = False

    def add_location(self, location: ConstantLocation) -> None:
        """Add a location to this group.

        Args:
            location: The constant location to add
        """
        self.locations.append(location)
        self.all_names.add(location.name)

    @property
    def file_count(self) -> int:
        """Number of unique files containing this constant."""
        return len({loc.file_path for loc in self.locations})
