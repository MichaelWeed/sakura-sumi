"""Tests for PDF converter."""

import pytest
import tempfile
from pathlib import Path
from src.compression.pdf_converter import PDFConverter
from src.utils.file_discovery import FileInfo


@pytest.fixture
def temp_output():
    """Create temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_file_info(temp_output):
    """Create sample file info."""
    test_file = temp_output / 'test.ts'
    test_file.write_text('export const test = "hello";')
    
    return FileInfo(
        path=str(test_file),
        relative_path='test.ts',
        size=test_file.stat().st_size,
        file_type='ts',
        category='source',
    )


def test_pdf_converter_basic(temp_output, sample_file_info):
    """Test basic PDF conversion."""
    converter = PDFConverter(str(temp_output))
    pdf_path = converter.convert_file(sample_file_info)
    
    assert pdf_path is not None
    assert pdf_path.exists()
    assert pdf_path.suffix == '.pdf'


def test_pdf_converter_json_formatting(temp_output):
    """Test JSON file formatting."""
    test_file = temp_output / 'test.json'
    test_file.write_text('{"key":"value"}')
    
    file_info = FileInfo(
        path=str(test_file),
        relative_path='test.json',
        size=test_file.stat().st_size,
        file_type='json',
        category='config',
    )
    
    converter = PDFConverter(str(temp_output))
    pdf_path = converter.convert_file(file_info)
    
    assert pdf_path is not None
    assert pdf_path.exists()


def test_pdf_converter_stats(temp_output, sample_file_info):
    """Test conversion statistics."""
    converter = PDFConverter(str(temp_output))
    converter.convert_file(sample_file_info)
    
    stats = converter.get_stats()
    assert stats['success'] > 0
    assert 'compression_ratio' in stats


def test_pdf_converter_yaml_formatting(temp_output):
    """Test YAML file formatting."""
    test_file = temp_output / 'test.yaml'
    test_file.write_text('key: value\nnested:\n  item: test')
    
    file_info = FileInfo(
        path=str(test_file),
        relative_path='test.yaml',
        size=test_file.stat().st_size,
        file_type='yaml',
        category='config',
    )
    
    converter = PDFConverter(str(temp_output))
    pdf_path = converter.convert_file(file_info)
    
    assert pdf_path is not None
    assert pdf_path.exists()


def test_pdf_converter_encoding_handling(temp_output):
    """Test encoding error handling."""
    test_file = temp_output / 'test.txt'
    # Create file with problematic encoding
    test_file.write_bytes(b'\xff\xfe\x00\x00')  # Invalid UTF-8
    
    file_info = FileInfo(
        path=str(test_file),
        relative_path='test.txt',
        size=test_file.stat().st_size,
        file_type='txt',
        category='documentation',
        encoding='utf-8'
    )
    
    converter = PDFConverter(str(temp_output))
    pdf_path = converter.convert_file(file_info)
    
    # Should handle gracefully (may return None or use fallback encoding)
    assert pdf_path is None or pdf_path.exists()


def test_pdf_converter_nonexistent_file(temp_output):
    """Test handling of nonexistent file."""
    file_info = FileInfo(
        path='/nonexistent/file.ts',
        relative_path='file.ts',
        size=1000,
        file_type='ts',
        category='source',
    )
    
    converter = PDFConverter(str(temp_output))
    pdf_path = converter.convert_file(file_info)
    
    # Should return None when file doesn't exist
    assert pdf_path is None
    # May or may not increment failed count depending on error handling
    # Just verify it handled gracefully
    assert 'errors' in converter.conversion_stats


def test_pdf_converter_large_content(temp_output):
    """Test PDF generation with large content."""
    test_file = temp_output / 'large.ts'
    # Create large file
    large_content = 'const x = "test";\n' * 1000
    test_file.write_text(large_content)
    
    file_info = FileInfo(
        path=str(test_file),
        relative_path='large.ts',
        size=test_file.stat().st_size,
        file_type='ts',
        category='source',
    )
    
    converter = PDFConverter(str(temp_output))
    pdf_path = converter.convert_file(file_info)
    
    assert pdf_path is not None
    assert pdf_path.exists()


def test_pdf_converter_special_characters(temp_output):
    """Test PDF generation with special characters."""
    test_file = temp_output / 'special.ts'
    # Content with XML/HTML special characters
    content = '<Component prop="value">&amp;test</Component>'
    test_file.write_text(content)
    
    file_info = FileInfo(
        path=str(test_file),
        relative_path='special.ts',
        size=test_file.stat().st_size,
        file_type='ts',
        category='source',
    )
    
    converter = PDFConverter(str(temp_output))
    pdf_path = converter.convert_file(file_info)
    
    assert pdf_path is not None
    assert pdf_path.exists()


def test_pdf_converter_concatenate_files(temp_output):
    """Test concatenating multiple files."""
    # Create multiple test files
    files = []
    for i in range(3):
        test_file = temp_output / f'file{i}.ts'
        test_file.write_text(f'export const test{i} = "value{i}";')
        files.append(FileInfo(
            path=str(test_file),
            relative_path=f'file{i}.ts',
            size=test_file.stat().st_size,
            file_type='ts',
            category='source',
        ))
    
    converter = PDFConverter(str(temp_output))
    pdf_path = converter.concatenate_files_to_pdf(
        files=files,
        pdf_name='combined',
        max_pages=100,
        max_size_bytes=10 * 1024 * 1024
    )
    
    assert pdf_path is not None
    assert pdf_path.exists()
    assert 'combined' in pdf_path.name


def test_pdf_converter_concatenate_empty_list(temp_output):
    """Test concatenating empty file list."""
    converter = PDFConverter(str(temp_output))
    pdf_path = converter.concatenate_files_to_pdf(
        files=[],
        pdf_name='empty',
        max_pages=100,
        max_size_bytes=10 * 1024 * 1024
    )
    
    # Should handle gracefully
    assert pdf_path is None or pdf_path.exists()


def test_pdf_converter_hybrid_mode(temp_output, sample_file_info):
    """Test PDF converter with hybrid mode enabled."""
    converter = PDFConverter(str(temp_output), hybrid_mode=True)
    pdf_path = converter.convert_file(sample_file_info)
    
    assert pdf_path is not None
    assert pdf_path.exists()


def test_pdf_converter_malformed_json(temp_output):
    """Test handling of malformed JSON."""
    test_file = temp_output / 'bad.json'
    test_file.write_text('{ invalid json }')
    
    file_info = FileInfo(
        path=str(test_file),
        relative_path='bad.json',
        size=test_file.stat().st_size,
        file_type='json',
        category='config',
    )
    
    converter = PDFConverter(str(temp_output))
    pdf_path = converter.convert_file(file_info)
    
    # Should handle gracefully (may return original content)
    assert pdf_path is None or pdf_path.exists()


def test_pdf_converter_fallback_generation(temp_output, sample_file_info, monkeypatch):
    """Force fallback PDF generation path."""
    from src.compression import pdf_converter as module
    
    class FailingDoc:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("failure")
    
    monkeypatch.setattr(module, 'SimpleDocTemplate', FailingDoc)
    
    converter = PDFConverter(str(temp_output))
    pdf_path = converter.convert_file(sample_file_info)
    
    assert pdf_path is not None
    assert pdf_path.exists()

