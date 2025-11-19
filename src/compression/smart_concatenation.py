"""Smart concatenation engine with prioritized roll-up strategy."""

from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass

from ..utils.file_discovery import FileInfo


@dataclass
class PDFGroup:
    """Represents a group of files to be concatenated into one PDF."""
    name: str  # e.g., "src_components.pdf"
    files: List[FileInfo]
    directory_path: str  # e.g., "src/components"
    priority: int  # Higher = more important


class SmartConcatenationEngine:
    """Implements smart concatenation with prioritized roll-up strategy.
    
    Ensures exactly 10 PDFs maximum, including root files in the count.
    """
    
    # Key project folders that get priority
    KEY_FOLDERS = {
        'src', 'components', 'api', 'services', 'utils', 'lib', 
        'public', 'tests', 'test', 'specs', 'config', 'scripts'
    }
    
    def __init__(
        self,
        source_dir: Path,
        max_pdfs: int = 10,
        max_pages_per_pdf: int = 100,
        max_size_per_pdf_mb: int = 10,
        max_total_pages: int = 10,
    ):
        self.source_dir = source_dir
        self.max_pdfs = max_pdfs
        self.max_pages_per_pdf = max_pages_per_pdf
        self.max_size_per_pdf_bytes = max_size_per_pdf_mb * 1024 * 1024
        self.max_total_pages = max_total_pages
    
    def build_directory_tree(self, files: List[FileInfo]) -> Tuple[Dict[str, List[FileInfo]], List[FileInfo]]:
        """
        Build directory tree: {dir_path: [FileInfo, ...]}
        Only includes directories that contain files.
        Returns (dir_tree, root_files).
        """
        tree = defaultdict(list)
        root_files = []
        
        for file_info in files:
            # Get directory path (parent of file)
            file_path = Path(file_info.relative_path)
            if len(file_path.parts) > 1:
                # File is in a subdirectory
                dir_path = str(file_path.parent)
                tree[dir_path].append(file_info)
            else:
                # File is at root
                root_files.append(file_info)
        
        return dict(tree), root_files
    
    def identify_key_folders(self, dir_tree: Dict[str, List[FileInfo]]) -> Set[str]:
        """Identify top-level key folders from the directory tree."""
        key_folders = set()
        
        for dir_path in dir_tree.keys():
            if not dir_path:  # Skip root (handled separately)
                continue
            
            # Get first component (top-level folder)
            parts = dir_path.split('/')
            if parts and parts[0] in self.KEY_FOLDERS:
                key_folders.add(parts[0])
        
        return key_folders
    
    def calculate_directory_priority(self, dir_path: str, file_count: int, total_size: int) -> int:
        """
        Calculate priority for a directory.
        Higher priority = more important (should be kept separate).
        """
        priority = 0
        
        # Key folders get high priority
        parts = dir_path.split('/') if dir_path else []
        if parts and parts[0] in self.KEY_FOLDERS:
            priority += 1000
        
        # Deeper directories get higher priority (we want to preserve granularity)
        priority += len(parts) * 10
        
        # More files = higher priority
        priority += min(file_count, 100)  # Cap at 100
        
        # Larger total size = higher priority
        priority += min(total_size // 1024, 500)  # Cap at 500
        
        return priority
    
    def roll_up_directories(
        self, 
        dir_tree: Dict[str, List[FileInfo]]
    ) -> Dict[str, List[FileInfo]]:
        """
        Roll up child directories into parents when count > max_pdfs.
        Traverses from deepest to shallowest.
        """
        if len(dir_tree) <= self.max_pdfs:
            return dir_tree
        
        # Build depth map: {depth: [dir_paths]}
        depth_map = defaultdict(list)
        for dir_path in dir_tree.keys():
            depth = len(dir_path.split('/')) if dir_path else 0
            depth_map[depth].append(dir_path)
        
        # Start from deepest directories
        max_depth = max(depth_map.keys()) if depth_map else 0
        merged_tree = dir_tree.copy()
        
        # Traverse from deepest to shallowest
        for depth in range(max_depth, 0, -1):
            if len(merged_tree) <= self.max_pdfs:
                break
            
            dirs_at_depth = sorted(depth_map[depth])
            
            for dir_path in dirs_at_depth:
                if len(merged_tree) <= self.max_pdfs:
                    break
                
                if dir_path not in merged_tree:
                    continue
                
                # Find parent directory
                parts = dir_path.split('/')
                if len(parts) > 1:
                    parent_path = '/'.join(parts[:-1])
                    
                    # Merge this directory into parent
                    if parent_path in merged_tree:
                        merged_tree[parent_path].extend(merged_tree[dir_path])
                        del merged_tree[dir_path]
        
        return merged_tree
    
    def group_files(
        self, 
        files: List[FileInfo]
    ) -> List[PDFGroup]:
        """
        Main grouping logic implementing prioritized roll-up strategy.
        Returns list of PDFGroups. Ensures exactly max_pdfs (default 10) total.
        """
        # Step 1: Build directory tree and separate root files
        dir_tree, root_files = self.build_directory_tree(files)
        
        # Step 2: Identify key folders
        key_folders = self.identify_key_folders(dir_tree)
        
        # Step 3: Start with all directories separate (most granular approach)
        # Only roll up if we exceed max_pdfs
        groups = []
        
        # If we have <= max_pdfs directories, keep them all separate
        if len(dir_tree) <= self.max_pdfs:
            # Simple case: keep all directories as separate PDFs
            for dir_path, dir_files in dir_tree.items():
                pdf_name = self._sanitize_pdf_name(dir_path) if dir_path else "misc.pdf"
                total_size = sum(f.size for f in dir_files)
                groups.append(PDFGroup(
                    name=f"{pdf_name}.pdf",
                    files=dir_files,
                    directory_path=dir_path,
                    priority=self.calculate_directory_priority(dir_path, len(dir_files), total_size)
                ))
        else:
            # We have > max_pdfs directories - need to group/roll-up
            # Strategy: Prioritize key folders, roll up their subdirectories if needed
            
            # First, separate key folders from others
            key_folder_groups = {}
            other_dirs = {}
            
            for dir_path, dir_files in dir_tree.items():
                parts = dir_path.split('/')
                top_level = parts[0] if parts else ""
                
                if top_level in key_folders:
                    if top_level not in key_folder_groups:
                        key_folder_groups[top_level] = {}
                    key_folder_groups[top_level][dir_path] = dir_files
                else:
                    other_dirs[dir_path] = dir_files
            
            # Process key folders: try to keep subdirectories separate if possible
            for folder_name, subdirs in key_folder_groups.items():
                # Calculate how many slots we have left (accounting for root files)
                slots_for_key_folders = self.max_pdfs - len(other_dirs) - 1  # -1 for potential root/misc
                
                if len(subdirs) <= slots_for_key_folders:
                    # We have room - keep subdirectories separate
                    for dir_path, dir_files in subdirs.items():
                        total_size = sum(f.size for f in dir_files)
                        pdf_name = self._sanitize_pdf_name(dir_path)
                        groups.append(PDFGroup(
                            name=f"{pdf_name}.pdf",
                            files=dir_files,
                            directory_path=dir_path,
                            priority=self.calculate_directory_priority(dir_path, len(dir_files), total_size)
                        ))
                else:
                    # Too many subdirectories - roll up into single PDF
                    all_files = []
                    for dir_files in subdirs.values():
                        all_files.extend(dir_files)
                    total_size = sum(f.size for f in all_files)
                    groups.append(PDFGroup(
                        name=f"{folder_name}.pdf",
                        files=all_files,
                        directory_path=folder_name,
                        priority=self.calculate_directory_priority(folder_name, len(all_files), total_size)
                    ))
            
            # Handle other directories - apply roll-up if still needed
            if len(groups) + len(other_dirs) > self.max_pdfs:
                other_dirs = self.roll_up_directories(other_dirs)
            
            # Add other directories as groups
            for dir_path, dir_files in other_dirs.items():
                pdf_name = self._sanitize_pdf_name(dir_path) if dir_path else "misc.pdf"
                total_size = sum(f.size for f in dir_files)
                groups.append(PDFGroup(
                    name=f"{pdf_name}.pdf",
                    files=dir_files,
                    directory_path=dir_path,
                    priority=self.calculate_directory_priority(dir_path, len(dir_files), total_size)
                ))
        
        # Step 5: Handle root files - CRITICAL: Must be included in the 10-PDF limit
        # Count how many slots we have left
        slots_remaining = self.max_pdfs - len(groups)
        
        if root_files:
            if slots_remaining > 0:
                # We have room for root_config.pdf
                groups.append(PDFGroup(
                    name="root_config.pdf",
                    files=root_files,
                    directory_path="",
                    priority=50  # Medium priority
                ))
            else:
                # No room left - merge root files into misc bucket
                # Find or create misc group
                misc_group = None
                for group in groups:
                    if group.name == "misc.pdf":
                        misc_group = group
                        break
                
                if misc_group:
                    # Add root files to existing misc group
                    misc_group.files.extend(root_files)
                else:
                    # Need to create misc group, but we're at limit
                    # Merge lowest priority group into misc
                    if groups:
                        groups = sorted(groups, key=lambda g: g.priority, reverse=True)
                        misc_files = groups[-1].files.copy()
                        misc_files.extend(root_files)
                        groups[-1] = PDFGroup(
                            name="misc.pdf",
                            files=misc_files,
                            directory_path="misc",
                            priority=0
                        )
        
        # Step 7: Apply misc bucket if still over limit (shouldn't happen, but safety check)
        if len(groups) > self.max_pdfs:
            groups = self._apply_misc_bucket(groups)
        
        # Final validation: ensure we have exactly max_pdfs or fewer
        if len(groups) > self.max_pdfs:
            # Emergency fallback: take top N-1, merge rest into misc
            groups = sorted(groups, key=lambda g: g.priority, reverse=True)
            top_groups = groups[:self.max_pdfs - 1]
            misc_files = []
            for group in groups[self.max_pdfs - 1:]:
                misc_files.extend(group.files)
            
            if misc_files:
                top_groups.append(PDFGroup(
                    name="misc.pdf",
                    files=misc_files,
                    directory_path="misc",
                    priority=0
                ))
            groups = top_groups
        
        return groups
    
    def _apply_misc_bucket(self, groups: List[PDFGroup]) -> List[PDFGroup]:
        """
        Fallback: Select top (max_pdfs - 1) groups, merge rest into misc.pdf
        This ensures exactly max_pdfs total.
        """
        # Sort by priority (highest first)
        sorted_groups = sorted(groups, key=lambda g: g.priority, reverse=True)
        
        # Take top (max_pdfs - 1) to leave room for misc
        top_groups = sorted_groups[:self.max_pdfs - 1]
        
        # Collect all files from remaining groups
        misc_files = []
        for group in sorted_groups[self.max_pdfs - 1:]:
            misc_files.extend(group.files)
        
        # Create misc group (this makes exactly max_pdfs total)
        if misc_files:
            top_groups.append(PDFGroup(
                name="misc.pdf",
                files=misc_files,
                directory_path="misc",
                priority=0
            ))
        
        return top_groups
    
    def _sanitize_pdf_name(self, dir_path: str) -> str:
        """Convert directory path to PDF filename."""
        # Replace / with _
        name = dir_path.replace('/', '_')
        # Remove leading/trailing underscores
        name = name.strip('_')
        # Replace multiple underscores with single
        while '__' in name:
            name = name.replace('__', '_')
        return name or "misc"

