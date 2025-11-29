#!/usr/bin/env python3
"""
Purpose: Demonstrates SRP linter usage patterns and integration approaches

Scope: Library API examples, configuration options, and CI/CD integration patterns

Overview: Working examples showing how to use the SRP linter programmatically through
    multiple usage patterns. Covers basic usage with default settings, custom threshold
    configuration, language-specific settings, batch processing of multiple files, CI/CD
    pipeline integration, and keyword-based filtering. Demonstrates both the convenience
    srp_lint function and direct SRPRule class usage for different scenarios.

Dependencies: thailint package (src.Linter, src.SRPRule, src.srp_lint), pathlib, sys

Exports: Six example functions demonstrating different SRP linter usage patterns

Interfaces: example_1_basic_usage(), example_2_custom_thresholds(), example_3_language_specific(),
    example_4_batch_processing(), example_5_ci_integration(), example_6_filtering_by_keyword()

Implementation: Executable examples with working code showing API usage and integration patterns
"""

import sys
from pathlib import Path

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import Linter, SRPRule, srp_lint


def example_1_basic_usage():
    """Basic SRP linting with default settings."""
    print("=" * 60)
    print("Example 1: Basic SRP Linting")
    print("=" * 60)

    # Lint current directory with defaults
    # Default: max_methods=7, max_loc=200
    violations = srp_lint("src/")

    if not violations:
        print("\n✅ No SRP violations found!")
        return

    print(f"\n❌ Found {len(violations)} SRP violations:\n")
    for v in violations:
        print(f"  {v.file_path}:{v.line}")
        print(f"    {v.message}")
        if v.suggestion:
            print(f"    💡 {v.suggestion}")
        print()


def example_2_custom_thresholds():
    """Using custom thresholds for stricter checking."""
    print("\n" + "=" * 60)
    print("Example 2: Custom Thresholds")
    print("=" * 60)

    # Create linter with custom config
    linter = Linter()

    # Custom metadata with stricter thresholds
    custom_config = {
        "srp": {
            "enabled": True,
            "max_methods": 5,  # Stricter than default 7
            "max_loc": 150,    # Stricter than default 200
            "check_keywords": True
        }
    }

    violations = []
    for py_file in Path("src/").rglob("*.py"):
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()

        rule = SRPRule()
        from src.core.base import BaseLintContext

        context = BaseLintContext(
            file_path=str(py_file),
            file_content=content,
            language="python",
            metadata=custom_config
        )

        file_violations = rule.check(context)
        violations.extend(file_violations)

    if violations:
        print(f"\n❌ Found {len(violations)} violations with strict thresholds:\n")
        for v in violations:
            print(f"  {v.file_path}:{v.line} - {v.message}")
    else:
        print("\n✅ All classes meet strict SRP requirements!")


def example_3_language_specific():
    """Language-specific configuration for Python and TypeScript."""
    print("\n" + "=" * 60)
    print("Example 3: Language-Specific Configuration")
    print("=" * 60)

    # Config with language-specific thresholds
    config = {
        "srp": {
            "enabled": True,
            # Python: stricter (more concise language)
            "python": {
                "max_methods": 8,
                "max_loc": 200
            },
            # TypeScript: more lenient (verbose with types)
            "typescript": {
                "max_methods": 10,
                "max_loc": 250
            },
            # Defaults for other languages
            "max_methods": 7,
            "max_loc": 200
        }
    }

    linter = Linter()

    # Check Python files
    python_violations = []
    for py_file in Path("src/").rglob("*.py"):
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()

        rule = SRPRule()
        from src.core.base import BaseLintContext

        context = BaseLintContext(
            file_path=str(py_file),
            file_content=content,
            language="python",
            metadata=config
        )

        python_violations.extend(rule.check(context))

    print(f"\nPython files: {len(python_violations)} violations")
    print("  (Using Python thresholds: 8 methods, 200 LOC)")


def example_4_batch_processing():
    """Process multiple files and generate report."""
    print("\n" + "=" * 60)
    print("Example 4: Batch Processing with Report")
    print("=" * 60)

    linter = Linter(config_file=".thailint.yaml")

    # Collect violations by severity
    all_violations = linter.lint("src/", rules=["srp.violation"])

    if not all_violations:
        print("\n✅ No SRP violations found in codebase!")
        return

    # Group by file
    violations_by_file = {}
    for v in all_violations:
        if v.file_path not in violations_by_file:
            violations_by_file[v.file_path] = []
        violations_by_file[v.file_path].append(v)

    # Print report
    print(f"\n📊 SRP Violation Report")
    print(f"   Total violations: {len(all_violations)}")
    print(f"   Files affected: {len(violations_by_file)}")
    print("\nViolations by file:")

    for file_path, violations in sorted(violations_by_file.items()):
        print(f"\n  {file_path} ({len(violations)} violations)")
        for v in violations:
            print(f"    Line {v.line}: {v.message}")


def example_5_ci_integration():
    """Integration pattern for CI/CD pipelines."""
    print("\n" + "=" * 60)
    print("Example 5: CI/CD Integration Pattern")
    print("=" * 60)

    # This pattern is useful for CI/CD where you want to:
    # 1. Run SRP checks
    # 2. Generate JSON report
    # 3. Fail build if violations found

    violations = srp_lint("src/")

    # Generate JSON-compatible report
    report = {
        "total_violations": len(violations),
        "violations": [
            {
                "file": v.file_path,
                "line": v.line,
                "column": v.column,
                "rule_id": v.rule_id,
                "message": v.message,
                "severity": v.severity.value,
                "suggestion": v.suggestion
            }
            for v in violations
        ]
    }

    if report["total_violations"] > 0:
        print(f"\n❌ CI Check Failed: {report['total_violations']} SRP violations")
        print("\nViolations:")
        for v in report["violations"]:
            print(f"  {v['file']}:{v['line']} - {v['message']}")

        # In CI, you would:
        # - Save report to file: json.dump(report, open('srp-report.json', 'w'))
        # - Exit with error code: sys.exit(1)
        print("\n💡 In CI, this would exit with code 1 to fail the build")
    else:
        print("\n✅ CI Check Passed: No SRP violations")
        # Exit with success: sys.exit(0)


def example_6_filtering_by_keyword():
    """Filter violations by responsibility keyword."""
    print("\n" + "=" * 60)
    print("Example 6: Filtering by Responsibility Keywords")
    print("=" * 60)

    # Custom keywords to detect
    config = {
        "srp": {
            "enabled": True,
            "check_keywords": True,
            "keywords": [
                "Manager",
                "Handler",
                "Processor",
                "Utility",
                "Helper",
                "Controller",  # Added custom
                "Service"       # Added custom
            ]
        }
    }

    rule = SRPRule()
    keyword_violations = []

    for py_file in Path("src/").rglob("*.py"):
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()

        from src.core.base import BaseLintContext

        context = BaseLintContext(
            file_path=str(py_file),
            file_content=content,
            language="python",
            metadata=config
        )

        violations = rule.check(context)
        # Filter for keyword-only violations
        keyword_only = [v for v in violations if "keyword" in v.message.lower()]
        keyword_violations.extend(keyword_only)

    if keyword_violations:
        print(f"\n🔍 Found {len(keyword_violations)} classes with responsibility keywords:\n")
        for v in keyword_violations:
            print(f"  {v.file_path}:{v.line}")
            print(f"    {v.message}\n")
    else:
        print("\n✅ No responsibility keywords found in class names!")


if __name__ == "__main__":
    print("\n🏛️  SRP Linter - Usage Examples\n")

    try:
        example_1_basic_usage()
        example_2_custom_thresholds()
        example_3_language_specific()
        example_4_batch_processing()
        example_5_ci_integration()
        example_6_filtering_by_keyword()

        print("\n" + "=" * 60)
        print("✨ All examples completed!")
        print("=" * 60)
        print("\nFor more information, see:")
        print("  - docs/srp-linter.md (comprehensive guide)")
        print("  - docs/cli-reference.md (CLI commands)")
        print("  - docs/configuration.md (config options)")
        print()

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
