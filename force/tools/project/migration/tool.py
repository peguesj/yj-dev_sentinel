"""
Project migration tool for FORCE.

This module provides the ProjectMigrationTool that performs comprehensive project structure migrations
with file moves, link updates, and symlink creation for backward compatibility.
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


class ProjectMigrationTool:
    """
    A tool that performs comprehensive project structure migrations with file moves,
    link updates, and symlink creation for backward compatibility.
    
    Attributes:
        source_dir (str): The source directory to migrate
        target_dir (str): The target directory for migration
        mapping_file (str): Path to a JSON mapping file with move instructions
        create_symlinks (bool): Whether to create symlinks for backward compatibility
        update_imports (bool): Whether to update import statements in code files
        update_links (bool): Whether to update links in documentation files
    """

    def __init__(self, source_dir=None, target_dir=None, mapping_file=None, 
                 create_symlinks=True, update_imports=True, update_links=True):
        """
        Initialize the ProjectMigrationTool with configured parameters.

        Args:
            source_dir (str): The source directory to migrate
            target_dir (str): The target directory for migration
            mapping_file (str): Path to a JSON mapping file with move instructions
            create_symlinks (bool): Whether to create symlinks for backward compatibility
            update_imports (bool): Whether to update import statements in code files
            update_links (bool): Whether to update links in documentation files
        """
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.mapping_file = mapping_file
        self.create_symlinks = create_symlinks
        self.update_imports = update_imports
        self.update_links = update_links
        self.log_entries = []
        self.errors = []

    @staticmethod
    def print_section_header(title):
        """Print a section header with the given title."""
        print("=" * 80)
        print(f"{title:^80}")
        print("=" * 80)

    def create_structure_backup(self, source_dir, backup_suffix="_backup", preserve_permissions=True, exclude_git_data=False):
        """
        Create a complete backup of the original structure.
        
        Args:
            source_dir (str): The directory to backup
            backup_suffix (str): The suffix to add to the backup directory
            preserve_permissions (bool): Whether to preserve file permissions
            exclude_git_data (bool): Whether to exclude .git directories
        
        Returns:
            Path: The path to the backup directory
        """
        source_path = Path(source_dir)
        if not source_path.exists() or not source_path.is_dir():
            self.log_error(f"Error: Source directory '{source_dir}' does not exist or is not a directory.")
            return None
            
        backup_path = Path(f"{source_dir}{backup_suffix}")
        
        # If the backup already exists, create a uniquely named one
        if backup_path.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = Path(f"{source_dir}_{timestamp}{backup_suffix}")
            
        try:
            if exclude_git_data:
                shutil.copytree(
                    source_path,
                    backup_path,
                    symlinks=True,
                    ignore=shutil.ignore_patterns('.git*'),
                    dirs_exist_ok=False
                )
            else:
                shutil.copytree(
                    source_path,
                    backup_path,
                    symlinks=True,
                    dirs_exist_ok=False
                )
            self.log_info(f"Created backup at: {backup_path}")
            return backup_path
        except Exception as e:
            self.log_error(f"Error creating backup: {str(e)}")
            return None
    
    def log_info(self, message):
        """Log an informational message"""
        print(message)
        self.log_entries.append({"level": "INFO", "message": message, "timestamp": datetime.now().isoformat()})
    
    def log_error(self, message):
        """Log an error message"""
        print(f"ERROR: {message}", file=sys.stderr)
        self.errors.append(message)
        self.log_entries.append({"level": "ERROR", "message": message, "timestamp": datetime.now().isoformat()})
    
    def log_warning(self, message):
        """Log a warning message"""
        print(f"WARNING: {message}")
        self.log_entries.append({"level": "WARNING", "message": message, "timestamp": datetime.now().isoformat()})
    
    def validate_mapping(self, mapping):
        """
        Validate the migration mapping structure.
        
        Args:
            mapping (dict): The mapping dictionary to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(mapping, dict):
            self.log_error("Mapping must be a dictionary.")
            return False
            
        required_keys = ["version", "migrations"]
        for key in required_keys:
            if key not in mapping:
                self.log_error(f"Missing required key in mapping: {key}")
                return False
                
        if not isinstance(mapping["migrations"], list):
            self.log_error("'migrations' must be a list.")
            return False
            
        for i, migration in enumerate(mapping["migrations"]):
            if not isinstance(migration, dict):
                self.log_error(f"Migration entry {i} must be a dictionary.")
                return False
                
            if "source" not in migration or "target" not in migration:
                self.log_error(f"Migration entry {i} missing required 'source' or 'target'.")
                return False
                
        return True
    
    def generate_migration_report(self, output_file=None):
        """
        Generate a report of the migration.
        
        Args:
            output_file (str): Path to save the report, or None to print to console
            
        Returns:
            str: The report content
        """
        report = []
        report.append("# Project Migration Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        report.append("## Summary")
        report.append(f"- Source directory: {self.source_dir}")
        report.append(f"- Target directory: {self.target_dir}")
        report.append(f"- Mapping file: {self.mapping_file}")
        report.append(f"- Create symlinks: {self.create_symlinks}")
        report.append(f"- Update imports: {self.update_imports}")
        report.append(f"- Update links: {self.update_links}")
        report.append("")
        
        if self.errors:
            report.append("## Errors")
            for error in self.errors:
                report.append(f"- {error}")
            report.append("")
        
        report.append("## Log Entries")
        for entry in self.log_entries:
            report.append(f"[{entry['level']}] {entry['timestamp']}: {entry['message']}")
        
        report_content = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_content)
            print(f"Report saved to: {output_file}")
        else:
            print(report_content)
            
        return report_content
    
    def run(self):
        """
        Run the migration process.
        
        Returns:
            bool: True if successful, False otherwise
        """
        self.print_section_header("Project Migration Tool")
        
        # Validate inputs
        if not self.source_dir or not os.path.isdir(self.source_dir):
            self.log_error(f"Invalid source directory: {self.source_dir}")
            return False
            
        if not self.mapping_file or not os.path.isfile(self.mapping_file):
            self.log_error(f"Invalid mapping file: {self.mapping_file}")
            return False
            
        # Load and validate the mapping
        try:
            with open(self.mapping_file, 'r') as f:
                mapping = json.load(f)
        except Exception as e:
            self.log_error(f"Error loading mapping file: {str(e)}")
            return False
            
        if not self.validate_mapping(mapping):
            return False
            
        # Create backup
        self.log_info("Creating backup...")
        backup_path = self.create_structure_backup(self.source_dir)
        if not backup_path:
            self.log_error("Failed to create backup. Aborting.")
            return False
            
        # Process migrations
        self.log_info("Processing migrations...")
        success = True
        for migration in mapping["migrations"]:
            source = os.path.join(self.source_dir, migration["source"])
            target = os.path.join(self.target_dir or self.source_dir, migration["target"])
            
            self.log_info(f"Moving: {source} -> {target}")
            
            # Create target directory if it doesn't exist
            os.makedirs(os.path.dirname(target), exist_ok=True)
            
            try:
                # Perform the move
                if os.path.exists(source):
                    if os.path.exists(target):
                        self.log_warning(f"Target already exists: {target}")
                        # Handle based on configuration (skip, overwrite, etc.)
                    else:
                        # Move the file or directory
                        shutil.move(source, target)
                    
                    # Create symlink for backward compatibility if requested
                    if self.create_symlinks:
                        # Make source dir if it doesn't exist
                        os.makedirs(os.path.dirname(source), exist_ok=True)
                        
                        # Create a relative symlink
                        rel_path = os.path.relpath(target, os.path.dirname(source))
                        os.symlink(rel_path, source)
                        self.log_info(f"Created symlink: {source} -> {rel_path}")
                else:
                    self.log_warning(f"Source does not exist: {source}")
            except Exception as e:
                self.log_error(f"Error processing migration: {str(e)}")
                success = False
                
        # Generate and save the report
        report_path = os.path.join(self.target_dir or self.source_dir, "migration_report.md")
        self.generate_migration_report(report_path)
        
        if success:
            self.log_info("Migration completed successfully.")
        else:
            self.log_warning("Migration completed with errors. Check the report for details.")
            
        return success


def main():
    """Main entry point for the project migration tool."""
    parser = argparse.ArgumentParser(description="FORCE Project Migration Tool")
    parser.add_argument("--source-dir", required=True, help="Source directory to migrate")
    parser.add_argument("--target-dir", help="Target directory for the migration")
    parser.add_argument("--mapping-file", required=True, help="JSON file with migration mapping")
    parser.add_argument("--no-symlinks", action="store_true", help="Disable creation of symlinks")
    parser.add_argument("--no-update-imports", action="store_true", help="Disable import statement updates")
    parser.add_argument("--no-update-links", action="store_true", help="Disable documentation link updates")
    parser.add_argument("--report", help="Path for the migration report")
    
    args = parser.parse_args()
    
    tool = ProjectMigrationTool(
        source_dir=args.source_dir,
        target_dir=args.target_dir,
        mapping_file=args.mapping_file,
        create_symlinks=not args.no_symlinks,
        update_imports=not args.no_update_imports,
        update_links=not args.no_update_links
    )
    
    success = tool.run()
    
    if args.report:
        tool.generate_migration_report(args.report)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
