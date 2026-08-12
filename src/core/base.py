"""
Purpose: Abstract base classes defining the core plugin architecture interfaces

Scope: Foundation interfaces for all linting rules, contexts, and plugin implementations

Overview: Establishes the contract that all linting plugins must follow through abstract base
    classes, enabling the plugin architecture that allows dynamic rule discovery and execution.
    Defines BaseLintRule which all concrete linting rules inherit from, specifying required
    properties (rule_id, rule_name, description) and the check() method for violation detection.
    Provides BaseLintContext as the interface for accessing file information during analysis,
    exposing file_path, file_content, and language properties. Includes MultiLanguageLintRule
    intermediate class implementing template method pattern for language dispatch, eliminating
    code duplication across multi-language linters (nesting, srp, magic_numbers). These
    abstractions enable the rule registry to discover and instantiate rules dynamically without
    tight coupling, supporting the extensible plugin system where new rules can be added by
    simply placing them in the appropriate directory structure.

Dependencies: abc for abstract base class support, pathlib for Path types, Violation from types

Exports: BaseLintRule (abstract rule interface), BaseLintContext (abstract context interface),
    MultiLanguageLintRule (template method base for multi-language linters)

Interfaces: BaseLintRule.check(context) -> list[Violation], BaseLintContext properties
    (file_path, file_content, language), all abstract methods must be implemented by subclasses

Implementation: ABC-based interface definitions with @abstractmethod decorators, property-based
    API for rule metadata, context-based execution pattern for rule checking
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .constants import Language
from .types import Violation


class BaseLintContext(ABC):
    """Base class for lint context.

    A lint context provides all the information a rule needs to analyze
    a file, including the file path, content, and language.
    """

    @property
    @abstractmethod
    def file_path(self) -> Path | None:
        """Get the file path being analyzed.

        Returns:
            Path to the file, or None if analyzing content without a file.
        """
        raise NotImplementedError("Subclasses must implement file_path")

    @property
    @abstractmethod
    def file_content(self) -> str | None:
        """Get the file content being analyzed.

        Returns:
            Content of the file as a string, or None if file not available.
        """
        raise NotImplementedError("Subclasses must implement file_content")

    @property
    @abstractmethod
    def language(self) -> str:
        """Get the programming language of the file.

        Returns:
            Language identifier (e.g., 'python', 'javascript', 'go').
        """
        raise NotImplementedError("Subclasses must implement language")


class BaseLintRule(ABC):
    """Base class for all linting rules.

    All concrete linting rules must inherit from this class and implement
    all abstract methods and properties. Rules are discovered and registered
    automatically by the rule registry.
    """

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique identifier for this rule.

        The rule ID should follow the format 'category.rule-name', e.g.,
        'file-placement.deny-pattern' or 'naming.class-pascal-case'.

        Returns:
            Unique rule identifier.
        """
        raise NotImplementedError("Subclasses must implement rule_id")

    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Human-readable name for this rule.

        Returns:
            Descriptive name for display to users.
        """
        raise NotImplementedError("Subclasses must implement rule_name")

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this rule checks.

        Returns:
            Detailed description of the rule's purpose and behavior.
        """
        raise NotImplementedError("Subclasses must implement description")

    @abstractmethod
    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for violations in the given context.

        Args:
            context: The lint context containing file information.

        Returns:
            List of violations found. Empty list if no violations.
        """
        raise NotImplementedError("Subclasses must implement check")

    def finalize(self) -> list[Violation]:
        """Finalize analysis after all files processed.

        Optional hook called after all files have been processed via check().
        Useful for rules that need to perform cross-file analysis or aggregate
        results (e.g., DRY linter querying for duplicates across all files).

        Returns:
            List of violations found during finalization. Empty list by default.
        """
        return []

    def get_parallel_shared_config(self, shared_dir: Path) -> dict[str, Any] | None:
        """Return a config-section override to share state across --parallel workers.

        Optional hook consulted before dispatching worker processes. A rule whose
        finalize() needs cross-file state (built up across check() calls) cannot rely on
        that state existing in the main process under --parallel, since each worker runs
        check() in an isolated process. Returning a non-None override here merges it into
        every worker's config (and the main process's), letting the rule redirect its
        state into something shared - e.g. a real on-disk file instead of an in-memory
        store. shared_dir is a directory the rule may use for on-disk state needed only
        for the duration of this one run.

        Args:
            shared_dir: Directory available for this run's shared on-disk state.

        Returns:
            Config-section override dict to merge in, or None if no override is needed.
        """
        return None

    def finalize_after_parallel(self, raw_config: dict[str, Any]) -> list[Violation]:
        """Finalize after a --parallel run, for rules that returned a shared config.

        Called instead of finalize() when running under --parallel. Default
        implementation just calls finalize() unchanged, which is correct for rules that
        never returned an override from get_parallel_shared_config(). Rules that did
        return an override should use raw_config here to reconnect to the shared state
        those workers wrote to before delegating to their normal finalize() logic.

        Args:
            raw_config: The full raw config dict used for this run, including any
                override from get_parallel_shared_config().

        Returns:
            List of violations found during finalization.
        """
        return self.finalize()


class MultiLanguageLintRule(BaseLintRule):
    """Base class for linting rules that support multiple programming languages.

    Provides language dispatch pattern to eliminate code duplication across multi-language
    linters. Subclasses implement language-specific checking methods rather than handling
    dispatch logic themselves.

    Subclasses must implement:
    - _check_python(context, config) for Python language support
    - _check_typescript(context, config) for TypeScript/JavaScript support
    - _load_config(context) for configuration loading
    """

    def __init__(self) -> None:
        """Initialize the multi-language lint rule."""
        pass  # Base class for multi-language linters

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for violations with automatic language dispatch.

        Dispatches to language-specific checking methods based on context.language.
        Handles common patterns like file content validation and config loading.

        Args:
            context: Lint context with file information

        Returns:
            List of violations found
        """
        from .linter_utils import has_file_content

        if not has_file_content(context):
            return []

        config = self._load_config(context)
        if not config.enabled:
            return []

        return self._dispatch_by_language(context, config)

    def _dispatch_by_language(self, context: BaseLintContext, config: Any) -> list[Violation]:
        """Dispatch to language-specific check method.

        Args:
            context: Lint context with language information
            config: Loaded configuration

        Returns:
            List of violations from language-specific checker
        """
        if context.language == Language.PYTHON:
            return self._check_python(context, config)

        if context.language in (Language.TYPESCRIPT, Language.JAVASCRIPT):
            return self._check_typescript(context, config)

        if context.language == Language.RUST:
            return self._check_rust(context, config)

        return []

    @abstractmethod
    def _load_config(self, context: BaseLintContext) -> Any:
        """Load configuration from context.

        Args:
            context: Lint context

        Returns:
            Configuration object with at minimum an 'enabled' attribute
        """
        raise NotImplementedError("Subclasses must implement _load_config")

    @abstractmethod
    def _check_python(self, context: BaseLintContext, config: Any) -> list[Violation]:
        """Check Python code for violations.

        Args:
            context: Lint context with Python file information
            config: Loaded configuration

        Returns:
            List of violations found in Python code
        """
        raise NotImplementedError("Subclasses must implement _check_python")

    @abstractmethod
    def _check_typescript(self, context: BaseLintContext, config: Any) -> list[Violation]:
        """Check TypeScript/JavaScript code for violations.

        Args:
            context: Lint context with TypeScript/JavaScript file information
            config: Loaded configuration

        Returns:
            List of violations found in TypeScript/JavaScript code
        """
        raise NotImplementedError("Subclasses must implement _check_typescript")

    def _check_rust(self, context: BaseLintContext, config: Any) -> list[Violation]:
        """Check Rust code for violations.

        Override in subclasses to add Rust language support.
        Returns empty list by default for linters that do not support Rust.

        Args:
            context: Lint context with Rust file information
            config: Loaded configuration

        Returns:
            List of violations found in Rust code
        """
        return []
