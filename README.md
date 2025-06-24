# Dev Sentinel: Force-Enabled Autonomous Development Platform

<div align="center">
  <img src="docs/diagrams/dev_sentinel_logo.svg" alt="Dev Sentinel Logo" width="200"/>
  
  **Version: 2.0.0**  
  **Date: June 24, 2025**  
  **Author: Jeremiah Pegues <jeremiah@pegues.io>**  
  **Organization: Pegues OPSCORP LLC**  
  **License: [MIT](LICENSE-MIT.md)**
  
  [![Built with: Python](https://img.shields.io/badge/Built%20with-Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
  [![Architecture: Force-Enabled](https://img.shields.io/badge/Architecture-Force%20Enabled-009688?logo=blueprint&logoColor=white)](docs/.force/README.md)
  [![Documentation: PlantUML](https://img.shields.io/badge/Documentation-PlantUML-orange?logo=diagram&logoColor=white)](docs/diagrams/)
  [![Force System: Active](https://img.shields.io/badge/Force%20System-Active-brightgreen?logo=star&logoColor=white)](docs/.force/)
</div>

## 📋 Overview

Dev Sentinel is a modernized, schema-driven autonomous development platform that combines proven agent-based architecture with the sophisticated Force agentic framework. The system provides comprehensive development assistance through intelligent tools, proven patterns, automated constraints, continuous learning, and governance enforcement.

### 🚀 What's New in Version 2.0

- **Force System Integration**: Complete schema-driven development framework
- **Enhanced MCP Support**: Advanced Model Context Protocol integration for VS Code
- **Self-Learning Capabilities**: System learns and optimizes from usage patterns
- **Governance Framework**: Automated quality gates and compliance enforcement
- **Pattern-Driven Development**: Codified best practices with measurable outcomes
- **Advanced Tool System**: Parameterized, validated tools with comprehensive error handling

### Key Features

- **🛠️ Schema-Driven Tools**: Validated, parameterized development tools with comprehensive monitoring
- **📋 Pattern Management**: Proven development workflows with context-aware application
- **🔒 Constraint Enforcement**: Automated quality gates with auto-fix capabilities
- **🧠 Learning System**: Continuous optimization through execution analytics and pattern recognition
- **🏛️ Governance Framework**: Policy enforcement with configurable quality gates
- **🤖 Autonomous Agents**: Legacy agent compatibility with modern Force integration
- **📊 Real-time Analytics**: Performance monitoring and optimization insights
- **🔌 MCP Integration**: Full Model Context Protocol support with Force capabilities
- **🔄 Version Control Intelligence**: Advanced git workflow management with semantic versioning
- **📚 Documentation Quality**: Automated analysis, validation, and synchronization

## 🏛️ System Architecture

Dev Sentinel is built on a modular, event-driven architecture with specialized agents that communicate through a central message bus. The diagram below illustrates the high-level architecture:

<details>
<summary>System Architecture Diagram (PlantUML)</summary>

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
</details>

<details>
<summary>System Architecture Diagram (Mermaid)</summary>

```mermaid
graph TB
    %% Define subgraphs
    subgraph "Dev Sentinel Core"
        subgraph MB["Message Bus"]
            TR["Topic Registry"]
            SM["Subscription Manager"]
            MQ["Message Queue"]
        end
        subgraph TM["Task Manager"]
            TQ["Task Queue"]
            TD["Task Dispatcher"]
            RC["Result Collector"]
        end
        API["Agent API"]
    end
    
    subgraph "Specialized Agents"
        subgraph VCMA["Version Control<br>Master Agent<br>(VCMA)"]
            RM["Repository Monitor"]
            CA["Commit Analyzer"]
            VC["VCLA Coordinator"]
        end
        subgraph VCLA["Version Control<br>Listener Agent<br>(VCLA)"]
            PM["Path Monitor"]
            CD["Change Detector"]
        end
        subgraph CDIA["Code Documentation<br>Inspector Agent<br>(CDIA)"]
            DSP["DocString Parser"]
            COA["Coverage Analyzer"]
        end
        subgraph RDIA["README<br>Inspector Agent<br>(RDIA)"]
            MP["Markdown Parser"]
            SV["Section Validator"]
        end
        subgraph SAA["Static Analysis<br>Agent<br>(SAA)"]
            MLA["Multi-language<br>Analyzer"]
            ID["Issue Detector"]
        end
    end
    
    subgraph "Integration Layer"
        subgraph FORCE["FORCE"]
            TM_FORCE["Terminal Manager"]
            CP_FORCE["Command Processor"]
            MA_FORCE["Master Agent"]
        end
        subgraph FAST["Fast-Agent"]
            ADAPTER["Adapter"]
            MCP["MCP Servers"]
        end
        subgraph DIAG["Diagram Generator"]
            PUML["PlantUML Engine"]
            MERM["Mermaid Engine"]
        end
    end
    
    subgraph "External Systems"
        GIT["Git"]
        CICD["CI/CD"]
        IDE["Development<br>Environment"]
    end
    
    %% Core Connections
    MB --- API
    API --- TM
    
    %% Agent connections to core
    VCMA --- API
    VCLA --- API
    CDIA --- API
    RDIA --- API
    SAA --- API
    
    %% Agent relationships
    VCMA --- VCLA
    VCMA --- CDIA
    VCMA --- RDIA
    CDIA --- SAA
    
    %% Integration connections
    FORCE --- MB
    FAST --- FORCE
    DIAG --- MB
    
    %% External system connections
    VCMA --- GIT
    VCLA --- GIT
    FAST --- CICD
    IDE --- FORCE
    
    %% Message flow examples
    MB -.-> VCMA
    VCMA -.-> MB
    MB -.-> CDIA
    CDIA -.-> MB
    TM -.-> SAA
    SAA -.-> TM
    
    %% Style nodes
    classDef core fill:#4D7A97,stroke:#000000,color:#fff
    classDef agent fill:#6597B2,stroke:#000000,color:#fff
    classDef integration fill:#F3B95F,stroke:#000000,color:#fff
    classDef external fill:#93A1A1,stroke:#000000,color:#fff
    
    class MB,TM,API core
    class VCMA,VCLA,CDIA,RDIA,SAA agent
    class FORCE,FAST,DIAG integration
    class GIT,CICD,IDE external
```
</details>

### Core Components

The Dev Sentinel system is built around these core components:

#### Message Bus

The Message Bus provides a pub/sub mechanism for asynchronous communication between agents:

<details>
<summary>Message Bus Architecture (PlantUML)</summary>

```plantuml
@startuml Message Bus Architecture
!theme plain
skinparam backgroundColor transparent
skinparam defaultFontSize 14

' Define colors
!$core_color = "#4D7A97"
!$component_color = "#6597B2"
!$interface_color = "#D6EAF8"

' Core component
class MessageBus {
  - topics: Dict[str, Set[AgentCallback]]
  - message_queue: Queue
  + register_agent(agent: BaseAgent)
  + subscribe(topic: str, callback: AgentCallback)
  + unsubscribe(topic: str, callback: AgentCallback)
  + publish(topic: str, message: Message)
  - _dispatch_messages()
  - _process_queue()
}

' Message handling
class Message {
  + topic: str
  + content: Dict
  + sender_id: str
  + timestamp: datetime
  + id: str
  + get_content()
  + to_dict()
  + from_dict()
}

' Interfaces
interface AgentCallback {
  + __call__(message: Message)
}

' Context manager for automatic unsubscribe
class Subscription {
  - topic: str
  - callback: AgentCallback
  - message_bus: MessageBus
  + __enter__()
  + __exit__()
}

' Relationships
MessageBus --> "0..*" Message: processes >
MessageBus --> "0..*" AgentCallback: notifies >
MessageBus --> "0..*" Subscription: creates >
Subscription --> MessageBus: unsubscribes from >

@enduml
```
</details>

<details>
<summary>Message Bus Architecture (Mermaid)</summary>

```mermaid
classDiagram
    class MessageBus {
        -topics: Dict[str, Set[AgentCallback]]
        -message_queue: Queue
        +register_agent(agent: BaseAgent)
        +subscribe(topic: str, callback: AgentCallback)
        +unsubscribe(topic: str, callback: AgentCallback)
        +publish(topic: str, message: Message)
        -_dispatch_messages()
        -_process_queue()
    }

    class Message {
        +topic: str
        +content: Dict
        +sender_id: str
        +timestamp: datetime
        +id: str
        +get_content()
        +to_dict()
        +from_dict()
    }

    class AgentCallback {
        +__call__(message: Message)
    }

    class Subscription {
        -topic: str
        -callback: AgentCallback
        -message_bus: MessageBus
        +__enter__()
        +__exit__()
    }

    MessageBus --> Message : "processes >"
    MessageBus --> AgentCallback : "notifies >"
    MessageBus --> Subscription : "creates >"
    Subscription --> MessageBus : "unsubscribes from >"
```
</details>

The Message Bus uses a topic-based publish-subscribe pattern, allowing agents to communicate without direct dependencies.

#### Task Manager

Handles the creation, distribution, and tracking of tasks across the system, enabling asynchronous workload management.

<details>
<summary>Task Manager Architecture (PlantUML)</summary>

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
</details>

<details>
<summary>Task Manager Architecture (Mermaid)</summary>

```mermaid
classDiagram
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

    class TaskStatus {
        <<enumeration>>
        PENDING
        IN_PROGRESS
        COMPLETED
        FAILED
        CANCELLED
    }

    TaskManager *-- Task : "manages >"
    Task *-- TaskStatus : "has >"
    
    Agent1 --> TaskManager : "registers handlers >"
    Agent2 --> TaskManager : "registers handlers >"
    Agent3 --> TaskManager : "creates tasks >"
```
</details>

#### BaseAgent

The foundation for all agent implementations in the system, providing common functionality and lifecycle management.

<details>
<summary>BaseAgent Architecture (PlantUML)</summary>

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
</details>

<details>
<summary>BaseAgent Architecture (Mermaid)</summary>

```mermaid
classDiagram
    class BaseAgent {
        <<abstract>>
        +agent_id: str
        +config: Dict[str, Any]
        +status: AgentStatus
        +logger: Logger
        +statistics: Dict[str, Any]
        #activity_log: List[Dict]
        #error_log: List[Dict]
        +__init__(agent_id: Optional[str], config: Optional[Dict])
        +start(): Awaitable[None]
        +shutdown(): Awaitable[None]
        +update_status(status: AgentStatus): None
        +get_agent_state(): Dict[str, Any]
        +log_activity(activity_type: str, details: Dict): None
        +log_error(error_type: str, message: str, details: Dict): None
    }

    class AgentStatus {
        <<enumeration>>
        INITIALIZING
        IDLE
        BUSY
        ERROR
        PAUSED
        TERMINATED
    }

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

    BaseAgent *-- AgentStatus : "has >"
    BaseAgent <|-- VersionControlMasterAgent
    BaseAgent <|-- VersionControlListenerAgent
    BaseAgent <|-- CodeDocumentationInspectorAgent
    BaseAgent <|-- READMEInspectorAgent
    BaseAgent <|-- StaticAnalysisAgent
```
</details>

## 🤖 Agent Components

Dev Sentinel uses specialized agents for different aspects of the development workflow:

### Version Control Master Agent (VCMA)

Proactively manages version control operations by observing code changes and making intelligent decisions about when and what to commit.

<details>
<summary>VCMA Architecture (PlantUML)</summary>

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
</details>

<details>
<summary>VCMA Architecture (Mermaid)</summary>

```mermaid
classDiagram
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
    
    VersionControlMasterAgent -- VersionControlListenerAgent : "coordinates >"
    VersionControlMasterAgent -- MessageBus : "publishes to >"
    VersionControlMasterAgent -- TaskManager : "handles tasks from >"
```
</details>

**Key Responsibilities:**
- Repository state tracking and versioning
- Commit analysis and history management
- VCLA coordination and delegation
- Smart commit decision-making

[View the complete VCMA specification](vc_master_agent_spec.md)

### Version Control Listener Agent (VCLA)

Monitors specific aspects of the repository, focusing on particular paths, file types, or behaviors as delegated by the VCMA.

<details>
<summary>VCLA Architecture (PlantUML)</summary>

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
</details>

<details>
<summary>VCLA Architecture (Mermaid)</summary>

```mermaid
classDiagram
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
    
    VersionControlListenerAgent -- VersionControlMasterAgent : "reports to >"
    VersionControlListenerAgent -- MessageBus : "publishes to >"
    VersionControlListenerAgent -- TaskManager : "handles tasks from >"
```
</details>

**Key Responsibilities:**
- Path-specific file monitoring
- Change detection and notification
- Specialized observation of repository components

[View the complete VCLA specification](vc_listener_agent_spec.md)

### Code Documentation Inspector Agent (CDIA)

Evaluates and improves in-code documentation quality across a codebase, supporting multiple programming languages.

<details>
<summary>CDIA Architecture (PlantUML)</summary>

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
</details>

<details>
<summary>CDIA Architecture (Mermaid)</summary>

```mermaid
classDiagram
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
    
    CodeDocumentationInspectorAgent -- MessageBus : "publishes to >"
    CodeDocumentationInspectorAgent -- TaskManager : "handles tasks from >"
    CodeDocumentationInspectorAgent -- VersionControlMasterAgent : "receives updates from >"
```

</details>

**Key Responsibilities:**
- Documentation pattern detection
- Coverage calculation and reporting
- Multi-language support
- Issue identification and notification

[View the complete CDIA specification](code_doc_inspector_agent_spec.md)

### README Inspector Agent (RDIA)

Ensures README files align with best practices, providing suggestions for improvement.

<details>
<summary>RDIA Architecture (PlantUML)</summary>

```plantuml
@startuml RDIA Architecture
!theme plain
skinparam backgroundColor transparent
skinparam linetype ortho

class ReadmeInspectorAgent {
  +current_tasks: Dict[str, Task]
  +readme_standards: Dict[str, Dict]
  +__init__(agent_id: Optional[str], config: Optional[Dict])
  +start(): Awaitable[None]
  +process_task(task: Task): Awaitable[Dict]
  -_analyze_readme(file_path: str): Awaitable[Dict]
  -_validate_against_standards(content: str): Awaitable[Dict]
  -_generate_improvement_recommendations(analysis: Dict): Awaitable[Dict]
  -_handle_inspect_readme_task(task: Task): Awaitable[Dict]
  -_handle_improve_readme_task(task: Task): Awaitable[Dict]
  +shutdown(): Awaitable[None]
}

BaseAgent <|-- ReadmeInspectorAgent

ReadmeInspectorAgent -- MessageBus : publishes to >
ReadmeInspectorAgent -- TaskManager : handles tasks from >
ReadmeInspectorAgent -- "README Files" : analyzes >

@enduml
```
</details>

<details>
<summary>RDIA Architecture (Mermaid)</summary>

```mermaid
classDiagram
    class ReadmeInspectorAgent {
        +current_tasks: Dict[str, Task]
        +readme_standards: Dict[str, Dict]
        +__init__(agent_id: Optional[str], config: Optional[Dict])
        +start(): Awaitable[None]
        +process_task(task: Task): Awaitable[Dict]
        -_analyze_readme(file_path: str): Awaitable[Dict]
        -_validate_against_standards(content: str): Awaitable[Dict]
        -_generate_improvement_recommendations(analysis: Dict): Awaitable[Dict]
        -_handle_inspect_readme_task(task: Task): Awaitable[Dict]
        -_handle_improve_readme_task(task: Task): Awaitable[Dict]
        +shutdown(): Awaitable[None]
    }

    BaseAgent <|-- ReadmeInspectorAgent

    ReadmeInspectorAgent -- MessageBus : "publishes to >"
    ReadmeInspectorAgent -- TaskManager : "handles tasks from >"
    ReadmeInspectorAgent -- "README Files" : "analyzes >"
```
</details>

**Key Responsibilities:**
- README section validation
- Content quality assessment
- Markdown structure analysis
- Cross-referencing with codebase

[View the complete RDIA specification](readme_inspector_agent_spec.md)

### Static Analysis Agent (SAA)

Analyzes code for potential issues, security vulnerabilities, and adherence to best practices.

<details>
<summary>SAA Architecture (PlantUML)</summary>

```plantuml
@startuml SAA Architecture
!theme plain
skinparam backgroundColor transparent
skinparam linetype ortho

class StaticAnalysisAgent {
  +repo_path: str
  +analysis_tools: Dict[str, Dict]
  +last_analyzed_commit: Optional[str]
  +__init__(agent_id: Optional[str], config: Optional[Dict])
  +start(): Awaitable[None]
  +process_task(task: Task): Awaitable[Dict]
  -_handle_commit_analyzed(message: Dict): Awaitable[None]
  -_handle_repo_refreshed(message: Dict): Awaitable[None]
  -_handle_analyze_code_task(task: Task): Awaitable[Dict]
  +analyze_code(file_path: str, commit_info: Optional[Dict]): Awaitable[Dict]
  -_run_static_analysis(file_path: str): Dict
  -_run_tool(tool: str, file_path: str): Dict
  +shutdown(): Awaitable[None]
}

BaseAgent <|-- StaticAnalysisAgent

StaticAnalysisAgent -- MessageBus : publishes to >
StaticAnalysisAgent -- TaskManager : handles tasks from >
StaticAnalysisAgent -- VersionControlMasterAgent : receives updates from >

@enduml
```
</details>

<details>
<summary>SAA Architecture (Mermaid)</summary>

```mermaid
classDiagram
    class StaticAnalysisAgent {
        +repo_path: str
        +analysis_tools: Dict[str, Dict]
        +last_analyzed_commit: Optional[str]
        +__init__(agent_id: Optional[str], config: Optional[Dict])
        +start(): Awaitable[None]
        +process_task(task: Task): Awaitable[Dict]
        -_handle_commit_analyzed(message: Dict): Awaitable[None]
        -_handle_repo_refreshed(message: Dict): Awaitable[None]
        -_handle_analyze_code_task(task: Task): Awaitable[Dict]
        +analyze_code(file_path: str, commit_info: Optional[Dict]): Awaitable[Dict]
        -_run_static_analysis(file_path: str): Dict
        -_run_tool(tool: str, file_path: str): Dict
        +shutdown(): Awaitable[None]
    }

    BaseAgent <|-- StaticAnalysisAgent
    
    StaticAnalysisAgent -- MessageBus : "publishes to >"
    StaticAnalysisAgent -- TaskManager : "handles tasks from >"
    StaticAnalysisAgent -- VersionControlMasterAgent : "receives updates from >"
```
</details>

**Key Responsibilities:**
- Multi-language code analysis
- Code quality issue detection
- Static analysis tool integration
- Issue reporting and tracking

## 🔌 Integration Architecture

### FORCE: Federated Orchestration & Reporting

The [FORCE architecture](FORCE.spec.md) provides a federated approach to agent orchestration, telemetry collection, and operation reporting:

<details>
<summary>FORCE Architecture (PlantUML)</summary>

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
</details>

<details>
<summary>FORCE Architecture (Mermaid)</summary>

```mermaid
graph TD
    User((User))
    subgraph FORCE_Architecture[FORCE Architecture]
        subgraph MA[Master Agent]
            YCP[YUNG Command Parser]
            CP[Command Processor]
            TC[Telemetry Collector]
            OR[Operation Reporter]
        end
        subgraph TM[Terminal Manager]
            TSR[Terminal Session Registry]
            TSP[Terminal State Persistence]
            EM[Environment Manager]
        end
        subgraph Subagent_Terminals[Subagent Terminals]
            VT[VCS Terminal]
            GC[Git Context]
            DT[Documentation Terminal]
            DC[Doc Context]
            CT[Code Terminal]
            CC[Code Context]
            IT[Infrastructure Terminal]
            IC[Infra Context]
            TT[Testing Terminal]
            TC2[Test Context]
            FT[Fast-Agent Terminal]
            MC[MCP Context]
        end
    end
    subgraph Integration_Layer[Integration Layer]
        subgraph FA[Fast-Agent]
            MCPBridge[MCP Bridge]
            Adapters[Agent Adapters]
            Servers[MCP Servers]
        end
        subgraph DG[Diagram Generator]
            PE[PlantUML Engine]
            ME[Mermaid Engine]
            AAG[ASCII Art Generator]
        end
    end
    subgraph External_Systems[External Systems]
        GitRepo[Git Repository]
        DevEnv[Development Environment]
        CICD[CI/CD Pipeline]
    end
    
    %% Command flow connections
    User-->|"Commands"|MA
    MA-->|"parses command"|YCP
    YCP-->|"processes command"|CP
    CP-->|"$VCS commands"|VT
    CP-->|"$DOC commands"|DT
    CP-->|"$CODE commands"|CT
    CP-->|"$INFRA commands"|IT
    CP-->|"$TEST commands"|TT
    CP-->|"$FAST commands"|FT
    CP-->|"$DIAGRAM commands"|DG
    
    %% Terminal registry connections
    VT-->|"registers"|TM
    DT-->|"registers"|TM
    CT-->|"registers"|TM
    IT-->|"registers"|TM
    TT-->|"registers"|TM
    FT-->|"registers"|TM
    
    %% Management connections
    TM-->|"persists state"|TSP
    TSR-->|"manages"|EM
    
    %% External system connections
    VT-->|"interacts with"|GitRepo
    FA-->|"integrates with"|CICD
    MA-->|"monitors"|DevEnv
    
    %% Implementation connections - fixing the syntax error
    VT-.->|"implements operation"|FA
    DT-.->|"implements operation"|FA
    CT-.->|"implements operation"|FA
    IT-.->|"implements operation"|FA
    TT-.->|"implements operation"|FA
    FT-.->|"implements operation"|FA
    
    %% Example flow (dotted lines)
    User-.->|"$VCS COMMIT 'fix: update documentation'"|MA
    MA-.->|"delegates command"|VT
    VT-.->|"executes git commit"|GitRepo
    VT-.->|"updates terminal state"|TM
    VT-.->|"reports result"|MA
```
</details>

### Terminal State Management

The Terminal Manager maintains persistent state for each specialized agent terminal:

<details>
<summary>Terminal State Management (PlantUML)</summary>

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
</details>

<details>
<summary>Terminal State Management (Mermaid)</summary>

```mermaid
classDiagram
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
```
</details>

## � MCP Integration

Dev Sentinel provides modern integration with the Model Context Protocol (MCP), enabling seamless integration with VS Code and other MCP-compatible development tools. The MCP integration allows you to interact with Dev Sentinel agents directly from your development environment.

### Features

- **Direct Tool Integration**: Access Dev Sentinel capabilities as VS Code tools
- **Async Command Processing**: Full async/await support for responsive interactions
- **Agent-Specific Adapters**: Specialized adapters for each agent type with tailored command vocabularies
- **Dynamic Capability Discovery**: Runtime discovery of agent capabilities and supported commands
- **Error Recovery**: Graceful handling of errors with informative feedback

### Architecture

The MCP integration consists of three main components:

1. **MCP Server** (`integration/fast_agent/mcp_servers.py`)
   - Implements the MCP protocol for tool integration
   - Provides standardized tool schemas for external systems
   - Handles command routing and response formatting

2. **Adapter Framework** (`integration/fast_agent/adapter.py`)
   - Abstract base classes for extensible adapter patterns
   - MCP-specific adapters with async initialization
   - Dynamic capability reporting and error handling

3. **Specialized Adapters** (`integration/fast_agent/specialized_adapters.py`)
   - Agent-specific adapters for each Dev Sentinel agent:
     - `VCMAAdapter` - Version Control Master Agent operations
     - `VCLAAdapter` - Version Control Listener Agent monitoring
     - `CDIAAdapter` - Code Documentation Inspector operations
     - `RDIAAdapter` - README Documentation Inspector operations
     - `SAAAdapter` - Static Analysis Agent operations

### Usage

#### Basic Agent Interaction
```python
from integration.fast_agent.specialized_adapters import create_specialized_adapter

# Create specialized adapter for any agent
adapter = await create_specialized_adapter(agent, adapter_type="mcp")

# Execute agent-specific commands
result = await adapter.process_command("analyze_commits", {
    "repository_path": "/path/to/repo",
    "branch": "main"
})
```

#### Running the MCP Server
```python
from integration.fast_agent.mcp_servers import DevSentinelMCPServer

# Initialize and run MCP server
server = DevSentinelMCPServer()
await server.run()
```

### Installation

To use MCP integration, install the MCP package:

```bash
pip install mcp
```

### VS Code Integration

1. Install a compatible MCP client for VS Code
2. Configure the client to connect to Dev Sentinel's MCP server
3. Access Dev Sentinel tools directly from the VS Code command palette

The MCP integration provides a modern, standards-compliant way to integrate Dev Sentinel with contemporary development workflows and tools.

## �🚀 Getting Started

Dev Sentinel requires Python 3.12 and several dependencies to run its agent-based architecture. Follow these steps to set up and start using the system:

### Prerequisites

- **Python 3.12** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Virtual Environment** - Recommended for dependency isolation

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/pegues/dev-sentinel.git

# Navigate to the project directory
cd dev-sentinel

# Set up a virtual environment (recommended)
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize the system
python -m integration.force.initialize
```

This initialization process sets up the FORCE architecture, including the message bus, task manager, terminal manager, and fast-agent integration. The command will provide a summary of successful component initializations.

### Starting the FORCE System

The FORCE (Federated Orchestration & Reporting for Copilot Execution) system is the coordination layer that manages agent communication. To start it:

```bash
# Start the master agent
python -m integration.force.master_agent
```

Once the master agent is running, you can interact with Dev Sentinel using YUNG commands in the terminal interface.

### Using YUNG Commands

YUNG (YES Ultimate Net Good) is the command language used to interact with Dev Sentinel. Some essential command examples:

```bash
# Version control operations
$VCS STATUS                    # Check repository status
$VCS COMMIT "fix: update docs" # Commit changes with a message

# Documentation inspection
$VIC DOCS                      # Validate documentation integrity
$VIC FILE=README.md            # Inspect specific file

# Code operations
$CODE TIER=BACKEND IMPL        # Implement backend code
$CODE ALL ANALYZE              # Analyze all code

# Diagram generation
$DIAGRAM ARCH FORMAT=svg       # Generate architecture diagram
$DIAGRAM FORCE FORMAT=png      # Generate FORCE integration diagram
```

For a complete reference of YUNG commands, see the [YUNG specification](YUNG_spec.md).

### MCP Server Setup for VS Code Integration

Dev Sentinel can be integrated with VS Code through the Model Context Protocol (MCP):

```bash
# Start the MCP server
python -m integration.fast_agent.dev_sentinel_server --http-port 8000 --mcp-port 8090
```

This starts two servers:
- An HTTP API server on port 8000 for command execution
- An MCP server on port 8090 for VS Code integration

To connect VS Code to Dev Sentinel:

1. Open VS Code settings and configure the MCP connection:
   ```json
   {
     "mcp.connections": [
       {
         "name": "Dev Sentinel",
         "url": "localhost:8090"
       }
     ]
   }
   ```
2. Connect to Dev Sentinel through the MCP panel in VS Code

VS Code now has native support for the Model Context Protocol, eliminating the need for additional extensions.

## 📊 User Journey Workflows

### Command Line Workflow

```mermaid
sequenceDiagram
    participant User
    participant MasterAgent as FORCE Master Agent
    participant SubagentTerminal as Subagent Terminal
    participant Agents as Specialized Agents
    participant Repository as Git Repository

    User->>MasterAgent: Start master_agent.py
    activate MasterAgent
    MasterAgent-->>User: Terminal ready for commands
    
    User->>MasterAgent: $VCS STATUS
    MasterAgent->>SubagentTerminal: Route to VCS terminal
    SubagentTerminal->>Repository: git status
    Repository-->>SubagentTerminal: Status results
    SubagentTerminal-->>MasterAgent: Command results
    MasterAgent-->>User: Display repository status
    
    User->>MasterAgent: $VIC DOCS
    MasterAgent->>SubagentTerminal: Route to documentation terminal
    SubagentTerminal->>Agents: Invoke RDIA for analysis
    Agents-->>SubagentTerminal: Analysis results
    SubagentTerminal-->>MasterAgent: Documentation validation results
    MasterAgent-->>User: Display validation summary and recommendations
    
    User->>MasterAgent: $DIAGRAM ARCH
    MasterAgent->>SubagentTerminal: Route to diagram generator
    SubagentTerminal->>Agents: Generate architecture diagram
    Agents-->>SubagentTerminal: Diagram generation complete
    SubagentTerminal-->>MasterAgent: Diagram location
    MasterAgent-->>User: Display diagram generation results
    deactivate MasterAgent
```

### VS Code Integration Workflow

```mermaid
sequenceDiagram
    participant User
    participant VSCode as VS Code
    participant FastAgent as Fast Agent Extension
    participant MCPServer as MCP Server
    participant DevSentinel as Dev Sentinel System
    participant Repository as Git Repository
    
    User->>User: Start MCP Server
    User->>VSCode: Open VS Code
    User->>FastAgent: Connect to Dev Sentinel (localhost:8090)
    FastAgent->>MCPServer: Establish connection
    MCPServer-->>FastAgent: Connection established
    
    User->>FastAgent: Enter prompt about code documentation
    FastAgent->>MCPServer: Send prompt
    MCPServer->>DevSentinel: Process prompt as YUNG command
    DevSentinel->>Repository: Analyze repository
    Repository-->>DevSentinel: Repository data
    DevSentinel-->>MCPServer: Analysis and recommendations
    MCPServer-->>FastAgent: Response with action plan
    FastAgent-->>VSCode: Display response and actions
    VSCode-->>User: Show recommendations
    
    User->>FastAgent: Accept recommendations
    FastAgent->>MCPServer: Execute recommended actions
    MCPServer->>DevSentinel: Process actions
    DevSentinel->>Repository: Make changes
    Repository-->>DevSentinel: Update confirmation
    DevSentinel-->>MCPServer: Action results
    MCPServer-->>FastAgent: Update status
    FastAgent-->>VSCode: Refresh with changes
    VSCode-->>User: Show updated code
```

### Python API Integration Workflow

```mermaid
sequenceDiagram
    participant Application as Python Application
    participant MessageBus as Message Bus
    participant TaskManager as Task Manager
    participant Agents as Specialized Agents
    participant Repository as External Systems
    
    Application->>MessageBus: Initialize MessageBus
    Application->>TaskManager: Initialize TaskManager(message_bus)
    
    Application->>Agents: Create and initialize agents
    Agents-->>MessageBus: Subscribe to relevant topics
    
    Application->>TaskManager: create_task("analyze_repo", params)
    TaskManager->>Agents: Route task to appropriate agent
    Agents->>Repository: Perform operations
    Repository-->>Agents: Operation results
    Agents->>TaskManager: update_task_status(results)
    TaskManager-->>Application: Task completion status
    
    Application->>MessageBus: publish("vc.analyze", message)
    MessageBus->>Agents: Notify subscribed agents
    Agents->>Repository: Process message
    Repository-->>Agents: Processing results
    Agents->>MessageBus: publish("vc.analysis_complete", results)
    MessageBus-->>Application: Notification of completion
```

## 📚 Implementation Resources

Resources for setting up and extending Dev Sentinel:

### Core Dependencies

- **Python 3.12+**: [Python Documentation](https://docs.python.org/3.12/)
- **Pydantic 2.0+**: [Pydantic Documentation](https://docs.pydantic.dev/latest/) - Data validation
- **aiohttp**: [aiohttp Documentation](https://docs.aiohttp.org/en/stable/) - Async HTTP client/server

### MCP and Fast Agent Integration

- **Model Context Protocol**: [MCP Documentation](https://github.com/microsoft/model-context-protocol) - Protocol for integrating AI models
- **Fast Agent for VS Code**: [Fast Agent Extension](https://marketplace.visualstudio.com/items?itemName=FastAGI.fast-agent-agent) - VS Code integration

### Diagramming Tools

- **PlantUML**: [PlantUML Documentation](https://plantuml.com/guide) - UML diagram generation
- **Mermaid.js**: [Mermaid Documentation](https://mermaid.js.org/intro/) - Markdown-based diagramming

### Version Control Integration

- **GitPython**: [GitPython Documentation](https://gitpython.readthedocs.io/en/stable/) - Git repository management

For detailed specifications of Dev Sentinel components, refer to:
- [FORCE Architecture Specification](FORCE.spec.md)
- [YUNG Command Specification](YUNG_spec.md)
- [README Inspector Agent (RDIA) Specification](readme_inspector_agent_spec.md)
- [Code Documentation Inspector Agent (CDIA) Specification](code_doc_inspector_agent_spec.md)