# README Documentation Inspector Agent (RDIA)

> Version: 0.1.0

## Overview

The README Documentation Inspector Agent (RDIA) specializes in analyzing, validating, and improving markdown documentation files, particularly README files and other project documentation files. It ensures that project documentation is complete, accurate, and well-structured.

## Core Capabilities

### Markdown Analysis

The RDIA analyzes markdown documentation for quality and completeness:

- Structure validation (headers, sections)
- Content completeness checks
- Link validation (internal and external)
- Image reference validation
- Code block syntax checking
- Formatting consistency

### README Standard Enforcement

The agent ensures that README files follow best practices:

- Essential sections presence (Overview, Installation, Usage, etc.)
- Badge and shield accuracy
- Project metadata completeness
- License information validation
- Contributor guidelines presence

### Documentation Improvement

Provides suggestions to improve documentation:

- Content organization recommendations
- Readability improvements
- Missing information identification
- Markdown formatting enhancements
- Consistency recommendations

### Project Documentation Management

Manages overall project documentation:

- Documentation structure validation
- Cross-document link verification
- Documentation freshness assessment
- Terminology consistency checking

## System Interfaces

### Input Interfaces

The RDIA accepts the following inputs:

- Markdown files for analysis
- README validation requests
- Documentation structure check requests
- Improvement suggestion requests

### Output Interfaces

The RDIA produces the following outputs:

- Markdown analysis reports
- README validation results
- Documentation improvement suggestions
- Documentation structure recommendations

## Implementation

The RDIA is implemented in `agents/rdia/rdia_agent.py` and follows the standard Dev Sentinel agent architecture. It extends the base `Agent` class and implements the required interfaces.

### Key Components

- **MarkdownAnalyzer**: Analyzes markdown content and structure
- **READMEValidator**: Validates README content against standards
- **DocImprover**: Generates documentation improvements
- **LinkValidator**: Checks internal and external links

## Configuration

The RDIA can be configured in the `config/fastagent.config.yaml` file:

```yaml
agents:
  rdia:
    enabled: true
    analysis_scope:
      - "**/*.md"
      - "**/*.markdown"
    excluded_paths:
      - "node_modules/**"
    readme_requirements:
      require_overview: true
      require_installation: true
      require_usage: true
      require_license: true
      check_external_links: true
```

## Usage

The RDIA can be used to analyze README and markdown files:

```python
# Request README analysis
result = await message_bus.request(
    topic="rdia.analyze.request",
    message={
        "file_path": "README.md",
        "check_links": True
    },
    response_topic="rdia.analyze.response"
)
```

## Related Components

- [Code Documentation Inspector Agent (CDIA)](cdia.md) - Code documentation inspection
- [Documentation Tools](/docs/reference/tools/documentation-tools.md) - Tools for documentation management
