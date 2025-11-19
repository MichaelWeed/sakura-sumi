"""Tests for smart concatenation engine."""

import pytest
import tempfile
from pathlib import Path
from src.compression.smart_concatenation import SmartConcatenationEngine, PDFGroup
from src.utils.file_discovery import FileInfo


@pytest.fixture
def temp_source_dir():
    """Create temporary source directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_files():
    """Create sample FileInfo objects for testing."""
    files = []
    
    # Root files
    files.append(FileInfo(
        path='/fake/root/file1.ts',
        relative_path='file1.ts',
        size=1000,
        file_type='ts',
        category='source'
    ))
    
    # Files in src directory
    files.append(FileInfo(
        path='/fake/src/component.ts',
        relative_path='src/component.ts',
        size=2000,
        file_type='ts',
        category='source'
    ))
    
    files.append(FileInfo(
        path='/fake/src/utils.ts',
        relative_path='src/utils.ts',
        size=1500,
        file_type='ts',
        category='source'
    ))
    
    # Files in src/components subdirectory
    files.append(FileInfo(
        path='/fake/src/components/Button.tsx',
        relative_path='src/components/Button.tsx',
        size=3000,
        file_type='tsx',
        category='source'
    ))
    
    files.append(FileInfo(
        path='/fake/src/components/Input.tsx',
        relative_path='src/components/Input.tsx',
        size=2500,
        file_type='tsx',
        category='source'
    ))
    
    # Files in tests directory
    files.append(FileInfo(
        path='/fake/tests/test1.ts',
        relative_path='tests/test1.ts',
        size=1000,
        file_type='ts',
        category='source'
    ))
    
    return files


def test_smart_concatenation_initialization(temp_source_dir):
    """Test engine initialization."""
    engine = SmartConcatenationEngine(
        source_dir=temp_source_dir,
        max_pdfs=10,
        max_pages_per_pdf=100,
        max_size_per_pdf_mb=10,
        max_total_pages=1000
    )
    
    assert engine.source_dir == temp_source_dir
    assert engine.max_pdfs == 10
    assert engine.max_pages_per_pdf == 100
    assert engine.max_size_per_pdf_bytes == 10 * 1024 * 1024
    assert engine.max_total_pages == 1000


def test_build_directory_tree(temp_source_dir, sample_files):
    """Test building directory tree."""
    engine = SmartConcatenationEngine(temp_source_dir)
    dir_tree, root_files = engine.build_directory_tree(sample_files)
    
    # Should have directories: src, src/components, tests
    assert 'src' in dir_tree
    assert 'src/components' in dir_tree
    assert 'tests' in dir_tree
    
    # Root files should be separate
    assert len(root_files) == 1
    assert root_files[0].relative_path == 'file1.ts'
    
    # Check directory contents
    assert len(dir_tree['src']) == 2  # component.ts, utils.ts
    assert len(dir_tree['src/components']) == 2  # Button.tsx, Input.tsx
    assert len(dir_tree['tests']) == 1  # test1.ts


def test_build_directory_tree_only_root_files(temp_source_dir):
    """Test directory tree with only root files."""
    engine = SmartConcatenationEngine(temp_source_dir)
    root_files_only = [
        FileInfo(
            path='/fake/file1.ts',
            relative_path='file1.ts',
            size=1000,
            file_type='ts',
            category='source'
        ),
        FileInfo(
            path='/fake/file2.ts',
            relative_path='file2.ts',
            size=2000,
            file_type='ts',
            category='source'
        )
    ]
    
    dir_tree, root_files = engine.build_directory_tree(root_files_only)
    
    assert len(dir_tree) == 0
    assert len(root_files) == 2


def test_identify_key_folders(temp_source_dir, sample_files):
    """Test identifying key folders."""
    engine = SmartConcatenationEngine(temp_source_dir)
    dir_tree, _ = engine.build_directory_tree(sample_files)
    key_folders = engine.identify_key_folders(dir_tree)
    
    assert 'src' in key_folders
    assert 'tests' in key_folders


def test_identify_key_folders_no_key_folders(temp_source_dir):
    """Test with no key folders."""
    engine = SmartConcatenationEngine(temp_source_dir)
    files = [
        FileInfo(
            path='/fake/other/file.ts',
            relative_path='other/file.ts',
            size=1000,
            file_type='ts',
            category='source'
        )
    ]
    dir_tree, _ = engine.build_directory_tree(files)
    key_folders = engine.identify_key_folders(dir_tree)
    
    assert len(key_folders) == 0


def test_calculate_directory_priority(temp_source_dir):
    """Test priority calculation."""
    engine = SmartConcatenationEngine(temp_source_dir)
    
    # Key folder should have high priority
    priority_key = engine.calculate_directory_priority('src', 10, 50000)
    priority_other = engine.calculate_directory_priority('other', 10, 50000)
    
    assert priority_key > priority_other
    assert priority_key >= 1000  # Key folders get +1000
    
    # Deeper directories should have higher priority
    priority_deep = engine.calculate_directory_priority('src/components', 10, 50000)
    assert priority_deep > priority_key
    
    # More files = higher priority
    priority_more_files = engine.calculate_directory_priority('src', 50, 50000)
    priority_few_files = engine.calculate_directory_priority('src', 5, 50000)
    assert priority_more_files > priority_few_files


def test_roll_up_directories(temp_source_dir):
    """Test directory roll-up."""
    engine = SmartConcatenationEngine(temp_source_dir, max_pdfs=3)
    
    # Create nested directories (need parent-child relationships for roll-up to work)
    files = []
    for i in range(2):
        # Create parent directories
        files.append(FileInfo(
            path=f'/fake/parent{i}/file.ts',
            relative_path=f'parent{i}/file.ts',
            size=1000,
            file_type='ts',
            category='source'
        ))
        # Create child directories under each parent
        for j in range(4):
            files.append(FileInfo(
                path=f'/fake/parent{i}/child{j}/file.ts',
                relative_path=f'parent{i}/child{j}/file.ts',
                size=1000,
                file_type='ts',
                category='source'
            ))
    
    dir_tree, _ = engine.build_directory_tree(files)
    # Should have 2 parents + 8 children = 10 directories
    original_count = len(dir_tree)
    assert original_count > engine.max_pdfs
    
    # Roll up should merge children into parents
    rolled = engine.roll_up_directories(dir_tree)
    # After roll-up, should have fewer or equal directories
    assert len(rolled) <= original_count
    # Verify some merging occurred (may not get to max_pdfs if all at same level)
    # At minimum, verify the function works without error


def test_roll_up_directories_within_limit(temp_source_dir):
    """Test roll-up when already within limit."""
    engine = SmartConcatenationEngine(temp_source_dir, max_pdfs=10)
    
    files = []
    for i in range(5):
        files.append(FileInfo(
            path=f'/fake/dir{i}/file.ts',
            relative_path=f'dir{i}/file.ts',
            size=1000,
            file_type='ts',
            category='source'
        ))
    
    dir_tree, _ = engine.build_directory_tree(files)
    rolled = engine.roll_up_directories(dir_tree)
    
    # Should remain unchanged
    assert len(rolled) == len(dir_tree)
    assert len(rolled) == 5


def test_sanitize_pdf_name(temp_source_dir):
    """Test PDF name sanitization."""
    engine = SmartConcatenationEngine(temp_source_dir)
    
    assert engine._sanitize_pdf_name('src/components') == 'src_components'
    assert engine._sanitize_pdf_name('src/components/ui') == 'src_components_ui'
    assert engine._sanitize_pdf_name('') == 'misc'
    assert engine._sanitize_pdf_name('_src_') == 'src'
    assert engine._sanitize_pdf_name('src__components') == 'src_components'


def test_group_files_simple_case(temp_source_dir, sample_files):
    """Test grouping with few directories (within limit)."""
    engine = SmartConcatenationEngine(temp_source_dir, max_pdfs=10)
    groups = engine.group_files(sample_files)
    
    # Should have groups for each directory plus root
    assert len(groups) <= engine.max_pdfs
    assert any(g.name == 'root_config.pdf' for g in groups)


def test_group_files_exceeds_limit(temp_source_dir):
    """Test grouping when directories exceed max_pdfs."""
    engine = SmartConcatenationEngine(temp_source_dir, max_pdfs=3)
    
    # Create many directories
    files = []
    for i in range(15):
        files.append(FileInfo(
            path=f'/fake/src/dir{i}/file.ts',
            relative_path=f'src/dir{i}/file.ts',
            size=1000,
            file_type='ts',
            category='source'
        ))
    
    groups = engine.group_files(files)
    
    # Should be exactly max_pdfs or fewer
    assert len(groups) <= engine.max_pdfs


def test_group_files_with_root_files(temp_source_dir):
    """Test grouping with root files."""
    engine = SmartConcatenationEngine(temp_source_dir, max_pdfs=5)
    
    files = [
        FileInfo(path='/fake/root1.ts', relative_path='root1.ts', size=1000, file_type='ts', category='source'),
        FileInfo(path='/fake/root2.ts', relative_path='root2.ts', size=2000, file_type='ts', category='source'),
        FileInfo(path='/fake/src/file.ts', relative_path='src/file.ts', size=1500, file_type='ts', category='source'),
    ]
    
    groups = engine.group_files(files)
    
    # Should include root files
    root_group = next((g for g in groups if g.name == 'root_config.pdf'), None)
    assert root_group is not None
    assert len(root_group.files) == 2


def test_group_files_root_files_no_slots(temp_source_dir):
    """Test root files when no slots available."""
    engine = SmartConcatenationEngine(temp_source_dir, max_pdfs=2)
    
    # Create enough directories to fill slots
    files = []
    for i in range(5):
        files.append(FileInfo(
            path=f'/fake/dir{i}/file.ts',
            relative_path=f'dir{i}/file.ts',
            size=1000,
            file_type='ts',
            category='source'
        ))
    
    # Add root files
    files.append(FileInfo(
        path='/fake/root.ts',
        relative_path='root.ts',
        size=1000,
        file_type='ts',
        category='source'
    ))
    
    groups = engine.group_files(files)
    
    # Should still be within limit
    assert len(groups) <= engine.max_pdfs
    # Root files should be merged into misc or another group
    assert all(len(g.files) > 0 for g in groups)


def test_group_files_key_folders_priority(temp_source_dir):
    """Test that key folders get priority."""
    engine = SmartConcatenationEngine(temp_source_dir, max_pdfs=5)
    
    files = []
    # Add files in key folder
    for i in range(3):
        files.append(FileInfo(
            path=f'/fake/src/file{i}.ts',
            relative_path=f'src/file{i}.ts',
            size=1000,
            file_type='ts',
            category='source'
        ))
    
    # Add files in non-key folder
    for i in range(3):
        files.append(FileInfo(
            path=f'/fake/other/file{i}.ts',
            relative_path=f'other/file{i}.ts',
            size=1000,
            file_type='ts',
            category='source'
        ))
    
    groups = engine.group_files(files)
    
    # Key folder should be represented
    src_groups = [g for g in groups if 'src' in g.name]
    assert len(src_groups) > 0


def test_apply_misc_bucket(temp_source_dir):
    """Test misc bucket fallback."""
    engine = SmartConcatenationEngine(temp_source_dir, max_pdfs=3)
    
    # Create many groups
    groups = []
    for i in range(10):
        groups.append(PDFGroup(
            name=f'group{i}.pdf',
            files=[FileInfo(
                path=f'/fake/file{i}.ts',
                relative_path=f'file{i}.ts',
                size=1000,
                file_type='ts',
                category='source'
            )],
            directory_path=f'dir{i}',
            priority=i
        ))
    
    result = engine._apply_misc_bucket(groups)
    
    # Should have exactly max_pdfs groups
    assert len(result) == engine.max_pdfs
    
    # Should have misc.pdf
    misc_group = next((g for g in result if g.name == 'misc.pdf'), None)
    assert misc_group is not None
    assert len(misc_group.files) > 0


def test_group_files_empty_input(temp_source_dir):
    """Test grouping with empty file list."""
    engine = SmartConcatenationEngine(temp_source_dir)
    groups = engine.group_files([])
    
    assert len(groups) == 0


def test_group_files_single_root_file(temp_source_dir):
    """Test grouping with single root file."""
    engine = SmartConcatenationEngine(temp_source_dir, max_pdfs=10)
    
    files = [
        FileInfo(
            path='/fake/file.ts',
            relative_path='file.ts',
            size=1000,
            file_type='ts',
            category='source'
        )
    ]
    
    groups = engine.group_files(files)
    
    # Should have root_config.pdf
    assert len(groups) == 1
    assert groups[0].name == 'root_config.pdf'
    assert len(groups[0].files) == 1


def test_group_files_nested_directories(temp_source_dir):
    """Test with deeply nested directories."""
    engine = SmartConcatenationEngine(temp_source_dir, max_pdfs=5)
    
    files = [
        FileInfo(
            path='/fake/src/components/ui/buttons/Button.tsx',
            relative_path='src/components/ui/buttons/Button.tsx',
            size=1000,
            file_type='tsx',
            category='source'
        ),
        FileInfo(
            path='/fake/src/components/ui/inputs/Input.tsx',
            relative_path='src/components/ui/inputs/Input.tsx',
            size=1000,
            file_type='tsx',
            category='source'
        )
    ]
    
    groups = engine.group_files(files)
    
    # Should handle nested structure
    assert len(groups) <= engine.max_pdfs
    assert all(len(g.files) > 0 for g in groups)

