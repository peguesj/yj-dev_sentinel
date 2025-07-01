"""
System-level Force tools for managing Force components and configuration.
Includes startup validation and batch fixing capabilities.
"""

import os
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

from force.tools import BaseToolExecutor

class ForceStartupValidator:
    """Handles Force component validation and fixing at system startup."""
    
    @staticmethod
    def run_validation_and_fix(force_root: str = ".force", auto_fix: bool = True) -> bool:
        """Run validation and optional auto-fix at startup."""
        try:
            # Run validation first
            validation_success = ForceStartupValidator._run_validation(force_root)
            
            if not validation_success and auto_fix:
                print("🔧 Validation failed, attempting automatic fixes...")
                fix_success = ForceStartupValidator._run_auto_fix(force_root)
                if fix_success:
                    # Re-run validation after fixes
                    print("🔍 Re-validating after fixes...")
                    validation_success = ForceStartupValidator._run_validation(force_root)
                else:
                    print("❌ Auto-fix failed, manual intervention required")
                    return False
            
            return validation_success
            
        except Exception as e:
            print(f"❌ Error during startup validation: {e}")
            return False
    
    @staticmethod
    def _run_validation(force_root: str) -> bool:
        """Run Force component validation."""
        try:
            cmd = [
                sys.executable,
                "force/tools/force_component_validator.py",
                force_root,
                "--startup-check"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Log output for debugging
            if result.stdout:
                print(f"Validation output:\n{result.stdout}")
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running validation: {e}")
            return False
    
    @staticmethod
    def _run_auto_fix(force_root: str) -> bool:
        """Run automatic fixing of Force components."""
        try:
            cmd = [
                sys.executable,
                "force/tools/force_component_fix_system.py",
                "--force-root", force_root,
                "--fix"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Log output for debugging
            if result.stdout:
                print(f"Auto-fix output:\n{result.stdout}")
            
            return result.returncode in [0, 1]  # 0 = success, 1 = partial success
            
        except Exception as e:
            print(f"❌ Error running auto-fix: {e}")
            return False

class ForceSyncTool(BaseToolExecutor):
    """Tool for synchronizing Force components between default and project directories."""
    
    tool_id = "force_sync"
    tool_category = "system"
    tool_name = "Force Component Sync"
    tool_description = "Synchronize Force components between default and project directories, including pattern-to-tool conversion"

    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the Force sync tool."""
        if context is None:
            context = {}
            
        direction = parameters.get("direction", "default-to-project")
        components = parameters.get("components", [])
        convert_pattern_tools = parameters.get("convertPatternTools", False)
        update_existing = parameters.get("updateExisting", True)
        dry_run = parameters.get("dryRun", False)

        # Define source and target directories
        if direction == "default-to-project":
            source_dir = Path("./force")
            target_dir = Path("./.force")
        else:  # project-to-default
            source_dir = Path("./.force")
            target_dir = Path("./force")

        # Default to all components if none specified
        if not components:
            components = ["tools", "patterns", "constraints", "governance"]

        sync_results = []

        for component in components:
            source_path = source_dir / component
            target_path = target_dir / component

            if not source_path.exists():
                sync_results.append({
                    "component": component,
                    "status": "skipped",
                    "reason": f"Source directory {source_path} does not exist"
                })
                continue

            if dry_run:
                # Just report what would be synced
                files_to_sync = []
                if source_path.is_dir():
                    for file_path in source_path.rglob("*"):
                        if file_path.is_file():
                            files_to_sync.append(str(file_path.relative_to(source_path)))

                sync_results.append({
                    "component": component,
                    "status": "would_sync",
                    "files": files_to_sync,
                    "count": len(files_to_sync)
                })
            else:
                try:
                    # Handle pattern-to-tool conversion if requested
                    if convert_pattern_tools and component == "patterns":
                        pattern_results = self._convert_pattern_tools(source_path, target_dir / "tools", update_existing)
                        sync_results.extend(pattern_results)
                    
                    # Perform regular sync
                    if target_path.exists():
                        shutil.rmtree(target_path)

                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(source_path, target_path)

                    # Count synced files
                    synced_files = len(list(target_path.rglob("*"))) if target_path.is_dir() else 1

                    sync_results.append({
                        "component": component,
                        "status": "synced",
                        "files_synced": synced_files
                    })
                except Exception as e:
                    sync_results.append({
                        "component": component,
                        "status": "error",
                        "error": str(e)
                    })

        return {
            "success": True,
            "direction": direction,
            "dry_run": dry_run,
            "results": sync_results
        }

    def _convert_pattern_tools(self, patterns_dir: Path, tools_dir: Path, update_existing: bool) -> List[Dict[str, Any]]:
        """Convert tools found in patterns to individual tool JSON files."""
        results = []
        tools_dir.mkdir(parents=True, exist_ok=True)

        # Track processed tools to avoid duplicates
        processed_tools = set()

        for pattern_file in patterns_dir.glob("*.json"):
            try:
                with open(pattern_file) as f:
                    pattern_data = json.load(f)

                # Skip if not a pattern definition
                if not isinstance(pattern_data, dict) or pattern_data.get("type") != "pattern":
                    continue

                # Process tools from implementation steps
                implementation = pattern_data.get("implementation", {})
                steps = implementation.get("steps", [])

                for step in steps:
                    tool_id = step.get("toolId")
                    if not tool_id or tool_id in processed_tools:
                        continue

                    # Create tool definition
                    tool_def = {
                        "id": tool_id,
                        "name": step.get("name", tool_id.replace("_", " ").title()),
                        "category": pattern_data.get("category", "workflow"),
                        "description": step.get("description", ""),
                        "parameters": step.get("parameters", {}),
                        "execution": {
                            "strategy": "sequential",
                            "commands": step.get("commands", []),
                            "validation": step.get("validation", {})
                        },
                        "metadata": {
                            "created": pattern_data.get("metadata", {}).get("created"),
                            "updated": pattern_data.get("metadata", {}).get("updated"),
                            "version": "1.0.0",
                            "complexity": "medium",
                            "tags": pattern_data.get("metadata", {}).get("tags", []),
                            "source_pattern": pattern_data.get("id")
                        }
                    }

                    tool_file = tools_dir / f"{tool_id}.json"
                    
                    # Handle existing tool files
                    if tool_file.exists() and update_existing:
                        with open(tool_file) as f:
                            existing_tool = json.load(f)
                            current_version = existing_tool.get("metadata", {}).get("version", "1.0.0")
                            # Increment version
                            version_parts = current_version.split('.')
                            if len(version_parts) == 3:
                                try:
                                    patch = int(version_parts[2]) + 1
                                    new_version = f"{version_parts[0]}.{version_parts[1]}.{patch}"
                                    tool_def["metadata"]["version"] = new_version
                                except ValueError:
                                    tool_def["metadata"]["version"] = "1.0.1"
                            else:
                                tool_def["metadata"]["version"] = "1.0.1"

                    # Write tool definition
                    with open(tool_file, 'w') as f:
                        json.dump(tool_def, f, indent=4)

                    processed_tools.add(tool_id)
                    results.append({
                        "component": "tools",
                        "status": "converted",
                        "source_pattern": pattern_data.get("id"),
                        "tool_id": tool_id,
                        "file": str(tool_file)
                    })

            except Exception as e:
                results.append({
                    "component": "tools",
                    "status": "error",
                    "source": str(pattern_file),
                    "error": str(e)
                })

        return results
