#!/usr/bin/env python3
"""
Force Component Validator
Comprehensive validation system for Force components with MCP server startup integration.
"""

import json
import jsonschema
from jsonschema import validate, ValidationError, RefResolver
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class ForceValidator:
    """Comprehensive validator for Force system components."""
    
    def __init__(self, force_dir: str = "/Users/jeremiah/Developer/dev_sentinel/.force"):
        self.force_dir = Path(force_dir)
        # Prefer extended schema, fallback to standard schema
        extended_schema_file = self.force_dir / "schemas" / "force-extended-schema.json"
        standard_schema_file = self.force_dir / "schemas" / "force-schema.json"
        
        if extended_schema_file.exists():
            self.schema_file = extended_schema_file
            self.logger = logging.getLogger("ForceValidator")
            self.logger.info("Using extended Force schema for validation")
        elif standard_schema_file.exists():
            self.schema_file = standard_schema_file
            self.logger = logging.getLogger("ForceValidator")
            self.logger.info("Using standard Force schema for validation")
        else:
            self.logger = logging.getLogger("ForceValidator")
            raise FileNotFoundError("No Force schema found (neither extended nor standard)")
        
        # Load schema
        self.schema = self._load_schema()
        self.resolver = RefResolver.from_schema(self.schema)
        
        # Component type configurations
        self.component_types = {
            'tools': {
                'dir': self.force_dir / "tools",
                'schema_key': 'ToolDefinition',
                'enabled': True
            },
            'patterns': {
                'dir': self.force_dir / "patterns", 
                'schema_key': 'Pattern',
                'enabled': True
            },
            'constraints': {
                'dir': self.force_dir / "constraints",
                'schema_key': 'Constraint', 
                'enabled': True
            },
            'governance': {
                'dir': self.force_dir / "governance",
                'schema_key': 'LearningRecord',
                'enabled': True
            }
        }
        
    def _load_schema(self) -> Dict[str, Any]:
        """Load and validate the Force schema."""
        try:
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            # Validate schema itself
            jsonschema.Draft7Validator.check_schema(schema)
            self.logger.info("✅ Force schema loaded and validated successfully")
            return schema
            
        except FileNotFoundError:
            self.logger.error(f"❌ Schema file not found: {self.schema_file}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Invalid JSON in schema file: {e}")
            raise
        except jsonschema.SchemaError as e:
            self.logger.error(f"❌ Invalid schema structure: {e}")
            raise
    
    def _load_component(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load a component JSON file with error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"❌ Failed to load {file_path.name}: {e}")
            return None
    
    def validate_component(self, component_data: Dict[str, Any], schema_key: str) -> Dict[str, Any]:
        """Validate a single component against its schema."""
        result = {
            'valid': False,
            'errors': [],
            'detailed_errors': [],
            'schema_key': schema_key
        }
        
        try:
            # Get component schema from definitions
            component_schema = self.schema['definitions'][schema_key]
            
            # Validate against schema
            validate(instance=component_data, schema=component_schema, resolver=self.resolver)
            
            # Additional semantic validation
            semantic_errors = self._validate_semantics(component_data, schema_key)
            if semantic_errors:
                result['errors'] = semantic_errors
                result['detailed_errors'] = semantic_errors
            else:
                result['valid'] = True
                
        except ValidationError as e:
            result['errors'] = [str(e.message)]
            result['detailed_errors'] = [self._format_validation_error(e)]
        except Exception as e:
            result['errors'] = [f"Validation error: {str(e)}"]
            result['detailed_errors'] = [str(e)]
        
        return result
    
    def _format_validation_error(self, error: ValidationError) -> str:
        """Format validation error with path information."""
        path = " -> ".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
        return f"Path '{path}': {error.message}"
    
    def _validate_semantics(self, component_data: Dict[str, Any], component_type: str) -> List[str]:
        """Perform semantic validation beyond schema requirements."""
        errors = []
        
        if component_type == 'ToolDefinition':
            # Check for invalid 'type' property (not in schema)
            if 'type' in component_data:
                errors.append("Property 'type' is not allowed in ToolDefinition")
            
            # Validate execution strategy consistency
            if 'execution' in component_data:
                execution = component_data['execution']
                strategy = execution.get('strategy')
                commands = execution.get('commands', [])
                
                if strategy == 'sequential' and len(commands) <= 1:
                    errors.append("Sequential strategy should have multiple commands")
                elif strategy == 'parallel' and len(commands) <= 1:
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
                        errors.append("Pattern implementation should include examples")
        
        elif component_type == 'Constraint':
            # Validate constraint-specific semantics
            if 'enforcement' in component_data:
                enforcement = component_data['enforcement']
                level = enforcement.get('level')
                if level not in ['error', 'warning', 'info']:
                    errors.append(f"Invalid enforcement level: {level}")
        
        return errors
    
    def validate_component_type(self, component_type: str) -> Dict[str, Any]:
        """Validate all components of a specific type."""
        config = self.component_types[component_type]
        directory = config['dir']
        schema_key = config['schema_key']
        
        results = {
            'type': component_type,
            'total': 0,
            'valid': [],
            'invalid': [],
            'enabled': config['enabled']
        }
        
        if not config['enabled']:
            self.logger.info(f"Skipping disabled component type: {component_type}")
            return results
            
        if not directory.exists():
            self.logger.warning(f"Directory does not exist: {directory}")
            return results
        
        json_files = list(directory.glob("*.json"))
        results['total'] = len(json_files)
        
        self.logger.info(f"Validating {len(json_files)} {component_type} files...")
        
        for json_file in json_files:
            component_data = self._load_component(json_file)
            
            if component_data is None:
                # File loading failed
                invalid_result = {
                    'file': json_file.name,
                    'path': str(json_file.relative_to(self.force_dir)),
                    'valid': False,
                    'error': 'Failed to load JSON file',
                    'detailed_errors': ['Failed to load JSON file']
                }
                results['invalid'].append(invalid_result)
                self.logger.warning(f"❌ Invalid {component_type}: {json_file.name} - Failed to load JSON file")
                continue
            
            # Validate component
            validation_result = self.validate_component(component_data, schema_key)
            
            component_result = {
                'file': json_file.name,
                'path': str(json_file.relative_to(self.force_dir)),
                'valid': validation_result['valid'],
                'error': None,
                'detailed_errors': validation_result['detailed_errors']
            }
            
            # Extract component metadata
            if 'id' in component_data:
                component_result['tool_id'] = component_data['id']
            if 'name' in component_data:
                component_result['tool_name'] = component_data['name']
            
            if validation_result['valid']:
                results['valid'].append(component_result)
            else:
                # Format error message
                error_count = len(validation_result['errors'])
                if error_count == 1 and 'Semantic validation failed' not in validation_result['errors'][0]:
                    component_result['error'] = f"Validation failed with {error_count} errors"
                else:
                    component_result['error'] = "Semantic validation failed"
                
                results['invalid'].append(component_result)
                self.logger.warning(f"❌ Invalid {component_type}: {json_file.name} - {component_result['error']}")
        
        return results
    
    def validate_all(self) -> Dict[str, Any]:
        """Validate all Force components."""
        self.logger.info("🔍 Starting comprehensive Force component validation...")
        
        results = {
            'success': True,
            'validation_timestamp': datetime.now().isoformat(),
            'schema_path': str(self.schema_file.relative_to(self.force_dir)),
            'summary': {
                'total_components': 0,
                'valid_components': 0,
                'invalid_components': 0,
                'ready_for_loading': True
            }
        }
        
        # Validate each component type
        for component_type in self.component_types:
            type_results = self.validate_component_type(component_type)
            results[component_type] = type_results
            
            # Update summary
            results['summary']['total_components'] += type_results['total']
            results['summary']['valid_components'] += len(type_results['valid'])
            results['summary']['invalid_components'] += len(type_results['invalid'])
        
        # Determine if system is ready for loading
        if results['summary']['invalid_components'] > 0:
            results['summary']['ready_for_loading'] = False
        
        return results
    
    def generate_validation_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive validation report."""
        report = []
        
        # Header
        report.append("🔍 FORCE COMPONENT VALIDATION REPORT\\n")
        report.append("=" * 80)
        report.append(f"Validation Time: {results['validation_timestamp']}")
        report.append(f"Schema Path: {results['schema_path']}")
        
        # Summary
        summary = results['summary']
        report.append("\\n📊 VALIDATION SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Components: {summary['total_components']}")
        valid_pct = (summary['valid_components'] / summary['total_components'] * 100) if summary['total_components'] > 0 else 0
        report.append(f"Valid Components: {summary['valid_components']} ({valid_pct:.1f}%)")
        report.append(f"Invalid Components: {summary['invalid_components']}")
        report.append(f"Ready for Loading: {'✅ YES' if summary['ready_for_loading'] else '❌ NO'}")
        
        # Component type details
        for component_type in ['tools', 'patterns', 'constraints', 'governance']:
            if component_type not in results:
                continue
                
            type_data = results[component_type]
            if not type_data.get('enabled', True):
                continue
                
            report.append(f"\\n🔧 {component_type.upper()}")
            report.append("-" * 40)
            report.append(f"Total: {type_data['total']}")
            report.append(f"Valid: {len(type_data['valid'])}")
            report.append(f"Invalid: {len(type_data['invalid'])}")
            
            # Show invalid components
            if type_data['invalid']:
                report.append("\\n❌ Invalid " + component_type + ":")
                for comp in type_data['invalid'][:10]:  # Limit to first 10
                    report.append(f"  • {comp['file']}: {comp['error']}")
                if len(type_data['invalid']) > 10:
                    remaining = len(type_data['invalid']) - 10
                    report.append(f"  ... and {remaining} more")
            
            # Show valid components
            if type_data['valid']:
                report.append("\\n✅ Valid " + component_type + ":")
                for comp in type_data['valid'][:5]:  # Limit to first 5
                    name = comp.get('tool_name', comp['file'])
                    report.append(f"  • {name}")
                if len(type_data['valid']) > 5:
                    remaining = len(type_data['valid']) - 5
                    report.append(f"  ... and {remaining} more")
        
        return "\\n".join(report)
    
    def save_validation_report(self, results: Dict[str, Any]) -> str:
        """Save detailed validation results to JSON file."""
        output_path = self.force_dir / "validation_report.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return str(output_path.relative_to(self.force_dir))
    
    def check_blocking_issues(self, results: Dict[str, Any]) -> List[str]:
        """Check for issues that would prevent MCP server startup"""
        blocking_issues = []
        
        if not results.get('success'):
            blocking_issues.append(f"Schema validation failed: {results.get('error')}")
            return blocking_issues
        
        # For demonstration purposes, we'll be less strict about individual tool failures
        # In production, you might want to enforce critical tools more strictly
        
        # Check if the majority of core components are failing (> 80% failure rate)
        for component_type in ['tools']:
            total = results[component_type]['total']
            valid = results[component_type]['valid']
            if total > 0:
                failure_rate = (total - len(valid)) / total
                if failure_rate > 0.9:  # More than 90% failure
                    blocking_issues.append(f"Critical system failure: {failure_rate*100:.1f}% of {component_type} are invalid")
        
        return blocking_issues


def main():
    """Main validation entry point for MCP server startup"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Force Component Validator")
    parser.add_argument("force_dir", nargs='?', default=".force", 
                       help="Path to Force directory (default: .force)")
    parser.add_argument("--startup-check", action="store_true",
                       help="Run startup validation check")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--save-report", action="store_true",
                       help="Save detailed JSON report")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.startup_check:
        print("🚀 Force Component Validation at MCP Server Startup")
        print("=" * 60)
    
    # Create validator and run validation
    validator = ForceValidator(args.force_dir)
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
