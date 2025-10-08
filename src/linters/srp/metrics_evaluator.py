"""
Purpose: SRP metrics evaluation against configured thresholds

Scope: Evaluates class metrics to determine SRP violations

Overview: Provides metrics evaluation functionality for the SRP linter. Checks class metrics
    (method count, lines of code, naming keywords) against configured thresholds. Collects
    issues when metrics exceed limits. Isolates threshold evaluation logic from class analysis
    and violation building to maintain single responsibility.

Dependencies: SRPConfig, typing

Exports: evaluate_metrics

Interfaces: evaluate_metrics(metrics, config) -> list[str] (returns list of issue descriptions)

Implementation: Compares numeric thresholds and keyword patterns, returns descriptive issue strings
"""

from typing import Any

from .config import SRPConfig


def evaluate_metrics(metrics: dict[str, Any], config: SRPConfig) -> list[str]:
    """Evaluate class metrics and collect SRP issues.

    Args:
        metrics: Class metrics dictionary with method_count, loc, has_keyword
        config: SRP configuration with thresholds

    Returns:
        List of issue descriptions (empty if no violations)
    """
    issues = []

    # Check numeric thresholds
    if metrics["method_count"] > config.max_methods:
        issues.append(f"{metrics['method_count']} methods (max: {config.max_methods})")
    if metrics["loc"] > config.max_loc:
        issues.append(f"{metrics['loc']} lines (max: {config.max_loc})")

    # Check keyword heuristic
    if config.check_keywords and metrics["has_keyword"]:
        issues.append("responsibility keyword in name")

    return issues
