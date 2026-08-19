# Customer Churn Prediction

A customer churn prediction system for an e-commerce platform. This is an end-to-end MLOps pipeline: a trained XGBoost model is wrapped in a FastAPI service, customer data is stored in PostgreSQL, and the daily prediction pipeline is automated with Apache Airflow.

## How it works
1. **The model** is trained in a Jupyter notebook (`notebooks/main.ipynb`) on `datasets/data_ecommerce_customer_churn.csv` and saved to `models/model.joblib`.
2. **The FastAPI service** loads the model on startup and accepts customer data at the `POST /predict_batch` endpoint, returning the churn probability and risk level for each customer.
3. **PostgreSQL** stores the `customer_stats` table (customer characteristics) and the `customer_churn_predictions` table (prediction results).
4. **The Airflow DAG** (`predict_churn_pipeline`) reads customers from the database in batches (10,000 at a time) every day, sends them to the API, and writes the results back to the database.
5. **The `seed_postgres_db.py` script** creates the database and tables and fills them with synthetic data (500 records by default) for demonstration purposes.

## Churn risk levels
The risk level is derived from the churn probability `churn_prob`:

| Probability     | Risk level |
|-----------------|------------|
| `< 0.30`        | `Low`      |
| `0.30 – 0.49`   | `Medium`   |
| `>= 0.50`       | `High`     |

## Tech stack
- **Language / environment:** Python 3.13
- **ML:** XGBoost, scikit-learn, joblib, matplotlib, pandas
- **API:** FastAPI
- **UI:** Streamlit
- **Database:** PostgreSQL (psycopg2, SQLAlchemy)
- **Orchestration:** Apache Airflow
- **Infrastructure:** Docker, docker-compose
- **Testing:** pytest, FastAPI TestClient


## Quick start (Docker)
Copy the environment configuration and start all services:

```bash
cp .env.example .env
docker compose up --build
```

After startup:
- **API (FastAPI):** http://localhost:8000
  - Swagger docs: http://localhost:8000/docs
  - Health check: http://localhost:8000/health
- **UI (Streamlit):** http://localhost:8501
- **Airflow Webserver:** http://localhost:8080 (default login/password `airflow` / `airflow`)

The `churn-api` server creates the database, tables, and seeds them with synthetic data on startup via `entrypoint.sh` → `seed_postgres_db.py`. It also starts the Streamlit interface (http://localhost:8501), where you can enter customer data and get a churn prediction from the API.

After Airflow starts, trigger the `predict_churn_pipeline` DAG to run the first prediction. By default, the pipeline runs daily.

The `predict_churn_pipeline` DAG:
- **Schedule:** daily (`@daily`), no catch-up;
- **Workflow:** reads `customer_stats` in batches of 10,000 customers, sends them to `PREDICT_API_URL`, and writes the returned results (churn_prob, risk_level) to `customer_churn_predictions`;
- **Fault tolerance:** on API or database errors it rolls back the transaction and fails the task.

## Docker architecture

| Service             | Purpose                                            | Port |
|---------------------|----------------------------------------------------|------|
| `churn-api`         | FastAPI prediction service + Streamlit UI  | 8000, 8501 |
| `churn-db`          | PostgreSQL with customer data and predictions      | 5432 |
| `airflow-postgres`  | PostgreSQL for Airflow metadata                    | -    |
| `airflow-webserver` | Airflow web UI                                     | 8080 |
| `airflow-scheduler` | Airflow task scheduler                             | -    |
| `airflow-init`      | Airflow DB initialization and user creation        | -    |

## TODO:
- Add DVC
