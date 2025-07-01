#!/usr/bin/env python
"""
This script leverages the FORCE system's grouped_commit_workflow tool to intelligently organize
and commit changes in the repository.
"""

import os
import sys
import json
from pathlib import Path
import subprocess
import argparse

def print_section_header(title):
    """Print a section header with the given title."""
    print("=" * 80)
    print(f"{title:^80}")
    print("=" * 80)

def get_git_status():
    """Get the current git status output."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"], 
            capture_output=True, 
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting git status: {e}")
        return None

def analyze_changes_by_context(changes, include_chat_context=True, analyze_file_relationships=True):
    """
    Analyze changes by logical context using file analysis.
    This is a simplified version of what would be in the actual tool.
    """
    print("Analyzing changes by logical context...")
    
    # Dictionary to hold grouped changes
    groups = {
        "documentation": [],
        "feature": [],
        "bugfix": [],
        "refactor": [],
        "test": [],
        "config": [],
        "other": []
    }
    
    # Simple categorization based on file paths and change types
    for change_line in changes.split("\n"):
        if not change_line.strip():
            continue
            
        status = change_line[:2].strip()
        file_path = change_line[3:].strip()
        
        # Categorize based on file path patterns
        if file_path.endswith((".md", ".txt", ".rst")):
            groups["documentation"].append((status, file_path))
        elif "test" in file_path or file_path.startswith("tests/"):
            groups["test"].append((status, file_path))
        elif file_path.endswith((".json", ".yaml", ".yml", ".toml", ".ini")):
            groups["config"].append((status, file_path))
        elif "/fix/" in file_path or "fix_" in file_path.lower():
            groups["bugfix"].append((status, file_path))
        elif "/feature/" in file_path or "feat_" in file_path.lower():
            groups["feature"].append((status, file_path))
        elif "/refactor/" in file_path or "refactor_" in file_path.lower():
            groups["refactor"].append((status, file_path))
        else:
            # Default group
            groups["other"].append((status, file_path))
    
    # Filter out empty groups
    return {k: v for k, v in groups.items() if v}

def create_granular_commits(grouped_changes, use_conventional_commits=True, include_impact_analysis=True):
    """
    Create individual commits for each logical group with descriptive messages.
    This is a simplified version of what would be in the actual tool.
    """
    print("Creating granular commits based on logical grouping...")
    
    commit_results = []
    
    for group_name, changes in grouped_changes.items():
        if not changes:
            continue
            
        files_to_commit = [file_path for _, file_path in changes]
        
        # Generate commit message using conventional commits format if requested
        if use_conventional_commits:
            # Convert group name to conventional commit type
            commit_type = {
                "documentation": "docs",
                "feature": "feat",
                "bugfix": "fix",
                "refactor": "refactor",
                "test": "test",
                "config": "chore",
                "other": "chore"
            }.get(group_name, "chore")
            
            # Generate a basic commit message
            message_title = f"{commit_type}: update {len(files_to_commit)} files related to {group_name}"
            
            # Add file names to the message body
            message_body = "\n\nFiles changed:\n" + "\n".join(f"- {file_path}" for file_path in files_to_commit)
            
            # If impact analysis is requested, add a simple analysis
            if include_impact_analysis:
                impact = "low"
                if group_name in ["feature", "bugfix"]:
                    impact = "medium"
                message_body += f"\n\nImpact: {impact}"
                
            commit_message = message_title + message_body
        else:
            # Simple non-conventional commit message
            commit_message = f"Update {len(files_to_commit)} files related to {group_name}"
        
        print(f"\nCommitting {group_name} changes:")
        print(f"Commit message: {message_title}")
        print(f"Files to commit: {', '.join(files_to_commit)}")
        
        # In a real implementation, this would actually run git commands
        # For this demo script, we'll just simulate it
        commit_results.append({
            "group": group_name,
            "files": files_to_commit,
            "message": commit_message,
            "success": True
        })
    
    return commit_results

def determine_version_increment(commit_results, analyze_breaking_changes=True, 
                               analyze_new_features=True, analyze_bug_fixes=True):
    """
    Analyze cumulative changes to determine appropriate semantic version increment.
    This is a simplified version of what would be in the actual tool.
    """
    print("\nDetermining appropriate version increment...")
    
    # Default to patch increment
    increment = "patch"
    
    # Check for features if requested
    if analyze_new_features and any(commit["group"] == "feature" for commit in commit_results):
        increment = "minor"
    
    # Check for breaking changes if requested (simulated logic)
    if analyze_breaking_changes:
        # In a real implementation, this would analyze the actual changes
        # For this demo, we'll just check for "BREAKING CHANGE" in commit messages
        if any("BREAKING CHANGE" in commit["message"] for commit in commit_results):
            increment = "major"
    
    print(f"Determined version increment: {increment}")
    return increment

def apply_semantic_version_tag(version_increment, tag_format="v{major}.{minor}.{patch}", include_release_notes=True):
    """
    Create and push semantic version tag based on change analysis.
    This is a simplified version of what would be in the actual tool.
    """
    print(f"\nApplying semantic version tag ({version_increment} increment)...")
    
    # In a real implementation, this would get the latest version tag and increment it
    # For this demo, we'll just simulate it with a dummy version
    current_version = {"major": 0, "minor": 1, "patch": 0}
    
    # Increment the appropriate part
    if version_increment == "major":
        current_version["major"] += 1
        current_version["minor"] = 0
        current_version["patch"] = 0
    elif version_increment == "minor":
        current_version["minor"] += 1
        current_version["patch"] = 0
    else:  # patch
        current_version["patch"] += 1
    
    # Format the new version tag
    new_version = tag_format.format(
        major=current_version["major"],
        minor=current_version["minor"],
        patch=current_version["patch"]
    )
    
    print(f"New version tag: {new_version}")
    
    # In a real implementation, this would actually create and push the tag
    # For this demo, we'll just simulate it
    
    return new_version

def main():
    parser = argparse.ArgumentParser(description="FORCE Grouped Commit Workflow Tool")
    parser.add_argument("--scope", type=str, help="Optional scope to limit commits to specific files or components")
    parser.add_argument("--version-increment", choices=["patch", "minor", "major", "auto"], default="auto", 
                       help="Override automatic version increment detection")
    parser.add_argument("--commit-message-prefix", type=str, default="",
                       help="Prefix for commit messages to maintain consistency")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode without making actual commits")
    args = parser.parse_args()
    
    print_section_header("FORCE Grouped Commit Workflow")
    print("Running grouped commit workflow to intelligently organize and commit changes...\n")
    
    # Get the git status
    changes = get_git_status()
    if not changes:
        print("No changes detected or error getting git status.")
        return 1
    
    print(f"Found changes in the git repository:\n{changes}\n")
    
    # Analyze changes by context
    grouped_changes = analyze_changes_by_context(changes)
    if not grouped_changes:
        print("No changes to analyze or group.")
        return 0
    
    print(f"\nGrouped changes into {len(grouped_changes)} logical categories:")
    for group, changes in grouped_changes.items():
        print(f"  - {group}: {len(changes)} files")
    
    # Create granular commits
    commit_results = create_granular_commits(grouped_changes)
    
    # Determine version increment
    version_increment = args.version_increment
    if version_increment == "auto":
        version_increment = determine_version_increment(commit_results)
    
    # Apply semantic version tag
    new_version = apply_semantic_version_tag(version_increment)
    
    print_section_header("Grouped Commit Workflow Complete")
    print(f"Successfully analyzed and grouped changes into {len(commit_results)} logical commits")
    print(f"New version tag: {new_version}")
    print("\nNote: This is a simulation. In an actual implementation, the commits and tags would be created.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
