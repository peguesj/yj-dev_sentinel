"""
Force Governance Module

This module provides governance policy loading and management functionality for the Force framework.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class GovernanceRegistry:
    """Registry for Force governance policies"""
    
    def __init__(self, force_engine):
        self.force_engine = force_engine
        self.policies = {}
        
    def load_governance(self):
        """Load all governance policies from the governance directory"""
        governance_dir = os.path.join(os.path.dirname(__file__))
        governance_files = [f for f in os.listdir(governance_dir) if f.endswith('.json')]
        
        for governance_file in governance_files:
            try:
                governance_path = os.path.join(governance_dir, governance_file)
                with open(governance_path, 'r') as f:
                    governance_data = json.load(f)
                    # Handle both single policy and multiple policies in a file
                    if isinstance(governance_data, dict):
                        if 'policies' in governance_data:
                            # Multiple policies in file
                            for policy_id, policy_data in governance_data['policies'].items():
                                self.policies[policy_id] = policy_data
                                logger.debug(f"Loaded governance policy: {policy_id}")
                        else:
                            # Single policy
                            policy_id = governance_data.get('id', governance_file.replace('.json', ''))
                            self.policies[policy_id] = governance_data
                            logger.debug(f"Loaded governance policy: {policy_id}")
            except Exception as e:
                logger.warning(f"Failed to load governance {governance_file}: {e}")
                
        logger.info(f"Loaded {len(self.policies)} governance policies")
        return self.policies
        
    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get a governance policy by ID"""
        return self.policies.get(policy_id)
        
    def list_policies(self) -> List[Dict[str, Any]]:
        """List all available governance policies"""
        return list(self.policies.values())

def initialize(force_engine):
    """Initialize the governance module"""
    registry = GovernanceRegistry(force_engine)
    registry.load_governance()
    return registry
