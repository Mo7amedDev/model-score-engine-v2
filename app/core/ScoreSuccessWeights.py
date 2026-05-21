from dataclasses import dataclass
from typing import List, Dict, Any
import math


@dataclass
class ScoreWeights:
    success_rate: float = 0.75
    latency: float = 0.15
    confidence: float = 0.10


class ModelScorerSuccess:
    """
    Rank models by:
    1. success_rate (MOST IMPORTANT)
    2. avg_latency
    3. total_calls confidence

    Higher score = better model
    """

    def __init__(self, weights: ScoreWeights = None):
        self.weights = weights or ScoreWeights()

    @staticmethod
    def _safe_div(a: float, b: float, default: float = 0.0):
        return a / b if b else default

    def _normalize_latency(
        self,
        latency: float,
        min_latency: float,
        max_latency: float,
    ) -> float:
        """
        Convert latency to score between 0 and 1
        lower latency = better score
        """

        if max_latency == min_latency:
            return 1.0

        normalized = (latency - min_latency) / (
            max_latency - min_latency
        )

        return 1 - normalized

    def _confidence_score(self, total_calls: int) -> float:
        """
        Log confidence:
        more calls => more trust
        """

        return min(math.log10(total_calls + 1) / 3, 1.0)

    def score_models(
        self,
        models: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        if not models:
            return []

        latencies = [
            m.get('metadata',{}).get('ranking_results',{}).get("avg_latency", 0)
            for m in models
        ]

        min_latency = min(latencies)
        max_latency = max(latencies)

        scored_models = []

        for model in models:
            ranking_results = model.get('metadata',{}).get('ranking_results',{})
            
            total_calls = ranking_results.get("total_calls", 0)
            success_calls = ranking_results.get("success_call_counts", 0)

            success_rate = ranking_results.get(
                "success_rate",
                self._safe_div(success_calls, total_calls)
            )

            avg_latency = ranking_results.get("avg_latency", 0)

            latency_score = self._normalize_latency(
                avg_latency,
                min_latency,
                max_latency
            )

            confidence_score = self._confidence_score(
                total_calls
            )

            final_score = (
                success_rate * self.weights.success_rate
                +
                latency_score * self.weights.latency
                +
                confidence_score * self.weights.confidence
            )

            scored = {
                **model,
                "latency_score": round(latency_score, 4),
                "confidence_score": round(confidence_score, 4),
                "final_score": round(final_score, 4),
            }

            scored_models.append(scored)

        scored_models.sort(
            key=lambda m: m["final_score"],
            reverse=True
        )

        return scored_models