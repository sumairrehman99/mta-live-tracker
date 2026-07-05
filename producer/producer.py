import time
import json
from confluent_kafka import Producer

from app.mta_client import get_feed, FEEDS
from app.parser import extract_arrivals
from datetime import datetime
import os

producer = Producer({
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
})

TOPIC = 'train-updates'

def send_arrivals():
    for feed_name, url in FEEDS.items():
        feed = get_feed(url=url)
        arrivals = extract_arrivals(feed)

        for arrival in arrivals:
            producer.produce(
                topic=TOPIC,
                key=arrival['stop_id'],
                value=json.dumps(arrival)
            )

        producer.flush()
        print(feed_name, 'feed sent at', datetime.now().isoformat())

if __name__ == '__main__':
    while True:
        send_arrivals()
        time.sleep(30)