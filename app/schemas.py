from enum import Enum, IntEnum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, computed_field


class PreferredOrderCategory(str, Enum):
    LAPTOP_ACCESSORY = "Laptop & Accessory"
    MOBILE_PHONE = "Mobile Phone"
    MOBILE = "Mobile"
    FASHION = "Fashion"
    GROCERY = "Grocery"
    OTHERS = "Others"


class Marital(str, Enum):
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"


class Complaint(IntEnum):
    NO = 0
    YES = 1


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class UserStats(BaseModel):
    customer_id: Optional[str] = Field()
    Tenure: float = Field(ge=0.0)
    WarehouseToHome: float = Field(ge=0.0)
    NumberOfDeviceRegistered: int = Field(ge=1)
    PreferedOrderCat: PreferredOrderCategory = Field()
    SatisfactionScore: int = Field(ge=1, le=5)
    MaritalStatus: Marital = Field()
    NumberOfAddress: int = Field(ge=1)
    Complain: Complaint = Field()
    DaySinceLastOrder: int = Field(ge=0)
    CashbackAmount: float = Field(ge=0.0)


class SinglePrediction(BaseModel):
    customer_id: Optional[str] = Field(default=None)
    churn_prob: float = Field(ge=0.0, le=1.0)

    @computed_field
    @property
    def risk_level(self) -> RiskLevel:
        if self.churn_prob >= 0.5:
            return RiskLevel.HIGH
        elif self.churn_prob >= 0.3:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW


class PredictionResponse(BaseModel):
    predictions: List[SinglePrediction]