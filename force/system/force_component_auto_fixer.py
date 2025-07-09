#!/usr/bin/env python3
"""
Force Component Auto-Fixer
Automatically repairs legacy Force component files to match current schema format.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re

class ForceComponentAutoFixer:
    """Auto-fixer for Force component files to match current schema."""
    
    def __init__(self, force_dir: str = ".force"):
        self.force_dir = Path(force_dir)
        self.logger = logging.getLogger("ForceAutoFixer")
        
        # Track fixes applied
        self.fixes_applied = []
        self.files_modified = []
        
        # Common fixes patterns
        self.fix_patterns = {
            'tools': self._fix_tool_component,
            'patterns': self._fix_pattern_component,
            'constraints': self._fix_constraint_component,
            'governance': self._fix_governance_component
        }
    
    def auto_fix_all_components(self) -> Dict[str, Any]:
        """Auto-fix all invalid components in the Force directory."""
        self.logger.info("🔧 Starting auto-fix process for Force components...")
        
        results = {
            'success': True,
            'total_files_processed': 0,
            'files_fixed': 0,
            'fixes_applied': [],
            'failed_fixes': [],
            'backup_created': False
        }
        
        # Create backup before making changes
        backup_dir = self._create_backup()
        if backup_dir:
            results['backup_created'] = True
            results['backup_location'] = str(backup_dir)
            self.logger.info(f"📁 Backup created at: {backup_dir}")
        
        try:
            # Process each component type
            for component_type in ['tools', 'patterns', 'constraints', 'governance']:
                component_dir = self.force_dir / component_type
                if not component_dir.exists():
                    continue
                
                # Find all JSON files recursively
                json_files = list(component_dir.rglob("*.json"))
                results['total_files_processed'] += len(json_files)
                
                for json_file in json_files:
                    try:
                        fixed = self._fix_component_file(json_file, component_type)
                        if fixed:
                            results['files_fixed'] += 1
                            self.files_modified.append(str(json_file.relative_to(self.force_dir)))
                    except Exception as e:
                        self.logger.error(f"Failed to fix {json_file.name}: {e}")
                        results['failed_fixes'].append({
                            'file': str(json_file.relative_to(self.force_dir)),
                            'error': str(e)
                        })
            
            results['fixes_applied'] = self.fixes_applied
            results['files_modified'] = self.files_modified
            
            self.logger.info(f"✅ Auto-fix completed: {results['files_fixed']}/{results['total_files_processed']} files fixed")
            
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
            self.logger.error(f"❌ Auto-fix process failed: {e}")
        
        return results
    
    def _create_backup(self) -> Optional[Path]:
        """Create backup of the Force directory before making changes."""
        try:
            import shutil
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.force_dir.parent / f".force_backup_{timestamp}"
            shutil.copytree(self.force_dir, backup_dir)
            return backup_dir
        except Exception as e:
            self.logger.warning(f"Failed to create backup: {e}")
            return None
    
    def _fix_component_file(self, file_path: Path, component_type: str) -> bool:
        """Fix a single component file."""
        try:
            # Load the component
            with open(file_path, 'r', encoding='utf-8') as f:
                component_data = json.load(f)
            
            # Apply fixes based on component type
            if component_type in self.fix_patterns:
                original_data = json.dumps(component_data, sort_keys=True)
                fixed_data = self.fix_patterns[component_type](component_data, file_path)
                
                # Check if changes were made
                if json.dumps(fixed_data, sort_keys=True) != original_data:
                    # Save the fixed component
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(fixed_data, f, indent=2, ensure_ascii=False)
                    
                    self.logger.info(f"🔧 Fixed: {file_path.name}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error fixing {file_path.name}: {e}")
            raise
    
    def _fix_tool_component(self, data: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """Fix tool component to match current schema."""
        fixes_in_file = []
        
        # Fix missing required fields
        if 'parameters' not in data:
            data['parameters'] = {"required": [], "optional": []}
            fixes_in_file.append("Added missing parameters structure")
        
        # Fix old parameter format
        if 'parameters' in data and isinstance(data['parameters'], dict):
            old_params = data['parameters']
            if any(key not in ['required', 'optional'] for key in old_params.keys()):
                # Convert old format to new format
                data['parameters'] = self._convert_old_parameters(old_params)
                fixes_in_file.append("Converted old parameter format to new format")
            elif 'required' in old_params or 'optional' in old_params:
                # Fix parameter names in new format
                params_fixed = self._fix_parameter_names(old_params)
                if params_fixed:
                    data['parameters'] = old_params
                    fixes_in_file.append("Fixed parameter names to use snake_case format")
        
        # Fix execution section
        if 'execution' not in data:
            data['execution'] = {
                "strategy": "sequential",
                "commands": [{"action": "placeholder_action", "description": "Placeholder command"}],
                "validation": {"pre_conditions": [], "post_conditions": [], "error_handling": []}
            }
            fixes_in_file.append("Added missing execution structure")
        else:
            execution = data['execution']
            
            # Fix missing strategy
            if 'strategy' not in execution:
                execution['strategy'] = 'sequential'
                fixes_in_file.append("Added missing execution strategy")
            
            # Fix old command format
            if 'command' in execution and 'commands' not in execution:
                # Convert single command to commands array
                old_command = execution.pop('command')
                execution['commands'] = [{
                    "action": old_command,
                    "description": f"Execute {old_command}"
                }]
                fixes_in_file.append("Converted single command to commands array")
            
            # Ensure commands exist
            if 'commands' not in execution:
                execution['commands'] = [{"action": "placeholder_action", "description": "Placeholder command"}]
                fixes_in_file.append("Added missing commands array")
            
            # Fix validation structure
            if 'validation' not in execution:
                execution['validation'] = {"pre_conditions": [], "post_conditions": [], "error_handling": []}
                fixes_in_file.append("Added missing validation structure")
            elif isinstance(execution['validation'], dict):
                validation = execution['validation']
                # Move validation fields that are outside execution.validation
                if 'pre_conditions' in data and 'pre_conditions' not in validation:
                    validation['pre_conditions'] = data.pop('pre_conditions', [])
                    fixes_in_file.append("Moved pre_conditions to execution.validation")
                if 'post_conditions' in data and 'post_conditions' not in validation:
                    validation['post_conditions'] = data.pop('post_conditions', [])
                    fixes_in_file.append("Moved post_conditions to execution.validation")
                
                # Ensure all validation fields exist
                for field in ['pre_conditions', 'post_conditions', 'error_handling']:
                    if field not in validation:
                        validation[field] = []
                        fixes_in_file.append(f"Added missing validation.{field}")
        
        # Fix metadata section
        if 'metadata' not in data:
            data['metadata'] = {
                "created": datetime.now().isoformat() + "Z",
                "updated": datetime.now().isoformat() + "Z",
                "version": "1.0.0"
            }
            fixes_in_file.append("Added missing metadata structure")
        else:
            metadata = data['metadata']
            # Ensure required metadata fields
            if 'created' not in metadata:
                metadata['created'] = datetime.now().isoformat() + "Z"
                fixes_in_file.append("Added missing metadata.created")
            if 'updated' not in metadata:
                metadata['updated'] = datetime.now().isoformat() + "Z"
                fixes_in_file.append("Added missing metadata.updated")
            if 'version' not in metadata:
                metadata['version'] = "1.0.0"
                fixes_in_file.append("Added missing metadata.version")
        
        # Remove old schema fields that don't belong
        old_fields = ['inputSchema', 'outputSchema', 'implementation', 'executor', 'entryPoint', 'timeout']
        for field in old_fields:
            if field in data:
                data.pop(field)
                fixes_in_file.append(f"Removed legacy field: {field}")
        
        # Record fixes
        if fixes_in_file:
            self.fixes_applied.append({
                'file': str(file_path.relative_to(self.force_dir)),
                'type': 'tool',
                'fixes': fixes_in_file
            })
        
        return data
    
    def _fix_pattern_component(self, data: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """Fix pattern component to match current schema."""
        fixes_in_file = []
        
        # Remove $schema field if present
        if '$schema' in data:
            data.pop('$schema')
            fixes_in_file.append("Removed $schema field")
        
        # Ensure required fields exist
        required_fields = ['id', 'name', 'description', 'category', 'implementation', 'metadata']
        for field in required_fields:
            if field not in data:
                if field == 'implementation':
                    data[field] = {"steps": [], "examples": []}
                elif field == 'metadata':
                    data[field] = {
                        "created": datetime.now().isoformat() + "Z",
                        "updated": datetime.now().isoformat() + "Z",
                        "version": "1.0.0"
                    }
                else:
                    data[field] = f"Generated {field}"
                fixes_in_file.append(f"Added missing required field: {field}")
        
        # Fix implementation structure
        if 'implementation' in data:
            impl = data['implementation']
            if 'steps' not in impl:
                impl['steps'] = []
                fixes_in_file.append("Added missing implementation.steps")
            if 'examples' not in impl:
                impl['examples'] = []
                fixes_in_file.append("Added missing implementation.examples")
        
        # Record fixes
        if fixes_in_file:
            self.fixes_applied.append({
                'file': str(file_path.relative_to(self.force_dir)),
                'type': 'pattern',
                'fixes': fixes_in_file
            })
        
        return data
    
    def _fix_constraint_component(self, data: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """Fix constraint component to match current schema."""
        fixes_in_file = []
        
        # Ensure required fields exist
        required_fields = ['id', 'name', 'description', 'scope', 'enforcement', 'metadata']
        for field in required_fields:
            if field not in data:
                if field == 'scope':
                    data[field] = {"applies_to": ["**/*"], "excludes": []}
                elif field == 'enforcement':
                    data[field] = {"level": "warning", "trigger": "on_change"}
                elif field == 'metadata':
                    data[field] = {
                        "created": datetime.now().isoformat() + "Z",
                        "updated": datetime.now().isoformat() + "Z",
                        "version": "1.0.0"
                    }
                else:
                    data[field] = f"Generated {field}"
                fixes_in_file.append(f"Added missing required field: {field}")
        
        # Record fixes
        if fixes_in_file:
            self.fixes_applied.append({
                'file': str(file_path.relative_to(self.force_dir)),
                'type': 'constraint',
                'fixes': fixes_in_file
            })
        
        return data
    
    def _fix_governance_component(self, data: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """Fix governance component to match current schema."""
        fixes_in_file = []
        
        # Ensure required fields exist
        required_fields = ['id', 'timestamp', 'event_type', 'data', 'metadata']
        for field in required_fields:
            if field not in data:
                if field == 'timestamp':
                    data[field] = datetime.now().isoformat() + "Z"
                elif field == 'event_type':
                    data[field] = "policy_update"
                elif field == 'data':
                    data[field] = {}
                elif field == 'metadata':
                    data[field] = {
                        "created": datetime.now().isoformat() + "Z",
                        "updated": datetime.now().isoformat() + "Z",
                        "version": "1.0.0"
                    }
                else:
                    data[field] = f"Generated {field}"
                fixes_in_file.append(f"Added missing required field: {field}")
        
        # Record fixes
        if fixes_in_file:
            self.fixes_applied.append({
                'file': str(file_path.relative_to(self.force_dir)),
                'type': 'governance',
                'fixes': fixes_in_file
            })
        
        return data
    
    def _convert_old_parameters(self, old_params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert old parameter format to new required/optional format."""
        new_params = {"required": [], "optional": []}
        
        for param_name, param_def in old_params.items():
            if isinstance(param_def, dict):
                # Convert camelCase to snake_case
                snake_case_name = self._to_snake_case(param_name)
                
                param_obj = {
                    "name": snake_case_name,
                    "type": param_def.get("type", "string"),
                    "description": param_def.get("description", f"Parameter {snake_case_name}")
                }
                
                # Copy additional properties
                for key in ["default", "enum", "items", "minimum", "maximum"]:
                    if key in param_def:
                        param_obj[key] = param_def[key]
                
                # Determine if required
                if param_def.get("required", False) or "default" not in param_def:
                    new_params["required"].append(param_obj)
                else:
                    new_params["optional"].append(param_obj)
        
        return new_params
    
    def _fix_parameter_names(self, params: Dict[str, Any]) -> bool:
        """Fix parameter names to use snake_case format. Returns True if any changes were made."""
        changes_made = False
        
        for param_list_name in ['required', 'optional']:
            if param_list_name in params:
                for param in params[param_list_name]:
                    if isinstance(param, dict) and 'name' in param:
                        old_name = param['name']
                        new_name = self._to_snake_case(old_name)
                        if old_name != new_name:
                            param['name'] = new_name
                            changes_made = True
        
        return changes_made
    
    def _to_snake_case(self, name: str) -> str:
        """Convert camelCase or other formats to snake_case."""
        # Handle camelCase
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        # Handle numbers and remaining uppercase
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        # Remove any invalid characters and ensure it starts with a letter
        s3 = re.sub(r'[^a-z0-9_]', '_', s2)
        # Ensure it starts with a letter
        if s3 and not s3[0].isalpha():
            s3 = 'param_' + s3
        # Ensure it doesn't end with underscore
        s3 = s3.rstrip('_')
        # Ensure it's not empty
        if not s3:
            s3 = 'param'
        return s3


def main():
    """Main entry point for auto-fixer."""
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description="Force Component Auto-Fixer")
    parser.add_argument("force_dir", nargs='?', default=".force", 
                       help="Path to Force directory (default: .force)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be fixed without making changes")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create auto-fixer and run
    fixer = ForceComponentAutoFixer(args.force_dir)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        # TODO: Implement dry-run logic
        print("Dry-run functionality not yet implemented")
        return
    
    results = fixer.auto_fix_all_components()
    
    # Display results
    print("\n🔧 FORCE COMPONENT AUTO-FIX RESULTS")
    print("=" * 50)
    print(f"Total files processed: {results['total_files_processed']}")
    print(f"Files fixed: {results['files_fixed']}")
    print(f"Failed fixes: {len(results.get('failed_fixes', []))}")
    
    if results.get('backup_created'):
        print(f"Backup created: {results.get('backup_location')}")
    
    if results['fixes_applied']:
        print("\n📝 FIXES APPLIED:")
        for fix in results['fixes_applied']:
            print(f"  {fix['file']} ({fix['type']}):")
            for change in fix['fixes']:
                print(f"    • {change}")
    
    if results.get('failed_fixes'):
        print("\n❌ FAILED FIXES:")
        for fail in results['failed_fixes']:
            print(f"  {fail['file']}: {fail['error']}")


if __name__ == "__main__":
    main()
