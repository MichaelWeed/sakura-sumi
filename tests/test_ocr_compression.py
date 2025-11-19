"""Tests for OCR compression (optional feature)."""

import pytest
from src.compression.ocr_compression import OCRCompressor, create_ocr_compressor
from pathlib import Path
import tempfile


def test_ocr_compressor_initialization():
    """Test OCR compressor initialization."""
    compressor = OCRCompressor(mode='small')
    
    assert compressor.mode == 'small'
    assert compressor.config['target_ratio'] == 7
    assert compressor.config['accuracy'] == 0.97


def test_ocr_compressor_modes():
    """Test available compression modes."""
    modes = OCRCompressor.get_available_modes()
    
    assert 'small' in modes
    assert 'medium' in modes
    assert 'large' in modes
    assert 'maximum' in modes
    
    assert modes['small']['target_ratio'] == 7
    assert modes['small']['accuracy'] == 0.97


def test_ocr_compressor_dependency_check():
    """Test dependency checking."""
    deps = OCRCompressor.check_dependencies()
    
    assert 'vllm' in deps
    assert 'transformers' in deps
    assert 'deepseek_ocr_model' in deps
    assert isinstance(deps['vllm'], bool)


def test_ocr_compressor_availability():
    """Test availability checking."""
    compressor = OCRCompressor(mode='small')
    # Should return False since dependencies not installed
    assert compressor.is_available() == False


def test_create_ocr_compressor():
    """Test factory function."""
    compressor = create_ocr_compressor(mode='small')
    # Should return None if dependencies not available
    assert compressor is None or isinstance(compressor, OCRCompressor)


def test_ocr_compressor_invalid_mode():
    """Test invalid mode handling."""
    with pytest.raises(ValueError):
        OCRCompressor(mode='invalid_mode')


def test_ocr_compressor_all_modes():
    """Test all compression modes."""
    for mode in ['small', 'medium', 'large', 'maximum']:
        compressor = OCRCompressor(mode=mode)
        assert compressor.mode == mode
        assert 'target_ratio' in compressor.config
        assert 'accuracy' in compressor.config


def test_ocr_compressor_mode_configs():
    """Test mode-specific configurations."""
    small = OCRCompressor(mode='small')
    medium = OCRCompressor(mode='medium')
    large = OCRCompressor(mode='large')
    maximum = OCRCompressor(mode='maximum')
    
    # Verify compression ratios increase
    assert small.config['target_ratio'] < medium.config['target_ratio']
    assert medium.config['target_ratio'] < large.config['target_ratio']
    assert large.config['target_ratio'] < maximum.config['target_ratio']
    
    # Verify accuracy decreases (trade-off)
    assert small.config['accuracy'] >= medium.config['accuracy']
    assert medium.config['accuracy'] >= large.config['accuracy']


def test_ocr_compressor_dependency_status():
    """Test dependency status reporting."""
    deps = OCRCompressor.check_dependencies()
    
    # Should return dict with boolean values
    assert isinstance(deps, dict)
    for key, value in deps.items():
        assert isinstance(value, bool)


def test_ocr_compressor_unavailable_operations():
    """Test operations when dependencies unavailable."""
    compressor = OCRCompressor(mode='small')
    
    # Since dependencies aren't available, these should return None or raise
    assert compressor.is_available() == False


def test_create_ocr_compressor_all_modes():
    """Test factory function with all modes."""
    for mode in ['small', 'medium', 'large', 'maximum']:
        compressor = create_ocr_compressor(mode=mode)
        # Should return None if deps unavailable, or OCRCompressor if available
        assert compressor is None or isinstance(compressor, OCRCompressor)


def test_ocr_compressor_mode_validation():
    """Test mode validation."""
    # Valid modes should work
    for mode in ['small', 'medium', 'large', 'maximum']:
        compressor = OCRCompressor(mode=mode)
        assert compressor.mode == mode
    
    # Invalid mode should raise
    with pytest.raises(ValueError, match='Invalid mode'):
        OCRCompressor(mode='invalid')
    
    with pytest.raises(ValueError):
        OCRCompressor(mode='')
    
    with pytest.raises(ValueError):
        OCRCompressor(mode=None)


def test_ocr_compressor_compress_pdf_with_cache(monkeypatch, tmp_path):
    """Test compress_pdf when OCR is available and caching enabled."""
    from src.compression import ocr_compression as oc

    monkeypatch.setattr(oc, 'OCR_AVAILABLE', True)
    compressor = oc.OCRCompressor(mode='small', cache_dir=str(tmp_path))
    # Prevent actual model loading logic
    monkeypatch.setattr(compressor, '_load_model', lambda: setattr(compressor, 'model_loaded', True))

    pdf_path = tmp_path / 'sample.pdf'
    pdf_path.write_text('fake pdf content')

    # First compression should create cached file
    cached_path = compressor.compress_pdf(pdf_path)
    assert cached_path is not None
    assert cached_path.exists()

    # Second compression should hit cache
    cached_again = compressor.compress_pdf(pdf_path)
    assert cached_again == cached_path
    stats = compressor.get_stats()
    assert stats['files_compressed'] == 1
    assert stats['files_cached'] == 1


def test_ocr_compressor_batch_processing(monkeypatch, tmp_path):
    """Test batch compression with progress callback."""
    from src.compression import ocr_compression as oc

    monkeypatch.setattr(oc, 'OCR_AVAILABLE', True)
    compressor = oc.OCRCompressor(mode='small', cache_dir=str(tmp_path))
    monkeypatch.setattr(compressor, '_load_model', lambda: setattr(compressor, 'model_loaded', True))

    pdf_paths = []
    for i in range(2):
        pdf = tmp_path / f'sample_{i}.pdf'
        pdf.write_text('content')
        pdf_paths.append(pdf)

    progress_calls = []
    results = compressor.compress_pdfs_batch(pdf_paths, progress_callback=lambda path, success: progress_calls.append((path, success)))

    assert len(results) == len(pdf_paths)
    assert len(progress_calls) == len(pdf_paths)
    assert all(success for _, success in progress_calls)

