from typing import Dict, List, Optional, Any, Set
import numpy as np
from dataclasses import dataclass
from datetime import datetime
import logging
from enum import Enum
import json
import networkx as nx
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class KnowledgeType(Enum):
    FACT = "fact"
    RULE = "rule"
    PATTERN = "pattern"
    RELATIONSHIP = "relationship"
    PREDICTION = "prediction"

@dataclass
class KnowledgeNode:
    id: str
    type: KnowledgeType
    content: Any
    confidence: float
    source: str
    timestamp: datetime
    metadata: Dict[str, Any]

class KnowledgeMatrix:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.knowledge_nodes: Dict[str, KnowledgeNode] = {}
        self.patterns: Dict[str, List[float]] = {}
        self.relationships: Dict[str, Set[str]] = {}
        
    def add_knowledge(self, node: KnowledgeNode):
        self.knowledge_nodes[node.id] = node
        self.graph.add_node(node.id, **node.__dict__)
        logger.info(f"Added knowledge node: {node.id}")
        
    def add_relationship(self, source_id: str, target_id: str, relationship_type: str):
        if source_id in self.knowledge_nodes and target_id in self.knowledge_nodes:
            self.graph.add_edge(source_id, target_id, type=relationship_type)
            if source_id not in self.relationships:
                self.relationships[source_id] = set()
            self.relationships[source_id].add(target_id)
            logger.info(f"Added relationship: {source_id} -> {target_id}")
            
    def find_patterns(self, min_samples: int = 3, eps: float = 0.5):
        node_features = []
        node_ids = []
        
        for node_id, node in self.knowledge_nodes.items():
            if node.type == KnowledgeType.PATTERN:
                features = self._extract_features(node)
                node_features.append(features)
                node_ids.append(node_id)
                
        if len(node_features) >= min_samples:
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(node_features)
            
            clustering = DBSCAN(eps=eps, min_samples=min_samples)
            labels = clustering.fit_predict(scaled_features)
            
            for i, label in enumerate(labels):
                if label != -1:
                    pattern_id = f"pattern_cluster_{label}"
                    if pattern_id not in self.patterns:
                        self.patterns[pattern_id] = []
                    self.patterns[pattern_id].extend(node_features[i])
                    
    def _extract_features(self, node: KnowledgeNode) -> List[float]:
        features = []
        if isinstance(node.content, (int, float)):
            features.append(float(node.content))
        elif isinstance(node.content, dict):
            features.extend([float(v) for v in node.content.values() if isinstance(v, (int, float))])
        elif isinstance(node.content, list):
            features.extend([float(v) for v in node.content if isinstance(v, (int, float))])
        return features
        
    def query_knowledge(self, query: Dict[str, Any]) -> List[KnowledgeNode]:
        results = []
        for node in self.knowledge_nodes.values():
            if self._matches_query(node, query):
                results.append(node)
        return results
        
    def _matches_query(self, node: KnowledgeNode, query: Dict[str, Any]) -> bool:
        for key, value in query.items():
            if key == "type" and node.type != value:
                return False
            elif key == "confidence" and node.confidence < value:
                return False
            elif key == "source" and node.source != value:
                return False
            elif key in node.metadata and node.metadata[key] != value:
                return False
        return True
        
    def get_related_knowledge(self, node_id: str, max_depth: int = 2) -> List[KnowledgeNode]:
        if node_id not in self.knowledge_nodes:
            return []
            
        related_nodes = set()
        for _, target in nx.dfs_edges(self.graph, node_id, depth_limit=max_depth):
            related_nodes.add(target)
            
        return [self.knowledge_nodes[node_id] for node_id in related_nodes]
        
    def export_knowledge(self) -> Dict[str, Any]:
        return {
            "nodes": {
                node_id: {
                    "type": node.type.value,
                    "content": node.content,
                    "confidence": node.confidence,
                    "source": node.source,
                    "timestamp": node.timestamp.isoformat(),
                    "metadata": node.metadata
                }
                for node_id, node in self.knowledge_nodes.items()
            },
            "relationships": {
                source: list(targets)
                for source, targets in self.relationships.items()
            },
            "patterns": self.patterns
        }
        
    def import_knowledge(self, data: Dict[str, Any]):
        for node_id, node_data in data["nodes"].items():
            node = KnowledgeNode(
                id=node_id,
                type=KnowledgeType(node_data["type"]),
                content=node_data["content"],
                confidence=node_data["confidence"],
                source=node_data["source"],
                timestamp=datetime.fromisoformat(node_data["timestamp"]),
                metadata=node_data["metadata"]
            )
            self.add_knowledge(node)
            
        for source, targets in data["relationships"].items():
            for target in targets:
                self.add_relationship(source, target, "imported")
                
        self.patterns = data["patterns"]
        logger.info("Imported knowledge matrix") 