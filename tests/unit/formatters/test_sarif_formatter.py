"""
Purpose: Unit tests for SARIF v2.1.0 formatter implementation

Scope: SARIF document structure, field mappings, tool metadata, result conversion

Overview: Comprehensive test suite for SarifFormatter class validating SARIF v2.1.0 compliance.
    Tests document structure requirements (version, schema, runs), tool metadata (name, version,
    informationUri), result conversion from Violation objects, location mapping with proper indexing,
    and edge cases (empty violations, special characters). Following TDD methodology - tests written
    BEFORE implementation exists, all tests MUST FAIL initially, implementation in PR3 makes them pass.

Dependencies: pytest (testing), src.core.types.Violation (dataclass),
    src.formatters.sarif.SarifFormatter (NOT YET EXISTS)

Exports: 40+ test functions validating SARIF v2.1.0 compliance

Interfaces: pytest test discovery, parametrized tests, fixtures for sample violations

Implementation: TDD approach with comprehensive test coverage, expects SarifFormatter in PR3
"""

import json

import pytest

from src.core.types import Severity, Violation
from src.formatters.sarif import SarifFormatter

# === Fixtures ===


@pytest.fixture
def sample_violation() -> Violation:
    """Create a sample violation for testing."""
    return Violation(
        rule_id="test.rule-id",
        file_path="src/example.py",
        line=42,
        column=10,
        message="Test violation message",
        severity=Severity.ERROR,
        suggestion="Test suggestion",
    )


@pytest.fixture
def empty_violations() -> list[Violation]:
    """Empty violations list."""
    return []


@pytest.fixture
def multiple_violations() -> list[Violation]:
    """Multiple violations for testing."""
    return [
        Violation(
            rule_id="file-placement.misplaced-file",
            file_path="src/test_utils.py",
            line=1,
            column=0,
            message="Test file in src/ directory",
            severity=Severity.ERROR,
            suggestion="Move to tests/ directory",
        ),
        Violation(
            rule_id="nesting.excessive-depth",
            file_path="src/complex.py",
            line=15,
            column=4,
            message="Nesting depth of 5 exceeds maximum 4",
            severity=Severity.ERROR,
            suggestion=None,
        ),
    ]


# === Document Structure Tests (10 tests) ===


class TestDocumentStructure:
    """Tests for SARIF document structure requirements."""

    def test_sarif_document_has_required_fields(self, sample_violation: Violation) -> None:
        """SARIF document must have version, $schema, runs."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        assert "version" in sarif_doc
        assert "$schema" in sarif_doc
        assert "runs" in sarif_doc

    def test_sarif_version_is_2_1_0(self, sample_violation: Violation) -> None:
        """SARIF version must be exactly 2.1.0."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        assert sarif_doc["version"] == "2.1.0"

    def test_sarif_schema_uri_is_correct(self, sample_violation: Violation) -> None:
        """SARIF $schema must point to 2.1.0 schema."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        expected_schema = (
            "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/"
            "main/sarif-2.1/schema/sarif-schema-2.1.0.json"
        )
        assert sarif_doc["$schema"] == expected_schema

    def test_sarif_runs_is_list(self, sample_violation: Violation) -> None:
        """SARIF runs must be a list."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        assert isinstance(sarif_doc["runs"], list)

    def test_sarif_runs_has_one_element(self, sample_violation: Violation) -> None:
        """SARIF runs must have exactly one run for single invocation."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        assert len(sarif_doc["runs"]) == 1

    def test_sarif_run_has_tool_and_results(self, sample_violation: Violation) -> None:
        """SARIF run must have tool and results fields."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        run = sarif_doc["runs"][0]
        assert "tool" in run
        assert "results" in run

    def test_sarif_results_is_list(self, sample_violation: Violation) -> None:
        """SARIF results must be a list."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        run = sarif_doc["runs"][0]
        assert isinstance(run["results"], list)

    def test_sarif_empty_violations_produces_empty_results(
        self, empty_violations: list[Violation]
    ) -> None:
        """Empty violations list produces empty results array."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format(empty_violations)

        run = sarif_doc["runs"][0]
        assert len(run["results"]) == 0

    def test_sarif_multiple_violations_produces_multiple_results(
        self, multiple_violations: list[Violation]
    ) -> None:
        """Multiple violations produce multiple results."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format(multiple_violations)

        run = sarif_doc["runs"][0]
        assert len(run["results"]) == 2

    def test_sarif_document_is_valid_json(self, sample_violation: Violation) -> None:
        """SARIF document can be serialized to JSON."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        # Should not raise exception
        json_str = json.dumps(sarif_doc)
        assert len(json_str) > 0


# === Tool Metadata Tests (10 tests) ===


class TestToolMetadata:
    """Tests for SARIF tool metadata requirements."""

    def test_sarif_tool_has_driver(self, sample_violation: Violation) -> None:
        """SARIF tool must have driver field."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        tool = sarif_doc["runs"][0]["tool"]
        assert "driver" in tool

    def test_sarif_driver_has_name(self, sample_violation: Violation) -> None:
        """SARIF driver must have name field."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        driver = sarif_doc["runs"][0]["tool"]["driver"]
        assert "name" in driver

    def test_sarif_driver_name_is_thai_lint(self, sample_violation: Violation) -> None:
        """SARIF driver name must be 'thai-lint'."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        driver = sarif_doc["runs"][0]["tool"]["driver"]
        assert driver["name"] == "thai-lint"

    def test_sarif_driver_has_version(self, sample_violation: Violation) -> None:
        """SARIF driver must have version field."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        driver = sarif_doc["runs"][0]["tool"]["driver"]
        assert "version" in driver
        assert isinstance(driver["version"], str)
        assert len(driver["version"]) > 0

    def test_sarif_driver_has_information_uri(self, sample_violation: Violation) -> None:
        """SARIF driver must have informationUri field."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        driver = sarif_doc["runs"][0]["tool"]["driver"]
        assert "informationUri" in driver

    def test_sarif_driver_information_uri_is_valid_url(self, sample_violation: Violation) -> None:
        """SARIF driver informationUri must be a valid URL."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        driver = sarif_doc["runs"][0]["tool"]["driver"]
        uri = driver["informationUri"]
        assert uri.startswith("https://")

    def test_sarif_driver_has_rules_array(self, sample_violation: Violation) -> None:
        """SARIF driver should have rules array."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        driver = sarif_doc["runs"][0]["tool"]["driver"]
        assert "rules" in driver
        assert isinstance(driver["rules"], list)

    def test_sarif_rules_contains_violation_rule_id(self, sample_violation: Violation) -> None:
        """SARIF rules must include rule metadata for violation."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        driver = sarif_doc["runs"][0]["tool"]["driver"]
        rule_ids = [rule["id"] for rule in driver["rules"]]
        assert sample_violation.rule_id in rule_ids

    def test_sarif_rule_has_short_description(self, sample_violation: Violation) -> None:
        """SARIF rule should have shortDescription with text."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        driver = sarif_doc["runs"][0]["tool"]["driver"]
        rule = driver["rules"][0]
        assert "shortDescription" in rule
        assert "text" in rule["shortDescription"]

    def test_sarif_driver_version_matches_package(self, sample_violation: Violation) -> None:
        """SARIF driver version should match thai-lint package version."""
        from src import __version__

        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        driver = sarif_doc["runs"][0]["tool"]["driver"]
        assert driver["version"] == __version__


# === Result Conversion Tests (10 tests) ===


class TestResultConversion:
    """Tests for SARIF result conversion from Violation objects."""

    def test_sarif_result_has_rule_id(self, sample_violation: Violation) -> None:
        """SARIF result must have ruleId field."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        result = sarif_doc["runs"][0]["results"][0]
        assert "ruleId" in result

    def test_sarif_result_rule_id_matches_violation(self, sample_violation: Violation) -> None:
        """SARIF result ruleId must match Violation.rule_id."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        result = sarif_doc["runs"][0]["results"][0]
        assert result["ruleId"] == sample_violation.rule_id

    def test_sarif_result_has_level(self, sample_violation: Violation) -> None:
        """SARIF result must have level field."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        result = sarif_doc["runs"][0]["results"][0]
        assert "level" in result

    def test_sarif_result_level_is_error(self, sample_violation: Violation) -> None:
        """SARIF result level must be 'error' for ERROR severity."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        result = sarif_doc["runs"][0]["results"][0]
        assert result["level"] == "error"

    def test_sarif_result_has_message(self, sample_violation: Violation) -> None:
        """SARIF result must have message field."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        result = sarif_doc["runs"][0]["results"][0]
        assert "message" in result

    def test_sarif_result_message_has_text(self, sample_violation: Violation) -> None:
        """SARIF result message must have text field."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        result = sarif_doc["runs"][0]["results"][0]
        assert "text" in result["message"]

    def test_sarif_result_message_text_matches_violation(self, sample_violation: Violation) -> None:
        """SARIF result message text must match Violation.message."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        result = sarif_doc["runs"][0]["results"][0]
        assert result["message"]["text"] == sample_violation.message

    def test_sarif_result_has_locations(self, sample_violation: Violation) -> None:
        """SARIF result must have locations array."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        result = sarif_doc["runs"][0]["results"][0]
        assert "locations" in result
        assert isinstance(result["locations"], list)
        assert len(result["locations"]) == 1

    def test_sarif_result_location_has_physical_location(self, sample_violation: Violation) -> None:
        """SARIF result location must have physicalLocation."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        result = sarif_doc["runs"][0]["results"][0]
        location = result["locations"][0]
        assert "physicalLocation" in location

    def test_sarif_result_preserves_violation_order(
        self, multiple_violations: list[Violation]
    ) -> None:
        """SARIF results must preserve violation order."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format(multiple_violations)

        results = sarif_doc["runs"][0]["results"]
        assert results[0]["ruleId"] == multiple_violations[0].rule_id
        assert results[1]["ruleId"] == multiple_violations[1].rule_id


# === Location Mapping Tests (10 tests) ===


class TestLocationMapping:
    """Tests for SARIF location mapping from Violation objects."""

    def test_sarif_physical_location_has_artifact_location(
        self, sample_violation: Violation
    ) -> None:
        """SARIF physicalLocation must have artifactLocation."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        result = sarif_doc["runs"][0]["results"][0]
        phys_loc = result["locations"][0]["physicalLocation"]
        assert "artifactLocation" in phys_loc

    def test_sarif_artifact_location_has_uri(self, sample_violation: Violation) -> None:
        """SARIF artifactLocation must have uri field."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        result = sarif_doc["runs"][0]["results"][0]
        artifact = result["locations"][0]["physicalLocation"]["artifactLocation"]
        assert "uri" in artifact

    def test_sarif_artifact_uri_matches_file_path(self, sample_violation: Violation) -> None:
        """SARIF artifactLocation uri must match Violation.file_path."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        result = sarif_doc["runs"][0]["results"][0]
        artifact = result["locations"][0]["physicalLocation"]["artifactLocation"]
        assert artifact["uri"] == sample_violation.file_path

    def test_sarif_physical_location_has_region(self, sample_violation: Violation) -> None:
        """SARIF physicalLocation must have region field."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        result = sarif_doc["runs"][0]["results"][0]
        phys_loc = result["locations"][0]["physicalLocation"]
        assert "region" in phys_loc

    def test_sarif_region_has_start_line(self, sample_violation: Violation) -> None:
        """SARIF region must have startLine field."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        result = sarif_doc["runs"][0]["results"][0]
        region = result["locations"][0]["physicalLocation"]["region"]
        assert "startLine" in region

    def test_sarif_region_start_line_matches_violation(self, sample_violation: Violation) -> None:
        """SARIF region startLine must match Violation.line."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        result = sarif_doc["runs"][0]["results"][0]
        region = result["locations"][0]["physicalLocation"]["region"]
        assert region["startLine"] == sample_violation.line

    def test_sarif_region_has_start_column(self, sample_violation: Violation) -> None:
        """SARIF region must have startColumn field."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        result = sarif_doc["runs"][0]["results"][0]
        region = result["locations"][0]["physicalLocation"]["region"]
        assert "startColumn" in region

    def test_sarif_region_start_column_is_one_indexed(self, sample_violation: Violation) -> None:
        """SARIF region startColumn must be 1-indexed (Violation.column + 1)."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        result = sarif_doc["runs"][0]["results"][0]
        region = result["locations"][0]["physicalLocation"]["region"]
        # Violation.column is 0-indexed (10), SARIF is 1-indexed (11)
        assert region["startColumn"] == sample_violation.column + 1

    def test_sarif_handles_zero_column_correctly(self) -> None:
        """SARIF must convert column 0 to column 1 (1-indexed)."""
        violation = Violation(
            rule_id="test.rule",
            file_path="test.py",
            line=1,
            column=0,  # 0-indexed
            message="Test",
            severity=Severity.ERROR,
        )

        formatter = SarifFormatter()
        sarif_doc = formatter.format([violation])

        result = sarif_doc["runs"][0]["results"][0]
        region = result["locations"][0]["physicalLocation"]["region"]
        assert region["startColumn"] == 1  # 1-indexed

    def test_sarif_handles_large_line_numbers(self) -> None:
        """SARIF must handle large line numbers correctly."""
        violation = Violation(
            rule_id="test.rule",
            file_path="test.py",
            line=999999,
            column=0,
            message="Test",
            severity=Severity.ERROR,
        )

        formatter = SarifFormatter()
        sarif_doc = formatter.format([violation])

        result = sarif_doc["runs"][0]["results"][0]
        region = result["locations"][0]["physicalLocation"]["region"]
        assert region["startLine"] == 999999


# === Edge Case Tests (10+ tests) ===


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_sarif_handles_special_characters_in_message(self) -> None:
        """SARIF must handle special characters in message."""
        violation = Violation(
            rule_id="test.rule",
            file_path="test.py",
            line=1,
            column=0,
            message='Message with "quotes" and <brackets> and & ampersand',
            severity=Severity.ERROR,
        )

        formatter = SarifFormatter()
        sarif_doc = formatter.format([violation])

        result = sarif_doc["runs"][0]["results"][0]
        assert result["message"]["text"] == violation.message

    def test_sarif_handles_unicode_in_file_path(self) -> None:
        """SARIF must handle unicode characters in file path."""
        violation = Violation(
            rule_id="test.rule",
            file_path="src/日本語.py",
            line=1,
            column=0,
            message="Test",
            severity=Severity.ERROR,
        )

        formatter = SarifFormatter()
        sarif_doc = formatter.format([violation])

        result = sarif_doc["runs"][0]["results"][0]
        artifact = result["locations"][0]["physicalLocation"]["artifactLocation"]
        assert artifact["uri"] == "src/日本語.py"

    def test_sarif_handles_unicode_in_message(self) -> None:
        """SARIF must handle unicode characters in message."""
        violation = Violation(
            rule_id="test.rule",
            file_path="test.py",
            line=1,
            column=0,
            message="Message with émojis 🎉 and ñ characters",
            severity=Severity.ERROR,
        )

        formatter = SarifFormatter()
        sarif_doc = formatter.format([violation])

        result = sarif_doc["runs"][0]["results"][0]
        assert result["message"]["text"] == violation.message

    def test_sarif_handles_none_suggestion(self) -> None:
        """SARIF must handle None suggestion gracefully."""
        violation = Violation(
            rule_id="test.rule",
            file_path="test.py",
            line=1,
            column=0,
            message="Test",
            severity=Severity.ERROR,
            suggestion=None,  # Explicitly None
        )

        formatter = SarifFormatter()
        sarif_doc = formatter.format([violation])

        # Should not raise exception
        result = sarif_doc["runs"][0]["results"][0]
        assert result["message"]["text"] == "Test"

    def test_sarif_handles_large_column_numbers(self) -> None:
        """SARIF must handle large column numbers correctly."""
        violation = Violation(
            rule_id="test.rule",
            file_path="test.py",
            line=1,
            column=9999,  # 0-indexed
            message="Test",
            severity=Severity.ERROR,
        )

        formatter = SarifFormatter()
        sarif_doc = formatter.format([violation])

        result = sarif_doc["runs"][0]["results"][0]
        region = result["locations"][0]["physicalLocation"]["region"]
        assert region["startColumn"] == 10000  # 1-indexed

    def test_sarif_handles_very_long_messages(self) -> None:
        """SARIF must preserve very long messages."""
        long_message = "A" * 10000
        violation = Violation(
            rule_id="test.rule",
            file_path="test.py",
            line=1,
            column=0,
            message=long_message,
            severity=Severity.ERROR,
        )

        formatter = SarifFormatter()
        sarif_doc = formatter.format([violation])

        result = sarif_doc["runs"][0]["results"][0]
        assert result["message"]["text"] == long_message

    def test_sarif_deduplicates_rules(self) -> None:
        """SARIF rules array must deduplicate repeated rule IDs."""
        violations = [
            Violation("test.rule-a", "file1.py", 1, 0, "Msg 1", Severity.ERROR),
            Violation("test.rule-a", "file2.py", 2, 0, "Msg 2", Severity.ERROR),
            Violation("test.rule-b", "file3.py", 3, 0, "Msg 3", Severity.ERROR),
        ]

        formatter = SarifFormatter()
        sarif_doc = formatter.format(violations)

        driver = sarif_doc["runs"][0]["tool"]["driver"]
        rule_ids = [rule["id"] for rule in driver["rules"]]
        assert len(rule_ids) == 2  # Not 3 (rule-a deduplicated)
        assert "test.rule-a" in rule_ids
        assert "test.rule-b" in rule_ids

    def test_sarif_formatter_is_reusable(self) -> None:
        """SarifFormatter instance can format multiple violation lists."""
        formatter = SarifFormatter()

        violations1 = [Violation("test.a", "file1.py", 1, 0, "Msg1", Severity.ERROR)]
        violations2 = [Violation("test.b", "file2.py", 2, 0, "Msg2", Severity.ERROR)]

        sarif1 = formatter.format(violations1)
        sarif2 = formatter.format(violations2)

        # Both should be valid SARIF documents
        assert sarif1["version"] == "2.1.0"
        assert sarif2["version"] == "2.1.0"
        assert sarif1["runs"][0]["results"][0]["ruleId"] == "test.a"
        assert sarif2["runs"][0]["results"][0]["ruleId"] == "test.b"

    def test_sarif_handles_empty_file_path(self) -> None:
        """SARIF must handle empty file path."""
        violation = Violation(
            rule_id="test.rule",
            file_path="",
            line=1,
            column=0,
            message="Test",
            severity=Severity.ERROR,
        )

        formatter = SarifFormatter()
        sarif_doc = formatter.format([violation])

        result = sarif_doc["runs"][0]["results"][0]
        artifact = result["locations"][0]["physicalLocation"]["artifactLocation"]
        assert artifact["uri"] == ""

    def test_sarif_handles_rule_id_with_dots(self) -> None:
        """SARIF must handle rule IDs with multiple dots."""
        violation = Violation(
            rule_id="file-placement.misplaced-file.test-in-src",
            file_path="test.py",
            line=1,
            column=0,
            message="Test",
            severity=Severity.ERROR,
        )

        formatter = SarifFormatter()
        sarif_doc = formatter.format([violation])

        result = sarif_doc["runs"][0]["results"][0]
        assert result["ruleId"] == "file-placement.misplaced-file.test-in-src"

    def test_sarif_handles_newlines_in_message(self) -> None:
        """SARIF must handle newline characters in message."""
        violation = Violation(
            rule_id="test.rule",
            file_path="test.py",
            line=1,
            column=0,
            message="Line 1\nLine 2\nLine 3",
            severity=Severity.ERROR,
        )

        formatter = SarifFormatter()
        sarif_doc = formatter.format([violation])

        result = sarif_doc["runs"][0]["results"][0]
        assert result["message"]["text"] == "Line 1\nLine 2\nLine 3"

    def test_sarif_json_serialization_roundtrip(self, sample_violation: Violation) -> None:
        """SARIF document survives JSON serialization roundtrip."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        # Serialize and deserialize
        json_str = json.dumps(sarif_doc)
        roundtrip_doc = json.loads(json_str)

        # Should be identical
        assert roundtrip_doc == sarif_doc


# === JSON Output Format Tests ===


class TestJsonOutputFormat:
    """Tests for SARIF JSON output formatting."""

    def test_sarif_output_is_dict(self, sample_violation: Violation) -> None:
        """SARIF formatter returns a dictionary."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        assert isinstance(sarif_doc, dict)

    def test_sarif_keys_are_strings(self, sample_violation: Violation) -> None:
        """All top-level keys in SARIF document are strings."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        for key in sarif_doc:
            assert isinstance(key, str)

    def test_sarif_no_none_values_in_required_fields(self, sample_violation: Violation) -> None:
        """Required SARIF fields should not have None values."""
        formatter = SarifFormatter()
        sarif_doc = formatter.format([sample_violation])

        assert sarif_doc["version"] is not None
        assert sarif_doc["$schema"] is not None
        assert sarif_doc["runs"] is not None
        assert sarif_doc["runs"][0]["tool"] is not None
        assert sarif_doc["runs"][0]["results"] is not None
