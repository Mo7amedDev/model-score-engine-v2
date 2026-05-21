import requests
from typing import Literal,List,Optional

ORDER_FILTER = Literal['most-popular','newest','top-weekly','pricing-low-to-high',
                       'pricing-high-to-low','context-high-to-low',
                       'throughput-high-to-low','latency-low-to-high']

CATEGORY_FILER = Literal['programming',
                         'roleplay',
                         'marketing','seo',
                         'technology','science',
                         'translation','legal','finance',
                         'health','trivia','academia']

def scrapeRouterModels(order:Optional[ORDER_FILTER]=None,categories:Optional[List[CATEGORY_FILER]]=None):
    categories = f"&categories={','.join(categories)}" if categories else ''
    order = f"&order={order}" if order else ''
    param = f"{order}{categories}"
    api_end_point = f"https://openrouter.ai/api/frontend/models/find?active=true{param}&input_modalities=text"
    
    response = requests.get(api_end_point)
    response.raise_for_status()
    
    data = response.json().get("data",[]) 
    return data

def fetchOpenRouterModels():
    base_url = "https://openrouter.ai/api/v1/models"
    
    response = requests.get(base_url)
    response.raise_for_status()
    
    data = response.json().get("data",[])
    return data 


