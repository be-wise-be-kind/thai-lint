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
from typing import NamedTuple

import pytest

from src.core.types import Severity, Violation

# =============================================================================
# Test Data
# =============================================================================


class EdgeCaseTestCase(NamedTuple):
    """Test case for edge case violations."""

    rule_id: str
    file_path: str
    line: int
    column: int
    message: str
    expected_column: int | None
    description: str


EDGE_CASE_VIOLATIONS = [
    EdgeCaseTestCase(
        rule_id="test.rule",
        file_path="test.py",
        line=1,
        column=0,
        message="Test",
        expected_column=1,
        description="zero_column_to_one_indexed",
    ),
    EdgeCaseTestCase(
        rule_id="test.rule",
        file_path="test.py",
        line=999999,
        column=0,
        message="Test",
        expected_column=1,
        description="large_line_number",
    ),
    EdgeCaseTestCase(
        rule_id="test.rule",
        file_path="test.py",
        line=1,
        column=9999,
        message="Test",
        expected_column=10000,
        description="large_column_number",
    ),
]

SPECIAL_CHARACTER_CASES = [
    EdgeCaseTestCase(
        rule_id="test.rule",
        file_path="test.py",
        line=1,
        column=0,
        message='Message with "quotes" and <brackets> and & ampersand',
        expected_column=None,
        description="special_characters_in_message",
    ),
    EdgeCaseTestCase(
        rule_id="test.rule",
        file_path="src/日本語.py",
        line=1,
        column=0,
        message="Test",
        expected_column=None,
        description="unicode_in_file_path",
    ),
    EdgeCaseTestCase(
        rule_id="test.rule",
        file_path="test.py",
        line=1,
        column=0,
        message="Message with émojis 🎉 and ñ characters",
        expected_column=None,
        description="unicode_in_message",
    ),
    EdgeCaseTestCase(
        rule_id="test.rule",
        file_path="test.py",
        line=1,
        column=0,
        message="Line 1\nLine 2\nLine 3",
        expected_column=None,
        description="newlines_in_message",
    ),
    EdgeCaseTestCase(
        rule_id="test.rule",
        file_path="",
        line=1,
        column=0,
        message="Test",
        expected_column=None,
        description="empty_file_path",
    ),
    EdgeCaseTestCase(
        rule_id="file-placement.misplaced-file.test-in-src",
        file_path="test.py",
        line=1,
        column=0,
        message="Test",
        expected_column=None,
        description="rule_id_with_multiple_dots",
    ),
]


# =============================================================================
# TestDocumentStructure: SARIF document requirements
# =============================================================================


class TestDocumentStructure:
    """Tests for SARIF document structure requirements."""

    @pytest.mark.parametrize(
        "field",
        ["version", "$schema", "runs"],
        ids=["has_version", "has_schema", "has_runs"],
    )
    def test_sarif_document_has_required_field(self, formatter, sample_violation, field):
        """SARIF document must have required fields."""
        sarif_doc = formatter.format([sample_violation])
        assert field in sarif_doc

    def test_sarif_version_is_2_1_0(self, formatter, sample_violation):
        """SARIF version must be exactly 2.1.0."""
        sarif_doc = formatter.format([sample_violation])
        assert sarif_doc["version"] == "2.1.0"

    def test_sarif_schema_uri_is_correct(self, formatter, sample_violation):
        """SARIF $schema must point to 2.1.0 schema."""
        sarif_doc = formatter.format([sample_violation])
        expected_schema = (
            "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/"
            "main/sarif-2.1/schema/sarif-schema-2.1.0.json"
        )
        assert sarif_doc["$schema"] == expected_schema

    def test_sarif_runs_is_list_with_one_element(self, formatter, sample_violation):
        """SARIF runs must be a list with exactly one run."""
        sarif_doc = formatter.format([sample_violation])
        assert isinstance(sarif_doc["runs"], list)
        assert len(sarif_doc["runs"]) == 1

    @pytest.mark.parametrize(
        "field",
        ["tool", "results"],
        ids=["has_tool", "has_results"],
    )
    def test_sarif_run_has_required_field(self, formatter, sample_violation, field):
        """SARIF run must have tool and results fields."""
        sarif_doc = formatter.format([sample_violation])
        run = sarif_doc["runs"][0]
        assert field in run

    def test_sarif_results_is_list(self, formatter, sample_violation):
        """SARIF results must be a list."""
        sarif_doc = formatter.format([sample_violation])
        run = sarif_doc["runs"][0]
        assert isinstance(run["results"], list)

    def test_sarif_empty_violations_produces_empty_results(self, formatter, empty_violations):
        """Empty violations list produces empty results array."""
        sarif_doc = formatter.format(empty_violations)
        run = sarif_doc["runs"][0]
        assert len(run["results"]) == 0

    def test_sarif_multiple_violations_produces_multiple_results(
        self, formatter, multiple_violations
    ):
        """Multiple violations produce multiple results."""
        sarif_doc = formatter.format(multiple_violations)
        run = sarif_doc["runs"][0]
        assert len(run["results"]) == 2

    def test_sarif_document_is_valid_json(self, formatter, sample_violation):
        """SARIF document can be serialized to JSON."""
        sarif_doc = formatter.format([sample_violation])
        json_str = json.dumps(sarif_doc)
        assert len(json_str) > 0


# =============================================================================
# TestToolMetadata: SARIF tool metadata requirements
# =============================================================================


class TestToolMetadata:
    """Tests for SARIF tool metadata requirements."""

    def test_sarif_tool_has_driver(self, formatter, sample_violation):
        """SARIF tool must have driver field."""
        sarif_doc = formatter.format([sample_violation])
        tool = sarif_doc["runs"][0]["tool"]
        assert "driver" in tool

    @pytest.mark.parametrize(
        "field",
        ["name", "version", "informationUri", "rules"],
        ids=["has_name", "has_version", "has_informationUri", "has_rules"],
    )
    def test_sarif_driver_has_required_field(self, formatter, sample_violation, field):
        """SARIF driver must have required fields."""
        sarif_doc = formatter.format([sample_violation])
        driver = sarif_doc["runs"][0]["tool"]["driver"]
        assert field in driver

    def test_sarif_driver_name_is_thai_lint(self, formatter, sample_violation):
        """SARIF driver name must be 'thai-lint'."""
        sarif_doc = formatter.format([sample_violation])
        driver = sarif_doc["runs"][0]["tool"]["driver"]
        assert driver["name"] == "thai-lint"

    def test_sarif_driver_version_is_valid_string(self, formatter, sample_violation):
        """SARIF driver version must be a non-empty string."""
        sarif_doc = formatter.format([sample_violation])
        driver = sarif_doc["runs"][0]["tool"]["driver"]
        assert isinstance(driver["version"], str)
        assert len(driver["version"]) > 0

    def test_sarif_driver_information_uri_is_valid_url(self, formatter, sample_violation):
        """SARIF driver informationUri must be a valid HTTPS URL."""
        sarif_doc = formatter.format([sample_violation])
        driver = sarif_doc["runs"][0]["tool"]["driver"]
        assert driver["informationUri"].startswith("https://")

    def test_sarif_driver_rules_is_list(self, formatter, sample_violation):
        """SARIF driver rules must be a list."""
        sarif_doc = formatter.format([sample_violation])
        driver = sarif_doc["runs"][0]["tool"]["driver"]
        assert isinstance(driver["rules"], list)

    def test_sarif_rules_contains_violation_rule_id(self, formatter, sample_violation):
        """SARIF rules must include rule metadata for violation."""
        sarif_doc = formatter.format([sample_violation])
        driver = sarif_doc["runs"][0]["tool"]["driver"]
        rule_ids = [rule["id"] for rule in driver["rules"]]
        assert sample_violation.rule_id in rule_ids

    def test_sarif_rule_has_short_description(self, formatter, sample_violation):
        """SARIF rule should have shortDescription with text."""
        sarif_doc = formatter.format([sample_violation])
        driver = sarif_doc["runs"][0]["tool"]["driver"]
        rule = driver["rules"][0]
        assert "shortDescription" in rule
        assert "text" in rule["shortDescription"]

    def test_sarif_driver_version_matches_package(self, formatter, sample_violation):
        """SARIF driver version should match thai-lint package version."""
        from src import __version__

        sarif_doc = formatter.format([sample_violation])
        driver = sarif_doc["runs"][0]["tool"]["driver"]
        assert driver["version"] == __version__


# =============================================================================
# TestResultConversion: SARIF result conversion from Violation objects
# =============================================================================


class TestResultConversion:
    """Tests for SARIF result conversion from Violation objects."""

    @pytest.mark.parametrize(
        "field",
        ["ruleId", "level", "message", "locations"],
        ids=["has_ruleId", "has_level", "has_message", "has_locations"],
    )
    def test_sarif_result_has_required_field(self, formatter, sample_violation, field):
        """SARIF result must have required fields."""
        sarif_doc = formatter.format([sample_violation])
        result = sarif_doc["runs"][0]["results"][0]
        assert field in result

    def test_sarif_result_rule_id_matches_violation(self, formatter, sample_violation):
        """SARIF result ruleId must match Violation.rule_id."""
        sarif_doc = formatter.format([sample_violation])
        result = sarif_doc["runs"][0]["results"][0]
        assert result["ruleId"] == sample_violation.rule_id

    def test_sarif_result_level_is_error(self, formatter, sample_violation):
        """SARIF result level must be 'error' for ERROR severity."""
        sarif_doc = formatter.format([sample_violation])
        result = sarif_doc["runs"][0]["results"][0]
        assert result["level"] == "error"

    def test_sarif_result_message_has_text(self, formatter, sample_violation):
        """SARIF result message must have text field matching violation."""
        sarif_doc = formatter.format([sample_violation])
        result = sarif_doc["runs"][0]["results"][0]
        assert "text" in result["message"]
        assert result["message"]["text"] == sample_violation.message

    def test_sarif_result_locations_is_list_with_one_element(self, formatter, sample_violation):
        """SARIF result locations must be a list with one element."""
        sarif_doc = formatter.format([sample_violation])
        result = sarif_doc["runs"][0]["results"][0]
        assert isinstance(result["locations"], list)
        assert len(result["locations"]) == 1

    def test_sarif_result_location_has_physical_location(self, formatter, sample_violation):
        """SARIF result location must have physicalLocation."""
        sarif_doc = formatter.format([sample_violation])
        result = sarif_doc["runs"][0]["results"][0]
        location = result["locations"][0]
        assert "physicalLocation" in location

    def test_sarif_result_preserves_violation_order(self, formatter, multiple_violations):
        """SARIF results must preserve violation order."""
        sarif_doc = formatter.format(multiple_violations)
        results = sarif_doc["runs"][0]["results"]
        assert results[0]["ruleId"] == multiple_violations[0].rule_id
        assert results[1]["ruleId"] == multiple_violations[1].rule_id


# =============================================================================
# TestLocationMapping: SARIF location mapping from Violation objects
# =============================================================================


class TestLocationMapping:
    """Tests for SARIF location mapping from Violation objects."""

    @pytest.mark.parametrize(
        "nested_path,expected_key",
        [
            (["physicalLocation", "artifactLocation"], "artifactLocation"),
            (["physicalLocation", "region"], "region"),
        ],
        ids=["has_artifactLocation", "has_region"],
    )
    def test_sarif_physical_location_has_required_field(
        self, formatter, sample_violation, nested_path, expected_key
    ):
        """SARIF physicalLocation must have required nested fields."""
        sarif_doc = formatter.format([sample_violation])
        result = sarif_doc["runs"][0]["results"][0]
        phys_loc = result["locations"][0]["physicalLocation"]
        assert expected_key in phys_loc

    def test_sarif_artifact_location_has_uri(self, formatter, sample_violation):
        """SARIF artifactLocation must have uri field."""
        sarif_doc = formatter.format([sample_violation])
        result = sarif_doc["runs"][0]["results"][0]
        artifact = result["locations"][0]["physicalLocation"]["artifactLocation"]
        assert "uri" in artifact

    def test_sarif_artifact_uri_matches_file_path(self, formatter, sample_violation):
        """SARIF artifactLocation uri must match Violation.file_path."""
        sarif_doc = formatter.format([sample_violation])
        result = sarif_doc["runs"][0]["results"][0]
        artifact = result["locations"][0]["physicalLocation"]["artifactLocation"]
        assert artifact["uri"] == sample_violation.file_path

    @pytest.mark.parametrize(
        "field",
        ["startLine", "startColumn"],
        ids=["has_startLine", "has_startColumn"],
    )
    def test_sarif_region_has_required_field(self, formatter, sample_violation, field):
        """SARIF region must have required fields."""
        sarif_doc = formatter.format([sample_violation])
        result = sarif_doc["runs"][0]["results"][0]
        region = result["locations"][0]["physicalLocation"]["region"]
        assert field in region

    def test_sarif_region_start_line_matches_violation(self, formatter, sample_violation):
        """SARIF region startLine must match Violation.line."""
        sarif_doc = formatter.format([sample_violation])
        result = sarif_doc["runs"][0]["results"][0]
        region = result["locations"][0]["physicalLocation"]["region"]
        assert region["startLine"] == sample_violation.line

    def test_sarif_region_start_column_is_one_indexed(self, formatter, sample_violation):
        """SARIF region startColumn must be 1-indexed (Violation.column + 1)."""
        sarif_doc = formatter.format([sample_violation])
        result = sarif_doc["runs"][0]["results"][0]
        region = result["locations"][0]["physicalLocation"]["region"]
        assert region["startColumn"] == sample_violation.column + 1

    @pytest.mark.parametrize(
        "case",
        EDGE_CASE_VIOLATIONS,
        ids=[c.description for c in EDGE_CASE_VIOLATIONS],
    )
    def test_sarif_handles_column_edge_cases(self, formatter, case):
        """SARIF must handle column edge cases correctly."""
        violation = Violation(
            rule_id=case.rule_id,
            file_path=case.file_path,
            line=case.line,
            column=case.column,
            message=case.message,
            severity=Severity.ERROR,
        )
        sarif_doc = formatter.format([violation])
        result = sarif_doc["runs"][0]["results"][0]
        region = result["locations"][0]["physicalLocation"]["region"]
        assert region["startColumn"] == case.expected_column
        assert region["startLine"] == case.line


# =============================================================================
# TestEdgeCases: Special scenarios and edge cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    @pytest.mark.parametrize(
        "case",
        SPECIAL_CHARACTER_CASES,
        ids=[c.description for c in SPECIAL_CHARACTER_CASES],
    )
    def test_sarif_handles_special_characters(self, formatter, case):
        """SARIF must handle special characters correctly."""
        violation = Violation(
            rule_id=case.rule_id,
            file_path=case.file_path,
            line=case.line,
            column=case.column,
            message=case.message,
            severity=Severity.ERROR,
        )
        sarif_doc = formatter.format([violation])
        result = sarif_doc["runs"][0]["results"][0]

        # Message should be preserved exactly
        assert result["message"]["text"] == case.message
        # File path should be preserved exactly
        artifact = result["locations"][0]["physicalLocation"]["artifactLocation"]
        assert artifact["uri"] == case.file_path
        # Rule ID should be preserved exactly
        assert result["ruleId"] == case.rule_id

    def test_sarif_handles_none_suggestion(self, formatter, make_violation):
        """SARIF must handle None suggestion gracefully."""
        violation = make_violation(suggestion=None)
        sarif_doc = formatter.format([violation])
        result = sarif_doc["runs"][0]["results"][0]
        assert result["message"]["text"] == "Test"

    def test_sarif_handles_very_long_messages(self, formatter, make_violation):
        """SARIF must preserve very long messages."""
        long_message = "A" * 10000
        violation = make_violation(message=long_message)
        sarif_doc = formatter.format([violation])
        result = sarif_doc["runs"][0]["results"][0]
        assert result["message"]["text"] == long_message

    def test_sarif_deduplicates_rules(self, formatter):
        """SARIF rules array must deduplicate repeated rule IDs."""
        violations = [
            Violation("test.rule-a", "file1.py", 1, 0, "Msg 1", Severity.ERROR),
            Violation("test.rule-a", "file2.py", 2, 0, "Msg 2", Severity.ERROR),
            Violation("test.rule-b", "file3.py", 3, 0, "Msg 3", Severity.ERROR),
        ]
        sarif_doc = formatter.format(violations)
        driver = sarif_doc["runs"][0]["tool"]["driver"]
        rule_ids = [rule["id"] for rule in driver["rules"]]
        assert len(rule_ids) == 2
        assert "test.rule-a" in rule_ids
        assert "test.rule-b" in rule_ids

    def test_sarif_formatter_is_reusable(self, formatter):
        """SarifFormatter instance can format multiple violation lists."""
        violations1 = [Violation("test.a", "file1.py", 1, 0, "Msg1", Severity.ERROR)]
        violations2 = [Violation("test.b", "file2.py", 2, 0, "Msg2", Severity.ERROR)]

        sarif1 = formatter.format(violations1)
        sarif2 = formatter.format(violations2)

        assert sarif1["version"] == "2.1.0"
        assert sarif2["version"] == "2.1.0"
        assert sarif1["runs"][0]["results"][0]["ruleId"] == "test.a"
        assert sarif2["runs"][0]["results"][0]["ruleId"] == "test.b"

    def test_sarif_json_serialization_roundtrip(self, formatter, sample_violation):
        """SARIF document survives JSON serialization roundtrip."""
        sarif_doc = formatter.format([sample_violation])
        json_str = json.dumps(sarif_doc)
        roundtrip_doc = json.loads(json_str)
        assert roundtrip_doc == sarif_doc


# =============================================================================
# TestJsonOutputFormat: SARIF JSON output formatting
# =============================================================================


class TestJsonOutputFormat:
    """Tests for SARIF JSON output formatting."""

    def test_sarif_output_is_dict(self, formatter, sample_violation):
        """SARIF formatter returns a dictionary."""
        sarif_doc = formatter.format([sample_violation])
        assert isinstance(sarif_doc, dict)

    def test_sarif_keys_are_strings(self, formatter, sample_violation):
        """All top-level keys in SARIF document are strings."""
        sarif_doc = formatter.format([sample_violation])
        for key in sarif_doc:
            assert isinstance(key, str)

    @pytest.mark.parametrize(
        "path",
        [
            ["version"],
            ["$schema"],
            ["runs"],
            ["runs", 0, "tool"],
            ["runs", 0, "results"],
        ],
        ids=["version", "schema", "runs", "tool", "results"],
    )
    def test_sarif_required_fields_not_none(self, formatter, sample_violation, path):
        """Required SARIF fields should not have None values."""
        sarif_doc = formatter.format([sample_violation])
        value = sarif_doc
        for key in path:
            value = value[key]
        assert value is not None
