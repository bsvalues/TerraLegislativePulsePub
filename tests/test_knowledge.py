import pytest
from datetime import datetime
from core.knowledge import KnowledgeType, KnowledgeNode

def test_knowledge_addition(knowledge_matrix):
    node = KnowledgeNode(
        id="test_node2",
        type=KnowledgeType.RULE,
        content={"condition": "if x > 0"},
        confidence=0.8,
        source="test",
        timestamp=datetime.now(),
        metadata={"category": "logic"}
    )
    knowledge_matrix.add_knowledge(node)
    assert "test_node2" in knowledge_matrix.knowledge_nodes

def test_relationship_creation(knowledge_matrix):
    node1 = KnowledgeNode(
        id="node1",
        type=KnowledgeType.FACT,
        content={"value": 1},
        confidence=0.9,
        source="test",
        timestamp=datetime.now(),
        metadata={}
    )
    node2 = KnowledgeNode(
        id="node2",
        type=KnowledgeType.FACT,
        content={"value": 2},
        confidence=0.9,
        source="test",
        timestamp=datetime.now(),
        metadata={}
    )
    
    knowledge_matrix.add_knowledge(node1)
    knowledge_matrix.add_knowledge(node2)
    knowledge_matrix.add_relationship("node1", "node2", "leads_to")
    
    assert "node1" in knowledge_matrix.relationships
    assert "node2" in knowledge_matrix.relationships["node1"]

def test_pattern_recognition(knowledge_matrix):
    # Add pattern nodes
    for i in range(5):
        node = KnowledgeNode(
            id=f"pattern_{i}",
            type=KnowledgeType.PATTERN,
            content={"value": i * 10},
            confidence=0.9,
            source="test",
            timestamp=datetime.now(),
            metadata={}
        )
        knowledge_matrix.add_knowledge(node)
    
    knowledge_matrix.find_patterns(min_samples=3, eps=1.0)
    assert len(knowledge_matrix.patterns) > 0

def test_knowledge_querying(knowledge_matrix):
    results = knowledge_matrix.query_knowledge({
        "type": KnowledgeType.FACT,
        "confidence": 0.9
    })
    assert len(results) > 0
    assert all(node.type == KnowledgeType.FACT for node in results)
    assert all(node.confidence >= 0.9 for node in results)

def test_related_knowledge(knowledge_matrix):
    # Create a chain of related nodes
    for i in range(3):
        node = KnowledgeNode(
            id=f"chain_{i}",
            type=KnowledgeType.FACT,
            content={"value": i},
            confidence=0.9,
            source="test",
            timestamp=datetime.now(),
            metadata={}
        )
        knowledge_matrix.add_knowledge(node)
        if i > 0:
            knowledge_matrix.add_relationship(f"chain_{i-1}", f"chain_{i}", "next")
    
    related = knowledge_matrix.get_related_knowledge("chain_0", max_depth=2)
    assert len(related) == 2  # chain_1 and chain_2

def test_knowledge_export_import(knowledge_matrix):
    # Add some test data
    node = KnowledgeNode(
        id="export_test",
        type=KnowledgeType.FACT,
        content={"value": "test"},
        confidence=0.9,
        source="test",
        timestamp=datetime.now(),
        metadata={"test": True}
    )
    knowledge_matrix.add_knowledge(node)
    
    # Export and import
    exported = knowledge_matrix.export_knowledge()
    new_matrix = KnowledgeMatrix()
    new_matrix.import_knowledge(exported)
    
    # Verify imported data
    assert "export_test" in new_matrix.knowledge_nodes
    imported_node = new_matrix.knowledge_nodes["export_test"]
    assert imported_node.type == KnowledgeType.FACT
    assert imported_node.content["value"] == "test"
    assert imported_node.metadata["test"] is True 