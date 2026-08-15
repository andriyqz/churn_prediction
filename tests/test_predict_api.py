import copy

def test_predict_success(client, valid_payload):
    response = client.post("/predict_batch", json=valid_payload)
    assert response.status_code == 200
    data = response.json()
    assert "churn_prob" in data['predictions'][0]
    assert 0.0 <= data['predictions'][0]["churn_prob"] <= 1.0


def test_predict_invalid_satisfaction_score(client, valid_payload):
    """Test (SatisfactionScore > 5)"""
    invalid_payload = copy.deepcopy(valid_payload)
    invalid_payload[0]["SatisfactionScore"] = 10

    response = client.post("/predict_batch", json=invalid_payload)
    assert response.status_code == 422

def test_predict_negative_tenure(client, valid_payload):
    """Test (Tenure < 0)"""
    invalid_payload = copy.deepcopy(valid_payload)
    invalid_payload[0]["Tenure"] = -5.0

    response = client.post("/predict_batch", json=invalid_payload)
    assert response.status_code == 422