"""
Purpose: Unit tests for the first-class optional Tags header field

Scope: Testing Tags field recognition and controlled-vocabulary validation

Overview: Test suite for the optional Tags header field across the file header linter.
    Verifies that Tags is optional by default (a header without Tags lints clean and a
    header with any Tags value is accepted when no vocabulary is configured), and that an
    optional controlled vocabulary configured via allowed_tags reports any tag outside the
    list as a violation while accepting in-vocabulary tags. Covers comma-separated tag
    parsing and whitespace handling.

Dependencies: pytest, conftest.create_mock_context, src.linters.file_header.linter.FileHeaderRule

Exports: TestTagsOptional, TestAllowedTagsVocabulary test classes

Interfaces: test_tags_not_required_by_default, test_rejects_tag_outside_vocabulary,
    test_accepts_tags_in_vocabulary, and other test methods

Implementation: Uses mock contexts with metadata for allowed_tags configuration, validates
    optional Tags behavior and controlled-vocabulary enforcement
"""

from tests.unit.linters.file_header.conftest import create_mock_context

PY_HEADER_WITH_TAGS = '''"""
Purpose: Order history view module.
Scope: Customer portal order history.
Overview: Renders the order-history table and paginates results server-side
    for the customer portal.
Dependencies: flask, sqlalchemy
Exports: render_orders
Interfaces: render_orders(customer_id)
Implementation: Server-side pagination with row-level links.
Tags: {tags}
"""
'''

PY_HEADER_NO_TAGS = '''"""
Purpose: Order history view module.
Scope: Customer portal order history.
Overview: Renders the order-history table and paginates results server-side
    for the customer portal.
Dependencies: flask, sqlalchemy
Exports: render_orders
Interfaces: render_orders(customer_id)
Implementation: Server-side pagination with row-level links.
"""
'''


class TestTagsOptional:
    """Test that Tags is an optional field."""

    def test_tags_not_required_by_default(self):
        """A header without Tags should lint clean (Tags is optional)."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(PY_HEADER_NO_TAGS, "orders.py", "python")
        violations = rule.check(context)

        tags_violations = [v for v in violations if "tag" in v.message.lower()]
        assert len(tags_violations) == 0, "Tags should be optional"
        missing = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing) == 0, "All required fields present, none missing"

    def test_any_tags_value_accepted_without_vocabulary(self):
        """With no allowed_tags configured, any Tags value is accepted."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        code = PY_HEADER_WITH_TAGS.format(tags="anything, goes-here, freeform")
        context = create_mock_context(code, "orders.py", "python")
        violations = rule.check(context)

        tags_violations = [v for v in violations if "tag" in v.message.lower()]
        assert len(tags_violations) == 0, "Any tag accepted when no vocabulary configured"


class TestAllowedTagsVocabulary:
    """Test optional controlled-vocabulary validation via allowed_tags."""

    def test_rejects_tag_outside_vocabulary(self):
        """A tag outside allowed_tags should be reported."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        code = PY_HEADER_WITH_TAGS.format(tags="customer-portal, not-a-real-tag")
        context = create_mock_context(
            code,
            "orders.py",
            "python",
            metadata={"file_header": {"allowed_tags": ["customer-portal", "orders"]}},
        )
        violations = rule.check(context)

        tags_violations = [v for v in violations if "not-a-real-tag" in v.message]
        assert len(tags_violations) >= 1, "Tag outside vocabulary should be reported"

    def test_accepts_tags_in_vocabulary(self):
        """Tags within allowed_tags should be accepted."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        code = PY_HEADER_WITH_TAGS.format(tags="customer-portal, orders")
        context = create_mock_context(
            code,
            "orders.py",
            "python",
            metadata={"file_header": {"allowed_tags": ["customer-portal", "orders"]}},
        )
        violations = rule.check(context)

        tags_violations = [v for v in violations if "tag" in v.message.lower()]
        assert len(tags_violations) == 0, "In-vocabulary tags should be accepted"

    def test_handles_whitespace_in_tag_list(self):
        """Comma-separated tags with extra whitespace should parse correctly."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        code = PY_HEADER_WITH_TAGS.format(tags="customer-portal ,  orders")
        context = create_mock_context(
            code,
            "orders.py",
            "python",
            metadata={"file_header": {"allowed_tags": ["customer-portal", "orders"]}},
        )
        violations = rule.check(context)

        tags_violations = [v for v in violations if "tag" in v.message.lower()]
        assert len(tags_violations) == 0, "Whitespace around tags should be stripped"

    def test_no_tags_field_with_vocabulary_configured(self):
        """A file without Tags should not error even when allowed_tags is set."""
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(
            PY_HEADER_NO_TAGS,
            "orders.py",
            "python",
            metadata={"file_header": {"allowed_tags": ["customer-portal", "orders"]}},
        )
        violations = rule.check(context)

        tags_violations = [v for v in violations if "tag" in v.message.lower()]
        assert len(tags_violations) == 0, "Absent Tags is fine even with vocabulary configured"
