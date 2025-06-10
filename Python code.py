import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
import time
from datetime import datetime

# ===== Configuratie =====
MQTT_BROKER = "192.168.1.42"
MQTT_PORT = 1883
INFLUX_HOST = "localhost"
INFLUX_DB = "test_mqtt"

# ===== InfluxDB Setup =====
influx = InfluxDBClient(host=INFLUX_HOST, database=INFLUX_DB)

# ===== MQTT Callbacks =====
def on_connect(client, userdata, flags, rc, properties):
    print(f"Verbonden met MQTT (code: {rc})")
    client.subscribe([
        ("robot/status", 0),
        ("robot/sensors/voor", 0),
        ("robot/drukknop", 0)  
    ])

def on_message(client, userdata, msg):
    try:
        timestamp = datetime.utcnow().isoformat()
        topic = msg.topic
        payload = msg.payload.decode()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {topic} : {payload}")
        
        if topic == "robot/status":
            # Schrijf naar alle 3 measurements met 1/0
            statuses = ["Stoppen", "Lijnvolgen", "Obstakel"]
            
            for status in statuses:
                influx.write_points([{
                    "measurement": status.lower(),
                    "tags": {"robot": "esp32"},
                    "fields": {
                        "value": 1 if payload == status else 0
                    },
                    "time": timestamp
                }])
        
        elif topic == "robot/drukknop":  # Nieuwe drukknop verwerking
            status = "ingedrukt" if payload == "1" else "losgelaten"
            influx.write_points([{
                "measurement": "drukknoprobotje",
                "tags": {"component": "button"},
                "fields": {"value": int(payload)},
                "time": timestamp
            }])
            print(f"Knopstatus: {status}")
            
        elif "sensors" in topic:
            # Bestaande sensor logica
            if "voor" in topic:
                influx.write_points([{
                    "measurement": "voor_sensor",
                    "tags": {"type": "ultrasonic"},
                    "fields": {"value": float(payload)},
                    "time": timestamp
                }])

            
    except Exception as e:
        print(f"Verwerkingsfout: {str(e)}")

# ===== Hoofdprogramma =====
def main():
    print("=== Robot Monitoring Systeem ===")
    print("Configuratie:")
    print(f"- MQTT Broker: {MQTT_BROKER}")
    print(f"- InfluxDB Database: {INFLUX_DB}\n")
    
    # MQTT Client setup
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        print("Start monitoring... (Ctrl+C om te stoppen)\n")
        mqtt_client.loop_forever()
        
    except KeyboardInterrupt:
        print("\nAfsluiten...")
    finally:
        mqtt_client.disconnect()
        influx.close()

if __name__ == "__main__":
    # Eerst database aanmaken indien nodig
    influx.create_database(INFLUX_DB)
    main()