from pydantic import BaseModel, Field
from typing import Optional

class CustomWeights(BaseModel):
    # Global metrics
    popularity: Optional[float] = Field(default=0.0, description="Weight for overall model usage volume.")
    reasoning: Optional[float] = Field(default=0.0, description="Weight for deep thinking, complex logic, and chain-of-thought capabilities.")
    tools: Optional[float] = Field(default=0.0, description="Weight for function calling and external tool usage capabilities.")
    reliability: Optional[float] = Field(default=0.0, description="Weight for low error rates during structured execution.")
    cache: Optional[float] = Field(default=0.0, description="Weight for prompt caching efficiency and cost savings.")

    # Category metrics
    programming: Optional[float] = Field(default=0.0, description="Weight for software engineering, code generation, and debugging.")
    science: Optional[float] = Field(default=0.0, description="Weight for scientific research, physics, chemistry, etc.")
    technology: Optional[float] = Field(default=0.0, description="Weight for technical, IT, and general engineering topics.")
    finance: Optional[float] = Field(default=0.0, description="Weight for financial analysis, math, spreadsheet logic, and market data.")
    marketing: Optional[float] = Field(default=0.0, description="Weight for copy-writing, creative content generation, and ad hooks.")
    translation: Optional[float] = Field(default=0.0, description="Weight for multi-language translation and localization accuracy.")
    legal: Optional[float] = Field(default=0.0, description="Weight for contract analysis, legal terminology, and compliance.")
    health: Optional[float] = Field(default=0.0, description="Weight for medical, biological, and health-related general information.")
    roleplay: Optional[float] = Field(default=0.0, description="Weight for conversational depth, character persona maintenance, and creative writing.")
    academia: Optional[float] = Field(default=0.0, description="Weight for academic writing, citations, and research papers.")
    
    marketing_seo: Optional[float] = Field(default=0.0, alias="marketing/seo", description="Weight specifically for search engine optimization strategy and web ranking copy.")

    model_config = {
        "populate_by_name": True 
    }