"""Tests for token estimation service."""

import math
import pytest
from src.utils.token_estimation import (
    TokenEstimationService,
    get_compression_recommendation,
    WARNING_THRESHOLD,
    ERROR_THRESHOLD
)
from src.utils.file_discovery import FileInfo
from pathlib import Path
import tempfile


@pytest.fixture
def token_service():
    """Create token estimation service."""
    return TokenEstimationService()


@pytest.fixture
def sample_files():
    """Create sample files for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        (base / 'src').mkdir(parents=True, exist_ok=True)
        
        # Create files with known content
        (base / 'src' / 'file1.ts').write_text('console.log("test");\n' * 100)
        (base / 'src' / 'file2.ts').write_text('export function test() { return true; }\n' * 50)
        (base / 'package.json').write_text('{"name": "test", "version": "1.0.0"}')
        
        files = [
            FileInfo(
                path=str(base / 'src' / 'file1.ts'),
                relative_path='src/file1.ts',
                size=1000,
                file_type='ts',
                category='source'
            ),
            FileInfo(
                path=str(base / 'src' / 'file2.ts'),
                relative_path='src/file2.ts',
                size=500,
                file_type='ts',
                category='source'
            ),
            FileInfo(
                path=str(base / 'package.json'),
                relative_path='package.json',
                size=50,
                file_type='json',
                category='config'
            )
        ]
        
        yield files


def test_token_estimation_pre_compression(token_service, sample_files):
    """Test pre-compression token estimation."""
    result = token_service.estimate_pre_compression(sample_files)
    
    assert 'total_tokens' in result
    assert 'file_tokens' in result
    assert 'file_count' in result
    assert result['file_count'] == 3
    assert result['total_tokens'] > 0


def test_token_estimation_post_compression(token_service):
    """Test post-compression estimation."""
    # Test with 491k tokens (should round to 500k)
    pre_tokens = 491000
    result = token_service.estimate_post_compression(pre_tokens)
    
    assert result['estimated_tokens'] == 50000  # ceil(491k/10) = 49.1k → round to 50k
    assert result['savings'] == pre_tokens - 50000
    assert result['savings_percent'] > 0
    assert result['compression_ratio'] > 0


def test_token_estimation_rounding(token_service):
    """Test hybrid rounding logic."""
    # Test various rounding scenarios
    test_cases = [
        (4200, math.ceil(4200 / 10)),   # Small tokens -> exact (no rounding)
        (491000, 50000),                # < 500k -> 1k rounding
        (125000, 13000),                # Example from SOP (1k rounding)
        (87000, 9000),
        (101700, 11000),
        (750000, 80000),                # > 500k -> 10k rounding
    ]
    
    for pre_tokens, expected_post in test_cases:
        result = token_service.estimate_post_compression(pre_tokens)
        assert result['estimated_tokens'] == expected_post
        assert result['savings'] == pre_tokens - expected_post
        assert result['has_valid_tokens'] is True


def test_token_estimation_zero_tokens(token_service):
    """Zero-token runs should return safe defaults."""
    result = token_service.estimate_post_compression(0)
    assert result['estimated_tokens'] == 0
    assert result['savings_percent'] == 0
    assert result['has_valid_tokens'] is False


def test_warning_threshold_at_50k():
    """Test warning threshold at 50k tokens."""
    # Test at threshold boundary
    result = get_compression_recommendation(50000)
    assert result['severity'] == 'success'
    assert result['recommended'] == True
    
    # Test just below threshold
    result = get_compression_recommendation(49999)
    assert result['severity'] == 'warning'
    assert 'Minimal savings' in result['message']
    assert result['recommended'] == True


def test_error_threshold_at_10k():
    """Test error threshold at 10k tokens."""
    # Test at threshold boundary (10k is the threshold, so <10k is error)
    result = get_compression_recommendation(9999)
    assert result['severity'] == 'error'
    assert 'Not recommended' in result['message']
    assert result['recommended'] == False
    
    # Test below threshold
    result = get_compression_recommendation(5000)
    assert result['severity'] == 'error'
    assert result['recommended'] == False
    
    # Test at exactly 10k (should be warning, not error)
    result = get_compression_recommendation(10000)
    assert result['severity'] == 'warning'
    assert result['recommended'] == True


def test_recommendation_severity_levels():
    """Test all severity levels."""
    # High tokens (>50k) - success
    result = get_compression_recommendation(100000)
    assert result['severity'] == 'success'
    assert result['icon'] == '✅'
    
    # Medium tokens (10k-50k) - warning
    result = get_compression_recommendation(30000)
    assert result['severity'] == 'warning'
    assert result['icon'] == '⚠️'
    
    # Low tokens (<10k) - error
    result = get_compression_recommendation(5000)
    assert result['severity'] == 'error'
    assert result['icon'] == '❌'


def test_format_tokens(token_service):
    """Test token formatting."""
    assert token_service.format_tokens(1000) == "1.0k"
    assert token_service.format_tokens(1500) == "1.5k"
    assert token_service.format_tokens(1000000) == "1.0M"
    assert token_service.format_tokens(500) == "500"


def test_post_compression_calculation():
    """Test post-compression calculation formula."""
    service = TokenEstimationService()
    
    # Test the formula: ceil(pre/10) rounded to nearest 1k
    pre = 491000
    result = service.estimate_post_compression(pre)
    
    # ceil(491000/10) = 49100
    # Round to nearest 1k: ceil(49100/1000) * 1000 = 50 * 1000 = 50000
    assert result['estimated_tokens'] == 50000
    
    # Verify savings calculation
    assert result['savings'] == pre - 50000
    assert result['savings_percent'] == round(((pre - 50000) / pre) * 100, 2)

