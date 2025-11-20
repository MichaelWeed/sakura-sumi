"""File discovery and inventory system for codebase compression."""

import os
import fnmatch
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileInfo:
    """Metadata about a discovered file."""
    path: str
    relative_path: str
    size: int
    file_type: str
    category: str  # 'source', 'config', 'documentation', etc.
    encoding: str = 'utf-8'


class FileDiscovery:
    """Discovers and categorizes files in a codebase."""
    
    # Supported file extensions
    SOURCE_EXTENSIONS = {
        '.ts', '.tsx', '.js', '.jsx',  # TypeScript/JavaScript
        '.py', '.pyx',  # Python
        '.java', '.kt',  # Java/Kotlin
        '.go', '.rs', '.cpp', '.c', '.h', '.hpp',  # Systems languages
        '.rb', '.php', '.swift', '.dart',  # Other languages
    }
    
    CONFIG_EXTENSIONS = {
        '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
        '.xml', '.properties', '.env', '.config',
    }
    
    STYLE_EXTENSIONS = {
        '.css', '.scss', '.sass', '.less', '.styl',
    }
    
    MARKUP_EXTENSIONS = {
        '.html', '.htm', '.xhtml', '.md', '.markdown', '.txt',
    }
    
    DOCUMENT_EXTENSIONS = {
        '.docx',  # Microsoft Word documents (text extraction supported)
    }
    
    ALL_EXTENSIONS = SOURCE_EXTENSIONS | CONFIG_EXTENSIONS | STYLE_EXTENSIONS | MARKUP_EXTENSIONS | DOCUMENT_EXTENSIONS
    
    # Default exclusion patterns
    DEFAULT_EXCLUSIONS = {
        'node_modules',
        'dist',
        'build',
        'out',
        '.git',
        '.svn',
        '.hg',
        '__pycache__',
        '.pytest_cache',
        '.mypy_cache',
        '.venv',
        'venv',
        'env',
        '.env',
        '.idea',
        '.vscode',
        '.vs',
        'android',  # Android build files (for Love Oracle AI)
        'latest',  # Build artifacts
        '.gradle',
        'gradle',
        'bin',
        'obj',
        '.next',
        '.nuxt',
        'coverage',
        '.nyc_output',
        '*.log',
        '*.tmp',
        '*.swp',
        '*.swo',
        '.DS_Store',
    }
    
    def __init__(self, source_dir: str, exclusions: Set[str] = None):
        """
        Initialize file discovery.
        
        Args:
            source_dir: Root directory to scan
            exclusions: Additional exclusion patterns (merged with defaults)
        """
        # Clean up path: strip quotes and whitespace, expand user home
        source_dir = str(source_dir).strip().strip("'\"")
        self.source_dir = Path(source_dir).expanduser().resolve()
        if not self.source_dir.exists():
            raise ValueError(f"Source directory does not exist: {self.source_dir}")
        
        self.exclusions = self.DEFAULT_EXCLUSIONS.copy()
        if exclusions:
            self.exclusions.update(exclusions)
        
        self.discovered_files: List[FileInfo] = []
        self.stats: Dict[str, int] = {
            'total_files': 0,
            'by_type': {},
            'by_category': {},
            'total_size': 0,
        }
    
    def _should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded."""
        # Get relative path string for pattern matching
        try:
            relative_path = path.relative_to(self.source_dir)
            relative_str = str(relative_path)
            path_str = str(path)
        except ValueError:
            # Path is outside source_dir, use absolute path
            relative_str = str(path)
            path_str = str(path)
        
        # Check each exclusion pattern
        for exclusion in self.exclusions:
            # Handle wildcard patterns (e.g., *.log, node_modules/*)
            if '*' in exclusion or '?' in exclusion:
                # Match against relative path and filename
                if fnmatch.fnmatch(relative_str, exclusion) or fnmatch.fnmatch(path.name, exclusion):
                    return True
                # Also check each path component
                for part in path.parts:
                    if fnmatch.fnmatch(part, exclusion):
                        return True
            else:
                # Exact match or directory name match
                if exclusion in path.parts:
                    return True
                # Check if path contains exclusion as substring (for directory patterns like "node_modules/")
                if exclusion.rstrip('/') in relative_str or exclusion.rstrip('/') in path_str:
                    # Make sure it's a directory match, not partial string match
                    exclusion_clean = exclusion.rstrip('/')
                    parts = relative_str.split(os.sep)
                    if exclusion_clean in parts:
                        return True
        
        # Check file extensions (exclude non-text files)
        if path.suffix and path.suffix.lower() not in self.ALL_EXTENSIONS:
            return True
        
        return False
    
    def _categorize_file(self, path: Path) -> str:
        """Categorize a file based on its extension and location."""
        ext = path.suffix.lower()
        
        if ext in self.SOURCE_EXTENSIONS:
            return 'source'
        elif ext in self.CONFIG_EXTENSIONS:
            return 'config'
        elif ext in self.STYLE_EXTENSIONS:
            return 'style'
        elif ext in self.MARKUP_EXTENSIONS:
            if path.name.lower() in ('readme.md', 'readme.txt', 'license', 'changelog'):
                return 'documentation'
            return 'markup'
        elif ext in self.DOCUMENT_EXTENSIONS:
            return 'documentation'
        else:
            return 'other'
    
    def _get_file_type(self, path: Path) -> str:
        """Get file type from extension."""
        ext = path.suffix.lower()
        if ext:
            return ext[1:]  # Remove leading dot
        return 'no-extension'
    
    def _detect_encoding(self, path: Path) -> str:
        """Detect file encoding (simplified - defaults to utf-8)."""
        # In production, could use chardet or similar
        # For now, default to utf-8 and handle errors during reading
        return 'utf-8'
    
    def discover(self) -> List[FileInfo]:
        """
        Discover all relevant files in the source directory.
        
        Returns:
            List of FileInfo objects
        """
        self.discovered_files = []
        self.stats = {
            'total_files': 0,
            'by_type': {},
            'by_category': {},
            'total_size': 0,
            'unsupported_files': {},  # Track unsupported file types
            'total_scanned': 0,  # Total files encountered (including unsupported)
        }
        
        for root, dirs, files in os.walk(self.source_dir):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not self._should_exclude(Path(root) / d)]
            
            for file in files:
                file_path = Path(root) / file
                self.stats['total_scanned'] += 1
                
                # Track unsupported extensions BEFORE checking exclusions
                # (so we can report what file types were found, even if excluded)
                file_ext = file_path.suffix.lower()
                
                # Skip excluded files
                if self._should_exclude(file_path):
                    # Still track unsupported extensions even if excluded
                    if file_ext and file_ext not in self.ALL_EXTENSIONS:
                        if file_ext not in self.stats['unsupported_files']:
                            self.stats['unsupported_files'][file_ext] = 0
                        self.stats['unsupported_files'][file_ext] += 1
                    continue
                
                # Track unsupported extensions (not excluded, but not supported either)
                if file_ext and file_ext not in self.ALL_EXTENSIONS:
                    if file_ext not in self.stats['unsupported_files']:
                        self.stats['unsupported_files'][file_ext] = 0
                    self.stats['unsupported_files'][file_ext] += 1
                    continue
                
                try:
                    # Get file size
                    size = file_path.stat().st_size
                    
                    # Skip empty files
                    if size == 0:
                        continue
                    
                    # Create FileInfo
                    relative_path = file_path.relative_to(self.source_dir)
                    file_info = FileInfo(
                        path=str(file_path),
                        relative_path=str(relative_path),
                        size=size,
                        file_type=self._get_file_type(file_path),
                        category=self._categorize_file(file_path),
                        encoding=self._detect_encoding(file_path),
                    )
                    
                    self.discovered_files.append(file_info)
                    
                    # Update statistics
                    self.stats['total_files'] += 1
                    self.stats['total_size'] += size
                    
                    file_type = file_info.file_type
                    category = file_info.category
                    
                    self.stats['by_type'][file_type] = self.stats['by_type'].get(file_type, 0) + 1
                    self.stats['by_category'][category] = self.stats['by_category'].get(category, 0) + 1
                
                except (OSError, PermissionError) as e:
                    # Skip files we can't access
                    print(f"Warning: Could not access {file_path}: {e}")
                    continue
        
        return self.discovered_files
    
    def generate_inventory_report(self) -> Dict:
        """
        Generate a comprehensive inventory report.
        
        Returns:
            Dictionary with inventory statistics and file list
        """
        # Sanitize path: use basename only to avoid exposing full directory structure
        source_basename = self.source_dir.name if self.source_dir.name else Path(self.source_dir).name
        return {
            'source_directory': source_basename,  # Sanitized: basename only
            'scan_date': datetime.now().isoformat(),
            'statistics': self.stats.copy(),
            'files': [
                {
                    'path': f.relative_path,
                    'size': f.size,
                    'type': f.file_type,
                    'category': f.category,
                }
                for f in self.discovered_files
            ],
            'breakdown_by_type': {
                k: v for k, v in sorted(
                    self.stats['by_type'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            },
            'breakdown_by_category': {
                k: v for k, v in sorted(
                    self.stats['by_category'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            },
        }
    
    def print_summary(self):
        """Print a human-readable summary of discovered files."""
        print(f"\n{'='*60}")
        print(f"File Discovery Summary")
        print(f"{'='*60}")
        print(f"Source Directory: {self.source_dir}")
        print(f"Total Files Scanned: {self.stats.get('total_scanned', 0)}")
        print(f"Total Files Found: {self.stats['total_files']}")
        print(f"Total Size: {self._format_size(self.stats['total_size'])}")
        
        # Show unsupported files if any
        unsupported = self.stats.get('unsupported_files', {})
        if unsupported:
            print(f"\n⚠️  Unsupported File Types Found:")
            for ext, count in sorted(unsupported.items(), key=lambda x: x[1], reverse=True):
                ext_display = ext if ext else '(no extension)'
                print(f"  {ext_display:15s}: {count:4d} file(s)")
            print(f"\n💡 Tip: Sakura Sumi only processes text-based source code files.")
            print(f"   See https://github.com/MichaelWeed/sakura-sumi#file-type-support for supported types.")
        
        if self.stats['by_category']:
            print(f"\nBreakdown by Category:")
            for category, count in sorted(
                self.stats['by_category'].items(),
                key=lambda x: x[1],
                reverse=True
            ):
                print(f"  {category:15s}: {count:4d} files")
        
        if self.stats['by_type']:
            print(f"\nBreakdown by Type:")
            for file_type, count in sorted(
                self.stats['by_type'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]:  # Top 10
                print(f"  .{file_type:10s}: {count:4d} files")
        print(f"{'='*60}\n")
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes into human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

