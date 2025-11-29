"""
Purpose: Integration tests validating SARIF output across all thai-lint linters

Scope: All 5 linters (file-placement, nesting, srp, dry, magic-numbers) with SARIF output

Overview: End-to-end integration tests ensuring all thai-lint linters produce valid SARIF v2.1.0
    output. Tests each linter individually with --format sarif option, validates SARIF structure,
    verifies linter-specific rule IDs appear in output, and ensures consistency across linters.
    Following TDD methodology - tests written BEFORE implementation, all tests MUST FAIL initially.

Dependencies: pytest, click.testing.CliRunner, src.cli (all linter commands), json (parsing)

Exports: 10+ integration test functions for multi-linter SARIF validation

Interfaces: CLI testing runner, JSON parsing, temporary file creation

Implementation: TDD approach with comprehensive linter coverage, expects SARIF support in PR3
"""

import json

from click.testing import CliRunner

from src.cli import cli

# === File Placement Linter Tests ===


class TestFilePlacementSarifIntegration:
    """Integration tests for file-placement linter with SARIF output."""

    def test_file_placement_produces_valid_sarif(self, tmp_path) -> None:
        """file-placement linter produces valid SARIF output."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        test_file = src_dir / "test_utils.py"
        test_file.write_text("# test utilities")

        runner = CliRunner()
        result = runner.invoke(cli, ["file-placement", "--format", "sarif", str(tmp_path)])

        output = json.loads(result.output)
        assert output["version"] == "2.1.0"
        assert output["runs"][0]["tool"]["driver"]["name"] == "thai-lint"

    def test_file_placement_sarif_contains_rule_ids(self, tmp_path) -> None:
        """file-placement SARIF output contains file-placement rule IDs when violations found."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        test_file = src_dir / "test_file.py"
        test_file.write_text("# potentially misplaced file")

        runner = CliRunner()
        result = runner.invoke(cli, ["file-placement", "--format", "sarif", str(tmp_path)])

        output = json.loads(result.output)
        # If violations found, rule IDs should contain "file-placement"
        if output["runs"][0]["results"]:
            rule_id = output["runs"][0]["results"][0]["ruleId"]
            assert "file-placement" in rule_id


# === Nesting Linter Tests ===


class TestNestingSarifIntegration:
    """Integration tests for nesting linter with SARIF output."""

    def test_nesting_produces_valid_sarif(self, tmp_path) -> None:
        """nesting linter produces valid SARIF output."""
        test_file = tmp_path / "nested.py"
        test_file.write_text("""
def deeply_nested():
    for i in range(10):
        if i > 5:
            for j in range(5):
                if j > 2:
                    print(i, j)
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["nesting", "--format", "sarif", str(test_file)])

        output = json.loads(result.output)
        assert output["version"] == "2.1.0"
        assert output["runs"][0]["tool"]["driver"]["name"] == "thai-lint"

    def test_nesting_sarif_contains_rule_ids(self, tmp_path) -> None:
        """nesting SARIF output contains nesting rule IDs when violations found."""
        test_file = tmp_path / "deeply_nested.py"
        test_file.write_text("""
def very_deeply_nested():
    if True:
        for i in range(10):
            while True:
                if i > 5:
                    for j in range(5):
                        if j > 2:
                            if j > 3:
                                print(i, j)
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["nesting", "--format", "sarif", str(test_file)])

        output = json.loads(result.output)
        # If violations found, rule IDs should contain "nesting"
        if output["runs"][0]["results"]:
            rule_id = output["runs"][0]["results"][0]["ruleId"]
            assert "nesting" in rule_id


# === SRP Linter Tests ===


class TestSrpSarifIntegration:
    """Integration tests for srp linter with SARIF output."""

    def test_srp_produces_valid_sarif(self, tmp_path) -> None:
        """srp linter produces valid SARIF output."""
        test_file = tmp_path / "class_file.py"
        test_file.write_text("""
class SmallClass:
    def method1(self): pass
    def method2(self): pass
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["srp", "--format", "sarif", str(test_file)])

        output = json.loads(result.output)
        assert output["version"] == "2.1.0"
        assert output["runs"][0]["tool"]["driver"]["name"] == "thai-lint"

    def test_srp_sarif_contains_rule_ids(self, tmp_path) -> None:
        """srp SARIF output contains srp rule IDs when violations found."""
        # Create class with many methods to trigger SRP violation
        methods = "\n".join([f"    def method_{i}(self): pass" for i in range(20)])
        test_file = tmp_path / "large_class.py"
        test_file.write_text(f"""
class LargeClass:
{methods}
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["srp", "--format", "sarif", str(test_file)])

        output = json.loads(result.output)
        # If violations found, rule IDs should contain "srp"
        if output["runs"][0]["results"]:
            rule_id = output["runs"][0]["results"][0]["ruleId"]
            assert "srp" in rule_id


# === DRY Linter Tests ===


class TestDrySarifIntegration:
    """Integration tests for dry linter with SARIF output."""

    def test_dry_produces_valid_sarif(self, tmp_path) -> None:
        """dry linter produces valid SARIF output."""
        test_file = tmp_path / "duplicates.py"
        test_file.write_text("""
def func1():
    x = 1
    y = 2
    return x + y

def func2():
    x = 1
    y = 2
    return x + y
""")

        config = tmp_path / ".thailint.yaml"
        config.write_text("dry:\n  enabled: true\n  cache_enabled: false")

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["dry", "--format", "sarif", str(tmp_path), "--config", str(config)],
        )

        output = json.loads(result.output)
        assert output["version"] == "2.1.0"
        assert output["runs"][0]["tool"]["driver"]["name"] == "thai-lint"

    def test_dry_sarif_contains_rule_ids(self, tmp_path) -> None:
        """dry SARIF output contains dry rule IDs when violations found."""
        file1 = tmp_path / "file1.py"
        file1.write_text("""
def process():
    for item in items:
        if item.valid:
            item.save()
""")
        file2 = tmp_path / "file2.py"
        file2.write_text("""
def handle():
    for item in items:
        if item.valid:
            item.save()
""")

        config = tmp_path / ".thailint.yaml"
        config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["dry", "--format", "sarif", str(tmp_path), "--config", str(config)],
        )

        output = json.loads(result.output)
        # If violations found, rule IDs should start with "dry"
        if output["runs"][0]["results"]:
            rule_id = output["runs"][0]["results"][0]["ruleId"]
            assert rule_id.startswith("dry")


# === Magic Numbers Linter Tests ===


class TestMagicNumbersSarifIntegration:
    """Integration tests for magic-numbers linter with SARIF output."""

    def test_magic_numbers_produces_valid_sarif(self, tmp_path) -> None:
        """magic-numbers linter produces valid SARIF output."""
        test_file = tmp_path / "numbers.py"
        test_file.write_text("""
def calculate():
    timeout = 3600
    retries = 5
    return timeout * retries
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["magic-numbers", "--format", "sarif", str(test_file)])

        output = json.loads(result.output)
        assert output["version"] == "2.1.0"
        assert output["runs"][0]["tool"]["driver"]["name"] == "thai-lint"

    def test_magic_numbers_sarif_contains_rule_ids(self, tmp_path) -> None:
        """magic-numbers SARIF output contains magic-number rule IDs when violations found."""
        test_file = tmp_path / "magic.py"
        test_file.write_text("""
def calculate():
    timeout = 86400
    retries = 12345
    return timeout * retries
""")

        runner = CliRunner()
        result = runner.invoke(cli, ["magic-numbers", "--format", "sarif", str(test_file)])

        output = json.loads(result.output)
        # If violations found, rule IDs should contain "magic-number"
        if output["runs"][0]["results"]:
            rule_id = output["runs"][0]["results"][0]["ruleId"]
            assert "magic-number" in rule_id


# === Cross-Linter Consistency Tests ===


class TestCrossLinterSarifConsistency:
    """Tests for SARIF output consistency across all linters."""

    def test_all_linters_produce_same_sarif_version(self, tmp_path) -> None:
        """All linters produce SARIF version 2.1.0."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test file\nx = 1")

        config = tmp_path / ".thailint.yaml"
        config.write_text("dry:\n  enabled: true\n  cache_enabled: false")

        runner = CliRunner()
        linters = ["file-placement", "nesting", "srp", "dry", "magic-numbers"]
        versions = []

        for linter in linters:
            if linter == "dry":
                result = runner.invoke(
                    cli,
                    [linter, "--format", "sarif", str(tmp_path), "--config", str(config)],
                )
            else:
                result = runner.invoke(cli, [linter, "--format", "sarif", str(test_file)])
            output = json.loads(result.output)
            versions.append(output["version"])

        # All versions should be identical
        assert all(v == "2.1.0" for v in versions)

    def test_all_linters_produce_same_tool_name(self, tmp_path) -> None:
        """All linters produce SARIF with tool name 'thai-lint'."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test file\nx = 1")

        config = tmp_path / ".thailint.yaml"
        config.write_text("dry:\n  enabled: true\n  cache_enabled: false")

        runner = CliRunner()
        linters = ["file-placement", "nesting", "srp", "dry", "magic-numbers"]
        tool_names = []

        for linter in linters:
            if linter == "dry":
                result = runner.invoke(
                    cli,
                    [linter, "--format", "sarif", str(tmp_path), "--config", str(config)],
                )
            else:
                result = runner.invoke(cli, [linter, "--format", "sarif", str(test_file)])
            output = json.loads(result.output)
            tool_names.append(output["runs"][0]["tool"]["driver"]["name"])

        # All tool names should be "thai-lint"
        assert all(name == "thai-lint" for name in tool_names)

    def test_all_linters_have_results_array(self, tmp_path) -> None:
        """All linters produce SARIF with results array."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test file\nx = 1")

        config = tmp_path / ".thailint.yaml"
        config.write_text("dry:\n  enabled: true\n  cache_enabled: false")

        runner = CliRunner()
        linters = ["file-placement", "nesting", "srp", "dry", "magic-numbers"]

        for linter in linters:
            if linter == "dry":
                result = runner.invoke(
                    cli,
                    [linter, "--format", "sarif", str(tmp_path), "--config", str(config)],
                )
            else:
                result = runner.invoke(cli, [linter, "--format", "sarif", str(test_file)])
            output = json.loads(result.output)
            assert "results" in output["runs"][0], f"Linter {linter} missing results"
            assert isinstance(output["runs"][0]["results"], list)
