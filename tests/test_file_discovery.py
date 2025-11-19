"""Tests for file discovery system."""

import pytest
import tempfile
from pathlib import Path
from src.utils.file_discovery import FileDiscovery, FileInfo


@pytest.fixture
def temp_codebase():
    """Create a temporary codebase for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        
        # Create test files (ensure parent directories exist)
        (base / 'src').mkdir(parents=True, exist_ok=True)
        (base / 'node_modules' / 'dep').mkdir(parents=True, exist_ok=True)
        (base / 'dist').mkdir(parents=True, exist_ok=True)
        
        (base / 'src' / 'main.ts').write_text('console.log("hello");')
        (base / 'src' / 'utils.ts').write_text('export function test() {}')
        (base / 'package.json').write_text('{"name": "test"}')
        (base / 'README.md').write_text('# Test Project')
        (base / 'node_modules' / 'dep' / 'index.js').write_text('module.exports = {}')
        (base / 'dist' / 'bundle.js').write_text('compiled code')
        
        yield base


def test_file_discovery_basic(temp_codebase):
    """Test basic file discovery."""
    discovery = FileDiscovery(str(temp_codebase))
    files = discovery.discover()
    
    assert len(files) > 0
    assert any(f.relative_path == 'src/main.ts' for f in files)
    assert any(f.relative_path == 'package.json' for f in files)
    assert any(f.relative_path == 'README.md' for f in files)


def test_file_discovery_exclusions(temp_codebase):
    """Test that exclusions work."""
    discovery = FileDiscovery(str(temp_codebase))
    files = discovery.discover()
    
    # Should not include node_modules or dist
    paths = [f.relative_path for f in files]
    assert not any('node_modules' in str(p) for p in paths)
    assert not any('dist' in str(p) for p in paths)


def test_file_discovery_categorization(temp_codebase):
    """Test file categorization."""
    discovery = FileDiscovery(str(temp_codebase))
    files = discovery.discover()
    
    categories = {f.category for f in files}
    assert 'source' in categories
    assert 'config' in categories
    # README.md is categorized as 'documentation', not 'markup'
    assert 'documentation' in categories or 'markup' in categories


def test_file_discovery_inventory(temp_codebase):
    """Test inventory report generation."""
    discovery = FileDiscovery(str(temp_codebase))
    files = discovery.discover()
    report = discovery.generate_inventory_report()
    
    assert 'statistics' in report
    assert 'files' in report
    assert report['statistics']['total_files'] > 0

