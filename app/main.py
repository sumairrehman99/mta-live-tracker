import subprocess
import signal
import sys
import time

processes = []


def start(name, command):
    print(f"Starting {name}...")
    process = subprocess.Popen(command)
    processes.append(process)
    return process


def shutdown(*args):
    print("\nStopping all services...")

    for process in processes:
        if process.poll() is None:
            process.terminate()

    for process in processes:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Kafka producer
    start(
        "Producer",
        ["python", "-m", "producer.producer"]
    )

    time.sleep(2)

    # Kafka consumer
    start(
        "Consumer",
        ["python", "-m", "consumer.consumer"]
    )

    time.sleep(2)

    # FastAPI
    start(
        "FastAPI",
        [
            "uvicorn",
            "api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--reload",
        ],
    )

    time.sleep(2)

    # Streamlit
    start(
        "Streamlit",
        [
            "streamlit",
            "run",
            "frontend/frontend.py",
        ],
    )

    print("\nEverything is running!")
    print("Ctrl+C to stop all services.")

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()