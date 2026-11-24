import json
import os
import threading
import time

import db
import paho.mqtt.client as mqtt
from validation import valid_node_id


class Ingestor:
    def __init__(self, broker=None, port=None, on_telemetry=None, on_bands=None):
        self.broker = broker or os.environ.get("MQTT_BROKER", "127.0.0.1")
        self.port = int(port or os.environ.get("MQTT_PORT", "1883"))
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        username = os.environ.get("MQTT_USERNAME")
        password = os.environ.get("MQTT_PASSWORD")
        if username:
            self.client.username_pw_set(username, password)
        self.client.connect(self.broker, self.port, 60)
        self.on_telemetry = on_telemetry
        self.on_bands = on_bands
        self.thread = threading.Thread(target=self.client.loop_forever, daemon=True)

    def start(self):
        self.thread.start()

    def _on_connect(self, c, u, flags, rc, props=None):
        c.subscribe("vs/+/telemetry")
        c.subscribe("vs/+/bands")
        c.subscribe("vs/hello")

    def _on_message(self, c, u, msg):
        parts = msg.topic.split("/")
        if len(parts) < 3:
            return
        node_id = parts[1]
        kind = parts[2]
        if not valid_node_id(node_id):
            return
        try:
            d = json.loads(msg.payload)
        except (ValueError, TypeError):
            return
        if not isinstance(d, dict):
            return
        if kind == "telemetry":
            db.upsert_node(node_id)
            db.insert_telemetry(node_id, time.time(), d)
            if self.on_telemetry:
                self.on_telemetry(node_id, d)
        elif kind == "bands":
            db.upsert_node(node_id)
            db.insert_telemetry(node_id, time.time(), {
                "b1": d.get("b1"),
                "b2": d.get("b2"),
                "b3": d.get("b3"),
            })
            if self.on_bands:
                self.on_bands(node_id, d)
        elif kind == "hello":
            db.upsert_node(node_id)


if __name__ == "__main__":
    Ingestor().start()
    print("ingestor running on vs/# ...")
    while True:
        time.sleep(1)
