"""
Git workflow grouped commit tool for FORCE.

This module provides the GroupedCommitWorkflow tool that intelligently groups untracked work
based on logical changes and git history, creating granular commits for developer clarity,
and applying semantic versioning tags based on change impact weight.
"""

import os
import sys
import json
from pathlib import Path
import subprocess
import argparse
from datetime import datetime

class GroupedCommitTool:
    """
    A tool that intelligently groups untracked work based on logical changes and git history,
    creates granular commits for developer clarity, and applies semantic versioning tags.
    """
    
    TOOL_ID = "grouped_commit_workflow"
    TOOL_NAME = "Grouped Commit Workflow"
    TOOL_VERSION = "1.0.0"
    TOOL_DESCRIPTION = """
    Intelligently groups untracked work based on logical changes and git history, 
    creates granular commits for developer clarity, and applies semantic versioning 
    tags based on change impact weight.
    """
    
    def __init__(self, scope=None, semantic_version_increment="auto", 
                commit_message_prefix="", dry_run=False):
        """
        Initialize the GroupedCommitTool.
        
        Args:
            scope: Optional scope to limit commits to specific files or components
            semantic_version_increment: Override automatic version increment detection
            commit_message_prefix: Prefix for commit messages to maintain consistency
            dry_run: If True, perform a dry run without making actual commits
        """
        self.scope = scope
        self.semantic_version_increment = semantic_version_increment
        self.commit_message_prefix = commit_message_prefix
        self.dry_run = dry_run
        
    @property
    def tool_id(self):
        """Property for tool_id for registration."""
        return self.TOOL_ID
    
    def get_git_status(self):
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
    
    def analyze_changes_by_context(self, changes, include_chat_context=True, analyze_file_relationships=True):
        """
        Analyze changes by logical context using file analysis.
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
            
            # Scope filtering if provided
            if self.scope and self.scope.lower() not in file_path.lower():
                continue
                
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
    
    def create_granular_commits(self, grouped_changes, use_conventional_commits=True, include_impact_analysis=True):
        """
        Create individual commits for each logical group with descriptive messages.
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
                message_title = f"{self.commit_message_prefix}{commit_type}: update {len(files_to_commit)} files related to {group_name}"
                
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
                commit_message = f"{self.commit_message_prefix}Update {len(files_to_commit)} files related to {group_name}"
            
            print(f"\nCommitting {group_name} changes:")
            print(f"Commit message: {message_title}")
            print(f"Files to commit: {', '.join(files_to_commit)}")
            
            # Actually run git commands if not in dry run mode
            if not self.dry_run:
                try:
                    # Stage the files
                    for file_path in files_to_commit:
                        subprocess.run(["git", "add", file_path], check=True)
                    
                    # Create the commit
                    subprocess.run(["git", "commit", "-m", commit_message], check=True)
                    success = True
                except subprocess.CalledProcessError as e:
                    print(f"Error creating commit: {e}")
                    success = False
            else:
                success = True  # Assume success in dry run mode
            
            commit_results.append({
                "group": group_name,
                "files": files_to_commit,
                "message": commit_message,
                "success": success
            })
        
        return commit_results
    
    def determine_version_increment(self, commit_results, analyze_breaking_changes=True, 
                                   analyze_new_features=True, analyze_bug_fixes=True):
        """
        Analyze cumulative changes to determine appropriate semantic version increment.
        """
        print("\nDetermining appropriate version increment...")
        
        # Override with user-specified increment if not auto
        if self.semantic_version_increment != "auto":
            print(f"Using user-specified version increment: {self.semantic_version_increment}")
            return self.semantic_version_increment
        
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
    
    def apply_semantic_version_tag(self, version_increment, tag_format="v{major}.{minor}.{patch}", include_release_notes=True):
        """
        Create and push semantic version tag based on change analysis.
        """
        print(f"\nApplying semantic version tag ({version_increment} increment)...")
        
        # Get latest version tag
        try:
            result = subprocess.run(
                ["git", "tag", "--sort=-v:refname"], 
                capture_output=True, 
                text=True,
                check=True
            )
            
            # Parse versions from tags
            version_tags = [tag for tag in result.stdout.strip().split("\n") if tag.startswith("v")]
            
            if version_tags:
                latest_tag = version_tags[0]
                # Parse version components
                version_parts = latest_tag[1:].split(".")
                current_version = {
                    "major": int(version_parts[0]) if len(version_parts) > 0 else 0,
                    "minor": int(version_parts[1]) if len(version_parts) > 1 else 0,
                    "patch": int(version_parts[2]) if len(version_parts) > 2 else 0
                }
            else:
                current_version = {"major": 0, "minor": 1, "patch": 0}
        except subprocess.CalledProcessError:
            # Default if git tag command fails
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
        
        # Apply the tag if not in dry run mode
        if not self.dry_run:
            try:
                # Create tag with message
                tag_message = f"Version {new_version}"
                subprocess.run(["git", "tag", "-a", new_version, "-m", tag_message], check=True)
                
                # Push tag if release notes are included
                if include_release_notes:
                    subprocess.run(["git", "push", "origin", new_version], check=True)
                
                print(f"Successfully created and pushed tag: {new_version}")
                
            except subprocess.CalledProcessError as e:
                print(f"Error creating version tag: {e}")
                return None
        
        return new_version
        
    def execute(self):
        """Execute the grouped commit workflow."""
        print("Running grouped commit workflow to intelligently organize and commit changes...\n")
        
        # Get the git status
        changes = self.get_git_status()
        if not changes:
            print("No changes detected or error getting git status.")
            return {"success": False, "message": "No changes detected"}
        
        print(f"Found changes in the git repository:\n{changes}\n")
        
        # Analyze changes by context
        grouped_changes = self.analyze_changes_by_context(changes)
        if not grouped_changes:
            print("No changes to analyze or group.")
            return {"success": True, "message": "No changes to group"}
        
        print(f"\nGrouped changes into {len(grouped_changes)} logical categories:")
        for group, changes in grouped_changes.items():
            print(f"  - {group}: {len(changes)} files")
        
        # Create granular commits
        commit_results = self.create_granular_commits(grouped_changes)
        
        # Determine version increment and apply tag
        version_increment = self.determine_version_increment(commit_results)
        new_version = self.apply_semantic_version_tag(version_increment)
        
        result = {
            "success": all(commit["success"] for commit in commit_results),
            "message": f"Successfully grouped changes into {len(commit_results)} logical commits",
            "commits": len(commit_results),
            "version": new_version,
            "dry_run": self.dry_run,
            "commit_results": commit_results
        }
        
        return result


def main():
    """Command line entry point for the grouped commit tool."""
    parser = argparse.ArgumentParser(description="FORCE Grouped Commit Workflow Tool")
    parser.add_argument("--scope", type=str, help="Optional scope to limit commits to specific files or components")
    parser.add_argument("--version-increment", choices=["patch", "minor", "major", "auto"], default="auto", 
                       help="Override automatic version increment detection")
    parser.add_argument("--commit-message-prefix", type=str, default="",
                       help="Prefix for commit messages to maintain consistency")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode without making actual commits")
    args = parser.parse_args()
    
    print("=" * 80)
    print(f"{'FORCE Grouped Commit Workflow':^80}")
    print("=" * 80)
    
    tool = GroupedCommitTool(
        scope=args.scope,
        semantic_version_increment=args.version_increment,
        commit_message_prefix=args.commit_message_prefix,
        dry_run=args.dry_run
    )
    
    result = tool.execute()
    
    print("=" * 80)
    print(f"{'Grouped Commit Workflow Complete':^80}")
    print("=" * 80)
    
    print(result["message"])
    print(f"New version tag: {result['version']}")
    
    if args.dry_run:
        print("\nThis was a simulation. In an actual implementation, the commits and tags would be created.")
    
    return 0 if result["success"] else 1

if __name__ == "__main__":
    sys.exit(main())
