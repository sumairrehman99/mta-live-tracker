from confluent_kafka import Consumer
import json
from collections import defaultdict
from datetime import datetime, timezone
import os
import time

from app.station_lookup import get_stop_name
from app.redis_client import redis_client
from app.postgres_client import create_tables, get_connection


conn = get_connection()
create_tables()


consumer = Consumer({
    "bootstrap.servers": os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "localhost:9092"
    ),
    "group.id": "mta-consumer-v4",
    "auto.offset.reset": "latest",
})

consumer.subscribe(["train-updates"])


arrivals_by_stop = defaultdict(dict)


def parse_time(value):
    dt = datetime.fromisoformat(value)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def insert_train_update(
    route_id,
    stop_id,
    stop_name,
    trip_id,
    arrival_time
):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO train_updates
                (
                    route_id,
                    stop_id,
                    stop_name,
                    trip_id,
                    arrival_time
                )
                VALUES (%s,%s,%s,%s,%s)
                """,
                (
                    route_id,
                    stop_id,
                    stop_name,
                    trip_id,
                    arrival_time
                )
            )

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Postgres train update error: {e}")


def insert_pipeline_metric(
    messages_processed,
    elapsed_seconds,
    messages_per_second,
    messages_per_minute
):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO pipeline_metrics
                (
                    messages_processed,
                    elapsed_seconds,
                    messages_per_second,
                    messages_per_minute
                )
                VALUES (%s,%s,%s,%s)
                """,
                (
                    messages_processed,
                    elapsed_seconds,
                    messages_per_second,
                    messages_per_minute
                )
            )

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Pipeline metrics error: {e}")


print("Listening and writing to Redis...", flush=True)


messages_received = 0
start_time = time.time()

THROUGHPUT_WINDOW_SECONDS = 60

INGESTION_WINDOW = 100
ingestion_count = 0


try:
    while True:

        elapsed = time.time() - start_time


        # Every 60 seconds write pipeline metrics
        if elapsed >= THROUGHPUT_WINDOW_SECONDS:

            msg_per_sec = messages_received / elapsed
            msg_per_min = msg_per_sec * 60

            print(
                f"CONSUMER THROUGHPUT: "
                f"{messages_received} messages in {elapsed:.1f}s "
                f"({msg_per_sec:.2f} msg/sec, "
                f"{msg_per_min:.0f} msg/min)",
                flush=True
            )


            insert_pipeline_metric(
                messages_received,
                elapsed,
                msg_per_sec,
                msg_per_min
            )


            messages_received = 0
            start_time = time.time()



        msg = consumer.poll(1.0)


        if msg is None:
            continue


        if msg.error():
            print(msg.error(), flush=True)
            continue



        arrival = json.loads(
            msg.value().decode("utf-8")
        )


        route_id = arrival["route_id"]
        stop_id = arrival["stop_id"]
        trip_id = arrival["trip_id"]

        stop_name = get_stop_name(stop_id)

        arrival["stop_name"] = stop_name


        stop_key = f"{route_id}:{stop_id}"


        arrivals_by_stop[stop_key][trip_id] = arrival


        now = datetime.now(timezone.utc)

        future_arrivals = []


        for saved_arrival in arrivals_by_stop[stop_key].values():

            arrival_time = parse_time(
                saved_arrival["arrival_time"]
            )

            if arrival_time > now:

                saved_arrival["minutes_away"] = int(
                    (
                        arrival_time - now
                    ).total_seconds() // 60
                )

                future_arrivals.append(saved_arrival)



        future_arrivals = sorted(
            future_arrivals,
            key=lambda x: parse_time(
                x["arrival_time"]
            )
        )[:5]


        arrivals_by_stop[stop_key] = {
            a["trip_id"]: a
            for a in future_arrivals
        }


        redis_key = f"arrivals:{route_id}:{stop_id}"


        redis_client.set(
            redis_key,
            json.dumps(
                {
                    "route_id": route_id,
                    "stop_id": stop_id,
                    "stop_name": stop_name,
                    "arrivals": future_arrivals,
                    "last_updated": datetime.now(
                        timezone.utc
                    ).isoformat(),
                }
            ),
            ex=120,
        )


        # Count messages
        ingestion_count += 1


        # Store every 100th message in Postgres
        if ingestion_count % INGESTION_WINDOW == 0:

            insert_train_update(
                route_id,
                stop_id,
                stop_name,
                trip_id,
                arrival["arrival_time"]
            )


        print(
            "Saved:",
            redis_key,
            len(future_arrivals),
            flush=True
        )


        messages_received += 1



except KeyboardInterrupt:
    pass


finally:
    consumer.close()
    conn.close()