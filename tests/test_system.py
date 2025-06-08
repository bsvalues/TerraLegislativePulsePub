import pytest
from core.system import SystemState

async def test_system_initialization(precision_automation):
    assert precision_automation.state == SystemState.RUNNING
    assert precision_automation.metrics.active_tasks == 0
    assert precision_automation.metrics.error_count == 0

async def test_task_execution(precision_automation):
    async def test_task():
        return "success"
        
    task = await precision_automation.execute_task("test_task", test_task)
    result = await task
    assert result == "success"
    assert precision_automation.metrics.active_tasks == 0

async def test_error_handling(precision_automation):
    async def failing_task():
        raise ValueError("Test error")
        
    error_handler_called = False
    async def error_handler(error):
        nonlocal error_handler_called
        error_handler_called = True
        assert isinstance(error, ValueError)
        
    precision_automation.register_error_handler("failing_task", error_handler)
    
    task = await precision_automation.execute_task("failing_task", failing_task)
    with pytest.raises(ValueError):
        await task
        
    assert error_handler_called
    assert precision_automation.metrics.error_count == 1

async def test_system_shutdown(precision_automation):
    await precision_automation.shutdown()
    assert precision_automation.state == SystemState.SHUTDOWN
    assert len(precision_automation.tasks) == 0 