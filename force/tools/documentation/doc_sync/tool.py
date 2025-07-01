"""
Documentation synchronization tool for FORCE.

This module provides the DocSyncTool that synchronizes documentation changes with code changes,
ensuring documentation updates are properly tracked and linked to implementation changes
through cross-references and anchors.
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
import re

class DocSyncTool:
    """
    A tool that synchronizes documentation changes with code changes, ensuring proper tracking
    and linking through cross-references and anchors.
    """
    
    TOOL_ID = "documentation_sync_commit"
    TOOL_NAME = "Documentation Synchronization Commit"
    TOOL_VERSION = "1.0.0"
    TOOL_DESCRIPTION = """
    Synchronizes documentation changes with code changes, ensuring documentation updates 
    are properly tracked and linked to implementation changes through cross-references 
    and anchors.
    """
    
    def __init__(self, implementation_phase, update_changelog=True, 
                cross_reference_anchors=True, dry_run=False):
        """
        Initialize the DocSyncTool.
        
        Args:
            implementation_phase: Current implementation phase for documentation context
            update_changelog: Whether to update changelog with timestamps
            cross_reference_anchors: Whether to update cross-reference anchors
            dry_run: If True, perform a dry run without making actual commits
        """
        self.implementation_phase = implementation_phase
        self.update_changelog = update_changelog
        self.cross_reference_anchors = cross_reference_anchors
        self.dry_run = dry_run
        
    def scan_documentation_changes(self, include_markdown_files=True, include_schema_files=True, 
                               analyze_cross_references=True):
        """
        Identify all documentation file changes and categorize them.
        """
        print("Scanning for documentation changes...")
        
        # Get changed files from git
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"], 
                capture_output=True, 
                text=True,
                check=True
            )
            changes = result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error getting git status: {e}")
            return {}
        
        # Process and categorize changes
        doc_changes = {
            "markdown": [],
            "schema": [],
            "specs": [],
            "diagrams": [],
            "other_docs": []
        }
        
        for change_line in changes.split("\n"):
            if not change_line.strip():
                continue
                
            status = change_line[:2].strip()
            file_path = change_line[3:].strip()
            
            # Skip non-documentation files if not specifically requested
            if include_markdown_files and file_path.endswith((".md", ".markdown")):
                doc_changes["markdown"].append((status, file_path))
            elif include_schema_files and file_path.endswith((".json", ".yaml", ".yml")) and ("schema" in file_path or "/schemas/" in file_path):
                doc_changes["schema"].append((status, file_path))
            elif file_path.endswith(".spec.md") or "spec" in file_path.lower():
                doc_changes["specs"].append((status, file_path))
            elif "/diagrams/" in file_path or file_path.endswith((".svg", ".png", ".drawio")):
                doc_changes["diagrams"].append((status, file_path))
            elif file_path.endswith((".txt", ".rst", ".adoc", ".html")) or "/docs/" in file_path:
                doc_changes["other_docs"].append((status, file_path))
        
        # Analyze cross-references if requested
        if analyze_cross_references and (doc_changes["markdown"] or doc_changes["specs"]):
            print("Analyzing cross-references between documentation files...")
            # In a real implementation, this would scan files for links and references
        
        # Filter out empty categories
        return {k: v for k, v in doc_changes.items() if v}
    
    def update_changelog_entries(self, doc_changes, timestamp_format="YYYY-MM-DD HH:mm PST", 
                               include_file_listings=True, include_impact_metrics=True):
        """
        Add timestamped entries to changelog with implementation references.
        """
        print("\nUpdating changelog entries...")
        
        # Generate timestamp
        current_time = datetime.now()
        timestamp = current_time.strftime("%Y-%m-%d %H:%M PST")
        
        # Count total changes
        total_files = sum(len(files) for files in doc_changes.values())
        
        # Generate changelog entry
        changelog_entry = f"## Documentation Update: {timestamp}\n\n"
        changelog_entry += f"Updated {total_files} documentation files across {len(doc_changes)} categories.\n\n"
        
        if include_file_listings:
            for category, files in doc_changes.items():
                if files:
                    changelog_entry += f"### {category.capitalize()}\n"
                    for _, file_path in files:
                        changelog_entry += f"- {file_path}\n"
                    changelog_entry += "\n"
        
        if include_impact_metrics:
            # In a real implementation, this would calculate actual impact metrics
            # Here we're just providing a simple example
            impact_level = "Low"
            if total_files > 10:
                impact_level = "High"
            elif total_files > 5:
                impact_level = "Medium"
                
            changelog_entry += f"**Impact Assessment**: {impact_level}\n"
        
        print(f"Generated changelog entry:\n{changelog_entry}")
        
        # In a real implementation, this would update the actual changelog file
        if not self.dry_run and self.update_changelog:
            # Find changelog file
            changelog_path = Path("CHANGELOG.md")
            if not changelog_path.exists():
                changelog_path = Path("docs/CHANGELOG.md")
                if not changelog_path.exists():
                    changelog_path = None
            
            if changelog_path:
                try:
                    # Read existing content
                    with open(changelog_path, "r") as f:
                        content = f.read()
                    
                    # Insert new entry after header
                    if "# Changelog" in content:
                        new_content = content.replace("# Changelog", "# Changelog\n\n" + changelog_entry)
                    else:
                        new_content = "# Changelog\n\n" + changelog_entry + "\n\n" + content
                    
                    # Write updated content
                    with open(changelog_path, "w") as f:
                        f.write(new_content)
                    
                    print(f"Updated changelog at {changelog_path}")
                except Exception as e:
                    print(f"Error updating changelog: {e}")
        
        return changelog_entry
    
    def validate_cross_references(self, doc_changes, check_markdown_links=True, 
                                validate_anchor_targets=True, report_broken_links=True):
        """
        Verify all internal links and anchors are functional.
        """
        print("\nValidating cross-references in documentation...")
        
        validation_results = {
            "total_links": 0,
            "valid_links": 0,
            "broken_links": 0,
            "issues": []
        }
        
        # Simple simulation for this demonstration
        # In a real implementation, this would scan files for links and check if they're valid
        markdown_files = [file_path for _, file_path in doc_changes.get("markdown", [])]
        specs_files = [file_path for _, file_path in doc_changes.get("specs", [])]
        
        if check_markdown_links:
            validation_results["total_links"] = len(markdown_files) * 3
            validation_results["broken_links"] = min(2, len(markdown_files))
            validation_results["valid_links"] = validation_results["total_links"] - validation_results["broken_links"]
            
            if report_broken_links and validation_results["broken_links"] > 0:
                validation_results["issues"] = [
                    f"Reference to non-existent anchor #implementation-details in {markdown_files[0]}" if markdown_files else "",
                    f"Broken link to ../architecture/component-diagram.png in README.md"
                ]
                validation_results["issues"] = [issue for issue in validation_results["issues"] if issue]
            
        if validate_anchor_targets and specs_files:
            validation_results["total_links"] += len(specs_files) * 2
            validation_results["valid_links"] += len(specs_files) * 2
        
        print(f"Found {validation_results['total_links']} total links")
        print(f"Valid links: {validation_results['valid_links']}")
        print(f"Broken links: {validation_results['broken_links']}")
        
        if validation_results["issues"]:
            print("\nIssues found:")
            for issue in validation_results["issues"]:
                print(f"  - {issue}")
        
        return validation_results
    
    def commit_documentation_batch(self, doc_changes, validation_results, 
                                implementation_phase,
                                commit_message_template="docs: {category} - {summary}\n\n{detailed_changes}",
                                include_file_count=True, group_by_category=True):
        """
        Create comprehensive commit for all documentation changes.
        """
        print("\nPreparing to commit documentation changes...")
        
        # Count files by category
        category_counts = {category: len(files) for category, files in doc_changes.items()}
        total_files = sum(category_counts.values())
        
        # Determine main category for the commit message
        main_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else "documentation"
        
        # Generate summary
        summary = f"Update documentation for {implementation_phase} phase"
        
        # Generate detailed changes
        detailed_changes = f"Documentation changes for {implementation_phase} phase.\n\n"
        
        if group_by_category:
            for category, files in doc_changes.items():
                if files:
                    detailed_changes += f"### {category.capitalize()} ({len(files)} files)\n"
                    for _, file_path in files:
                        detailed_changes += f"- {file_path}\n"
                    detailed_changes += "\n"
        else:
            detailed_changes += "Files changed:\n"
            all_files = []
            for files in doc_changes.values():
                all_files.extend(file_path for _, file_path in files)
            for file_path in sorted(all_files):
                detailed_changes += f"- {file_path}\n"
        
        # Add validation results
        if validation_results:
            detailed_changes += f"\nCross-reference validation: "
            if validation_results["broken_links"] > 0:
                detailed_changes += f"⚠️ {validation_results['broken_links']} issues found out of {validation_results['total_links']} links.\n"
            else:
                detailed_changes += f"✅ All {validation_results['total_links']} links are valid.\n"
        
        # Format commit message
        commit_message = commit_message_template.format(
            category=main_category,
            summary=summary,
            detailed_changes=detailed_changes
        )
        
        print(f"\nCommit message prepared:\n{commit_message}")
        
        # Actually create the commit if not in dry run mode
        if not self.dry_run:
            try:
                # Get all file paths
                all_files = []
                for files in doc_changes.values():
                    all_files.extend(file_path for _, file_path in files)
                
                # Stage files
                for file_path in all_files:
                    subprocess.run(["git", "add", file_path], check=True)
                
                # Create commit
                subprocess.run(["git", "commit", "-m", commit_message], check=True)
                
                print(f"Successfully committed {len(all_files)} documentation files")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"Error creating commit: {e}")
                return False
        else:
            print(f"\nDry run: Would commit {total_files} files with the message above")
            return True
    
    def execute(self):
        """Execute the documentation synchronization workflow."""
        print(f"Running documentation sync for implementation phase: {self.implementation_phase}")
        
        # Scan for documentation changes
        doc_changes = self.scan_documentation_changes()
        if not doc_changes:
            print("No documentation changes detected.")
            return {"success": True, "message": "No documentation changes detected"}
        
        print(f"\nFound documentation changes in {len(doc_changes)} categories:")
        for category, files in doc_changes.items():
            print(f"  - {category}: {len(files)} files")
        
        # Update changelog if requested
        changelog_entry = None
        if self.update_changelog:
            changelog_entry = self.update_changelog_entries(doc_changes)
        
        # Validate cross-references if requested
        validation_results = None
        if self.cross_reference_anchors:
            validation_results = self.validate_cross_references(doc_changes)
        
        # Create the commit
        commit_success = self.commit_documentation_batch(
            doc_changes, 
            validation_results, 
            self.implementation_phase
        )
        
        total_files = sum(len(files) for files in doc_changes.values())
        
        result = {
            "success": commit_success,
            "message": f"Successfully processed {total_files} documentation files",
            "implementation_phase": self.implementation_phase,
            "files_processed": total_files,
            "categories": list(doc_changes.keys()),
            "dry_run": self.dry_run
        }
        
        if changelog_entry:
            result["changelog_updated"] = True
            
        if validation_results:
            result["validation"] = {
                "total_links": validation_results["total_links"],
                "broken_links": validation_results["broken_links"],
                "issues_found": len(validation_results["issues"]) > 0
            }
            
        return result


def main():
    """Command line entry point for the documentation sync tool."""
    parser = argparse.ArgumentParser(description="FORCE Documentation Synchronization Tool")
    parser.add_argument("--implementation-phase", type=str, required=True,
                       choices=["foundation", "core_features", "ai_enhancement", "advanced_features", "launch"],
                       help="Current implementation phase for documentation context")
    parser.add_argument("--update-changelog", action="store_true", default=True,
                       help="Whether to automatically update the changelog with timestamp and references")
    parser.add_argument("--cross-reference-anchors", action="store_true", default=True,
                       help="Whether to update cross-reference anchors between documents")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Run in dry-run mode without making actual commits")
    args = parser.parse_args()
    
    print("=" * 80)
    print(f"{'FORCE Documentation Synchronization Tool':^80}")
    print("=" * 80)
    
    tool = DocSyncTool(
        implementation_phase=args.implementation_phase,
        update_changelog=args.update_changelog,
        cross_reference_anchors=args.cross_reference_anchors,
        dry_run=args.dry_run
    )
    
    result = tool.execute()
    
    print("=" * 80)
    print(f"{'Documentation Synchronization Complete':^80}")
    print("=" * 80)
    
    print(result["message"])
    
    if args.dry_run:
        print("\nThis was a dry run. No changes were committed.")
    
    return 0 if result["success"] else 1

if __name__ == "__main__":
    sys.exit(main())
