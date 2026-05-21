from app.core.fetch import scrapeRouterModels
from app.core.fetch import fetchOpenRouterModels 
from app.core.utils import saveJsonData,loadJsonData
from app.core.utils import saveErrorLog
from app.core.ModelScorer import ScoreEngine
from app.core.features_extraction import FeatureNormalizer 
from app.core.features_extraction import FeatureExtractor


def preprocessingModels(fetchedOpenRouterModels,scrapedModels):
    m_slug = [m.get('canonical_slug') for m in fetchedOpenRouterModels]
    
    models = [m for m in scrapedModels.get('models',[]) if m.get('permaslug') in m_slug]
    analytics = scrapedModels.get('analytics',{})
    categories = scrapedModels.get('categories',{}) 
    
    return models,analytics,categories

def get_right_or_models(pricing,permasulg,fetchedOpenRouterModels):
    prompt = pricing.get('prompt',0)
    completion = pricing.get('completion',0) 
    input_cache_write = pricing.get('input_cache_write',0)
    web_search = pricing.get('web_search',0)
    input_cache_read = pricing.get("input_cache_read",0)
   
    or_models = [] 
    for m in fetchedOpenRouterModels:
        if m.get('canonical_slug') == permasulg :
            pricing1 = m.get('pricing',{})
            prompt1 = pricing1.get('prompt',0)
            completion1 = pricing1.get('completion',0) 
            input_cache_write1 = pricing1.get('input_cache_write',0)
            web_search1 = pricing1.get('web_search',0)
            input_cache_read1 = pricing1.get("input_cache_read",0)
            
            if (prompt == prompt1 and 
                completion == completion1 and 
                input_cache_write == input_cache_write1 and 
                input_cache_read == input_cache_read1 and 
                web_search == web_search1):
                
                or_models.append(m)
    #if(len(ids)>1):print(ids)
    return or_models

def get_pricing_by_1M(pricing):
    if not isinstance(pricing, dict):
        return pricing

    result = {}

    for key, value in pricing.items():

        # keep None as-is
        if value is None:
            result[key] = None
            continue

        # do NOT scale web_search
        if key == "web_search":
            try: result[key] = float(value)
            except: result[key] = value
            continue

        # convert string → float then scale
        try:
            numeric_value = float(value) * 1_000_000
            result[key] = round(numeric_value, 3) 
        except:
            # fallback: keep original if something weird
            result[key] = value

    return result

def mergeModelScores(last_model_score_engine,new_model_score_engine):
    for l in last_model_score_engine:
        metadata = l.get('metadata') 
        ranking_results = metadata.get('ranking_results',None)
        id = l.get('id') 
        if ranking_results:
            for n in new_model_score_engine:
                if n.get('id') == id:
                    n['metadata']['ranking_results'] = ranking_results 
                    break 
    
        

def updateModels():
    try:
        scrapedRouterModels = scrapeRouterModels()
        fetchedOpenRouterModels = fetchOpenRouterModels() 
        try:
            last_model_score_engine = loadJsonData('models_for_score_engine.json')
        except:
            last_model_score_engine = None
            pass 
        
        #saveJsonData('openRouterModels.json')
        
        models,analytics,categories = preprocessingModels(fetchedOpenRouterModels,scrapedRouterModels)
        categories_to_map = lambda categories:{
                                    c["category"]: {key:value for key,value in c.items() if key !='category'}
                                    for c in categories
                                    }
        
        new_models = []
        for m in models:
            if m.get('permaslug') in analytics.keys():
                or_models = get_right_or_models(m.get('endpoint').get('pricing'),m.get('permaslug'),fetchedOpenRouterModels)
                first_model = or_models[0]
                id = first_model.get('id') 
                pricing = first_model.get('pricing') 
                supported_parameters = first_model.get('supported_parameters') 
                architecture = first_model.get('architecture',{})
                input_modalities = architecture.get('input_modalities',[])
                output_modalities = architecture.get('output_modalities',[])
                new_models.append({
                    "id":id,
                    "permaslug":m.get('permaslug'),
                    "metadata":{
                        "supported_parameters":supported_parameters,
                        "pricing":pricing,
                        "context_length":first_model.get('context_length',None),
                        "input_modalities":input_modalities,
                        "output_modalities":output_modalities,
                    },
                    "analytics":{
                        "total_completion_tokens":analytics[m.get('permaslug')].get("total_completion_tokens"),
                        "total_prompt_tokens":analytics[m.get('permaslug')].get("total_prompt_tokens"),
                        "total_native_tokens_reasoning":analytics[m.get('permaslug')].get("total_native_tokens_reasoning"),
                        "total_native_tokens_cached":analytics[m.get('permaslug')].get("total_native_tokens_cached"),
                        "total_tool_calls":analytics[m.get('permaslug')].get("total_tool_calls"),
                        "requests_with_tool_call_errors":analytics[m.get('permaslug')].get("requests_with_tool_call_errors"),
                        "categories":categories_to_map(categories.get(m.get("permaslug")) or categories.get(m.get('permaslug')+":free") or [])
                    }
                })


        saveJsonData(new_models,'models.json')
        # ================= EXTRACT FUTURES =================
        #models = new_models
        
        extractor = FeatureExtractor(new_models)
        features = extractor.extract_all()
        
        models_for_score_engine = [{key:value 
                                    if key!='metadata' 
                                    else {**value,"pricing":value.get('pricing')} 
                                    for key,value in f.items() if key!='analytics'} for f in features]
        
        
        mergeModelScores(last_model_score_engine,models_for_score_engine)
        saveJsonData(models_for_score_engine,'models_for_score_engine.json') 
        print("models updated successfult")
        return True
    
    except Exception as e:
        saveErrorLog(e )
        raise  # optional but recommended 
        

    
    
    