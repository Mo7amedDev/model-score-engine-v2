
from app.core.fetch import CATEGORY_FILER
from pydantic import BaseModel 
from typing import Optional,Literal,List
from app.core.utils import loadJsonData
from app.core.ModelScorer import ScoreEngine
from app.core.types import CustomWeights

MODALITY = Literal['text','image','video','file','audio']

class ModelFilter(BaseModel):
    max_1m_input_tokens_price: Optional[float] = 5
    max_1m_output_tokens_price: Optional[float] = 10
    
    require_tools: Optional[bool] = None
    require_structured: Optional[bool] = None
    
    without_reasoning:Optional[bool] = None 
    
     
    min_context_length: Optional[int] = None 
    
    exclude_free_models:Optional[bool] = False
    
    input_modality:Optional[List[MODALITY]]=['text']
    output_modality:Optional[List[MODALITY]]=['text']
    
    

def apply_filters(model:dict, filter:ModelFilter)  :
    metadata = model.get('metadata',{})
    
    supported_parameters = metadata.get('supported_parameters',None)
    context_length = metadata.get('context_length',0)
    
    input_modalities = metadata.get('input_modalities',['text'])
    output_modalities = metadata.get('output_modalities',['text'])
    
    pricing = metadata.get('pricing',{})
    input_price = float(pricing.get('prompt'))*1_000_000
    output_price = float(pricing.get('completion'))*1_000_000
    
    if not all(inm in input_modalities for inm in filter.input_modality):
        return False 
    if not all(oum in output_modalities for oum in filter.output_modality):
        return False
    
    # ================= Price =================
    if input_price > filter.max_1m_input_tokens_price:
        return False

    if output_price > filter.max_1m_output_tokens_price:
        return False
    
    # ================= Context length =================
     
    if filter.min_context_length is not None and context_length < filter.min_context_length:
        return False
    
    # ================= Tools =================
    has_tools = 'tools' in supported_parameters
    if not has_tools and filter.require_tools: return False
    
    # ================= Structured =================
    has_structured = "structured_outputs" in supported_parameters
    if not has_structured and filter.require_structured: return False
    
    # ================ Reasoning ====================
    has_reasoning = "reasoning" in supported_parameters 
    if filter.without_reasoning and has_reasoning: return False
    
    if(filter.exclude_free_models):
        if input_price==0 and output_price ==0 : return False
    
    return True
    
def rank_models_by_task(task:CATEGORY_FILER,filter:ModelFilter,top_k:int=10):
    if(not task):
        raise Exception('task required')
    raw_models = loadJsonData("models_for_score_engine.json")
    
    # Apply filters
    models = [m for m in raw_models if apply_filters(m,filter)] if filter else raw_models
   
    engine = ScoreEngine(models) 
    
    return engine.top_models_by_task(task,top_k)


def rank_models_by_weights(weights:CustomWeights,filter:ModelFilter,top_k:int=10):
    if(not weights):
        raise Exception('weights required')
    raw_models = loadJsonData("models_for_score_engine.json")
    
    models = [m for m in raw_models if apply_filters(m,filter)] if filter else raw_models
   
    engine = ScoreEngine(models) 
    
    return engine.top_model_by_custom_weights(weights,top_k)
    
    
    