from confluent_kafka import Consumer
import json
from collections import defaultdict
from datetime import datetime, timezone

from app.station_lookup import get_stop_name
from app.redis_client import redis_client
import os


consumer = Consumer({
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    "group.id": "mta-consumer-v4",
    "auto.offset.reset": "latest",
})

consumer.subscribe(["train-updates"])

# key: "route_id:stop_id"
# value: dict of trip_id -> latest arrival
arrivals_by_stop = defaultdict(dict)

print("Listening and writing to Redis...")


def parse_time(value):
    dt = datetime.fromisoformat(value)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            print(msg.error())
            continue

        arrival = json.loads(msg.value().decode("utf-8"))

        route_id = arrival["route_id"]
        stop_id = arrival["stop_id"]
        trip_id = arrival["trip_id"]

        arrival["stop_name"] = get_stop_name(stop_id)

        stop_key = f"{route_id}:{stop_id}"

        # IMPORTANT:
        # overwrite latest info for this trip instead of appending duplicates
        arrivals_by_stop[stop_key][trip_id] = arrival

        now = datetime.now(timezone.utc)

        future_arrivals = []

        for saved_trip_id, saved_arrival in arrivals_by_stop[stop_key].items():
            arrival_time = parse_time(saved_arrival["arrival_time"])

            if arrival_time > now:
                saved_arrival["minutes_away"] = int(
                    (arrival_time - now).total_seconds() // 60
                )
                future_arrivals.append(saved_arrival)

        future_arrivals = sorted(
            future_arrivals,
            key=lambda x: parse_time(x["arrival_time"])
        )[:5]

        # rebuild memory with only future arrivals
        arrivals_by_stop[stop_key] = {
            a["trip_id"]: a for a in future_arrivals
        }

        redis_key = f"arrivals:{route_id}:{stop_id}"

        redis_client.set(
            redis_key,
            json.dumps({
                "route_id": route_id,
                "stop_id": stop_id,
                "stop_name": get_stop_name(stop_id),
                "arrivals": future_arrivals,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }),
            ex=120,
        )

        print("Saved:", redis_key, len(future_arrivals))

except KeyboardInterrupt:
    pass

finally:
    consumer.close()