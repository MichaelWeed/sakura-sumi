"""Tests for compression pipeline."""

import json
import pytest
import tempfile
from pathlib import Path
from src.compression.pipeline import CompressionPipeline


@pytest.fixture
def temp_codebase():
    """Create temporary codebase."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        (base / 'src').mkdir(parents=True, exist_ok=True)
        (base / 'src' / 'main.ts').write_text('console.log("test");')
        (base / 'package.json').write_text('{"name": "test"}')
        yield base


@pytest.fixture
def temp_output():
    """Create temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_pipeline_basic(temp_codebase, temp_output, capsys):
    """Test basic pipeline execution."""
    pipeline = CompressionPipeline(
        source_dir=str(temp_codebase),
        output_dir=str(temp_output),
    )
    
    results = pipeline.run(verbose=True)
    
    assert results['success'] is True
    assert results['summary']['files_discovered'] > 0
    assert results['summary']['files_converted'] > 0
    
    captured = capsys.readouterr().out
    assert "Compression Pipeline Summary" in captured
    assert results['failure_report'] is None


def test_pipeline_parallel(temp_codebase, temp_output):
    """Test parallel processing."""
    pipeline = CompressionPipeline(
        source_dir=str(temp_codebase),
        output_dir=str(temp_output),
        parallel=True,
        max_workers=2,
    )
    
    results = pipeline.run(verbose=False)
    assert results['success'] is True


def test_pipeline_resume(temp_codebase, temp_output):
    """Test resume functionality."""
    # First run
    pipeline1 = CompressionPipeline(
        source_dir=str(temp_codebase),
        output_dir=str(temp_output),
    )
    results1 = pipeline1.run(verbose=False)
    
    # Second run with resume
    pipeline2 = CompressionPipeline(
        source_dir=str(temp_codebase),
        output_dir=str(temp_output),
        resume=True,
    )
    results2 = pipeline2.run(verbose=False)
    
    assert results2['success'] is True
    # Should skip already processed files
    assert results2['summary']['files_already_processed'] > 0


def test_pipeline_no_files(temp_output):
    """Pipeline should handle directories with no files."""
    with tempfile.TemporaryDirectory() as empty_dir:
        pipeline = CompressionPipeline(
            source_dir=empty_dir,
            output_dir=str(temp_output),
        )
        results = pipeline.run(verbose=False)
        assert results['success'] is False
        assert results['error'] == 'No files discovered'


def test_pipeline_checkpoint_recovery(temp_codebase, temp_output):
    """Invalid checkpoint files should be handled gracefully."""
    pipeline = CompressionPipeline(
        source_dir=str(temp_codebase),
        output_dir=str(temp_output),
        resume=True,
    )
    # Write malformed checkpoint data
    checkpoint_path = pipeline.checkpoint_file
    checkpoint_path.write_text('{ invalid json')

    results = pipeline.run(verbose=False)
    assert results['success'] is True


def test_pipeline_smart_concatenation(temp_codebase, temp_output, capsys):
    """Smart concatenation pipeline should complete successfully."""
    pipeline = CompressionPipeline(
        source_dir=str(temp_codebase),
        output_dir=str(temp_output),
    )
    results = pipeline.run_smart_concatenation(max_pdfs=2, verbose=True)
    assert results['success'] is True
    assert results['smart_concatenation']['total_pdfs_created'] > 0
    out = capsys.readouterr().out
    assert "Smart concatenation complete" in out or "Smart concatenation pipeline" in out
    assert results['failure_report'] is None


def test_pipeline_print_helpers(temp_codebase, temp_output, capsys):
    """Printing helpers should render summaries without errors."""
    pipeline = CompressionPipeline(
        source_dir=str(temp_codebase),
        output_dir=str(temp_output),
    )
    
    sample_results = {
        'duration_seconds': 1.5,
        'summary': {
            'files_discovered': 2,
            'files_converted': 2,
            'files_failed': 0,
            'files_already_processed': 0,
            'total_size_original_bytes': 1000,
            'total_size_pdf_bytes': 500,
            'compression_ratio': 2.0,
        },
        'failed_files': [{'file': 'bad.ts', 'error': 'boom'}],
    }
    pipeline._print_summary(sample_results)
    
    sample_metrics = {
        'original': {
            'estimated_tokens': 1000,
            'total_size_bytes': 1000,
        },
        'pdf': {
            'estimated_tokens': 500,
            'total_size_bytes': 500,
            'token_compression_ratio': 2.0,
            'token_savings': 500,
            'token_savings_percent': 50.0,
        },
        'gemini_compatibility': {
            'context_limit': 2_000_000,
            'fits_pdf': True,
            'pdf_usage_percent': 0.1,
            'fits_ocr': True,
            'ocr_usage_percent': 0.05,
        },
        'summary': {
            'recommended_action': 'Proceed',
        },
        'ocr': {
            'estimated_tokens': 400,
            'total_size_bytes': 400,
        }
    }
    pipeline._print_metrics_summary(sample_metrics)
    
    captured = capsys.readouterr().out
    assert "Compression Metrics" in captured


def test_pipeline_failure_report(temp_codebase, temp_output, monkeypatch):
    """Failures should generate a report file."""
    pipeline = CompressionPipeline(
        source_dir=str(temp_codebase),
        output_dir=str(temp_output),
    )
    
    original_convert = pipeline.converter.convert_file
    
    def fail_first(file_info):
        if file_info.relative_path.endswith('main.ts'):
            raise RuntimeError('boom')
        return original_convert(file_info)
    
    monkeypatch.setattr(pipeline.converter, 'convert_file', fail_first)
    
    results = pipeline.run(verbose=False)
    assert results['failed_files']
    report_path = Path(results['failure_report'])
    assert report_path.exists()
    data = json.loads(report_path.read_text())
    assert len(data['failures']) == len(results['failed_files'])

