import time
import json
import websocket

WS_URL = "ws://localhost:8000/ws/logs"

fake_logs = [
    {"log": "User logged in successfully"},  # Normal
    {"log": "Failed login attempt detected"},  # Normal
    {"log": "Unauthorized access attempt"},  #  Suspicious
    {"log": "Running system scan"},  # Normal
    {"log": "Potential SQL injection attack"},  #  Suspicious
    {"log": "Downloaded file is clean"},  # Normal
    {"log": "Malware detected in temp folder"},  #  Suspicious
    {"log": "Suspicious process running on host"},  #  Suspicious
]

def send_logs():
    try:
        ws = websocket.create_connection(WS_URL)
        print("[✓] Connected to WebSocket")

        for i, log_entry in enumerate(fake_logs):
            message = json.dumps(log_entry)
            ws.send(message)
            print(f"[TEST] Sent Log {i+1}: {log_entry['log']}")
            time.sleep(1.5)

        ws.close()
    except Exception as e:
        print(f"[x] WebSocket connection failed: {e}")

if __name__ == "__main__":
    send_logs()
