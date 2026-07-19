import time
import json
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

MQTT_PORT = 8883
MQTT_BROKER = "157cc16c2b0443d0931cfacc745a094f.s1.eu.hivemq.cloud"
MQTT_USER = "SHH"
MQTT_PASSWORD = "grp16_shh"
player_hearts = {"player1": 60, "player2": 60, "player3": 60}
current_target = None

def on_connect(client, userdata, flags, rc, properties=None):
    print("MQTT connected")
    client.subscribe("house/players/+/heartbeat")
    client.subscribe("house/actuators/game4/target")

def on_message(client, userdata, msg):
    global current_target
    topic = msg.topic
    payload_str = msg.payload.decode()

    if topic.startswith("house/players/") and topic.endswith("/heartbeat"):
        try:
            bpm = int(payload_str)
            player_name = topic.split("/")[2]
            
            if player_name in player_hearts:
                player_hearts[player_name] = bpm
                print(f"Update: P1: {player_hearts['player1']} | P2: {player_hearts['player2']} | P3: {player_hearts['player3']}")

                highest_player = max(player_hearts, key=player_hearts.get)
                highest_bpm = player_hearts[highest_player]

                if highest_bpm > 60:
                    client.publish("house/sensors/scared", json.dumps({"heartrate": True, "player": highest_player}))
                else:
                    client.publish("house/sensors/scared", json.dumps({"heartrate": False, "player": None}))
        except Exception as e:
            print(f"Error parsing heartbeat data stream: {e}")

    elif topic == "house/actuators/game4/target":
        try:
            data = json.loads(payload_str)
            target_player = data.get("player")
            
            if target_player in player_hearts:
                print(f"[ACTION EXECUTED] Sending push notification output to: {target_player}")
                
                for p in player_hearts.keys():
                    if p != target_player:
                        client.publish(f"house/players/{p}/notifications", "")

                client.publish(f"house/players/{target_player}/notifications", "I'm closer than you think")
        except Exception as e:
            print(f"Error handling authorized jump scare delivery: {e}")

client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
#client.connect("localhost", 1883, 60)
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.tls_set()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

print("Waiting for players' heartrates")
client.loop_forever()