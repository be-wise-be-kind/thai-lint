"""
Purpose: Configuration merge utilities for init-config command

Scope: Functions for merging missing linter sections into existing config files

Overview: Provides utilities for the init-config command to add missing linter sections
    to existing configuration files without overwriting user customizations. Handles
    template parsing, section extraction, missing section identification, and content
    merging while preserving comments and formatting.

Dependencies: re for pattern matching, yaml for config parsing, click for output,
    pathlib for file operations

Exports: perform_merge, LINTER_SECTIONS

Interfaces: perform_merge(output_path, preset, output, generate_config_fn) -> None

Implementation: Text-based parsing and merging to preserve YAML comments
"""

import re
import sys
from collections.abc import Callable
from pathlib import Path

import click
import yaml

# Known linter section names that should be in the template
LINTER_SECTIONS = [
    "magic-numbers",
    "nesting",
    "srp",
    "dry",
    "file-placement",
    "print-statements",
    "stringly-typed",
    "file-header",
    "method-property",
    "stateless-class",
    "pipeline",
    "lazy-ignores",
]


def _is_section_header_line(line: str) -> bool:
    """Check if line is a section header (# ==== style comment)."""
    return line.startswith("# ===")


def _get_linter_section_name(line: str) -> str | None:
    """Extract linter section name from line if it's a known linter section."""
    section_match = re.match(r"^([a-z][a-z0-9-]*):$", line)
    if section_match and section_match.group(1) in LINTER_SECTIONS:
        return section_match.group(1)
    return None


def _is_buffer_line(line: str) -> bool:
    """Check if line should be buffered (comment or empty)."""
    stripped = line.strip()
    return stripped.startswith("#") or stripped == ""


def _save_current_section(
    sections: dict[str, str], current_section: str | None, current_content: list[str]
) -> None:
    """Save current section to sections dict if valid."""
    if current_section and current_content:
        sections[current_section] = "\n".join(current_content)


def _handle_section_header(
    line: str, sections: dict[str, str], current_section: str | None, current_content: list[str]
) -> tuple[str | None, list[str], list[str]]:
    """Handle a section header line (# === style)."""
    _save_current_section(sections, current_section, current_content)
    return None, [], [line]


def _start_linter_section(
    section_name: str, line: str, header_buffer: list[str]
) -> tuple[str | None, list[str], list[str]]:
    """Start a new linter section with the header buffer and section line."""
    return section_name, header_buffer + [line], []


def _handle_content_line(
    line: str, current_section: str | None, current_content: list[str], header_buffer: list[str]
) -> tuple[str | None, list[str], list[str]]:
    """Handle a regular content line."""
    if current_section:
        current_content.append(line)
        return current_section, current_content, header_buffer
    if _is_buffer_line(line):
        header_buffer.append(line)
        return current_section, current_content, header_buffer
    return current_section, current_content, []


def _process_template_line(
    line: str,
    sections: dict[str, str],
    current_section: str | None,
    current_content: list[str],
    header_buffer: list[str],
) -> tuple[str | None, list[str], list[str]]:
    """Process a single template line and update state."""
    if _is_section_header_line(line):
        return _handle_section_header(line, sections, current_section, current_content)

    section_name = _get_linter_section_name(line)
    if section_name:
        _save_current_section(sections, current_section, current_content)
        return _start_linter_section(section_name, line, header_buffer)

    return _handle_content_line(line, current_section, current_content, header_buffer)


def extract_linter_sections(template: str) -> dict[str, str]:
    """Extract each linter section from template as text blocks.

    Args:
        template: Full template content

    Returns:
        Dict mapping section name to section content (with header comments)
    """
    sections: dict[str, str] = {}
    lines = template.split("\n")
    current_section: str | None = None
    current_content: list[str] = []
    header_buffer: list[str] = []

    for line in lines:
        current_section, current_content, header_buffer = _process_template_line(
            line, sections, current_section, current_content, header_buffer
        )

    # Save last section
    if current_section and current_content:
        sections[current_section] = "\n".join(current_content)

    return sections


def identify_missing_sections(existing_config: dict, all_sections: list[str]) -> list[str]:
    """Identify which linter sections are missing from existing config.

    Args:
        existing_config: Parsed existing config dict
        all_sections: List of all linter section names

    Returns:
        List of section names missing from existing config
    """
    return [s for s in all_sections if s not in existing_config]


def _find_global_settings_position(content: str) -> int:
    """Find position of GLOBAL SETTINGS section in content."""
    marker = "# ============================================================================\n# GLOBAL SETTINGS"
    return content.find(marker)


def _insert_before_global_settings(content: str, sections_text: str, insert_pos: int) -> str:
    """Insert sections before GLOBAL SETTINGS marker."""
    return content[:insert_pos] + sections_text + "\n\n" + content[insert_pos:]


def merge_config_sections(existing_content: str, missing_sections: dict[str, str]) -> str:
    """Merge missing sections into existing config content.

    Args:
        existing_content: Original config file content
        missing_sections: Dict of section name -> section content to add

    Returns:
        Merged config content with missing sections appended
    """
    if not missing_sections:
        return existing_content

    sections_text = "\n".join(missing_sections.values())
    insert_pos = _find_global_settings_position(existing_content)

    if insert_pos > 0:
        return _insert_before_global_settings(existing_content, sections_text, insert_pos)
    return existing_content.rstrip() + "\n\n" + sections_text + "\n"


def _parse_existing_config(content: str, output: str) -> dict:
    """Parse existing config file content as YAML."""
    try:
        return yaml.safe_load(content) or {}
    except yaml.YAMLError:
        click.echo(f"Error: Could not parse {output} as YAML", err=True)
        click.echo("Use --force to overwrite with a fresh config", err=True)
        sys.exit(1)


def _build_missing_sections_dict(
    missing_names: list[str], template_sections: dict[str, str]
) -> dict[str, str]:
    """Build dict of missing section name -> content."""
    return {name: template_sections[name] for name in missing_names if name in template_sections}


def _report_merge_results(missing_names: list[str], output: str) -> None:
    """Report which sections were added."""
    click.echo(f"Added {len(missing_names)} missing linter section(s) to {output}:")
    for name in missing_names:
        click.echo(f"  - {name}")


def perform_merge(
    output_path: Path, preset: str, output: str, generate_config_fn: Callable[[str], str]
) -> None:
    """Merge missing linter sections into existing config.

    Args:
        output_path: Path to existing config file
        preset: Preset to use for missing sections
        output: Output filename for display
        generate_config_fn: Function to generate config content from preset
    """
    existing_content = output_path.read_text(encoding="utf-8")
    existing_config = _parse_existing_config(existing_content, output)

    template_sections = extract_linter_sections(generate_config_fn(preset))
    missing_names = identify_missing_sections(existing_config, list(template_sections.keys()))

    if not missing_names:
        click.echo(f"{output} already contains all linter sections")
        return

    missing_sections = _build_missing_sections_dict(missing_names, template_sections)
    merged_content = merge_config_sections(existing_content, missing_sections)
    output_path.write_text(merged_content, encoding="utf-8")

    _report_merge_results(missing_names, output)
