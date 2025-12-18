"""
Purpose: Unit tests for collection-pipeline linter

Scope: Test coverage for pattern detection, suggestions, and configuration

Overview: Test package for the collection-pipeline linter. Contains comprehensive tests
    for detecting embedded filtering patterns in for loops that could be refactored to
    collection pipelines (generator expressions, filter()). Follows TDD methodology with
    tests written before implementation.

Dependencies: pytest, src.linters.collection_pipeline

Exports: Test classes and fixtures for collection-pipeline testing

Interfaces: Standard pytest test discovery

Implementation: TDD-driven test suite with pattern detection and edge case coverage
"""
