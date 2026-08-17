from datetime import datetime, timezone
from enum import Enum, IntEnum

from sqlalchemy import Column, DateTime, Float, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import declarative_base

Base = declarative_base()


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


class CustomerStatsModel(Base):
    __tablename__ = "customer_stats"

    customer_id = Column(String, primary_key=True)
    tenure = Column(Float, nullable=False)
    warehouse_to_home = Column(Float, nullable=False)
    number_of_device_registered = Column(Integer, nullable=False)

    preferred_order_cat = Column(
        SQLEnum(PreferredOrderCategory, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    satisfaction_score = Column(Integer, nullable=False)
    marital_status = Column(
        SQLEnum(Marital, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    number_of_address = Column(Integer, nullable=False)
    complain = Column(Integer, nullable=False)
    day_since_last_order = Column(Integer, nullable=False)
    cashback_amount = Column(Float, nullable=False)

class CustomerChurnPredictionModel(Base):
    __tablename__ = "customer_churn_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), nullable=False)
    risk_level = Column(String(50), nullable=False)
    churn_prob = Column(Float, nullable=True)
    predicted_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )