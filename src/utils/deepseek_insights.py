"""DeepSeek-OCR insights calculation service."""

import json
import math
from pathlib import Path
from typing import Dict, Any, Optional


class DeepSeekInsightsService:
    """Service for calculating DeepSeek-OCR insights and metrics."""
    
    DEFAULT_CONFIG = {
        'compression_ratio': 10,
        'accuracy': 0.97,
        'throughput_pages_per_day': 200000,
        'avg_processing_time_per_page_seconds': 0.005,
        'text_to_vision_token_ratio': 0.1,
        'model_version': 'DeepSeek-OCR v2.0'
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize DeepSeek insights service.
        
        Args:
            config_path: Optional path to configuration JSON file
        """
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Load DeepSeek configuration from JSON or use defaults.
        
        Args:
            config_path: Optional path to configuration file
            
        Returns:
            Configuration dictionary
        """
        if config_path is None:
            # Default path: configs/deepseek_ocr.json
            config_path = Path(__file__).parent.parent.parent / 'configs' / 'deepseek_ocr.json'
        
        if config_path.exists():
            try:
                config_data = json.loads(config_path.read_text())
                # Extract deepseek_ocr section if nested
                if 'deepseek_ocr' in config_data:
                    return config_data['deepseek_ocr']
                return config_data
            except Exception as e:
                print(f"Warning: Could not load DeepSeek config: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            return self.DEFAULT_CONFIG.copy()
    
    def calculate_insights(self, file_count: int, pre_tokens: int) -> Dict[str, Any]:
        """
        Calculate DeepSeek-OCR insights for given file count and token count.
        
        Args:
            file_count: Number of files to process
            pre_tokens: Token count before compression
            
        Returns:
            Dictionary with all insights and metrics
        """
        # Estimate pages (rough: 1 file ≈ 1-3 pages, use 2 as average)
        estimated_pages = file_count * 2
        
        # Calculate processing time
        processing_time_seconds = estimated_pages * self.config['avg_processing_time_per_page_seconds']
        processing_time_formatted = self._format_duration(processing_time_seconds)
        
        # Calculate throughput capacity
        pages_per_day = self.config['throughput_pages_per_day']
        capacity_percentage = (estimated_pages / pages_per_day) * 100 if pages_per_day > 0 else 0
        
        # Calculate vision tokens using same rounding logic as token estimation
        # Apply compression ratio, then round up to nearest 1k to match "After Compression" display
        compression_ratio = self.config.get('compression_ratio', 10)
        compressed = math.ceil(pre_tokens / compression_ratio)
        vision_tokens_estimate = math.ceil(compressed / 1000) * 1000 if compressed > 0 else 1
        # Safety check: ensure vision tokens never exceed pre_tokens
        vision_tokens_estimate = min(vision_tokens_estimate, pre_tokens)
        
        return {
            'compression_ratio': self.config['compression_ratio'],
            'accuracy': self.config['accuracy'],
            'accuracy_percent': int(self.config['accuracy'] * 100),
            'estimated_pages': estimated_pages,
            'processing_time_seconds': processing_time_seconds,
            'processing_time_formatted': processing_time_formatted,
            'throughput_capacity_percent': round(capacity_percentage, 2),
            'throughput_pages_per_day': pages_per_day,
            'text_to_vision_token_ratio': self.config['text_to_vision_token_ratio'],
            'vision_tokens_estimate': vision_tokens_estimate,
            'pre_tokens': pre_tokens,
            'model_version': self.config.get('model_version', 'DeepSeek-OCR v2.0')
        }
    
    def _format_duration(self, seconds: float) -> str:
        """
        Format duration in seconds to human-readable string.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted string (e.g., "2.5 minutes", "1.2 hours")
        """
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        else:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
    
    def get_summary(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get summary view of insights (for collapsed panel).
        
        Args:
            insights: Full insights dictionary
            
        Returns:
            Summary dictionary with key metrics only
        """
        return {
            'compression_ratio': f"{insights['compression_ratio']}x",
            'accuracy': f"{insights['accuracy_percent']}%",
            'estimated_time': insights['processing_time_formatted']
        }
    
    def get_technical_details(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get technical details (for expanded panel).
        
        Args:
            insights: Full insights dictionary
            
        Returns:
            Technical details dictionary
        """
        return {
            'estimated_pages': insights['estimated_pages'],
            'text_tokens': insights['pre_tokens'],
            'vision_tokens': insights['vision_tokens_estimate'],
            'conversion_ratio': f"1k text → {int(insights['text_to_vision_token_ratio'] * 1000)} vision",
            'throughput_capacity': f"{insights['throughput_capacity_percent']}%",
            'model_version': insights['model_version']
        }

