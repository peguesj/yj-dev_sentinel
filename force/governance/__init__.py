"""
Governance module for the FORCE system.

Provides governance policy enforcement and audit capabilities.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class GovernancePolicy:
    """Base class for governance policies."""
    
    def __init__(self, policy_id: str, name: str, description: str, severity: str = "warning"):
        """Initialize a governance policy."""
        self.policy_id = policy_id
        self.name = name
        self.description = description
        self.severity = severity  # "error", "warning", or "info"
        
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the policy against the provided context.
        
        Args:
            context: Context to evaluate
            
        Returns:
            Evaluation result with compliance status
        """
        raise NotImplementedError("Governance policies must implement evaluate()")


class GovernanceManager:
    """Manager for governance policy enforcement."""
    
    def __init__(self, force_engine):
        """Initialize the governance manager."""
        self.force_engine = force_engine
        self.policies: Dict[str, GovernancePolicy] = {}
        self.policy_definitions: Dict[str, Dict[str, Any]] = {}
        
    def register_policy(self, policy: GovernancePolicy) -> None:
        """
        Register a governance policy.
        
        Args:
            policy: Policy to register
        """
        if policy.policy_id in self.policies:
            logger.warning(f"Policy {policy.policy_id} already registered, overriding")
            
        logger.info(f"Registering governance policy: {policy.policy_id}")
        self.policies[policy.policy_id] = policy
        
    def register_policy_definition(self, policy_definition: Dict[str, Any]) -> None:
        """
        Register a policy definition from a JSON definition.
        
        Args:
            policy_definition: Policy definition data
        """
        policy_id = policy_definition.get('id')
        if not policy_id:
            raise ValueError("Policy definition missing id field")
            
        if policy_id in self.policy_definitions:
            logger.warning(f"Policy definition {policy_id} already registered, overriding")
            
        logger.info(f"Registering policy definition: {policy_id}")
        self.policy_definitions[policy_id] = policy_definition
        
    async def evaluate_policies(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate all registered policies against the provided context.
        
        Args:
            context: Context to evaluate
            
        Returns:
            Evaluation results for all policies
        """
        results = {}
        for policy_id, policy in self.policies.items():
            try:
                results[policy_id] = await policy.evaluate(context)
            except Exception as e:
                logger.error(f"Error evaluating policy {policy_id}: {e}")
                results[policy_id] = {
                    "compliant": False,
                    "error": str(e)
                }
                
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_compliant": all(result.get("compliant", False) for result in results.values()),
            "policies": results
        }
        
    def load_policies(self) -> None:
        """Load policies from the governance directory."""
        try:
            governance_dir = self.force_engine.governance_dir
            if not governance_dir.exists():
                logger.warning(f"Governance directory not found: {governance_dir}")
                return
                
            for json_file in governance_dir.glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        policy_data = json.load(f)
                        
                    if "id" in policy_data:
                        self.register_policy_definition(policy_data)
                    elif "policies" in policy_data:
                        for policy_def in policy_data.get("policies", []):
                            self.register_policy_definition(policy_def)
                            
                except Exception as e:
                    logger.error(f"Error loading policy from {json_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error loading governance policies: {e}")


# Initialize the governance manager when this module is imported
governance_manager = None

def initialize(force_engine):
    """Initialize the governance module with a reference to the Force engine."""
    global governance_manager
    governance_manager = GovernanceManager(force_engine)
    governance_manager.load_policies()
    return governance_manager
