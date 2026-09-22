import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.customer_service_agent import CustomerServiceAgent

def main():
    print("🤖 Testing Customer Service Agent\n")
    
    agent = CustomerServiceAgent()
    
    # Test queries
    queries = [
        "What is your return policy?",
        "How long does shipping take?",
        "I need to track my order",
        "Do you accept PayPal?",
        "I want a refund for a damaged item worth $500"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"❓ User: {query}")
        print(f"{'='*60}")
        
        response = agent.run(query)
        print(f"🤖 Agent: {response}\n")

if __name__ == "__main__":
    main()