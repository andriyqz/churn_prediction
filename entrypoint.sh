#!/bin/sh
set -e

# mock database
python scripts/seed_postgres_db.py

python -m streamlit run ./app/ui/main.py &

exec uvicorn app.main:app --host 0.0.0.0 --port 8000