
# FORCE Engine Specification (v0.5.0)


# FORCE Engine Specification (v0.5.0)

| Version | Date       | Author   | Description                                  |
|---------|------------|----------|----------------------------------------------|
| v0.5.0  | 2025-07-16 | peguesj  | Release: Variant support, schema, docs update |

![Build Status](https://img.shields.io/github/actions/workflow/status/peguesj/yj-dev_sentinel/ci.yml?branch=main)
![Release](https://img.shields.io/github/v/release/peguesj/yj-dev_sentinel)
- **Variant**: New Force component for session orchestration and prompt engineering
- **Schema**: Extended with open enums, new oneOf, and anchors for orchestration
- **Tools**: Learning tool, execution analytics, and more


## Variant Component (v0.5.0)

### Definition

The **Variant** is a first-class Force component designed for session orchestration, prompt engineering, and agentic workflow customization. Variants encapsulate prompt instructions, behavioral rules, session context, and orchestration targets, enabling advanced agentic systems to adapt, specialize, and coordinate their behavior.

**Key Use Cases:**
- Defining system messages and behavioral rules for agentic tools (e.g., Copilot, Cursor, Claude)
- Orchestrating multi-agent sessions with distinct personas, goals, and environments
- Anchoring constraints, governance, patterns, and learnings to session logic

### Schema Excerpt

```json
{
  "id": "variant_example",
  "name": "GitHub Copilot Orchestration",
  "description": "Session orchestration for Copilot-style agentic coding.",
  "category": "orchestration",
  "instructions": "You are a coding assistant. Follow user intent and coding best practices.",
  "rules": [
    "Never write insecure code.",
    "Always explain complex changes.",
    "Respect project conventions."
  ],
  "context": {
    "persona": "coding assistant",
    "goals": ["accelerate development", "reduce errors"],
    "environment": "vscode",
    "examples": [
      {"input": "Add a function for JWT validation.", "output": "def validate_jwt(token): ..."}
    ]
  },
  "targets": ["github_copilot"],
  "anchors": {
    "constraints": ["drtw"],
    "governance": [],
    "patterns": [],
    "learnings": []
  },
  "metadata": {
    "created": "2025-07-16T00:00:00Z",
    "updated": "2025-07-16T00:00:00Z",
    "version": "0.5.0",
    "author": "peguesj",
    "tags": ["copilot", "orchestration"]
  }
}
```

### Usage

- Place Variant JSON files in `.force/variants/`.
- Reference Variants in orchestration, tool, or pattern definitions.
- Use anchors to enforce constraints, governance, and learning integration.

### Example: Multi-Agent Orchestration

Define multiple Variants for different agentic tools (e.g., Copilot, Cursor, Claude) and orchestrate a session by selecting the appropriate Variant based on user context or workflow.

---
