"""Tests for Flask web application helper logic."""

import json
import shutil
import subprocess

import pytest

from src.web import app as web_app


@pytest.fixture
def client(monkeypatch, tmp_path):
    """Provide Flask test client with isolated job storage."""
    jobs_file = tmp_path / 'jobs_test.json'
    monkeypatch.setattr(web_app, 'JOBS_FILE', jobs_file)
    web_app.jobs.clear()
    web_app.job_counter = 0
    web_app.app.config['TESTING'] = True
    return web_app.app.test_client()


def test_sanitize_prompt_filename():
    """Slugify prompt names."""
    result = web_app._sanitize_prompt_filename('Hello World!@', 'fallback')
    assert result == 'hello-world'
    assert web_app._sanitize_prompt_filename('', 'fallback') == 'fallback'


def test_build_prompt_workspace_success():
    """Workspace should contain prompt files and metadata."""
    payload = [
        {'name': 'First Prompt', 'text': 'console.log("first");'},
        {'name': 'Second', 'text': 'console.log("second");'}
    ]
    workspace, metadata = web_app.build_prompt_workspace(payload)
    try:
        assert workspace.exists()
        assert metadata['prompt_count'] == 2
        assert metadata['total_characters'] > 0
        files = list(workspace.glob('*.txt'))
        assert len(files) == 2
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_build_prompt_workspace_invalid_payload():
    """Invalid prompt payloads should raise ValueError."""
    with pytest.raises(ValueError):
        web_app.build_prompt_workspace([])
    with pytest.raises(ValueError):
        web_app.build_prompt_workspace([{'name': 'Empty'}])


def test_estimate_prompt_payload_endpoint(client):
    """Prompt payload estimation should return token estimates."""
    payload = [{'name': 'Snippet', 'text': 'console.log("payload");'}]
    response = client.post('/api/estimate', json={'prompt_payload': payload})
    assert response.status_code == 200
    data = response.get_json()
    assert 'pre_compression' in data
    assert 'deepseek_insights' in data


def test_estimate_directory_endpoint(client, tmp_path):
    """Directory estimation should succeed for real files."""
    project = tmp_path / 'project'
    project.mkdir()
    (project / 'main.ts').write_text('console.log("estimate");')

    response = client.post('/api/estimate', json={'source_dir': str(project)})
    assert response.status_code == 200
    data = response.get_json()
    assert data['pre_compression']['file_count'] == 1


def test_compress_prompt_job(client, monkeypatch, tmp_path):
    """Compression endpoint should enqueue and complete prompt jobs."""

    class DummyPipeline:
        def __init__(self, *args, **kwargs):
            pass

        def run(self, verbose=False):
            return {
                'success': True,
                'metrics': {
                    'original': {'total_files': 1},
                    'pdf': {'total_files': 1, 'compression_ratio': 2.0},
                    'gemini_compatibility': {'fits_pdf': True}
                },
                'discovery': {'statistics': {'total_files': 1}},
                'conversion': {
                    'total_size_original': 100,
                    'total_size_pdf': 50,
                    'compression_ratio': 2.0
                },
                'summary': {
                    'files_discovered': 1,
                    'files_converted': 1,
                    'files_failed': 0,
                    'files_already_processed': 0,
                    'total_size_original_bytes': 100,
                    'total_size_pdf_bytes': 50,
                    'compression_ratio': 2.0
                },
                'failed_files': []
            }

        def run_smart_concatenation(self, **kwargs):
            return self.run()

    class ImmediateThread:
        def __init__(self, target, args=(), kwargs=None, daemon=None):
            self._target = target
            self._args = args
            self._kwargs = kwargs or {}

        def start(self):
            self._target(*self._args, **self._kwargs)

    monkeypatch.setattr(web_app, 'CompressionPipeline', DummyPipeline)
    monkeypatch.setattr(web_app, 'create_ocr_compressor', lambda *args, **kwargs: None)
    monkeypatch.setattr(web_app.threading, 'Thread', ImmediateThread)

    payload = [{'name': 'Prompt', 'text': 'print("hi")'}]
    response = client.post('/api/compress', json={'prompt_payload': payload})
    assert response.status_code == 200
    job_info = response.get_json()
    job_id = job_info['job_id']

    status_resp = client.get(f'/api/job/{job_id}')
    assert status_resp.status_code == 200
    status_data = status_resp.get_json()
    assert status_data['status'] == 'completed'
    assert status_data['results']['summary']['files_converted'] == 1


def test_compress_directory_job_with_smart_concat(client, monkeypatch, tmp_path):
    """Directory-based job with smart concatenation."""
    source_dir = tmp_path / 'codebase'
    source_dir.mkdir()
    (source_dir / 'main.ts').write_text('console.log("dir");')

    class DummyPipeline:
        def __init__(self, *args, **kwargs):
            pass

        def run(self, verbose=False):
            return {
                'success': True,
                'metrics': {
                    'original': {'total_files': 1},
                    'pdf': {'total_files': 1, 'compression_ratio': 2.0},
                    'gemini_compatibility': {'fits_pdf': True}
                },
                'discovery': {'statistics': {'total_files': 1}},
                'conversion': {
                    'total_size_original': 100,
                    'total_size_pdf': 50,
                    'compression_ratio': 2.0
                },
                'summary': {
                    'files_discovered': 1,
                    'files_converted': 1,
                    'files_failed': 0,
                    'files_already_processed': 0,
                    'total_size_original_bytes': 100,
                    'total_size_pdf_bytes': 50,
                    'compression_ratio': 2.0
                },
                'failed_files': []
            }

        def run_smart_concatenation(self, **kwargs):
            return self.run()

    class ImmediateThread:
        def __init__(self, target, args=(), kwargs=None, daemon=None):
            self._target = target
            self._args = args
            self._kwargs = kwargs or {}

        def start(self):
            self._target(*self._args, **self._kwargs)

    monkeypatch.setattr(web_app, 'CompressionPipeline', DummyPipeline)
    monkeypatch.setattr(web_app, 'create_ocr_compressor', lambda *args, **kwargs: None)
    monkeypatch.setattr(web_app.threading, 'Thread', ImmediateThread)

    output_dir = tmp_path / 'output_dir'
    response = client.post('/api/compress', json={
        'source_dir': str(source_dir),
        'output_dir': str(output_dir),
        'smart_concatenation': True
    })
    assert response.status_code == 200
    job_id = response.get_json()['job_id']
    status_resp = client.get(f'/api/job/{job_id}')
    assert status_resp.status_code == 200


def test_estimate_prompt_payload_validation(client):
    """Invalid prompt payload should return 400."""
    response = client.post('/api/estimate', json={'prompt_payload': []})
    assert response.status_code == 400
    response = client.post('/api/estimate', json={'prompt_payload': [{'name': 'Empty', 'text': ''}]})
    assert response.status_code >= 400  # No usable text triggers error handling


def test_compress_request_validation(client, tmp_path):
    """Compression endpoint should validate input combinations."""
    payload = [{'name': 'Prompt', 'text': 'text'}]
    # Both source_dir and prompt payload provided
    resp = client.post('/api/compress', json={'source_dir': str(tmp_path), 'prompt_payload': payload})
    assert resp.status_code == 400
    # Missing both
    resp = client.post('/api/compress', json={})
    assert resp.status_code == 400


def test_job_insights_and_listing(client, tmp_path):
    """Job listing and insights routes should respond correctly."""
    insights_service = web_app.DeepSeekInsightsService()
    sample_insights = insights_service.calculate_insights(1, 1000)
    job_id = 'job_test_insights'
    web_app.jobs[job_id] = {
        'status': 'completed',
        'created_at': '2025-01-01T00:00:00',
        'progress': 100,
        'message': 'Done',
        'source_dir': 'test',
        'output_dir': str(tmp_path),
        'mode': 'code',
        'estimates': {
            'deepseek_insights': sample_insights,
            'pre_compression': {'total_tokens': 1000},
            'post_compression': {'estimated_tokens': 100},
            'recommendation': {'recommended': True}
        }
    }

    resp = client.get(f'/api/job/{job_id}/insights')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'summary' in data

    resp = client.get('/api/jobs')
    assert resp.status_code == 200
    assert len(resp.get_json()['jobs']) >= 1


def test_download_results_endpoint(client, monkeypatch, tmp_path):
    """Download endpoint should create a ZIP of the output directory."""
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    (output_dir / 'file.txt').write_text('content')

    job_id = 'job_download'
    web_app.jobs[job_id] = {
        'status': 'completed',
        'created_at': '2025-01-01T00:00:00',
        'progress': 100,
        'message': 'Done',
        'source_dir': str(output_dir),
        'output_dir': str(output_dir),
        'mode': 'code',
    }

    temp_zip_path = tmp_path / 'temp.zip'

    class FakeTmp:
        def __init__(self):
            self.name = str(temp_zip_path)

        def close(self):
            pass

    monkeypatch.setattr(web_app.tempfile, 'NamedTemporaryFile', lambda delete=False, suffix='': FakeTmp())

    resp = client.get(f'/api/download/{job_id}')
    assert resp.status_code == 200
    assert temp_zip_path.exists()
    temp_zip_path.unlink()  # cleanup


def test_ocr_modes_endpoint(client):
    """OCR modes endpoint should return modes and dependency info."""
    resp = client.get('/api/ocr/modes')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'modes' in data
    assert 'dependencies_available' in data


def test_job_failure_report_endpoint(client, tmp_path):
    """Expose failure report contents via API."""
    report_path = tmp_path / 'failure.json'
    payload = {'failures': [{'file': 'a.ts', 'error': 'boom'}], 'conversion_errors': []}
    report_path.write_text(json.dumps(payload))
    
    job_id = 'job_failure_api'
    web_app.jobs[job_id] = {
        'id': job_id,
        'status': 'completed',
        'created_at': 'now',
        'progress': 100,
        'message': 'done',
        'results': {'failure_report': str(report_path)}
    }
    
    response = client.get(f'/api/job/{job_id}/failures')
    assert response.status_code == 200
    assert response.get_json()['failures'][0]['file'] == 'a.ts'
    web_app.jobs.pop(job_id, None)


def test_job_failure_report_missing(client):
    """Missing reports should return 404."""
    job_id = 'job_no_report'
    web_app.jobs[job_id] = {
        'id': job_id,
        'status': 'completed',
        'created_at': 'now',
        'progress': 100,
        'message': 'done',
        'results': {}
    }
    response = client.get(f'/api/job/{job_id}/failures')
    assert response.status_code == 404
    web_app.jobs.pop(job_id, None)


def test_open_folder_invalid_path(client):
    """Open-folder route should validate paths."""
    response = client.post('/api/open-folder', json={'path': '/nonexistent/path'})
    assert response.status_code == 404


def test_browse_directory_cancellation(client, monkeypatch):
    """Simulate macOS directory picker cancellation."""
    monkeypatch.setattr(web_app.platform, 'system', lambda: 'Darwin')
    def raise_called(*args, **kwargs):
        raise subprocess.CalledProcessError(1, 'osascript')
    monkeypatch.setattr(web_app.subprocess, 'run', raise_called)
    
    response = client.post('/api/browse-directory')
    assert response.status_code == 400

