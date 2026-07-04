import paho.mqtt.client as mqtt
import json

mqtt_live_state = {
    "pir_triggered_3_people": False,
    "door_sensor_active": False,
    "angle_g1_sensor_active": False,
    "ultrasonic_g3_sensor_active": False,
    "ultrasonic_g2_sensor_active": False,
    "scaredy_cat_g4_active": False,
    "riddle_timeout_reached": False,
    "exit_timeout_reached": False,
    "light_sensor_active": False,
    "red_led_active": False 
}

def on_message(client, userdata, msg):
    global mqtt_live_state
    
    payload = json.loads(msg.payload.decode())
    
    if msg.topic == "house/sensors/pir":
        if payload.get("count", 0) >= 3:
            mqtt_live_state["pir_triggered_3_people"] = True
            
    elif msg.topic == "house/sensors/light":
        if payload.get("lux", 0) > 500:
            mqtt_live_state["light_sensor_active"] = True

    elif msg.topic == "house/sensors/ultrasonic_g2":
        if payload.get("lux", 0) > 500:
            mqtt_live_state["ultrasonic_g2_sensor_active"] = True

    elif msg.topic == "house/sensors/ultrasonic_g3":
        if payload.get("lux", 0) > 500:
            mqtt_live_state["ultrasonic_g3_sensor_active"] = True

    elif msg.topic == "house/sensors/angle":
        if payload.get("lux", 0) > 500:
            mqtt_live_state["angle_g1_sensor_active"] = True

    elif msg.topic == "house/sensors/scared":
        if payload.get("lux", 0) > 500:
            mqtt_live_state["scaredy_cat_g4_active"] = True
    
    elif msg.topic == "house/timers/game_over":
        if payload.get("status") == "expired":
            mqtt_live_state["red_led_active"] = True

client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("house/#")
client.loop_start()