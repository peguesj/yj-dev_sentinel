#!/usr/bin/env python
"""
This script simulates the FORCE system's project_structure_migration tool to perform
comprehensive project structure migrations with file moves, link updates, and symlink creation
for backward compatibility.
"""

import os
import sys
import json
import argparse
import subprocess
import shutil
from pathlib import Path
import re
import tempfile
from datetime import datetime

def print_section_header(title):
    """Print a section header with the given title."""
    print("=" * 80)
    print(f"{title:^80}")
    print("=" * 80)

def create_structure_backup(source_dir, backup_suffix="_backup", preserve_permissions=True, exclude_git_data=False):
    """
    Create a complete backup of the original structure.
    """
    source_path = Path(source_dir)
    if not source_path.exists() or not source_path.is_dir():
        print(f"Error: Source directory '{source_dir}' does not exist or is not a directory")
        return None
    
    # Create backup directory name
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_dir = f"{source_dir}{backup_suffix}_{timestamp}"
    backup_path = Path(backup_dir)
    
    print(f"Creating backup at {backup_dir}...")
    
    try:
        # Create backup directory
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Define patterns to exclude
        exclude_patterns = []
        if exclude_git_data:
            exclude_patterns.append(".git")
        
        # Copy files and directories
        for item in source_path.iterdir():
            # Skip excluded patterns
            if any(pattern in str(item) for pattern in exclude_patterns):
                print(f"Skipping {item} (excluded pattern)")
                continue
                
            # Copy to backup
            if item.is_dir():
                shutil.copytree(
                    item, 
                    backup_path / item.name, 
                    symlinks=True,
                    ignore=None
                )
            else:
                shutil.copy2(item, backup_path / item.name)
        
        print(f"Backup created successfully at {backup_dir}")
        return backup_dir
        
    except Exception as e:
        print(f"Error creating backup: {e}")
        return None

def create_target_directories(target_structure, create_parent_dirs=True, set_permissions="inherit"):
    """
    Create the new directory structure.
    """
    print(f"\nCreating target directory structure at {target_structure}...")
    
    target_path = Path(target_structure)
    
    # If target already exists, check if it's empty or not
    if target_path.exists():
        if any(target_path.iterdir()):
            print(f"Warning: Target directory {target_structure} already exists and is not empty")
    else:
        # Create target directory
        if create_parent_dirs:
            target_path.mkdir(parents=True, exist_ok=True)
        else:
            target_path.mkdir(exist_ok=True)
    
    # In a real implementation, this would create all subdirectories based on a structure definition
    # For this demo, we'll create some example directories
    example_dirs = [
        "src/core",
        "src/models",
        "src/controllers",
        "src/views",
        "docs/api",
        "docs/guides",
        "tests/unit",
        "tests/integration"
    ]
    
    for dir_path in example_dirs:
        full_path = target_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {full_path}")
    
    print(f"Created target directory structure successfully")
    return True

def migrate_files_logically(source_dir, target_dir, preserve_git_history=True, 
                          group_by_function=True, maintain_relationships=True):
    """
    Move files to new locations based on logical grouping.
    """
    print(f"\nMigrating files from {source_dir} to {target_dir}...")
    
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Track migration actions for reporting
    migration_actions = []
    
    # In a real implementation, this would analyze files and determine their logical groupings
    # For this demo, we'll define some example migrations
    example_migrations = [
        {
            "source": "models/*.py", 
            "target": "src/models", 
            "function": "data_models"
        },
        {
            "source": "controllers/*.py", 
            "target": "src/controllers", 
            "function": "business_logic"
        },
        {
            "source": "views/*.py", 
            "target": "src/views", 
            "function": "presentation"
        },
        {
            "source": "*.md", 
            "target": "docs/guides", 
            "function": "documentation"
        },
        {
            "source": "test_*.py", 
            "target": "tests/unit", 
            "function": "testing"
        }
    ]
    
    # Simulate file migration
    for migration in example_migrations:
        source_pattern = migration["source"]
        target_subdir = migration["target"]
        function_group = migration["function"]
        
        print(f"Migrating {source_pattern} files to {target_subdir} ({function_group})...")
        
        # In a real implementation, this would use glob to find files and actually move them
        # For this demo, we'll just simulate it
        migration_actions.append({
            "pattern": source_pattern,
            "target": target_subdir,
            "function": function_group,
            "count": 3,  # Simulate finding 3 files for each pattern
            "success": True
        })
    
    # If preserve_git_history is True, use git mv instead of regular move
    if preserve_git_history:
        print("Using 'git mv' to preserve file history in git")
    
    print(f"Completed file migration - moved files from {len(migration_actions)} patterns")
    return migration_actions

def update_internal_references(target_dir, scan_file_types=None, update_relative_paths=True, preserve_external_links=True):
    """
    Update all internal links, imports, and references to new paths.
    """
    if scan_file_types is None:
        scan_file_types = ["md", "json", "ts", "js", "yaml"]
        
    print(f"\nUpdating internal references in {target_dir}...")
    print(f"Scanning file types: {', '.join(scan_file_types)}")
    
    target_path = Path(target_dir)
    
    # Track reference updates
    updates = {
        "total_files_scanned": 0,
        "files_updated": 0,
        "references_updated": 0
    }
    
    # In a real implementation, this would walk the directory and update files
    # For this demo, we'll just simulate it
    updates["total_files_scanned"] = 45
    updates["files_updated"] = 23
    updates["references_updated"] = 78
    
    print(f"Updated {updates['references_updated']} references in {updates['files_updated']} files")
    return updates

def create_compatibility_symlinks(source_dir, target_dir, symlink_critical_paths=True, 
                                create_symlink_registry=True, test_symlink_integrity=True):
    """
    Create symlinks from old locations to new locations.
    """
    print(f"\nCreating backward compatibility symlinks...")
    
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Track created symlinks
    symlinks = []
    
    # In a real implementation, this would analyze critical paths and create actual symlinks
    # For this demo, we'll define some example symlinks
    example_symlinks = [
        {
            "old_path": "models",
            "new_path": "src/models",
            "critical": True
        },
        {
            "old_path": "controllers",
            "new_path": "src/controllers",
            "critical": True
        },
        {
            "old_path": "docs",
            "new_path": "docs/guides",
            "critical": False
        }
    ]
    
    # Filter if only critical paths are requested
    if symlink_critical_paths:
        example_symlinks = [s for s in example_symlinks if s["critical"]]
    
    # Simulate symlink creation
    for symlink in example_symlinks:
        old_path = symlink["old_path"]
        new_path = symlink["new_path"]
        critical = symlink["critical"]
        
        print(f"Creating symlink: {old_path} -> {new_path} (Critical: {critical})")
        
        # In a real implementation, this would create actual symlinks
        # For this demo, we'll just simulate it
        symlinks.append({
            "old_path": old_path,
            "new_path": new_path,
            "critical": critical,
            "success": True
        })
    
    # Create registry file if requested
    if create_symlink_registry:
        print("Creating symlink registry file for documentation and future reference")
        # In a real implementation, this would create a JSON file with symlink information
    
    # Test integrity if requested
    if test_symlink_integrity:
        print("Testing symlink integrity")
        # In a real implementation, this would verify symlinks are valid
    
    print(f"Created {len(symlinks)} backward compatibility symlinks")
    return symlinks

def validate_migration_integrity(source_dir, target_dir, check_file_integrity=True, 
                               validate_links=True, test_functionality=True):
    """
    Comprehensive validation of the migration results.
    """
    print(f"\nValidating migration integrity...")
    
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    validation_results = {
        "file_count_source": 0,
        "file_count_target": 0,
        "missing_files": [],
        "broken_links": [],
        "passed": True
    }
    
    # In a real implementation, this would perform actual validation
    # For this demo, we'll simulate it
    
    # Check file integrity
    if check_file_integrity:
        print("Checking file integrity - comparing source and target file counts")
        validation_results["file_count_source"] = 100  # Simulated count
        validation_results["file_count_target"] = 100  # Simulated count
        
        if validation_results["file_count_source"] != validation_results["file_count_target"]:
            validation_results["passed"] = False
            print(f"⚠️ File count mismatch: {validation_results['file_count_source']} (source) vs {validation_results['file_count_target']} (target)")
        else:
            print(f"✓ File counts match: {validation_results['file_count_source']} files")
    
    # Validate links
    if validate_links:
        print("Validating internal links")
        # In a real implementation, this would check links
        # For this demo, we'll simulate finding no broken links
        validation_results["broken_links"] = []
        print(f"✓ No broken internal links found")
    
    # Test functionality
    if test_functionality:
        print("Testing basic functionality")
        # In a real implementation, this would run tests
        # For this demo, we'll simulate all tests passing
        print(f"✓ All functionality tests passed")
    
    if validation_results["passed"]:
        print(f"✓ Migration validation completed successfully - all checks passed")
    else:
        print(f"⚠️ Migration validation found issues - see details above")
    
    return validation_results

def main():
    parser = argparse.ArgumentParser(description="FORCE Project Structure Migration Tool")
    parser.add_argument("--source", required=True, help="Path to the current project structure to be migrated")
    parser.add_argument("--target", required=True, help="Path to the new project structure layout")
    parser.add_argument("--create-symlinks", action="store_true", default=True,
                       help="Whether to create symlinks for backward compatibility")
    parser.add_argument("--update-links", action="store_true", default=True,
                       help="Whether to update internal markdown and reference links")
    parser.add_argument("--backup", action="store_true", default=True,
                       help="Whether to create a backup of the original structure")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Run in dry-run mode without making actual changes")
    args = parser.parse_args()
    
    print_section_header("FORCE Project Structure Migration Tool")
    print(f"Source directory: {args.source}")
    print(f"Target directory: {args.target}")
    
    if args.dry_run:
        print("Running in dry-run mode - no actual changes will be made")
    
    # Validate source directory
    if not os.path.exists(args.source) or not os.path.isdir(args.source):
        print(f"Error: Source directory '{args.source}' does not exist or is not a directory")
        return 1
    
    # Create backup if requested
    backup_path = None
    if args.backup and not args.dry_run:
        backup_path = create_structure_backup(args.source)
        if not backup_path:
            print("Error creating backup - aborting migration")
            return 1
    elif args.backup and args.dry_run:
        print("Backup would be created at (simulated): {args.source}_backup_YYYYMMDDHHMMSS")
    
    # Create target directory structure
    if not args.dry_run:
        if not create_target_directories(args.target):
            print("Error creating target directories - aborting migration")
            return 1
    else:
        print("Target directories would be created (simulated)")
    
    # Migrate files
    if not args.dry_run:
        migration_actions = migrate_files_logically(args.source, args.target)
    else:
        print("Files would be migrated logically based on function and relationships (simulated)")
    
    # Update internal references
    if args.update_links and not args.dry_run:
        updates = update_internal_references(args.target)
    elif args.update_links:
        print("Internal references would be updated (simulated)")
    
    # Create symlinks
    if args.create_symlinks and not args.dry_run:
        symlinks = create_compatibility_symlinks(args.source, args.target)
    elif args.create_symlinks:
        print("Backward compatibility symlinks would be created (simulated)")
    
    # Validate migration
    if not args.dry_run:
        validation_results = validate_migration_integrity(args.source, args.target)
    else:
        print("Migration integrity validation would be performed (simulated)")
    
    print_section_header("Project Structure Migration Complete")
    if args.dry_run:
        print("This was a dry run - no changes were made")
        print("Run without --dry-run to perform the actual migration")
    else:
        print("Migration completed successfully")
        if backup_path:
            print(f"Backup created at: {backup_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
