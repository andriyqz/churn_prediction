import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field
from enum import Enum

app = FastAPI()

class PreferedOrderCat(str, Enum):
    LAPTOP_ACCESSORY = "Laptop & Accessory"
    MOBILE_PHONE = "Mobile Phone"
    MOBILE = "Mobile"
    FASHION = "Fashion"
    GROCERY = "Grocery"
    OTHERS = "Others"

class MaritalStatus(str, Enum):
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"

class Complain(int, Enum):
    NO = 0
    YES = 1

class UserStats(BaseModel):
    Tenure: float = Field(ge=0.0)
    WarehouseToHome: float = Field(ge=0.0)
    NumberOfDeviceRegistered: int = Field(ge=1)
    PreferedOrderCat: PreferedOrderCat
    SatisfactionScore: int = Field(ge=1, le=5)
    MaritalStatus: MaritalStatus
    NumberOfAddress: int = Field(ge=1)
    Complain: Complain
    DaySinceLastOrder: int = Field(ge=0)
    CashbackAmount: float = Field(ge=0.0)

with open('models/model.joblib', 'rb') as file:
    model = joblib.load(file)

@app.get('/')
async def root():
    return {'success': True}

@app.post('/predict/')
async def predict(user_stats: UserStats):
    input_data = pd.DataFrame([user_stats.model_dump()])
    prediction = model.predict_proba(input_data)
    print(prediction)
    return {'churn_prob': round(float(prediction[0][1]), 2)}