import tempfile
from pathlib import Path

import pytest

from parse import (
    build_stem_mapping,
    escape_markdown_cell,
    format_table_as_markdown,
    resolve_output_path,
    sanitize_filename,
)


class TestSanitizeFilename:
    def test_normal_filename(self):
        assert sanitize_filename("report") == "report"

    def test_special_chars(self):
        assert sanitize_filename('a?b*c<d>e"f/g\\h|i') == "a_b_c_d_e_f_g_h_i"

    def test_leading_trailing_dots_spaces(self):
        assert sanitize_filename("...file...") == "file"
        assert sanitize_filename("   file   ") == "file"

    def test_empty_result(self):
        assert sanitize_filename("???") == "___"

    def test_long_filename(self):
        long_name = "a" * 300
        result = sanitize_filename(long_name)
        assert len(result) == 200


class TestBuildStemMapping:
    def test_no_collision(self):
        files = [Path("/tmp/report.pdf"), Path("/tmp/data.pdf")]
        mapping = build_stem_mapping(files)
        assert len(mapping) == 2
        assert len(mapping["report"]) == 1
        assert len(mapping["data"]) == 1

    def test_special_char_collision(self):
        files = [Path("/tmp/a?b.pdf"), Path("/tmp/a*b.pdf")]
        mapping = build_stem_mapping(files)
        assert len(mapping) == 1
        assert len(mapping["a_b"]) == 2

    def test_case_insensitive_collision(self):
        files = [Path("/tmp/Foo.pdf"), Path("/tmp/foo.pdf")]
        mapping = build_stem_mapping(files)
        assert len(mapping) == 1
        assert len(mapping["foo"]) == 2

    def test_mixed_collision(self):
        files = [
            Path("/tmp/report.pdf"),
            Path("/tmp/Foo.pdf"),
            Path("/tmp/foo.pdf"),
            Path("/tmp/a?b.pdf"),
            Path("/tmp/a*b.pdf"),
        ]
        mapping = build_stem_mapping(files)
        assert len(mapping) == 3
        assert len(mapping["report"]) == 1
        assert len(mapping["foo"]) == 2
        assert len(mapping["a_b"]) == 2


class TestResolveOutputPath:
    def test_no_collision(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            source = Path("/tmp/report.pdf")
            mapping = build_stem_mapping([source])
            result = resolve_output_path(output_dir, source, mapping)
            assert result == output_dir / "report.md"

    def test_special_char_collision(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            sources = [Path("/tmp/a?b.pdf"), Path("/tmp/a*b.pdf")]
            mapping = build_stem_mapping(sources)
            result1 = resolve_output_path(output_dir, sources[0], mapping)
            result2 = resolve_output_path(output_dir, sources[1], mapping)
            assert result1 != result2
            assert result1.name.startswith("a_b_")
            assert result2.name.startswith("a_b_")
            assert result1.name.endswith(".md")
            assert result2.name.endswith(".md")

    def test_case_insensitive_collision(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            sources = [Path("/tmp/Foo.pdf"), Path("/tmp/foo.pdf")]
            mapping = build_stem_mapping(sources)
            result1 = resolve_output_path(output_dir, sources[0], mapping)
            result2 = resolve_output_path(output_dir, sources[1], mapping)
            assert result1 != result2
            assert result1.name.startswith("Foo_")
            assert result2.name.startswith("foo_")

    def test_stable_hash(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            sources = [Path("/tmp/Foo.pdf"), Path("/tmp/foo.pdf")]
            mapping = build_stem_mapping(sources)
            result1a = resolve_output_path(output_dir, sources[0], mapping)
            result1b = resolve_output_path(output_dir, sources[0], mapping)
            assert result1a == result1b


class TestEscapeMarkdownCell:
    def test_normal_text(self):
        assert escape_markdown_cell("hello") == "hello"

    def test_pipe_char(self):
        assert escape_markdown_cell("a|b") == "a\\|b"

    def test_newlines(self):
        assert escape_markdown_cell("line1\nline2") == "line1 line2"

    def test_crlf(self):
        assert escape_markdown_cell("line1\r\nline2") == "line1 line2"

    def test_cr(self):
        assert escape_markdown_cell("line1\rline2") == "line1 line2"

    def test_leading_trailing_spaces(self):
        assert escape_markdown_cell("  hello  ") == "hello"


class TestFormatTableAsMarkdown:
    def test_empty_table(self):
        assert format_table_as_markdown([]) == ""

    def test_single_row(self):
        table = [["a", "b", "c"]]
        result = format_table_as_markdown(table)
        assert "| a | b | c |" in result
        assert "| --- | --- | --- |" in result

    def test_multiple_rows(self):
        table = [["a", "b"], ["c", "d"]]
        result = format_table_as_markdown(table)
        lines = result.split("\n")
        assert len(lines) == 3
        assert lines[0] == "| a | b |"
        assert lines[1] == "| --- | --- |"
        assert lines[2] == "| c | d |"

    def test_inconsistent_columns(self):
        table = [["a", "b", "c"], ["d", "e"]]
        result = format_table_as_markdown(table)
        lines = result.split("\n")
        assert lines[0] == "| a | b | c |"
        assert lines[2] == "| d | e |  |"

    def test_pipe_in_cell(self):
        table = [["a|b", "c"]]
        result = format_table_as_markdown(table)
        assert "a\\|b" in result
