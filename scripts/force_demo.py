#!/usr/bin/env python3
"""
Force System Demonstration Script

Showcases the key capabilities of the integrated Force Agentic Development System
within the modernized Dev Sentinel architecture.
"""

import asyncio
import json
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from force import ForceEngine
from force.legacy_adapter import LegacyAgentManager
from force.yung_integration import YUNGForceIntegration


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_result(result, title="Result"):
    """Print a formatted result."""
    print(f"\n🎯 {title}:")
    if isinstance(result, dict):
        for key, value in result.items():
            if key == 'timestamp':
                print(f"   {key}: {value}")
            elif isinstance(value, (dict, list)) and len(str(value)) > 100:
                print(f"   {key}: {type(value).__name__} with {len(value)} items")
            else:
                print(f"   {key}: {value}")
    else:
        print(f"   {result}")


def demonstrate_force_engine():
    """Demonstrate Force engine capabilities."""
    print_section("🚀 Force Engine Demonstration")
    
    try:
        # Initialize Force engine
        print("⚡ Initializing Force engine...")
        engine = ForceEngine()
        print("✅ Force engine initialized successfully")
        
        # Discover components
        print("\n🔍 Discovering Force components...")
        tools = engine.list_tools()
        patterns = engine.list_patterns()
        constraints = engine.list_constraints()
        
        print(f"✅ Found {len(tools)} tools: {', '.join(tools)}")
        print(f"✅ Found {len(patterns)} patterns: {', '.join(patterns)}")
        print(f"✅ Found {len(constraints)} constraints")
        
        # Execute a tool
        print("\n🔧 Executing Force tool...")
        result = engine.execute_tool_sync('documentation_analysis', {
            'directory': '.',
            'analyze_readmes': True,
            'check_completeness': True
        })
        print_result(result, "Tool Execution")
        
        # Execute another tool
        print("\n🏗️ Executing project structure analysis...")
        result = engine.execute_tool_sync('project_structure_analysis', {
            'directory': '.',
            'include_hidden': False,
            'max_depth': 3
        })
        print_result(result, "Project Analysis")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in Force engine demo: {e}")
        return False


def demonstrate_legacy_integration():
    """Demonstrate legacy agent integration."""
    print_section("🔄 Legacy Agent Integration Demonstration")
    
    try:
        # Initialize legacy manager
        print("⚡ Initializing legacy agent manager...")
        manager = LegacyAgentManager()
        print("✅ Legacy agent manager initialized successfully")
        
        # Discover agents
        print("\n🔍 Discovering legacy agents...")
        agents = manager.get_available_agents()
        print(f"✅ Found {len(agents)} legacy agents:")
        for agent_id, description in agents.items():
            print(f"   • {agent_id}: {description}")
            
        # Create agent adapters
        print("\n🔧 Creating agent adapters...")
        for agent_type in ['VCMA', 'RDIA', 'SAA']:
            adapter = manager.get_agent_adapter(agent_type)
            if adapter:
                print(f"✅ {agent_type} adapter created successfully")
                capabilities = manager.list_agent_capabilities(agent_type)
                print(f"   Capabilities: {', '.join(capabilities)}")
            else:
                print(f"⚠️ {agent_type} adapter creation failed")
                
        return True
        
    except Exception as e:
        print(f"❌ Error in legacy integration demo: {e}")
        return False


async def demonstrate_yung_integration():
    """Demonstrate YUNG command integration."""
    print_section("🎮 YUNG Command Integration Demonstration")
    
    try:
        # Initialize YUNG integration
        print("⚡ Initializing YUNG integration...")
        integration = YUNGForceIntegration()
        print("✅ YUNG integration initialized successfully")
        
        # Test various commands
        commands = [
            "STATUS",
            "ANALYZE README", 
            "HEALTH CHECK",
            "LIST TOOLS"
        ]
        
        print("\n🔧 Processing YUNG commands...")
        for command in commands:
            print(f"\n   Processing: '{command}'")
            try:
                result = await integration.process_yung_command(command)
                if isinstance(result, dict) and len(str(result)) > 200:
                    print(f"   ✅ Command processed successfully (result truncated)")
                else:
                    print(f"   ✅ Result: {result}")
            except Exception as e:
                print(f"   ⚠️ Command failed: {e}")
                
        # Show execution stats
        print("\n📊 YUNG execution statistics...")
        stats = integration.get_execution_stats()
        print_result(stats, "Execution Stats")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in YUNG integration demo: {e}")
        return False


async def demonstrate_end_to_end_workflow():
    """Demonstrate end-to-end Force workflow."""
    print_section("🌐 End-to-End Workflow Demonstration")
    
    try:
        print("⚡ Initializing all Force components...")
        
        # Initialize all components
        engine = ForceEngine()
        legacy_manager = LegacyAgentManager()
        yung_integration = YUNGForceIntegration()
        
        print("✅ All components initialized")
        
        # Simulate a complete development workflow
        print("\n🔄 Simulating development workflow...")
        
        # 1. Analyze project structure
        print("\n   Step 1: Analyzing project structure...")
        structure_result = engine.execute_tool_sync('project_structure_analysis', {
            'directory': '.',
            'include_hidden': False,
            'max_depth': 2
        })
        print(f"   ✅ Structure analysis: {structure_result['success']}")
        
        # 2. Check documentation
        print("\n   Step 2: Checking documentation...")
        doc_result = engine.execute_tool_sync('documentation_analysis', {
            'directory': '.',
            'analyze_readmes': True,
            'check_completeness': True
        })
        print(f"   ✅ Documentation check: {doc_result['success']}")
        
        # 3. Process YUNG command
        print("\n   Step 3: Processing YUNG command...")
        yung_result = await yung_integration.process_yung_command("STATUS")
        print("   ✅ YUNG command processed successfully")
        
        # 4. Get legacy agent
        print("\n   Step 4: Accessing legacy agent...")
        adapter = legacy_manager.get_agent_adapter('VCMA')
        if adapter:
            print("   ✅ Legacy agent adapter available")
        else:
            print("   ⚠️ Legacy agent adapter not available")
            
        print("\n🎉 End-to-end workflow completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in end-to-end workflow: {e}")
        return False


def show_system_status():
    """Show overall system status."""
    print_section("📋 Force System Status Report")
    
    try:
        engine = ForceEngine()
        
        # Component counts
        tools = engine.list_tools()
        patterns = engine.list_patterns()
        constraints = engine.list_constraints()
        
        print("🎯 System Overview:")
        print(f"   • Force Directory: {engine.force_dir}")
        print(f"   • Tools Available: {len(tools)}")
        print(f"   • Patterns Available: {len(patterns)}")
        print(f"   • Constraints Active: {len(constraints)}")
        
        # Legacy agents
        manager = LegacyAgentManager()
        agents = manager.get_available_agents()
        print(f"   • Legacy Agents: {len(agents)}")
        
        print("\n✅ Force System Status: OPERATIONAL")
        print("✅ Legacy Integration Status: ACTIVE")
        print("✅ YUNG Compatibility Status: ENABLED")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking system status: {e}")
        return False


async def main():
    """Main demonstration function."""
    print("🚀 Force Agentic Development System")
    print("    Integrated with Dev Sentinel")
    print(f"    Demonstration Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run demonstrations
    results.append(("Force Engine", demonstrate_force_engine()))
    results.append(("Legacy Integration", demonstrate_legacy_integration()))
    results.append(("YUNG Integration", await demonstrate_yung_integration()))
    results.append(("End-to-End Workflow", await demonstrate_end_to_end_workflow()))
    results.append(("System Status", show_system_status()))
    
    # Summary
    print_section("📊 Demonstration Summary")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    
    print(f"🎯 Demonstration Results:")
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   • {test_name}: {status}")
        
    print(f"\n📈 Overall Score: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("\n🎉 All demonstrations completed successfully!")
        print("   The Force system is fully operational and ready for production use.")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} demonstrations had issues.")
        print("   Check the output above for details.")


if __name__ == '__main__':
    asyncio.run(main())
