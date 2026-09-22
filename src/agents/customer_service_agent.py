import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from typing import TypedDict, Annotated, List
import operator
from src.rag.vector_store import KnowledgeBase
from config.settings import settings

class AgentState(TypedDict):
    query: str
    context: Annotated[list, operator.add]
    response: str
    intent: str
    should_escalate: bool

class CustomerServiceAgent:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0.3,
            model_name="llama-3.3-70b-versatile",
            groq_api_key=settings.groq_api_key
        )
        self.kb = KnowledgeBase()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_intent", self.classify_intent)
        workflow.add_node("retrieve_context", self.retrieve_context)
        workflow.add_node("generate_response", self.generate_response)
        workflow.add_node("escalate", self.escalate_to_human)
        
        # Add edges
        workflow.set_entry_point("classify_intent")
        workflow.add_conditional_edges(
            "classify_intent",
            self.should_escalate,
            {
                True: "escalate",
                False: "retrieve_context"
            }
        )
        workflow.add_edge("retrieve_context", "generate_response")
        workflow.add_edge("generate_response", END)
        workflow.add_edge("escalate", END)
        
        return workflow.compile()
    
    def classify_intent(self, state: AgentState) -> AgentState:
        """Classify customer intent"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Classify the customer query into one of these categories:
            - order_tracking
            - returns
            - product_info
            - shipping
            - billing
            - complaint
            - other
            
            Also determine if this needs human escalation (complex complaints, refunds, etc.)
            Respond in format: INTENT: <category> | ESCALATE: <yes/no>"""),
            ("user", "{query}")
        ])
        
        chain = prompt | self.llm
        result = chain.invoke({"query": state["query"]})
        
        # Parse result
        content = result.content
        intent = content.split("|")[0].split(":")[1].strip()
        escalate = "yes" in content.split("|")[1].lower()
        
        state["intent"] = intent
        state["should_escalate"] = escalate
        return state
    
    def should_escalate(self, state: AgentState) -> bool:
        return state["should_escalate"]
    
    def retrieve_context(self, state: AgentState) -> AgentState:
        """Retrieve relevant context from knowledge base"""
        results = self.kb.search(state["query"], limit=3)
        state["context"] = results
        return state
    
    def generate_response(self, state: AgentState) -> AgentState:
        """Generate response using LLM + context"""
        context_str = "\n".join([doc["content"] for doc in state["context"]])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful customer service agent. Use the provided context to answer the customer's question accurately and professionally.
            
            Context:
            {context}
            
            Guidelines:
            - Be concise and friendly
            - Cite specific policies when relevant
            - If you're unsure, say so
            - Keep responses under 3 sentences for voice clarity"""),
            ("user", "{query}")
        ])
        
        chain = prompt | self.llm
        result = chain.invoke({
            "query": state["query"],
            "context": context_str
        })
        
        state["response"] = result.content
        return state
    
    def escalate_to_human(self, state: AgentState) -> AgentState:
        """Handle escalation to human agent"""
        state["response"] = "I understand this requires special attention. Let me connect you with a specialist who can help you better. Please hold."
        return state
    
    def run(self, query: str) -> str:
        """Run the agent workflow"""
        initial_state = {
            "query": query,
            "context": [],
            "response": "",
            "intent": "",
            "should_escalate": False
        }
        
        result = self.graph.invoke(initial_state)
        return result["response"]