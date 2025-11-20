"""Main compression pipeline orchestrator with enhanced batch processing."""

import sys
import json
import signal
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count
import time

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

from ..utils.file_discovery import FileDiscovery, FileInfo
from ..utils.metrics import CompressionMetrics, create_visualizations
from ..utils.telemetry import TelemetryLogger
from .pdf_converter import PDFConverter


class CompressionPipeline:
    """Orchestrates the complete compression pipeline with enhanced batch processing."""
    
    def __init__(
        self,
        source_dir: str,
        output_dir: str,
        exclusions: Optional[set] = None,
        parallel: bool = False,
        max_workers: Optional[int] = None,
        batch_size: int = 10,
        resume: bool = False,
        checkpoint_file: Optional[str] = None,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        hybrid_mode: bool = False,  # HYBRID_MODE_START
    ):
        """
        Initialize compression pipeline.
        
        Args:
            source_dir: Source codebase directory
            output_dir: Output directory for PDFs
            exclusions: Additional exclusion patterns
            parallel: Enable parallel processing
            max_workers: Maximum number of worker processes/threads (None = auto)
            batch_size: Number of files to process in each batch
            resume: Resume from checkpoint if available
            checkpoint_file: Path to checkpoint file for state saving
            retry_count: Number of retries for failed files
            retry_delay: Delay between retries in seconds
        """
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.exclusions = exclusions or set()
        self.parallel = parallel
        self.max_workers = max_workers or (cpu_count() - 1 or 1)
        self.hybrid_mode = hybrid_mode  # HYBRID_MODE_START
        self.batch_size = batch_size
        self.resume = resume
        self.checkpoint_file = Path(checkpoint_file) if checkpoint_file else self.output_dir / '.compression_checkpoint.json'
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        
        self.discovery = FileDiscovery(str(self.source_dir), self.exclusions)
        self.converter = PDFConverter(str(self.output_dir), hybrid_mode=hybrid_mode)  # HYBRID_MODE_START
        self.metrics = CompressionMetrics()
        self.telemetry = TelemetryLogger(self.output_dir)
        self.failure_report_path = self.output_dir / 'failed_files.json'
        
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.processed_files: set = set()
        self.failed_files: List[Dict[str, Any]] = []
        self.cancelled = False
        
        # Setup signal handler for graceful shutdown (only in main thread)
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except ValueError:
            # Signal handlers can only be set in main thread
            # This is expected when running in background threads
            pass
    
    def _signal_handler(self, signum, frame):
        """Handle cancellation signals gracefully."""
        self.cancelled = True
        print("\n\nCancellation requested. Finishing current batch and saving checkpoint...")
    
    def _load_checkpoint(self) -> Dict[str, Any]:
        """Load checkpoint state if it exists."""
        if not self.checkpoint_file.exists():
            return {'processed_files': [], 'failed_files': []}
        
        try:
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load checkpoint: {e}")
            return {'processed_files': [], 'failed_files': []}
    
    def _save_checkpoint(self, processed_files: set, failed_files: List[Dict]):
        """Save checkpoint state."""
        try:
            checkpoint_data = {
                'processed_files': list(processed_files),
                'failed_files': failed_files,
                'timestamp': datetime.now().isoformat(),
                'source_dir': str(self.source_dir),
                'output_dir': str(self.output_dir),
            }
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save checkpoint: {e}")
    
    def _convert_file_with_retry(self, file_info: FileInfo) -> tuple[Optional[Path], Optional[str]]:
        """Convert a file with retry logic."""
        last_error = None
        
        for attempt in range(self.retry_count):
            if self.cancelled:
                return None, "Cancelled"
            
            try:
                pdf_path = self.converter.convert_file(file_info)
                if pdf_path:
                    return pdf_path, None
                else:
                    last_error = "PDF generation returned None"
            except Exception as e:
                last_error = str(e)
            
            if attempt < self.retry_count - 1:
                time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
        
        return None, last_error
    
    def _process_file_batch(self, files: List[FileInfo], progress_callback: Optional[Callable] = None) -> tuple[int, int, List[Dict]]:
        """Process a batch of files."""
        converted = 0
        failed = 0
        errors = []
        
        for file_info in files:
            if self.cancelled:
                break
            
            # Check if already processed (resume mode)
            if self.resume and file_info.relative_path in self.processed_files:
                continue
            
            pdf_path, error = self._convert_file_with_retry(file_info)
            
            if pdf_path:
                converted += 1
                self.processed_files.add(file_info.relative_path)
            else:
                failed += 1
                error_info = {
                    'file': file_info.relative_path,
                    'error': error or 'Unknown error',
                    'attempts': self.retry_count,
                }
                errors.append(error_info)
                self.failed_files.append(error_info)
            
            if progress_callback:
                progress_callback(file_info, pdf_path is not None)
        
        return converted, failed, errors
    
    def _process_parallel(self, files: List[FileInfo], verbose: bool = True) -> tuple[int, int]:
        """Process files in parallel."""
        # Filter out already processed files
        files_to_process = [
            f for f in files
            if not (self.resume and f.relative_path in self.processed_files)
        ]
        
        if not files_to_process:
            return len(files), 0
        
        converted_count = 0
        failed_count = 0
        
        # Use ThreadPoolExecutor for I/O-bound PDF generation
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Create progress bar
            if tqdm and verbose:
                pbar = tqdm(
                    total=len(files_to_process),
                    desc="Converting files",
                    unit="file",
                    ncols=100,
                )
            else:
                pbar = None
            
            # Submit all tasks
            future_to_file = {
                executor.submit(self._convert_file_with_retry, file_info): file_info
                for file_info in files_to_process
            }
            
            # Process completed tasks
            for future in as_completed(future_to_file):
                if self.cancelled:
                    future.cancel()
                    continue
                
                file_info = future_to_file[future]
                try:
                    pdf_path, error = future.result()
                    if pdf_path:
                        converted_count += 1
                        self.processed_files.add(file_info.relative_path)
                    else:
                        failed_count += 1
                        self.failed_files.append({
                            'file': file_info.relative_path,
                            'error': error or 'Unknown error',
                        })
                except Exception as e:
                    failed_count += 1
                    self.failed_files.append({
                        'file': file_info.relative_path,
                        'error': str(e),
                    })
                
                if pbar:
                    pbar.update(1)
                    pbar.set_postfix({
                        'converted': converted_count,
                        'failed': failed_count,
                    })
            
            if pbar:
                pbar.close()
        
        return converted_count, failed_count
    
    def run(self, verbose: bool = True) -> dict:
        """
        Run the complete compression pipeline.
        
        Args:
            verbose: Print progress information
            
        Returns:
            Dictionary with pipeline results and statistics
        """
        self.start_time = datetime.now()
        
        if verbose:
            print("Starting compression pipeline...")
            print(f"Source: {self.source_dir}")
            print(f"Output: {self.output_dir}")
            print(f"Parallel: {self.parallel} (workers: {self.max_workers})")
            print(f"Resume: {self.resume}")
            print()
        
        # Load checkpoint if resuming
        if self.resume:
            checkpoint = self._load_checkpoint()
            self.processed_files = set(checkpoint.get('processed_files', []))
            self.failed_files = checkpoint.get('failed_files', [])
            if verbose and self.processed_files:
                print(f"Resuming: {len(self.processed_files)} files already processed")
        
        # Step 1: Discover files
        if verbose:
            print("Step 1: Discovering files...")
        
        files = self.discovery.discover()
        
        if verbose:
            self.discovery.print_summary()
        
        if not files:
            discovery_stats = self.discovery.generate_inventory_report()
            unsupported = discovery_stats.get('statistics', {}).get('unsupported_files', {})
            total_scanned = discovery_stats.get('statistics', {}).get('total_scanned', 0)
            
            # Build detailed error message
            if unsupported:
                unsupported_list = ', '.join(f"{ext} ({count})" for ext, count in sorted(
                    unsupported.items(), key=lambda x: x[1], reverse=True
                )[:5])  # Show top 5
                if len(unsupported) > 5:
                    unsupported_list += f" and {len(unsupported) - 5} more"
                error_message = (
                    f"No supported files discovered. Found {total_scanned} file(s) total, "
                    f"but they are unsupported types: {unsupported_list}. "
                    f"Sakura Sumi only processes text-based source code files. "
                    f"See https://github.com/MichaelWeed/sakura-sumi#file-type-support for supported types."
                )
            else:
                error_message = (
                    "No files discovered in the specified directory. "
                    "Please ensure the directory contains supported source code files. "
                    f"See https://github.com/MichaelWeed/sakura-sumi#file-type-support for supported types."
                )
            
            if verbose:
                print("No files found to process!")
                if unsupported:
                    print(f"\n⚠️  Found {total_scanned} file(s) but none are supported types.")
                    print(f"   Unsupported file types: {', '.join(sorted(unsupported.keys()))}")
                    print("   💡 Tip: Sakura Sumi only processes text-based source code files.")
                    print("      See README.md for a complete list of supported file types.")
            
            failure_results = self._build_failure_result(
                error_message=error_message,
                discovery_stats=discovery_stats,
                duration_seconds=(datetime.now() - self.start_time).total_seconds(),
            )
            self._emit_telemetry('pipeline_run', failure_results, {
                'reason': 'no_files',
                'total_scanned': total_scanned,
                'unsupported_types': list(unsupported.keys()) if unsupported else []
            })
            return failure_results
        
        # Step 2: Convert files to PDFs
        if verbose:
            print(f"\nStep 2: Converting {len(files)} files to PDFs...")
            if self.parallel:
                print(f"Using {self.max_workers} workers for parallel processing")
        
        converted_count = 0
        failed_count = 0
        
        if self.parallel:
            # Parallel processing
            converted_count, failed_count = self._process_parallel(files, verbose)
        else:
            # Sequential processing with progress bar
            files_to_process = [
                f for f in files
                if not (self.resume and f.relative_path in self.processed_files)
            ]
            
            if files_to_process:
                if tqdm and verbose:
                    pbar = tqdm(
                        total=len(files_to_process),
                        desc="Converting files",
                        unit="file",
                        ncols=100,
                    )
                else:
                    pbar = None
                
                batch_start = 0
                while batch_start < len(files_to_process) and not self.cancelled:
                    batch_end = min(batch_start + self.batch_size, len(files_to_process))
                    batch = files_to_process[batch_start:batch_end]
                    
                    batch_converted, batch_failed, batch_errors = self._process_file_batch(
                        batch,
                        lambda f, success: pbar.update(1) if pbar else None
                    )
                    
                    converted_count += batch_converted
                    failed_count += batch_failed
                    
                    # Save checkpoint after each batch
                    self._save_checkpoint(self.processed_files, self.failed_files)
                    
                    batch_start = batch_end
                
                if pbar:
                    pbar.close()
        
        if verbose:
            print(f"\n\nConversion complete!")
            if self.cancelled:
                print("⚠️  Processing was cancelled. Checkpoint saved.")
        
        # Step 3: Generate reports
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        discovery_stats = self.discovery.generate_inventory_report()
        conversion_stats = self.converter.get_stats()
        
        # Final checkpoint save
        self._save_checkpoint(self.processed_files, self.failed_files)
        
        # Calculate metrics
        original_files = [
            {'size': f.size, 'path': f.relative_path}
            for f in files
        ]
        
        # Get PDF file info
        pdf_files = []
        for pdf_path in self.output_dir.rglob('*.pdf'):
            if pdf_path.is_file():
                pdf_files.append({
                    'size': pdf_path.stat().st_size,
                    'path': str(pdf_path.relative_to(self.output_dir)),
                })
        
        compression_metrics = self.metrics.calculate_metrics(
            original_files=original_files,
            pdf_files=pdf_files,
            ocr_stats=None,  # Will be added if OCR is used
        )
        
        files_already_processed = len(self.processed_files) - converted_count if self.resume else 0
        summary = self._create_summary(
            files_discovered=len(files),
            files_converted=converted_count,
            files_failed=failed_count,
            files_already_processed=files_already_processed,
            conversion_stats=conversion_stats,
        )
        
        results = {
            'success': True,
            'cancelled': self.cancelled,
            'source_directory': self._sanitize_path(self.source_dir),  # Sanitized: basename only
            'output_directory': self._sanitize_path(self.output_dir),  # Sanitized: basename only
            'duration_seconds': duration,
            'discovery': discovery_stats,
            'conversion': conversion_stats,
            'metrics': compression_metrics,
            'summary': summary,
            'failed_files': self.failed_files,
        }
        
        if verbose:
            self._print_summary(results)
            self._print_metrics_summary(compression_metrics)
        
        self._write_failure_report(results)
        self._attach_telemetry_reference(results)
        self._emit_telemetry('pipeline_run', results)
        return results
    
    def _print_metrics_summary(self, metrics: Dict[str, Any]):
        """Print metrics summary."""
        print(f"\n{'='*60}")
        print("Compression Metrics")
        print(f"{'='*60}")
        
        orig = metrics['original']
        pdf = metrics['pdf']
        gemini = metrics['gemini_compatibility']
        
        print(f"Original: {orig['estimated_tokens']:,} tokens ({self._format_size(orig['total_size_bytes'])})")
        print(f"PDF:      {pdf['estimated_tokens']:,} tokens ({self._format_size(pdf['total_size_bytes'])})")
        print(f"Token Compression: {pdf['token_compression_ratio']:.2f}x")
        print(f"Token Savings: {pdf['token_savings']:,} ({pdf['token_savings_percent']:.1f}%)")
        print(f"\nGemini Compatibility:")
        print(f"  Context Limit: {gemini['context_limit']:,} tokens")
        print(f"  PDF Fits: {'✅ Yes' if gemini['fits_pdf'] else '❌ No'}")
        if gemini.get('pdf_usage_percent'):
            print(f"  PDF Usage: {gemini['pdf_usage_percent']:.1f}% of context window")
        
        if metrics.get('ocr'):
            ocr = metrics['ocr']
            print(f"\nOCR:      {ocr['estimated_tokens']:,} tokens ({self._format_size(ocr['total_size_bytes'])})")
            print(f"  OCR Fits: {'✅ Yes' if gemini.get('fits_ocr') else '❌ No'}")
            if gemini.get('ocr_usage_percent'):
                print(f"  OCR Usage: {gemini['ocr_usage_percent']:.1f}% of context window")
        
        print(f"\nRecommendation: {metrics['summary']['recommended_action']}")
        print(f"{'='*60}\n")
    
    def _print_summary(self, results: dict):
        """Print pipeline summary."""
        print(f"\n{'='*60}")
        print("Compression Pipeline Summary")
        print(f"{'='*60}")
        print(f"Duration: {results['duration_seconds']:.2f} seconds")
        print(f"Files Discovered: {results['summary']['files_discovered']}")
        print(f"Files Converted: {results['summary']['files_converted']}")
        print(f"Files Failed: {results['summary']['files_failed']}")
        if results['summary']['files_already_processed'] > 0:
            print(f"Files Already Processed: {results['summary']['files_already_processed']}")
        print(f"\nSize Statistics:")
        print(f"  Original: {self._format_size(results['summary']['total_size_original_bytes'])}")
        print(f"  PDF:      {self._format_size(results['summary']['total_size_pdf_bytes'])}")
        print(f"  Ratio:    {results['summary']['compression_ratio']:.2f}x")
        
        if results['failed_files']:
            print(f"\nFailed Files ({len(results['failed_files'])}):")
            for error in results['failed_files'][:5]:  # Show first 5
                print(f"  - {error['file']}: {error['error']}")
            if len(results['failed_files']) > 5:
                print(f"  ... and {len(results['failed_files']) - 5} more")
        
        print(f"{'='*60}\n")
    
    def run_smart_concatenation(
        self,
        max_pdfs: int = 10,
        max_pages_per_pdf: int = 100,
        max_size_per_pdf_mb: int = 10,
        max_total_pages: int = 1000,
        verbose: bool = True,
    ) -> dict:
        """
        Run compression with smart concatenation strategy.
        Ensures exactly max_pdfs (default 10) PDFs maximum.
        
        Args:
            max_pdfs: Maximum number of PDFs to create (hard limit)
            max_pages_per_pdf: Maximum pages per individual PDF
            max_size_per_pdf_mb: Maximum size per PDF in MB
            max_total_pages: Maximum total pages across all PDFs
            verbose: Print progress information
            
        Returns:
            Dictionary with pipeline results and statistics
        """
        from .smart_concatenation import SmartConcatenationEngine
        
        self.start_time = datetime.now()
        
        if verbose:
            print("Starting smart concatenation pipeline...")
            print(f"Source: {self.source_dir}")
            print(f"Output: {self.output_dir}")
            print(f"Max PDFs: {max_pdfs}")
            print(f"Max pages per PDF: {max_pages_per_pdf}")
            print(f"Max size per PDF: {max_size_per_pdf_mb} MB")
            print()
        
        # Step 1: Discover files
        if verbose:
            print("Step 1: Discovering files...")
        
        files = self.discovery.discover()
        
        if verbose:
            self.discovery.print_summary()
        
        if not files:
            discovery_stats = self.discovery.generate_inventory_report()
            unsupported = discovery_stats.get('statistics', {}).get('unsupported_files', {})
            total_scanned = discovery_stats.get('statistics', {}).get('total_scanned', 0)
            
            # Build detailed error message
            if unsupported:
                unsupported_list = ', '.join(f"{ext} ({count})" for ext, count in sorted(
                    unsupported.items(), key=lambda x: x[1], reverse=True
                )[:5])  # Show top 5
                if len(unsupported) > 5:
                    unsupported_list += f" and {len(unsupported) - 5} more"
                error_message = (
                    f"No supported files discovered. Found {total_scanned} file(s) total, "
                    f"but they are unsupported types: {unsupported_list}. "
                    f"Sakura Sumi only processes text-based source code files. "
                    f"See https://github.com/MichaelWeed/sakura-sumi#file-type-support for supported types."
                )
            else:
                error_message = (
                    "No files discovered in the specified directory. "
                    "Please ensure the directory contains supported source code files. "
                    f"See https://github.com/MichaelWeed/sakura-sumi#file-type-support for supported types."
                )
            
            if verbose:
                print("No files found to process!")
                if unsupported:
                    print(f"\n⚠️  Found {total_scanned} file(s) but none are supported types.")
                    print(f"   Unsupported file types: {', '.join(sorted(unsupported.keys()))}")
                    print("   💡 Tip: Sakura Sumi only processes text-based source code files.")
                    print("      See README.md for a complete list of supported file types.")
            
            failure_results = self._build_failure_result(
                error_message=error_message,
                discovery_stats=discovery_stats,
                duration_seconds=(datetime.now() - self.start_time).total_seconds(),
            )
            self._emit_telemetry('pipeline_smart_concatenation', failure_results, {
                'reason': 'no_files',
                'total_scanned': total_scanned,
                'unsupported_types': list(unsupported.keys()) if unsupported else []
            })
            return failure_results
        
        # Step 2: Group files using smart concatenation
        if verbose:
            print(f"\nStep 2: Grouping {len(files)} files into PDFs...")
        
        engine = SmartConcatenationEngine(
            source_dir=self.source_dir,
            max_pdfs=max_pdfs,
            max_pages_per_pdf=max_pages_per_pdf,
            max_size_per_pdf_mb=max_size_per_pdf_mb,
            max_total_pages=max_total_pages,
        )
        
        pdf_groups = engine.group_files(files)
        
        if verbose:
            print(f"\nSmart Concatenation Plan:")
            print(f"Total files discovered: {len(files)}")
            print(f"Total directories found: {len(set(str(Path(f.relative_path).parent) if len(Path(f.relative_path).parts) > 1 else '' for f in files))}")
            print(f"Total PDFs to create: {len(pdf_groups)}")
            for group in pdf_groups:
                print(f"  - {group.name}: {len(group.files)} files")
                if len(group.files) > 0:
                    print(f"    Sample files: {', '.join([f.relative_path for f in group.files[:3]])}")
                    if len(group.files) > 3:
                        print(f"    ... and {len(group.files) - 3} more files")
        
        # Step 3: Generate PDFs
        if verbose:
            print(f"\nStep 3: Generating {len(pdf_groups)} PDFs...")
        
        converted_count = 0
        failed_count = 0
        pdf_results = []
        
        for group in pdf_groups:
            if self.cancelled:
                break
            
            pdf_path = self.converter.concatenate_files_to_pdf(
                files=group.files,
                pdf_name=group.name.replace('.pdf', ''),
                max_pages=max_pages_per_pdf,
                max_size_bytes=max_size_per_pdf_mb * 1024 * 1024,
            )
            
            if pdf_path:
                converted_count += len(group.files)
                pdf_results.append({
                    'name': group.name,
                    'path': str(pdf_path.relative_to(self.output_dir)),
                    'file_count': len(group.files),
                    'size_bytes': pdf_path.stat().st_size if pdf_path.exists() else 0,
                })
            else:
                failed_count += len(group.files)
                self.failed_files.append({
                    'group': group.name,
                    'files': [f.relative_path for f in group.files],
                    'error': 'PDF generation failed'
                })
        
        if verbose:
            print(f"\n\nSmart concatenation complete!")
            if self.cancelled:
                print("⚠️  Processing was cancelled.")
        
        # Step 4: Generate reports
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        discovery_stats = self.discovery.generate_inventory_report()
        conversion_stats = self.converter.get_stats()
        
        # Calculate metrics
        original_files = [
            {'size': f.size, 'path': f.relative_path}
            for f in files
        ]
        
        pdf_files = []
        for pdf_result in pdf_results:
            pdf_files.append({
                'size': pdf_result['size_bytes'],
                'path': pdf_result['path'],
            })
        
        compression_metrics = self.metrics.calculate_metrics(
            original_files=original_files,
            pdf_files=pdf_files,
            ocr_stats=None,
        )
        
        summary = self._create_summary(
            files_discovered=len(files),
            files_converted=converted_count,
            files_failed=failed_count,
            files_already_processed=0,
            conversion_stats=conversion_stats,
        )
        summary['total_pdfs'] = len(pdf_results)
        
        results = {
            'success': True,
            'cancelled': self.cancelled,
            'source_directory': self._sanitize_path(self.source_dir),  # Sanitized: basename only
            'output_directory': self._sanitize_path(self.output_dir),  # Sanitized: basename only
            'duration_seconds': duration,
            'discovery': discovery_stats,
            'conversion': conversion_stats,
            'metrics': compression_metrics,
            'smart_concatenation': {
                'max_pdfs': max_pdfs,
                'pdf_groups': pdf_results,
                'total_pdfs_created': len(pdf_results),
            },
            'summary': summary,
            'failed_files': self.failed_files,
        }
        
        if verbose:
            self._print_summary(results)
            self._print_metrics_summary(compression_metrics)
        
        self._write_failure_report(results)
        self._attach_telemetry_reference(results)
        self._emit_telemetry('pipeline_smart_concatenation', results)
        return results
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes into human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def _sanitize_path(self, path: Path) -> str:
        """
        Sanitize path to return only basename, avoiding exposure of full directory structure.
        
        Args:
            path: Path object to sanitize
            
        Returns:
            Basename of the path (directory name only)
        """
        if isinstance(path, str):
            path = Path(path)
        return path.name if path.name else Path(path).name
    
    def _prepare_conversion_stats(self) -> Dict[str, Any]:
        stats = self.converter.get_stats()
        return {
            'total_size_original': stats.get('total_size_original', 0),
            'total_size_pdf': stats.get('total_size_pdf', 0),
            'compression_ratio': stats.get('compression_ratio', 0.0),
            **{k: v for k, v in stats.items() if k not in {'total_size_original', 'total_size_pdf', 'compression_ratio'}}
        }

    def _create_summary(
        self,
        *,
        files_discovered: int,
        files_converted: int,
        files_failed: int,
        files_already_processed: int,
        conversion_stats: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        stats = conversion_stats or self._prepare_conversion_stats()
        return {
            'files_discovered': files_discovered,
            'files_converted': files_converted,
            'files_failed': files_failed,
            'files_already_processed': files_already_processed,
            'total_size_original_bytes': stats.get('total_size_original', 0),
            'total_size_pdf_bytes': stats.get('total_size_pdf', 0),
            'compression_ratio': stats.get('compression_ratio', 0.0),
        }

    def _build_failure_result(
        self,
        error_message: str,
        discovery_stats: Optional[Dict[str, Any]] = None,
        duration_seconds: float = 0.0,
    ) -> Dict[str, Any]:
        discovery_stats = discovery_stats or {'statistics': {'total_files': 0}}
        conversion_stats = self._prepare_conversion_stats()
        files_discovered = discovery_stats.get('statistics', {}).get('total_files', 0)
        summary = self._create_summary(
            files_discovered=files_discovered,
            files_converted=0,
            files_failed=len(self.failed_files),
            files_already_processed=len(self.processed_files),
            conversion_stats=conversion_stats,
        )
        result = {
            'success': False,
            'cancelled': self.cancelled,
            'source_directory': self._sanitize_path(self.source_dir),  # Sanitized: basename only
            'output_directory': self._sanitize_path(self.output_dir),  # Sanitized: basename only
            'duration_seconds': duration_seconds,
            'discovery': discovery_stats,
            'conversion': conversion_stats,
            'metrics': {},
            'summary': summary,
            'failed_files': self.failed_files,
            'error': error_message,
        }
        self._write_failure_report(result)
        self._attach_telemetry_reference(result)
        return result

    def _emit_telemetry(self, event: str, results: Dict[str, Any], extra: Optional[Dict[str, Any]] = None) -> None:
        payload = {
            'success': results.get('success'),
            'error': results.get('error'),
            'cancelled': results.get('cancelled', False),
            'summary': results.get('summary', {}),
            'duration_seconds': results.get('duration_seconds'),
        }
        if extra:
            payload.update(extra)
        self.telemetry.log_event(event, payload)
    
    def _attach_telemetry_reference(self, results: Dict[str, Any]) -> None:
        if self.telemetry.enabled:
            results['telemetry_log'] = str(self.telemetry.log_path)
        else:
            results['telemetry_log'] = None

    def _write_failure_report(self, results: Dict[str, Any]) -> None:
        failures = results.get('failed_files') or []
        conversion_errors = (results.get('conversion') or {}).get('errors', [])
        report_needed = bool(failures or conversion_errors)
        
        if not report_needed:
            results['failure_report'] = None
            if self.failure_report_path.exists():
                try:
                    self.failure_report_path.unlink()
                except Exception as exc:
                    print(f"Warning: Could not delete failure report: {exc}")
            return
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'source_directory': self._sanitize_path(self.source_dir),  # Sanitized: basename only
            'output_directory': self._sanitize_path(self.output_dir),  # Sanitized: basename only
            'failures': failures,
            'conversion_errors': conversion_errors,
        }
        
        try:
            self.failure_report_path.parent.mkdir(parents=True, exist_ok=True)
            with self.failure_report_path.open('w', encoding='utf-8') as handle:
                json.dump(report, handle, indent=2)
            results['failure_report'] = str(self.failure_report_path)
        except Exception as exc:
            print(f"Warning: Could not write failure report: {exc}")
            results['failure_report'] = None
