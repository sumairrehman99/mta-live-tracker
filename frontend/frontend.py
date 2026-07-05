import os
import requests
import streamlit as st
from streamlit_geolocation import streamlit_geolocation

from app.station_lookup import get_stops_for_route, get_all_routes


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="MTA Train Arrivals", layout="centered")

st.title("MTA Train Arrivals")


@st.cache_data
def cached_routes():
    return get_all_routes()


@st.cache_data
def cached_stops_for_route(route):
    return get_stops_for_route(route)


location = streamlit_geolocation()

st.divider()

st.subheader("Nearby Arrivals")

if st.button("Get Nearby Arrivals"):
    if (
        not location
        or location["latitude"] is None
        or location["longitude"] is None
    ):
        st.warning("Click the location button and allow location access.")
        st.stop()

    response = requests.get(
        f"{API_URL}/nearby_arrivals",
        params={
            "lat": location["latitude"],
            "lon": location["longitude"],
        },
    )

    if response.status_code != 200:
        st.error(f"API error: {response.status_code}")
        st.code(response.text)
        st.stop()

    data = response.json()
    arrivals = data.get("arrivals", [])

    if not arrivals:
        st.warning("No nearby arrivals found yet.")
        st.stop()

    for arrival in arrivals[:10]:
        st.write(
            f"{arrival['route_id']} train — "
            f"{arrival['direction']} — "
            f"{arrival['stop_name']} — "
            f"{arrival['minutes_away']} min — "
            f"{arrival['distance']}m away"
        )


st.divider()

st.subheader("Search by Route")

route = st.selectbox(
    "Route",
    cached_routes(),
    index=None,
    placeholder="Select route",
)

direction = st.selectbox(
    "Direction",
    ["N", "S"],
    index=None,
    placeholder="Select direction",
)

if route and direction:
    route_stops = cached_stops_for_route(route)

    route_stops = route_stops[
        route_stops["stop_id"].astype(str).str.endswith(direction)
    ]

    if route_stops.empty:
        st.error("No stops found for that route/direction.")
        st.stop()

    stop_name = st.selectbox(
        "Stop",
        route_stops["stop_name"].unique(),
        index=None,
        placeholder="Select stop",
        key=f"stop_{route}_{direction}",
    )

    if stop_name:
        matching_stop = route_stops[
            route_stops["stop_name"] == stop_name
        ].iloc[0]

        required_stop_id = matching_stop["stop_id"]

        if st.button("Get Arrivals"):
            response = requests.get(
                f"{API_URL}/arrivals",
                params={
                    "route": route,
                    "stop_id": required_stop_id,
                },
            )

            if response.status_code != 200:
                st.error(f"API error: {response.status_code}")
                st.code(response.text)
                st.stop()

            data = response.json()

            if "message" in data:
                st.warning(data["message"])
                st.stop()

            arrivals = data.get("arrivals", [])

            if not arrivals:
                st.warning("No upcoming arrivals found.")
                st.stop()

            st.subheader(
                f"{data['route_id']} train — {data.get('stop_name', stop_name)}"
            )

            for arrival in arrivals:
                st.metric(
                    label=data.get("stop_name", stop_name),
                    value=f"{arrival['minutes_away']} min",
                )