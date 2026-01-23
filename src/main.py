#!/usr/bin/env python3
"""Main entry point for Visual Token Arbitrage Engine."""

import sys
import argparse
from pathlib import Path

from .compression.pipeline import CompressionPipeline
from .compression.density_profiles import DensityProfile
from .utils.metrics import CompressionMetrics, create_visualizations
from .security import SecurityConfig, HookConfig


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='🌸 Sakura Sumi - Visual Token Arbitrage Engine - Maximize AI context and intelligence through high-density visual arbitrage'
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
        '--density-profile',
        type=str,
        default='machine_dense',
        choices=['human', 'machine_dense'],
        help='Rendering density profile: human (readable) or machine_dense (maximum density) (default: machine_dense)'
    )
    parser.add_argument(
        '--no-topological-sort',
        action='store_true',
        help='Disable topological sorting (use alphabetical order instead)'
    )
    parser.add_argument(
        '--security-hook',
        type=str,
        action='append',
        help='Security hook command (can be specified multiple times). Format: type:command (e.g., shell:./check-secrets.sh)'
    )
    parser.add_argument(
        '--security-regex',
        type=str,
        help='Path to file containing regex patterns for security scanning (one pattern per line)'
    )
    parser.add_argument(
        '--security-on-dirty',
        type=str,
        default='fail',
        choices=['fail', 'redact', 'skip'],
        help='Action when security hook detects sensitive content (default: fail)'
    )
    
    args = parser.parse_args()
    
    # Validate source directory
    source_path = Path(args.source_dir)
    if not source_path.exists():
        print(f"\n✗ Error: Source directory does not exist: {args.source_dir}")
        print(f"   💡 Tip: Check the path and ensure the directory exists.")
        print(f"   💡 Tip: Use an absolute path or ensure you're in the correct working directory.")
        sys.exit(1)
    
    if not source_path.is_dir():
        print(f"\n✗ Error: Path is not a directory: {args.source_dir}")
        print(f"   💡 Tip: The specified path points to a file, not a directory.")
        print(f"   💡 Tip: Provide the directory containing your source code files.")
        sys.exit(1)
    
    # Set output directory
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = Path(f"{args.source_dir}_ocr_ready")
    
    # Parse density profile
    density_profile = DensityProfile(args.density_profile)
    
    # Parse security configuration
    security_config = None
    if args.security_hook or args.security_regex:
        hooks = []
        
        # Add shell command hooks
        if args.security_hook:
            for hook_spec in args.security_hook:
                if ':' in hook_spec:
                    hook_type, command = hook_spec.split(':', 1)
                    if hook_type == 'shell':
                        hooks.append(HookConfig(
                            hook_type='shell',
                            shell_command=command,
                            on_dirty=args.security_on_dirty
                        ))
                    elif hook_type == 'python':
                        # Format: python:module:function
                        parts = command.split(':', 1)
                        if len(parts) == 2:
                            hooks.append(HookConfig(
                                hook_type='python',
                                python_module=parts[0],
                                python_function=parts[1],
                                on_dirty=args.security_on_dirty
                            ))
                else:
                    # Default to shell command
                    hooks.append(HookConfig(
                        hook_type='shell',
                        shell_command=hook_spec,
                        on_dirty=args.security_on_dirty
                    ))
        
        # Add regex hook
        if args.security_regex:
            hooks.append(HookConfig(
                hook_type='regex',
                regex_file=args.security_regex,
                on_dirty=args.security_on_dirty
            ))
        
        if hooks:
            security_config = SecurityConfig(
                enabled=True,
                hooks=hooks
            )
    
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
        density_profile=density_profile,
        security_config=security_config,
        topological_sort=not args.no_topological_sort,
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

