#!/usr/bin/env python3
"""
Purpose: Removes skipped test functions using AST parsing for accurate removal
Scope: Test file cleanup and maintenance
Overview: Utility script that removes test functions marked with @pytest.mark.skip
    decorators using Python AST parsing for precise line identification. Walks the
    AST to find functions with skip decorators, identifies exact line ranges including
    decorators, and removes those lines from source files. More accurate than regex
    approaches as it understands Python syntax. Cleans up excessive blank lines.
Dependencies: ast, subprocess, pathlib, collections for AST parsing and file operations
Exports: main script logic for AST-based test removal
Interfaces: Scans tests/**/*.py files, modifies test files in place
Implementation: AST-based function detection with line-range removal and cleanup
"""

import ast
import subprocess
from pathlib import Path
from collections import defaultdict

print("Collecting all skipped tests...")

# Run pytest to get list of all skipped tests
result = subprocess.run(
    ["poetry", "run", "pytest", "-v", "tests/", "--collect-only"],
    capture_output=True,
    text=True,
    timeout=60
)

# Parse test IDs for skipped tests
# During collection, pytest shows markers like [reason="100% duplicate"]
# But we need to actually run to see which are skipped
# So let's use a different approach - grep for @pytest.mark.skip in files

test_files = list(Path("tests").rglob("test_*.py"))
tests_to_remove = defaultdict(list)

for test_file in test_files:
    try:
        source = test_file.read_text()
        tree = ast.parse(source)

        # Find all functions with @pytest.mark.skip decorator
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check if function has @pytest.mark.skip decorator
                has_skip = False
                for decorator in node.decorator_list:
                    # Handle both @pytest.mark.skip and @pytest.mark.skip(reason="...")
                    if isinstance(decorator, ast.Attribute):
                        if (hasattr(decorator, 'attr') and decorator.attr == 'skip' and
                            hasattr(decorator.value, 'attr') and decorator.value.attr == 'mark'):
                            has_skip = True
                            break
                    elif isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute):
                            if (hasattr(decorator.func, 'attr') and decorator.func.attr == 'skip' and
                                hasattr(decorator.func.value, 'attr') and decorator.func.value.attr == 'mark'):
                                has_skip = True
                                break

                if has_skip:
                    tests_to_remove[str(test_file)].append(node.name)

    except Exception as e:
        print(f"  Warning: Could not parse {test_file}: {e}")

total_tests = sum(len(tests) for tests in tests_to_remove.values())
print(f"Found {total_tests} skipped tests across {len(tests_to_remove)} files")

# Now remove these tests from their files
removed_count = 0

for file_path, function_names in tests_to_remove.items():
    try:
        source = Path(file_path).read_text()
        tree = ast.parse(source)

        # Track which lines to remove
        lines_to_remove = set()

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in function_names:
                    # Mark decorator lines and function lines for removal
                    # Start from first decorator (or function def if no decorators)
                    start_line = node.lineno
                    if node.decorator_list:
                        start_line = node.decorator_list[0].lineno

                    # End is the last line of the function
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno

                    for line_num in range(start_line, end_line + 1):
                        lines_to_remove.add(line_num)

                    removed_count += 1
                    if removed_count % 50 == 0:
                        print(f"  Marked {removed_count}/{total_tests} tests for removal...")

        # Remove the lines
        if lines_to_remove:
            lines = source.split('\n')
            new_lines = [line for i, line in enumerate(lines, 1) if i not in lines_to_remove]

            # Clean up excessive blank lines
            final_lines = []
            blank_count = 0
            for line in new_lines:
                if not line.strip():
                    blank_count += 1
                    if blank_count <= 2:  # Allow max 2 consecutive blank lines
                        final_lines.append(line)
                else:
                    blank_count = 0
                    final_lines.append(line)

            Path(file_path).write_text('\n'.join(final_lines))

    except Exception as e:
        print(f"  ERROR processing {file_path}: {e}")

print(f"\n✅ Removed {removed_count} skipped tests")
print(f"Next: Run 'poetry run pytest --collect-only -q' to verify")
