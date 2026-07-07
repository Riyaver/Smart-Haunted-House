import paho.mqtt.client as mqtt
import json
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

NECESS_GAMES = ["game1", "game2", "game3", "game4"]
ALL_GAMES = ["game1", "game2", "game3", "game4", "game5", "game6"]

def pick_random_guide_light(client):
    global mqtt_live_state
    available_rooms = [r for r in NECESS_GAMES if r not in mqtt_live_state["completed_games"]]
    
    if available_rooms:
        chosen_game = random.choice(available_rooms)
        mqtt_live_state["active_led_game"] = chosen_game
        print(f"Guiding player to: {chosen_game}")
        client.publish(f"house/actuators/{chosen_game}/led", json.dumps({"power": "ON", "device": f"{chosen_game}_led"}))
        for room in ALL_GAMES:
            if room != chosen_game:
                client.publish(f"house/actuators/{room}/led", json.dumps({"power": "OFF"}))
    else:
        if "game5" not in mqtt_live_state["completed_games"]:
            mqtt_live_state["active_led_game"] = "game5"
            print("Riddle unlocked: game5")
            client.publish("house/actuators/game5/led", json.dumps({"power": "ON", "device": "game5_led"}))
        elif "game6" not in mqtt_live_state["completed_games"]:
            mqtt_live_state["active_led_game"] = "game6"
            print("Final Light Sensor: game6")
            client.publish("house/actuators/game6/led", json.dumps({"power": "ON", "device": "game6_led"}))

def on_message(client, userdata, msg):
    global mqtt_live_state
    
    payload = json.loads(msg.payload.decode())
    state_changed = False

    if msg.topic == "house/sensors/pir":
        if payload.get("count", 0) >= 3:
            if not mqtt_live_state["door_sensor_active"]:
                mqtt_live_state["door_sensor_active"] = True
                print("\nDoor closed")
                pick_random_guide_light(client)

    elif msg.topic == "house/sensors/angle":
        if payload.get("angle") == True and not mqtt_live_state["angle_g1_sensor_active"]:
            mqtt_live_state["angle_g1_sensor_active"] = True
            state_changed = True

    elif msg.topic == "house/sensors/ultrasonic_g2":
        if payload.get("ultasonic_g2") == True and not mqtt_live_state["ultrasonic_g2_sensor_active"]:
            mqtt_live_state["ultrasonic_g2_sensor_active"] = True
            state_changed = True

    elif msg.topic == "house/sensors/ultrasonic_g3":
        if payload.get("ultrasonic_g3") == True and not mqtt_live_state["ultrasonic_g3_sensor_active"]:
            mqtt_live_state["ultrasonic_g3_sensor_active"] = True
            state_changed = True

    elif msg.topic == "house/sensors/scared":
        if payload.get("heartrate") == True and not mqtt_live_state["scaredy_cat_g4_active"]:
            mqtt_live_state["scaredy_cat_g4_active"] = True
            state_changed = True
                
    elif msg.topic == "house/sensors/riddle":
        if payload.get("solved") == True and not mqtt_live_state["riddle_g5_active"]:
            mqtt_live_state["riddle_g5_active"] = True
            state_changed = True

    elif msg.topic == "house/sensors/light":
        if payload.get("light") == True and not mqtt_live_state["light_g6_sensor_active"]:
            mqtt_live_state["light_g6_sensor_active"] = True
            state_changed = True
    
    elif msg.topic == "house/timers/game_over":
        if payload.get("status") == "expired":
            print("\nTIMEOUTTT")
            client.publish("house/actuators/global/red_led", json.dumps({"power": "ON"}))
            return 

    if state_changed:
        print(f"\nSensor change detected: {msg.topic}")        
        actions_sequence, goal_achieved = generate_problem(mqtt_live_state)
        
        if goal_achieved:
            print("\nGOAL MET")
            client.disconnect()
            sys.exit(0)
            
        if actions_sequence:
            chosen_action = actions_sequence[0]
            action_name = chosen_action.action.name
            params = chosen_action.actual_parameters
            if action_name.startswith("human_"):
                print(f"Carry on with current game")
                return

            print(f"Next Action: {action_name} -> {params}")
            
            if action_name == "game_activate":
                target_led = str(params[0])
                target_game = str(params[1])
                mqtt_live_state["active_led_game"] = target_game
                client.publish(f"house/actuators/{target_game}/led", json.dumps({"power": "ON", "device": target_led}))
                for room in ALL_GAMES:
                    if room != target_game:
                        client.publish(f"house/actuators/{room}/led", json.dumps({"power": "OFF"}))
                        
            elif action_name in ["game_1", "game_4", "game_5", "solve_physical_sensor_game", "game_6_exit"]:
                if action_name in ["solve_physical_sensor_game", "game_6_exit"]:
                    current_room = str(params[3])
                    target_device = str(params[2])
                else:
                    current_room = str(params[0])
                    target_device = str(params[1])
                
                print(f"🎬 [HARDWARE ACTION AUTHORIZED] Activating device: {target_device} inside {current_room}")
                hardware_payload = {"status": "TRIGGERED", "device_id": target_device, "action": "ACTIVATE"}
                client.publish(f"house/actuators/{current_room}/device", json.dumps(hardware_payload))
                client.publish(f"house/actuators/{current_room}/led", json.dumps({"power": "OFF"}))
                
                mqtt_live_state["completed_games"].append(current_room)
                pick_random_guide_light(client)
                
                _, final_victory_sync = generate_problem(mqtt_live_state)
                if final_victory_sync:
                    print("\nGOAL MET")
                    client.disconnect()
                    sys.exit(0)
        else:
            print("error with states")

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("house/#")

print("...yea boi...")
client.loop_forever()