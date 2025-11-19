"""Dense PDF conversion engine for codebase compression."""

import os
import json
import html
from pathlib import Path
from typing import Optional, Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT
import yaml

from ..utils.file_discovery import FileInfo
from .hybrid_preprocessor import preprocess_code, prepend_dict  # HYBRID_MODE_START


class PDFConverter:
    """Converts source code files to dense, OCR-optimized PDFs."""
    
    # Dense layout settings for maximum information density
    FONT_SIZE = 8  # Small font for density
    LINE_HEIGHT = FONT_SIZE * 1.2
    MARGIN = 0.3 * inch  # Minimal margins
    MAX_LINE_LENGTH = 110  # Characters per line (truncate longer lines)
    
    def __init__(self, output_dir: str, hybrid_mode: bool = False):  # HYBRID_MODE_START
        """
        Initialize PDF converter.
        
        Args:
            output_dir: Directory to save PDF files
            hybrid_mode: Enable hybrid preprocessing for OCR-friendly transformation
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.hybrid_mode = hybrid_mode  # HYBRID_MODE_END
        self.translation_dict_global = {}  # Accumulate translations across all files
        
        self.conversion_stats = {
            'success': 0,
            'failed': 0,
            'total_size_original': 0,
            'total_size_pdf': 0,
            'errors': [],
        }
    
    def convert_file(self, file_info: FileInfo) -> Optional[Path]:
        """
        Convert a single file to PDF.
        
        Args:
            file_info: FileInfo object with file metadata
            
        Returns:
            Path to generated PDF file, or None if conversion failed
        """
        try:
            # Read file content
            content = self._read_file(file_info)
            if content is None:
                return None
            
            # HYBRID_MODE_START
            # Apply hybrid preprocessing if enabled
            is_first_file = not self.translation_dict_global  # Track if this is the first file processed
            if self.hybrid_mode:
                processed_content, translation_dict = preprocess_code(content, mode='hybrid')
                # Accumulate translations for global dictionary
                self.translation_dict_global.update(translation_dict)
                content = processed_content
                # Prepend translation dict to first file only
                if is_first_file and self.translation_dict_global:
                    content = prepend_dict(content, self.translation_dict_global)
                    print(f"[HYBRID] Prepended translation dict to {file_info.relative_path} ({len(self.translation_dict_global)} mappings)")
                elif translation_dict:
                    print(f"[HYBRID] Processed {file_info.relative_path}: {len(translation_dict)} symbol replacements")
            # HYBRID_MODE_END
            
            # Format content based on file type
            formatted_content = self._format_content(content, file_info.file_type)
            
            # Generate PDF
            pdf_path = self._generate_pdf(file_info, formatted_content)
            
            if pdf_path and pdf_path.exists():
                # Update statistics
                self.conversion_stats['success'] += 1
                self.conversion_stats['total_size_original'] += file_info.size
                self.conversion_stats['total_size_pdf'] += pdf_path.stat().st_size
                return pdf_path
            else:
                self.conversion_stats['failed'] += 1
                self.conversion_stats['errors'].append({
                    'file': file_info.relative_path,
                    'error': 'PDF generation failed'
                })
                return None
        
        except Exception as e:
            self.conversion_stats['failed'] += 1
            self.conversion_stats['errors'].append({
                'file': file_info.relative_path,
                'error': str(e)
            })
            return None
    
    def _read_file(self, file_info: FileInfo) -> Optional[str]:
        """Read file content with proper encoding handling."""
        try:
            with open(file_info.path, 'r', encoding=file_info.encoding, errors='replace') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try other common encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_info.path, 'r', encoding=encoding, errors='replace') as f:
                        return f.read()
                except (UnicodeDecodeError, LookupError):
                    continue
            
            # If all else fails, skip the file
            self.conversion_stats['errors'].append({
                'file': file_info.relative_path,
                'error': 'Could not decode file encoding'
            })
            return None
        except Exception as e:
            self.conversion_stats['errors'].append({
                'file': file_info.relative_path,
                'error': f'File read error: {str(e)}'
            })
            return None
    
    def _format_content(self, content: str, file_type: str) -> str:
        """Format content based on file type."""
        if file_type in ('json', 'yaml', 'yml'):
            return self._format_structured_data(content, file_type)
        else:
            return content
    
    def _format_structured_data(self, content: str, file_type: str) -> str:
        """Format JSON/YAML with proper indentation."""
        try:
            if file_type == 'json':
                data = json.loads(content)
                return json.dumps(data, indent=2, ensure_ascii=False)
            elif file_type in ('yaml', 'yml'):
                data = yaml.safe_load(content)
                return yaml.dump(data, indent=2, default_flow_style=False, allow_unicode=True)
        except Exception:
            # If parsing fails, return original content
            return content
        
        return content
    
    def _generate_pdf(self, file_info: FileInfo, content: str) -> Optional[Path]:
        """Generate PDF file with dense layout."""
        # Create output filename (preserve relative path structure)
        relative_path = Path(file_info.relative_path)
        pdf_filename = relative_path.with_suffix('.pdf')
        pdf_path = self.output_dir / pdf_filename
        
        # Create parent directories if needed
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Use SimpleDocTemplate for better control
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                leftMargin=self.MARGIN,
                rightMargin=self.MARGIN,
                topMargin=self.MARGIN,
                bottomMargin=self.MARGIN,
            )
            
            # Build PDF content
            story = []
            
            # Add file header
            styles = getSampleStyleSheet()
            header_style = styles['Heading2']
            header_style.fontSize = 10
            header_style.leading = 12
            
            story.append(Paragraph(f"<b>File:</b> {file_info.relative_path}", header_style))
            story.append(Paragraph(f"<b>Type:</b> {file_info.file_type} | <b>Size:</b> {file_info.size} bytes", styles['Normal']))
            story.append(Spacer(1, 6))
            
            # Add content as preformatted text (preserves formatting)
            # Use Code style with monospace font
            code_style = styles['Code']
            code_style.fontSize = self.FONT_SIZE
            code_style.leading = self.LINE_HEIGHT
            code_style.fontName = 'Courier'
            
            lines = content.split('\n')
            for line in lines:
                # Truncate very long lines
                if len(line) > self.MAX_LINE_LENGTH:
                    line = line[:self.MAX_LINE_LENGTH] + '...'
                
                # Escape XML/HTML special characters for reportlab Paragraph parser
                # reportlab uses XML-like markup, so we must escape <, >, and &
                # First preserve any existing HTML entities by replacing them with placeholders
                line = line.replace('&nbsp;', '__NBSP__').replace('&lt;', '__LT__').replace('&gt;', '__GT__').replace('&amp;', '__AMP__')
                # Now escape all remaining &, <, > characters
                escaped_line = html.escape(line)
                # Restore preserved entities
                escaped_line = escaped_line.replace('__NBSP__', '&nbsp;').replace('__LT__', '&lt;').replace('__GT__', '&gt;').replace('__AMP__', '&amp;')
                # Replace spaces with non-breaking spaces for better formatting
                escaped_line = escaped_line.replace(' ', '&nbsp;')
                
                # Use Paragraph with Code style to preserve formatting
                story.append(Paragraph(escaped_line, code_style))
            
            # Build PDF
            doc.build(story)
            
            return pdf_path
        
        except Exception as e:
            # Fallback to simpler canvas-based approach if SimpleDocTemplate fails
            try:
                return self._generate_pdf_simple(file_info, content, pdf_path)
            except Exception as e2:
                self.conversion_stats['errors'].append({
                    'file': file_info.relative_path,
                    'error': f'PDF generation error: {str(e2)}'
                })
                return None
    
    def _generate_pdf_simple(self, file_info: FileInfo, content: str, pdf_path: Path) -> Path:
        """Fallback simple PDF generation using canvas."""
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.setFont("Courier", self.FONT_SIZE)
        
        # Add header
        y_pos = 750
        c.drawString(self.MARGIN, y_pos, f"File: {file_info.relative_path}")
        y_pos -= self.LINE_HEIGHT * 1.5
        c.drawString(self.MARGIN, y_pos, f"Type: {file_info.file_type} | Size: {file_info.size} bytes")
        y_pos -= self.LINE_HEIGHT * 2
        
        # Add content
        lines = content.split('\n')
        for line in lines:
            if y_pos < 50:
                c.showPage()
                c.setFont("Courier", self.FONT_SIZE)
                y_pos = 750
            
            # Truncate long lines
            if len(line) > self.MAX_LINE_LENGTH:
                line = line[:self.MAX_LINE_LENGTH] + '...'
            
            c.drawString(self.MARGIN, y_pos, line)
            y_pos -= self.LINE_HEIGHT
        
        c.save()
        return pdf_path
    
    def concatenate_files_to_pdf(
        self, 
        files: List[FileInfo], 
        pdf_name: str,
        max_pages: Optional[int] = None,
        max_size_bytes: Optional[int] = None,
    ) -> Optional[Path]:
        """
        Concatenate multiple files into a single PDF.
        
        Args:
            files: List of FileInfo objects to concatenate
            pdf_name: Output PDF filename (without .pdf extension)
            max_pages: Optional maximum pages per PDF
            max_size_bytes: Optional maximum size per PDF
            
        Returns:
            Path to generated PDF, or None if failed
        """
        pdf_path = self.output_dir / f"{pdf_name}.pdf"
        
        try:
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                leftMargin=self.MARGIN,
                rightMargin=self.MARGIN,
                topMargin=self.MARGIN,
                bottomMargin=self.MARGIN,
            )
            
            story = []
            styles = getSampleStyleSheet()
            header_style = styles['Heading2']
            header_style.fontSize = 10
            header_style.leading = 12
            
            code_style = styles['Code']
            code_style.fontSize = self.FONT_SIZE
            code_style.leading = self.LINE_HEIGHT
            code_style.fontName = 'Courier'
            
            # Sort files alphabetically for consistency
            sorted_files = sorted(files, key=lambda f: f.relative_path)
            
            total_size_original = 0
            files_included = 0
            files_skipped_size_limit = 0
            is_first_file = True  # HYBRID_MODE_START - track first file for dict prepending
            
            for file_info in sorted_files:
                # Check size limit - only enforce if we've already included at least one file
                # This ensures every PDF group gets at least one file
                if max_size_bytes and files_included > 0:
                    if (total_size_original + file_info.size) > max_size_bytes:
                        files_skipped_size_limit += 1
                        continue  # Skip this file, try next one
                
                # Read file content
                content = self._read_file(file_info)
                if content is None:
                    continue
                
                # HYBRID_MODE_START
                # Apply hybrid preprocessing if enabled
                if self.hybrid_mode:
                    processed_content, translation_dict = preprocess_code(content, mode='hybrid')
                    # Accumulate translations for global dictionary
                    self.translation_dict_global.update(translation_dict)
                    content = processed_content
                    # Prepend translation dict to first file only
                    if is_first_file and self.translation_dict_global:
                        content = prepend_dict(content, self.translation_dict_global)
                        is_first_file = False
                        print(f"[HYBRID] Prepended translation dict to {file_info.relative_path} ({len(self.translation_dict_global)} mappings)")
                    elif translation_dict:
                        print(f"[HYBRID] Processed {file_info.relative_path}: {len(translation_dict)} symbol replacements")
                # HYBRID_MODE_END
                
                # Format content
                formatted_content = self._format_content(content, file_info.file_type)
                
                # Add file separator
                story.append(Spacer(1, 12))
                story.append(Paragraph(
                    f"<b>File:</b> {file_info.relative_path}", 
                    header_style
                ))
                story.append(Paragraph(
                    f"<b>Type:</b> {file_info.file_type} | <b>Size:</b> {file_info.size} bytes", 
                    styles['Normal']
                ))
                story.append(Spacer(1, 6))
                
                # Add file content
                lines = formatted_content.split('\n')
                for line in lines:
                    if len(line) > self.MAX_LINE_LENGTH:
                        line = line[:self.MAX_LINE_LENGTH] + '...'
                    
                    # Escape XML/HTML special characters for reportlab Paragraph parser
                    # reportlab uses XML-like markup, so we must escape <, >, and &
                    escaped_line = html.escape(line)
                    # Replace spaces with non-breaking spaces for better formatting
                    escaped_line = escaped_line.replace(' ', '&nbsp;')
                    
                    story.append(Paragraph(escaped_line, code_style))
                
                total_size_original += file_info.size
                files_included += 1
            
            # Build PDF
            doc.build(story)
            
            # Update stats
            if pdf_path.exists():
                pdf_size = pdf_path.stat().st_size
                self.conversion_stats['success'] += files_included
                self.conversion_stats['total_size_original'] += total_size_original
                self.conversion_stats['total_size_pdf'] += pdf_size
                
                # Log if files were skipped due to size limit
                if files_skipped_size_limit > 0:
                    self.conversion_stats['errors'].append({
                        'pdf': pdf_name,
                        'warning': f'{files_skipped_size_limit} files skipped due to size limit ({max_size_bytes / (1024*1024):.1f} MB)'
                    })
                
                return pdf_path
            
            return None
            
        except Exception as e:
            self.conversion_stats['failed'] += len(files)
            self.conversion_stats['errors'].append({
                'files': [f.relative_path for f in files],
                'error': str(e)
            })
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conversion statistics."""
        compression_ratio = 0.0
        if self.conversion_stats['total_size_original'] > 0:
            compression_ratio = (
                self.conversion_stats['total_size_pdf'] / 
                self.conversion_stats['total_size_original']
            )
        
        return {
            **self.conversion_stats,
            'compression_ratio': compression_ratio,
            'success_rate': (
                self.conversion_stats['success'] / 
                max(1, self.conversion_stats['success'] + self.conversion_stats['failed'])
            ) * 100,
        }

