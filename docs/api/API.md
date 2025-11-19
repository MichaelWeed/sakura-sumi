# API Documentation

Python API for programmatic use of 🌸 Sakura Sumi - OCR Compression System.

## CompressionPipeline

Main pipeline orchestrator with support for standard and smart concatenation modes.

### Standard Mode

```python
from src.compression.pipeline import CompressionPipeline

pipeline = CompressionPipeline(
    source_dir="/path/to/codebase",
    output_dir="/path/to/output",
    parallel=True,
    max_workers=4,
    resume=False,
    retry_count=3,
)

results = pipeline.run(verbose=True)
```

### Smart Concatenation Mode

```python
from src.compression.pipeline import CompressionPipeline

pipeline = CompressionPipeline(
    source_dir="/path/to/codebase",
    output_dir="/path/to/output",
    exclusions={"node_modules", ".git"},
)

results = pipeline.run_smart_concatenation(
    max_pdfs=10,                    # Hard limit: max 10 PDFs
    max_pages_per_pdf=100,          # Max pages per PDF
    max_size_per_pdf_mb=10,          # Max size per PDF (MB)
    max_total_pages=1000,           # Max total pages across all PDFs
    verbose=True
)
```

**Smart Concatenation Features:**
- Intelligently groups files into maximum 10 PDFs
- Prioritizes key project folders (src, components, api, etc.)
- Rolls up subdirectories when needed
- Handles root files separately
- Ensures all files are included

See `docs/developer/SMART_CONCATENATION.md` for detailed documentation.

### Parameters

- `source_dir` (str): Source codebase directory
- `output_dir` (str): Output directory for PDFs
- `exclusions` (set, optional): Additional exclusion patterns
- `parallel` (bool): Enable parallel processing
- `max_workers` (int, optional): Number of workers
- `batch_size` (int): Batch size for sequential processing
- `resume` (bool): Resume from checkpoint
- `retry_count` (int): Retry attempts for failed files

### Returns

Dictionary with:
- `success` (bool): Whether pipeline succeeded
- `metrics` (dict): Compression metrics
- `summary` (dict): Summary statistics
- `failed_files` (list): List of failed files

## FileDiscovery

File discovery and inventory system.

```python
from src.utils.file_discovery import FileDiscovery

discovery = FileDiscovery(
    source_dir="/path/to/codebase",
    exclusions={"test", "spec"}
)

files = discovery.discover()
report = discovery.generate_inventory_report()
```

## PDFConverter

PDF conversion engine with support for single-file and multi-file concatenation.

### Single File Conversion

```python
from src.compression.pdf_converter import PDFConverter
from src.utils.file_discovery import FileInfo

converter = PDFConverter(output_dir="/path/to/output")

file_info = FileInfo(
    path="/path/to/file.ts",
    relative_path="file.ts",
    size=1024,
    file_type="ts",
    category="source"
)

pdf_path = converter.convert_file(file_info)
```

### Multi-File Concatenation (Smart Concatenation)

```python
from src.compression.pdf_converter import PDFConverter
from src.utils.file_discovery import FileInfo

converter = PDFConverter(output_dir="/path/to/output")

# List of files to concatenate into single PDF
files = [FileInfo(...), FileInfo(...), ...]

pdf_path = converter.concatenate_files_to_pdf(
    files=files,
    pdf_name="src_components",
    max_pages=100,
    max_size_bytes=10 * 1024 * 1024  # 10 MB
)
```

**Important:** The converter automatically escapes XML/HTML special characters (`<`, `>`, `&`) for reportlab compatibility. This prevents parse errors when processing code files containing these characters.

## CompressionMetrics

Metrics calculation and reporting.

```python
from src.utils.metrics import CompressionMetrics, create_visualizations

metrics_calc = CompressionMetrics()

metrics = metrics_calc.calculate_metrics(
    original_files=[...],
    pdf_files=[...],
    ocr_stats=None
)

# Generate report
report = metrics_calc.generate_report(
    metrics,
    output_path=Path("report.md"),
    format="markdown"
)

# Create visualizations
charts = create_visualizations(metrics, Path("charts"))
```

## OCRCompressor

Optional OCR compression.

```python
from src.compression.ocr_compression import OCRCompressor, create_ocr_compressor

# Check availability
compressor = create_ocr_compressor(mode="small")
if compressor:
    compressed_path = compressor.compress_pdf(pdf_path)
```

