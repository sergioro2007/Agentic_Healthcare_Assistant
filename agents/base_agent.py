"""
Base agent implementation using LangGraph and LangChain.
"""
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
import os
import time
import threading
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage

class RateLimitedLLM:
    """Wrapper that adds rate limiting to LLM calls."""
    def __init__(self, llm, rate_limit_func):
        self._llm = llm
        self._rate_limit_func = rate_limit_func
    
    def invoke(self, *args, **kwargs):
        """Rate-limited invoke."""
        self._rate_limit_func()
        return self._llm.invoke(*args, **kwargs)
    
    def __getattr__(self, name):
        """Delegate all other attributes to the wrapped LLM."""
        return getattr(self._llm, name)

class AgentState(BaseModel):
    """State for the agent workflow."""
    messages: List[BaseMessage] = Field(default_factory=list)
    current_task: str = Field(default="")
    task_queue: List[str] = Field(default_factory=list)
    results: Dict[str, Any] = Field(default_factory=dict)

class BaseAgent:
    """Base agent class with common functionality."""
    
    # Class-level rate limiting (15 requests per minute = 1 request every 4 seconds)
    _last_request_time = 0
    _rate_limit_lock = threading.Lock()
    _min_request_interval = 4.0  # seconds between requests
    
    def __init__(self, api_key: str = None):
        """Initialize the agent with a Gemini model."""
        if not api_key and not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("API key must be provided either as argument or GOOGLE_API_KEY environment variable")
            
        self.llm = self._create_llm(api_key)
    
    @classmethod
    def _wait_for_rate_limit(cls):
        """Ensure we don't exceed 15 requests per minute."""
        with cls._rate_limit_lock:
            current_time = time.time()
            time_since_last = current_time - cls._last_request_time
            
            if time_since_last < cls._min_request_interval:
                sleep_time = cls._min_request_interval - time_since_last
                print(f"⏱️  Rate limiting: waiting {sleep_time:.1f}s...")
                time.sleep(sleep_time)
            
            cls._last_request_time = time.time()
    
    def _create_llm(self, api_key: str = None):
        """Create the Gemini LLM instance with rate limiting."""
        # Using gemini-2.5-pro (confirmed to exist in your API)
        # Rate limiting: max 15 requests/minute = 1 request every 4 seconds
        base_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=api_key or os.getenv("GOOGLE_API_KEY"),
            convert_system_message_to_human=True
        )
        
        # Return a wrapper that adds rate limiting
        return RateLimitedLLM(base_llm, self._wait_for_rate_limit)
    
    def _create_graph(self) -> StateGraph:
        """Create the agent's workflow graph."""
        raise NotImplementedError("Subclasses must implement _create_graph")
    
    def _handle_task(self, state: AgentState) -> AgentState:
        """Process a task in the agent's workflow."""
        raise NotImplementedError("Subclasses must implement _handle_task")
    
    async def aprocess(self, task: str, **kwargs) -> Dict[str, Any]:
        """Process a task asynchronously."""
        raise NotImplementedError("Subclasses must implement aprocess")
    
    def process(self, task: str, **kwargs) -> Dict[str, Any]:
        """Process a task synchronously."""
        raise NotImplementedError("Subclasses must implement process")