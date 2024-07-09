#!/bin/bash

# Run Alembic migrations
python migrate.py

# Start the FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload