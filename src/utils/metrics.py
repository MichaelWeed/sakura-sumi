"""Compression metrics and reporting utilities."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class CompressionMetrics:
    """Calculate and report compression metrics."""
    
    # Gemini context window limit
    GEMINI_CONTEXT_LIMIT = 2_000_000  # 2M tokens
    
    # Visual token estimation (approximate)
    # PDFs processed as images: ~258 tokens per image ≤384px
    # Average page: ~100-200 visual tokens
    VISUAL_TOKENS_PER_PAGE = 150
    CHARS_PER_PAGE = 3000  # Approximate
    
    def __init__(self):
        """Initialize metrics calculator."""
        self.encoding = None
        if TIKTOKEN_AVAILABLE:
            try:
                # Try to use cl100k_base (GPT-4) or fallback
                self.encoding = tiktoken.get_encoding("cl100k_base")
            except Exception:
                pass
    
    def estimate_text_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text content
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        
        if self.encoding:
            try:
                return len(self.encoding.encode(text))
            except Exception:
                pass
        
        # Fallback: rough estimation (1 token ≈ 4 characters)
        return len(text) // 4
    
    def estimate_pdf_tokens(self, pdf_size_bytes: int, page_count: Optional[int] = None) -> int:
        """
        Estimate visual tokens for PDF.
        
        Args:
            pdf_size_bytes: Size of PDF in bytes
            page_count: Optional page count (if known)
            
        Returns:
            Estimated visual token count
        """
        if page_count:
            return page_count * self.VISUAL_TOKENS_PER_PAGE
        
        # Estimate pages from size (rough: 1 page ≈ 50KB)
        estimated_pages = max(1, pdf_size_bytes // 50_000)
        return estimated_pages * self.VISUAL_TOKENS_PER_PAGE
    
    def calculate_metrics(
        self,
        original_files: List[Dict[str, Any]],
        pdf_files: List[Dict[str, Any]],
        ocr_stats: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive compression metrics.
        
        Args:
            original_files: List of original file info dicts
            pdf_files: List of PDF file info dicts
            ocr_stats: Optional OCR compression statistics
            
        Returns:
            Dictionary with all metrics
        """
        # Calculate original text tokens
        total_original_tokens = 0
        total_original_size = 0
        
        for file_info in original_files:
            size = file_info.get('size', 0)
            total_original_size += size
            
            # Estimate tokens from file size (rough: 1KB ≈ 250 tokens)
            tokens = size // 4
            total_original_tokens += tokens
        
        # Calculate PDF visual tokens
        total_pdf_tokens = 0
        total_pdf_size = 0
        
        for pdf_info in pdf_files:
            size = pdf_info.get('size', 0)
            total_pdf_size += size
            total_pdf_tokens += self.estimate_pdf_tokens(size)
        
        # Calculate OCR tokens if available
        total_ocr_tokens = None
        total_ocr_size = None
        ocr_compression_ratio = None
        
        if ocr_stats:
            total_ocr_size = ocr_stats.get('total_output_size', 0)
            # OCR compressed: estimate tokens from size
            # Compressed markdown: ~1KB ≈ 250 tokens
            total_ocr_tokens = total_ocr_size // 4 if total_ocr_size else None
            
            if total_ocr_size and total_pdf_size:
                ocr_compression_ratio = total_pdf_size / total_ocr_size
        
        # Calculate compression ratios
        pdf_compression_ratio = 0.0
        if total_pdf_size > 0:
            pdf_compression_ratio = total_original_size / total_pdf_size
        
        token_compression_ratio = 0.0
        if total_pdf_tokens > 0:
            token_compression_ratio = total_original_tokens / total_pdf_tokens
        
        # Gemini compatibility
        fits_gemini_pdf = total_pdf_tokens <= self.GEMINI_CONTEXT_LIMIT
        fits_gemini_ocr = total_ocr_tokens <= self.GEMINI_CONTEXT_LIMIT if total_ocr_tokens else None
        
        # Calculate savings
        pdf_token_savings = total_original_tokens - total_pdf_tokens
        pdf_token_savings_pct = (
            (pdf_token_savings / total_original_tokens * 100)
            if total_original_tokens > 0 else 0
        )
        
        ocr_token_savings = None
        ocr_token_savings_pct = None
        if total_ocr_tokens:
            ocr_token_savings = total_original_tokens - total_ocr_tokens
            ocr_token_savings_pct = (
                (ocr_token_savings / total_original_tokens * 100)
                if total_original_tokens > 0 else 0
            )
        
        return {
            'original': {
                'total_files': len(original_files),
                'total_size_bytes': total_original_size,
                'estimated_tokens': total_original_tokens,
            },
            'pdf': {
                'total_files': len(pdf_files),
                'total_size_bytes': total_pdf_size,
                'estimated_tokens': total_pdf_tokens,
                'compression_ratio': pdf_compression_ratio,
                'token_compression_ratio': token_compression_ratio,
                'token_savings': pdf_token_savings,
                'token_savings_percent': pdf_token_savings_pct,
            },
            'ocr': {
                'total_size_bytes': total_ocr_size,
                'estimated_tokens': total_ocr_tokens,
                'compression_ratio': ocr_compression_ratio,
            } if ocr_stats else None,
            'gemini_compatibility': {
                'context_limit': self.GEMINI_CONTEXT_LIMIT,
                'fits_pdf': fits_gemini_pdf,
                'fits_ocr': fits_gemini_ocr,
                'pdf_usage_percent': (total_pdf_tokens / self.GEMINI_CONTEXT_LIMIT * 100) if fits_gemini_pdf else None,
                'ocr_usage_percent': (total_ocr_tokens / self.GEMINI_CONTEXT_LIMIT * 100) if fits_gemini_ocr and total_ocr_tokens else None,
            },
            'summary': {
                'best_format': 'ocr' if (ocr_stats and fits_gemini_ocr) else 'pdf',
                'recommended_action': (
                    'Use OCR compression for maximum savings'
                    if (ocr_stats and fits_gemini_ocr)
                    else 'PDF format is sufficient'
                    if fits_gemini_pdf
                    else 'Codebase too large, consider splitting'
                ),
            },
        }
    
    def generate_report(
        self,
        metrics: Dict[str, Any],
        output_path: Optional[Path] = None,
        format: str = 'json',
    ) -> str:
        """
        Generate formatted report.
        
        Args:
            metrics: Metrics dictionary
            output_path: Optional path to save report
            format: Report format ('json', 'markdown', 'html')
            
        Returns:
            Report content as string
        """
        if format == 'json':
            content = json.dumps(metrics, indent=2)
        elif format == 'markdown':
            content = self._generate_markdown_report(metrics)
        elif format == 'html':
            content = self._generate_html_report(metrics)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        if output_path:
            output_path.write_text(content, encoding='utf-8')
        
        return content
    
    def _generate_markdown_report(self, metrics: Dict[str, Any]) -> str:
        """Generate Markdown report."""
        lines = [
            "# Compression Metrics Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            "",
        ]
        
        # Original stats
        orig = metrics['original']
        lines.extend([
            f"- **Original Files**: {orig['total_files']}",
            f"- **Original Size**: {self._format_size(orig['total_size_bytes'])}",
            f"- **Estimated Tokens**: {orig['estimated_tokens']:,}",
            "",
        ])
        
        # PDF stats
        pdf = metrics['pdf']
        lines.extend([
            "## PDF Compression",
            "",
            f"- **PDF Files**: {pdf['total_files']}",
            f"- **PDF Size**: {self._format_size(pdf['total_size_bytes'])}",
            f"- **Estimated Visual Tokens**: {pdf['estimated_tokens']:,}",
            f"- **Compression Ratio**: {pdf['compression_ratio']:.2f}x",
            f"- **Token Compression Ratio**: {pdf['token_compression_ratio']:.2f}x",
            f"- **Token Savings**: {pdf['token_savings']:,} ({pdf['token_savings_percent']:.1f}%)",
            "",
        ])
        
        # OCR stats
        if metrics.get('ocr'):
            ocr = metrics['ocr']
            lines.extend([
                "## OCR Compression",
                "",
                f"- **OCR Size**: {self._format_size(ocr['total_size_bytes'])}",
                f"- **Estimated Tokens**: {ocr['estimated_tokens']:,}",
                f"- **Compression Ratio**: {ocr['compression_ratio']:.2f}x",
                "",
            ])
        
        # Gemini compatibility
        gemini = metrics['gemini_compatibility']
        lines.extend([
            "## Gemini Compatibility",
            "",
            f"- **Context Limit**: {gemini['context_limit']:,} tokens",
            f"- **PDF Fits**: {'✅ Yes' if gemini['fits_pdf'] else '❌ No'}",
        ])
        
        if gemini['pdf_usage_percent']:
            lines.append(f"- **PDF Usage**: {gemini['pdf_usage_percent']:.1f}% of context window")
        
        if gemini.get('fits_ocr') is not None:
            lines.append(f"- **OCR Fits**: {'✅ Yes' if gemini['fits_ocr'] else '❌ No'}")
            if gemini.get('ocr_usage_percent'):
                lines.append(f"- **OCR Usage**: {gemini['ocr_usage_percent']:.1f}% of context window")
        
        lines.extend([
            "",
            "## Recommendation",
            "",
            f"**{metrics['summary']['recommended_action']}**",
            "",
        ])
        
        return "\n".join(lines)
    
    def _generate_html_report(self, metrics: Dict[str, Any]) -> str:
        """Generate HTML report."""
        markdown = self._generate_markdown_report(metrics)
        # Simple HTML wrapper (could be enhanced)
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Compression Metrics Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; margin-top: 30px; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
{self._markdown_to_html(markdown)}
</body>
</html>"""
        return html
    
    def _markdown_to_html(self, markdown: str) -> str:
        """Simple markdown to HTML conversion."""
        html = markdown
        # Replace headers
        lines = html.split('\n')
        html_lines = []
        for line in lines:
            if line.startswith('# '):
                html_lines.append(f'<h1>{line[2:]}</h1>')
            elif line.startswith('## '):
                html_lines.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('**') and line.endswith('**'):
                html_lines.append(f'<strong>{line[2:-2]}</strong>')
            else:
                html_lines.append(line)
        html = '<br>\n'.join(html_lines)
        return html
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes into human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"


def create_visualizations(metrics: Dict[str, Any], output_dir: Path) -> List[Path]:
    """
    Create visualization charts.
    
    Args:
        metrics: Metrics dictionary
        output_dir: Directory to save charts
        
    Returns:
        List of created chart file paths
    """
    if not MATPLOTLIB_AVAILABLE:
        return []
    
    output_dir.mkdir(parents=True, exist_ok=True)
    charts = []
    
    # Size comparison chart
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        categories = ['Original', 'PDF']
        sizes = [
            metrics['original']['total_size_bytes'],
            metrics['pdf']['total_size_bytes'],
        ]
        
        if metrics.get('ocr'):
            categories.append('OCR')
            sizes.append(metrics['ocr']['total_size_bytes'])
        
        ax.bar(categories, [s / 1024 / 1024 for s in sizes])  # Convert to MB
        ax.set_ylabel('Size (MB)')
        ax.set_title('File Size Comparison')
        ax.grid(axis='y', alpha=0.3)
        
        chart_path = output_dir / 'size_comparison.png'
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        charts.append(chart_path)
    except Exception as e:
        print(f"Warning: Could not create size chart: {e}")
    
    # Token comparison chart
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        categories = ['Original', 'PDF']
        tokens = [
            metrics['original']['estimated_tokens'],
            metrics['pdf']['estimated_tokens'],
        ]
        
        if metrics.get('ocr') and metrics['ocr']['estimated_tokens']:
            categories.append('OCR')
            tokens.append(metrics['ocr']['estimated_tokens'])
        
        ax.bar(categories, [t / 1000 for t in tokens])  # Convert to thousands
        ax.set_ylabel('Tokens (thousands)')
        ax.set_title('Token Count Comparison')
        ax.grid(axis='y', alpha=0.3)
        
        # Add Gemini limit line
        gemini_limit = metrics['gemini_compatibility']['context_limit'] / 1000
        ax.axhline(y=gemini_limit, color='r', linestyle='--', label='Gemini Limit (2M)')
        ax.legend()
        
        chart_path = output_dir / 'token_comparison.png'
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        charts.append(chart_path)
    except Exception as e:
        print(f"Warning: Could not create token chart: {e}")
    
    return charts

