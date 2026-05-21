from fastapi import APIRouter
from pydantic import BaseModel 
from typing import Optional, List
from app.core.fetch import CATEGORY_FILER
from app.core.types import CustomWeights
from app.core.rank_models import ModelFilter,rank_models_by_task,rank_models_by_weights
from app.core.utils import loadJsonData,saveErrorLog
from app.core.ScoreSuccessWeights import ModelScorerSuccess
from app.core.exceptions import ModelsNotFoundError

router = APIRouter()

class RankRequest(BaseModel):
    task:Optional[CATEGORY_FILER] = None 
    weights:Optional[CustomWeights] = None
    filter:Optional[ModelFilter] = None 
    top_k:int = 10 
    order_by_reliable_call:Optional[bool] = False,
    
    class Config:    
        class Config:
            json_schema_extra = {
            "example": {
                "task":"""programming \n availables:
                'programming', 'roleplay', 'marketing', 'seo', 'technology', 
                'science', 'translation', 'legal', 
                'finance', 'health', 'trivia', 'academia'
                """,
                "weights": {
                    "popularity":0.0, 
                    "reasoning":0.5, 
                    "tools":0.0, 
                    "reliability":0.0, 
                    "cache":0.0, 
                    "programming":0.5, 
                    "science":0.0, 
                    "technology":0.0, 
                    "finance":0.0, 
                    "marketing":0.0, 
                    "translation":0.0, 
                    "legal":0.0, 
                    "health":0.0, 
                    "roleplay":0.0, 
                    "academia":0.0, 
                    "marketing_seo":0.0
                },
                "filter":{
                    "max_1m_input_tokens_price":1,
                    "max_1m_output_tokens_price":1,
                    "exclude_free_models":False,
                    "min_context_length":4000,
                    "require_structured":False,
                    "require_tools":False,
                },
                "top_k": 5
            }
        }
            

@router.post(
    "/models",
    summary="Rank AI Models",
    description="Ranks AI models based on task or giving custom weights and optional filters."
)
def rank(req:RankRequest):
    models = (rank_models_by_task(req.task,req.filter,req.top_k) 
            if req.task
            else rank_models_by_weights(req.weights,req.filter,req.top_k)) 
    
    if(req.order_by_reliable_call):
        score = ModelScorerSuccess()
        models = score.score_models(models)
        
        
    
    return [{
        "id":m.get('id'),
        "pricing":m.get('metadata',{}).get('pricing')
        
    } for m in models]


class ModelPricingRequest(BaseModel):
    models_id:List[str]
    

def is_exist(origin,req_models):
    for m in req_models:
        if m == origin.get('id') or m.replace(':free','') == origin.get('id'): return {
                "pricing":origin.get('metadata',{}).get('pricing'),
                "model_id":m,
                "origin_id":origin.get('id'),
            }
        if m == origin.get('permaslug') or m.replace(':free','') == origin.get('permaslug'): return {
            "pricing":origin.get('metadata',{}).get('pricing'),
            "model_id":m,
            "origin_id":origin.get('id')
        }
    

    
@router.post('/pricing')
def get_pricing(request:ModelPricingRequest):
    
    models = loadJsonData("models_for_score_engine.json")
    pricings = []
    for m in models:
        pricing = is_exist(m,request.models_id)
        if(pricing):
            pricings.append(pricing)
         
    if(len(pricings) < len(request.models_id)):
        not_found_models = [{
            "pricing":None,
            "model_id":m,
            "origin_id":None,
            "status":f'{m} not found'
            } for m in request.models_id 
                            if m not in [i.get('origin_id') for i in pricings] 
                            and m not in [i.get('model_id') for i in pricings]]
        saveErrorLog(ModelsNotFoundError(
            f"Feching Pricing Warning: Models not found: {list(set([m.get('model_id') for m in  not_found_models]))}"
        ))
        pricings += not_found_models
    
    return pricings 
    
            
