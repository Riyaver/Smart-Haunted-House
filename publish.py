import time
import json
import paho.mqtt.client as mqtt
import grovepi

MQTT_BROKER = "localhost" 
TOPIC = "haunted_house/sensors/game2/ultrasonic"

client = mqtt.Client()
client.connect(MQTT_BROKER, 1883, 60)

print("OOOh")

while True:
    try:
        dist = grovepi.ultrasonicRead(4)
        is_close = 0 < dist < 30
        
        # Just stream raw/boolean status to the broker
        client.publish(TOPIC, json.dumps({"triggered": is_close}))
    except IOError:
        pass
    time.sleep(0.2)