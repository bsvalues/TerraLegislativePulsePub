import pytest
from core.distributed import NodeState
import asyncio

async def test_node_registration(distributed_system):
    await distributed_system.register_node("node1", 1.0, "us-east")
    node_status = await distributed_system.get_node_status("node1")
    assert node_status is not None
    assert node_status["state"] == NodeState.ACTIVE.value
    assert node_status["capacity"] == 1.0
    assert node_status["location"] == "us-east"

async def test_task_submission(distributed_system, redis_client):
    await distributed_system.register_node("node1", 1.0, "us-east")
    await distributed_system.submit_task("task1", {"data": "test"}, priority=1)
    
    # Wait for task to be processed
    await asyncio.sleep(0.1)
    
    # Check Redis for task assignment
    task_data = await redis_client.get("node:node1:tasks")
    assert task_data is not None
    assert b"task1" in task_data

async def test_node_selection(distributed_system):
    await distributed_system.register_node("node1", 1.0, "us-east")
    await distributed_system.register_node("node2", 2.0, "us-west")
    
    # Submit tasks to fill node1
    for i in range(2):
        await distributed_system.submit_task(f"task{i}", {"data": "test"})
    
    # Next task should go to node2
    await distributed_system.submit_task("task2", {"data": "test"})
    await asyncio.sleep(0.1)
    
    node_status = await distributed_system.get_node_status("node2")
    assert node_status["current_load"] > 0

async def test_node_failure(distributed_system):
    await distributed_system.register_node("node1", 1.0, "us-east")
    
    # Simulate node failure by not sending heartbeat
    await asyncio.sleep(10)  # Wait for heartbeat timeout
    
    node_status = await distributed_system.get_node_status("node1")
    assert node_status["state"] == NodeState.ERROR.value

async def test_system_shutdown(distributed_system):
    await distributed_system.register_node("node1", 1.0, "us-east")
    await distributed_system.shutdown()
    
    node_status = await distributed_system.get_node_status("node1")
    assert node_status["state"] == NodeState.MAINTENANCE.value 