import paho.mqtt.client as mqtt
import json
import threading
from time import sleep
import random
import sys
from python_problem_generation import generate_problem

mqtt_live_state = {
    "door_sensor_active": False,
    "angle_g1_sensor_active": False,
    "ultrasonic_g2_sensor_active": False,
    "ultrasonic_g3_sensor_active": False,
    "scaredy_cat_g4_active": False,
    "riddle_g5_active": False,
    "light_g6_sensor_active": False,
    "active_led_game": None,       
    "completed_games": []         
}

mutex = False
state_changed = False

NECESS_GAMES = ["game1", "game2", "game3", "game4"]
ALL_GAMES = ["game1", "game2", "game3", "game4", "game5", "game6"]

def run():
    global mutex
    global state_changed
    while True:
        if mutex == False:
            mutex = True
            if state_changed == True:
                state_changed = False
                print('Detected a state change. Generating a new problem based on current state')
                print('Current State :')
                print(mqtt_live_state)
                actions_sequence, goal_achieved, status = generate_problem(mqtt_live_state)
                
                if actions_sequence:
                    print(actions_sequence)
                    for chosen_action in actions_sequence:
                        action_name = chosen_action.action.name
                        params = chosen_action.actual_parameters
                        if action_name.startswith("human_"):
                            print(f"Carry on with current game")
                            continue
                        elif action_name in ["solve_physical_sensor_game", "game_5", "game_4", "game_6_exit"]:
                                current_room = str(params[3])
                                target_device = str(params[2])
                                print(f"[HARDWARE ACTION AUTHORIZED] Activating device: {target_device} inside {current_room}")
                                hardware_payload = {"status": "TRIGGERED", "device_id": target_device, "action": "ACTIVATE"}
                                client.publish(f"house/actuators/{current_room}/device", json.dumps(hardware_payload))
                                client.publish(f"house/actuators/{current_room}/led", json.dumps({"power": "OFF"}))

                                mqtt_live_state["completed_games"].append(current_room)    
                else:
                    print("No planning possible")
                    print(status)

                if len(mqtt_live_state["completed_games"]) >=6:
                    print('GG')
                    return
                
            mutex = False


def on_message(client, userdata, msg):
    global mqtt_live_state
    global state_changed
    global mutex

    print('Received a message in MQTT')

    while mutex == True:
        sleep(0.1)

    mutex = True 

    state_changed = False

    payload = json.loads(msg.payload.decode())

    if msg.topic == "house/sensors/pir":
        if payload.get("count", 0) >= 3:
            if not mqtt_live_state["door_sensor_active"]:
                mqtt_live_state["door_sensor_active"] = True
                print("\nDoor closed")

    elif msg.topic == "house/sensors/angle":
        if payload.get("angle") != mqtt_live_state["angle_g1_sensor_active"]:
            state_changed = True
        mqtt_live_state["angle_g1_sensor_active"] = payload.get("angle")

    elif msg.topic == "house/sensors/ultrasonic_g2":
        if payload.get("ultasonic_g2") != mqtt_live_state["ultrasonic_g2_sensor_active"]:
            state_changed = True
        mqtt_live_state["ultrasonic_g2_sensor_active"] = payload.get("ultasonic_g2")

    elif msg.topic == "house/sensors/ultrasonic_g3":
        if payload.get("ultrasonic_g3") != mqtt_live_state["ultrasonic_g3_sensor_active"]:
            state_changed = True
        mqtt_live_state["ultrasonic_g3_sensor_active"] = payload.get("ultrasonic_g3")

    elif msg.topic == "house/sensors/scared":
        if payload.get("heartrate") != mqtt_live_state["scaredy_cat_g4_active"]:
            state_changed = True
        mqtt_live_state["scaredy_cat_g4_active"] = payload.get("heartrate")
                
    elif msg.topic == "house/sensors/riddle":
        if payload.get("solved") != mqtt_live_state["riddle_g5_active"]:
            state_changed = True
        mqtt_live_state["riddle_g5_active"] = payload.get("solved")

    elif msg.topic == "house/sensors/light":
        if payload.get("light") != mqtt_live_state["light_g6_sensor_active"]:
            state_changed = True
        mqtt_live_state["light_g6_sensor_active"] = payload.get("light")
    
    elif msg.topic == "house/timers/game_over":
        if payload.get("status") == "expired":
            print("\nTIMEOUTTT")
            client.publish("house/actuators/global/red_led", json.dumps({"power": "ON"}))
            return 
    mutex = False
        

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("house/#")

print("...yea boi...")

t1 = threading.Thread(target=client.loop_forever, daemon=True)
t1.start()


if __name__ == "__main__":
    run()
    sys.exit(0)
