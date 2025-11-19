# Troubleshooting Guide

Common issues and solutions.

## Installation Issues

### Virtual Environment Not Activating

**Problem**: `source venv/bin/activate` fails

**Solutions**:
- Use full path: `source /full/path/to/venv/bin/activate`
- Check Python version: `python3 --version` (need 3.8+)
- Recreate venv: `rm -rf venv && python3 -m venv venv`

### Dependencies Not Installing

**Problem**: `pip install` fails

**Solutions**:
- Upgrade pip: `pip install --upgrade pip`
- Use Python 3 explicitly: `python3 -m pip install`
- Check internet connection
- Try individual packages: `pip install reportlab`

## Runtime Issues

### No Files Discovered

**Problem**: Pipeline reports "No files found"

**Solutions**:
- Verify source directory path is correct
- Check file permissions
- Ensure source files exist
- Review exclusion patterns (may be too aggressive)

### PDF Generation Fails

**Problem**: Some files fail to convert

**Solutions**:
- Check file encoding (should be UTF-8)
- Verify file is not binary
- Check disk space
- Review error messages in verbose output
- Use retry: `--retry 5`

### Memory Errors

**Problem**: Out of memory or system slowdown

**Solutions**:
- Reduce workers: `--workers 2`
- Disable parallel: Remove `--parallel`
- Process smaller batches
- Close other applications
- Increase system RAM

### Slow Performance

**Problem**: Compression takes too long

**Solutions**:
- Enable parallel: `--parallel --workers 4`
- Exclude unnecessary files: `--exclude "test"`
- Use resume for large codebases
- Check disk I/O performance
- Use SSD instead of HDD

## OCR Compression Issues

### OCR Not Available

**Problem**: OCR compression fails or unavailable

**Solutions**:
- Install dependencies: `pip install vllm transformers`
- Check GPU availability (may be required)
- Use PDF compression instead
- Verify model download completed

### OCR Slow

**Problem**: OCR compression very slow

**Solutions**:
- This is expected - OCR is computationally intensive
- Use GPU if available
- Consider using PDF compression instead
- Process in smaller batches

## Web Portal Issues

### Portal Won't Start

**Problem**: `python run_web.py` fails

**Solutions**:
- Check Flask installed: `pip install flask`
- Verify port 5000 not in use
- Check firewall settings
- Try different port: Edit `run_web.py`

### Portal Not Accessible

**Problem**: Can't access http://localhost:5000

**Solutions**:
- Check firewall settings
- Verify server started successfully
- Try http://127.0.0.1:5000
- Check browser console for errors

## Metrics Issues

### Token Estimation Inaccurate

**Problem**: Token counts seem wrong

**Solutions**:
- Token estimation is approximate
- Visual tokens for PDFs are estimates
- Use as planning guide, not exact counts
- Check actual usage in Gemini

### Charts Not Generating

**Problem**: `--generate-charts` produces no output

**Solutions**:
- Install matplotlib: `pip install matplotlib`
- Check write permissions
- Verify output directory exists
- Check error messages

## Checkpoint Issues

### Resume Not Working

**Problem**: `--resume` doesn't skip files

**Solutions**:
- Verify checkpoint file exists: `.compression_checkpoint.json`
- Check checkpoint file is readable
- Ensure same output directory
- Check file paths match

### Checkpoint Corrupted

**Problem**: Checkpoint file causes errors

**Solutions**:
- Delete checkpoint: `rm .compression_checkpoint.json`
- Start fresh without resume
- Check JSON syntax in checkpoint file

## Platform-Specific Issues

### macOS

- May need to allow Python in Security settings
- Use `python3` explicitly
- Check PATH includes Python

### Linux

- May need `python3-dev` package
- Check permissions on directories
- Verify Python 3.8+ installed

### Windows

- Use `python` instead of `python3`
- Use backslashes in paths or raw strings
- Check antivirus not blocking Python

## Getting Help

1. Check verbose output: `-v` flag
2. Review error messages carefully
3. Check logs in output directory
4. Verify all dependencies installed
5. Test with small codebase first

## Known Limitations

- Binary files not supported
- Very large files (>100MB) may cause issues
- OCR compression requires GPU for best performance
- Token estimation is approximate
- Some special characters may not render perfectly in PDFs

