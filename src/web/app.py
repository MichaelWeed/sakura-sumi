"""Flask web application for 🌸 Sakura Sumi - OCR Compression Portal."""

import os
import json
import threading
import subprocess
import platform
import re
import shutil
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import zipfile
import tempfile
from datetime import datetime

from ..compression.pipeline import CompressionPipeline
from ..compression.ocr_compression import OCRCompressor, create_ocr_compressor
from ..utils.token_estimation import TokenEstimationService
from ..utils.deepseek_insights import DeepSeekInsightsService
from ..utils.file_discovery import FileDiscovery

app = Flask(__name__)
# Use environment variable for secret key (required for multi-instance deployments)
# Falls back to random key for local development only
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24).hex())
if not os.environ.get('FLASK_SECRET_KEY'):
    import warnings
    warnings.warn("FLASK_SECRET_KEY not set. Using ephemeral key. Sessions will not persist across restarts.")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Job storage (in production, use Redis or database)
jobs = {}
job_counter = 0
JOBS_FILE = Path(__file__).parent.parent.parent / 'build' / 'jobs.json'

# Load jobs from file on startup
def load_jobs():
    """Load jobs from persistent storage."""
    global jobs, job_counter
    if JOBS_FILE.exists():
        try:
            with open(JOBS_FILE, 'r') as f:
                data = json.load(f)
                jobs = data.get('jobs', {})
                job_counter = data.get('counter', 0)
        except Exception as e:
            print(f"Warning: Could not load jobs: {e}")

def save_jobs():
    """Save jobs to persistent storage."""
    try:
        with open(JOBS_FILE, 'w') as f:
            json.dump({
                'jobs': jobs,
                'counter': job_counter
            }, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save jobs: {e}")

# Load jobs on startup
load_jobs()


def create_app():
    """Create and configure Flask app."""
    return app


def _sanitize_prompt_filename(name: str, fallback: str) -> str:
    """Convert a prompt name into a filesystem-friendly slug."""
    if not name:
        return fallback
    slug = re.sub(r'[^a-zA-Z0-9-_]+', '-', name.strip().lower())
    slug = re.sub(r'-{2,}', '-', slug).strip('-_')
    return slug or fallback


def build_prompt_workspace(prompt_payload):
    """
    Create a temporary directory containing virtual prompt files.

    Returns:
        tuple(Path, dict): (workspace_path, metadata)
    """
    if not isinstance(prompt_payload, list) or not prompt_payload:
        raise ValueError('Prompt payload must be a non-empty list.')

    workspace = Path(tempfile.mkdtemp(prefix='prompt_session_'))
    total_chars = 0
    created_files = 0

    try:
        for index, entry in enumerate(prompt_payload, start=1):
            if not isinstance(entry, dict):
                continue
            text = str(entry.get('text', '') or '')
            if not text.strip():
                continue
            total_chars += len(text)
            name = entry.get('name') or f'Prompt {index}'
            slug = _sanitize_prompt_filename(name, f'prompt_{index}')
            file_path = workspace / f"{slug}.txt"
            file_path.write_text(text, encoding='utf-8')
            created_files += 1

        if created_files == 0:
            raise ValueError('Prompt payload contained no usable text.')

        metadata = {
            'prompt_count': created_files,
            'total_characters': total_chars,
        }
        return workspace, metadata
    except Exception:
        shutil.rmtree(workspace, ignore_errors=True)
        raise


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')


@app.route('/api/browse-directory', methods=['POST'])
def browse_directory():
    """Open native folder picker dialog and return selected path."""
    system = platform.system()
    
    # macOS: Use AppleScript for folder picker (works without tkinter)
    if system == 'Darwin':
        try:
            script = '''
            tell application "System Events"
                activate
                set folderPath to choose folder with prompt "Select Directory"
                return POSIX path of folderPath
            end tell
            '''
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )
            folder_path = result.stdout.strip()
            if folder_path:
                return jsonify({'path': folder_path})
            else:
                return jsonify({'error': 'No directory selected'}), 400
        except subprocess.CalledProcessError:
            # User cancelled or error occurred
            return jsonify({'error': 'No directory selected'}), 400
        except FileNotFoundError:
            # osascript not available (shouldn't happen on macOS)
            pass
    
    # Try tkinter for Windows and Linux
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        # Create a root window and hide it
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.attributes('-topmost', True)  # Bring to front
        
        # Open folder dialog
        folder_path = filedialog.askdirectory(title="Select Directory")
        root.destroy()
        
        if folder_path:
            return jsonify({'path': folder_path})
        else:
            return jsonify({'error': 'No directory selected'}), 400
            
    except ImportError:
        # Fallback: return error suggesting manual input
        return jsonify({
            'error': 'Directory picker not available. Please enter path manually.',
            'suggestion': 'Install tkinter: sudo apt-get install python3-tk (Linux) or enter path directly'
        }), 501
    except Exception as tk_error:
        # Handle headless mode errors (Linux without DISPLAY)
        error_msg = str(tk_error)
        if 'DISPLAY' in error_msg or 'display' in error_msg.lower():
            return jsonify({
                'error': 'Directory picker unavailable in headless mode',
                'suggestion': 'Please enter the directory path manually'
            }), 503
        return jsonify({
            'error': f'Failed to open directory picker: {str(tk_error)}',
            'suggestion': 'Please enter the directory path manually'
        }), 500


@app.route('/api/open-folder', methods=['POST'])
def open_folder():
    """Open a folder in the system file manager."""
    data = request.json
    folder_path = data.get('path')
    
    if not folder_path:
        return jsonify({'error': 'Path is required'}), 400
    
    try:
        folder_path = Path(folder_path).expanduser().resolve()
        
        if not folder_path.exists():
            return jsonify({'error': f'Folder does not exist: {folder_path}'}), 404
        
        if not folder_path.is_dir():
            return jsonify({'error': f'Path is not a directory: {folder_path}'}), 400
        
        # Open folder based on OS
        system = platform.system()
        try:
            if system == 'Windows':
                os.startfile(str(folder_path))
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', str(folder_path)], check=True)
            else:  # Linux
                # Check for DISPLAY on Linux
                if os.environ.get('DISPLAY') is None:
                    return jsonify({
                        'error': 'Folder opening unavailable in headless mode',
                        'suggestion': 'Use file manager or CLI to access output directory'
                    }), 503
                subprocess.run(['xdg-open', str(folder_path)], check=True)
            
            return jsonify({'success': True, 'path': str(folder_path)})
        except subprocess.CalledProcessError as e:
            return jsonify({'error': f'Failed to open folder: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Failed to open folder: {str(e)}'}), 500


@app.route('/api/estimate', methods=['POST'])
def estimate():
    """Get token estimation for a directory or prompt payload."""
    data = request.json
    source_dir = data.get('source_dir')
    prompt_payload = data.get('prompt_payload')
    exclusions_text = data.get('exclusions', '')
    
    # Handle prompt payload estimation
    if prompt_payload:
        if not isinstance(prompt_payload, list) or not prompt_payload:
            return jsonify({'error': 'Prompt payload must be a non-empty list'}), 400
        
        try:
            # Build temporary workspace for estimation
            workspace, _ = build_prompt_workspace(prompt_payload)
            cleanup_paths = [workspace]
            
            try:
                # Discover files (the virtual prompt files)
                discovery = FileDiscovery(str(workspace), exclusions=set())
                files = discovery.discover()
                
                # Estimate tokens
                token_service = TokenEstimationService()
                pre_estimation = token_service.estimate_pre_compression(files)
                post_estimation = token_service.estimate_post_compression(pre_estimation['total_tokens'])
                recommendation = token_service.get_recommendation(pre_estimation['total_tokens'])
                
                # Calculate DeepSeek insights
                insights_service = DeepSeekInsightsService()
                insights = insights_service.calculate_insights(len(files), pre_estimation['total_tokens'])
                
                return jsonify({
                    'pre_compression': pre_estimation,
                    'post_compression': post_estimation,
                    'recommendation': recommendation,
                    'deepseek_insights': insights,
                    'summary': insights_service.get_summary(insights),
                    'technical_details': insights_service.get_technical_details(insights)
                })
            finally:
                # Cleanup temporary workspace
                for path in cleanup_paths:
                    if Path(path).exists():
                        shutil.rmtree(path, ignore_errors=True)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Handle directory estimation (existing code)
    if not source_dir:
        return jsonify({'error': 'Source directory or prompt payload is required'}), 400
    
    # Strip quotes and whitespace
    source_dir = source_dir.strip().strip("'\"")
    
    # Parse exclusions
    exclusions = set()
    if exclusions_text:
        for line in exclusions_text.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):  # Ignore empty lines and comments
                exclusions.add(line)
    
    # Resolve path and check existence
    try:
        source_path = Path(source_dir).expanduser().resolve()
        if not source_path.exists():
            return jsonify({
                'error': f'Directory does not exist: {source_path}',
                'provided': source_dir
            }), 400
        if not source_path.is_dir():
            return jsonify({
                'error': f'Path is not a directory: {source_path}',
                'provided': source_dir
            }), 400
        source_dir = str(source_path)
    except Exception as e:
        return jsonify({
            'error': f'Invalid path: {str(e)}',
            'provided': source_dir
        }), 400
    
    try:
        # Discover files with exclusions
        discovery = FileDiscovery(source_dir, exclusions=exclusions)
        files = discovery.discover()
        
        # Estimate tokens
        token_service = TokenEstimationService()
        pre_estimation = token_service.estimate_pre_compression(files)
        post_estimation = token_service.estimate_post_compression(pre_estimation['total_tokens'])
        recommendation = token_service.get_recommendation(pre_estimation['total_tokens'])
        
        # Calculate DeepSeek insights
        insights_service = DeepSeekInsightsService()
        insights = insights_service.calculate_insights(len(files), pre_estimation['total_tokens'])
        
        return jsonify({
            'pre_compression': pre_estimation,
            'post_compression': post_estimation,
            'recommendation': recommendation,
            'deepseek_insights': insights,
            'summary': insights_service.get_summary(insights),
            'technical_details': insights_service.get_technical_details(insights)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compress', methods=['POST'])
def compress():
    """Start compression job."""
    global job_counter
    
    data = request.json
    source_dir = data.get('source_dir')
    prompt_payload = data.get('prompt_payload')
    output_dir = data.get('output_dir') or None  # Explicitly handle None
    parallel = data.get('parallel', False)
    workers = data.get('workers', None)
    if workers:
        try:
            workers = int(workers)  # Convert to int if provided
        except (ValueError, TypeError):
            workers = None
    resume = data.get('resume', False)
    ocr_enabled = data.get('ocr_enabled', False)
    ocr_mode = data.get('ocr_mode', 'small')
    hybrid_mode = data.get('hybrid_mode', False)  # HYBRID_MODE_START
    exclusions_text = data.get('exclusions', '')
    smart_concatenation = data.get('smart_concatenation', False)
    max_pdfs = data.get('max_pdfs', 10)
    max_pages_per_pdf = data.get('max_pages_per_pdf', 100)
    max_size_per_pdf_mb = data.get('max_size_per_pdf_mb', 10)
    max_total_pages = data.get('max_total_pages', 1000)

    cleanup_paths = []
    prompt_metadata = None
    is_prompt_mode = bool(prompt_payload)
    
    if is_prompt_mode and source_dir:
        return jsonify({'error': 'Choose either a source directory or the prompt collector, not both.'}), 400
    if not source_dir and not is_prompt_mode:
        return jsonify({'error': 'Source directory is required'}), 400

    if output_dir:
        output_dir = output_dir.strip().strip("'\"")

    if is_prompt_mode:
        try:
            workspace, prompt_metadata = build_prompt_workspace(prompt_payload)
        except ValueError as exc:
            return jsonify({'error': str(exc)}), 400
        source_dir = str(workspace)
        exclusions = set()
        resume = False  # Resume does not apply to ephemeral prompt sessions
        cleanup_paths.append(source_dir)
        source_label = 'Prompt Collector'
        if not output_dir:
            default_root = Path.home() / 'prompt_collector_exports'
            default_root.mkdir(parents=True, exist_ok=True)
            output_dir = str(default_root / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    else:
        # Strip quotes and whitespace
        source_dir = source_dir.strip().strip("'\"")
        
        # Parse exclusions
        exclusions = set()
        if exclusions_text:
            for line in exclusions_text.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):  # Ignore empty lines and comments
                    exclusions.add(line)
        
        # Resolve path and check existence
        try:
            source_path = Path(source_dir).expanduser().resolve()
            if not source_path.exists():
                return jsonify({
                    'error': f'Directory does not exist: {source_path}',
                    'provided': source_dir
                }), 400
            if not source_path.is_dir():
                return jsonify({
                    'error': f'Path is not a directory: {source_path}',
                    'provided': source_dir
                }), 400
            source_dir = str(source_path)
            source_label = source_dir
        except Exception as e:
            return jsonify({
                'error': f'Invalid path: {str(e)}',
                'provided': source_dir
            }), 400
        
        # Set default output directory if not provided
        if not output_dir:
            output_dir = f"{source_dir}_ocr_ready"
    
    # Calculate estimates before starting
    estimates = None
    try:
        discovery = FileDiscovery(source_dir, exclusions=exclusions)
        files = discovery.discover()
        
        token_service = TokenEstimationService()
        pre_estimation = token_service.estimate_pre_compression(files)
        post_estimation = token_service.estimate_post_compression(pre_estimation['total_tokens'])
        recommendation = token_service.get_recommendation(pre_estimation['total_tokens'])
        
        insights_service = DeepSeekInsightsService()
        insights = insights_service.calculate_insights(len(files), pre_estimation['total_tokens'])
        
        estimates = {
            'pre_compression': pre_estimation,
            'post_compression': post_estimation,
            'recommendation': recommendation,
            'deepseek_insights': insights
        }
    except Exception as e:
        print(f"Warning: Could not calculate estimates: {e}")
    
    # Create job
    job_counter += 1
    job_id = f"job_{job_counter}_{int(datetime.now().timestamp())}"
    
    # Sanitize paths for storage: use basename only to avoid exposing full directory structure
    def sanitize_path_for_storage(path_str: str) -> str:
        """Return basename of path to avoid exposing full directory structure."""
        if not path_str:
            return path_str
        return Path(path_str).name
    
    job = {
        'id': job_id,
        'status': 'queued',
        'source_dir': sanitize_path_for_storage(source_label),  # Sanitized: basename only
        'mode': 'prompt' if is_prompt_mode else 'code',
        'output_dir': sanitize_path_for_storage(output_dir) if output_dir else sanitize_path_for_storage(f"{source_dir}_ocr_ready"),  # Sanitized: basename only
        'created_at': datetime.now().isoformat(),
        'progress': 0,
        'message': 'Job queued',
        'results': None,
        'estimates': estimates,  # Include estimates in job
    }
    if prompt_metadata:
        job['prompt_metadata'] = prompt_metadata
    jobs[job_id] = job
    save_jobs()  # Save to persistent storage
    
    # Start compression in background thread
    thread = threading.Thread(
        target=run_compression_job,
        args=(job_id, source_dir, output_dir, parallel, workers, resume, ocr_enabled, ocr_mode, hybrid_mode, exclusions, smart_concatenation, max_pdfs, max_pages_per_pdf, max_size_per_pdf_mb, max_total_pages),  # HYBRID_MODE_START
        kwargs={'cleanup_paths': cleanup_paths or None},
        daemon=True
    )
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'status': 'queued',
        'estimates': estimates  # Include estimates in response
    })


def run_compression_job(job_id, source_dir, output_dir, parallel, workers, resume, ocr_enabled, ocr_mode, hybrid_mode=False, exclusions=None, smart_concatenation=False, max_pdfs=10, max_pages_per_pdf=100, max_size_per_pdf_mb=10, max_total_pages=1000, cleanup_paths=None):  # HYBRID_MODE_START
    """Run compression job in background."""
    try:
        jobs[job_id]['status'] = 'running'
        jobs[job_id]['message'] = 'Discovering files...'
        jobs[job_id]['progress'] = 10
        save_jobs()
        
        # Ensure output_dir is a string, not None
        if not output_dir:
            output_dir = f"{source_dir}_ocr_ready"
        
        # HYBRID_MODE_START
        # Pass hybrid_mode to pipeline for preprocessing
        if hybrid_mode:
            print(f"[HYBRID] Hybrid mode enabled - preprocessing code for OCR fidelity")
        pipeline = CompressionPipeline(
            source_dir=str(source_dir),
            output_dir=str(output_dir),
            exclusions=exclusions or set(),
            parallel=parallel,
            max_workers=workers,
            resume=resume,
            hybrid_mode=hybrid_mode,  # Enable hybrid preprocessing
        )
        # HYBRID_MODE_END
        
        if smart_concatenation:
            jobs[job_id]['message'] = 'Grouping files and converting to PDFs...'
            jobs[job_id]['progress'] = 30
            save_jobs()
            results = pipeline.run_smart_concatenation(
                max_pdfs=max_pdfs,
                max_pages_per_pdf=max_pages_per_pdf,
                max_size_per_pdf_mb=max_size_per_pdf_mb,
                max_total_pages=max_total_pages,
                verbose=False
            )
        else:
            jobs[job_id]['message'] = 'Converting files to PDFs...'
            jobs[job_id]['progress'] = 30
            save_jobs()
            results = pipeline.run(verbose=False)
        
        # Apply OCR compression if enabled
        if ocr_enabled:
            jobs[job_id]['message'] = 'Applying OCR compression...'
            jobs[job_id]['progress'] = 70
            save_jobs()
            ocr_compressor = create_ocr_compressor(mode=ocr_mode, cache_dir=output_dir)
            if ocr_compressor:
                # Find all PDFs and compress them
                pdf_dir = Path(output_dir)
                pdf_files = list(pdf_dir.rglob('*.pdf'))
                ocr_results = ocr_compressor.compress_pdfs_batch(pdf_files)
                results['ocr'] = {
                    'enabled': True,
                    'mode': ocr_mode,
                    'files_compressed': len(ocr_results),
                    'stats': ocr_compressor.get_stats(),
                }
            else:
                results['ocr'] = {
                    'enabled': False,
                    'error': 'OCR dependencies not available',
                }
        
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['message'] = 'Compression complete'
        jobs[job_id]['progress'] = 100
        jobs[job_id]['results'] = results
        save_jobs()
        
    except Exception as e:
        jobs[job_id]['status'] = 'failed'
        jobs[job_id]['message'] = f'Error: {str(e)}'
        jobs[job_id]['error'] = str(e)
        save_jobs()
    finally:
        if cleanup_paths:
            for path in cleanup_paths:
                try:
                    shutil.rmtree(path, ignore_errors=True)
                except Exception as cleanup_error:
                    print(f"Warning: Could not clean prompt workspace {path}: {cleanup_error}")


@app.route('/api/job/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status."""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id].copy()
    # Remove large data from response
    if 'results' in job and job['results']:
        results = job['results'].copy()
        if 'discovery' in results:
            results['discovery'] = {'total_files': results['discovery'].get('statistics', {}).get('total_files', 0)}
        job['results'] = results
    
    return jsonify(job)


@app.route('/api/job/<job_id>/failures', methods=['GET'])
def get_job_failures(job_id):
    """Return the failure report for a job, if available."""
    job = jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    results = job.get('results') or {}
    report_path = results.get('failure_report')
    if not report_path:
        return jsonify({'error': 'No failure report available'}), 404
    
    report_file = Path(report_path)
    if not report_file.exists():
        return jsonify({'error': 'Failure report not found on disk'}), 404
    
    try:
        data = json.loads(report_file.read_text())
        return jsonify(data)
    except Exception as exc:
        return jsonify({'error': f'Unable to read failure report: {exc}'}), 500


@app.route('/api/job/<job_id>/insights', methods=['GET'])
def get_job_insights(job_id):
    """Get DeepSeek insights for a job."""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    # If estimates already exist, return them
    if job.get('estimates'):
        insights_service = DeepSeekInsightsService()
        insights = job['estimates']['deepseek_insights']
        return jsonify({
            'summary': insights_service.get_summary(insights),
            'technical_details': insights_service.get_technical_details(insights),
            'full_insights': insights
        })
    
    return jsonify({'error': 'Insights not available for this job'}), 404


@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all jobs."""
    job_list = []
    for job_id, job in jobs.items():
        job_data = {
            'id': job_id,
            'status': job['status'],
            'created_at': job['created_at'],
            'progress': job.get('progress', 0),
            'message': job.get('message', ''),
            'source_dir': job.get('source_dir', ''),
            'output_dir': job.get('output_dir', ''),
            'mode': job.get('mode', 'code'),
        }
        # Include estimates if available
        if 'estimates' in job:
            job_data['estimates'] = job['estimates']
        job_list.append(job_data)
    
    # Sort by created_at descending (newest first)
    job_list.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({'jobs': job_list})


@app.route('/api/download/<job_id>', methods=['GET'])
def download_results(job_id):
    """Download compression results as ZIP."""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    if job['status'] != 'completed':
        return jsonify({'error': 'Job not completed'}), 400
    
    output_dir = Path(job['output_dir'])
    if not output_dir.exists():
        return jsonify({'error': 'Output directory not found'}), 404
    
    # Create temporary ZIP file
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    temp_zip_path = temp_zip.name
    temp_zip.close()
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in output_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(output_dir)
                    zipf.write(file_path, arcname)
        
        return send_file(
            temp_zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'compression_results_{job_id}.zip'
        )
    except Exception as e:
        return jsonify({'error': f'Failed to create ZIP: {str(e)}'}), 500


@app.route('/api/ocr/modes', methods=['GET'])
def get_ocr_modes():
    """Get available OCR compression modes."""
    modes = OCRCompressor.get_available_modes()
    deps = OCRCompressor.check_dependencies()
    
    return jsonify({
        'modes': modes,
        'dependencies_available': deps,
        'ocr_available': deps.get('deepseek_ocr_model', False),
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

