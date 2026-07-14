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
    "highest_scared_player": None,
    "riddle_g5_active": False,
    "light_g6_sensor_active": False,
    "active_led_game": None,       
    "completed_games": []         
}

mutex = False
state_changed = False
total_game_seconds = 300  

def game_countdown_timer():
    """Maintains room entry timelines so mobile clocks stay synchronized."""
    global total_game_seconds, state_changed, mutex
    while not mqtt_live_state["door_sensor_active"]:
        sleep(0.5)
        
    print("[CLOCK] Match started! Ticking down 5-minute room matrix.")
    while total_game_seconds > 0:
        sleep(1)
        total_game_seconds -= 1
        client.publish("house/timers/timer_sync", str(total_game_seconds))

    print("[CLOCK] Match time expired!")
    client.publish("house/timers/game_over", json.dumps({"status": "expired"}))


def run():
    global mutex
    global state_changed
    while True:
        if mutex == False:
            mutex = True
            if state_changed == True:
                state_changed = False
                print('\n======================================================================')
                print('Detected a state change. Generating a new problem based on current state')
                print(f'Current State   : {mqtt_live_state}')
                print(f'Completed Games : {mqtt_live_state["completed_games"]}')
                print('======================================================================')
                
                actions_sequence, goal_achieved, status = generate_problem(mqtt_live_state)
                
                if actions_sequence:
                    print(f"Generated Sequence: {actions_sequence}")
                    for chosen_action in actions_sequence:
                        action_name = chosen_action.action.name
                        params = chosen_action.actual_parameters
                        if action_name.startswith("human_"):
                            print(f"Carry on with current game")
                            continue
                        
                        elif action_name == "game_activate":
                            target_game = str(params[1])
                            print(f"[AI PLANNER EXECUTION] Automatically launching: {target_game}")
                            
                            if target_game == "game5":
                                print("[PLANNER EFFECT] Game 5 Riddle is active. Sending message to all users.")
                                text_payload = "RIDDLE: What has keys but opens no locks? Enter solution to proceed."
                                for player in ["player1", "player2", "player3"]:
                                    client.publish(f"house/players/{player}/notifications", text_payload)
                                    
                            mqtt_live_state["active_led_game"] = target_game
                            state_changed = True
                            break

                        elif action_name in ["solve_physical_sensor_game", "game_5", "game_4"]:
                            current_room = str(params[3])
                            target_device = str(params[2])
                            
                            if action_name == "game_4":
                                target_player = mqtt_live_state.get("highest_scared_player", "player1")
                                print(f"[ACTION AUTHORIZED] Firing targeted jump scare output for: {target_player}")
                                client.publish("house/actuators/game4/target", json.dumps({"player": target_player}))
                                print(f"[ACTION EXECUTED] Sending push notification output to: {target_player}")

                            if current_room == "game_5":
                                print("riddle sent")
                                riddle_payload = "idk bro"
                                for player in ["player1", "player2", "player3"]:
                                    client.publish(f"house/players/{player}/notifications", riddle_payload)
                                sleep(0.5)

                            if current_room == "game6":
                                print("[VICTORY] Game 6 completed! Broadcasting final escape text to all phones.")
                                victory_payload = "CONGRATULATIONS! THE SYSTEM IS UNLOCKED. YOU ESCAPED!"
                                for player in ["player1", "player2", "player3"]:
                                    client.publish(f"house/players/{player}/notifications", victory_payload)
                                sleep(0.5)

                            print(f"[HARDWARE ACTION AUTHORIZED] Activating device: {target_device} inside {current_room}")
                            hardware_payload = {"status": "TRIGGERED", "device_id": target_device, "action": "ACTIVATE"}
                            client.publish(f"house/actuators/{current_room}/device", json.dumps(hardware_payload))
                            client.publish(f"house/actuators/{current_room}/led", json.dumps({"power": "OFF"}))

                            mqtt_live_state["active_led_game"] = None
                            mqtt_live_state["completed_games"].append(current_room)    
                            state_changed = True
                            
                            # Automatically sets the Riddle puzzle active right when games 1-4 finish
                            if all(g in mqtt_live_state["completed_games"] for g in ["game1", "game2", "game3", "game4"]):
                                if not mqtt_live_state["riddle_g5_active"] and "game5" not in mqtt_live_state["completed_games"]:
                                    print("[CLOCK MONITOR] Games 1-4 completed successfully. Automatically activating Game 5 Riddle!")
                                    mqtt_live_state["riddle_g5_active"] = True
                else:
                    print("No planning possible")
                    print(status)

                if len(mqtt_live_state["completed_games"]) >= 6:
                    print('\nGG - All Goals Cleared! Closing Planning Environment.')
                    client.disconnect()
                    sys.exit(0)
                
            mutex = False
            
        sleep(0.05)


def on_message(client, userdata, msg):
    global mqtt_live_state
    global state_changed
    global mutex

    while mutex == True:
        sleep(0.1)

    mutex = True 
    state_changed = False

    try:
        payload = json.loads(msg.payload.decode())
    except Exception:
        mutex = False
        return

    if msg.topic == "house/sensors/pir":
        if payload.get("count", 0) >= 3:
            if not mqtt_live_state["door_sensor_active"]:
                mqtt_live_state["door_sensor_active"] = True
                state_changed = True
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
        is_scared = payload.get("heartrate", False)
        target_player = payload.get("player")
        if is_scared != mqtt_live_state["scaredy_cat_g4_active"]:
            state_changed = True
        mqtt_live_state["scaredy_cat_g4_active"] = is_scared
        mqtt_live_state["highest_scared_player"] = target_player
                
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
            mutex = False
            return 
    mutex = False
        

try:
    from paho.mqtt.enums import CallbackAPIVersion
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION1)
except (ImportError, AttributeError, TypeError):
    client = mqtt.Client()

client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("house/#")

print("...yea boi...")

t1 = threading.Thread(target=client.loop_forever, daemon=True)
t1.start()

t2 = threading.Thread(target=game_countdown_timer, daemon=True)
t2.start()

if __name__ == "__main__":
    run()
    sys.exit(0)