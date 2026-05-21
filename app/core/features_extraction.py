import math
from typing import Dict, List, Any


class FeatureExtractor:

    def __init__(self, models: List[Dict[str, Any]]):

        self.models = models
        self.max_ranks = self._compute_max_ranks()

    # ---------------------------------------------------
    # HELPERS
    # ---------------------------------------------------
    
    def _log_score(self, value: float) -> float:
        """
        Prevent huge models from dominating.
        """
        return math.log10(value + 1)

    def _compute_max_ranks(self) -> Dict[str, int]:

        max_ranks = {}

        for model in self.models:

            categories = model.get("analytics", {}).get("categories", {})
            
            for category, data in categories.items():

                rank = data.get("rank", 0)
                current_max = max_ranks.get(category, 0)

                max_ranks[category] = max(current_max,rank)

        return max_ranks

    # ---------------------------------------------------
    # FEATURE FUNCTIONS
    # ---------------------------------------------------

    def pop_score(self, analytics: Dict) -> float:

        total = (
            analytics.get("total_prompt_tokens", 0) +
            analytics.get("total_completion_tokens", 0)
        )

        return self._log_score(total)

    def reasoning_score(self, analytics: Dict) -> float:

        reasoning_tokens = analytics.get("total_native_tokens_reasoning",0)

        return self._log_score(reasoning_tokens)

    def tool_score(self, analytics: Dict) -> float:

        tool_calls = analytics.get("total_tool_calls",0)

        return self._log_score(tool_calls)

    def reliability_score(self, analytics: Dict) -> float:

        tool_calls = analytics.get("total_tool_calls",0)

        if tool_calls == 0: return 0

        errors = analytics.get("requests_with_tool_call_errors",0)

        reliability_ratio = ( tool_calls - errors) / tool_calls

        return (
            reliability_ratio *
            self._log_score(tool_calls)
        )

    def cache_score(self, analytics: Dict) -> float:

        cached = analytics.get("total_native_tokens_cached",0)
        prompts = analytics.get("total_prompt_tokens",0)

        if prompts == 0: return 0

        return cached / prompts

    def category_score(self,  analytics,category):
    
        categories = analytics.get("categories", {})
        #print(category,'sssssssss')
        cat = categories.get(category,None)
        if not cat: return 0        
        
        rank = cat.get("rank", 0)
        volume = cat.get("volume", 0)

        max_rank = self.max_ranks.get(category, 1)

        rank_score = (max_rank - rank) / max_rank

        volume_score = math.log10(volume + 1)

        return (
            rank_score * 0.7 +
            volume_score * 0.3
        )

    # ---------------------------------------------------
    # MAIN EXTRACTION
    # ---------------------------------------------------

    def extract_features(
        self,
        model: Dict
    ) -> Dict:

        analytics = model.get("analytics",{})
        
         
        print(analytics)
        features = {

            # Global features
            "popularity":self.pop_score(analytics),
            "reasoning":self.reasoning_score(analytics),
            "tools":self.tool_score(analytics),
            "reliability":self.reliability_score(analytics),
            "cache":self.cache_score(analytics),
            
             
            # Categories
            "programming":self.category_score( analytics, "programming"),
            "science":self.category_score(analytics,"science"),
            "technology":self.category_score(analytics,"technology"),
            "finance":self.category_score(analytics,"finance"),
            "marketing":self.category_score(analytics,"marketing"),
            "translation":self.category_score(analytics,"translation"),
            "marketing/seo":self.category_score(analytics,'marketing/seo'),
            "legal":self.category_score(analytics,"legal"),
            "health":self.category_score(analytics,"health"),
            "roleplay":self.category_score(analytics,"roleplay"),
            "academia":self.category_score(analytics,"academia"),
        }
        return {
            **model,
            "features": features
        }

    # ---------------------------------------------------
    # EXTRACT ALL
    # ---------------------------------------------------

    def extract_all(self) -> List[Dict]:

        features =  [
            self.extract_features(model)
            for model in self.models
        ]
        normalizer = FeatureNormalizer(features)
        normalized = normalizer.normalize_all()
        return normalized
        
        
    
class FeatureNormalizer:
    
    def __init__(self, features):

        self.features = features
        self.stats = self._compute_stats()
    def _compute_stats(self):

        stats = {}

        feature_names = (
            self.features[0]["features"].keys()
        )

        for feature in feature_names:

            values = [
                model["features"][feature]
                for model in self.features
            ]

            stats[feature] = {
                "min": min(values),
                "max": max(values)
            }

        return stats

    def normalize_value(
        self,
        feature_name,
        value
    ):
       
        stat = self.stats[feature_name]

        mn = stat["min"]
        mx = stat["max"]

        if mx == mn:
            return 0.0 if mx == 0 else 1.0

        return (value - mn) / (mx - mn)

    def normalize_model(self, model):

        normalized = {}

        for feature, value in model["features"].items():

            normalized[feature] = (
                self.normalize_value(
                    feature,
                    value
                )
            )

        return {
            **model,
            "features": normalized
        }

    def normalize_all(self):

        return [
            self.normalize_model(model)
            for model in self.features
        ]
        
    ''' 
    FeatureExtractor
        ↓
    FeatureNormalizer
        ↓
    ScoreEngine
        ↓
    RecommendationEngine 
    '''