#!/usr/bin/env python3
"""Main entry point for OCR compression system."""

import sys
import argparse
from pathlib import Path

from .compression.pipeline import CompressionPipeline
from .utils.metrics import CompressionMetrics, create_visualizations


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='🌸 Sakura Sumi - OCR Compression System - Convert codebase to compressed PDFs for LLM analysis'
    )
    parser.add_argument(
        'source_dir',
        type=str,
        help='Source codebase directory to compress'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output directory for PDFs (default: {source_dir}_ocr_ready)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--exclude',
        nargs='+',
        default=[],
        help='Additional exclusion patterns'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Enable parallel processing'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=None,
        help='Number of parallel workers (default: CPU count - 1)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Batch size for sequential processing (default: 10)'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from checkpoint if available'
    )
    parser.add_argument(
        '--retry',
        type=int,
        default=3,
        help='Number of retries for failed files (default: 3)'
    )
    parser.add_argument(
        '--ocr',
        action='store_true',
        help='Enable DeepSeek-OCR compression (requires additional dependencies)'
    )
    parser.add_argument(
        '--ocr-mode',
        type=str,
        default='small',
        choices=['small', 'medium', 'large', 'maximum'],
        help='OCR compression mode (default: small)'
    )
    parser.add_argument(
        '--ocr-cache',
        type=str,
        default=None,
        help='Directory for OCR compression cache'
    )
    parser.add_argument(
        '--generate-report',
        type=str,
        default=None,
        choices=['json', 'markdown', 'html'],
        help='Generate metrics report in specified format'
    )
    parser.add_argument(
        '--generate-charts',
        action='store_true',
        help='Generate visualization charts'
    )
    
    args = parser.parse_args()
    
    # Validate source directory
    source_path = Path(args.source_dir)
    if not source_path.exists():
        print(f"Error: Source directory does not exist: {args.source_dir}")
        sys.exit(1)
    
    if not source_path.is_dir():
        print(f"Error: Source path is not a directory: {args.source_dir}")
        sys.exit(1)
    
    # Set output directory
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = Path(f"{args.source_dir}_ocr_ready")
    
    # Create pipeline
    exclusions = set(args.exclude) if args.exclude else None
    pipeline = CompressionPipeline(
        source_dir=str(source_path),
        output_dir=str(output_dir),
        exclusions=exclusions,
        parallel=args.parallel,
        max_workers=args.workers,
        batch_size=args.batch_size,
        resume=args.resume,
        retry_count=args.retry,
    )
    
    # Run pipeline
    try:
        results = pipeline.run(verbose=args.verbose)
        
        if results['success']:
            print(f"\n✓ Success! PDFs ready at: {output_dir}")
            
            # Generate report if requested
            if args.generate_report:
                from .utils.metrics import CompressionMetrics
                metrics_calc = CompressionMetrics()
                report_path = output_dir / f'metrics_report.{args.generate_report}'
                metrics_calc.generate_report(
                    results['metrics'],
                    output_path=report_path,
                    format=args.generate_report,
                )
                print(f"✓ Metrics report saved to: {report_path}")
            
            # Generate charts if requested
            if args.generate_charts:
                charts = create_visualizations(results['metrics'], output_dir / 'charts')
                if charts:
                    print(f"✓ Generated {len(charts)} visualization charts in: {output_dir / 'charts'}")
            
            sys.exit(0)
        else:
            print(f"\n✗ Pipeline failed: {results.get('error', 'Unknown error')}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

