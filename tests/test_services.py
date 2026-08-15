from app.schemas import UserStats
from app.services import model_service


def test_model_inference_format(valid_payload):
    user_data = UserStats(**valid_payload[0])
    probability = model_service.predict([user_data])[0]

    assert isinstance(probability, float)
    assert 0.0 <= probability <= 1.0