"""
Path Setup Module for Dev Sentinel

This module handles setting up proper Python path configuration
for running Dev Sentinel components from any directory.
"""

import os
import sys

def setup_paths():
    """
    Set up Python paths for Dev Sentinel.
    Add project root to Python path to ensure all modules can be imported.
    """
    # Get the path to the project root (directory containing this file)
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Add project root to Python path if not already there
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        
    return project_root

# Automatically run setup when imported
project_root = setup_paths()