import logging
from pathlib import Path

import joblib
import pandas as pd

from app.schemas import UserStats
from app.settings import settings

logger = logging.getLogger(__name__)


class ModelService:
    def __init__(self, model_path: Path):
        self.model_path = model_path
        self.model = None

    def load_model(self):
        if not self.model_path.exists():
            logger.critical(f"Model file not found: {self.model_path}")
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        self.model = joblib.load(self.model_path)

    def predict(self, users_stats: list[UserStats]) -> list[float | int]:
        input_batch = [user_stats.model_dump(mode="json") for user_stats in users_stats]
        input_df = pd.DataFrame(input_batch)
        predictions = self.model.predict_proba(input_df)

        return [round(float(prediction[1]), 2) for prediction in predictions]


model_service = ModelService(settings.model_path)
