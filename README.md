# Dev Sentinel: Autonomous Development Agent Architecture

<div align="center">
  <img src="docs/diagrams/dev_sentinel_logo.svg" alt="Dev Sentinel Logo" width="200"/>
  
  **Version: 0.2.0**  
  **Date: May 2, 2025**  
  **Author: Jeremiah Pegues <jeremiah@pegues.io>**  
  **Organization: Pegues OPSCORP LLC**  
  **License: [MIT](LICENSE-MIT.md)**
  
  [![Built with: Python](https://img.shields.io/badge/Built%20with-Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
  [![Architecture: Agent-Based](https://img.shields.io/badge/Architecture-Agent%20Based-009688?logo=blueprint&logoColor=white)](docs/markdown/architecture.md)
  [![Documentation: PlantUML](https://img.shields.io/badge/Documentation-PlantUML-orange?logo=diagram&logoColor=white)](docs/diagrams/)
</div>

## 📋 Overview

Dev Sentinel is a comprehensive framework for autonomous development agents that collaborate to streamline software development, enforce best practices, and ensure high-quality documentation. The system consists of specialized intelligent agents that work together through a shared message bus to manage version control, inspect documentation, analyze code quality, and integrate with external systems.

### Key Features

- **Autonomous Version Control Management**: Intelligent commit, branch, and merge operations
- **Documentation Quality Assurance**: Automated inspection and improvement of READMEs and code documentation
- **Code Quality Analysis**: Static analysis integration with multi-language support
- **Agent Collaboration Framework**: Event-driven architecture with message bus communication
- **Terminal State Persistence**: Context-aware management of development environments
- **Extensible Architecture**: Plug-in model for adding new agent capabilities
- **Visualization Capabilities**: Automated generation of system diagrams and documentation

## 🏛️ System Architecture

Dev Sentinel is built on a modular, event-driven architecture with specialized agents that communicate through a central message bus. The diagram below illustrates the high-level architecture:

```plantuml
@startuml Dev Sentinel Architecture Overview
!theme plain
skinparam backgroundColor transparent
skinparam defaultFontSize 14
skinparam componentStyle rectangle
skinparam linetype ortho

' Define colors
!$core_color = "#4D7A97"
!$agent_color = "#6597B2"
!$integration_color = "#F3B95F"
!$external_color = "#93A1A1"
!$message_color = "#D6EAF8"
!$task_color = "#FADBD8"

' Set component styles
skinparam component {
    BackgroundColor<<Core>> $core_color
    BackgroundColor<<Agent>> $agent_color
    BackgroundColor<<Integration>> $integration_color
    BackgroundColor<<External>> $external_color
    BorderColor black
    ArrowColor black
}

' Core Components
package "Dev Sentinel Core" {
    component "Message Bus" as MB <<Core>> {
        component "Topic Registry" as TR
        component "Subscription Manager" as SM
        component "Message Queue" as MQ
    }
    component "Task Manager" as TM <<Core>> {
        component "Task Queue" as TQ
        component "Task Dispatcher" as TD
        component "Result Collector" as RC
    }
    interface "Agent API" as API
}

' Agent Components
package "Specialized Agents" {
    component "Version Control\nMaster Agent\n(VCMA)" as VCMA <<Agent>> {
        component "Repository Monitor" as RM
        component "Commit Analyzer" as CA
        component "VCLA Coordinator" as VC
    }
    component "Version Control\nListener Agent\n(VCLA)" as VCLA <<Agent>> {
        component "Path Monitor" as PM
        component "Change Detector" as CD
    }
    component "Code Documentation\nInspector Agent\n(CDIA)" as CDIA <<Agent>> {
        component "DocString Parser" as DSP
        component "Coverage Analyzer" as COA
    }
    component "README\nInspector Agent\n(RDIA)" as RDIA <<Agent>> {
        component "Markdown Parser" as MP
        component "Section Validator" as SV
    }
    component "Static Analysis\nAgent\n(SAA)" as SAA <<Agent>> {
        component "Multi-language\nAnalyzer" as MLA
        component "Issue Detector" as ID
    }
}

' Integration Layer
package "Integration Layer" {
    component "FORCE" as FORCE <<Integration>> {
        component "Terminal Manager" as TM_FORCE
        component "Command Processor" as CP_FORCE
        component "Master Agent" as MA_FORCE
    }
    component "Fast-Agent" as FAST <<Integration>> {
        component "Adapter" as ADAPTER
        component "MCP Servers" as MCP
    }
    component "Diagram Generator" as DIAG <<Integration>> {
        component "PlantUML Engine" as PUML
        component "Mermaid Engine" as MERM
    }
}

' External Systems
package "External Systems" {
    component "Git" as GIT <<External>>
    component "CI/CD" as CICD <<External>>
    component "Development\nEnvironment" as IDE <<External>>
}

' Core Connections
MB -- API : provides >
API -- TM : coordinates >

' Agent connections to core
VCMA -- API : implements >
VCLA -- API : implements >
CDIA -- API : implements >
RDIA -- API : implements >
SAA -- API : implements >

' Agent relationships
VCMA *-- VCLA : coordinates >
VCMA -- CDIA : notifies changes >
VCMA -- RDIA : triggers inspection >
CDIA -- SAA : shares analysis >

' Integration connections
FORCE -- MB : subscribes to >
FAST -- FORCE : extends >
DIAG -- MB : monitors >

' External system connections
VCMA --- GIT : manages >
VCLA --- GIT : monitors >
FAST --- CICD : integrates with >
IDE --- FORCE : commands from >

' Message flow examples
MB ..> VCMA : "vc.commit_analyzed" #$message_color
VCMA ..> MB : "vc.new_commits" #$message_color
MB ..> CDIA : "vc.file_changed" #$message_color
CDIA ..> MB : "cdia.inspection_complete" #$message_color
TM ..> SAA : "analyze_code_task" #$task_color
SAA ..> TM : "task_result" #$task_color

@enduml
```

### Core Components

The Dev Sentinel system is built around these core components:

#### Message Bus

The central nervous system of Dev Sentinel, facilitating asynchronous communication between agents through a publish-subscribe pattern.

```plantuml
@startuml Message Bus Architecture
!theme plain
skinparam backgroundColor transparent
skinparam defaultFontSize 14
skinparam linetype ortho

class MessageBus {
  -instance: MessageBus
  -subscribers: Dict[str, List[Callable]]
  -history: Dict[str, List[Dict]]
  +subscribe(topic: str, callback: Callable): None
  +unsubscribe(topic: str, callback: Callable): None
  +publish(topic: str, message: Dict, sender_id: Optional[str]): Awaitable[None]
  +get_history(topic: str, limit: Optional[int]): List[Dict]
}

class MessageSubscriber {
  +callback: Callable
  +filters: Dict[str, Any]
  +process_message(message: Dict): Awaitable[None]
  +matches_filters(message: Dict): bool
}

class MessagePublisher {
  +message_bus: MessageBus
  +publish_message(topic: str, payload: Dict): Awaitable[None]
  +create_message(message_type: str, data: Dict): Dict
}

MessageBus *-- MessageSubscriber : manages >
MessagePublisher --> MessageBus : uses >

Agent1 --> MessagePublisher : implements >
Agent2 --> MessageSubscriber : implements >
Agent3 --> MessagePublisher : implements >
Agent3 --> MessageSubscriber : implements >

@enduml
```

#### Task Manager

Handles the creation, distribution, and tracking of tasks across the system, enabling asynchronous workload management.

```plantuml
@startuml Task Manager Architecture
!theme plain
skinparam backgroundColor transparent
skinparam defaultFontSize 14
skinparam linetype ortho

class TaskManager {
  -instance: TaskManager
  -tasks: Dict[str, Task]
  -handlers: Dict[str, Callable]
  +register_handler(task_type: str, handler: Callable): None
  +unregister_handler(task_type: str, handler: Callable): None
  +create_task(task_type: str, params: Dict, requester: str): Task
  +get_handler(task_type: str): Optional[Callable]
  +get_task(task_id: str): Optional[Task]
  +update_task_status(task_id: str, status: TaskStatus, result: Dict): None
}

class Task {
  +task_id: str
  +task_type: str
  +params: Dict
  +requester: str
  +status: TaskStatus
  +created_at: datetime
  +updated_at: datetime
  +result: Optional[Dict]
  +get_age(): int
  +to_dict(): Dict
}

enum TaskStatus {
  PENDING
  IN_PROGRESS
  COMPLETED
  FAILED
  CANCELLED
}

TaskManager *-- Task : manages >
Task *-- TaskStatus : has >

Agent1 --> TaskManager : registers handlers >
Agent2 --> TaskManager : registers handlers >
Agent3 --> TaskManager : creates tasks >

@enduml
```

#### BaseAgent

The foundation for all agent implementations in the system, providing common functionality and lifecycle management.

```plantuml
@startuml BaseAgent Architecture
!theme plain
skinparam backgroundColor transparent
skinparam defaultFontSize 14
skinparam linetype ortho

abstract class BaseAgent {
  +agent_id: str
  +config: Dict[str, Any]
  +status: AgentStatus
  +logger: Logger
  +statistics: Dict[str, Any]
  #activity_log: List[Dict]
  #error_log: List[Dict]
  +__init__(agent_id: Optional[str], config: Optional[Dict])
  +{abstract} start(): Awaitable[None]
  +{abstract} shutdown(): Awaitable[None]
  +update_status(status: AgentStatus): None
  +get_agent_state(): Dict[str, Any]
  +log_activity(activity_type: str, details: Dict): None
  +log_error(error_type: str, message: str, details: Dict): None
}

enum AgentStatus {
  INITIALIZING
  IDLE
  BUSY
  ERROR
  PAUSED
  TERMINATED
}

BaseAgent *-- AgentStatus : has >

class VersionControlMasterAgent {
}

class VersionControlListenerAgent {
}

class CodeDocumentationInspectorAgent {
}

class READMEInspectorAgent {
}

class StaticAnalysisAgent {
}

BaseAgent <|-- VersionControlMasterAgent
BaseAgent <|-- VersionControlListenerAgent
BaseAgent <|-- CodeDocumentationInspectorAgent
BaseAgent <|-- READMEInspectorAgent
BaseAgent <|-- StaticAnalysisAgent

@enduml
```

## 🤖 Agent Components

Dev Sentinel uses specialized agents for different aspects of the development workflow:

### Version Control Master Agent (VCMA)

Proactively manages version control operations by observing code changes and making intelligent decisions about when and what to commit.

```plantuml
@startuml VCMA Architecture
!theme plain
skinparam backgroundColor transparent
skinparam linetype ortho

class VersionControlMasterAgent {
  +repo_path: str
  +known_branches: Set[str]
  +tracked_files: Set[str]
  +last_commit_hash: Optional[str]
  +file_change_history: Dict[str, List]
  +vcla_agents: Set[str]
  +__init__(agent_id: Optional[str], config: Optional[Dict])
  +start(): Awaitable[None]
  -_periodic_repo_scan(interval_seconds: int): Awaitable[None]
  -_refresh_repo_state(): Awaitable[Dict]
  -_update_tracked_files(): Awaitable[None]
  -_analyze_new_commits(old_hash: str, new_hash: str): Awaitable[None]
  -_run_git_command(command: str): Awaitable[str]
  -_handle_vc_changes(message: Dict): Awaitable[None]
  -_handle_status_request(message: Dict): Awaitable[None]
  -_handle_refresh_repo_task(task: Task): Awaitable[Dict]
  -_handle_analyze_commit_task(task: Task): Awaitable[Dict]
  +process_task(task: Dict): Awaitable[Dict]
  +register_vcla(agent_id: str): None
  +unregister_vcla(agent_id: str): None
  +shutdown(): Awaitable[None]
}

BaseAgent <|-- VersionControlMasterAgent

VersionControlMasterAgent -- "1..*" VersionControlListenerAgent : coordinates >
VersionControlMasterAgent -- MessageBus : publishes to >
VersionControlMasterAgent -- TaskManager : handles tasks from >

@enduml
```

**Key Responsibilities:**
- Repository state tracking and versioning
- Commit analysis and history management
- VCLA coordination and delegation
- Smart commit decision-making

[View the complete VCMA specification](vc_master_agent_spec.md)

### Version Control Listener Agent (VCLA)

Monitors specific aspects of the repository, focusing on particular paths, file types, or behaviors as delegated by the VCMA.

```plantuml
@startuml VCLA Architecture
!theme plain
skinparam backgroundColor transparent
skinparam linetype ortho

class VersionControlListenerAgent {
  +repo_path: str
  +monitored_paths: Set[str]
  +vcma_id: Optional[str]
  +__init__(agent_id: Optional[str], config: Optional[Dict])
  +start(): Awaitable[None]
  +process_task(task: Task): Awaitable[Dict]
  +shutdown(): Awaitable[None]
}

BaseAgent <|-- VersionControlListenerAgent

VersionControlListenerAgent -- VersionControlMasterAgent : reports to >
VersionControlListenerAgent -- MessageBus : publishes to >
VersionControlListenerAgent -- TaskManager : handles tasks from >

@enduml
```

**Key Responsibilities:**
- Path-specific file monitoring
- Change detection and notification
- Specialized observation of repository components

[View the complete VCLA specification](vc_listener_agent_spec.md)

### Code Documentation Inspector Agent (CDIA)

Evaluates and improves in-code documentation quality across a codebase, supporting multiple programming languages.

```plantuml
@startuml CDIA Architecture
!theme plain
skinparam backgroundColor transparent
skinparam linetype ortho

class CodeDocumentationInspectorAgent {
  +repo_path: str
  +file_extensions: List[str]
  +excluded_paths: Set[str]
  +min_doc_coverage: float
  +last_analyzed_commit: Optional[str]
  +__init__(agent_id: Optional[str], config: Optional[Dict])
  -_get_all_extensions(): List[str]
  -_get_language_for_file(file_path: str): Optional[str]
  +start(): Awaitable[None]
  +process_task(task: Task): Awaitable[Dict]
  -_handle_commit_analyzed(message: Dict): Awaitable[None]
  -_handle_repo_refreshed(message: Dict): Awaitable[None]
  -_handle_readme_inspection(message: Dict): Awaitable[None]
  -_handle_inspect_code_task(task: Task): Awaitable[Dict]
  -_handle_inspect_file_task(task: Task): Awaitable[Dict]
  +inspect_files(file_paths: List[str], commit_info: Optional[Dict]): Awaitable[List[Dict]]
  -_analyze_file_documentation(content: str, language: str, file_path: str): List[Dict]
  -_calculate_doc_coverage(content: str, language: str): float
  +shutdown(): Awaitable[None]
}

BaseAgent <|-- CodeDocumentationInspectorAgent

CodeDocumentationInspectorAgent -- MessageBus : publishes to >
CodeDocumentationInspectorAgent -- TaskManager : handles tasks from >
CodeDocumentationInspectorAgent -- VersionControlMasterAgent : receives updates from >

@enduml
```

**Key Responsibilities:**
- Documentation pattern detection
- Coverage calculation and reporting
- Multi-language support
- Issue identification and notification

[View the complete CDIA specification](code_doc_inspector_agent_spec.md)

### README Inspector Agent (RDIA)

Ensures that project documentation is comprehensive, accurate, up-to-date, and follows best practices.

```plantuml
@startuml RDIA Architecture
!theme plain
skinparam backgroundColor transparent
skinparam linetype ortho

class READMEInspectorAgent {
  +repo_path: str
  +readme_files: List[str]
  +section_requirements: Dict[str, Dict]
  +last_analyzed_commit: Optional[str]
  +__init__(agent_id: Optional[str], config: Optional[Dict])
  +start(): Awaitable[None]
  +process_task(task: Task): Awaitable[Dict]
  -_handle_commit_analyzed(message: Dict): Awaitable[None]
  -_handle_repo_refreshed(message: Dict): Awaitable[None]
  -_handle_inspect_readme_task(task: Task): Awaitable[Dict]
  +inspect_readme(file_path: str, commit_info: Optional[Dict]): Awaitable[Dict]
  -_analyze_readme_content(content: str, file_path: str): Dict
  -_check_section_requirements(sections: Dict[str, str]): List[Dict]
  -_extract_sections(content: str): Dict[str, str]
  +shutdown(): Awaitable[None]
}

BaseAgent <|-- READMEInspectorAgent

READMEInspectorAgent -- MessageBus : publishes to >
READMEInspectorAgent -- TaskManager : handles tasks from >
READMEInspectorAgent -- VersionControlMasterAgent : receives updates from >

@enduml
```

**Key Responsibilities:**
- README section validation
- Content quality assessment
- Markdown structure analysis
- Cross-referencing with codebase

[View the complete RDIA specification](readme_inspector_agent_spec.md)

### Static Analysis Agent (SAA)

Applies static analysis techniques to identify code quality issues, potential bugs, and anti-patterns across multiple programming languages.

```plantuml
@startuml SAA Architecture
!theme plain
skinparam backgroundColor transparent
skinparam linetype ortho

class StaticAnalysisAgent {
  +repo_path: str
  +supported_languages: Dict[str, List[str]]
  +analyzers: Dict[str, Dict]
  +excluded_paths: Set[str]
  +issue_threshold: Dict[str, int]
  +last_analyzed_commit: Optional[str]
  +__init__(agent_id: Optional[str], config: Optional[Dict])
  +start(): Awaitable[None]
  +process_task(task: Task): Awaitable[Dict]
  -_handle_commit_analyzed(message: Dict): Awaitable[None]
  -_handle_repo_refreshed(message: Dict): Awaitable[None]
  -_handle_analyze_code_task(task: Task): Awaitable[Dict]
  -_handle_analyze_file_task(task: Task): Awaitable[Dict]
  +analyze_files(file_paths: List[str]): Awaitable[List[Dict]]
  -_get_analyzer_for_file(file_path: str): Optional[str]
  -_run_analyzer(analyzer: str, file_path: str): Awaitable[Dict]
  -_parse_analyzer_output(analyzer: str, output: str): List[Dict]
  +shutdown(): Awaitable[None]
}

BaseAgent <|-- StaticAnalysisAgent

StaticAnalysisAgent -- MessageBus : publishes to >
StaticAnalysisAgent -- TaskManager : handles tasks from >
StaticAnalysisAgent -- VersionControlMasterAgent : receives updates from >

@enduml
```

**Key Responsibilities:**
- Multi-language code analysis
- Code quality issue detection
- Static analysis tool integration
- Issue reporting and tracking

## 🔌 Integration Architecture

### FORCE: Federated Orchestration & Reporting

The [FORCE architecture](FORCE.spec.md) provides a federated approach to agent orchestration, telemetry collection, and operation reporting:

```plantuml
@startuml FORCE Architecture
!theme plain
skinparam backgroundColor transparent
skinparam componentStyle rectangle
skinparam linetype ortho

!$command_color = "#D6EAF8"
!$state_color = "#FADBD8"

actor "User" as User

package "FORCE Architecture" {
    component "Master Agent" as MA {
        component "YUNG Command Parser" as YCP
        component "Command Processor" as CP
        component "Telemetry Collector" as TC
        component "Operation Reporter" as OR
    }
    
    package "Terminal Manager" as TM {
        component "Terminal Session Registry" as TSR
        component "Terminal State Persistence" as TSP
        component "Environment Manager" as EM
    }
    
    package "Subagent Terminals" {
        component "VCS Terminal" as VT {
            component "Git Context" as GC
        }
        component "Documentation Terminal" as DT {
            component "Doc Context" as DC
        }
        component "Code Terminal" as CT {
            component "Code Context" as CC
        }
        component "Infrastructure Terminal" as IT {
            component "Infra Context" as IC
        }
        component "Testing Terminal" as TT {
            component "Test Context" as TC2
        }
        component "Fast-Agent Terminal" as FT {
            component "MCP Context" as MC
        }
    }
}

package "Integration Layer" {
    component "Fast-Agent" as FA {
        component "MCP Bridge" as MCPBridge
        component "Agent Adapters" as Adapters
        component "MCP Servers" as Servers
    }
    
    component "Diagram Generator" as DG {
        component "PlantUML Engine" as PE
        component "Mermaid Engine" as ME
        component "ASCII Art Generator" as AAG
    }
}

package "External Systems" {
    component "Git Repository" as GitRepo
    component "Development Environment" as DevEnv
    component "CI/CD Pipeline" as CICD
}

' Command flow
User -r-> MA : Commands
MA --> YCP : parses command
YCP --> CP : processes command
CP --> VT : "$VCS commands"
CP --> DT : "$VIC commands"
CP --> CT : "$CODE commands"
CP --> IT : "$INFRA commands"
CP --> TT : "$TEST commands"
CP --> FT : "$FAST commands"
CP --> DG : "$DIAGRAM commands"

' Context flow
VT --> TM : registers
DT --> TM : registers
CT --> TM : registers
IT --> TM : registers
TT --> TM : registers
FT --> TM : registers

TM --> TSP : persists state
TSR --> EM : manages

' External connections
VT --> GitRepo : interacts with
FA --> CICD : integrates with
MA --> DevEnv : monitors

' Terminal integration
VT ..> FA : implements operation
DT ..> FA : implements operation
CT ..> FA : implements operation
IT ..> FA : implements operation
TT ..> FA : implements operation
FT ..> FA : implements operation

' Example flows
User -[#blue]-> MA : "$VCS COMMIT \"fix: update documentation\"" #$command_color
MA -[#blue]-> VT : delegates command #$command_color
VT -[#blue]-> GitRepo : executes git commit #$command_color
VT -[#red]-> TM : updates terminal state #$state_color
VT -[#red]-> MA : reports result #$state_color

@enduml
```

### Terminal State Management

The Terminal Manager maintains persistent state for each specialized agent terminal:

```plantuml
@startuml Terminal State Management
!theme plain
skinparam backgroundColor transparent
skinparam defaultFontSize 14
skinparam linetype ortho

class TerminalSession {
  +terminal_id: str
  +subagent_name: str
  +working_dir: str
  +env_vars: Dict[str, str]
  +command_history: List[Dict]
  +active: bool
  +last_active: datetime
  +tracked_files: List[str]
  +cached_assets: Dict[str, Any]
  +initialize(): bool
  +execute_command(command: str): Dict[str, Any]
  +get_state(): Dict[str, Any]
  +update_state(state_updates: Dict[str, Any]): None
  +add_to_history(command: str, result: Dict): None
  +get_history(limit: int): List[Dict]
  +get_tracked_files(): List[str]
  +add_tracked_file(file_path: str): None
  +remove_tracked_file(file_path: str): None
}

class TerminalManager {
  -instance: TerminalManager
  +terminals: Dict[str, TerminalSession]
  +state_dir: str
  +create_terminal(subagent_name: str, terminal_id: str, working_dir: str): str
  +get_terminal(terminal_id: str): Optional[TerminalSession]
  +execute_in_terminal(terminal_id: str, command: str): Dict[str, Any]
  -_save_terminal_state(terminal: TerminalSession): None
  -_load_terminal_state(terminal_id: str): Optional[TerminalSession]
  +get_or_create_terminal(subagent_name: str): TerminalSession
  +list_terminals(): List[Dict[str, Any]]
  +get_terminal_state(terminal_id: str): Dict[str, Any]
  +update_terminal_state(terminal_id: str, state_updates: Dict): None
  +restore_terminal_state(terminal_id: str): bool
}

class TerminalSessionState {
  +terminal_id: str
  +subagent_name: str
  +working_dir: str
  +env_vars: Dict[str, str]
  +command_history: List[Dict]
  +active: bool
  +last_active: datetime
  +tracked_files: List[str]
  +cached_assets: Dict[str, Any]
  +to_dict(): Dict[str, Any]
  +from_dict(data: Dict): TerminalSessionState
  +save_to_file(file_path: str): None
  +load_from_file(file_path: str): TerminalSessionState
}

class TerminalCommand {
  +command: str
  +timestamp: datetime
  +result: Dict
  +execution_time: float
  +to_dict(): Dict[str, Any]
  +from_dict(data: Dict): TerminalCommand
}

TerminalManager o-- "0..*" TerminalSession : manages
TerminalSession *-- "1" TerminalSessionState : has state
TerminalSession *-- "0..*" TerminalCommand : has history

@enduml
```

## 📊 Command Structure: YUNG Specification

Dev Sentinel implements the [YUNG (YES Ultimate Net Good)](YUNG_spec.md) universal instruction set for standardized command execution across autonomous agents:

```plantuml
@startuml YUNG Command Flow
!theme plain
skinparam backgroundColor transparent
skinparam defaultFontSize 14
skinparam sequenceMessageAlign center
skinparam sequenceParticipant underline

actor User
participant "Master Agent" as Master
participant "Command Parser" as Parser
participant "Terminal Manager" as TM
participant "Subagent Terminal" as Terminal
participant "Agent Implementation" as Agent
participant "External System" as External

User -> Master: "$VCS COMMIT \"fix: update documentation\""
activate Master

Master -> Parser: Parse YUNG command
activate Parser
Parser --> Master: Parsed command structure
deactivate Parser

Master -> TM: Get terminal for "vcs" subagent
activate TM
TM -> Terminal: Initialize or restore terminal
TM --> Master: Terminal session ready
deactivate TM

Master -> Terminal: Execute VCS command
activate Terminal

Terminal -> Agent: Execute operation
activate Agent

Agent -> External: Perform external action
activate External
External --> Agent: Action result
deactivate External

Agent --> Terminal: Operation result
deactivate Agent

Terminal -> TM: Update terminal state
activate TM
TM --> Terminal: State updated
deactivate TM

Terminal --> Master: Command execution result
deactivate Terminal

Master --> User: Operation result and status
deactivate Master

@enduml
```

### Key Command Structure

Each YUNG command follows a consistent structure:

```
$COMMAND_TYPE [SUBCOMMAND] [PARAM1=VALUE1 PARAM2=VALUE2 ...] [POSITIONAL_ARGS...]
```

For example:
- `$VCS COMMIT "fix: update documentation"` - Commit changes with a message
- `$CODE TIER=BACKEND IMPL` - Implement backend code
- `$VIC DOCS` - Validate the integrity of documentation
- `$DIAGRAM ARCH FORMAT=svg` - Generate system architecture diagrams

See the complete [YUNG specification](YUNG_spec.md) for more details.

## 📊 Workflow Integration

Dev Sentinel integrates with development workflows through multiple channels:

```plantuml
@startuml Dev Sentinel Workflow Integration
!theme plain
skinparam backgroundColor transparent
skinparam defaultFontSize 14
skinparam linetype ortho

rectangle "Developer Workflow" {
    (Code Writing) as CodeWriting
    (Documentation) as Doc
    (Code Review) as Review
    (Testing) as Test
    (Deployment) as Deploy
}

rectangle "Dev Sentinel" {
    (VCMA) as VCMA
    (CDIA) as CDIA
    (RDIA) as RDIA
    (SAA) as SAA
    (FORCE System) as FORCE
}

rectangle "External Systems" {
    (Git Repository) as Git
    (CI/CD Pipeline) as CICD
    (IDE Integration) as IDE
    (Project Management) as PM
}

' Developer workflow connections
CodeWriting --> Doc : leads to
Doc --> Review : enables
Review --> Test : verifies
Test --> Deploy : allows

' Dev Sentinel integration points
CodeWriting <--> VCMA : monitors changes
CodeWriting <--> SAA : analyzes quality
Doc <--> CDIA : evaluates in-code docs
Doc <--> RDIA : inspects README
Review <--> FORCE : provides insights
FORCE <--> Test : suggests tests

' External system connections
VCMA <--> Git : manages repo
FORCE <--> CICD : integrates with
FORCE <--> IDE : provides commands
FORCE <--> PM : updates status

@enduml
```

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/pegues/dev-sentinel.git

# Install dependencies
cd dev-sentinel
pip install -r requirements.txt

# Install diagram dependencies (optional, but recommended for visualization)
pip install plantuml
npm install -g @mermaid-js/mermaid-cli

# Initialize and run the system
python -m integration.force.initialize
```

After initialization, you'll see a summary of all initialized components. The system will generate initial diagrams in the `docs/diagrams` directory.

### Starting the FORCE System

Once initialized, start the master agent to begin using the system:

```bash
python -m integration.force.master_agent
```

You can now use YUNG commands to interact with the system through the master agent's interface.

### Visualizing System Architecture

The initialization process generates key system diagrams automatically. To regenerate or create additional diagrams:

```bash
# In the master agent terminal
$DIAGRAM ARCH FORMAT=svg
$DIAGRAM FORCE FORMAT=png
$DIAGRAM TERM FORMAT=svg
```

### Diagram Dependencies

For full diagram generation support:
- Java JRE (for PlantUML)
- PlantUML JAR file
- Node.js and NPM (for Mermaid CLI)

## 📄 License

Dev Sentinel is available under the MIT License. See the [LICENSE-MIT.md](LICENSE-MIT.md) file for more information.

## 📊 Component Reference

| Component | Purpose | Documentation |
|-----------|---------|---------------|
| VCMA | Version Control Master Agent | [Specification](vc_master_agent_spec.md) |
| VCLA | Version Control Listener Agent | [Specification](vc_listener_agent_spec.md) |
| CDIA | Code Documentation Inspector Agent | [Specification](code_doc_inspector_agent_spec.md) |
| RDIA | README Inspector Agent | [Specification](readme_inspector_agent_spec.md) |
| SAA | Static Analysis Agent | [Architecture](docs/markdown/saa_architecture.md) |
| FORCE | Federated Orchestration & Reporting | [Specification](FORCE.spec.md) |
| YUNG | Command Specification | [Specification](YUNG_spec.md) |