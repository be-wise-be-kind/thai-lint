"""
Purpose: Unit tests for mid-file comment block extraction used by the comment-antecedents rule

Scope: Grouping of contiguous comment lines below a file's header block across hash and slash comment syntaxes

Overview: Test suite covering the extraction stage of the comment-antecedents rule. Verifies that
    contiguous comment lines are grouped into a single block, that blank lines and code lines close a
    block, that the leading header block is skipped for hash-comment languages, that a shebang does not
    start a header, and that a Python module docstring is never treated as a comment block. Each test
    corresponds to one scenario in the Gherkin specification held in the feature roadmap. Extraction
    correctness is a precondition for every measured precision figure, because all baselines were
    measured at comment-block granularity rather than per line.

Dependencies: pytest, src.linters.file_header.comment_block_extractor

Exports: TestHashCommentBlocks, TestSlashCommentBlocks, TestHeaderSkipping, TestDegenerateFiles

Interfaces: Exercises extract_comment_blocks(content, suffix) -> list[CommentBlock]

Implementation: Arrange/act/assert bodies mapped one-to-one onto Given/When/Then scenario steps
"""


class TestHashCommentBlocks:
    """Test grouping of contiguous hash comment lines."""

    def test_contiguous_hash_comment_lines_form_a_single_block(self):
        """Should group three consecutive '#' lines below the header into one block."""
        code = "x = 1\n\n# first line\n# second line\n# third line\ny = 2\n"

        from src.linters.file_header.comment_block_extractor import extract_comment_blocks

        blocks = extract_comment_blocks(code, ".py")

        assert len(blocks) == 1

    def test_block_text_joins_the_lines_with_single_spaces(self):
        """Should join the comment lines into one text with single spaces."""
        code = "x = 1\n\n# first line\n# second line\n# third line\ny = 2\n"

        from src.linters.file_header.comment_block_extractor import extract_comment_blocks

        blocks = extract_comment_blocks(code, ".py")

        assert blocks[0].text == "first line second line third line"

    def test_block_start_line_is_the_first_comment_line(self):
        """Should report the line number of the first '#' line in the run."""
        code = "x = 1\n\n# first line\n# second line\n# third line\ny = 2\n"

        from src.linters.file_header.comment_block_extractor import extract_comment_blocks

        blocks = extract_comment_blocks(code, ".py")

        assert blocks[0].start_line == 3

    def test_a_blank_line_separates_two_blocks(self):
        """Should close a block when a blank line interrupts the comment run."""
        code = "#!/usr/bin/env bash\n# Purpose: header\n\necho hi\n# first run\n\n# second run\n"

        from src.linters.file_header.comment_block_extractor import extract_comment_blocks

        blocks = extract_comment_blocks(code, ".sh")

        assert len(blocks) == 2

    def test_a_code_line_separates_two_blocks(self):
        """Should close a block when a code line interrupts the comment run."""
        code = '# Purpose: header\n\n# first run\nresource "aws_s3_bucket" "b" {}\n# second run\n'

        from src.linters.file_header.comment_block_extractor import extract_comment_blocks

        blocks = extract_comment_blocks(code, ".tf")

        assert len(blocks) == 2


class TestSlashCommentBlocks:
    """Test grouping of contiguous slash comment lines."""

    def test_slash_comment_lines_form_blocks(self):
        """Should group two consecutive '//' lines below the header into one block."""
        code = "const a = 1;\n\n// first line\n// second line\nconst b = 2;\n"

        from src.linters.file_header.comment_block_extractor import extract_comment_blocks

        blocks = extract_comment_blocks(code, ".ts")

        assert len(blocks) == 1


class TestHeaderSkipping:
    """Test that a file's own header block is never returned as a comment block."""

    def test_the_leading_hash_comment_header_block_is_skipped(self):
        """Should skip the leading contiguous '#' run and return only the mid-file comment."""
        code = (
            "# Purpose: thing\n"
            "# Scope: thing\n"
            "# Overview: thing\n"
            "# Dependencies: none\n"
            "# Exports: none\n"
            "# Implementation: none\n"
            "\n"
            "echo hi\n"
            "# mid-file comment\n"
        )

        from src.linters.file_header.comment_block_extractor import extract_comment_blocks

        blocks = extract_comment_blocks(code, ".sh")

        assert len(blocks) == 1
        assert blocks[0].text == "mid-file comment"

    def test_a_shebang_does_not_start_the_header_block(self):
        """Should treat the run after a shebang as the header and skip it."""
        code = (
            "#!/usr/bin/env bash\n# Purpose: thing\n# Scope: thing\n\necho hi\n# mid-file comment\n"
        )

        from src.linters.file_header.comment_block_extractor import extract_comment_blocks

        blocks = extract_comment_blocks(code, ".sh")

        assert len(blocks) == 1
        assert blocks[0].text == "mid-file comment"

    def test_a_python_module_docstring_is_not_a_comment_block(self):
        """Should not treat a module docstring as a comment block."""
        code = '"""\nPurpose: thing\nOverview: the flag used to be a boolean\n"""\n\nx = 1\n'

        from src.linters.file_header.comment_block_extractor import extract_comment_blocks

        blocks = extract_comment_blocks(code, ".py")

        assert len(blocks) == 0


class TestDegenerateFiles:
    """Test extraction against files with no analysable content."""

    def test_an_empty_file_produces_no_blocks(self):
        """Should return no blocks for empty content."""
        from src.linters.file_header.comment_block_extractor import extract_comment_blocks

        blocks = extract_comment_blocks("", ".py")

        assert blocks == []

    def test_a_file_of_only_a_header_produces_no_blocks(self):
        """Should return no blocks when the file holds only a header block."""
        code = "# Purpose: thing\n# Scope: thing\n# Overview: thing\n"

        from src.linters.file_header.comment_block_extractor import extract_comment_blocks

        blocks = extract_comment_blocks(code, ".sh")

        assert blocks == []
