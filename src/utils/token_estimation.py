"""Token estimation service for pre/post compression calculations."""

import math
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

from src.utils.file_discovery import FileInfo


# Constants (from SOP)
TOKEN_ENCODING = "cl100k_base"  # GPT-4 tokenizer
COMPRESSION_RATIO = 10  # 10x compression
# Hybrid rounding thresholds (balances accuracy + conservative planning)
SMALL_TOKEN_THRESHOLD = 5_000      # show exact values below this
LARGE_TOKEN_THRESHOLD = 500_000    # use 10k rounding above this
ROUNDING_INCREMENT_MEDIUM = 1_000
ROUNDING_INCREMENT_LARGE = 10_000
WARNING_THRESHOLD = 50000  # Warn below 50k tokens
ERROR_THRESHOLD = 10000  # Error below 10k tokens


class TokenEstimationService:
    """Service for token estimation before and after compression."""
    
    def __init__(self):
        """Initialize token estimation service."""
        self.encoding = None
        if TIKTOKEN_AVAILABLE:
            try:
                self.encoding = tiktoken.get_encoding(TOKEN_ENCODING)
            except Exception as e:
                print(f"Warning: Could not load tiktoken encoding: {e}")
    
    def estimate_pre_compression(self, files: List[FileInfo]) -> Dict[str, Any]:
        """
        Estimate tokens before compression using cl100k_base encoding.
        
        Args:
            files: List of FileInfo objects to estimate
            
        Returns:
            Dictionary with total_tokens, file_tokens, file_count
        """
        if not self.encoding:
            return {
                'total_tokens': 0,
                'file_tokens': {},
                'file_count': len(files),
                'error': 'tiktoken not available'
            }
        
        total_tokens = 0
        file_tokens = {}
        errors = []
        
        for file_info in files:
            try:
                content = Path(file_info.path).read_text(encoding='utf-8')
                tokens = self.encoding.encode(content)
                token_count = len(tokens)
                file_tokens[file_info.relative_path] = token_count
                total_tokens += token_count
            except Exception as e:
                errors.append({
                    'file': file_info.relative_path,
                    'error': str(e)
                })
                continue
        
        result = {
            'total_tokens': total_tokens,
            'file_tokens': file_tokens,
            'file_count': len(files),
            'files_with_errors': len(errors)
        }
        
        if errors:
            result['errors'] = errors
        
        return result
    
    def estimate_post_compression(self, pre_tokens: int) -> Dict[str, Any]:
        """
        Estimate tokens after DeepSeek-OCR compression.
        
        Formula: ceil(pre_tokens / 10) with hybrid rounding:
        - <5k tokens: no rounding (exact)
        - 5k–500k tokens: round up to nearest 1k
        - >500k tokens: round up to nearest 10k (conservative plan)
        
        Args:
            pre_tokens: Token count before compression
            
        Returns:
            Dictionary with estimated_tokens, savings, savings_percent, compression_ratio
        """
        if pre_tokens <= 0:
            return {
                'estimated_tokens': 0,
                'savings': 0,
                'savings_percent': 0,
                'compression_ratio': 0,
                'pre_tokens': pre_tokens,
                'has_valid_tokens': False
            }
        
        # Apply base compression ratio
        compressed = max(1, math.ceil(pre_tokens / COMPRESSION_RATIO))
        
        # Hybrid rounding:
        # - <5k: exact (no rounding)
        # - 5k–500k: round up to nearest 1k
        # - >500k: round up to nearest 10k (more conservative for huge jobs)
        if pre_tokens < SMALL_TOKEN_THRESHOLD:
            rounded = compressed
        elif pre_tokens < LARGE_TOKEN_THRESHOLD:
            rounded = math.ceil(compressed / ROUNDING_INCREMENT_MEDIUM) * ROUNDING_INCREMENT_MEDIUM
        else:
            rounded = math.ceil(compressed / ROUNDING_INCREMENT_LARGE) * ROUNDING_INCREMENT_LARGE
        
        # Safety check: ensure we never claim more savings than available
        rounded = min(rounded, pre_tokens)
        
        savings = max(0, pre_tokens - rounded)
        savings_percent = (savings / pre_tokens) * 100 if pre_tokens > 0 else 0
        compression_ratio = round(pre_tokens / rounded, 2) if rounded > 0 else 0
        
        return {
            'estimated_tokens': rounded,
            'savings': savings,
            'savings_percent': round(savings_percent, 2),
            'compression_ratio': compression_ratio,
            'pre_tokens': pre_tokens,
            'has_valid_tokens': True
        }
    
    def get_recommendation(self, pre_tokens: int) -> Dict[str, Any]:
        """
        Get compression recommendation based on token count.
        
        Args:
            pre_tokens: Token count before compression
            
        Returns:
            Dictionary with recommended, severity, message, action
        """
        if pre_tokens < ERROR_THRESHOLD:
            return {
                'recommended': False,
                'severity': 'error',
                'message': 'Not recommended—compression overhead exceeds benefits',
                'action': 'disable',
                'icon': '❌'
            }
        elif pre_tokens < WARNING_THRESHOLD:
            return {
                'recommended': True,
                'severity': 'warning',
                'message': 'Minimal savings—proceed for standardization?',
                'action': 'warn',
                'icon': '⚠️'
            }
        else:
            return {
                'recommended': True,
                'severity': 'success',
                'message': 'Significant compression benefits expected',
                'action': 'proceed',
                'icon': '✅'
            }
    
    def format_tokens(self, tokens: int) -> str:
        """Format token count for display."""
        if tokens >= 1_000_000:
            return f"{tokens / 1_000_000:.1f}M"
        elif tokens >= 1_000:
            return f"{tokens / 1_000:.1f}k"
        else:
            return str(tokens)


def get_compression_recommendation(pre_tokens: int) -> Dict[str, Any]:
    """
    Get compression recommendation (standalone function for convenience).
    
    Args:
        pre_tokens: Token count before compression
        
    Returns:
        Dictionary with recommendation details
    """
    service = TokenEstimationService()
    return service.get_recommendation(pre_tokens)

