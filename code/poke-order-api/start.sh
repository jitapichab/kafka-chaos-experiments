#!/bin/bash

RETRIES=10
WAIT=5

# Check if the database is ready
function wait_for_db() {
    echo "Waiting for database to be ready..."
    for i in $(seq 1 $RETRIES); do
        pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"
        if [ $? -eq 0 ]; then
            echo "Database is ready!"
            return 0
        fi
        echo "Database is not ready. Retrying in $WAIT seconds..."
        sleep $WAIT
    done
    echo "Database is not ready after $RETRIES attempts."
    return 1
}

# Check if the database is ready
wait_for_db
if [ $? -ne 0 ]; then
    echo "Exiting due to database readiness check failure."
    exit 1
fi

# Run alembic migrations
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

echo "Alembic upgrade successful. Starting FastAPI application..."
# Start the FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload