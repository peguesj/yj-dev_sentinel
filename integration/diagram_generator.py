"""
Diagram Generator Module for Dev Sentinel.

This module provides support for generating various types of diagrams for
documentation purposes. It supports multiple diagram formats including
PlantUML, Mermaid, and ASCII art diagrams.

Features:
- Architecture diagram generation
- Workflow/sequence diagram generation
- Component relationship diagram generation
- Terminal state diagram generation
- Extraction of diagrams from markdown documentation
"""

import os
import re
import sys
import json
import shutil
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("diagram_generator")

# Constants for diagram types and formats
DIAGRAM_FORMATS = ["png", "svg", "pdf", "txt"]
DIAGRAM_TYPES = ["ARCH", "FLOW", "COMP", "TERM", "EXTRACT"]
DIAGRAM_ENGINES = ["plantuml", "mermaid", "ascii"]

class DiagramDependencyError(Exception):
    """Exception raised when a required dependency for diagram generation is missing."""
    pass

async def check_diagram_dependencies() -> Dict[str, bool]:
    """
    Check if required dependencies for diagram generation are installed.
    
    Returns:
        Dict mapping dependency names to boolean indicating presence
    """
    dependencies = {
        "java": False,
        "plantuml": False,
        "mmdc": False,  # Mermaid CLI
        "dot": False,   # GraphViz
    }
    
    # Check for Java (required for PlantUML)
    try:
        proc = await asyncio.create_subprocess_exec(
            "java", "-version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, _ = await proc.communicate()
        dependencies["java"] = proc.returncode == 0
    except:
        pass
    
    # Check for PlantUML
    try:
        plantuml_path = shutil.which("plantuml")
        if not plantuml_path:
            plantuml_path = shutil.which("java -jar plantuml.jar")
        dependencies["plantuml"] = plantuml_path is not None
    except:
        pass
    
    # Check for Mermaid CLI
    try:
        proc = await asyncio.create_subprocess_exec(
            "mmdc", "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, _ = await proc.communicate()
        dependencies["mmdc"] = proc.returncode == 0
    except:
        pass
    
    # Check for GraphViz (dot)
    try:
        proc = await asyncio.create_subprocess_exec(
            "dot", "-V",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, _ = await proc.communicate()
        dependencies["dot"] = proc.returncode == 0
    except:
        pass
    
    return dependencies

class ArchitectureDiagramGenerator:
    """Generates architecture diagrams for the Dev Sentinel system."""
    
    def __init__(self, output_dir: str):
        """
        Initialize the architecture diagram generator.
        
        Args:
            output_dir: Directory where generated diagrams will be saved
        """
        self.output_dir = output_dir
        self.dependencies = {}
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    async def _init_dependencies(self):
        """Initialize and check for dependencies."""
        if not self.dependencies:
            self.dependencies = await check_diagram_dependencies()
            
    async def generate_project_overview_diagram(self, format: str = "png") -> Dict[str, Any]:
        """
        Generate a project overview architecture diagram.
        
        Args:
            format: Output format (png, svg, pdf)
            
        Returns:
            Dict containing generation results
        """
        await self._init_dependencies()
        
        # Check dependencies
        if not self.dependencies.get("plantuml"):
            return {
                "error": "PlantUML is required for architecture diagrams",
                "success": False,
                "missing_deps": ["plantuml"]
            }
        
        # Create PlantUML diagram code
        puml_code = """
@startuml DevSentinelArchitecture
!theme plain
skinparam componentStyle rectangle
skinparam backgroundColor transparent

title "Dev Sentinel Architecture Overview"

package "Dev Sentinel" {
    [Core Framework] as core
    [Integration Layer] as integration
    [Agent Manager] as manager
    
    package "Agents" {
        [VC Master Agent] as vcma
        [VC Listener Agent] as vcla
        [Code Doc Inspector Agent] as cdia
        [README Inspector Agent] as rdia
        [Static Analysis Agent] as saa
    }
    
    package "FORCE" {
        [Master Agent] as force_master
        [Terminal Manager] as terminal_mgr
        [Message Bus] as msg_bus
    }
    
    package "Fast-Agent Integration" {
        [Fast-Agent Adapter] as fast_adapter
        [MCP Server] as mcp
    }
}

core <--> manager
manager <--> Agents
integration <--> Agents

force_master --> terminal_mgr
force_master --> msg_bus
terminal_mgr --> Agents
msg_bus <--> Agents
fast_adapter <--> mcp
integration <--> fast_adapter

cloud "External Systems" {
    [Version Control System] as vcs
    [CI/CD Pipeline] as cicd
    [Documentation Platform] as docs
}

vcma --> vcs
vcla --> vcs
cdia --> docs
rdia --> docs
saa --> cicd

@enduml
"""
        
        # Write PlantUML code to temporary file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        puml_file = os.path.join(self.output_dir, f"arch_overview_{timestamp}.puml")
        output_file = os.path.join(self.output_dir, f"arch_overview_{timestamp}.{format}")
        
        with open(puml_file, "w") as f:
            f.write(puml_code)
        
        # Generate diagram using PlantUML
        try:
            cmd = ["plantuml", f"-t{format}", puml_file]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                return {
                    "error": f"PlantUML error: {stderr.decode()}",
                    "success": False
                }
                
            return {
                "success": True,
                "output_file": output_file,
                "message": f"Architecture overview diagram generated: {output_file}"
            }
            
        except Exception as e:
            return {
                "error": f"Error generating architecture diagram: {str(e)}",
                "success": False
            }
    
    async def generate_yung_command_flow_diagram(self, format: str = "png") -> Dict[str, Any]:
        """
        Generate a YUNG command flow diagram showing how commands are processed.
        
        Args:
            format: Output format (png, svg, pdf)
            
        Returns:
            Dict containing generation results
        """
        await self._init_dependencies()
        
        # Check dependencies
        if not self.dependencies.get("plantuml"):
            return {
                "error": "PlantUML is required for flow diagrams",
                "success": False,
                "missing_deps": ["plantuml"]
            }
        
        # Create PlantUML diagram code for YUNG command flow
        puml_code = """
@startuml YUNGCommandFlow
!theme plain
skinparam backgroundColor transparent

title "YUNG Command Processing Flow"

actor "User/Agent" as user
participant "FORCE Master Agent" as master
participant "Command Processor" as processor
participant "Terminal Manager" as terminal
participant "Subagent" as subagent
database "Message Bus" as msgbus

user -> master : "$COMMAND params"
activate master

master -> processor : process_command()
activate processor

processor -> processor : parse command type
processor -> processor : validate params

alt $VIC command
    processor -> subagent : documentation validation
    activate subagent
    subagent -> terminal : execute in terminal
    terminal --> subagent : result
    subagent --> processor : validation result
    deactivate subagent
else $CODE command
    processor -> subagent : code generation
    activate subagent
    subagent -> terminal : execute in terminal
    terminal --> subagent : result
    subagent --> processor : code result
    deactivate subagent
else $VCS command
    processor -> subagent : version control operation
    activate subagent
    subagent -> terminal : execute in terminal
    terminal --> subagent : result
    subagent --> processor : vcs result
    deactivate subagent
else $DIAGRAM command
    processor -> processor : parse diagram type
    processor -> subagent : generate diagram
    activate subagent
    subagent -> terminal : execute diagram generation
    terminal --> subagent : result
    subagent --> processor : diagram result
    deactivate subagent
end

processor --> master : command result
deactivate processor

master -> msgbus : publish results
master --> user : operation status
deactivate master

@enduml
"""
        
        # Write PlantUML code to temporary file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        puml_file = os.path.join(self.output_dir, f"yung_flow_{timestamp}.puml")
        output_file = os.path.join(self.output_dir, f"yung_flow_{timestamp}.{format}")
        
        with open(puml_file, "w") as f:
            f.write(puml_code)
        
        # Generate diagram using PlantUML
        try:
            cmd = ["plantuml", f"-t{format}", puml_file]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                return {
                    "error": f"PlantUML error: {stderr.decode()}",
                    "success": False
                }
                
            return {
                "success": True,
                "output_file": output_file,
                "message": f"YUNG command flow diagram generated: {output_file}"
            }
            
        except Exception as e:
            return {
                "error": f"Error generating flow diagram: {str(e)}",
                "success": False
            }
    
    async def generate_agent_class_diagram(self, format: str = "png") -> Dict[str, Any]:
        """
        Generate a class diagram showing agent relationships.
        
        Args:
            format: Output format (png, svg, pdf)
            
        Returns:
            Dict containing generation results
        """
        await self._init_dependencies()
        
        # Check dependencies
        if not self.dependencies.get("plantuml"):
            return {
                "error": "PlantUML is required for class diagrams",
                "success": False,
                "missing_deps": ["plantuml"]
            }
            
        # Create PlantUML class diagram code
        puml_code = """
@startuml AgentComponentDiagram
!theme plain
skinparam backgroundColor transparent
skinparam classAttributeIconSize 0
skinparam groupInheritance 2

title "Dev Sentinel Agent Component Relationships"

abstract class "BaseAgent" as BaseAgent {
    +name: str
    +id: str
    +is_active: bool
    +initialize()
    +process_message()
    +run_task()
    +shutdown()
}

class "VersionControlMasterAgent" as VCMA {
    +observe_changes()
    +suggest_commits()
    +handle_vcs_command()
}

class "VersionControlListenerAgent" as VCLA {
    +process_vcs_command()
    +validate_action()
    +execute_operation()
}

class "CodeDocInspectorAgent" as CDIA {
    +inspect_file()
    +evaluate_doc_quality()
    +suggest_improvements()
}

class "ReadmeInspectorAgent" as RDIA {
    +validate_readme()
    +check_completeness()
    +generate_sections()
}

class "StaticAnalysisAgent" as SAA {
    +analyze_code()
    +detect_issues()
    +suggest_fixes()
}

class "FORCEMasterAgent" as FMA {
    +process_command()
    +route_to_subagent()
    +collect_results()
}

BaseAgent <|-- VCMA
BaseAgent <|-- VCLA
BaseAgent <|-- CDIA
BaseAgent <|-- RDIA
BaseAgent <|-- SAA
BaseAgent <|-- FMA

FMA "1" *-- "many" BaseAgent : orchestrates >

@enduml
"""
        
        # Write PlantUML code to temporary file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        puml_file = os.path.join(self.output_dir, f"agent_components_{timestamp}.puml")
        output_file = os.path.join(self.output_dir, f"agent_components_{timestamp}.{format}")
        
        with open(puml_file, "w") as f:
            f.write(puml_code)
        
        # Generate diagram using PlantUML
        try:
            cmd = ["plantuml", f"-t{format}", puml_file]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                return {
                    "error": f"PlantUML error: {stderr.decode()}",
                    "success": False
                }
                
            return {
                "success": True,
                "output_file": output_file,
                "message": f"Agent component diagram generated: {output_file}"
            }
            
        except Exception as e:
            return {
                "error": f"Error generating component diagram: {str(e)}",
                "success": False
            }
    
    async def generate_terminal_state_diagram(self, format: str = "png") -> Dict[str, Any]:
        """
        Generate a state diagram showing terminal states and transitions.
        
        Args:
            format: Output format (png, svg, pdf)
            
        Returns:
            Dict containing generation results
        """
        await self._init_dependencies()
        
        # Check dependencies
        if not self.dependencies.get("plantuml"):
            return {
                "error": "PlantUML is required for state diagrams",
                "success": False,
                "missing_deps": ["plantuml"]
            }
        
        # Create PlantUML state diagram code
        puml_code = """
@startuml TerminalStates
!theme plain
skinparam backgroundColor transparent
skinparam stateBackgroundColor white
skinparam stateBorderColor black

title "Terminal State Transitions"

[*] --> Initializing

state Initializing {
    [*] --> CheckingDependencies
    CheckingDependencies --> CreatingEnvironment : dependencies OK
    CheckingDependencies --> [*] : dependencies missing
    CreatingEnvironment --> [*]
}

Initializing --> Ready : initialization complete

state Ready {
    [*] --> Idle
    Idle --> Processing : command received
    Processing --> Idle : command complete
    Processing --> Error : command failed
    Error --> Idle : error handled
}

Ready --> Executing : subagent command

state Executing {
    [*] --> RunningCommand
    RunningCommand --> WaitingForOutput : command running
    WaitingForOutput --> CollectingResults : output ready
    CollectingResults --> [*] : results collected
}

Executing --> Ready : execution complete
Executing --> Error : execution failed

state Error {
    [*] --> LoggingError
    LoggingError --> AttemptingRecovery : recovery possible
    LoggingError --> [*] : unrecoverable
    AttemptingRecovery --> [*] : recovery complete
}

Error --> Ready : error resolved

Ready --> ShuttingDown : shutdown requested
ShuttingDown --> [*] : cleanup complete

@enduml
"""
        
        # Write PlantUML code to temporary file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        puml_file = os.path.join(self.output_dir, f"terminal_states_{timestamp}.puml")
        output_file = os.path.join(self.output_dir, f"terminal_states_{timestamp}.{format}")
        
        with open(puml_file, "w") as f:
            f.write(puml_code)
        
        # Generate diagram using PlantUML
        try:
            cmd = ["plantuml", f"-t{format}", puml_file]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                return {
                    "error": f"PlantUML error: {stderr.decode()}",
                    "success": False
                }
                
            return {
                "success": True,
                "output_file": output_file,
                "message": f"Terminal state diagram generated: {output_file}"
            }
            
        except Exception as e:
            return {
                "error": f"Error generating state diagram: {str(e)}",
                "success": False
            }
    
    async def generate_force_integration_diagram(self, format: str = "png") -> Dict[str, Any]:
        """
        Generate a diagram showing FORCE integration architecture.
        
        Args:
            format: Output format (png, svg, pdf)
            
        Returns:
            Dict containing generation results
        """
        await self._init_dependencies()
        
        # Check dependencies
        if not self.dependencies.get("plantuml"):
            return {
                "error": "PlantUML is required for integration diagrams",
                "success": False,
                "missing_deps": ["plantuml"]
            }
        
        # Create PlantUML diagram code
        puml_code = """
@startuml ForceIntegration
!theme plain
skinparam backgroundColor transparent

title "FORCE Integration Architecture"

package "Dev Sentinel Framework" {
    [Core System] as core
    
    package "FORCE Architecture" {
        [FORCE Master Agent] as force
        [Terminal Manager] as terminals
        [Message Bus] as msgbus
    }
    
    package "YUNG Command Processor" {
        [Command Parser] as parser
        [Execution Router] as router
    }
    
    package "Agents" {
        [VCMA] as vcma
        [VCLA] as vcla
        [CDIA] as cdia
        [RDIA] as rdia
        [SAA] as saa
    }
    
    package "Integration Layer" {
        [Fast-Agent Adapter] as fastadapter
        [Terminal Integration] as termint
        [Diagram Generator] as diagrams
    }
    
    package "Output Channels" {
        [Code Generation] as codegen
        [Documentation] as docs
        [Terminal Output] as term
        [Visual Diagrams] as visuals
    }
}

core --> force
force --> parser
parser --> router
router --> Agents

force --> terminals
terminals --> Agents
msgbus <--> Agents

fastadapter <--> Agents
termint <--> Agents
diagrams <--> visuals

vcma --> codegen
cdia --> docs
rdia --> docs
diagrams --> docs
saa --> term

@enduml
"""
        
        # Write PlantUML code to temporary file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        puml_file = os.path.join(self.output_dir, f"force_integration_{timestamp}.puml")
        output_file = os.path.join(self.output_dir, f"force_integration_{timestamp}.{format}")
        
        with open(puml_file, "w") as f:
            f.write(puml_code)
        
        # Generate diagram using PlantUML
        try:
            cmd = ["plantuml", f"-t{format}", puml_file]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                return {
                    "error": f"PlantUML error: {stderr.decode()}",
                    "success": False
                }
                
            return {
                "success": True,
                "output_file": output_file,
                "message": f"FORCE integration diagram generated: {output_file}"
            }
            
        except Exception as e:
            return {
                "error": f"Error generating integration diagram: {str(e)}",
                "success": False
            }


async def generate_diagrams_from_markdown(markdown_file: str, output_dir: str) -> Dict[str, Any]:
    """
    Extract and generate diagrams from a markdown file.
    
    Args:
        markdown_file: Path to the markdown file
        output_dir: Directory where generated diagrams will be saved
        
    Returns:
        Dict containing extraction results
    """
    # Check if file exists
    if not os.path.exists(markdown_file):
        return {
            "error": f"File not found: {markdown_file}",
            "success": False
        }
    
    # Check dependencies
    dependencies = await check_diagram_dependencies()
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read markdown file
    try:
        with open(markdown_file, "r") as f:
            content = f.read()
    except Exception as e:
        return {
            "error": f"Error reading markdown file: {str(e)}",
            "success": False
        }
    
    # Extract code blocks
    plantuml_pattern = r"```plantuml\n(.*?)\n```"
    mermaid_pattern = r"```mermaid\n(.*?)\n```"
    ascii_pattern = r"```ascii\n(.*?)\n```"
    
    plantuml_blocks = re.findall(plantuml_pattern, content, re.DOTALL)
    mermaid_blocks = re.findall(mermaid_pattern, content, re.DOTALL)
    ascii_blocks = re.findall(ascii_pattern, content, re.DOTALL)
    
    generated_files = []
    errors = []
    
    # Process PlantUML blocks
    if plantuml_blocks and dependencies.get("plantuml"):
        for i, block in enumerate(plantuml_blocks):
            try:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = os.path.basename(markdown_file).split(".")[0]
                puml_file = os.path.join(output_dir, f"{filename}_plantuml_{i}_{timestamp}.puml")
                output_file = os.path.join(output_dir, f"{filename}_plantuml_{i}_{timestamp}.png")
                
                with open(puml_file, "w") as f:
                    f.write(block)
                
                cmd = ["plantuml", puml_file]
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                
                if proc.returncode == 0:
                    generated_files.append(output_file)
                else:
                    errors.append(f"Error generating PlantUML diagram {i}: {stderr.decode()}")
            except Exception as e:
                errors.append(f"Error processing PlantUML block {i}: {str(e)}")
    elif plantuml_blocks and not dependencies.get("plantuml"):
        errors.append("PlantUML is not installed but markdown contains PlantUML diagrams")
    
    # Process Mermaid blocks
    if mermaid_blocks and dependencies.get("mmdc"):
        for i, block in enumerate(mermaid_blocks):
            try:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = os.path.basename(markdown_file).split(".")[0]
                mmd_file = os.path.join(output_dir, f"{filename}_mermaid_{i}_{timestamp}.mmd")
                output_file = os.path.join(output_dir, f"{filename}_mermaid_{i}_{timestamp}.png")
                
                with open(mmd_file, "w") as f:
                    f.write(block)
                
                cmd = ["mmdc", "-i", mmd_file, "-o", output_file]
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                
                if proc.returncode == 0:
                    generated_files.append(output_file)
                else:
                    errors.append(f"Error generating Mermaid diagram {i}: {stderr.decode()}")
            except Exception as e:
                errors.append(f"Error processing Mermaid block {i}: {str(e)}")
    elif mermaid_blocks and not dependencies.get("mmdc"):
        errors.append("Mermaid CLI is not installed but markdown contains Mermaid diagrams")
    
    # Process ASCII blocks
    if ascii_blocks:
        for i, block in enumerate(ascii_blocks):
            try:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = os.path.basename(markdown_file).split(".")[0]
                output_file = os.path.join(output_dir, f"{filename}_ascii_{i}_{timestamp}.txt")
                
                with open(output_file, "w") as f:
                    f.write(block)
                
                generated_files.append(output_file)
            except Exception as e:
                errors.append(f"Error processing ASCII block {i}: {str(e)}")
    
    # Return results
    return {
        "success": len(errors) == 0,
        "generated_files": generated_files,
        "errors": errors,
        "extracted_diagrams": {
            "plantuml": len(plantuml_blocks),
            "mermaid": len(mermaid_blocks),
            "ascii": len(ascii_blocks)
        }
    }