#!/usr/bin/env python3
"""
Force Tool Validation System
Comprehensive validation system for Force tools that runs at MCP server startup.
Validates all Force components (tools, patterns, constraints) against schemas.
"""

import json
import jsonschema
from jsonschema import validate, ValidationError, Draft7Validator
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import logging

class ForceComponentValidator:
    """Comprehensive validation for Force components"""
    
    def __init__(self, force_root: Path):
        self.force_root = Path(force_root)
        self.schema_path = self.force_root / "schemas" / "force-schema.json"
        self.tools_path = self.force_root / "tools"
        self.patterns_path = self.force_root / "patterns"
        self.constraints_path = self.force_root / "constraints"
        
        self.schema = None
        self.validation_results = {
            'tools': {'valid': [], 'invalid': []},
            'patterns': {'valid': [], 'invalid': []},
            'constraints': {'valid': [], 'invalid': []},
            'summary': {}
        }
        
        # Setup logging
        self.logger = logging.getLogger('ForceValidator')
        
    def load_schema(self) -> bool:
        """Load and validate the Force schema itself"""
        try:
            if not self.schema_path.exists():
                self.logger.error(f"Force schema not found at {self.schema_path}")
                return False
                
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
            
            # Validate schema structure
            required_definitions = ['ToolDefinition', 'Pattern', 'Constraint', 'Parameter', 'Command', 'ErrorHandler']
            missing_defs = [d for d in required_definitions if d not in self.schema.get('definitions', {})]
            
            if missing_defs:
                self.logger.error(f"Schema missing required definitions: {missing_defs}")
                return False
                
            self.logger.info("✅ Force schema loaded and validated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load Force schema: {e}")
            return False
    
    def validate_component(self, component_data: Dict[str, Any], component_type: str, 
                          file_path: Path) -> Tuple[bool, Optional[str], List[str]]:
        """Validate a single Force component against its schema definition"""
        try:
            if not self.schema:
                return False, "Schema not loaded", ["Schema not loaded - call load_schema() first"]
            
            if component_type not in self.schema.get('definitions', {}):
                return False, f"Unknown component type: {component_type}", [f"Component type '{component_type}' not found in schema"]
            
            schema_def = self.schema['definitions'][component_type]
            
            # Create validator with resolver for $ref handling
            resolver = jsonschema.RefResolver.from_schema(self.schema)
            validator = Draft7Validator(schema_def, resolver=resolver)
            
            errors = []
            validation_errors = []
            
            # Collect all validation errors
            for error in validator.iter_errors(component_data):
                validation_errors.append(error)
                error_path = " -> ".join(str(x) for x in error.absolute_path) if error.absolute_path else "root"
                errors.append(f"Path '{error_path}': {error.message}")
            
            if validation_errors:
                return False, f"Validation failed with {len(validation_errors)} errors", errors
            
            # Additional semantic validation
            semantic_errors = self._perform_semantic_validation(component_data, component_type)
            if semantic_errors:
                return False, "Semantic validation failed", semantic_errors
                
            return True, None, []
            
        except Exception as e:
            return False, f"Validation error: {str(e)}", [str(e)]
    
    def _perform_semantic_validation(self, component_data: Dict[str, Any], 
                                   component_type: str) -> List[str]:
        """Perform additional semantic validation beyond schema"""
        errors = []
        
        if component_type == 'ToolDefinition':
            # Validate tool-specific semantics
            if 'execution' in component_data:
                execution = component_data['execution']
                
                # Check if strategy matches commands structure
                strategy = execution.get('strategy', '')
                commands = execution.get('commands', [])
                
                if strategy == 'sequential' and len(commands) < 2:
                    errors.append("Sequential strategy should have multiple commands")
                
                if strategy == 'parallel' and len(commands) < 2:
                    errors.append("Parallel strategy should have multiple commands")
                
                # Validate command dependencies for conditional/iterative strategies
                if strategy in ['conditional', 'iterative']:
                    for cmd in commands:
                        if 'condition' not in cmd and strategy == 'conditional':
                            errors.append(f"Conditional strategy requires 'condition' in command: {cmd.get('action', 'unknown')}")
            
            # Validate metadata consistency
            if 'metadata' in component_data:
                metadata = component_data['metadata']
                created = metadata.get('created')
                updated = metadata.get('updated')
                
                if created and updated:
                    try:
                        created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                        updated_dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                        if updated_dt < created_dt:
                            errors.append("Updated timestamp cannot be before created timestamp")
                    except ValueError as e:
                        errors.append(f"Invalid timestamp format: {e}")
        
        elif component_type == 'Pattern':
            # Validate pattern-specific semantics
            if 'implementation' in component_data:
                impl = component_data['implementation']
                if 'steps' in impl and 'examples' in impl:
                    if len(impl['steps']) == 0:
                        errors.append("Pattern implementation must have at least one step")
                    if len(impl['examples']) == 0:
                        errors.append("Pattern implementation must have at least one example")
        
        return errors
    
    def validate_tools(self) -> Dict[str, Any]:
        """Validate all Force tools"""
        if not self.tools_path.exists():
            self.logger.warning(f"Tools directory not found: {self.tools_path}")
            return {'valid': [], 'invalid': [], 'total': 0}
        
        tool_files = list(self.tools_path.glob("*.json"))
        results = {'valid': [], 'invalid': [], 'total': len(tool_files)}
        
        self.logger.info(f"Validating {len(tool_files)} tool files...")
        
        for tool_file in tool_files:
            try:
                with open(tool_file, 'r', encoding='utf-8') as f:
                    tool_data = json.load(f)
                
                is_valid, error_msg, detailed_errors = self.validate_component(
                    tool_data, 'ToolDefinition', tool_file
                )
                
                result = {
                    'file': tool_file.name,
                    'path': str(tool_file),
                    'valid': is_valid,
                    'error': error_msg,
                    'detailed_errors': detailed_errors,
                    'tool_id': tool_data.get('id', 'unknown'),
                    'tool_name': tool_data.get('name', 'unknown')
                }
                
                if is_valid:
                    results['valid'].append(result)
                    self.logger.debug(f"✅ Valid tool: {tool_file.name}")
                else:
                    results['invalid'].append(result)
                    self.logger.warning(f"❌ Invalid tool: {tool_file.name} - {error_msg}")
                    
            except Exception as e:
                result = {
                    'file': tool_file.name,
                    'path': str(tool_file),
                    'valid': False,
                    'error': f"Failed to load: {str(e)}",
                    'detailed_errors': [str(e)],
                    'tool_id': 'unknown',
                    'tool_name': 'unknown'
                }
                results['invalid'].append(result)
                self.logger.error(f"❌ Failed to load tool: {tool_file.name} - {e}")
        
        return results
    
    def validate_patterns(self) -> Dict[str, Any]:
        """Validate all Force patterns"""
        if not self.patterns_path.exists():
            self.logger.warning(f"Patterns directory not found: {self.patterns_path}")
            return {'valid': [], 'invalid': [], 'total': 0}
        
        pattern_files = list(self.patterns_path.glob("*.json"))
        results = {'valid': [], 'invalid': [], 'total': len(pattern_files)}
        
        self.logger.info(f"Validating {len(pattern_files)} pattern files...")
        
        for pattern_file in pattern_files:
            try:
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    pattern_data = json.load(f)
                
                is_valid, error_msg, detailed_errors = self.validate_component(
                    pattern_data, 'Pattern', pattern_file
                )
                
                result = {
                    'file': pattern_file.name,
                    'path': str(pattern_file),
                    'valid': is_valid,
                    'error': error_msg,
                    'detailed_errors': detailed_errors,
                    'pattern_id': pattern_data.get('id', 'unknown'),
                    'pattern_name': pattern_data.get('name', 'unknown')
                }
                
                if is_valid:
                    results['valid'].append(result)
                    self.logger.debug(f"✅ Valid pattern: {pattern_file.name}")
                else:
                    results['invalid'].append(result)
                    self.logger.warning(f"❌ Invalid pattern: {pattern_file.name} - {error_msg}")
                    
            except Exception as e:
                result = {
                    'file': pattern_file.name,
                    'path': str(pattern_file),
                    'valid': False,
                    'error': f"Failed to load: {str(e)}",
                    'detailed_errors': [str(e)],
                    'pattern_id': 'unknown',
                    'pattern_name': 'unknown'
                }
                results['invalid'].append(result)
                self.logger.error(f"❌ Failed to load pattern: {pattern_file.name} - {e}")
        
        return results
    
    def validate_constraints(self) -> Dict[str, Any]:
        """Validate all Force constraints"""
        if not self.constraints_path.exists():
            self.logger.warning(f"Constraints directory not found: {self.constraints_path}")
            return {'valid': [], 'invalid': [], 'total': 0}
        
        constraint_files = list(self.constraints_path.glob("*.json"))
        results = {'valid': [], 'invalid': [], 'total': len(constraint_files)}
        
        self.logger.info(f"Validating {len(constraint_files)} constraint files...")
        
        for constraint_file in constraint_files:
            try:
                with open(constraint_file, 'r', encoding='utf-8') as f:
                    constraint_data = json.load(f)
                
                is_valid, error_msg, detailed_errors = self.validate_component(
                    constraint_data, 'Constraint', constraint_file
                )
                
                result = {
                    'file': constraint_file.name,
                    'path': str(constraint_file),
                    'valid': is_valid,
                    'error': error_msg,
                    'detailed_errors': detailed_errors,
                    'constraint_id': constraint_data.get('id', 'unknown'),
                    'constraint_type': constraint_data.get('type', 'unknown')
                }
                
                if is_valid:
                    results['valid'].append(result)
                    self.logger.debug(f"✅ Valid constraint: {constraint_file.name}")
                else:
                    results['invalid'].append(result)
                    self.logger.warning(f"❌ Invalid constraint: {constraint_file.name} - {error_msg}")
                    
            except Exception as e:
                result = {
                    'file': constraint_file.name,
                    'path': str(constraint_file),
                    'valid': False,
                    'error': f"Failed to load: {str(e)}",
                    'detailed_errors': [str(e)],
                    'constraint_id': 'unknown',
                    'constraint_type': 'unknown'
                }
                results['invalid'].append(result)
                self.logger.error(f"❌ Failed to load constraint: {constraint_file.name} - {e}")
        
        return results
    
    def validate_all(self) -> Dict[str, Any]:
        """Validate all Force components and return comprehensive results"""
        if not self.load_schema():
            return {
                'success': False,
                'error': 'Failed to load Force schema',
                'tools': {'valid': [], 'invalid': [], 'total': 0},
                'patterns': {'valid': [], 'invalid': [], 'total': 0},
                'constraints': {'valid': [], 'invalid': [], 'total': 0}
            }
        
        self.logger.info("🔍 Starting comprehensive Force component validation...")
        
        # Validate all component types
        tools_results = self.validate_tools()
        patterns_results = self.validate_patterns()
        constraints_results = self.validate_constraints()
        
        # Calculate summary statistics
        total_components = tools_results['total'] + patterns_results['total'] + constraints_results['total']
        total_valid = len(tools_results['valid']) + len(patterns_results['valid']) + len(constraints_results['valid'])
        total_invalid = len(tools_results['invalid']) + len(patterns_results['invalid']) + len(constraints_results['invalid'])
        
        success_rate = (total_valid / total_components * 100) if total_components > 0 else 0
        
        results = {
            'success': True,
            'validation_timestamp': datetime.now().isoformat(),
            'tools': tools_results,
            'patterns': patterns_results,
            'constraints': constraints_results,
            'summary': {
                'total_components': total_components,
                'total_valid': total_valid,
                'total_invalid': total_invalid,
                'success_rate': success_rate,
                'ready_for_loading': total_invalid == 0
            }
        }
        
        self.validation_results = results
        return results
    
    def generate_validation_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive validation report"""
        if not results.get('success'):
            return f"❌ Validation failed: {results.get('error', 'Unknown error')}"
        
        report = []
        report.append("🔍 FORCE COMPONENT VALIDATION REPORT")
        report.append("=" * 80)
        report.append(f"Validation Time: {results['validation_timestamp']}")
        report.append(f"Schema Path: {self.schema_path}")
        report.append("")
        
        # Summary
        summary = results['summary']
        report.append("📊 VALIDATION SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Components: {summary['total_components']}")
        report.append(f"Valid Components: {summary['total_valid']} ({summary['success_rate']:.1f}%)")
        report.append(f"Invalid Components: {summary['total_invalid']}")
        report.append(f"Ready for Loading: {'✅ YES' if summary['ready_for_loading'] else '❌ NO'}")
        report.append("")
        
        # Component-wise breakdown
        for component_type in ['tools', 'patterns', 'constraints']:
            component_results = results[component_type]
            if component_results['total'] == 0:
                continue
                
            report.append(f"🔧 {component_type.upper()}")
            report.append("-" * 40)
            report.append(f"Total: {component_results['total']}")
            report.append(f"Valid: {len(component_results['valid'])}")
            report.append(f"Invalid: {len(component_results['invalid'])}")
            
            # Show invalid components with errors
            if component_results['invalid']:
                report.append(f"\n❌ Invalid {component_type}:")
                for item in component_results['invalid'][:10]:  # Show first 10
                    report.append(f"  • {item['file']}: {item['error']}")
                if len(component_results['invalid']) > 10:
                    report.append(f"  ... and {len(component_results['invalid']) - 10} more")
            
            # Show valid components
            if component_results['valid']:
                report.append(f"\n✅ Valid {component_type}:")
                for item in component_results['valid'][:5]:  # Show first 5
                    name = item.get(f'{component_type[:-1]}_name', item['file'])
                    report.append(f"  • {name}")
                if len(component_results['valid']) > 5:
                    report.append(f"  ... and {len(component_results['valid']) - 5} more")
            
            report.append("")
        
        return "\\n".join(report)
    
    def save_validation_report(self, results: Dict[str, Any], output_path: Optional[Path] = None) -> Path:
        """Save validation results to a JSON file for programmatic access"""
        if output_path is None:
            output_path = self.force_root / "validation_report.json"
        
        # Create a clean version for saving (remove logger references, etc.)
        clean_results = json.loads(json.dumps(results, default=str))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(clean_results, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def check_blocking_issues(self, results: Dict[str, Any]) -> List[str]:
        """Check for issues that would prevent MCP server startup"""
        blocking_issues = []
        
        if not results.get('success'):
            blocking_issues.append(f"Schema validation failed: {results.get('error')}")
            return blocking_issues
        
        # Check for critical component failures
        for component_type in ['tools', 'patterns', 'constraints']:
            invalid_components = results[component_type]['invalid']
            for component in invalid_components:
                # Critical tools that must be valid
                if component_type == 'tools':
                    critical_tools = ['force_sync', 'validate_components', 'list_tools']
                    tool_id = component.get('tool_id', '')
                    if tool_id in critical_tools:
                        blocking_issues.append(f"Critical tool '{tool_id}' is invalid: {component['error']}")
        
        return blocking_issues


def main():
    """Main validation entry point for MCP server startup"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Determine Force root path
    if len(sys.argv) > 1:
        force_root = Path(sys.argv[1])
    else:
        # Auto-detect from current working directory
        current_dir = Path.cwd()
        if (current_dir / ".force").exists():
            force_root = current_dir / ".force"
        else:
            print("❌ Could not find .force directory. Please specify path.")
            sys.exit(1)
    
    validator = ForceComponentValidator(force_root)
    
    print("🚀 Force Component Validation at MCP Server Startup")
    print("=" * 60)
    
    # Run validation
    results = validator.validate_all()
    
    # Generate and display report
    report = validator.generate_validation_report(results)
    print(report)
    
    # Save detailed results
    report_path = validator.save_validation_report(results)
    print(f"\\n📄 Detailed report saved to: {report_path}")
    
    # Check for blocking issues
    blocking_issues = validator.check_blocking_issues(results)
    if blocking_issues:
        print("\\n🚨 BLOCKING ISSUES DETECTED:")
        for issue in blocking_issues:
            print(f"  • {issue}")
        print("\\n❌ MCP server startup should be BLOCKED until these issues are resolved.")
        sys.exit(1)
    
    if not results['summary']['ready_for_loading']:
        print("\\n⚠️  Some components are invalid but not blocking MCP startup.")
        print("Consider fixing invalid components to ensure full Force functionality.")
    else:
        print("\\n✅ All Force components are valid. MCP server can proceed with startup.")
    
    return results


if __name__ == "__main__":
    main()
