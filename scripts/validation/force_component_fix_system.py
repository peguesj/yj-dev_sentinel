#!/usr/bin/env python3
"""
Force Component Fix System
Analyzes Force components, groups by validation errors, and provides batch fixing capabilities.
Designed to efficiently fix multiple components with similar issues.
"""

import json
import jsonschema
from jsonschema import validate, ValidationError
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import re
from typing import Dict, List, Any, Tuple, Optional

class ComponentFixSystem:
    """Comprehensive system for analyzing and fixing Force component validation errors."""
    
    def __init__(self, force_dir: str = "/Users/jeremiah/Developer/dev_sentinel/.force"):
        self.force_dir = Path(force_dir)
        self.schema_file = self.force_dir / "schemas" / "force-schema.json"
        self.tools_dir = self.force_dir / "tools"
        self.patterns_dir = self.force_dir / "patterns"
        self.constraints_dir = self.force_dir / "constraints"
        self.governance_dir = self.force_dir / "governance"
        
        self.schema = self._load_schema()
        self.component_types = {
            'tools': {'dir': self.tools_dir, 'schema_key': 'ToolDefinition'},
            'patterns': {'dir': self.patterns_dir, 'schema_key': 'Pattern'},
            'constraints': {'dir': self.constraints_dir, 'schema_key': 'Constraint'},
            'governance': {'dir': self.governance_dir, 'schema_key': 'LearningRecord'}
        }
        
    def _load_schema(self) -> Dict[str, Any]:
        """Load the Force schema."""
        with open(self.schema_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_component(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load a component JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return None
    
    def _save_component(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """Save a component JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving {file_path}: {e}")
            return False
    
    def _validate_component(self, data: Dict[str, Any], schema_key: str) -> Tuple[bool, List[str]]:
        """Validate a component against its schema and return validation errors."""
        try:
            component_schema = self.schema['definitions'][schema_key]
            validate(instance=data, schema=component_schema, 
                    resolver=jsonschema.RefResolver.from_schema(self.schema))
            return True, []
        except ValidationError as e:
            return False, [self._format_validation_error(e)]
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]
    
    def _format_validation_error(self, error: ValidationError) -> str:
        """Format validation error into a standardized string."""
        path = ' -> '.join(str(x) for x in error.absolute_path)
        if not path:
            path = "root"
        return f"{path}: {error.message}"
    
    def _categorize_error(self, error: str) -> str:
        """Categorize validation errors for grouping."""
        error_lower = error.lower()
        
        if "required property" in error_lower:
            return "missing_required_fields"
        elif "does not match" in error_lower and "pattern" in error_lower:
            return "invalid_id_pattern"
        elif "is not one of" in error_lower:
            return "invalid_enum_value"
        elif "format" in error_lower:
            return "invalid_format"
        elif "minimum" in error_lower or "maximum" in error_lower:
            return "value_out_of_range"
        elif "minlength" in error_lower or "maxlength" in error_lower:
            return "invalid_length"
        elif "type" in error_lower:
            return "invalid_type"
        else:
            return "other_validation_error"
    
    def analyze_all_components(self) -> Dict[str, Any]:
        """Analyze all Force components and group validation errors."""
        print("🔍 ANALYZING ALL FORCE COMPONENTS")
        print("=" * 60)
        
        analysis = {
            'summary': {
                'total_components': 0,
                'valid_components': 0,
                'invalid_components': 0,
                'component_types': {}
            },
            'error_groups': defaultdict(list),
            'component_details': {},
            'fix_suggestions': {}
        }
        
        for comp_type, config in self.component_types.items():
            if not config['dir'].exists():
                continue
                
            print(f"\n📁 Analyzing {comp_type}...")
            type_stats = {'total': 0, 'valid': 0, 'invalid': 0}
            
            for json_file in config['dir'].glob("*.json"):
                if json_file.name.startswith('__'):
                    continue
                    
                component_data = self._load_component(json_file)
                if not component_data:
                    continue
                
                type_stats['total'] += 1
                analysis['summary']['total_components'] += 1
                
                is_valid, errors = self._validate_component(component_data, config['schema_key'])
                
                component_info = {
                    'file': str(json_file),
                    'type': comp_type,
                    'schema_key': config['schema_key'],
                    'valid': is_valid,
                    'errors': errors,
                    'data': component_data
                }
                
                analysis['component_details'][str(json_file)] = component_info
                
                if is_valid:
                    type_stats['valid'] += 1
                    analysis['summary']['valid_components'] += 1
                    print(f"  ✅ {json_file.name}")
                else:
                    type_stats['invalid'] += 1
                    analysis['summary']['invalid_components'] += 1
                    print(f"  ❌ {json_file.name}: {len(errors)} error(s)")
                    
                    # Group errors by category
                    for error in errors:
                        error_category = self._categorize_error(error)
                        analysis['error_groups'][error_category].append({
                            'file': str(json_file),
                            'type': comp_type,
                            'error': error,
                            'data': component_data
                        })
            
            analysis['summary']['component_types'][comp_type] = type_stats
            print(f"  📊 {comp_type}: {type_stats['valid']}/{type_stats['total']} valid")
        
        # Generate fix suggestions
        analysis['fix_suggestions'] = self._generate_fix_suggestions(analysis['error_groups'])
        
        return analysis
    
    def _generate_fix_suggestions(self, error_groups: Dict[str, List]) -> Dict[str, Any]:
        """Generate suggestions for fixing grouped errors."""
        suggestions = {}
        
        for error_category, errors in error_groups.items():
            if error_category == "missing_required_fields":
                suggestions[error_category] = self._suggest_missing_fields_fix(errors)
            elif error_category == "invalid_id_pattern":
                suggestions[error_category] = self._suggest_id_pattern_fix(errors)
            elif error_category == "invalid_enum_value":
                suggestions[error_category] = self._suggest_enum_fix(errors)
            elif error_category == "invalid_format":
                suggestions[error_category] = self._suggest_format_fix(errors)
            else:
                suggestions[error_category] = {
                    'count': len(errors),
                    'files': [e['file'] for e in errors],
                    'fix_strategy': 'manual_review_required'
                }
        
        return suggestions
    
    def _suggest_missing_fields_fix(self, errors: List[Dict]) -> Dict[str, Any]:
        """Suggest fixes for missing required fields."""
        field_counts = defaultdict(list)
        
        for error in errors:
            # Extract field name from error message
            if "required property" in error['error']:
                field_match = re.search(r"'([^']+)' is a required property", error['error'])
                if field_match:
                    field_name = field_match.group(1)
                    field_counts[field_name].append(error)
        
        return {
            'count': len(errors),
            'fix_strategy': 'batch_add_missing_fields',
            'missing_fields': {field: len(files) for field, files in field_counts.items()},
            'field_details': field_counts,
            'batch_fixable': True
        }
    
    def _suggest_id_pattern_fix(self, errors: List[Dict]) -> Dict[str, Any]:
        """Suggest fixes for invalid ID patterns."""
        return {
            'count': len(errors),
            'fix_strategy': 'normalize_ids',
            'files': [e['file'] for e in errors],
            'pattern_required': '^[a-z][a-z0-9_]*[a-z0-9]$',
            'batch_fixable': True
        }
    
    def _suggest_enum_fix(self, errors: List[Dict]) -> Dict[str, Any]:
        """Suggest fixes for invalid enum values."""
        enum_issues = defaultdict(list)
        
        for error in errors:
            if "is not one of" in error['error']:
                enum_issues['category_fixes'].append(error)
        
        return {
            'count': len(errors),
            'fix_strategy': 'map_to_valid_enums',
            'enum_issues': enum_issues,
            'batch_fixable': True
        }
    
    def _suggest_format_fix(self, errors: List[Dict]) -> Dict[str, Any]:
        """Suggest fixes for format validation errors."""
        return {
            'count': len(errors),
            'fix_strategy': 'standardize_formats',
            'files': [e['file'] for e in errors],
            'batch_fixable': True
        }
    
    def generate_missing_fields_template(self, component_type: str, schema_key: str) -> Dict[str, Any]:
        """Generate a template for missing fields based on schema."""
        schema_def = self.schema['definitions'][schema_key]
        template = {}
        
        for field in schema_def.get('required', []):
            field_schema = schema_def['properties'].get(field, {})
            
            if field == 'parameters':
                template[field] = {
                    "required": [],
                    "optional": []
                }
            elif field == 'execution':
                template[field] = {
                    "strategy": "sequential",
                    "commands": [
                        {
                            "action": "placeholder_action",
                            "description": "Placeholder command description"
                        }
                    ],
                    "validation": {
                        "pre_conditions": [],
                        "post_conditions": [],
                        "error_handling": []
                    }
                }
            elif field == 'metadata':
                template[field] = {
                    "created": datetime.now().isoformat() + "Z",
                    "updated": datetime.now().isoformat() + "Z",
                    "version": "1.0.0",
                    "complexity": "medium",
                    "tags": [],
                    "dependencies": [],
                    "performance_metrics": {
                        "avg_execution_time": 0.0,
                        "success_rate": 0.0,
                        "usage_count": 0
                    }
                }
            elif field == 'context' and component_type == 'patterns':
                template[field] = {
                    "when_to_use": "Describe when to use this pattern",
                    "benefits": ["List", "key", "benefits"],
                    "trade_offs": ["List", "any", "trade_offs"]
                }
            elif field == 'implementation' and component_type == 'patterns':
                template[field] = {
                    "steps": ["Step 1", "Step 2", "Step 3"],
                    "examples": [{}]
                }
            elif field == 'enforcement' and component_type == 'constraints':
                template[field] = {
                    "level": "warning",
                    "validation_rules": ["Validation rule description"]
                }
            else:
                # Use schema default or generate based on type
                if 'default' in field_schema:
                    template[field] = field_schema['default']
                elif field_schema.get('type') == 'string':
                    template[field] = f"Generated {field}"
                elif field_schema.get('type') == 'array':
                    template[field] = []
                elif field_schema.get('type') == 'object':
                    template[field] = {}
                else:
                    template[field] = None
        
        return template
    
    def fix_id_pattern(self, component_id: str) -> str:
        """Fix ID to match required pattern: ^[a-z][a-z0-9_]*[a-z0-9]$"""
        # Convert to lowercase
        fixed_id = component_id.lower()
        
        # Replace hyphens with underscores
        fixed_id = fixed_id.replace('-', '_')
        
        # Remove invalid characters
        fixed_id = re.sub(r'[^a-z0-9_]', '', fixed_id)
        
        # Ensure starts with letter
        if fixed_id and not fixed_id[0].isalpha():
            fixed_id = 'tool_' + fixed_id
        
        # Ensure ends with alphanumeric
        if fixed_id and fixed_id[-1] == '_':
            fixed_id = fixed_id.rstrip('_') + '1'
        
        # Ensure minimum length
        if not fixed_id:
            fixed_id = 'component_1'
        
        return fixed_id
    
    def batch_fix_components(self, analysis: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
        """Apply batch fixes to components based on analysis."""
        print("\n🔧 BATCH FIXING FORCE COMPONENTS")
        print("=" * 60)
        
        if dry_run:
            print("🔍 DRY RUN MODE - No files will be modified")
        
        fix_results = {
            'total_fixes_attempted': 0,
            'successful_fixes': 0,
            'failed_fixes': 0,
            'fixes_by_category': {},
            'fixed_files': [],
            'failed_files': []
        }
        
        for error_category, suggestion in analysis['fix_suggestions'].items():
            if not suggestion.get('batch_fixable', False):
                continue
            
            print(f"\n📋 Fixing {error_category} ({suggestion['count']} components)")
            category_results = self._apply_category_fixes(error_category, suggestion, analysis, dry_run)
            fix_results['fixes_by_category'][error_category] = category_results
            
            fix_results['total_fixes_attempted'] += category_results['attempted']
            fix_results['successful_fixes'] += category_results['successful']
            fix_results['failed_fixes'] += category_results['failed']
            fix_results['fixed_files'].extend(category_results['fixed_files'])
            fix_results['failed_files'].extend(category_results['failed_files'])
        
        return fix_results
    
    def _apply_category_fixes(self, category: str, suggestion: Dict[str, Any], 
                            analysis: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Apply fixes for a specific error category."""
        results = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'fixed_files': [],
            'failed_files': []
        }
        
        if category == "missing_required_fields":
            results.update(self._fix_missing_fields(suggestion, analysis, dry_run))
        elif category == "invalid_id_pattern":
            results.update(self._fix_id_patterns(suggestion, analysis, dry_run))
        elif category == "invalid_enum_value":
            results.update(self._fix_enum_values(suggestion, analysis, dry_run))
        
        return results
    
    def _fix_missing_fields(self, suggestion: Dict[str, Any], analysis: Dict[str, Any], 
                          dry_run: bool) -> Dict[str, Any]:
        """Fix missing required fields in components."""
        results = {'attempted': 0, 'successful': 0, 'failed': 0, 'fixed_files': [], 'failed_files': []}
        
        for field_name, error_list in suggestion['field_details'].items():
            print(f"  🔧 Adding missing field '{field_name}' to {len(error_list)} components")
            
            for error_info in error_list:
                results['attempted'] += 1
                file_path = Path(error_info['file'])
                component_data = error_info['data'].copy()
                
                # Determine component type and generate template
                comp_type = error_info['type']
                schema_key = None
                for ct, config in self.component_types.items():
                    if ct == comp_type:
                        schema_key = config['schema_key']
                        break
                
                if not schema_key:
                    results['failed'] += 1
                    results['failed_files'].append(str(file_path))
                    continue
                
                # Generate template for missing field
                template = self.generate_missing_fields_template(comp_type, schema_key)
                
                if field_name in template:
                    component_data[field_name] = template[field_name]
                    
                    print(f"    ✅ {file_path.name}: Added {field_name}")
                    
                    if not dry_run:
                        if self._save_component(file_path, component_data):
                            results['successful'] += 1
                            results['fixed_files'].append(str(file_path))
                        else:
                            results['failed'] += 1
                            results['failed_files'].append(str(file_path))
                    else:
                        results['successful'] += 1
                        results['fixed_files'].append(str(file_path))
                else:
                    print(f"    ❌ {file_path.name}: No template for {field_name}")
                    results['failed'] += 1
                    results['failed_files'].append(str(file_path))
        
        return results
    
    def _fix_id_patterns(self, suggestion: Dict[str, Any], analysis: Dict[str, Any], 
                        dry_run: bool) -> Dict[str, Any]:
        """Fix invalid ID patterns in components."""
        results = {'attempted': 0, 'successful': 0, 'failed': 0, 'fixed_files': [], 'failed_files': []}
        
        for file_path in suggestion['files']:
            results['attempted'] += 1
            path_obj = Path(file_path)
            
            component_info = analysis['component_details'][file_path]
            component_data = component_info['data'].copy()
            
            if 'id' in component_data:
                old_id = component_data['id']
                new_id = self.fix_id_pattern(old_id)
                component_data['id'] = new_id
                
                print(f"  🔧 {path_obj.name}: '{old_id}' → '{new_id}'")
                
                if not dry_run:
                    if self._save_component(path_obj, component_data):
                        results['successful'] += 1
                        results['fixed_files'].append(file_path)
                    else:
                        results['failed'] += 1
                        results['failed_files'].append(file_path)
                else:
                    results['successful'] += 1
                    results['fixed_files'].append(file_path)
            else:
                results['failed'] += 1
                results['failed_files'].append(file_path)
        
        return results
    
    def _fix_enum_values(self, suggestion: Dict[str, Any], analysis: Dict[str, Any], 
                        dry_run: bool) -> Dict[str, Any]:
        """Fix invalid enum values in components."""
        results = {'attempted': 0, 'successful': 0, 'failed': 0, 'fixed_files': [], 'failed_files': []}
        
        # Common category mappings
        category_mappings = {
            'security': 'validation',
            'quality_assurance': 'validation',
            'code_analysis': 'analysis',
            'project_management': 'implementation',
            'build': 'deployment',
            'utility': 'optimization'
        }
        
        for error_info in suggestion.get('enum_issues', {}).get('category_fixes', []):
            results['attempted'] += 1
            file_path = Path(error_info['file'])
            component_data = error_info['data'].copy()
            
            if 'category' in component_data:
                old_category = component_data['category']
                new_category = category_mappings.get(old_category, 'analysis')
                component_data['category'] = new_category
                
                print(f"  🔧 {file_path.name}: category '{old_category}' → '{new_category}'")
                
                if not dry_run:
                    if self._save_component(file_path, component_data):
                        results['successful'] += 1
                        results['fixed_files'].append(str(file_path))
                    else:
                        results['failed'] += 1
                        results['failed_files'].append(str(file_path))
                else:
                    results['successful'] += 1
                    results['fixed_files'].append(str(file_path))
            else:
                results['failed'] += 1
                results['failed_files'].append(str(file_path))
        
        return results
    
    def generate_fix_report(self, analysis: Dict[str, Any], fix_results: Optional[Dict[str, Any]] = None) -> str:
        """Generate a comprehensive fix report."""
        report = []
        report.append("🔧 FORCE COMPONENT FIX SYSTEM REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        # Summary
        summary = analysis['summary']
        report.append("📊 COMPONENT ANALYSIS SUMMARY")
        report.append("-" * 30)
        report.append(f"Total components: {summary['total_components']}")
        report.append(f"Valid components: {summary['valid_components']}")
        report.append(f"Invalid components: {summary['invalid_components']}")
        report.append(f"Validation success rate: {summary['valid_components']/summary['total_components']*100:.1f}%")
        report.append("")
        
        # By component type
        report.append("📁 BY COMPONENT TYPE")
        report.append("-" * 20)
        for comp_type, stats in summary['component_types'].items():
            success_rate = stats['valid']/stats['total']*100 if stats['total'] > 0 else 0
            report.append(f"{comp_type:12} {stats['valid']:3}/{stats['total']:3} ({success_rate:5.1f}%)")
        report.append("")
        
        # Error groups
        report.append("❌ ERROR ANALYSIS")
        report.append("-" * 18)
        error_groups = analysis['error_groups']
        for category, errors in sorted(error_groups.items(), key=lambda x: len(x[1]), reverse=True):
            report.append(f"{category:25} {len(errors):3} components affected")
            suggestion = analysis['fix_suggestions'].get(category, {})
            if suggestion.get('batch_fixable'):
                report.append(f"{'':25} ✅ Batch fixable")
            else:
                report.append(f"{'':25} ⚠️  Manual review required")
        report.append("")
        
        # Fix suggestions
        report.append("💡 FIX SUGGESTIONS")
        report.append("-" * 17)
        for category, suggestion in analysis['fix_suggestions'].items():
            report.append(f"\n🔧 {category}")
            report.append(f"   Components affected: {suggestion['count']}")
            report.append(f"   Fix strategy: {suggestion['fix_strategy']}")
            report.append(f"   Batch fixable: {'Yes' if suggestion.get('batch_fixable') else 'No'}")
            
            if category == "missing_required_fields":
                report.append("   Missing fields:")
                for field, count in suggestion['missing_fields'].items():
                    report.append(f"     - {field}: {count} components")
        
        # Fix results if provided
        if fix_results:
            report.append("")
            report.append("🎯 FIX EXECUTION RESULTS")
            report.append("-" * 24)
            report.append(f"Total fixes attempted: {fix_results['total_fixes_attempted']}")
            report.append(f"Successful fixes: {fix_results['successful_fixes']}")
            report.append(f"Failed fixes: {fix_results['failed_fixes']}")
            if fix_results['total_fixes_attempted'] > 0:
                success_rate = fix_results['successful_fixes']/fix_results['total_fixes_attempted']*100
                report.append(f"Fix success rate: {success_rate:.1f}%")
            
            report.append("\nBy category:")
            for category, results in fix_results['fixes_by_category'].items():
                report.append(f"  {category}: {results['successful']}/{results['attempted']} successful")
        
        return "\n".join(report)

def main():
    """Main execution function for the fix system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Force Component Fix System")
    parser.add_argument("--dry-run", action="store_true", help="Analyze only, don't modify files")
    parser.add_argument("--fix", action="store_true", help="Apply fixes after analysis")
    parser.add_argument("--report-only", action="store_true", help="Generate report only")
    parser.add_argument("--output", type=str, help="Output file for report")
    
    args = parser.parse_args()
    
    fix_system = ComponentFixSystem()
    
    # Always run analysis
    print("🚀 Starting Force Component Analysis...")
    analysis = fix_system.analyze_all_components()
    
    fix_results = None
    
    # Apply fixes if requested
    if args.fix and not args.report_only:
        dry_run = args.dry_run
        print(f"\n🔧 Applying fixes (dry_run={dry_run})...")
        fix_results = fix_system.batch_fix_components(analysis, dry_run=dry_run)
    
    # Generate report
    report = fix_system.generate_fix_report(analysis, fix_results)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {args.output}")
    else:
        print("\n" + report)
    
    # Summary
    invalid_count = analysis['summary']['invalid_components']
    if invalid_count > 0:
        print(f"\n⚠️  {invalid_count} components need attention")
        if fix_results and fix_results['successful_fixes'] > 0:
            remaining = invalid_count - fix_results['successful_fixes']
            print(f"✅ {fix_results['successful_fixes']} components fixed")
            if remaining > 0:
                print(f"⚠️  {remaining} components still need manual attention")
    else:
        print("\n🎉 All components are valid!")

if __name__ == "__main__":
    main()
