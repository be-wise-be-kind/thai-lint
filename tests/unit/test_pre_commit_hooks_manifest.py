"""Unit tests validating the .pre-commit-hooks.yaml consumer manifest.

Purpose: Guarantee the repo-root .pre-commit-hooks.yaml stays valid and consumable as a
    pre-commit/prek `repo:` hook source

Scope: Structural and semantic validation of the .pre-commit-hooks.yaml manifest shipped at
    the repository root for downstream consumers

Overview: thai-lint ships a .pre-commit-hooks.yaml manifest so other repositories can pin and
    consume its linters via `repo: https://github.com/be-wise-be-kind/thai-lint`. This module
    validates that manifest end to end: it parses as a YAML list of hook mappings, every hook
    declares the mandatory pre-commit fields, every hook installs as a `language: python` hook,
    hook ids are unique and namespaced under `thailint-`, and every hook `entry` invokes the
    real `thailint` console script with a subcommand that is actually registered on the CLI.
    These checks prevent shipping a manifest that references a removed command or a malformed
    hook definition.

Dependencies: pytest for testing, PyYAML for manifest parsing, src.cli for the registered
    command set

Exports: Test classes covering manifest structure, hook field requirements, and command
    coverage

Interfaces: Reads .pre-commit-hooks.yaml from the repository root and inspects src.cli.cli
    Click command registry

Implementation: Loads the manifest once, then asserts per-hook invariants and cross-checks
    each entry subcommand against the live Click command group
"""

from pathlib import Path

import pytest
import yaml

from src.cli import cli

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / ".pre-commit-hooks.yaml"

REQUIRED_FIELDS = ("id", "name", "entry", "language")


def _load_manifest():
    """Parse the .pre-commit-hooks.yaml manifest into a list of hook mappings."""
    with MANIFEST_PATH.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _has_valid_types_or(hook):
    """Return True when the hook omits types_or or declares a non-empty list of strings."""
    if "types_or" not in hook:
        return True
    tags = hook["types_or"]
    return isinstance(tags, list) and bool(tags) and all(isinstance(tag, str) for tag in tags)


@pytest.fixture(scope="module")
def hooks():
    """Return the parsed list of hook definitions from the manifest."""
    return _load_manifest()


class TestManifestStructure:
    """Validate the top-level shape of the manifest."""

    def test_manifest_exists(self):
        """Manifest must exist at the repository root for `repo:` consumption."""
        assert MANIFEST_PATH.is_file()

    def test_manifest_is_nonempty_list(self, hooks):
        """Manifest must be a non-empty list of hook mappings."""
        assert isinstance(hooks, list)
        assert hooks
        assert all(isinstance(hook, dict) for hook in hooks)

    def test_hook_ids_are_unique(self, hooks):
        """Duplicate hook ids would make hooks unselectable by consumers."""
        ids = [hook["id"] for hook in hooks]
        assert len(ids) == len(set(ids))


class TestHookFields:
    """Validate required fields on every hook definition."""

    def test_all_hooks_have_required_fields(self, hooks):
        """Every hook must declare id, name, entry, and language."""
        for hook in hooks:
            for field in REQUIRED_FIELDS:
                assert field in hook, f"hook {hook.get('id')!r} missing {field!r}"

    def test_all_hooks_are_language_python(self, hooks):
        """Hooks must install as language: python for runner-agnostic, pinnable use."""
        for hook in hooks:
            assert hook["language"] == "python", hook["id"]

    def test_all_hook_ids_are_thailint_namespaced(self, hooks):
        """Hook ids must be namespaced under thailint- to avoid consumer collisions."""
        for hook in hooks:
            assert hook["id"].startswith("thailint-"), hook["id"]

    def test_types_or_filters_are_string_lists(self, hooks):
        """When present, types_or must be a non-empty list of identify tag strings."""
        invalid = [hook["id"] for hook in hooks if not _has_valid_types_or(hook)]
        assert not invalid, invalid


class TestEntryCommandCoverage:
    """Cross-check hook entries against the live CLI command registry."""

    def test_entries_invoke_thailint_console_script(self, hooks):
        """Every entry must invoke the `thailint` console script."""
        for hook in hooks:
            assert hook["entry"].split()[0] == "thailint", hook["id"]

    def test_entry_subcommands_are_registered(self, hooks):
        """Each entry subcommand must be a real, registered CLI command."""
        registered = set(cli.commands.keys())
        for hook in hooks:
            subcommand = hook["entry"].split()[1]
            assert subcommand in registered, f"{hook['id']}: unknown command {subcommand!r}"

    def test_no_deprecated_commands_referenced(self, hooks):
        """Manifest must not surface deprecated aliases to consumers."""
        deprecated = {"print-statements"}
        for hook in hooks:
            subcommand = hook["entry"].split()[1]
            assert subcommand not in deprecated, hook["id"]
