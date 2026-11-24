import json, time, threading
import paho.mqtt.client as mqtt
import db

class Ingestor:
    def __init__(self, broker="127.0.0.1", port=1883,
                 on_telemetry=None, on_bands=None):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.connect(broker, port, 60)
        self.on_telemetry = on_telemetry
        self.on_bands = on_bands
        self.thread = threading.Thread(target=self.client.loop_forever, daemon=True)

    def start(self): self.thread.start()

    def _on_connect(self, c, u, flags, rc, props=None):
        c.subscribe("vs/+/telemetry")
        c.subscribe("vs/+/bands")
        c.subscribe("vs/hello")

    def _on_message(self, c, u, msg):
        parts = msg.topic.split("/")
        if len(parts) < 3: return
        node_id = parts[1]; kind = parts[2]
        if kind == "telemetry":
            d = json.loads(msg.payload)
            db.upsert_node(node_id)
            db.insert_telemetry(node_id, time.time(), d)
            if self.on_telemetry: self.on_telemetry(node_id, d)
        elif kind == "bands":
            d = json.loads(msg.payload)
            db.upsert_node(node_id)
            db.insert_telemetry(node_id, time.time(), {"b1": d["b1"], "b2": d["b2"], "b3": d["b3"]})
            if self.on_bands: self.on_bands(node_id, d)
        elif kind == "hello":
            db.upsert_node(node_id)

if __name__ == "__main__":
    Ingestor().start()
    print("ingestor running on vs/# ...")
    while True: time.sleep(1)
