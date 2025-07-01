#!/usr/local/bin/python
"""
Dev Sentinel Server        # Run             # Re-run validation
            revalidation = subprocess.run([
                sys.executable,
                "force/tools/system/force_component_validator.py", 
                ".force",
                "--startup-check"
            ], capture_output=True, text=True, cwd=Path.cwd())x
        fix_result = subprocess.run([
            sys.executable,
            "force/tools/system/force_component_fix_system.py",
            "--fix"
        ], capture_output=True, text=True, cwd=Path.cwd())r

This script properly launches the Dev Sentinel MCP server with correct path setup
and integrated Force component validation and fixing.
"""

import os
import sys
import argparse
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("dev_sentinel_runner")

# Import path setup to ensure all modules can be properly imported
try:
    import path_setup
    logger.debug(f"Set up Python path: {path_setup.project_root}")
except ImportError:
    logger.error("Failed to import path_setup module")
    sys.exit(1)

# Run Force validation and fix at startup
logger.info("🔍 Running Force component validation at startup...")
try:
    from force.tools.system import run_startup_validation
    
    # Run validation and auto-fix using embedded system
    validation_success = run_startup_validation(".force", auto_fix=True)
    
    if validation_success:
        logger.info("✅ Force validation passed")
    else:
        logger.warning("⚠️ Some validation issues remain - server may encounter problems")
        
except ImportError:
    logger.warning("Force validation system not available, falling back to subprocess method...")
    try:
        import subprocess
        from pathlib import Path
        
        # Run validation
        result = subprocess.run([
            sys.executable,
            "force/tools/system/force_component_validator.py",
            ".force",
            "--startup-check"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode != 0:
            logger.warning("❌ Force validation failed, attempting auto-fix...")
            
            # Run auto-fix
            fix_result = subprocess.run([
                sys.executable,
                "force/tools/system/force_component_fix_system.py",
                "--fix"
            ], capture_output=True, text=True, cwd=Path.cwd())
            
            if fix_result.returncode in [0, 1]:
                logger.info("🔧 Auto-fix completed, re-validating...")
                # Re-run validation
                revalidation = subprocess.run([
                    sys.executable,
                    "force/tools/system/force_component_validator.py", 
                    ".force",
                    "--startup-check"
                ], capture_output=True, text=True, cwd=Path.cwd())
                
                if revalidation.returncode == 0:
                    logger.info("✅ Force validation passed after auto-fix")
                else:
                    logger.warning("⚠️ Some validation issues remain after auto-fix")
            else:
                logger.error("❌ Auto-fix failed")
        else:
            logger.info("✅ Force validation passed")
            
    except Exception as e:
        logger.warning(f"Force validation system error: {e}")
except Exception as e:
    logger.warning(f"Force validation system error: {e}")

# Now we can safely import Dev Sentinel components
try:
    from integration.fast_agent.dev_sentinel_server import ServerManager
except ImportError as e:
    logger.error(f"Failed to import Dev Sentinel components: {e}")
    logger.error("Make sure you have all required dependencies installed")
    sys.exit(1)

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Dev Sentinel MCP Server Launcher")
    parser.add_argument("--http-port", type=int, default=8000, help="Port for HTTP API server")
    parser.add_argument("--mcp-port", type=int, default=8090, help="Port for MCP server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--log-dir", help="Directory for log files")
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # Create and start server manager
    manager = ServerManager(
        http_port=args.http_port,
        mcp_port=args.mcp_port,
        host=args.host,
        verbose=args.verbose
    )
    
    await manager.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by keyboard interrupt")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)