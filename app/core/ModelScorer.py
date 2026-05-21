from typing import Dict, List, Any
from app.core.types import CustomWeights

class ScoreEngine:

    """
    Expects NORMALIZED features (0 -> 1)

    Example input:

    [
        {
            "id": "...",
            "metadata":{},
            "features": {
                "popularity": 0.91,
                "reasoning": 0.72,
                "tools": 0.44,
                "programming": 0.88
            }
        }
    ]
    """

    # ---------------------------------------------------
    # DEFAULT WEIGHTS
    # ---------------------------------------------------

    TASK_WEIGHTS = {

        "overall": {
            "popularity": 0.25,
            "reasoning": 0.20,
            "tools": 0.15,
            "reliability": 0.15,
            "cache": 0.05,

            "programming": 0.05,
            "science": 0.05,
            "technology": 0.05,
            "finance": 0.05
        },

        "programming": {
            "programming": 0.40,
            "reasoning": 0.25,
            "tools": 0.20,
            "reliability": 0.10,
            "popularity": 0.05
        },

        "reasoning": {
            "reasoning": 0.50,
            "science": 0.15,
            "programming": 0.10,
            "reliability": 0.10,
            "popularity": 0.10,
            "tools": 0.05
        },

        "agents": {
            "tools": 0.40,
            "reasoning": 0.25,
            "reliability": 0.20,
            "cache": 0.10,
            "popularity": 0.05
        },

        "science": {
            "science": 0.50,
            "reasoning": 0.20,
            "academia": 0.15,
            "reliability": 0.10,
            "popularity": 0.05
        },

        "finance": {
            "finance": 0.55,
            "reasoning": 0.15,
            "reliability": 0.15,
            "popularity": 0.10,
            "tools": 0.05
        },

        "marketing": {
            "marketing": 0.60,
            "roleplay": 0.10,
            "popularity": 0.15,
            "reliability": 0.10,
            "tools": 0.05
        },
        "marketing/seo":{
            "marketing": 0.60,
            "roleplay": 0.10,
            "popularity": 0.15,
            "reliability": 0.10,
            "tools": 0.05
        },
        "translation": {
            "translation": 0.70,
            "reliability": 0.15,
            "popularity": 0.10,
            "reasoning": 0.05
        },

        "roleplay": {
            "roleplay": 0.60,
            "reasoning": 0.15,
            "popularity": 0.15,
            "tools": 0.05,
            "reliability": 0.05
        }
    }

    # ---------------------------------------------------
    # INIT
    # ---------------------------------------------------

    def __init__(
        self,
        models: List[Dict[str, Any]]
    ):

        self.models = models

    # ---------------------------------------------------
    # CORE SCORING
    # ---------------------------------------------------

    def _compute_score(
        self,
        features: Dict[str, float],
        weights: Dict[str, float]
    ) -> float:

        score = 0

        for feature, weight in weights.items():

            value = features.get(feature, 0)

            score += value * weight

        return round(score, 4)

    # ---------------------------------------------------
    # TASK SCORE
    # ---------------------------------------------------

    def _task_score(
        self,
        model: Dict,
        task: str
    ) -> float:

        weights = self.TASK_WEIGHTS.get(task)

        if not weights:
            raise ValueError(
                f"Unknown task: {task}"
            )

        features = model.get("features", {})

        return self._compute_score(
            features,
            weights
        )

    # ---------------------------------------------------
    # SCORE SINGLE MODEL
    # ---------------------------------------------------

    def _score_model(
        self,
        model: Dict
    ) -> Dict:

        scores = {}

        for task in self.TASK_WEIGHTS:

            scores[task] = self._task_score(
                model,
                task
            )

        return {
            **model,
            "scores": scores
        }

    # ---------------------------------------------------
    # SCORE ALL MODELS
    # ---------------------------------------------------

    def _score_all(self) -> List[Dict]:

        return [
            self._score_model(model)
            for model in self.models
        ]

    # ---------------------------------------------------
    # GET TOP MODELS
    # ---------------------------------------------------

    def top_models_by_task(
        self,
        task: str,
        top_k: int = 10
    ) -> List[Dict]:

        scored = self._score_all()

        ranked = sorted(
            scored,
            key=lambda x: x["scores"].get(task, 0),
            reverse=True
        )

        return ranked[:top_k]

    # ---------------------------------------------------
    # CUSTOM SCORE
    # ---------------------------------------------------

    def top_model_by_custom_weights(
        self,
        weights: CustomWeights,
        top_k: int = 10
    ) -> List[Dict]:

        results = []
        
        # Convert Pydantic object to dict, translating 'marketing_seo' back to 'marketing/seo'
        weights_dict = weights.model_dump(by_alias=True)

        for model in self.models:

            score = self._compute_score(
                model.get("features", {}),
                weights_dict
            )

            results.append({
                **model,
                "score": score
            })

        # Sort the models from highest score to lowest
        ranked = sorted(
            results,
            key=lambda x: x["score"],
            reverse=True
        )
        print(len(self.models))
        # Return only the top K requested models
        return ranked[:top_k]
        
        

