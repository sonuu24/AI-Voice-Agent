from config.settings import settings
from src.rag.vector_store import KnowledgeBase

print("Testing Qdrant Cloud connection...")
print(f"URL: {settings.qdrant_url}")
print(f"API Key: {'*' * 20}{settings.qdrant_api_key[-4:]}")

kb = KnowledgeBase()
print("\n✅ Successfully connected to Qdrant Cloud!")

# Test adding a document
test_docs = [
    {
        "content": "Our return policy allows returns within 30 days.",
        "category": "returns"
    }
]

kb.add_documents(test_docs)
print("✅ Added test document")

# Test search
results = kb.search("return policy")
print(f"✅ Search works! Found: {results[0]['content']}")