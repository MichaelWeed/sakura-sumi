"""Tests for hybrid preprocessor utilities."""

from src.compression.hybrid_preprocessor import (
    preprocess_code,
    generate_translation_dict_yaml,
    prepend_dict,
    SYMBOL_MAP,
)


def test_preprocess_code_hybrid_mode():
    """Hybrid mode should replace symbols and pad operators."""
    content = "value─1 +2 –3"
    processed, translations = preprocess_code(content, mode="hybrid")

    # Box drawing and dash replacements applied
    assert "- - -" in processed  # Replacement for '─' with spacing
    assert "- -" in processed  # Replacement for '–'
    # Translation dictionary should include replaced characters
    assert "─" in translations
    assert translations["─"] == SYMBOL_MAP["─"]


def test_preprocess_code_code_mode_no_padding():
    """Code mode should replace symbols without padding operators."""
    content = "a—b"
    processed, translations = preprocess_code(content, mode="code")

    assert "'" not in processed  # ensure replacements occurred
    # No padding added around operators in code mode
    assert " - " not in processed
    assert "—" in translations


def test_preprocess_invalid_mode_returns_original():
    """Unsupported mode should return original content."""
    content = "plain text"
    processed, translations = preprocess_code(content, mode="off")

    assert processed == content
    assert translations == {}


def test_generate_translation_dict_yaml():
    """Translation dictionary should be rendered as YAML."""
    yaml_content = generate_translation_dict_yaml({"─": "---", "—": "---"})

    assert "translations:" in yaml_content
    assert "U+2500" in yaml_content
    assert "Hybrid Mode Translation Dictionary" in yaml_content


def test_prepend_dict_adds_frontmatter():
    """Prepend dict should add YAML frontmatter."""
    translation_dict = {"─": "---"}
    content = "body"

    combined = prepend_dict(content, translation_dict)
    assert combined.startswith("---")
    assert combined.endswith("body")


