import pytest
import asyncio
import aioredis
from datetime import datetime
from core.system import PrecisionAutomation, SystemState
from core.interface import ElegantInterface, InterfaceType, InterfaceConfig
from core.distributed import DistributedSystem, NodeState
from core.knowledge import KnowledgeMatrix, KnowledgeType, KnowledgeNode

@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def precision_automation():
    system = PrecisionAutomation()
    await system.initialize()
    yield system
    await system.shutdown()

@pytest.fixture
def elegant_interface():
    interface = ElegantInterface()
    interface.register_interface("web", InterfaceConfig(
        type=InterfaceType.WEB,
        theme="light",
        language="en",
        timezone="UTC",
        features=["auth", "api"]
    ))
    return interface

@pytest.fixture
async def distributed_system():
    system = DistributedSystem("redis://localhost:6379/0")
    await system.initialize()
    yield system
    await system.shutdown()

@pytest.fixture
def knowledge_matrix():
    matrix = KnowledgeMatrix()
    node = KnowledgeNode(
        id="test_node",
        type=KnowledgeType.FACT,
        content={"value": 42},
        confidence=0.95,
        source="test",
        timestamp=datetime.now(),
        metadata={"category": "test"}
    )
    matrix.add_knowledge(node)
    return matrix

@pytest.fixture
async def redis_client():
    client = await aioredis.from_url("redis://localhost:6379/0")
    yield client
    await client.close() 