"""Tests for DeepSeek-OCR insights service."""

import pytest
import json
import tempfile
from pathlib import Path
from src.utils.deepseek_insights import DeepSeekInsightsService


@pytest.fixture
def insights_service():
    """Create DeepSeek insights service with default config."""
    return DeepSeekInsightsService()


@pytest.fixture
def temp_config_file():
    """Create temporary config file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config = {
            'deepseek_ocr': {
                'compression_ratio': 12,
                'accuracy': 0.95,
                'throughput_pages_per_day': 150000,
                'avg_processing_time_per_page_seconds': 0.01,
                'text_to_vision_token_ratio': 0.08,
                'model_version': 'DeepSeek-OCR v3.0'
            }
        }
        json.dump(config, f)
        config_path = Path(f.name)
    
    yield config_path
    
    # Cleanup
    if config_path.exists():
        config_path.unlink()


def test_deepseek_insights_initialization(insights_service):
    """Test service initialization with default config."""
    assert insights_service.config is not None
    assert 'compression_ratio' in insights_service.config
    assert insights_service.config['compression_ratio'] == 10
    assert insights_service.config['accuracy'] == 0.97


def test_deepseek_insights_custom_config(temp_config_file):
    """Test service initialization with custom config file."""
    service = DeepSeekInsightsService(config_path=temp_config_file)
    
    assert service.config['compression_ratio'] == 12
    assert service.config['accuracy'] == 0.95
    assert service.config['model_version'] == 'DeepSeek-OCR v3.0'


def test_deepseek_insights_calculate_insights(insights_service):
    """Test calculate_insights method."""
    file_count = 50
    pre_tokens = 100000
    
    insights = insights_service.calculate_insights(file_count, pre_tokens)
    
    assert 'compression_ratio' in insights
    assert 'accuracy' in insights
    assert 'estimated_pages' in insights
    assert 'processing_time_seconds' in insights
    assert 'processing_time_formatted' in insights
    assert 'throughput_capacity_percent' in insights
    assert 'vision_tokens_estimate' in insights
    assert 'pre_tokens' in insights
    assert 'model_version' in insights
    
    # Verify calculations
    assert insights['estimated_pages'] == file_count * 2  # 100 pages
    assert insights['pre_tokens'] == pre_tokens
    assert insights['compression_ratio'] == 10
    assert insights['accuracy'] == 0.97
    assert insights['accuracy_percent'] == 97


def test_deepseek_insights_vision_tokens_rounding(insights_service):
    """Test vision tokens rounding logic."""
    # Test with 101700 tokens (should round to 11k)
    insights = insights_service.calculate_insights(10, 101700)
    assert insights['vision_tokens_estimate'] == 11000
    assert insights['vision_tokens_estimate'] % 1000 == 0
    
    # Test with 125000 tokens (should round to 13k)
    insights = insights_service.calculate_insights(10, 125000)
    assert insights['vision_tokens_estimate'] == 13000
    
    # Test with small tokens (should be at least 1)
    insights = insights_service.calculate_insights(1, 500)
    assert insights['vision_tokens_estimate'] >= 1
    assert insights['vision_tokens_estimate'] <= 500  # Should not exceed pre_tokens


def test_deepseek_insights_processing_time(insights_service):
    """Test processing time calculations."""
    # Small job
    insights = insights_service.calculate_insights(10, 50000)
    assert insights['processing_time_seconds'] > 0
    assert 'seconds' in insights['processing_time_formatted'] or 'minutes' in insights['processing_time_formatted']
    
    # Large job
    insights = insights_service.calculate_insights(1000, 1000000)
    assert insights['processing_time_seconds'] > 0
    # Should be formatted appropriately (minutes or hours)


def test_deepseek_insights_throughput_capacity(insights_service):
    """Test throughput capacity calculation."""
    # Small job
    insights = insights_service.calculate_insights(10, 50000)
    assert insights['throughput_capacity_percent'] >= 0
    assert insights['throughput_capacity_percent'] < 1  # Should be very small
    
    # Large job
    insights = insights_service.calculate_insights(100000, 10000000)
    assert insights['throughput_capacity_percent'] > 0
    # Should be a reasonable percentage


def test_deepseek_insights_format_duration_seconds(insights_service):
    """Test duration formatting for seconds."""
    result = insights_service._format_duration(30.5)
    assert 'seconds' in result
    assert '30.5' in result or '30' in result


def test_deepseek_insights_format_duration_minutes(insights_service):
    """Test duration formatting for minutes."""
    result = insights_service._format_duration(120.5)
    assert 'minutes' in result
    assert '2.0' in result or '2' in result


def test_deepseek_insights_format_duration_hours(insights_service):
    """Test duration formatting for hours."""
    result = insights_service._format_duration(7200.0)
    assert 'hours' in result
    assert '2.0' in result or '2' in result


def test_deepseek_insights_get_summary(insights_service):
    """Test get_summary method."""
    insights = insights_service.calculate_insights(50, 100000)
    summary = insights_service.get_summary(insights)
    
    assert 'compression_ratio' in summary
    assert 'accuracy' in summary
    assert 'estimated_time' in summary
    
    assert 'x' in summary['compression_ratio']
    assert '%' in summary['accuracy']
    assert isinstance(summary['estimated_time'], str)


def test_deepseek_insights_get_technical_details(insights_service):
    """Test get_technical_details method."""
    insights = insights_service.calculate_insights(50, 100000)
    details = insights_service.get_technical_details(insights)
    
    assert 'estimated_pages' in details
    assert 'text_tokens' in details
    assert 'vision_tokens' in details
    assert 'conversion_ratio' in details
    assert 'throughput_capacity' in details
    assert 'model_version' in details
    
    assert details['text_tokens'] == 100000
    assert details['vision_tokens'] == insights['vision_tokens_estimate']
    assert 'vision' in details['conversion_ratio']
    assert '%' in details['throughput_capacity']


def test_deepseek_insights_invalid_config_file():
    """Test service with non-existent config file (should use defaults)."""
    fake_path = Path('/nonexistent/path/config.json')
    service = DeepSeekInsightsService(config_path=fake_path)
    
    # Should fall back to defaults
    assert service.config['compression_ratio'] == 10
    assert service.config['accuracy'] == 0.97


def test_deepseek_insights_malformed_config_file():
    """Test service with malformed config file (should use defaults)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{ invalid json }')
        config_path = Path(f.name)
    
    try:
        service = DeepSeekInsightsService(config_path=config_path)
        # Should fall back to defaults
        assert service.config['compression_ratio'] == 10
    finally:
        if config_path.exists():
            config_path.unlink()


def test_deepseek_insights_config_without_nesting():
    """Test config file without nested 'deepseek_ocr' key."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config = {
            'compression_ratio': 15,
            'accuracy': 0.98
        }
        json.dump(config, f)
        config_path = Path(f.name)
    
    try:
        service = DeepSeekInsightsService(config_path=config_path)
        assert service.config['compression_ratio'] == 15
        assert service.config['accuracy'] == 0.98
    finally:
        if config_path.exists():
            config_path.unlink()


def test_deepseek_insights_zero_files(insights_service):
    """Test with zero files."""
    insights = insights_service.calculate_insights(0, 0)
    
    assert insights['estimated_pages'] == 0
    assert insights['processing_time_seconds'] == 0
    # When pre_tokens is 0, compressed is 0, so vision_tokens is 0 (not 1)
    assert insights['vision_tokens_estimate'] == 0


def test_deepseek_insights_custom_compression_ratio(temp_config_file):
    """Test with custom compression ratio."""
    service = DeepSeekInsightsService(config_path=temp_config_file)
    insights = service.calculate_insights(10, 100000)
    
    # Should use custom ratio of 12
    assert insights['compression_ratio'] == 12
    # Vision tokens should be calculated with custom ratio
    expected = (100000 / 12)  # ~8333, rounded up to 9k
    assert insights['vision_tokens_estimate'] >= 8000

