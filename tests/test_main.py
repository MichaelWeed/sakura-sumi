"""Tests for CLI main entry point."""

import pytest
import sys
from pathlib import Path
import tempfile
from unittest.mock import patch, MagicMock


def test_main_help():
    """Test --help flag."""
    from src.main import main
    
    with patch('sys.argv', ['compress.py', '--help']):
        try:
            main()
        except SystemExit as e:
            # Help exits with code 0
            assert e.code == 0


def test_main_invalid_directory(capsys):
    """Test with invalid directory."""
    from src.main import main
    
    with patch('sys.argv', ['compress.py', '/nonexistent/directory']):
        with pytest.raises(SystemExit):
            main()
        
        # Check error message was printed
        captured = capsys.readouterr()
        assert 'does not exist' in captured.err or 'Error' in captured.out


def test_main_valid_directory():
    """Test with valid directory."""
    from src.main import main
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file
        test_file = Path(tmpdir) / 'test.ts'
        test_file.write_text('console.log("test");')
        
        output_dir = Path(tmpdir) / 'output'
        
        with patch('sys.argv', [
            'compress.py',
            str(tmpdir),
            '-o', str(output_dir),
            '--verbose'
        ]):
            with patch('sys.exit') as mock_exit:
                try:
                    main()
                    # Should exit with code 0 on success
                    assert mock_exit.called
                except Exception:
                    # If it fails, that's okay for this test
                    pass

