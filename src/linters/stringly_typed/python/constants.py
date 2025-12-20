"""
Purpose: Shared constants for stringly-typed Python detection

Scope: Common configuration values used across Python pattern detectors

Overview: Provides shared constants used by MembershipValidationDetector,
    ConditionalPatternDetector, and other Python detection components.
    Centralizes configuration values to ensure consistency and avoid
    duplication across detector implementations.

Dependencies: None

Exports: MIN_VALUES_FOR_PATTERN constant

Interfaces: Constants only, no function interfaces

Implementation: Simple module-level constant definitions
"""

# Minimum number of string values to consider as enum candidate
MIN_VALUES_FOR_PATTERN = 2
