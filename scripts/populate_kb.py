import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.vector_store import KnowledgeBase
from pathlib import Path

def load_text_file(filepath):
    """Load and split text file into documents"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by double newlines (paragraphs)
    sections = [s.strip() for s in content.split('\n\n') if s.strip()]
    return sections

def main():
    print("📚 Populating Knowledge Base...\n")
    
    kb = KnowledgeBase()
    
    # Load FAQs
    faq_path = Path('data/knowledge_base/sample_faqs.txt')
    if faq_path.exists():
        faqs = load_text_file(faq_path)
        faq_docs = [
            {
                "content": faq,
                "category": "faq",
                "source": "sample_faqs.txt"
            }
            for faq in faqs
        ]
        kb.add_documents(faq_docs)
        print(f"✅ Added {len(faq_docs)} FAQs")
    
    # Load Policies
    policy_path = Path('data/knowledge_base/policies.txt')
    if policy_path.exists():
        policies = load_text_file(policy_path)
        policy_docs = [
            {
                "content": policy,
                "category": "policy",
                "source": "policies.txt"
            }
            for policy in policies
        ]
        kb.add_documents(policy_docs)
        print(f"✅ Added {len(policy_docs)} policies")
    
    print("\n🎉 Knowledge base populated successfully!")
    
    # Test search
    print("\n🔍 Testing search...")
    results = kb.search("return policy", limit=2)
    print(f"\nSearch results for 'return policy':")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['content'][:100]}...")

if __name__ == "__main__":
    main()