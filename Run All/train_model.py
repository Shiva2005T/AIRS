import json
from sklearn.ensemble import IsolationForest
from river import anomaly, preprocessing
import joblib
import pickle

# --- Load normal logs ---
def load_normal_logs(path):
    logs = []
    with open(path) as f:
        for line in f:
            try:
                entry = json.loads(line)
                log_obj = json.loads(entry["message"])
                logs.append(log_obj["log"])
            except Exception:
                continue
    return logs

# --- Load anomaly logs ---
def load_anomaly_logs(path):
    logs = []
    try:
        with open(path) as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    log_obj = json.loads(item["log"]) if isinstance(item["log"], str) else item["log"]
                    logs.append(log_obj if isinstance(log_obj, str) else log_obj.get("log", str(log_obj)))
            else:
                log_obj = json.loads(data["log"]) if isinstance(data["log"], str) else data["log"]
                logs.append(log_obj if isinstance(log_obj, str) else log_obj.get("log", str(log_obj)))
    except Exception:
        pass
    return logs

# --- Feature extraction ---
def extract_features(line):
    return {
        "length": len(line),
        "error_flag": int("error" in line.lower()),
        "fail_flag": int("failed" in line.lower()),
        "word_count": len(line.split())
    }

def extract_list(line):
    f = extract_features(line)
    return [f["length"], f["error_flag"], f["fail_flag"], f["word_count"]]

# --- Main training logic ---
if __name__ == "__main__":
    normal_logs = load_normal_logs("received_logs.jsonl")
    anomaly_logs = load_anomaly_logs("detected_anomaly.json")

    # Isolation Forest: fit on normal + anomaly logs
    X_train = [extract_list(l) for l in normal_logs + anomaly_logs]
    iso = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
    iso.fit(X_train)
    joblib.dump(iso, "isolation_forest_model.pkl")
    print("Saved isolation_forest_model.pkl")

    # River: fit only on normal logs (online)
    river_model = anomaly.HalfSpaceTrees(n_trees=25, height=7, seed=42)
    print("River model type:", type(river_model))
    if river_model is None:
        raise RuntimeError("River model failed to initialize!")

    for l in normal_logs:
        river_model.learn_one(extract_features(l))  # Do NOT assign back to river_model
    with open("river_model.pkl", "wb") as f:
        pickle.dump(river_model, f)
    print("Saved river_model.pkl")