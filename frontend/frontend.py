import requests
import streamlit as st
import sys
from pathlib import Path
from streamlit_geolocation import streamlit_geolocation

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.station_lookup import get_stops_for_route, get_all_routes

API_URL = "http://127.0.0.1:8000"

st.title("MTA Train Arrivals")

#route = st.text_input("Route", value=7).strip().upper()
route = st.selectbox('Route', get_all_routes(), placeholder='Select Route')
direction = st.selectbox("Direction", ["N", "S"], placeholder='Select Direction')

location = streamlit_geolocation()

c1, c2 = st.columns([1, 1])

with c2:
    nearby_arrivals_clicked = st.button('Get Nearby Arrivals')

with c1:
    get_arrivals_clicked = st.button('Get Arrivals')

if nearby_arrivals_clicked:
    if (
        not location
        or location["latitude"] is None
        or location["longitude"] is None
    ):
        st.warning("Please click on the location button and allow location access to find nearby trains.")
        st.stop()

    lat = location["latitude"]
    lon = location["longitude"]

    response = requests.get(
        f"{API_URL}/nearby_arrivals",
        params={"lat": lat, "lon": lon}
    )

    st.write("Status code:", response.status_code)
    st.code(response.text)

    if response.status_code != 200:
        st.stop()

    data = response.json()

    for arrival in data["arrivals"][:10]:
        st.write(
            f"{arrival['route_id']} train — "
            f"{arrival['direction']} — "
            f"{arrival['stop_name']} — "
            f"{arrival['minutes_away']} min — "
            f"{arrival['distance']}m away"
        )

if get_arrivals_clicked:
    route_stops = get_stops_for_route(route)

    # only keep stops matching direction
    route_stops = route_stops[
        route_stops["stop_id"].astype(str).str.endswith(direction)
    ]

    if route_stops.empty:
        st.error("No stops found for that route/direction.")
        st.stop()

    stop_name = st.selectbox(
        "Stop",
        route_stops["stop_name"].unique()
    )

    matching_stop = route_stops[
        route_stops["stop_name"] == stop_name
    ].iloc[0]

    required_stop_id = matching_stop["stop_id"]

    st.write("Using stop_id:", required_stop_id)

    if st.button("Get Arrival"):
        response = requests.get(
            f"{API_URL}/arrivals",
            params={
                "route": route,
                "stop_id": required_stop_id
            }
        )

        data = response.json()

        if "message" in data:
            st.warning(data["message"])
            st.write("Tried key:", f"arrivals:{route}:{required_stop_id}")
            st.stop()

        st.subheader(f"{data['route_id']} train — {data.get('stop_name', stop_name)}")
        # print(data['arrivals'])
        for arrival in data["arrivals"]:
            st.metric(
                label=arrival["stop_name"],
                value=f"{arrival['minutes_away']} min"
            )