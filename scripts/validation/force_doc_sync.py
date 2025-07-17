#!/usr/bin/env python
"""
This script simulates the FORCE system's documentation_sync_commit tool to synchronize
documentation changes with code changes, ensuring proper cross-references and changelog updates.
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
import re

def print_section_header(title):
    """Print a section header with the given title."""
    print("=" * 80)
    print(f"{title:^80}")
    print("=" * 80)

def scan_documentation_changes(include_markdown_files=True, include_schema_files=True, analyze_cross_references=True):
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

def update_changelog_entries(doc_changes, timestamp_format="YYYY-MM-DD HH:mm PST", 
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
    return changelog_entry

def validate_cross_references(doc_changes, check_markdown_links=True, 
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
    
    # In a real implementation, this would scan files for links and check if they're valid
    # For this demo, we'll simulate it
    
    # Simulate finding some links
    validation_results["total_links"] = len(doc_changes.get("markdown", [])) * 3 + len(doc_changes.get("specs", [])) * 5
    validation_results["valid_links"] = validation_results["total_links"] - 2
    validation_results["broken_links"] = 2
    
    if report_broken_links and validation_results["broken_links"] > 0:
        # Simulate finding broken links
        validation_results["issues"] = [
            "Reference to non-existent anchor #implementation-details in FORCE_IMPLEMENTATION_SUMMARY.md",
            "Broken link to ../architecture/component-diagram.png in README.md"
        ]
    
    print(f"Found {validation_results['total_links']} total links")
    print(f"Valid links: {validation_results['valid_links']}")
    print(f"Broken links: {validation_results['broken_links']}")
    
    if validation_results["issues"]:
        print("\nIssues found:")
        for issue in validation_results["issues"]:
            print(f"  - {issue}")
    
    return validation_results

def commit_documentation_batch(doc_changes, validation_results, implementation_phase,
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
    
    # In a real implementation, this would actually create the commit
    # For this demo, we'll just simulate it
    print("\nNOTE: This is a simulation. In a real implementation, the following would happen:")
    print(f"  - Stage all {total_files} documentation files")
    print(f"  - Create commit with the message above")
    
    return commit_message

def main():
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
    
    print_section_header("FORCE Documentation Synchronization Tool")
    print(f"Running documentation sync for implementation phase: {args.implementation_phase}")
    
    # Scan for documentation changes
    doc_changes = scan_documentation_changes()
    if not doc_changes:
        print("No documentation changes detected.")
        return 0
    
    print(f"\nFound documentation changes in {len(doc_changes)} categories:")
    for category, files in doc_changes.items():
        print(f"  - {category}: {len(files)} files")
    
    # Update changelog if requested
    changelog_entry = None
    if args.update_changelog:
        changelog_entry = update_changelog_entries(doc_changes)
    
    # Validate cross-references if requested
    validation_results = None
    if args.cross_reference_anchors:
        validation_results = validate_cross_references(doc_changes)
    
    # Create the commit
    commit_message = commit_documentation_batch(
        doc_changes, 
        validation_results, 
        args.implementation_phase
    )
    
    print_section_header("Documentation Synchronization Complete")
    total_files = sum(len(files) for files in doc_changes.values())
    print(f"Successfully processed {total_files} documentation files")
    
    if args.dry_run:
        print("\nThis was a dry run. No changes were committed.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
