from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from config.settings import settings
import uuid

class KnowledgeBase:
    def __init__(self, collection_name: str = "customer_service_kb"):
        # Connect to Qdrant Cloud with API key
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )
        self.collection_name = collection_name
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self._setup_collection()
    
    def _setup_collection(self):
        """Create collection if it doesn't exist"""
        try:
            self.client.get_collection(self.collection_name)
            print(f"✅ Collection '{self.collection_name}' already exists")
        except:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE
                )
            )
            print(f"✅ Created collection '{self.collection_name}'")
    
    def add_documents(self, documents: List[Dict[str, str]]):
        """Add documents to knowledge base"""
        points = []
        for doc in documents:
            vector = self.encoder.encode(doc['content']).tolist()
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=doc
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"✅ Added {len(documents)} documents to knowledge base")
    
    def search(self, query: str, limit: int = 3) -> List[Dict]:
        """Search for relevant documents"""
        query_vector = self.encoder.encode(query).tolist()
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit
        )
        return [hit.payload for hit in results.points]