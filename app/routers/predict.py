import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas import UserStats, SinglePrediction, PredictionResponse
from app.services import model_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get('/health')
async def health_check():
    is_loaded = model_service.model is not None
    return {'status': 'ok', 'model_loaded': is_loaded}


@router.post('/predict_batch', response_model=PredictionResponse)
async def predict_batch(users_stats: list[UserStats]):
    if model_service.model is None:
        logger.error("Attempted to predict while model is not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not available. Please try again later."
        )

    try:
        churn_probs = model_service.predict(users_stats)

        predictions = [
            SinglePrediction(
                customer_id=user.customer_id,
                churn_prob=prob
            )
            for user, prob in zip(users_stats, churn_probs)
        ]

        return PredictionResponse(predictions=predictions)

    except Exception as e:
        logger.error(f"Error during model's inference: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred."
        )