import json
import os

if os.path.exists("resolved_action.json"):
    with open("resolved_action.json", "r") as f:
        data = json.load(f)
        print(f"[ACTION] Executing: {data['suggested_action']} for Rule {data['rule_id']}")
else:
    print("[!] No suggested action found.")
