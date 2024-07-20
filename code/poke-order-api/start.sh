#!/bin/bash

RETRIES=5

WAIT=5

for i in $(seq 1 $RETRIES); do
        echo "Attempt $i: Running alembic upgrade head..."
        alembic upgrade head && break

        if [ "$i" -eq $RETRIES ]; then
            echo "Max retries reached. Alembic upgrade failed."
            exit 1
        fi

        echo "Alembic upgrade failed. Retrying in $WAIT seconds..."
        sleep $WAIT
    done

# Start the FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload