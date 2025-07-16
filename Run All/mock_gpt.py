import json
import os

if os.path.exists("detected_anomaly.json"):
    with open("detected_anomaly.json", "r") as f:
        data = json.load(f)
        print(f"[GPT] Received anomaly: {data}")
        suggestion = {
            "rule_id": data["rule_id"],
            "suggested_action": "Restart service"
        }
        with open("resolved_action.json", "w") as out:
            json.dump(suggestion, out)
        print("[✓] Action suggested and saved.")
else:
    print("[!] No detected anomaly found.")
