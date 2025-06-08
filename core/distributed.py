from typing import Dict, List, Optional, Any, Callable
import asyncio
import logging
from datetime import datetime
from dataclasses import dataclass
import json
import aiohttp
import aioredis
from enum import Enum

logger = logging.getLogger(__name__)

class NodeState(Enum):
    ACTIVE = "active"
    STANDBY = "standby"
    MAINTENANCE = "maintenance"
    ERROR = "error"

@dataclass
class NodeInfo:
    id: str
    state: NodeState
    capacity: float
    current_load: float
    last_heartbeat: datetime
    location: str

class DistributedSystem:
    def __init__(self, redis_url: str):
        self.nodes: Dict[str, NodeInfo] = {}
        self.redis = None
        self.redis_url = redis_url
        self.task_queue = asyncio.Queue()
        self.heartbeat_interval = 5
        
    async def initialize(self):
        self.redis = await aioredis.from_url(self.redis_url)
        asyncio.create_task(self._heartbeat_monitor())
        asyncio.create_task(self._task_processor())
        logger.info("Distributed system initialized")
        
    async def register_node(self, node_id: str, capacity: float, location: str):
        node = NodeInfo(
            id=node_id,
            state=NodeState.STANDBY,
            capacity=capacity,
            current_load=0.0,
            last_heartbeat=datetime.now(),
            location=location
        )
        self.nodes[node_id] = node
        await self._update_node_state(node_id, NodeState.ACTIVE)
        logger.info(f"Registered node: {node_id}")
        
    async def submit_task(self, task_id: str, task_data: Any, priority: int = 0):
        task = {
            "id": task_id,
            "data": task_data,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
        await self.task_queue.put(task)
        logger.info(f"Submitted task: {task_id}")
        
    async def _heartbeat_monitor(self):
        while True:
            try:
                for node_id, node in self.nodes.items():
                    if (datetime.now() - node.last_heartbeat).seconds > self.heartbeat_interval * 2:
                        await self._update_node_state(node_id, NodeState.ERROR)
                        logger.warning(f"Node {node_id} heartbeat timeout")
                await asyncio.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Heartbeat monitor error: {str(e)}")
                
    async def _task_processor(self):
        while True:
            try:
                task = await self.task_queue.get()
                node = await self._select_node()
                if node:
                    await self._assign_task(node.id, task)
                else:
                    logger.warning("No available nodes for task processing")
                self.task_queue.task_done()
            except Exception as e:
                logger.error(f"Task processor error: {str(e)}")
                
    async def _select_node(self) -> Optional[NodeInfo]:
        available_nodes = [
            node for node in self.nodes.values()
            if node.state == NodeState.ACTIVE and node.current_load < node.capacity
        ]
        if not available_nodes:
            return None
        return min(available_nodes, key=lambda x: x.current_load)
        
    async def _assign_task(self, node_id: str, task: Dict):
        node = self.nodes[node_id]
        node.current_load += 1
        await self.redis.publish(f"node:{node_id}:tasks", json.dumps(task))
        logger.info(f"Assigned task {task['id']} to node {node_id}")
        
    async def _update_node_state(self, node_id: str, state: NodeState):
        if node_id in self.nodes:
            self.nodes[node_id].state = state
            await self.redis.publish(f"node:{node_id}:state", state.value)
            logger.info(f"Updated node {node_id} state to {state.value}")
            
    async def get_node_status(self, node_id: str) -> Optional[Dict]:
        if node_id in self.nodes:
            node = self.nodes[node_id]
            return {
                "id": node.id,
                "state": node.state.value,
                "capacity": node.capacity,
                "current_load": node.current_load,
                "last_heartbeat": node.last_heartbeat.isoformat(),
                "location": node.location
            }
        return None
        
    async def shutdown(self):
        for node_id in self.nodes:
            await self._update_node_state(node_id, NodeState.MAINTENANCE)
        await self.redis.close()
        logger.info("Distributed system shutdown complete") 