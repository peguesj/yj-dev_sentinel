#!/usr/bin/env python3
"""
Force Component Fix System
Analyzes validation errors, groups components by similar issues, and provides 
batch fixing capabilities for maximum efficiency.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime
import argparse
import sys
from force_component_validator import ForceComponentValidator


class ForceComponentFixSystem:
    """Intelligent batch fixing system for Force components."""
    
    def __init__(self, force_root: Path):
        self.force_root = Path(force_root)
        self.validator = ForceComponentValidator(force_root)
        self.fix_groups = defaultdict(list)
        self.fix_templates = {}
        self.validation_results = None
        
    def analyze_validation_errors(self) -> Dict[str, Any]:
        """Analyze validation errors and group by fix patterns."""
        print("🔍 Analyzing validation errors for batch fixing opportunities...")
        
        # Run validation first
        self.validation_results = self.validator.validate_all()
        
        if not self.validation_results['success']:
            print(f"❌ Cannot analyze errors: {self.validation_results.get('error')}")
            return {}
        
        error_patterns = {
            'missing_fields': defaultdict(list),
            'invalid_types': defaultdict(list),
            'enum_violations': defaultdict(list),
            'pattern_violations': defaultdict(list),
            'semantic_errors': defaultdict(list)
        }
        
        # Analyze all component types
        for comp_type in ['tools', 'patterns', 'constraints']:
            for invalid_comp in self.validation_results[comp_type]['invalid']:
                self._categorize_errors(invalid_comp, error_patterns, comp_type)
        
        # Group by fix efficiency
        fix_groups = self._create_fix_groups(error_patterns)
        
        return {
            'error_patterns': error_patterns,
            'fix_groups': fix_groups,
            'efficiency_report': self._calculate_efficiency_metrics(fix_groups)
        }
    
    def _categorize_errors(self, component: Dict[str, Any], 
                          error_patterns: Dict[str, Any], comp_type: str) -> None:
        """Categorize individual component errors."""
        for error in component.get('detailed_errors', []):
            error_lower = error.lower()
            
            # Missing required fields
            if 'required property' in error_lower or 'missing' in error_lower:
                missing_field = self._extract_missing_field(error)
                if missing_field:
                    error_patterns['missing_fields'][missing_field].append({
                        'component': component,
                        'type': comp_type,
                        'error': error
                    })
            
            # Type mismatches
            elif 'not of type' in error_lower or 'wrong type' in error_lower:
                type_error = self._extract_type_error(error)
                if type_error:
                    error_patterns['invalid_types'][type_error].append({
                        'component': component,
                        'type': comp_type,
                        'error': error
                    })
            
            # Enum violations
            elif 'not one of' in error_lower or 'enum' in error_lower:
                enum_error = self._extract_enum_error(error)
                if enum_error:
                    error_patterns['enum_violations'][enum_error].append({
                        'component': component,
                        'type': comp_type,
                        'error': error
                    })
            
            # Pattern violations (regex)
            elif 'does not match' in error_lower or 'pattern' in error_lower:
                pattern_error = self._extract_pattern_error(error)
                if pattern_error:
                    error_patterns['pattern_violations'][pattern_error].append({
                        'component': component,
                        'type': comp_type,
                        'error': error
                    })
            
            # Semantic errors
            else:
                error_patterns['semantic_errors']['other'].append({
                    'component': component,
                    'type': comp_type,
                    'error': error
                })
    
    def _extract_missing_field(self, error: str) -> Optional[str]:
        """Extract missing field name from error message."""
        # Pattern: "'field_name' is a required property"
        match = re.search(r"'([^']+)' is a required property", error)
        if match:
            return match.group(1)
        
        # Pattern: "Path 'field_name': missing"
        match = re.search(r"Path '([^']+)'.*missing", error)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_type_error(self, error: str) -> Optional[str]:
        """Extract type error details."""
        # Pattern: "is not of type 'string'"
        match = re.search(r"not of type '([^']+)'", error)
        if match:
            return f"expected_{match.group(1)}"
        return None
    
    def _extract_enum_error(self, error: str) -> Optional[str]:
        """Extract enum violation details."""
        # Pattern: "'value' is not one of ['allowed1', 'allowed2']"
        match = re.search(r"'([^']+)' is not one of \[([^\]]+)\]", error)
        if match:
            field_value = match.group(1)
            allowed_values = match.group(2)
            return f"enum_violation_{field_value}_{len(allowed_values.split(','))}_options"
        return None
    
    def _extract_pattern_error(self, error: str) -> Optional[str]:
        """Extract pattern violation details."""
        if "snake_case" in error.lower() or "pattern" in error.lower():
            return "id_snake_case_pattern"
        return "pattern_violation"
    
    def _create_fix_groups(self, error_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Create fix groups ordered by efficiency."""
        fix_groups = {}
        
        # Group 1: Missing standard fields (high efficiency)
        standard_missing = {}
        for field, components in error_patterns['missing_fields'].items():
            if field in ['parameters', 'execution', 'metadata']:
                standard_missing[field] = components
        
        if standard_missing:
            fix_groups['missing_standard_fields'] = {
                'components': standard_missing,
                'fix_type': 'add_standard_structure',
                'efficiency': 'high',
                'estimated_time': len(sum(standard_missing.values(), [])) * 2,  # 2 min per component
                'description': 'Add missing standard field structures'
            }
        
        # Group 2: ID pattern violations (medium efficiency)
        id_pattern_components = error_patterns['pattern_violations'].get('id_snake_case_pattern', [])
        if id_pattern_components:
            fix_groups['id_pattern_fixes'] = {
                'components': id_pattern_components,
                'fix_type': 'convert_to_snake_case',
                'efficiency': 'medium',
                'estimated_time': len(id_pattern_components) * 1,  # 1 min per component
                'description': 'Convert IDs to snake_case format'
            }
        
        # Group 3: Category enum violations (high efficiency)
        category_violations = []
        for enum_key, components in error_patterns['enum_violations'].items():
            if 'category' in enum_key.lower():
                category_violations.extend(components)
        
        if category_violations:
            fix_groups['category_enum_fixes'] = {
                'components': category_violations,
                'fix_type': 'fix_category_enums',
                'efficiency': 'high',
                'estimated_time': len(category_violations) * 0.5,  # 30 sec per component
                'description': 'Fix category field enum violations'
            }
        
        # Group 4: Type mismatches (medium efficiency)
        type_fixes = {}
        for type_error, components in error_patterns['invalid_types'].items():
            type_fixes[type_error] = components
        
        if type_fixes:
            fix_groups['type_mismatches'] = {
                'components': type_fixes,
                'fix_type': 'fix_type_mismatches',
                'efficiency': 'medium',
                'estimated_time': len(sum(type_fixes.values(), [])) * 1.5,  # 1.5 min per component
                'description': 'Fix type mismatches'
            }
        
        # Group 5: Semantic errors (low efficiency - manual)
        semantic_errors = error_patterns['semantic_errors']
        if semantic_errors and semantic_errors.get('other'):
            fix_groups['semantic_errors'] = {
                'components': semantic_errors['other'],
                'fix_type': 'manual_review_required',
                'efficiency': 'low',
                'estimated_time': len(semantic_errors['other']) * 10,  # 10 min per component
                'description': 'Semantic errors requiring manual review'
            }
        
        return fix_groups
    
    def _calculate_efficiency_metrics(self, fix_groups: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate efficiency metrics for batch fixing."""
        total_components = 0
        total_time = 0
        efficiency_breakdown = {}
        
        for group_name, group_data in fix_groups.items():
            if isinstance(group_data['components'], dict):
                group_component_count = sum(len(comps) for comps in group_data['components'].values())
            else:
                group_component_count = len(group_data['components'])
            
            total_components += group_component_count
            total_time += group_data['estimated_time']
            
            efficiency_breakdown[group_name] = {
                'component_count': group_component_count,
                'estimated_time': group_data['estimated_time'],
                'efficiency': group_data['efficiency'],
                'time_per_component': group_data['estimated_time'] / max(group_component_count, 1)
            }
        
        return {
            'total_components_to_fix': total_components,
            'total_estimated_time_minutes': total_time,
            'average_time_per_component': total_time / max(total_components, 1),
            'efficiency_breakdown': efficiency_breakdown,
            'batch_efficiency_ratio': max(total_components, 1) / max(total_time / 60, 1)  # components per hour
        }
    
    def generate_fix_templates(self) -> Dict[str, Any]:
        """Generate fix templates for common issues."""
        return {
            'parameters_template': {
                "required": [],
                "optional": []
            },
            'execution_template': {
                "strategy": "sequential",
                "commands": [
                    {
                        "action": "placeholder_action",
                        "description": "Placeholder command description"
                    }
                ],
                "validation": {
                    "pre_conditions": ["Component is properly configured"],
                    "post_conditions": ["Component execution completed successfully"],
                    "error_handling": []
                }
            },
            'metadata_template': {
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
        }
    
    def apply_fixes(self, fix_groups: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
        """Apply fixes to components based on grouped errors."""
        if dry_run:
            print("🧪 DRY RUN MODE - No files will be modified")
        else:
            print("🔧 APPLYING FIXES - Files will be modified")
        
        fix_results = {
            'applied_fixes': [],
            'failed_fixes': [],
            'skipped_fixes': []
        }
        
        templates = self.generate_fix_templates()
        
        for group_name, group_data in fix_groups.items():
            print(f"\\n📦 Processing fix group: {group_name}")
            print(f"   Efficiency: {group_data['efficiency']}")
            print(f"   Estimated time: {group_data['estimated_time']} minutes")
            
            if group_data['fix_type'] == 'add_standard_structure':
                self._fix_missing_standard_fields(group_data, templates, dry_run, fix_results)
            elif group_data['fix_type'] == 'convert_to_snake_case':
                self._fix_id_patterns(group_data, dry_run, fix_results)
            elif group_data['fix_type'] == 'fix_category_enums':
                self._fix_category_enums(group_data, dry_run, fix_results)
            elif group_data['fix_type'] == 'fix_type_mismatches':
                self._fix_type_mismatches(group_data, dry_run, fix_results)
            elif group_data['fix_type'] == 'manual_review_required':
                self._handle_manual_fixes(group_data, fix_results)
        
        return fix_results
    
    def _fix_missing_standard_fields(self, group_data: Dict[str, Any], 
                                   templates: Dict[str, Any], dry_run: bool,
                                   fix_results: Dict[str, Any]) -> None:
        """Fix missing standard fields like parameters, execution, metadata."""
        for field_name, components in group_data['components'].items():
            print(f"  🔧 Fixing missing '{field_name}' field in {len(components)} components")
            
            for comp_info in components:
                component = comp_info['component']
                file_path = Path(component['path'])
                
                try:
                    if not dry_run:
                        # Load current component data
                        with open(file_path, 'r', encoding='utf-8') as f:
                            comp_data = json.load(f)
                        
                        # Add missing field with template
                        if field_name in templates:
                            comp_data[field_name] = templates[f"{field_name}_template"]
                        
                        # Save updated component
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(comp_data, f, indent=2, ensure_ascii=False)
                    
                    fix_results['applied_fixes'].append({
                        'file': component['file'],
                        'fix_type': f'added_{field_name}',
                        'description': f"Added missing {field_name} field"
                    })
                    print(f"    ✅ Fixed: {component['file']}")
                    
                except Exception as e:
                    fix_results['failed_fixes'].append({
                        'file': component['file'],
                        'error': str(e),
                        'fix_type': f'add_{field_name}'
                    })
                    print(f"    ❌ Failed: {component['file']} - {e}")
    
    def _fix_id_patterns(self, group_data: Dict[str, Any], dry_run: bool,
                        fix_results: Dict[str, Any]) -> None:
        """Fix ID pattern violations (convert to snake_case)."""
        components = group_data['components']
        print(f"  🔧 Converting {len(components)} component IDs to snake_case")
        
        for comp_info in components:
            component = comp_info['component']
            file_path = Path(component['path'])
            
            try:
                if not dry_run:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        comp_data = json.load(f)
                    
                    # Convert ID to snake_case
                    if 'id' in comp_data:
                        old_id = comp_data['id']
                        new_id = re.sub(r'[^a-z0-9_]', '_', old_id.lower())
                        new_id = re.sub(r'_+', '_', new_id)  # Remove multiple underscores
                        new_id = new_id.strip('_')  # Remove leading/trailing underscores
                        comp_data['id'] = new_id
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(comp_data, f, indent=2, ensure_ascii=False)
                
                fix_results['applied_fixes'].append({
                    'file': component['file'],
                    'fix_type': 'id_snake_case_conversion',
                    'description': f"Converted ID to snake_case format"
                })
                print(f"    ✅ Fixed: {component['file']}")
                
            except Exception as e:
                fix_results['failed_fixes'].append({
                    'file': component['file'],
                    'error': str(e),
                    'fix_type': 'id_pattern_fix'
                })
                print(f"    ❌ Failed: {component['file']} - {e}")
    
    def _fix_category_enums(self, group_data: Dict[str, Any], dry_run: bool,
                           fix_results: Dict[str, Any]) -> None:
        """Fix category enum violations."""
        components = group_data['components']
        print(f"  🔧 Fixing category enums in {len(components)} components")
        
        # Valid categories from schema
        valid_categories = ["git", "documentation", "analysis", "implementation", 
                          "testing", "deployment", "optimization", "validation"]
        
        category_mapping = {
            'security': 'validation',
            'quality_assurance': 'validation',
            'code_analysis': 'analysis',
            'project_management': 'implementation',
            'infrastructure': 'deployment'
        }
        
        for comp_info in components:
            component = comp_info['component']
            file_path = Path(component['path'])
            
            try:
                if not dry_run:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        comp_data = json.load(f)
                    
                    # Fix category
                    if 'category' in comp_data:
                        current_category = comp_data['category']
                        if current_category in category_mapping:
                            comp_data['category'] = category_mapping[current_category]
                        elif current_category not in valid_categories:
                            # Default mapping based on component type
                            comp_data['category'] = 'analysis'  # Safe default
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(comp_data, f, indent=2, ensure_ascii=False)
                
                fix_results['applied_fixes'].append({
                    'file': component['file'],
                    'fix_type': 'category_enum_fix',
                    'description': f"Fixed category enum violation"
                })
                print(f"    ✅ Fixed: {component['file']}")
                
            except Exception as e:
                fix_results['failed_fixes'].append({
                    'file': component['file'],
                    'error': str(e),
                    'fix_type': 'category_enum_fix'
                })
                print(f"    ❌ Failed: {component['file']} - {e}")
    
    def _fix_type_mismatches(self, group_data: Dict[str, Any], dry_run: bool,
                            fix_results: Dict[str, Any]) -> None:
        """Fix type mismatches."""
        for type_error, components in group_data['components'].items():
            print(f"  🔧 Fixing {type_error} in {len(components)} components")
            
            for comp_info in components:
                component = comp_info['component']
                # Type mismatches often require manual review
                fix_results['skipped_fixes'].append({
                    'file': component['file'],
                    'reason': 'Type mismatch requires manual review',
                    'fix_type': 'type_mismatch',
                    'error': type_error
                })
                print(f"    ⏭️  Skipped (manual review): {component['file']}")
    
    def _handle_manual_fixes(self, group_data: Dict[str, Any], 
                           fix_results: Dict[str, Any]) -> None:
        """Handle fixes that require manual review."""
        components = group_data['components']
        print(f"  📝 Marking {len(components)} components for manual review")
        
        for comp_info in components:
            component = comp_info['component']
            fix_results['skipped_fixes'].append({
                'file': component['file'],
                'reason': 'Requires manual review and fixing',
                'fix_type': 'manual_review',
                'error': comp_info['error']
            })
            print(f"    📝 Manual review: {component['file']}")
    
    def print_efficiency_report(self, analysis_results: Dict[str, Any]) -> None:
        """Print comprehensive efficiency report."""
        efficiency = analysis_results['efficiency_report']
        fix_groups = analysis_results['fix_groups']
        
        print(f"\\n📊 BATCH FIXING EFFICIENCY REPORT")
        print("=" * 80)
        print(f"Total components to fix: {efficiency['total_components_to_fix']}")
        print(f"Total estimated time: {efficiency['total_estimated_time_minutes']:.1f} minutes")
        print(f"Average time per component: {efficiency['average_time_per_component']:.1f} minutes")
        print(f"Batch efficiency: {efficiency['batch_efficiency_ratio']:.1f} components/hour")
        print()
        
        print("🎯 FIX GROUPS (ordered by efficiency):")
        for i, (group_name, breakdown) in enumerate(efficiency['efficiency_breakdown'].items(), 1):
            group_data = fix_groups[group_name]
            print(f"  {i}. {group_name.replace('_', ' ').title()}")
            print(f"     Components: {breakdown['component_count']}")
            print(f"     Time: {breakdown['estimated_time']:.1f} min")
            print(f"     Efficiency: {breakdown['efficiency']}")
            print(f"     Description: {group_data['description']}")
            print()


def main():
    """Main entry point for the fix system."""
    parser = argparse.ArgumentParser(description="Force Component Fix System")
    parser.add_argument("--force-root", default=".force", help="Force root directory")
    parser.add_argument("--analyze", action="store_true", help="Analyze errors and show fix groups")
    parser.add_argument("--fix", action="store_true", help="Apply fixes to components")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without applying")
    parser.add_argument("--groups", nargs="+", help="Specific fix groups to apply")
    
    args = parser.parse_args()
    
    fix_system = ForceComponentFixSystem(Path(args.force_root))
    
    print("🔧 FORCE COMPONENT FIX SYSTEM")
    print("=" * 60)
    
    # Always analyze first
    analysis_results = fix_system.analyze_validation_errors()
    
    if not analysis_results:
        print("❌ No analysis results available")
        sys.exit(1)
    
    # Print efficiency report
    fix_system.print_efficiency_report(analysis_results)
    
    if args.analyze:
        print("\\n✅ Analysis complete. Use --fix to apply fixes or --dry-run to preview.")
        return
    
    if args.fix or args.dry_run:
        fix_groups = analysis_results['fix_groups']
        
        # Filter groups if specified
        if args.groups:
            fix_groups = {k: v for k, v in fix_groups.items() if k in args.groups}
        
        if not fix_groups:
            print("\\n⚠️  No fix groups to process.")
            return
        
        # Apply fixes
        fix_results = fix_system.apply_fixes(fix_groups, dry_run=args.dry_run)
        
        # Print results
        print(f"\\n📊 FIX RESULTS:")
        print(f"✅ Applied: {len(fix_results['applied_fixes'])}")
        print(f"❌ Failed: {len(fix_results['failed_fixes'])}")
        print(f"⏭️  Skipped: {len(fix_results['skipped_fixes'])}")
        
        if fix_results['failed_fixes']:
            print(f"\\n❌ FAILED FIXES:")
            for failed in fix_results['failed_fixes']:
                print(f"  • {failed['file']}: {failed['error']}")
        
        if fix_results['skipped_fixes']:
            print(f"\\n⏭️  SKIPPED (Manual Review Required):")
            for skipped in fix_results['skipped_fixes']:
                print(f"  • {skipped['file']}: {skipped['reason']}")


if __name__ == "__main__":
    main()
