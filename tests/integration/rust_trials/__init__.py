"""
Purpose: Package marker for Rust validation trial scripts

Scope: Integration test infrastructure for validating Rust linters against popular repositories

Overview: Marks the rust_trials directory as a Python package. Contains standalone validation
    scripts (not pytest tests) that clone popular Rust repositories and run all Rust linters
    against them to measure false positive rates before release. Scripts include a trial runner,
    violation classifier, and report generator.

Dependencies: None (package marker only)

Exports: None (package marker only)

Interfaces: None (package marker only)

Implementation: Empty package marker following project conventions
"""
