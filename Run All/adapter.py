import psutil
import time
import os
import json
import websocket
import subprocess
import threading
from datetime import datetime

# Configuration
WS_URL = WS_URL = "ws://localhost:8000" # Update if server address changes
WATCH_EXTENSIONS = [".py", ".sh"]
USER = os.getlogin()

# Connect to WebSocket with retry
def connect_ws():
    """Establish WebSocket connection with retry mechanism"""
    while True:
        try:
            ws = websocket.WebSocket()
            ws.connect(WS_URL)
            print("[✓] Connected to WebSocket")
            return ws
        except Exception as e:
            print(f"[x] WebSocket connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

# Monitor Running Processes
def scan_processes(ws):
    """Watch for new script executions"""
    seen = set()
    while True:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            pid, cmdline = proc.info['pid'], proc.info['cmdline']
            if not cmdline or pid in seen:
                continue
            if any(cmdline[0].endswith(ext) for ext in WATCH_EXTENSIONS):
                try:
                    seen.add(pid)
                    print(f"[→] Detected script: {' '.join(cmdline)} (PID: {pid})")
                    threading.Thread(target=capture_output, args=(cmdline, pid, ws)).start()
                except Exception as e:
                    print(f"[!] Error capturing process {pid}: {e}")
        time.sleep(2)

# Capture Real-time Output (improved)
def capture_output(cmdline, pid, ws):
    """Capture stdout and stderr concurrently"""
    try:
        process = subprocess.Popen(
            cmdline,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        def stream(pipe, log_type):
            for line in pipe:
                send_log(ws, pid, log_type, line.strip())

        # Launch streaming threads
        t1 = threading.Thread(target=stream, args=(process.stdout, "stdout"))
        t2 = threading.Thread(target=stream, args=(process.stderr, "stderr"))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        process.wait()
        send_log(ws, pid, "status", f"Process {pid} completed")

    except Exception as e:
        print(f"[!] Error processing output for {pid}: {e}")

# Send Logs
def send_log(ws, pid, log_type, line):
    """Format and send logs"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": USER,
        "pid": pid,
        "log_type": log_type,
        "message": line
    }
    try:
        ws.send(json.dumps(log_entry))
        print(f"[✔] Sent log: {log_entry}")
    except Exception as e:
        print(f"[x] WebSocket send failed: {e}")

# Main Execution
if __name__ == "__main__":
    ws = connect_ws()
    if ws:
        scan_processes(ws)
