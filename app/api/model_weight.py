from app.core.types import CustomWeights 
from typing import Optional
from pydantic import BaseModel, Field 
from langchain_core.prompts import ChatPromptTemplate
from langchain_openrouter import ChatOpenRouter

system_instruction = """
You are an expert AI Systems Architect specializing in LLM routing and evaluation. 
Your job is to translate a user's natural language request into a precise dictionary of feature weights for a recommendation engine.

Available features you can assign weights to:
- popularity (Overall consumption)
- reasoning (Complex logic, math, chain-of-thought)
- tools (Function calling/API execution)
- reliability (Low error rates in production)
- cache (Cost optimization/prompt caching)
- programming (Coding, debugging, script generation)
- science (Hard sciences, chemistry, physics)
- technology (IT systems, hardware, generic engineering)
- finance (Economic analysis, numbers, spreadsheets)
- marketing (Content creation, ad copywriting)
- translation (Language accuracy)
- legal (Law, compliance, text dense evaluation)
- health (Medicine, wellness data)
- roleplay (Chat personas, fiction writing)
- academia (Research papers, thesis styling)
- marketing/seo (SEO metadata, web positioning)

CRITICAL RULES:
1. Identify the core intent of the user request and allocate weights only to the most relevant features.
2. The SUM of all weights you assign MUST equal exactly 1.0 (or 100%).
3. If a feature is completely irrelevant to the user's task, leave it as 0.0.
4. Distribute the 1.0 budget intelligently based on the priorities implicit in the user text.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_instruction),
    ("human", "Analyze this request and generate the weights: '{task_description}'")
])

llm = ChatOpenRouter(model='', temperature=0.0)

# Bind the Pydantic schema to force structured JSON output
structured_llm = llm.with_structured_output(CustomWeights)

# Combine into a runnable chain
weight_generation_chain = prompt | structured_llm