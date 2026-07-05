from fastapi import FastAPI
import json
from app.station_lookup import get_nearby_stops
from app.redis_client import redis_client
from datetime import datetime
import pytz

app = FastAPI()

ny_tz = pytz.timezone("America/New_York")


@app.get("/")
def home():
    return {"status": "ok"}


def calculate_minutes_away(arrival_time_string):
    arrival_time = datetime.fromisoformat(arrival_time_string)

    if arrival_time.tzinfo is None:
        arrival_time = ny_tz.localize(arrival_time)

    now = datetime.now(ny_tz)

    return int((arrival_time - now).total_seconds() // 60)


@app.get("/arrivals")
def get_arrivals(route: str, stop_id: str):
    key = f"arrivals:{route}:{stop_id}"

    data = redis_client.get(key)

    if data is None:
        return {"message": "No arrivals found"}

    data = json.loads(data)

    arrivals = []

    for arrival in data["arrivals"]:
        minutes_away = calculate_minutes_away(arrival["arrival_time"])

        if minutes_away < 0:
            continue

        arrival["minutes_away"] = minutes_away
        arrivals.append(arrival)

    data["arrivals"] = sorted(arrivals, key=lambda x: x["minutes_away"])

    return data


@app.get("/nearby_arrivals")
def get_nearby_arrivals(lat: float, lon: float, radius: int = 1500):
    nearby_stops = get_nearby_stops(lat, lon, radius)

    results = []

    for stop in nearby_stops:
        stop_id = stop["stop_id"]

        keys = redis_client.keys(f"arrivals:*:{stop_id}")

        for key in keys:
            redis_value = redis_client.get(key)

            if redis_value is None:
                continue

            data = json.loads(redis_value)

            for arrival in data["arrivals"]:
                minutes_away = calculate_minutes_away(arrival["arrival_time"])

                if minutes_away < 0:
                    continue

                results.append({
                    "route_id": data["route_id"],
                    "stop_id": stop_id,
                    "stop_name": stop["stop_name"],
                    "direction": "Northbound" if stop_id.endswith("N") else "Southbound",
                    "minutes_away": minutes_away,
                    "arrival_time": arrival["arrival_time"],
                    "distance": stop["distance"],
                })

    return {
        "lat": lat,
        "lon": lon,
        "arrivals": sorted(
            results,
            key=lambda x: (x["distance"], x["minutes_away"])
        )
    }


@app.get("/debug/keys")
def debug_keys():
    keys = redis_client.keys("arrivals:*")
    return {"keys": keys}