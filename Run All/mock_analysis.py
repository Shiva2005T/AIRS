from confluent_kafka import Consumer, KafkaException
import joblib
import pickle
from river import preprocessing, anomaly
import json
import subprocess
import os

# --- Config ---
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "lambda-logs"
ISO_MODEL_PATH = "isolation_forest_model.pkl"
RIVER_MODEL_PATH = "river_model.pkl"
LOG_FILE = "received_logs.jsonl"

# --- Load models ---
iso_model = joblib.load(ISO_MODEL_PATH)
with open(RIVER_MODEL_PATH, "rb") as f:
    river_model = pickle.load(f)

# --- Feature extraction ---
def extract_features(log_line):
    return {
        "length": len(log_line),
        "error_flag": int("error" in log_line.lower()),
        "fail_flag": int("failed" in log_line.lower()),
        "word_count": len(log_line.split())
    }

# --- Kafka consumer setup ---
consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'anomaly-detection-group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe([KAFKA_TOPIC])

print("🔍 Real-time anomaly detection started...")

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if not msg or msg.error():
            if msg and msg.error():
                raise KafkaException(msg.error())
            continue
        log_line = msg.value().decode('utf-8')
        features = extract_features(log_line)
        feature_list = list(features.values())
        # Predict
        iso_pred = iso_model.predict([feature_list])[0]
        river_score = river_model.score_one(features)
        river_model.learn_one(features)  # No assignment!
        # Decision
        if iso_pred == -1 or river_score > 3:
            print(f"🚨 Anomaly! ISO={iso_pred}, River={river_score:.2f} | {log_line}")
            anomaly_data = {
                "log": log_line,
                "features": features,
                "iso_pred": int(iso_pred),
                "river_score": float(river_score),
                "rule_id": "anomaly_detected"
            }
            with open("detected_anomaly.json", "w") as f:
                json.dump(anomaly_data, f)
            subprocess.run(["python", "mock_gpt.py"], cwd=os.path.dirname(__file__))
        else:
            print(f"✅ Normal | ISO={iso_pred}, River={river_score:.2f}")
except KeyboardInterrupt:
    print("\n🛑 Stopped Anomaly Detection.")
finally:
    consumer.close()