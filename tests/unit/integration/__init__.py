"""
Purpose: Integration test module for end-to-end linting workflows

Scope: Tests combining orchestrator, rules, config loader, and ignore systems

Overview: Contains integration tests validating complete workflows across multiple components.
    Tests ensure proper integration between the orchestrator and concrete linter implementations,
    verifies configuration loading cascades correctly to active rules, validates ignore directives
    function across all system layers, and confirms violations propagate correctly from rules
    through orchestrator to calling code. Focuses on real-world usage scenarios rather than
    isolated unit test cases, using temporary file fixtures and complete configuration hierarchies.

Dependencies: pytest for test framework

Exports: No exports (test module)

Interfaces: None (pytest discovers tests automatically)

Implementation: Fixture-based testing with temporary directories and complete configuration files
"""
