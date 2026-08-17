import logging
import os
import random

import psycopg2
from dotenv import load_dotenv
from faker import Faker
from psycopg2.extras import execute_values

from app.schemas import (
    Complaint,
    Marital,
    PreferredOrderCategory,
    UserStats,
)

print('START START START')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

load_dotenv()

TARGET_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@churn-db:5432/customer_churn_db",
)

SYS_DATABASE_URL = os.getenv(
    "SYS_DATABASE_URL",
    TARGET_DATABASE_URL.rsplit("/", 1)[0] + "/postgres",
)

fake = Faker()


def generate_fake_users(count: int = 1000) -> list[UserStats]:
    logger.info("Generating %d fake users...", count)
    users = []

    for _ in range(count):
        user = UserStats(
            customer_id=f"CUST-{fake.random_int(min=10000, max=99999)}",
            Tenure=round(random.uniform(0.0, 61.0), 1),
            WarehouseToHome=round(random.uniform(5.0, 127.0), 1),
            NumberOfDeviceRegistered=random.randint(1, 6),
            PreferedOrderCat=random.choice(list(PreferredOrderCategory)),
            SatisfactionScore=random.randint(1, 5),
            MaritalStatus=random.choice(list(Marital)),
            NumberOfAddress=random.randint(1, 10),
            Complain=random.choice([Complaint.NO, Complaint.YES]),
            DaySinceLastOrder=random.randint(0, 31),
            CashbackAmount=round(random.uniform(0.0, 350.0), 2),
        )
        users.append(user)

    logger.info("Successfully generated %d users.", len(users))
    return users


def insert_fake_users_to_postgres(count: int = 500):
    fake_users = generate_fake_users(count)

    records = [
        (
            u.customer_id,
            u.Tenure,
            u.WarehouseToHome,
            u.NumberOfDeviceRegistered,
            u.PreferedOrderCat.value,
            u.SatisfactionScore,
            u.MaritalStatus.value,
            u.NumberOfAddress,
            u.Complain.value,
            u.DaySinceLastOrder,
            u.CashbackAmount,
        )
        for u in fake_users
    ]

    insert_query = """
                   INSERT INTO customer_stats (customer_id, tenure, warehouse_to_home, number_of_device_registered, \
                                               preferred_order_cat, satisfaction_score, marital_status, \
                                               number_of_address, \
                                               complain, day_since_last_order, cashback_amount) \
                   VALUES %s ON CONFLICT (customer_id) DO NOTHING; \
                   """

    logger.info("Inserting %d records into PostgreSQL database...", len(records))
    try:
        conn = psycopg2.connect(TARGET_DATABASE_URL)
        with conn.cursor() as cur:
            execute_values(cur, insert_query, records)
            conn.commit()
        conn.close()
        logger.info("Records inserted successfully.")
    except Exception as e:
        logger.error("Failed to insert records into database: %s", e)
        raise


def init_db_and_tables():
    logger.info("Initializing database and table schema...")
    try:
        conn = psycopg2.connect(SYS_DATABASE_URL)
        conn.autocommit = True

        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = 'customer_churn_db'"
            )
            if not cur.fetchone():
                logger.info(
                    "Database 'customer_churn_db' does not exist. Creating database..."
                )
                cur.execute("CREATE DATABASE customer_churn_db;")
            else:
                logger.info("Database 'customer_churn_db' already exists.")
        conn.close()

        conn = psycopg2.connect(TARGET_DATABASE_URL)

        with conn.cursor() as cur:
            cur.execute("""
                        CREATE TABLE IF NOT EXISTS customer_stats
                        (
                            customer_id VARCHAR(50) PRIMARY KEY,
                            tenure NUMERIC(5, 1) NOT NULL,
                            warehouse_to_home NUMERIC(5, 1) NOT NULL,
                            number_of_device_registered INT NOT NULL,
                            preferred_order_cat VARCHAR(50) NOT NULL,
                            satisfaction_score INT CHECK (satisfaction_score BETWEEN 1 AND 5),
                            marital_status VARCHAR(50) NOT NULL,
                            number_of_address INT NOT NULL,
                            complain SMALLINT CHECK (complain IN (0, 1)),
                            day_since_last_order INT NOT NULL,
                            cashback_amount NUMERIC(7, 2) NOT NULL,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        );

                        CREATE TABLE IF NOT EXISTS customer_churn_predictions
                        (
                            id SERIAL PRIMARY KEY,
                            customer_id VARCHAR(50) NOT NULL,
                            risk_level VARCHAR(50) NOT NULL,
                            churn_prob FLOAT,
                            predicted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        );
                        """)
            conn.commit()
        conn.close()
        logger.info("Tables 'customer_stats' and 'customer_churn_predictions' verified/created successfully.")
    except Exception as e:
        logger.error("Database initialization failed: %s", e)
        raise


if __name__ == "__main__":
    logger.info("Starting pipeline execution...")
    init_db_and_tables()
    insert_fake_users_to_postgres(count=500)
    logger.info("Pipeline execution completed successfully.")