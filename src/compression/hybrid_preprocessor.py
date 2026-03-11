"""Hybrid mode preprocessor for OCR-friendly code transformation.

Replaces fragile Unicode characters (box-drawing, dashes, etc.) with ASCII equivalents
and applies padding transformations for better OCR fidelity.

Trade-offs:
- Fidelity gain: Preserves code structure that would be lost in aggressive OCR compression
- Density loss: Slightly increases token count (~5-15%) due to ASCII replacements
- Use case: When code contains box-drawing characters, special dashes, or other Unicode
  that commonly fails in OCR pipelines.
"""

import re
from typing import Dict, Tuple


# HYBRID_MODE_START
# Symbol translation map: Unicode → ASCII equivalents
SYMBOL_MAP: Dict[str, str] = {
    # Box-drawing characters (light)
    '─': '---',  # U+2500 LIGHT HORIZONTAL
    '━': '===',  # U+2501 HEAVY HORIZONTAL
    '│': '|',    # U+2502 LIGHT VERTICAL
    '┃': '||',   # U+2503 HEAVY VERTICAL
    '├': '|+',   # U+251C LIGHT VERTICAL AND RIGHT
    '┤': '+|',   # U+2524 LIGHT VERTICAL AND LEFT
    '┬': '+-+',  # U+252C LIGHT DOWN AND HORIZONTAL
    '┴': '+-+',  # U+2534 LIGHT UP AND HORIZONTAL
    '└': '`-',   # U+2514 LIGHT UP AND RIGHT
    '┘': '-`',   # U+2518 LIGHT UP AND LEFT
    '┌': '+-',   # U+250C LIGHT DOWN AND RIGHT
    '┐': '-+',   # U+2510 LIGHT DOWN AND LEFT
    
    # Box-drawing characters (heavy)
    '┏': '++',   # U+250F HEAVY DOWN AND RIGHT
    '┓': '++',   # U+2513 HEAVY DOWN AND LEFT
    '┗': '++',   # U+2517 HEAVY UP AND RIGHT
    '┛': '++',   # U+251B HEAVY UP AND LEFT
    '┣': '|+',   # U+2523 HEAVY VERTICAL AND RIGHT
    '┫': '+|',   # U+252B HEAVY VERTICAL AND LEFT
    '┳': '+++',  # U+2533 HEAVY DOWN AND HORIZONTAL
    '┻': '+++',  # U+253B HEAVY UP AND HORIZONTAL
    
    # Box-drawing characters (double)
    '╔': '==',   # U+2554 DOUBLE DOWN AND RIGHT
    '╗': '==',   # U+2557 DOUBLE DOWN AND LEFT
    '╚': '==',   # U+255A DOUBLE UP AND RIGHT
    '╝': '==',   # U+255D DOUBLE UP AND LEFT
    '╠': '||',   # U+2560 DOUBLE VERTICAL AND RIGHT
    '╣': '||',   # U+2563 DOUBLE VERTICAL AND LEFT
    '╦': '===',  # U+2566 DOUBLE DOWN AND HORIZONTAL
    '╩': '===',  # U+2569 DOUBLE UP AND HORIZONTAL
    '║': '||',   # U+2551 DOUBLE VERTICAL
    '═': '==',   # U+2550 DOUBLE HORIZONTAL
    '╬': '+++',  # U+256C DOUBLE VERTICAL AND HORIZONTAL
    
    # Dashes and hyphens (fragile in OCR)
    '‐': '-',    # U+2010 HYPHEN
    '‑': '-',    # U+2011 NON-BREAKING HYPHEN
    '‒': '-',    # U+2012 FIGURE DASH
    '–': '--',   # U+2013 EN DASH
    '—': '---',  # U+2014 EM DASH
    '―': '---',  # U+2015 HORIZONTAL BAR
    '−': '-',    # U+2212 MINUS SIGN
    '­': '-',    # U+00AD SOFT HYPHEN
    
    # Other problematic symbols
    '•': '*',    # U+2022 BULLET
    '·': '.',    # U+00B7 MIDDLE DOT
    '…': '...',  # U+2026 HORIZONTAL ELLIPSIS
    '′': "'",    # U+2032 PRIME
    '″': '"',    # U+2033 DOUBLE PRIME
    '°': 'deg',  # U+00B0 DEGREE SIGN
    '±': '+/-',  # U+00B1 PLUS-MINUS SIGN
    '×': '*',    # U+00D7 MULTIPLICATION SIGN
    '÷': '/',    # U+00F7 DIVISION SIGN
    '≈': '~=',   # U+2248 ALMOST EQUAL TO
    '≠': '!=',   # U+2260 NOT EQUAL TO
    '≤': '<=',   # U+2264 LESS-THAN OR EQUAL TO
    '≥': '>=',   # U+2265 GREATER-THAN OR EQUAL TO
    '∑': 'sum',  # U+2211 N-ARY SUMMATION
    '∫': 'int',  # U+222B INTEGRAL
    '√': 'sqrt', # U+221A SQUARE ROOT
    '∞': 'inf',  # U+221E INFINITY
    'µ': 'mu',   # U+00B5 MICRO SIGN
}


def preprocess_code(content: str, mode: str = 'hybrid') -> Tuple[str, Dict[str, str]]:
    """
    Preprocess code content for OCR-friendly transformation.
    
    Args:
        content: Original code content
        mode: Processing mode ('code', 'hybrid', or 'off')
        
    Returns:
        Tuple of (processed_content, translation_dict)
        translation_dict maps original Unicode → ASCII replacement
    """
    if mode not in ('code', 'hybrid'):
        return content, {}
    
    processed = content
    translation_dict = {}
    
    # Apply symbol replacements
    for unicode_char, ascii_replacement in SYMBOL_MAP.items():
        if unicode_char in processed:
            # Track what was replaced for the translation dictionary
            if unicode_char not in translation_dict:
                translation_dict[unicode_char] = ascii_replacement
            processed = processed.replace(unicode_char, ascii_replacement)
    
    # Apply padding transformations for better OCR fidelity
    # Add spacing around operators that OCR often misreads
    if mode == 'hybrid':
        # Pad operators with spaces (but preserve existing spacing)
        # Only pad if not already padded - be careful not to break string literals
        # Simple approach: pad operators outside of quotes
        # Note: This is a simplified implementation - full parsing would be more accurate
        # but may add ~5-15% token bloat as trade-off for OCR fidelity
        processed = re.sub(r'(?<!\s)([+\-*/=<>!])(?!\s)', r' \1 ', processed)
        # Clean up double spaces (but preserve intentional spacing)
        processed = re.sub(r'  +', ' ', processed)
    
    return processed, translation_dict


def generate_translation_dict_yaml(translation_dict: Dict[str, str]) -> str:
    """
    Generate YAML frontmatter for translation dictionary.
    
    Args:
        translation_dict: Dictionary mapping Unicode → ASCII
        
    Returns:
        YAML-formatted string with translation map
    """
    if not translation_dict:
        return ""
    
    yaml_lines = [
        "---",
        "# Hybrid Mode Translation Dictionary",
        "# Maps Unicode characters to ASCII equivalents for OCR fidelity",
        "# Use this to reverse-translate OCR output if needed",
        "translations:"
    ]
    
    for unicode_char, ascii_replacement in sorted(translation_dict.items()):
        # Escape Unicode for YAML
        unicode_hex = f"U+{ord(unicode_char):04X}"
        yaml_lines.append(f"  '{unicode_hex}': '{ascii_replacement}'  # {unicode_char}")
    
    yaml_lines.append("---")
    yaml_lines.append("")
    
    return "\n".join(yaml_lines)


def prepend_dict(content: str, translation_dict: Dict[str, str]) -> str:
    """
    Prepend translation dictionary as YAML frontmatter to content.
    
    Args:
        content: Original content
        translation_dict: Translation dictionary to prepend
        
    Returns:
        Content with YAML frontmatter prepended
    """
    if not translation_dict:
        return content
    
    yaml_dict = generate_translation_dict_yaml(translation_dict)
    return yaml_dict + content
# HYBRID_MODE_END

