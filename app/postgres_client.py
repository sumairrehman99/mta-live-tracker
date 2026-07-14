import psycopg2
import os

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "postgres"),
    dbname="mta",
    user="postgres",
    password="postgres",
)


def create_tables():
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS train_updates (
                id BIGSERIAL PRIMARY KEY,
                route_id TEXT NOT NULL,
                stop_id TEXT NOT NULL,
                stop_name TEXT,
                trip_id TEXT NOT NULL,
                arrival_time TIMESTAMPTZ,
                received_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_metrics (
                id BIGSERIAL PRIMARY KEY,
                recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                messages_processed INTEGER NOT NULL,
                elapsed_seconds DOUBLE PRECISION NOT NULL,
                messages_per_second DOUBLE PRECISION NOT NULL,
                messages_per_minute DOUBLE PRECISION NOT NULL
            );
        """)

    conn.commit()

    print("Tables created")


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        dbname="mta",
        user="postgres",
        password="postgres"
    )


if __name__ == "__main__":
    create_tables()