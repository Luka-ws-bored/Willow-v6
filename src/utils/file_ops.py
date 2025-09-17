"""
Secure file operations utility for Willow v6.
Provides path validation and safe file handling.
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Union, Optional, BinaryIO, TextIO, Any, Generator, List
from contextlib import contextmanager
import logging
from functools import lru_cache
import weakref


class SecurityError(Exception):
    """Custom exception for security-related file operation errors."""
    pass


class SecureFileOps:
    """Secure file operations with path validation, safety checks, and performance optimizations."""
    
    def __init__(self, project_root: Path):
        """Initialize with project root for path validation.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root.resolve()
        self._path_cache = weakref.WeakValueDictionary()  # Cache validated paths
        
    @lru_cache(maxsize=128)
    def validate_path(self, file_path: Union[str, Path]) -> Path:
        """Validate that a file path is within the project root (cached).
        
        Args:
            file_path: Path to validate
            
        Returns:
            Validated and resolved Path object
            
        Raises:
            SecurityError: If path is outside project root or invalid
        """
        # Convert to string for caching (Path objects aren't hashable for LRU cache)
        path_str = str(file_path)
        
        try:
            path = Path(path_str).resolve()
        except (OSError, ValueError) as e:
            raise SecurityError(f"Invalid path: {path_str} - {e}")
        
        # Check if path is within project root
        try:
            path.relative_to(self.project_root)
        except ValueError:
            raise SecurityError(f"Path outside project root: {path}")
        
        return path
    
    @contextmanager
    def safe_open(
        self, 
        file_path: Union[str, Path], 
        mode: str = 'r', 
        encoding: Optional[str] = 'utf-8',
        **kwargs
    ):
        """Safely open a file with path validation and proper cleanup.
        
        Args:
            file_path: Path to the file
            mode: File open mode
            encoding: Text encoding (None for binary mode)
            **kwargs: Additional arguments to pass to open()
            
        Yields:
            File handle
            
        Raises:
            SecurityError: If path validation fails
        """
        validated_path = self.validate_path(file_path)
        
        # Ensure parent directory exists for write operations
        if 'w' in mode or 'a' in mode:
            validated_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if encoding is not None and 'b' not in mode:
                with open(validated_path, mode, encoding=encoding, **kwargs) as f:
                    yield f
            else:
                with open(validated_path, mode, **kwargs) as f:
                    yield f
        except (OSError, IOError) as e:
            raise SecurityError(f"File operation failed: {validated_path} - {e}")
    
    def safe_read_text(self, file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
        """Safely read text from a file.
        
        Args:
            file_path: Path to the file
            encoding: Text encoding
            
        Returns:
            File contents as string
        """
        with self.safe_open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    
    def safe_write_text(
        self, 
        file_path: Union[str, Path], 
        content: str, 
        encoding: str = 'utf-8'
    ) -> None:
        """Safely write text to a file.
        
        Args:
            file_path: Path to the file
            content: Content to write
            encoding: Text encoding
        """
        with self.safe_open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
    
    @contextmanager
    def safe_temp_file(
        self, 
        suffix: str = '', 
        prefix: str = 'willow_', 
        text_mode: bool = True
    ):
        """Create a temporary file safely within project bounds.
        
        Args:
            suffix: File suffix
            prefix: File prefix
            text_mode: Whether to open in text mode
            
        Yields:
            Temporary file handle
        """
        # Create temp file in project's temp directory
        temp_dir = self.project_root / 'tmp'
        temp_dir.mkdir(exist_ok=True)
        
        mode = 'w+t' if text_mode else 'w+b'
        
        try:
            with tempfile.NamedTemporaryFile(
                mode=mode,
                suffix=suffix,
                prefix=prefix,
                dir=temp_dir,
                delete=False
            ) as temp_file:
                temp_path = Path(temp_file.name)
                try:
                    yield temp_file
                finally:
                    # Ensure cleanup
                    if temp_path.exists():
                        temp_path.unlink()
        except Exception as e:
            logging.error(f"Temporary file operation failed: {e}")
            raise
    
    def safe_copy(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        """Safely copy a file with path validation.
        
        Args:
            src: Source file path
            dst: Destination file path
        """
        src_path = self.validate_path(src)
        dst_path = self.validate_path(dst)
        
        if not src_path.exists():
            raise SecurityError(f"Source file does not exist: {src_path}")
        
        # Ensure destination directory exists
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copy2(src_path, dst_path)
        except (OSError, IOError) as e:
            raise SecurityError(f"Copy operation failed: {src_path} -> {dst_path} - {e}")
    
    def safe_delete(self, file_path: Union[str, Path]) -> bool:
        """Safely delete a file with path validation.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            True if file was deleted, False if it didn't exist
        """
        path = self.validate_path(file_path)
        
        if not path.exists():
            return False
        
        if path.is_file():
            try:
                path.unlink()
                return True
            except OSError as e:
                raise SecurityError(f"Delete operation failed: {path} - {e}")
        else:
            raise SecurityError(f"Path is not a file: {path}")
    
    def list_safe_files(self, directory: Union[str, Path], pattern: str = '*', recursive: bool = False) -> Generator[Path, None, None]:
        """Safely list files in a directory within project bounds (generator for memory efficiency).
        
        Args:
            directory: Directory to list
            pattern: Glob pattern to match
            recursive: Whether to search recursively
            
        Yields:
            File paths matching the pattern
        """
        dir_path = self.validate_path(directory)
        
        if not dir_path.exists():
            return
        
        if not dir_path.is_dir():
            raise SecurityError(f"Path is not a directory: {dir_path}")
        
        try:
            if recursive:
                for file_path in dir_path.rglob(pattern):
                    if file_path.is_file():
                        yield file_path
            else:
                for file_path in dir_path.glob(pattern):
                    if file_path.is_file():
                        yield file_path
        except OSError as e:
            raise SecurityError(f"Directory listing failed: {dir_path} - {e}")
    
    def safe_read_text_chunked(self, file_path: Union[str, Path], encoding: str = 'utf-8', chunk_size: int = 8192) -> Generator[str, None, None]:
        """Safely read text from a file in chunks for memory efficiency.
        
        Args:
            file_path: Path to the file
            encoding: Text encoding
            chunk_size: Size of each chunk to read
            
        Yields:
            Text chunks from the file
        """
        with self.safe_open(file_path, 'r', encoding=encoding) as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    
    def safe_read_lines_lazy(self, file_path: Union[str, Path], encoding: str = 'utf-8') -> Generator[str, None, None]:
        """Safely read lines from a file lazily for memory efficiency.
        
        Args:
            file_path: Path to the file
            encoding: Text encoding
            
        Yields:
            Individual lines from the file
        """
        with self.safe_open(file_path, 'r', encoding=encoding) as f:
            for line in f:
                yield line.rstrip('\n\r')
    
    def safe_write_batch(self, file_operations: List[tuple[Union[str, Path], str]], encoding: str = 'utf-8') -> None:
        """Perform multiple write operations in a batch for better performance.
        
        Args:
            file_operations: List of (file_path, content) tuples
            encoding: Text encoding
        """
        # Group operations by directory to minimize path validation overhead
        operations_by_dir = {}
        for file_path, content in file_operations:
            validated_path = self.validate_path(file_path)
            parent_dir = validated_path.parent
            if parent_dir not in operations_by_dir:
                operations_by_dir[parent_dir] = []
            operations_by_dir[parent_dir].append((validated_path, content))
        
        # Ensure all directories exist first
        for parent_dir in operations_by_dir:
            parent_dir.mkdir(parents=True, exist_ok=True)
        
        # Perform all write operations
        for operations in operations_by_dir.values():
            for file_path, content in operations:
                with open(file_path, 'w', encoding=encoding) as f:
                    f.write(content)
    
    def safe_copy_batch(self, copy_operations: List[tuple[Union[str, Path], Union[str, Path]]]) -> None:
        """Perform multiple copy operations in a batch for better performance.
        
        Args:
            copy_operations: List of (src, dst) tuples
        """
        # Validate all paths first
        validated_operations = []
        for src, dst in copy_operations:
            src_path = self.validate_path(src)
            dst_path = self.validate_path(dst)
            
            if not src_path.exists():
                raise SecurityError(f"Source file does not exist: {src_path}")
            
            validated_operations.append((src_path, dst_path))
        
        # Create all destination directories
        dst_dirs = {dst_path.parent for _, dst_path in validated_operations}
        for dst_dir in dst_dirs:
            dst_dir.mkdir(parents=True, exist_ok=True)
        
        # Perform copy operations
        for src_path, dst_path in validated_operations:
            try:
                shutil.copy2(src_path, dst_path)
            except (OSError, IOError) as e:
                raise SecurityError(f"Copy operation failed: {src_path} -> {dst_path} - {e}")
    
    def clear_cache(self) -> None:
        """Clear the path validation cache to free memory."""
        self.validate_path.cache_clear()
        logging.info("File operations cache cleared")


# Global instance - initialized with project root
_file_ops: Optional[SecureFileOps] = None


def get_file_ops() -> SecureFileOps:
    """Get the global secure file operations instance.
    
    Returns:
        SecureFileOps instance
    """
    global _file_ops
    if _file_ops is None:
        # Auto-detect project root
        current = Path(__file__).parent.parent
        _file_ops = SecureFileOps(current)
    return _file_ops