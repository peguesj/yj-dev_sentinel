"""
ANCHOR: Test Documentation
Test suite for ForceEngine and ToolExecutor functionality.
Strictly adheres to Pytest type casting best practices and verbose documentation standards.
"""
import pytest
from typing import Dict, Any
from dev_sentinel.force import ForceEngine, ToolExecutionError, SchemaValidationError

# ANCHOR: Type Safety - All test functions use explicit type hints
@pytest.fixture
def force_engine() -> ForceEngine:
    """
    ANCHOR: Test Documentation
    Fixture to initialize ForceEngine for tests.
    """
    return ForceEngine()

# ANCHOR: Type Safety
@pytest.mark.parametrize("tool_id,parameters", [
    ("analyze_code_changes", {"since_commit": "HEAD~1", "focus_areas": ["performance", "security"]}),
    ("code_quality_check", {"target": "src/", "linters": ["flake8", "pylint"], "target_files": ["src/main.py", "src/utils.py"]}),
    ("git_commit", {"message": "test commit", "scope": "test"})
])
def test_execute_tool_success(force_engine: ForceEngine, tool_id: str, parameters: Dict[str, Any]) -> None:
    """
    ANCHOR: Test Documentation
    Test successful execution of Force tools with valid parameters.
    """
    result: Dict[str, Any] = force_engine.execute_tool_sync(tool_id, parameters)
    assert result["success"] is True, f"Tool {tool_id} should execute successfully."
    assert "executionId" in result, "Execution ID should be present."
    assert "result" in result, "Result should be present."

# ANCHOR: Type Safety
@pytest.mark.parametrize("tool_id,parameters", [
    ("analyze_code_changes", {"sinceCommit": 123}),  # Invalid type
    ("code_quality_check", {"target": 42}),          # Invalid type
])
def test_execute_tool_type_error(force_engine: ForceEngine, tool_id: str, parameters: Dict[str, Any]) -> None:
    """
    ANCHOR: Test Documentation
    Test that invalid parameter types raise ToolExecutionError.
    """
    with pytest.raises(ToolExecutionError):
        force_engine.execute_tool_sync(tool_id, parameters)

# ANCHOR: Type Safety
@pytest.mark.parametrize("tool_id", [
    "nonexistent_tool",
    "invalid_tool"
])
def test_execute_tool_not_found(force_engine: ForceEngine, tool_id: str) -> None:
    """
    ANCHOR: Test Documentation
    Test that executing a nonexistent tool raises ToolExecutionError.
    """
    with pytest.raises(ToolExecutionError):
        force_engine.execute_tool_sync(tool_id, {})

# ANCHOR: Test Documentation
@pytest.mark.parametrize("tool_id,parameters", [
    ("analyze_code_changes", {"since_commit": "HEAD~1", "focus_areas": ["performance", "security"]}),
])
def test_learning_record_created(force_engine: ForceEngine, tool_id: str, parameters: Dict[str, Any]) -> None:
    """
    ANCHOR: Type Safety
    Test that learning records are created after tool execution.
    """
    initial_count: int = len(force_engine._learning_records)
    force_engine.execute_tool_sync(tool_id, parameters)
    assert len(force_engine._learning_records) > initial_count, "Learning record should be created."
