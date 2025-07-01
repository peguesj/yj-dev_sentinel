#!/usr/bin/env python3
"""
Force MCP Integration
Integrates Force component validation into MCP server startup process.
This script should be called before loading Force tools into the MCP server.
"""

import sys
import os
from pathlib import Path
import logging
from typing import Dict, Any, Tuple

# Add the force tools directory to the path so we can import the validator
sys.path.insert(0, str(Path(__file__).parent))

try:
    from force_component_validator import ForceComponentValidator
except ImportError:
    print("❌ Could not import ForceComponentValidator. Please check the installation.")
    sys.exit(1)

class ForceMCPIntegration:
    """Integration layer between Force validation and MCP server"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.force_root = self.project_root / ".force"
        self.validator = ForceComponentValidator(self.force_root)
        
        # Setup logging for MCP integration
        self.logger = logging.getLogger('ForceMCP')
        
    def validate_for_mcp_startup(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate Force components for MCP server startup.
        Returns (can_start, validation_results)
        """
        self.logger.info("🔍 Running Force validation for MCP server startup...")
        
        # Check if Force is properly set up
        if not self.force_root.exists():
            self.logger.warning("⚠️  .force directory not found - Force system disabled")
            return True, {"force_enabled": False, "reason": "No .force directory"}
        
        # Run comprehensive validation
        results = self.validator.validate_all()
        
        if not results.get('success'):
            self.logger.error(f"❌ Force validation failed: {results.get('error')}")
            return False, results
        
        # Check for blocking issues
        blocking_issues = self.validator.check_blocking_issues(results)
        
        if blocking_issues:
            self.logger.error("🚨 Blocking issues detected:")
            for issue in blocking_issues:
                self.logger.error(f"  • {issue}")
            return False, results
        
        # Report validation summary
        summary = results['summary']
        self.logger.info(f"✅ Force validation completed:")
        self.logger.info(f"  • Total components: {summary['total_components']}")
        self.logger.info(f"  • Valid: {summary['total_valid']} ({summary['success_rate']:.1f}%)")
        self.logger.info(f"  • Invalid: {summary['total_invalid']}")
        
        if summary['total_invalid'] > 0:
            self.logger.warning(f"⚠️  {summary['total_invalid']} invalid components found (non-blocking)")
        
        return True, results
    
    def get_valid_tools_for_loading(self, validation_results: Dict[str, Any]) -> list:
        """Get list of valid Force tools that can be safely loaded into MCP"""
        if not validation_results.get('success'):
            return []
        
        valid_tools = []
        for tool in validation_results['tools']['valid']:
            valid_tools.append({
                'id': tool['tool_id'],
                'name': tool['tool_name'],
                'file_path': tool['path'],
                'validated': True
            })
        
        return valid_tools
    
    def get_valid_patterns_for_loading(self, validation_results: Dict[str, Any]) -> list:
        """Get list of valid Force patterns that can be safely loaded"""
        if not validation_results.get('success'):
            return []
        
        valid_patterns = []
        for pattern in validation_results['patterns']['valid']:
            valid_patterns.append({
                'id': pattern['pattern_id'],
                'name': pattern['pattern_name'],
                'file_path': pattern['path'],
                'validated': True
            })
        
        return valid_patterns
    
    def get_valid_constraints_for_loading(self, validation_results: Dict[str, Any]) -> list:
        """Get list of valid Force constraints that can be safely loaded"""
        if not validation_results.get('success'):
            return []
        
        valid_constraints = []
        for constraint in validation_results['constraints']['valid']:
            valid_constraints.append({
                'id': constraint['constraint_id'],
                'type': constraint['constraint_type'],
                'file_path': constraint['path'],
                'validated': True
            })
        
        return valid_constraints
    
    def generate_mcp_startup_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate a startup report suitable for MCP server logs"""
        if not validation_results.get('success'):
            return f"❌ Force validation failed: {validation_results.get('error', 'Unknown error')}"
        
        summary = validation_results['summary']
        report_lines = [
            "🚀 FORCE MCP INTEGRATION REPORT",
            "=" * 50,
            f"Validation Time: {validation_results['validation_timestamp']}",
            f"Force Root: {self.force_root}",
            "",
            "📊 Component Summary:",
            f"  • Tools: {len(validation_results['tools']['valid'])}/{validation_results['tools']['total']} valid",
            f"  • Patterns: {len(validation_results['patterns']['valid'])}/{validation_results['patterns']['total']} valid", 
            f"  • Constraints: {len(validation_results['constraints']['valid'])}/{validation_results['constraints']['total']} valid",
            "",
            f"Overall Success Rate: {summary['success_rate']:.1f}%",
            f"Ready for Loading: {'✅ YES' if summary['ready_for_loading'] else '⚠️  PARTIAL'}"
        ]
        
        # Add information about what will be loaded
        valid_tools = self.get_valid_tools_for_loading(validation_results)
        if valid_tools:
            report_lines.append("")
            report_lines.append("🔧 Valid Tools to Load:")
            for tool in valid_tools[:5]:  # Show first 5
                report_lines.append(f"  • {tool['name']} ({tool['id']})")
            if len(valid_tools) > 5:
                report_lines.append(f"  ... and {len(valid_tools) - 5} more")
        
        return "\\n".join(report_lines)


def mcp_startup_validation(project_root: str | None = None) -> Dict[str, Any]:
    """
    Main entry point for MCP server startup validation.
    Called by MCP server before loading Force components.
    """
    # Setup logging for startup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if project_root is None:
        project_root = os.getcwd()
    
    integration = ForceMCPIntegration(Path(project_root))
    
    # Run validation
    can_start, validation_results = integration.validate_for_mcp_startup()
    
    # Generate startup report
    startup_report = integration.generate_mcp_startup_report(validation_results)
    print(startup_report)
    
    # Return results for MCP server decision making
    return {
        'can_start': can_start,
        'validation_results': validation_results,
        'valid_tools': integration.get_valid_tools_for_loading(validation_results),
        'valid_patterns': integration.get_valid_patterns_for_loading(validation_results),
        'valid_constraints': integration.get_valid_constraints_for_loading(validation_results),
        'startup_report': startup_report
    }


if __name__ == "__main__":
    """Command line interface for testing MCP integration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Force MCP Integration Validation')
    parser.add_argument('--project-root', type=str, default=None,
                       help='Path to project root directory (default: current directory)')
    parser.add_argument('--fail-on-invalid', action='store_true',
                       help='Exit with error code if any components are invalid')
    
    args = parser.parse_args()
    
    result = mcp_startup_validation(args.project_root)
    
    if args.fail_on_invalid and not result['validation_results']['summary']['ready_for_loading']:
        print("\\n❌ Exiting with error due to invalid components")
        sys.exit(1)
    elif not result['can_start']:
        print("\\n❌ MCP startup blocked due to critical validation failures")
        sys.exit(1)
    else:
        print("\\n✅ Force validation completed successfully")
        sys.exit(0)
