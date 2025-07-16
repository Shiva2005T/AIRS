import asyncio
import websockets
import json
import os

# Try Kafka integration
try:
    from confluent_kafka import Producer
    kafka_available = True
except ImportError:
    kafka_available = False
    print("[!] confluent_kafka not installed. Skipping Kafka integration.")

# Kafka configuration and test connection
producer = None
if kafka_available:
    # Kafka Configuration (with minimal logging for mock mode)
   conf = {
    'bootstrap.servers': 'localhost:9092',
    'log.connection.close': False
    }


try:
        producer = Producer(conf)
        # Dummy ping to check Kafka availability
        producer.produce("logs_topic", value=b"ping")
        producer.flush()
        print("[✓] Kafka producer initialized.")
except Exception as e:
        print(f"[!] Kafka not reachable. Switching to local file save only.\n    Error: {e}")
        kafka_available = False

# WebSocket Handler
async def handle_connection(websocket, path=None):
    print(f"[+] Connection established on path: {path or 'N/A'}")
    print("Saving logs to:", os.path.abspath("received_logs.jsonl"))

    async for message in websocket:
        print(f" Log Received: {message}")
        try:
            # Save to local file
            with open("received_logs.jsonl", "a") as f:
                f.write(message + "\n")

            # Optionally send to Kafka
            if kafka_available and producer:
                producer.produce("logs_topic", value=message.encode("utf-8"))
                producer.flush()
        except Exception as e:
            print(f"[!] Error saving log: {e}")

# Start WebSocket server
async def main():
    host = "localhost"
    port = 8000
    print(f" Starting WebSocket server on ws://{host}:{port}/ws/logs")
    try:
        async with websockets.serve(handle_connection, host, port):
            await asyncio.Future()  # keep running forever
    except Exception as e:
        print(f"Failed to start server: {e}")

if __name__ == "__main__":
    asyncio.run(main())
