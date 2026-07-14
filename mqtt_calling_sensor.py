import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion  # Added to fix deprecation warning
import json
import threading
import queue
import time
from time import sleep
import sys
from python_problem_generation import generate_problem
from unified_planning.engines import PlanGenerationResultStatus  # FIX: Added missing import

mqtt_live_state = {
    "door_sensor_active": False,
    "remaining_time": 300,
    "angle_g1_sensor_active": False,
    "ultrasonic_g2_sensor_active": False,
    "ultrasonic_g3_sensor_active": False,
    "scaredy_cat_g4_active": False,
    "highest_scared_player": "player1",
    "riddle_g5_active": False,
    "light_g6_sensor_active": False,
    "active_led_game": None,       
    "completed_games": []         
}

message_queue = queue.Queue()

NECESS_GAMES = ["game1", "game2", "game3", "game4"]
ALL_GAMES = ["game1", "game2", "game3", "game4", "game5", "game6"]

def timer_countdown_worker(mqtt_client):
    global mqtt_live_state
    remaining = 300  # 5-minute initial pool
    g5_triggered = False
    
    print("[TIMER] Countdown thread initialized.")
    while remaining > 0:
        # Halt counting immediately if victory condition is satisfied
        if len(mqtt_live_state["completed_games"]) >= 6:
            break
            
        # 1. Sync the Android UI: Publish remaining seconds as a raw payload string
        mqtt_client.publish("house/timers/timer_sync", str(remaining))
        mqtt_live_state["remaining_time"] = remaining
        
        # 2. Trigger Game 5: Inject virtual activation if we cross the 60-second mark
        if remaining <= 60 and not g5_triggered:
            g5_triggered = True
            print("\n[TIMER] 1 minute remaining! Queueing virtual Game 5 activation.")
            message_queue.put(("house/timers/virtual_g5", {"trigger": True}))
            
        time.sleep(1)
        remaining -= 1
        
    # 3. Handle timeout depletion if games aren't finished
    if remaining == 0 and len(mqtt_live_state["completed_games"]) < 6:
        print("\n[TIMER] Time has expired! Injecting game over message.")
        message_queue.put(("house/timers/game_over", {"status": "expired"}))

def run():
    global mqtt_live_state
    print("Processing worker loop is online and running.")
    
    while True:
        try:
            # Safely fetch item from queue without spinning the CPU or blocking the thread indefinitely
            topic, payload = message_queue.get(timeout=0.1)
        except queue.Empty:
            continue

        state_changed = False

        if topic == "house/sensors/pir":
            if payload.get("count", 0) >= 3:
                if not mqtt_live_state["door_sensor_active"]:
                    mqtt_live_state["door_sensor_active"] = True
                    state_changed = True
                    print("\nDoor closed and timer starts")
                    threading.Thread(
                            target=timer_countdown_worker, 
                            args=(client,), 
                            daemon=True
                        ).start()

        elif topic == "house/sensors/angle":
            if payload.get("angle") != mqtt_live_state["angle_g1_sensor_active"]:
                state_changed = True
            mqtt_live_state["angle_g1_sensor_active"] = payload.get("angle")

        elif topic == "house/sensors/ultrasonic_g2":
            if payload.get("ultasonic_g2") != mqtt_live_state["ultrasonic_g2_sensor_active"]:
                state_changed = True
            mqtt_live_state["ultrasonic_g2_sensor_active"] = payload.get("ultasonic_g2")

        elif topic == "house/sensors/ultrasonic_g3":
            if payload.get("ultrasonic_g3") != mqtt_live_state["ultrasonic_g3_sensor_active"]:
                state_changed = True
            mqtt_live_state["ultrasonic_g3_sensor_active"] = payload.get("ultrasonic_g3")

        elif topic == "house/sensors/scared":
            is_scared = payload.get("heartrate", False)
            target_player = payload.get("player", "player1")
            if (is_scared != mqtt_live_state["scaredy_cat_g4_active"]) or (is_scared and target_player != mqtt_live_state.get("highest_scared_player")):
                state_changed = True
            mqtt_live_state["scaredy_cat_g4_active"] = is_scared
            mqtt_live_state["highest_scared_player"] = target_player
                    
        elif topic == "house/sensors/riddle":
            if payload.get("solved") != mqtt_live_state["riddle_g5_active"]:
                state_changed = True
            mqtt_live_state["riddle_g5_active"] = payload.get("solved")

        elif topic == "house/sensors/light":
            if payload.get("light") != mqtt_live_state["light_g6_sensor_active"]:
                state_changed = True
            mqtt_live_state["light_g6_sensor_active"] = payload.get("light")

        elif topic == "house/timers/virtual_g5":
                if payload.get("trigger") and not mqtt_live_state["riddle_g5_active"]:
                    mqtt_live_state["riddle_g5_active"] = True
                    state_changed = True
                    print("\n[TRIGGER] Game 5 Riddle activated!")
        
        elif topic == "house/timers/game_over":
            if payload.get("status") == "expired":
                print("\nTIMEOUTTT")
                client.publish("house/actuators/global/red_led", json.dumps({"power": "ON"}))
                return 

        if state_changed:
            print('Detected a state change. Generating a new problem based on current state')
            print(f"Current State: {mqtt_live_state}")
            actions_sequence, goal_achieved, status = generate_problem(mqtt_live_state)
            
            if actions_sequence:
                print(f"Generated Actions Sequence: {actions_sequence}")
                for chosen_action in actions_sequence:
                    action_name = chosen_action.action.name
                    params = chosen_action.actual_parameters
                    
                    if action_name.startswith("human_"):
                        print(f"Carry on with current game")
                        continue
                    
                    elif action_name in ["solve_physical_sensor_game", "game_5", "game_4", "game_6_exit"]:
                        current_room = str(params[3])
                        target_device = str(params[2])
                        
                        if action_name == "game_4":
                            target_player = mqtt_live_state.get("highest_scared_player", "player1")
                            print(f"[ACTION AUTHORIZED] Scary message to: {target_player}")
                            client.publish("house/actuators/game4/target", json.dumps({"player": target_player}))

                        if action_name == "game_5":
                            print("riddle sent")
                            riddle_payload = "idk bro"
                            for player in ["player1", "player2", "player3"]:
                                client.publish(f"house/players/{player}/notifications", riddle_payload)
                            sleep(0.5)

                        if current_room == "game6":
                            print("[VICTORY] Game 6 completed! Broadcasting final escape text to all plauers.")
                            victory_payload = "CONGRATULATIONS! YOU ESCAPED!"
                            for player in ["player1", "player2", "player3"]:
                                client.publish(f"house/players/{player}/notifications", victory_payload)
                            sleep(0.5)
                            
                        print(f"[HARDWARE ACTION AUTHORIZED] Activating device: {target_device} inside {current_room}")
                        hardware_payload = {"status": "TRIGGERED", "device_id": target_device, "action": "ACTIVATE"}
                        client.publish(f"house/actuators/{current_room}/device", json.dumps(hardware_payload))
                        client.publish(f"house/actuators/{current_room}/led", json.dumps({"power": "OFF"}))

                        if current_room not in mqtt_live_state["completed_games"]:
                            mqtt_live_state["completed_games"].append(current_room)  
                            if not mqtt_live_state["riddle_g5_active"]:
                                prev_games_solved = all(g in mqtt_live_state["completed_games"] for g in ["game1", "game2", "game3", "game4"])
                                if prev_games_solved:
                                    print("\n[TRIGGER] Games 1-4 completed! Queueing virtual Game 5 activation.")
                                    message_queue.put(("house/timers/virtual_g5", {"trigger": True}))  
            else:
                # Safely intercept the correct enum statuses from the unified planning engine
                if status in [PlanGenerationResultStatus.UNSOLVABLE_INCOMPLETELY, PlanGenerationResultStatus.UNSOLVABLE_PROVEN]:
                    print("[STATUS] System active and secure. Waiting for players to interact with a game sensor...")
                else:
                    print("No planning possible due to a domain/problem configuration error:")
                    print(status)

            if len(mqtt_live_state["completed_games"]) >= 6:
                print('GG')
                return

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        message_queue.put((msg.topic, payload))
    except Exception as e:
        try:
            raw_val = msg.payload.decode()
            message_queue.put((msg.topic, {"value": raw_val}))
        except Exception as inner_e:
            print(f"Error parsing incoming payload data: {inner_e}")

# FIX: Swapped to VERSION2 interface to eliminate warning logs
client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("house/#")

print("...yea boi...")

t1 = threading.Thread(target=client.loop_forever, daemon=True)
t1.start()

if __name__ == "__main__":
    run()
    sys.exit(0)