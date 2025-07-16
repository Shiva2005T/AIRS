# run_all.py
import subprocess
import time
import os

scripts = [
    "ws_server.py",
    "target_script.py",
    "adapter.py",
    "mock_analysis.py",
    "mock_gpt.py",
    "train_model.py",
    "mock_action.py"
]

print("\n Launching Full Mock Cybersecurity Pipeline...\n")

for script in scripts:
    path = os.path.join(os.getcwd(), script)
    if os.path.exists(path):
        print(f"[+] Starting {script}...")
        subprocess.Popen(["python", path])
        time.sleep(2)  # Delay to ensure order
    else:
        print(f"[x] {script} not found, skipping.")

print("\n[✓] All scripts running. Press Ctrl+C to stop.")
