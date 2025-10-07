"""
Purpose: Integration test package for end-to-end testing of all deployment modes

Scope: E2E tests for CLI, Library API, Docker, performance, and real-world usage

Overview: Integration test suite for comprehensive end-to-end validation of the thai-lint
    framework across all three deployment modes (CLI, Library API, Docker). Tests verify
    complete workflows from user input to output, including help commands, linting operations,
    performance benchmarks, and real-world dogfooding. Ensures all components work together
    correctly in production-like scenarios with actual file I/O, subprocess execution, and
    container orchestration.

Dependencies: pytest for testing framework, subprocess for CLI/Docker execution

Exports: Integration test modules for CLI, Library, Docker, Performance, and Real-world testing

Interfaces: pytest test discovery, test classes and functions for E2E validation

Implementation: E2E tests with actual file system operations, subprocess calls, and
    performance measurements
"""
