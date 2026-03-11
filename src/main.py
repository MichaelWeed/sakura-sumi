#!/usr/bin/env python3
"""Main entry point for OCR Compression System."""

import sys
import argparse
from pathlib import Path

from .compression.pipeline import CompressionPipeline
from .utils.metrics import create_visualizations


# Force unbuffered output for better visibility in Automator
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
sys.stderr.reconfigure(line_buffering=True) if hasattr(sys.stderr, 'reconfigure') else None


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
    parser.add_argument(
        '--no-smart-concatenation',
        action='store_true',
        help='Disable smart concatenation (creates one PDF per file)'
    )
    parser.add_argument(
        '--max-pdfs',
        type=int,
        default=10,
        help='Maximum number of PDFs to create with smart concatenation (default: 10)'
    )
    parser.add_argument(
        '--max-pages-per-pdf',
        type=int,
        default=100,
        help='Maximum pages per PDF (default: 100)'
    )
    parser.add_argument(
        '--max-size-per-pdf-mb',
        type=int,
        default=10,
        help='Maximum size per PDF in MB (default: 10)'
    )
    parser.add_argument(
        '--max-total-pages',
        type=int,
        default=1000,
        help='Maximum total pages across all PDFs (default: 1000)'
    )
    parser.add_argument(
        '--key-folders',
        type=str,
        nargs='+',
        default=None,
        help='Custom key folders for smart concatenation priority (space-separated, e.g., --key-folders app core shared). Default: src, components, api, services, utils, lib, public, tests, test, specs, config, scripts'
    )
    parser.add_argument(
        '--no-topological-sort',
        action='store_true',
        help='Disable topological sorting (use alphabetical order instead)'
    )
    
    args = parser.parse_args()
    
    # Validate source directory and resolve to absolute path
    source_path = Path(args.source_dir).expanduser().resolve()
    if not source_path.exists():
        print(f"\n✗ Error: Source directory does not exist: {args.source_dir}")
        print("   💡 Tip: Check the path and ensure the directory exists.")
        print("   💡 Tip: Use an absolute path or ensure you're in the correct working directory.")
        sys.exit(1)
    
    if not source_path.is_dir():
        print(f"\n✗ Error: Path is not a directory: {args.source_dir}")
        print(f"   💡 Tip: The specified path points to a file, not a directory.")
        print(f"   💡 Tip: Provide the directory containing your source code files.")
        sys.exit(1)
    
    # Set output directory (use resolved absolute path)
    if args.output:
        output_dir = Path(args.output).expanduser().resolve()
    else:
        # Construct output directory next to source directory using absolute path
        output_dir = source_path.parent / f"{source_path.name}_ocr_ready"
    
    # Safety check: Detect if source path is a user home directory (common Quick Action mistake)
    # If source is /Users/johndoe, it means the Quick Action passed the wrong path
    restricted_parents = [Path('/Users'), Path('/System'), Path('/Library')]
    if source_path.parent in restricted_parents:
        # Check if this looks like a user home directory name (common usernames)
        common_home_names = ['johndoe', 'root', 'admin', 'system', 'nobody', 'daemon']
        if source_path.name.lower() in common_home_names or source_path == Path.home():
            error_msg = (
                f"Error: Invalid source directory: {source_path}\n"
                f"Tip: The selected path appears to be a user home directory, not a project directory.\n"
                f"Tip: This usually means the Quick Action didn't receive the correct folder path.\n"
                f"Tip: Please try:\n"
                f"  1. Right-click on the actual project folder (e.g., aether_-the-document-engineer)\n"
                f"  2. Not on the Downloads folder or user folder\n"
                f"  3. Or use the command line: ./scripts/compress_with_defaults.sh '/Users/johndoe/Downloads/aether_-the-document-engineer'"
            )
            # Print to both stdout and stderr to ensure Automator captures it
            print(f"\n✗ {error_msg}", file=sys.stderr)
            print(f"\n✗ {error_msg}", file=sys.stdout)
            sys.stderr.flush()
            sys.stdout.flush()
            sys.exit(1)
    
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
        # Use smart concatenation by default (groups files into max 10 PDFs)
        # Users can disable with --no-smart-concatenation flag
        # Parse key folders if provided
        key_folders = None
        if args.key_folders:
            key_folders = set(args.key_folders)
        
        if args.no_smart_concatenation:
            results = pipeline.run(verbose=args.verbose)
        else:
            results = pipeline.run_smart_concatenation(
                max_pdfs=args.max_pdfs,
                max_pages_per_pdf=args.max_pages_per_pdf,
                max_size_per_pdf_mb=args.max_size_per_pdf_mb,
                max_total_pages=args.max_total_pages,
                key_folders=key_folders,
                verbose=args.verbose
            )
        
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
            error_msg = results.get('error', 'Unknown error occurred')
            print(f"\n✗ Pipeline failed: {error_msg}")
            print(f"   💡 Tip: Check the output directory for detailed error logs: {output_dir}")
            print(f"   💡 Tip: Run with --verbose flag for more detailed error information.")
            print(f"   💡 Tip: Check file permissions and ensure you have write access to the output directory.")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        print("   💡 Tip: Use --resume flag to continue from where you left off.")
        sys.exit(130)
    except Exception as e:
        error_type = type(e).__name__
        print(f"\n✗ Unexpected error ({error_type}): {str(e)}")
        print(f"   💡 Tip: Run with --verbose flag to see the full stack trace.")
        print(f"   💡 Tip: Check that all dependencies are installed: pip install -r requirements.txt")
        print(f"   💡 Tip: Ensure you have sufficient disk space and file permissions.")
        import traceback
        if args.verbose:
            print("\nFull traceback:")
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

