import pandas as pd
from collections import defaultdict

from geopy.distance import geodesic

# Load GTFS files as strings so stop_id/route_id comparisons work correctly
stops = pd.read_csv("data/stops.txt", dtype=str)
routes = pd.read_csv("data/routes.txt", dtype=str)
trips = pd.read_csv("data/trips.txt", dtype=str)
stop_times = pd.read_csv("data/stop_times.txt", dtype=str)

# stop_id -> stop_name
stop_names = dict(zip(stops["stop_id"], stops["stop_name"]))

# stop_name -> list of stop_ids
stop_ids_by_name = defaultdict(list)

for _, row in stops.iterrows():
    stop_ids_by_name[row["stop_name"]].append(row["stop_id"])


def get_stop_name(stop_id):
    return stop_names.get(str(stop_id))


def get_stop_ids(stop_name):
    return stop_ids_by_name.get(stop_name, [])

def get_all_routes():
    return routes['route_id'].to_list()




def get_stops_for_route(route_id):
    route_id = str(route_id)

    route_trip_ids = trips.loc[
        trips["route_id"] == route_id,
        "trip_id"
    ]

    route_stop_ids = stop_times.loc[
        stop_times["trip_id"].isin(route_trip_ids),
        "stop_id"
    ].unique()

    route_stops = stops.loc[
        stops["stop_id"].isin(route_stop_ids),
        ["stop_id", "stop_name"]
    ]

    return route_stops.drop_duplicates().reset_index(drop=True)


def get_stop_id_for_station_direction(stop_name, direction):
    direction = direction.upper()

    if direction not in ["N", "S"]:
        raise ValueError("direction must be 'N' or 'S'")

    matching_ids = get_stop_ids(stop_name)

    for stop_id in matching_ids:
        if stop_id.endswith(direction):
            return stop_id

    return None


def get_nearby_stops(lat: float, lon: float, radius=1500):
    nearby_stops = []
    user_location = (lat, lon)

    for _, row in stops.iterrows():
        
        try:
            stop_lat = float(row['stop_lat'])
            stop_lon = float(row['stop_lon'])
        except (ValueError, TypeError):
            #print(row['stop_lat'], row['stop_lon'])
            continue

        distance = geodesic(user_location, (stop_lat, stop_lon)).meters

        if distance <= radius:
            nearby_stops.append({
                'stop_id': row['stop_id'],
                'stop_name': row['stop_name'],
                'distance': round(distance)
            })

    return sorted(nearby_stops, key=lambda x : x['distance'])
