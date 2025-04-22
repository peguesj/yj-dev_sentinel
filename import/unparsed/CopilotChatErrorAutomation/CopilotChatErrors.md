# GitHub Copilot Chat Error Documentation

## Error: No lowest priority node found
- **Cause**: Triggered in agent mode due to invalid or unresolved prompt tree states.
- **Resolution**:
  - Reload VS Code (`Developer: Reload Window`)
  - Modify prompt or reset conversation
  - Execute retry sequence

## Error: Error on conversation request
- **Cause**: Authentication issue or token timeout
- **Resolution**:
  - Re-authenticate GitHub via Command Palette
  - Reload window

## Error: Cannot read properties of undefined (reading 'map')
- **Cause**: Multiple open chat panes or state desync
- **Resolution**:
  - Close extra panes
  - Reload VS Code

## Error: fetch failed / ConnectTimeoutError
- **Cause**: Network fault or proxy issues
- **Resolution**:
  - Retry
  - Check connection/proxy
