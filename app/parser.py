from datetime import datetime, timezone
import pytz


def extract_arrivals(feed):
    rows = []

    for entity in feed.entity:
        if not entity.HasField("trip_update"):
            continue

        trip = entity.trip_update.trip

        for update in entity.trip_update.stop_time_update:
            if update.HasField("arrival"):
                timestamp = update.arrival.time
            elif update.HasField("departure"):
                timestamp = update.departure.time
            else:
                continue

            rows.append({
                "route_id": trip.route_id,
                "trip_id": trip.trip_id,
                "stop_id": update.stop_id,
                "arrival_time": datetime.fromtimestamp(timestamp, tz=pytz.timezone('America/New_York')).isoformat()
            })

    return rows