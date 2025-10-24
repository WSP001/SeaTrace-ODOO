# 🧪 Pytest Configuration
# For the Commons Good! 🌊

import pytest
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to test data directory"""
    return Path(__file__).parent / "data"


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing"""
    class MockRedis:
        def __init__(self):
            self.data = {}
        
        async def get(self, key):
            return self.data.get(key)
        
        async def set(self, key, value, ex=None):
            self.data[key] = value
            return True
        
        async def delete(self, key):
            if key in self.data:
                del self.data[key]
            return True
    
    return MockRedis()


@pytest.fixture
def mock_mongodb():
    """Mock MongoDB client for testing"""
    class MockCollection:
        def __init__(self):
            self.documents = []
        
        async def insert_one(self, doc):
            self.documents.append(doc)
            return type('obj', (object,), {'inserted_id': 'test_id'})
        
        async def find_one(self, query):
            for doc in self.documents:
                if all(doc.get(k) == v for k, v in query.items()):
                    return doc
            return None
    
    class MockDatabase:
        def __init__(self):
            self.collections = {}
        
        def __getitem__(self, name):
            if name not in self.collections:
                self.collections[name] = MockCollection()
            return self.collections[name]
    
    return MockDatabase()
