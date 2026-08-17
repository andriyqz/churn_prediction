import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def valid_payload():
    return [{
        "customer_id": "CUST-9999",
        "Tenure": 12.0,
        "WarehouseToHome": 10.0,
        "NumberOfDeviceRegistered": 3,
        "PreferedOrderCat": "Mobile Phone",
        "SatisfactionScore": 4,
        "MaritalStatus": "Single",
        "NumberOfAddress": 2,
        "Complain": 0,
        "DaySinceLastOrder": 5,
        "CashbackAmount": 150.0,
    }]
