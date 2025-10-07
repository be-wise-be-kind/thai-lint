"""Multi-language orchestrator for coordinating linting operations.

This package provides the main orchestration engine that coordinates rule execution
across files and languages.
"""

from .core import Orchestrator

__all__ = ["Orchestrator"]
