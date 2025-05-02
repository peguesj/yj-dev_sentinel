"""
Specialized adapters for specific Dev Sentinel agent types.
"""
from typing import List, Optional, Dict, Any

from integration.fast_agent.adapter import FastAgentAdapter
from agents.vcma.vcma_agent import VersionControlMasterAgent
from agents.vcla.vcla_agent import VersionControlListenerAgent
from agents.cdia.cdia_agent import CodeDocumentationInspectorAgent
from agents.rdia.rdia_agent import ReadmeDocumentationInspectorAgent
from agents.saa.saa_agent import StaticAnalysisAgent

import fast_agent_mcp as fast


class VCMAFastAdapter(FastAgentAdapter):
    """Adapter for Version Control Master Agent."""
    
    def __init__(self, agent: VersionControlMasterAgent, name: Optional[str] = None, 
                 servers: Optional[List[str]] = None):
        """
        Initialize the VCMA adapter.
        
        Args:
            agent: The VCMA agent to adapt
            name: Optional name for the fast-agent (defaults to 'vcma')
            servers: Optional list of MCP servers to use
        """
        instruction = """
        You are the Version Control Master Agent, responsible for proactively managing version control 
        operations by observing code changes and making intelligent decisions about when and what to commit.
        
        Key Responsibilities:
        - Monitor file system changes in the workspace
        - Analyze commit-worthiness of changes
        - Group logically related changes
        - Generate meaningful commit messages
        - Manage branch creation and merging
        """
        super().__init__(agent, name=name or "vcma", instruction=instruction, servers=servers)


class VCLAFastAdapter(FastAgentAdapter):
    """Adapter for Version Control Listener Agent."""
    
    def __init__(self, agent: VersionControlListenerAgent, name: Optional[str] = None, 
                 servers: Optional[List[str]] = None):
        """
        Initialize the VCLA adapter.
        
        Args:
            agent: The VCLA agent to adapt
            name: Optional name for the fast-agent (defaults to 'vcla')
            servers: Optional list of MCP servers to use
        """
        instruction = """
        You are the Version Control Listener Agent, responsible for responding to explicit version control
        requests from other agents or developers with appropriate validation and safety checks.
        
        You can perform operations like:
        - commit
        - branch
        - merge
        - push
        - pull
        - status
        - reset
        - checkout
        """
        super().__init__(agent, name=name or "vcla", instruction=instruction, servers=servers)


class CDIAFastAdapter(FastAgentAdapter):
    """Adapter for Code Documentation Inspector Agent."""
    
    def __init__(self, agent: CodeDocumentationInspectorAgent, name: Optional[str] = None, 
                 servers: Optional[List[str]] = None):
        """
        Initialize the CDIA adapter.
        
        Args:
            agent: The CDIA agent to adapt
            name: Optional name for the fast-agent (defaults to 'cdia')
            servers: Optional list of MCP servers to use
        """
        instruction = """
        You are the Code Documentation Inspector Agent, responsible for evaluating and improving 
        in-code documentation quality across a codebase.
        
        You can:
        - Evaluate documentation standards compliance
        - Generate docstring templates for missing documentation
        - Suggest documentation improvements
        - Analyze documentation completeness and accuracy
        """
        super().__init__(agent, name=name or "cdia", instruction=instruction, servers=servers)


class RDIAFastAdapter(FastAgentAdapter):
    """Adapter for README Documentation Inspector Agent."""
    
    def __init__(self, agent: ReadmeDocumentationInspectorAgent, name: Optional[str] = None, 
                 servers: Optional[List[str]] = None):
        """
        Initialize the RDIA adapter.
        
        Args:
            agent: The RDIA agent to adapt
            name: Optional name for the fast-agent (defaults to 'rdia')
            servers: Optional list of MCP servers to use
        """
        instruction = """
        You are the README Inspector Agent, responsible for ensuring that project documentation is 
        comprehensive, accurate, up-to-date, and follows best practices.
        
        You can:
        - Parse README and related documentation files
        - Extract and validate structured sections
        - Compare documentation against actual project capabilities
        - Identify gaps, inconsistencies, and outdated information
        - Generate documentation improvement recommendations
        """
        super().__init__(agent, name=name or "rdia", instruction=instruction, servers=servers)


class SAAFastAdapter(FastAgentAdapter):
    """Adapter for Static Analysis Agent."""
    
    def __init__(self, agent: StaticAnalysisAgent, name: Optional[str] = None, 
                 servers: Optional[List[str]] = None):
        """
        Initialize the SAA adapter.
        
        Args:
            agent: The SAA agent to adapt
            name: Optional name for the fast-agent (defaults to 'saa')
            servers: Optional list of MCP servers to use
        """
        instruction = """
        You are the Static Analysis Agent, responsible for applying static analysis techniques to identify 
        code quality issues, potential bugs, and anti-patterns.
        
        You can:
        - Perform linting against configurable rule sets
        - Analyze code complexity
        - Check types and infer types
        - Detect security vulnerabilities
        - Identify performance issues
        """
        super().__init__(agent, name=name or "saa", instruction=instruction, servers=servers)