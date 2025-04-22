"""
File Utilities for Dev Sentinel

This module provides utilities for file operations needed by the Dev Sentinel agent ecosystem.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Union, Tuple, Generator

logger = logging.getLogger(__name__)

def get_file_paths(directory: str, 
                  file_extensions: Optional[List[str]] = None,
                  ignore_patterns: Optional[List[str]] = None,
                  recursive: bool = True) -> List[str]:
    """
    Get file paths in a directory, optionally filtering by extension.
    
    Args:
        directory: Directory to search
        file_extensions: List of file extensions to include (None for all)
        ignore_patterns: List of regex patterns for paths to ignore
        recursive: Whether to search recursively
        
    Returns:
        List of file paths
    """
    compiled_patterns = None
    if ignore_patterns:
        compiled_patterns = [re.compile(pattern) for pattern in ignore_patterns]
        
    file_paths = []
    
    if recursive:
        for root, dirs, files in os.walk(directory):
            # Skip directories that match ignore patterns
            if compiled_patterns:
                dirs_to_remove = []
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    rel_path = os.path.relpath(dir_path, directory)
                    if any(pattern.search(rel_path) for pattern in compiled_patterns):
                        dirs_to_remove.append(dir_name)
                
                for dir_name in dirs_to_remove:
                    dirs.remove(dir_name)
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, directory)
                
                # Skip files that match ignore patterns
                if compiled_patterns and any(pattern.search(rel_path) for pattern in compiled_patterns):
                    continue
                    
                # Filter by extension if specified
                if file_extensions:
                    ext = os.path.splitext(file)[1].lower()
                    if ext and ext[1:] in file_extensions:  # Remove leading dot
                        file_paths.append(file_path)
                else:
                    file_paths.append(file_path)
    else:
        # Non-recursive search
        for item in os.listdir(directory):
            file_path = os.path.join(directory, item)
            
            if not os.path.isfile(file_path):
                continue
                
            rel_path = os.path.relpath(file_path, directory)
            
            # Skip files that match ignore patterns
            if compiled_patterns and any(pattern.search(rel_path) for pattern in compiled_patterns):
                continue
                
            # Filter by extension if specified
            if file_extensions:
                ext = os.path.splitext(item)[1].lower()
                if ext and ext[1:] in file_extensions:  # Remove leading dot
                    file_paths.append(file_path)
            else:
                file_paths.append(file_path)
    
    return file_paths

def read_file_content(file_path: str) -> str:
    """
    Read the content of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Content of the file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If the file can't be read
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {str(e)}")
            raise IOError(f"Failed to read file {file_path}: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to read file {file_path}: {str(e)}")
        raise

def write_file_content(file_path: str, content: str, create_dirs: bool = True) -> None:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file
        content: Content to write
        create_dirs: Whether to create parent directories if they don't exist
        
    Raises:
        IOError: If the file can't be written to
    """
    try:
        if create_dirs:
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        logger.error(f"Failed to write to file {file_path}: {str(e)}")
        raise IOError(f"Failed to write to file {file_path}: {str(e)}")

def append_file_content(file_path: str, content: str, create_dirs: bool = True) -> None:
    """
    Append content to a file.
    
    Args:
        file_path: Path to the file
        content: Content to append
        create_dirs: Whether to create parent directories if they don't exist
        
    Raises:
        IOError: If the file can't be written to
    """
    try:
        if create_dirs:
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        logger.error(f"Failed to append to file {file_path}: {str(e)}")
        raise IOError(f"Failed to append to file {file_path}: {str(e)}")

def file_exists(file_path: str) -> bool:
    """
    Check if a file exists.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file exists, False otherwise
    """
    return os.path.isfile(file_path)

def directory_exists(directory_path: str) -> bool:
    """
    Check if a directory exists.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if the directory exists, False otherwise
    """
    return os.path.isdir(directory_path)

def create_directory(directory_path: str) -> None:
    """
    Create a directory if it doesn't exist.
    
    Args:
        directory_path: Path to the directory
    """
    os.makedirs(directory_path, exist_ok=True)

def get_file_extension(file_path: str) -> str:
    """
    Get the extension of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension without the leading dot
    """
    return os.path.splitext(file_path)[1].lower()[1:]  # Remove leading dot

def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes
    """
    return os.path.getsize(file_path)

def count_lines(file_path: str) -> int:
    """
    Count the number of lines in a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Number of lines in the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return sum(1 for _ in file)
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='latin-1') as file:
            return sum(1 for _ in file)

def get_directory_structure(
    root_dir: str, 
    max_depth: Optional[int] = None,
    ignore_patterns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get a nested dictionary representing the directory structure.
    
    Args:
        root_dir: Root directory to start from
        max_depth: Maximum depth to traverse (None for unlimited)
        ignore_patterns: List of regex patterns to ignore
        
    Returns:
        Nested dictionary representing the directory structure
    """
    compiled_patterns = None
    if ignore_patterns:
        compiled_patterns = [re.compile(pattern) for pattern in ignore_patterns]
    
    root_path = Path(root_dir).resolve()
    
    def should_ignore(path: Path) -> bool:
        if compiled_patterns:
            rel_path = path.relative_to(root_path)
            return any(pattern.search(str(rel_path)) for pattern in compiled_patterns)
        return False
    
    def get_structure(directory: Path, current_depth: int = 0) -> Dict[str, Any]:
        if max_depth is not None and current_depth > max_depth:
            return {}
        
        result = {}
        
        try:
            for item in directory.iterdir():
                if should_ignore(item):
                    continue
                    
                if item.is_dir():
                    child_structure = get_structure(item, current_depth + 1)
                    if child_structure:  # Only add non-empty directories
                        result[item.name + '/'] = child_structure
                else:
                    result[item.name] = None  # Files are represented with None value
        except PermissionError:
            # Skip directories we can't access
            pass
        
        return result
    
    return get_structure(root_path)

def find_files_by_content(
    directory: str,
    pattern: str,
    file_extensions: Optional[List[str]] = None,
    ignore_patterns: Optional[List[str]] = None,
    is_regex: bool = False
) -> List[Tuple[str, List[Tuple[int, str]]]]:
    """
    Find files containing a specific pattern.
    
    Args:
        directory: Directory to search
        pattern: Text pattern to search for
        file_extensions: List of file extensions to include (None for all)
        ignore_patterns: List of regex patterns for paths to ignore
        is_regex: Whether the pattern is a regular expression
        
    Returns:
        List of tuples with (file_path, [(line_number, line_content), ...])
    """
    file_paths = get_file_paths(directory, file_extensions, ignore_patterns)
    
    if is_regex:
        compiled_pattern = re.compile(pattern)
    
    results = []
    
    for file_path in file_paths:
        matching_lines = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for i, line in enumerate(file, 1):
                    if is_regex:
                        if compiled_pattern.search(line):
                            matching_lines.append((i, line.rstrip('\n')))
                    else:
                        if pattern in line:
                            matching_lines.append((i, line.rstrip('\n')))
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    for i, line in enumerate(file, 1):
                        if is_regex:
                            if compiled_pattern.search(line):
                                matching_lines.append((i, line.rstrip('\n')))
                        else:
                            if pattern in line:
                                matching_lines.append((i, line.rstrip('\n')))
            except Exception:
                # Skip files we can't read
                pass
        except Exception:
            # Skip files we can't read
            pass
            
        if matching_lines:
            results.append((file_path, matching_lines))
    
    return results

def read_file_chunk(file_path: str, start_line: int, end_line: int) -> str:
    """
    Read a specific chunk of a file.
    
    Args:
        file_path: Path to the file
        start_line: Starting line (1-based)
        end_line: Ending line (1-based, inclusive)
        
    Returns:
        Content of the specified chunk
    """
    lines = []
    current_line = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for i, line in enumerate(file, 1):
                current_line = i
                if i >= start_line and i <= end_line:
                    lines.append(line)
                if i > end_line:
                    break
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='latin-1') as file:
            for i, line in enumerate(file, 1):
                current_line = i
                if i >= start_line and i <= end_line:
                    lines.append(line)
                if i > end_line:
                    break
    
    if current_line < start_line:
        raise ValueError(f"File has fewer lines ({current_line}) than requested start line ({start_line})")
    
    return ''.join(lines)

def make_file_path_relative(file_path: str, base_path: str) -> str:
    """
    Convert an absolute file path to a path relative to the base path.
    
    Args:
        file_path: Absolute file path
        base_path: Base path to make the file path relative to
        
    Returns:
        Relative file path
    """
    return os.path.relpath(file_path, base_path)

def make_file_path_absolute(file_path: str, base_path: str) -> str:
    """
    Convert a relative file path to an absolute path based on the base path.
    
    Args:
        file_path: Relative file path
        base_path: Base path to resolve the file path against
        
    Returns:
        Absolute file path
    """
    if os.path.isabs(file_path):
        return file_path
    return os.path.normpath(os.path.join(base_path, file_path))

def load_json_file(file_path: str) -> Any:
    """
    Load JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_json_file(file_path: str, data: Any, indent: int = 2) -> None:
    """
    Save data as JSON to a file.
    
    Args:
        file_path: Path to the JSON file
        data: Data to save
        indent: Indentation level for the JSON file
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=indent)

def get_text_file_type(file_path: str) -> str:
    """
    Attempt to determine the type of a text file based on its content and extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Type of the file (e.g., 'python', 'javascript', 'markdown', etc.)
    """
    ext = get_file_extension(file_path).lower()
    
    # Common file types based on extensions
    extension_map = {
        'py': 'python',
        'js': 'javascript',
        'ts': 'typescript',
        'jsx': 'react',
        'tsx': 'react-typescript',
        'html': 'html',
        'css': 'css',
        'scss': 'scss',
        'less': 'less',
        'json': 'json',
        'md': 'markdown',
        'markdown': 'markdown',
        'yml': 'yaml',
        'yaml': 'yaml',
        'xml': 'xml',
        'csv': 'csv',
        'txt': 'plaintext',
        'sh': 'shell',
        'bash': 'shell',
        'bat': 'batch',
        'ps1': 'powershell',
        'sql': 'sql',
        'java': 'java',
        'c': 'c',
        'cpp': 'cpp',
        'cs': 'csharp',
        'go': 'go',
        'rs': 'rust',
        'rb': 'ruby',
        'php': 'php',
        'swift': 'swift',
        'kt': 'kotlin',
        'kts': 'kotlin',
        'scala': 'scala',
        'lua': 'lua',
        'r': 'r',
        'dart': 'dart',
        'ex': 'elixir',
        'exs': 'elixir',
        'pl': 'perl',
        'h': 'c-header',
        'hpp': 'cpp-header',
        'vue': 'vue',
        'svelte': 'svelte',
        'graphql': 'graphql',
        'gql': 'graphql',
    }
    
    # Return the file type if the extension is known
    if ext in extension_map:
        return extension_map[ext]
    
    # For unknown extensions, try to detect based on content
    try:
        content = read_file_content(file_path)
        first_line = content.split('\n', 1)[0] if content else ''
        
        # Check for shebang line
        if first_line.startswith('#!'):
            if 'python' in first_line:
                return 'python'
            elif 'node' in first_line:
                return 'javascript'
            elif 'bash' in first_line or 'sh' in first_line:
                return 'shell'
            elif 'perl' in first_line:
                return 'perl'
            elif 'ruby' in first_line:
                return 'ruby'
        
        # Check for common patterns
        if '<?php' in content[:1000]:
            return 'php'
        if '<html' in content[:1000].lower():
            return 'html'
        if 'function' in content and '{' in content and '}' in content:
            if 'import React' in content or 'from React' in content:
                return 'react'
            return 'javascript'
    except Exception:
        pass
    
    # Default to plaintext if we can't determine the type
    return 'plaintext'

def calculate_file_hash(file_path: str) -> str:
    """
    Calculate the SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Hash of the file as a hex string
    """
    import hashlib
    
    sha256 = hashlib.sha256()
    
    try:
        with open(file_path, 'rb') as file:
            for block in iter(lambda: file.read(65536), b''):
                sha256.update(block)
        return sha256.hexdigest()
    except Exception as e:
        logger.error(f"Failed to calculate hash for {file_path}: {str(e)}")
        raise IOError(f"Failed to calculate hash for {file_path}: {str(e)}")

def is_binary_file(file_path: str) -> bool:
    """
    Check if a file is binary.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file is binary, False otherwise
    """
    # Check file extension first
    binary_extensions = {
        'exe', 'dll', 'so', 'dylib', 'bin', 'o', 'obj', 'a', 'lib',
        'pyc', 'pyd', 'pyo', 'class',
        'png', 'jpg', 'jpeg', 'gif', 'bmp', 'ico', 'tiff', 'webp', 'svg',
        'mp3', 'mp4', 'wav', 'flac', 'ogg', 'avi', 'mkv', 'mov',
        'zip', 'gz', 'tar', 'rar', '7z', 'xz', 'bz2',
        'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
        'db', 'sqlite', 'mdb',
    }
    
    ext = get_file_extension(file_path)
    if ext in binary_extensions:
        return True
    
    # Check file content
    try:
        with open(file_path, 'rb') as file:
            chunk = file.read(1024)
            # Check if the file contains null bytes (common in binary files)
            if b'\x00' in chunk:
                return True
            
            # Count control characters (excluding common whitespace)
            control_chars = sum(1 for byte in chunk if byte < 32 and byte not in (9, 10, 13))
            
            # If more than 10% are control characters, consider it binary
            return control_chars / len(chunk) > 0.1 if chunk else False
    except Exception:
        # If we can't read the file, default to treating it as binary
        return True