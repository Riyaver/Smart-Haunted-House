import paho.mqtt.client as mqtt
import json
import sys

# Matched to the broker URL inside MainActivity.kt
MQTT_BROKER = "10.110.66.148"
MQTT_PORT = 1883

def run_simulator():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
    try:
        print(f"Connecting to broker at {MQTT_BROKER}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 70)
    except Exception as e:
        print(f"Connection Failed: ({e})")
        sys.exit(1)

    sensor_blueprint = {
        "1": {"topic": "house/sensors/pir", "key": "count", "t_val": 3, "f_val": 0, "name": "PIR (Door Sensor)"},
        "2": {"topic": "house/sensors/angle", "key": "angle", "t_val": True, "f_val": False, "name": "Angle (G1 Painting)"},
        "3": {"topic": "house/sensors/ultrasonic_g2", "key": "ultasonic_g2", "t_val": True, "f_val": False, "name": "Ultrasonic G2 (G2 Hand)"},
        "4": {"topic": "house/sensors/ultrasonic_g3", "key": "ultrasonic_g3", "t_val": True, "f_val": False, "name": "Ultrasonic G3 (G3 Painting)"},
        "5": {"topic": "house/sensors/scared", "key": "heartrate", "t_val": True, "f_val": False, "name": "Scared Cat (Game 4 Targeted Notification)"},
        "6": {"topic": "house/sensors/riddle", "key": "solved", "t_val": True, "f_val": False, "name": "Riddle (G5 Torch)"},
        "7": {"topic": "house/sensors/light", "key": "light", "t_val": True, "f_val": False, "name": "Light (G6 Exit)"},
        "8": {"topic": "house/timers/game_over", "key": "status", "t_val": "expired", "f_val": "running", "name": "Timer"}
    }

    while True:
        print("\nSelect a device to toggle:")
        for selection_key, target in sensor_blueprint.items():
            print(f" [{selection_key}] {target['name']}")
        print(" [q] Exit Simulator")

        choice = input("\nChoose a sensor to mock: ").strip()
        if choice.lower() == 'q':
            client.disconnect()
            break

        if choice in sensor_blueprint:
            target = sensor_blueprint[choice]
            print(f"\nTargeting device: {target['name']}")
            state_input = input("Set target state -> [1] True/Active  [0] False/Inactive: ").strip()

            if state_input in ['1', '0']:
                if choice == "5" and state_input == '1':
                    print("\nSelect which player to scare:")
                    print(" [1] player1")
                    print(" [2] player2")
                    print(" [3] player3")
                    player_choice = input("Select option (Default is 1): ").strip()
                    
                    player_map = {"1": "player1", "2": "player2", "3": "player3"}
                    target_player = player_map.get(player_choice, "player1")
                    
                    payload_dict = {"heartrate": True, "player": target_player}
                elif choice == "5" and state_input == '0':
                    payload_dict = {"heartrate": False, "player": None}
                else:
                    chosen_value = target["t_val"] if state_input == '1' else target["f_val"]
                    payload_dict = {target["key"]: chosen_value}
                
                payload_json = json.dumps(payload_dict)
                client.publish(target["topic"], payload_json)
                print(f"Published -> Topic: '{target['topic']}' | Data: {payload_json}")
        
if __name__ == "__main__":
    run_simulator()