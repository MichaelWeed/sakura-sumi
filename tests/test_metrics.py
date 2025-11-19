"""Tests for metrics calculation."""

import pytest
from src.utils.metrics import CompressionMetrics, create_visualizations
from pathlib import Path
import tempfile


def test_metrics_calculation():
    """Test basic metrics calculation."""
    metrics_calc = CompressionMetrics()
    
    original_files = [
        {'size': 1000, 'path': 'file1.ts'},
        {'size': 2000, 'path': 'file2.ts'},
    ]
    
    pdf_files = [
        {'size': 1200, 'path': 'file1.pdf'},
        {'size': 2400, 'path': 'file2.pdf'},
    ]
    
    metrics = metrics_calc.calculate_metrics(
        original_files=original_files,
        pdf_files=pdf_files,
    )
    
    assert 'original' in metrics
    assert 'pdf' in metrics
    assert 'gemini_compatibility' in metrics
    assert metrics['original']['total_files'] == 2
    assert metrics['pdf']['total_files'] == 2
    assert metrics['pdf']['compression_ratio'] > 0


def test_metrics_gemini_compatibility():
    """Test Gemini compatibility checking."""
    metrics_calc = CompressionMetrics()
    
    # Small codebase (should fit)
    original_files = [{'size': 10000, 'path': 'small.ts'}]
    pdf_files = [{'size': 12000, 'path': 'small.pdf'}]
    
    metrics = metrics_calc.calculate_metrics(
        original_files=original_files,
        pdf_files=pdf_files,
    )
    
    assert 'fits_pdf' in metrics['gemini_compatibility']
    assert metrics['gemini_compatibility']['context_limit'] == 2_000_000


def test_metrics_report_generation():
    """Test report generation."""
    metrics_calc = CompressionMetrics()
    
    original_files = [{'size': 1000, 'path': 'test.ts'}]
    pdf_files = [{'size': 1200, 'path': 'test.pdf'}]
    
    metrics = metrics_calc.calculate_metrics(
        original_files=original_files,
        pdf_files=pdf_files,
    )
    
    # Test JSON report
    json_report = metrics_calc.generate_report(metrics, format='json')
    assert 'original' in json_report
    
    # Test Markdown report
    md_report = metrics_calc.generate_report(metrics, format='markdown')
    assert '# Compression Metrics Report' in md_report
    
    # Test HTML report
    html_report = metrics_calc.generate_report(metrics, format='html')
    assert '<html>' in html_report


def test_metrics_report_file_output():
    """Test report file output."""
    metrics_calc = CompressionMetrics()
    
    original_files = [{'size': 1000, 'path': 'test.ts'}]
    pdf_files = [{'size': 1200, 'path': 'test.pdf'}]
    
    metrics = metrics_calc.calculate_metrics(
        original_files=original_files,
        pdf_files=pdf_files,
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        report_path = Path(tmpdir) / 'test_report.md'
        metrics_calc.generate_report(
            metrics,
            output_path=report_path,
            format='markdown'
        )
        
        assert report_path.exists()
        content = report_path.read_text()
        assert 'Compression Metrics Report' in content


def test_visualizations():
    """Test visualization generation."""
    metrics_calc = CompressionMetrics()
    
    original_files = [{'size': 1000, 'path': 'test.ts'}]
    pdf_files = [{'size': 1200, 'path': 'test.pdf'}]
    
    metrics = metrics_calc.calculate_metrics(
        original_files=original_files,
        pdf_files=pdf_files,
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        charts = create_visualizations(metrics, Path(tmpdir))
        # Charts may or may not be created depending on matplotlib availability
        assert isinstance(charts, list)

