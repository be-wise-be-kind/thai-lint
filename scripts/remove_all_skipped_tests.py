#!/usr/bin/env python3
"""Remove ALL tests marked with @pytest.mark.skip decorator."""

import re
from pathlib import Path

test_dir = Path("tests")
removed_count = 0
files_modified = 0

print("Scanning for all @pytest.mark.skip decorated tests...")

# Find all test files
test_files = list(test_dir.rglob("test_*.py"))

for test_file in test_files:
    try:
        content = test_file.read_text()
        lines = content.split("\n")
        new_lines = []
        i = 0
        file_modified = False

        while i < len(lines):
            line = lines[i]

            # Check if this line has a @pytest.mark.skip decorator
            if "@pytest.mark.skip" in line:
                # Found a skip decorator - need to remove the entire function
                decorator_indent = len(line) - len(line.lstrip())

                # Skip the decorator line
                i += 1
                if i >= len(lines):
                    break

                # Next line should be the function definition
                func_line = lines[i]
                if not func_line.strip().startswith("def "):
                    # Not a function, just skip the decorator
                    new_lines.append(line)
                    new_lines.append(func_line)
                    i += 1
                    continue

                # Get function name for logging
                func_match = re.search(r'def\s+(\w+)\s*\(', func_line)
                func_name = func_match.group(1) if func_match else "unknown"

                # Get the function's indentation level
                function_indent = len(func_line) - len(func_line.lstrip())

                # Skip the function definition line
                i += 1

                # Skip all lines that are part of this function
                # (lines with greater indentation, or empty lines)
                while i < len(lines):
                    current_line = lines[i]

                    # If line is empty or whitespace-only, skip it
                    if not current_line.strip():
                        i += 1
                        continue

                    current_indent = len(current_line) - len(current_line.lstrip())

                    # If we hit something at same or lower indentation, we've left the function
                    if current_indent <= function_indent:
                        break

                    # Skip this line (it's part of the function)
                    i += 1

                removed_count += 1
                file_modified = True

                if removed_count % 10 == 0:
                    print(f"  Removed {removed_count} tests so far...")

                continue

            # Keep this line
            new_lines.append(line)
            i += 1

        # Write back if modified
        if file_modified:
            # Clean up multiple consecutive blank lines
            final_lines = []
            prev_blank = False
            for line in new_lines:
                is_blank = not line.strip()
                if is_blank and prev_blank:
                    continue  # Skip consecutive blank lines
                final_lines.append(line)
                prev_blank = is_blank

            test_file.write_text("\n".join(final_lines))
            files_modified += 1

    except Exception as e:
        print(f"  ERROR processing {test_file}: {e}")

print(f"\n✅ Removed {removed_count} skipped tests from {files_modified} files")
print(f"\nNext: Run 'poetry run pytest --collect-only -q' to verify")
