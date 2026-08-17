import logging
import os
from datetime import datetime

import requests
from airflow.decorators import dag, task
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from models import CustomerStatsModel, CustomerChurnPredictionModel

load_dotenv()

API_URL = os.getenv("PREDICT_API_URL", "http://127.0.0.1:8000/predict_batch")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@churn-db:5432/customer_churn_db"
)
Base = declarative_base()

BATCH_SIZE = 10000


@dag(
    dag_id="predict_churn_pipeline",
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
)
def predict_pipeline():
    @task
    def trigger_predict():
        logging.info("Starting churn prediction pipeline execution.")
        logging.info("Connecting to database...")

        try:
            engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            logging.info("Successfully connected to the database.")
        except Exception as e:
            logging.error("Failed to connect or initialize database: %s", e)
            raise

        with Session(engine) as session:
            offset = 0

            while True:
                logging.info("Fetching customer batch (Offset: %s, Limit: %s)...", offset, BATCH_SIZE)
                stmt = (
                    select(CustomerStatsModel)
                    .order_by(CustomerStatsModel.customer_id)
                    .limit(BATCH_SIZE)
                    .offset(offset)
                )
                customers = session.scalars(stmt).all()

                if not customers:
                    logging.info("No more customer records to process.")
                    break

                logging.info("Fetched %s records from database.", len(customers))

                payload = [
                    {
                        "customer_id": customer.customer_id,
                        "Tenure": customer.tenure,
                        "WarehouseToHome": customer.warehouse_to_home,
                        "NumberOfDeviceRegistered": customer.number_of_device_registered,
                        "PreferedOrderCat": customer.preferred_order_cat,
                        "SatisfactionScore": customer.satisfaction_score,
                        "MaritalStatus": customer.marital_status,
                        "NumberOfAddress": customer.number_of_address,
                        "Complain": customer.complain,
                        "DaySinceLastOrder": customer.day_since_last_order,
                        "CashbackAmount": customer.cashback_amount,
                    }
                    for customer in customers
                ]

                try:
                    logging.info("Sending batch payload to prediction API: %s", API_URL)
                    response = requests.post(API_URL, json=payload, timeout=30)
                    response.raise_for_status()
                    logging.info("Prediction API response received successfully.")

                    predictions_data = response.json()

                    prediction_records = [
                        CustomerChurnPredictionModel(
                            customer_id=item["customer_id"],
                            churn_prob=item.get("churn_prob"),
                            risk_level=item.get("risk_level"),
                        )
                        for item in predictions_data['predictions']
                    ]

                    session.add_all(prediction_records)
                    session.commit()
                    logging.info("Saved %s predictions to the database.", len(prediction_records))

                except requests.RequestException as e:
                    logging.error("API Request failed: %s", e)
                    session.rollback()
                    raise
                except Exception as e:
                    logging.error("An error occurred during prediction processing: %s", e)
                    session.rollback()
                    raise

                offset += BATCH_SIZE

        logging.info("Churn prediction pipeline completed successfully.")

    trigger_predict()


predict_pipeline()
