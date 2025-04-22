"""
Version Control System (VCS) Utilities for Dev Sentinel

This module provides utilities for interacting with version control systems
like Git for the Dev Sentinel agent ecosystem.
"""

import os
import subprocess
import logging
from typing import Dict, List, Tuple, Set, Optional, Any, Union
import json
import re
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class GitError(Exception):
    """Exception raised for Git command errors"""
    pass

def run_git_command(command: List[str], repo_path: str) -> str:
    """
    Run a Git command in the specified repository.
    
    Args:
        command: Git command as a list of strings
        repo_path: Path to the Git repository
        
    Returns:
        Command output as a string
        
    Raises:
        GitError: If the command fails
    """
    try:
        full_command = ["git"] + command
        logger.debug(f"Running Git command: {' '.join(full_command)}")
        
        result = subprocess.run(
            full_command,
            cwd=repo_path,
            check=True,
            text=True,
            capture_output=True
        )
        
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_msg = f"Git command failed: {e.stderr.strip()}"
        logger.error(error_msg)
        raise GitError(error_msg) from e

def get_repo_root(path: str) -> str:
    """
    Get the root directory of the Git repository containing the specified path.
    
    Args:
        path: Path within a Git repository
        
    Returns:
        Root path of the Git repository
        
    Raises:
        GitError: If the path is not in a Git repository
    """
    try:
        root = run_git_command(["rev-parse", "--show-toplevel"], path)
        return root
    except GitError as e:
        raise GitError(f"Failed to get repository root for path {path}: {str(e)}") from e

def get_current_branch(repo_path: str) -> str:
    """
    Get the name of the current Git branch.
    
    Args:
        repo_path: Path to the Git repository
        
    Returns:
        Name of the current branch
    """
    try:
        branch = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], repo_path)
        return branch
    except GitError:
        return "DETACHED_HEAD"

def get_current_commit(repo_path: str) -> str:
    """
    Get the hash of the current commit.
    
    Args:
        repo_path: Path to the Git repository
        
    Returns:
        Hash of the current commit
    """
    return run_git_command(["rev-parse", "HEAD"], repo_path)

def get_changed_files(repo_path: str, 
                     staged_only: bool = False, 
                     include_untracked: bool = False) -> Dict[str, str]:
    """
    Get a list of files that have been changed.
    
    Args:
        repo_path: Path to the Git repository
        staged_only: If True, only return staged changes
        include_untracked: If True, include untracked files
        
    Returns:
        Dictionary mapping file paths to their status
    """
    status_command = ["status", "--porcelain"]
    
    if staged_only:
        status_output = run_git_command(status_command, repo_path)
        changes = {}
        
        for line in status_output.splitlines():
            if not line:
                continue
                
            status = line[:2]
            # Only include staged files (first character is not a space)
            if status[0] != ' ' and status[0] != '?':
                file_path = line[3:]
                changes[file_path] = status
                
        return changes
    else:
        status_output = run_git_command(status_command, repo_path)
        changes = {}
        
        for line in status_output.splitlines():
            if not line:
                continue
                
            status = line[:2]
            file_path = line[3:]
            
            # Skip untracked files if not requested
            if status == '??' and not include_untracked:
                continue
                
            changes[file_path] = status
            
        return changes

def get_file_diff(repo_path: str, file_path: str, staged: bool = False) -> str:
    """
    Get the diff for a specific file.
    
    Args:
        repo_path: Path to the Git repository
        file_path: Path to the file to diff (relative to repo root)
        staged: If True, get the staged diff
        
    Returns:
        Diff content as a string
    """
    diff_command = ["diff"]
    
    if staged:
        diff_command.append("--staged")
        
    diff_command.extend(["--", file_path])
    
    return run_git_command(diff_command, repo_path)

def get_commit_details(repo_path: str, commit_hash: str) -> Dict[str, str]:
    """
    Get details about a specific commit.
    
    Args:
        repo_path: Path to the Git repository
        commit_hash: Hash of the commit to get details for
        
    Returns:
        Dictionary containing commit details
    """
    format_string = {
        "hash": "%H",
        "abbreviated_hash": "%h",
        "author_name": "%an",
        "author_email": "%ae",
        "author_date": "%aI",
        "committer_name": "%cn", 
        "committer_email": "%ce",
        "committer_date": "%cI",
        "subject": "%s",
        "body": "%b"
    }
    
    format_arg = "--format=" + "%n".join([f"{k}:{v}" for k, v in format_string.items()])
    
    details_output = run_git_command(["show", format_arg, commit_hash], repo_path)
    
    details = {}
    current_key = None
    current_value = []
    
    for line in details_output.splitlines():
        if ":" in line and line.split(":", 1)[0] in format_string:
            if current_key:
                details[current_key] = "\n".join(current_value).strip()
                current_value = []
                
            current_key, value = line.split(":", 1)
            current_value.append(value)
        elif current_key:
            current_value.append(line)
    
    if current_key:
        details[current_key] = "\n".join(current_value).strip()
    
    return details

def get_commit_files(repo_path: str, commit_hash: str) -> List[str]:
    """
    Get a list of files changed in a specific commit.
    
    Args:
        repo_path: Path to the Git repository
        commit_hash: Hash of the commit
        
    Returns:
        List of file paths changed in the commit
    """
    files_output = run_git_command(["diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash], repo_path)
    return files_output.splitlines()

def get_file_history(repo_path: str, file_path: str, max_entries: int = 10) -> List[Dict[str, str]]:
    """
    Get commit history for a specific file.
    
    Args:
        repo_path: Path to the Git repository
        file_path: Path to the file (relative to repo root)
        max_entries: Maximum number of history entries to return
        
    Returns:
        List of dictionaries containing commit information
    """
    format_string = "%H|%h|%an|%ae|%aI|%s"
    log_output = run_git_command(
        ["log", f"--max-count={max_entries}", f"--pretty=format:{format_string}", "--", file_path],
        repo_path
    )
    
    history = []
    for line in log_output.splitlines():
        if not line.strip():
            continue
            
        parts = line.split("|")
        if len(parts) >= 6:
            history.append({
                "hash": parts[0],
                "abbreviated_hash": parts[1],
                "author_name": parts[2],
                "author_email": parts[3],
                "date": parts[4],
                "subject": parts[5]
            })
    
    return history

def get_file_content_at_commit(repo_path: str, file_path: str, commit_hash: str) -> str:
    """
    Get the content of a file at a specific commit.
    
    Args:
        repo_path: Path to the Git repository
        file_path: Path to the file (relative to repo root)
        commit_hash: Hash of the commit to get the content from
        
    Returns:
        Content of the file at the specified commit
    """
    return run_git_command(["show", f"{commit_hash}:{file_path}"], repo_path)

def get_recent_commits(repo_path: str, max_count: int = 10, branch: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Get recent commits from the repository.
    
    Args:
        repo_path: Path to the Git repository
        max_count: Maximum number of commits to retrieve
        branch: Optional branch name to get commits from
        
    Returns:
        List of dictionaries containing commit information
    """
    command = ["log", f"--max-count={max_count}", "--pretty=format:%H|%h|%an|%ae|%aI|%s"]
    
    if branch:
        command.append(branch)
    
    log_output = run_git_command(command, repo_path)
    
    commits = []
    for line in log_output.splitlines():
        if not line.strip():
            continue
            
        parts = line.split("|")
        if len(parts) >= 6:
            commits.append({
                "hash": parts[0],
                "abbreviated_hash": parts[1],
                "author_name": parts[2],
                "author_email": parts[3],
                "date": parts[4],
                "subject": parts[5]
            })
    
    return commits

def analyze_repository_activity(repo_path: str, days: int = 30) -> Dict[str, Any]:
    """
    Analyze repository activity for the past number of days.
    
    Args:
        repo_path: Path to the Git repository
        days: Number of days to analyze
        
    Returns:
        Dictionary containing activity statistics
    """
    since_date = datetime.now(timezone.utc) - datetime.timedelta(days=days)
    since_date_str = since_date.strftime("%Y-%m-%d")
    
    # Get commits in the time range
    log_output = run_git_command([
        "log", 
        f"--since={since_date_str}", 
        "--pretty=format:%H|%an|%ae|%aI"
    ], repo_path)
    
    commits = []
    authors = set()
    dates = []
    
    for line in log_output.splitlines():
        if not line.strip():
            continue
            
        parts = line.split("|")
        if len(parts) >= 4:
            commit_hash = parts[0]
            author_name = parts[1]
            author_email = parts[2]
            date = parts[3]
            
            commits.append(commit_hash)
            authors.add(f"{author_name} <{author_email}>")
            dates.append(date)
    
    # Get files changed
    files_changed = set()
    for commit in commits:
        files = get_commit_files(repo_path, commit)
        files_changed.update(files)
    
    # Calculate statistics
    stats = {
        "period_days": days,
        "commit_count": len(commits),
        "author_count": len(authors),
        "files_changed": len(files_changed),
        "authors": list(authors)
    }
    
    if dates:
        # Calculate commit frequency
        first_date = datetime.fromisoformat(dates[-1])
        last_date = datetime.fromisoformat(dates[0])
        date_range = (last_date - first_date).days or 1  # Avoid division by zero
        
        stats["commits_per_day"] = len(commits) / date_range
    else:
        stats["commits_per_day"] = 0
    
    return stats

def get_branch_list(repo_path: str) -> List[str]:
    """
    Get a list of all branches in the repository.
    
    Args:
        repo_path: Path to the Git repository
        
    Returns:
        List of branch names
    """
    branches_output = run_git_command(["branch", "--list", "--format=%(refname:short)"], repo_path)
    return [branch for branch in branches_output.splitlines() if branch.strip()]

def create_branch(repo_path: str, branch_name: str, start_point: Optional[str] = None) -> bool:
    """
    Create a new branch.
    
    Args:
        repo_path: Path to the Git repository
        branch_name: Name for the new branch
        start_point: Optional starting point (commit/branch) for the new branch
        
    Returns:
        True if branch was created successfully
    """
    command = ["branch", branch_name]
    
    if start_point:
        command.append(start_point)
        
    try:
        run_git_command(command, repo_path)
        return True
    except GitError:
        return False

def checkout_branch(repo_path: str, branch_name: str) -> bool:
    """
    Checkout a branch.
    
    Args:
        repo_path: Path to the Git repository
        branch_name: Name of the branch to checkout
        
    Returns:
        True if checkout was successful
    """
    try:
        run_git_command(["checkout", branch_name], repo_path)
        return True
    except GitError:
        return False

def get_repo_status(repo_path: str) -> Dict[str, Any]:
    """
    Get a comprehensive status of the repository.
    
    Args:
        repo_path: Path to the Git repository
        
    Returns:
        Dictionary containing repository status information
    """
    try:
        status = {
            "branch": get_current_branch(repo_path),
            "commit": get_current_commit(repo_path)[:8],
            "changes": len(get_changed_files(repo_path, include_untracked=True))
        }
        
        # Add more detailed info about the current commit
        commit_details = get_commit_details(repo_path, "HEAD")
        status["current_commit"] = {
            "hash": commit_details.get("hash", "")[:8],
            "author": commit_details.get("author_name", ""),
            "date": commit_details.get("author_date", ""),
            "subject": commit_details.get("subject", "")
        }
        
        return status
    except GitError as e:
        logger.error(f"Error getting repository status: {str(e)}")
        return {
            "error": str(e),
            "branch": "unknown",
            "commit": "unknown",
            "changes": 0
        }