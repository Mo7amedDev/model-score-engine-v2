from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.core.utils import loadJsonData, saveJsonData,saveErrorLog
from app.core.exceptions import ModelsNotFoundError
router = APIRouter()


# =========================================
# REQUEST SCHEMAS
# =========================================

class ResultCalls(BaseModel):
    model_id: str
    latency: float


class TrackingResult(BaseModel):
    successed_call_models: List[ResultCalls]
    failed_calls_model: List[ResultCalls]


# =========================================
# HELPERS
# =========================================

def update_model_stats(
    model: dict,
    success: bool,
    latency: float
):
    """
    Update ranking statistics for a model.
    """

    metadata = model.setdefault("metadata", {})

    ranking_results = metadata.setdefault(
        "ranking_results",
        {
            "total_calls": 0,
            "success_call_counts": 0,
            "failed_calls_counts": 0,
            "total_latency": 0.0,
            "avg_latency": 0.0,
            "success_rate": 0.0,
        }
    )

    # =========================
    # UPDATE COUNTERS
    # =========================

    ranking_results["total_calls"] += 1

    if success:
        ranking_results["success_call_counts"] += 1
    else:
        ranking_results["failed_calls_counts"] += 1

    ranking_results["total_latency"] += latency

    # =========================
    # DERIVED METRICS
    # =========================

    total_calls = ranking_results["total_calls"]

    ranking_results["avg_latency"] = (
        ranking_results["total_latency"] / total_calls
        if total_calls > 0 else 0
    )

    ranking_results["success_rate"] = (
        ranking_results["success_call_counts"] / total_calls
        if total_calls > 0 else 0
    )


def find_model(models: list, model_id: str):
    return next(
        (m for m in models if m.get("id") == model_id),
        None
    )


# =========================================
# ROUTE
# =========================================

@router.post("/models_calls")
def tracking(req: TrackingResult):

    models = loadJsonData("models_for_score_engine.json")

    not_found_models = []

    # =====================================
    # HANDLE SUCCESS CALLS
    # =====================================

    for m in req.successed_call_models:

        model = find_model(models, m.model_id)

        if not model:
            not_found_models.append(m.model_id)
            continue

        update_model_stats(
            model=model,
            success=True,
            latency=m.latency
        )

    # =====================================
    # HANDLE FAILED CALLS
    # =====================================

    for m in req.failed_calls_model:

        model = find_model(models, m.model_id)

        if not model:
            not_found_models.append(m.model_id)
            continue

        update_model_stats(
            model=model,
            success=False,
            latency=m.latency
        )

    # =====================================
    # SAVE UPDATED DATA
    # =====================================
    saveJsonData(
        models,
        "models_for_score_engine.json",
    )
    if (len(list(set(not_found_models))) > 0):
        saveErrorLog(ModelsNotFoundError(
            f"Update Tracking Warning: Models not found: {list(set(not_found_models))}"
        ))
    return {
        "success": True,
        "updated_models": (
            len(req.successed_call_models)
            + len(req.failed_calls_model)
        ),
        "not_found_models": list(set(not_found_models))
    }