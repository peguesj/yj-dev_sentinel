# YUNG: YES Ultimate Net Good - Universal Instruction Set

**Version: 0.1.0**  
**Date: May 1, 2025**  
**Author: Jeremiah Pegues <jeremiah@pegues.io>**  
**Organization: Pegues OPSCORP LLC**  
**License: MIT**

## Overview

YUNG (YES Ultimate Net Good) is a universal instruction set designed for the Dev Sentinel agentic environment, enabling standardized command execution across autonomous agents while supporting human-agent interaction. This instruction set provides a consistent interface for controlling agent behavior, requesting specific operations, and managing workflow execution.

## Command Structure

### General Format

```
$<COMMAND> [ARGS] [CHAINED_COMMANDS with ";"]
```

## Primary Commands

### Validation Commands

#### `$VIC [SCOPE]`

Validate integrity of the current codebase or documentation.

| Scope Option | Description |
|--------------|-------------|
| `ALL` | Validate full project structure |
| `LAST` | Validate last affected components |
| `DOCS` | Validate only documentation assets |
| `FILE=<filepath>` | Validate a specific file |

**Example:**
```
$VIC FILE=/path/to/file.js
```

### Code Generation Commands

#### `$CODE [SCOPE] [ACTIONS] [STAGE]`

Code generation, patching, or updates.

| Scope Option | Description |
|--------------|-------------|
| `TIER=FRONTEND` | Target frontend application tier |
| `TIER=BACKEND` | Target backend application tier |
| `TIER=ALL` | Target all application tiers |
| `ALL` | Apply across all tiers (equivalent to TIER=ALL) |

| Action Option | Description |
|--------------|-------------|
| `IMPL` | Implement or update logic |
| `COMMENT` | Generate/expand documentation comments and docstrings |
| `DOCS` | Create or enhance documentation files |
| `TEST` | Generate or update test suites |
| `PKG=<zip\|tar\|targz>` | Package the codebase |

**Stage** (optional): Branch or patch label (e.g., `Stage F-1`)

**Example:**
```
$CODE TIER=BACKEND IMPL,TEST Stage F-1
```

### Preprocessing Commands

#### `$PP <PREPROCESSOR>`

Preprocess external libraries, references, or structured files.

**Example:**
```
$PP PUML
```

### System Commands

#### `$CLOG`

Output the latest syslog-formatted debug logs from operations.

#### `$man`

Display this universal command manual.

#### `$$ or $man$`

Re-display this manual before and after executing a set of commands.

## Command Chaining & Conditionals

| Operator | Description |
|----------|-------------|
| `;` | Chain multiple commands in sequential order |
| `proceed` | Continue to the next logical step |
| `+proceed` | Proceed only if the preceding command returns success |
| `+context+proceed` | Add new contextual operations after successful prior step |
| `+proceed+context` | Proceed first, then immediately execute new contextual instructions |

**Example:**
```
$VIC FILE=src/app.js; $CODE TIER=BACKEND IMPL +proceed
```

## Staging, Branching, and Versioning

- Fixes or modifications must branch using the format:
  - `Stage F-<n>` (e.g., `Stage F-1` for first patch)
  
- Archives and branch outputs should be logically named:
  - Example: `stage-f1.tgz`

- All project documentation must inherit:
  - Authorship metadata
  - Semantic versioning (if modifying specs or code-level documentation)

## Automatic Default Rules

- All `$CODE` commands imply an automatic:
  - `$VIC` after execution to validate structure
  - `$CLOG` unless explicitly disabled

- Silent Mode:
  - Commands proceed without verbose chat output unless an error occurs
  - Errors interrupt silent progression with critical debug output

- Packaging Defaults:
  - Archives default to `.tgz` unless `PKG` is explicitly defined otherwise

## Special Handling

### Preprocessing Requirements

Preprocessing (`$PP`) commands must:
- Load external libraries, assets, or structured files into internal memory
- Prepare for downstream RAG (Retrieval-Augmented Generation) usage

### Diagram Management

- Master architecture diagrams must be regenerated anytime application tiers, services, or logical structures are updated
- Nested diagram composition recommended when applicable (e.g., PlantUML)

### Environment Variables

- Always document expected environment variables such as `DATABASE_URL`, `REDIS_URL`, etc.

## Integration with Dev Sentinel Agents

The YUNG instruction set integrates with Dev Sentinel's agent architecture:

| Command | Primary Agent Handler | Supporting Agents |
|---------|----------------------|------------------|
| `$VIC` | Code Doc Inspector Agent (CDIA) | README Inspector Agent (RDIA) |
| `$CODE` | Static Analysis Agent (SAA) | Version Control Master Agent (VCMA) |
| `$PP` | Task Coordinator | All specialized agents |
| `$CLOG` | Agent Supervisor | All agents |

## User Interaction Model

YUNG supports a hybrid interaction model that enables:

1. **Direct Commands**: Users can issue explicit commands to perform specific tasks
2. **Conversational Requests**: Natural language that agents translate into YUNG commands
3. **Agent-Initiated Actions**: Autonomous operations with notification to users

### Interaction Examples:

```
# Direct command
$CODE TIER=FRONTEND IMPL

# Conversational equivalent
"Please implement the new button component on the frontend"

# Agent-initiated with notification
[Agent] "I've detected inconsistent documentation. Running $VIC DOCS to validate..."
```

## Notes

- Commands should be readable and operationalized by LLM agents or automation systems
- Full compliance with chaining, branching, and validation ensures maximum project integrity
- All system behaviors assume silent operation unless explicitly overridden for verbose interaction

---

*For more information on Dev Sentinel architecture and agent capabilities, refer to the [Dev Sentinel Design Document](dev_sentinel_design_document.md).*