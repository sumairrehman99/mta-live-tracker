# MTA Live Tracker

A real-time NYC subway tracking and analytics platform built to process live MTA GTFS-Realtime data. The project ingests train updates through a streaming pipeline, stores and processes the data, and exposes real-time information through an API and dashboard.

I built this project to explore real-time data engineering concepts including event streaming, data pipelines, analytics engineering, and workflow orchestration.

## Overview

The application collects live subway updates from the MTA GTFS-Realtime feed and processes them through a Kafka-based streaming pipeline.

The system:

- Ingests real-time train data from the MTA GTFS-Realtime API
- Publishes events through Apache Kafka
- Processes and stores train updates in PostgreSQL
- Uses Redis for caching frequently accessed API responses
- Transforms operational data into analytics models using dbt
- Runs scheduled data workflows using Apache Airflow
- Provides a frontend dashboard using Streamlit

The goal was to build an end-to-end pipeline similar to what would be used in a production data platform.

---

# Architecture

```text
                 MTA GTFS-Realtime Feed
                          |
                          v
                  Kafka Producer
                          |
                          v
                    Apache Kafka
                          |
                          v
                  Kafka Consumer
                          |
              +-----------+-----------+
              |                       |
              v                       v
        PostgreSQL              Redis Cache
              |
              v
       dbt Transformations
              |
              v
        Analytics Marts
              |
              v
        Airflow DAG
              |
              v
         dbt Tests


FastAPI
   |
   v
PostgreSQL + Redis


Streamlit Dashboard
   |
   v
FastAPI API
```

---

# Data Pipeline

## Data Ingestion

The pipeline starts by consuming live subway updates from the MTA GTFS-Realtime feed.

A Python producer:

- Connects to the MTA feed
- Parses incoming transit updates
- Publishes train events to Kafka

The Kafka consumer:

- Reads events from Kafka topics
- Processes train updates
- Writes records into PostgreSQL

This allows the application to handle continuously changing transit data in real time.

---

# Backend API

The backend is built using FastAPI.

The API provides endpoints for retrieving subway arrival information.

Features include:

- Querying arrivals by route
- Looking up nearby stations
- Returning cached responses through Redis

Example endpoints:

```
GET /arrivals
GET /nearby_arrivals
```

Redis caching was added to reduce repeated database queries and improve response times.

---

# Analytics Engineering

## dbt Models

I used dbt to transform raw operational data into analytics-ready datasets.

The transformation workflow includes:

```
Raw Train Updates
        |
        v
Staging Models
        |
        v
Analytics Marts
```

dbt is responsible for:

- Cleaning and standardizing raw data
- Creating analytical models
- Testing data quality before downstream use

Implemented tests include:

- Unique key validation
- Required field checks
- Accepted value validation
- Pipeline freshness monitoring
- Custom SQL data quality tests

---

# Airflow Orchestration

Apache Airflow is used to automate the analytics workflow.

The Airflow DAG:

1. Executes dbt transformations
2. Runs dbt tests
3. Validates that processed data meets quality expectations

This allows the transformation workflow to run automatically instead of manually executing dbt commands.

---

# Performance Metrics

I added pipeline metrics to measure system performance.

Current measurements:

- Streaming throughput: approximately 25,000–30,000 messages/minute
- Average API latency: approximately 0.0094 seconds

These metrics help evaluate ingestion performance and API responsiveness.

---

# Technology Stack

## Streaming

- Apache Kafka
- Python

## Backend

- FastAPI
- Redis

## Database

- PostgreSQL

## Data Engineering

- dbt
- Apache Airflow
- SQL

## Frontend

- Streamlit

## Infrastructure

- Docker
- Docker Compose

---

# Running the Application

Start all services:

```bash
docker compose up -d
```

Services:

Frontend:

```
http://localhost:8501
```

API:

```
http://localhost:8000
```

Airflow:

```
http://localhost:8080
```

---

# Data Quality Checks

dbt tests can be run with:

```bash
dbt test
```

Current checks include:

- Ensuring required fields are populated
- Detecting duplicate records
- Validating route values
- Monitoring whether new train data is arriving

Example freshness check:

```sql
select
    max(received_at) as latest_update
from {{ ref('stg_train_updates') }}
having max(received_at) < now() - interval '30 minutes'
```

This detects when the ingestion pipeline has stopped receiving new data.

---

# Future Improvements

Some improvements I would like to add:

- Deploy the application to the cloud
- Add monitoring and alerting
- Add incremental dbt models
- Build additional transit analytics dashboards
- Add CI/CD automation

---

# What I Learned

This project helped me gain hands-on experience with:

- Designing streaming data pipelines
- Working with event-driven architectures
- Building and testing analytics models
- Orchestrating workflows with Airflow
- Managing containerized applications
- Building systems that process real-time data
