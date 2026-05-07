"""
Purpose: Test package for Law of Demeter linter

Scope: Unit tests for LoD violation detection, filtering, and configuration

Overview: Contains comprehensive test suite for the Law of Demeter linter including
    tests for chain extraction, classification, all 9 false-positive filters, config
    loading, integration tests, violation messages, and ignore directives. Uses inline
    code fixtures derived from 23 real-world Python repos to validate both true-positive
    detection and false-positive filtering accuracy.

Dependencies: pytest, src.linters.law_of_demeter

Exports: Test modules for each component

Interfaces: Standard pytest test discovery

Implementation: TDD red/green methodology - tests written before implementation
"""
