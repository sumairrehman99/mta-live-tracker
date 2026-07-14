# MTA Live Tracker

A real-time NYC subway arrival tracker built using GTFS Realtime data. The application continuously ingests live train updates, processes them through a streaming pipeline, caches upcoming arrivals in Redis, and exposes a FastAPI backend consumed by a Streamlit frontend.

The project was built to explore real-time data engineering concepts including event streaming, message queues, caching, containerization, and API development.

---

## Features

- Real-time subway arrival predictions
- Route and direction selection
- Stop lookup for each route
- Upcoming train arrivals in minutes
- FastAPI REST API
- Streamlit frontend
- Redis caching for low-latency responses
- Kafka-based streaming pipeline
- Dockerized services
- CI/CD with GitHub Actions

---

## Architecture

```
GTFS Realtime Feed
        │
        ▼
Python Producer
        │
        ▼
Kafka Topic
        │
        ▼
Python Consumer
        │
        ▼
Redis Cache
        │
        ▼
FastAPI
        │
        ▼
Streamlit Frontend
```

---

## Tech Stack

- Python
- FastAPI
- Streamlit
- Apache Kafka
- Redis
- Docker & Docker Compose
- GitHub Actions
- GTFS Realtime
- Pandas

---

## How It Works

1. A producer continuously polls the MTA GTFS Realtime feed.
2. Live train updates are published to Kafka.
3. A consumer processes each message and stores upcoming arrivals in Redis.
4. FastAPI queries Redis to retrieve arrival information.
5. Streamlit displays arrivals through a simple user interface.

Because Redis stores preprocessed arrivals, API requests complete in milliseconds without repeatedly parsing the GTFS feed.


---

## Running Locally

Clone the repository

```bash
git clone https://github.com/sumairrehman99/mta-live-tracker.git
cd mta-live-tracker
```

Start all services

```bash
docker compose up --build
```

The application will start:

- Kafka
- Redis
- FastAPI
- Streamlit

---

## API

### Get Arrivals

```
GET /arrivals
```

Example

```
/arrivals?route=A&stop_id=A42
```

Response

```json
{
  "route": "A",
  "stop_name": "42 St-Port Authority Bus Terminal",
  "arrivals": [
    {
      "arrival_time": "2026-07-05T14:23:00-04:00",
      "minutes_away": 3
    }
  ]
}
```

---

## Future Improvements

- Nearby stations using device location
- Native iOS and Android apps
- Push notifications for approaching trains
- Historical on-time performance analytics
- Service disruption alerts
- Journey planner
- Arrival prediction models using historical data
- Interactive subway map

---

## Motivation

This project was built to gain hands-on experience with real-time data engineering systems. Rather than querying the GTFS feed on every request, the application maintains a continuously updated cache of arrivals, demonstrating an event-driven architecture commonly used in production systems.
