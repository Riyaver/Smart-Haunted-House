import paho.mqtt.client as mqtt
import json
import sys

def run_simulator():
    client = mqtt.Client()
    try:
        client.connect("localhost", 1883, 70)
    except Exception as e:
        print(f"({e})")
        sys.exit(1)

    sensor_blueprint = {
        "1": {"topic": "house/sensors/pir", "key": "count", "t_val": 3, "f_val": 0, "name": "PIR (Door Sensor)"},
        "2": {"topic": "house/sensors/angle", "key": "angle", "t_val": True, "f_val": False, "name": "Angle (G1 Painting)"},
        "3": {"topic": "house/sensors/ultrasonic_g2", "key": "ultasonic_g2", "t_val": True, "f_val": False, "name": "Ultrasonic G2 (G2 Hand)"}, # Matching your 'ultasonic' typo
        "4": {"topic": "house/sensors/ultrasonic_g3", "key": "ultrasonic_g3", "t_val": True, "f_val": False, "name": "Ultrasonic G3 (G3 Painting)"},
        "5": {"topic": "house/sensors/scared", "key": "heartrate", "t_val": True, "f_val": False, "name": "Scared shd be chnaged"},
        "6": {"topic": "house/sensors/riddle", "key": "solved", "t_val": True, "f_val": False, "name": "Riddle (G5 Torch)"},
        "7": {"topic": "house/sensors/light", "key": "light", "t_val": True, "f_val": False, "name": "Light (G6 Exit)"},
        "8": {"topic": "house/timers/game_over", "key": "status", "t_val": "expired", "f_val": "running", "name": "Timer"}
    }

    while True:
        print("\nSelect a device to toggle:")
        for selection_key, target in sensor_blueprint.items():
            print(f" [{selection_key}] {target['name']}")
        print(" [q] Exit Simulator")

        choice = input("choose the sensorrrrrr").strip()
        if choice.lower() == 'q':
            client.disconnect()
            break

        if choice in sensor_blueprint:
            target = sensor_blueprint[choice]
            print(f"\nTargeting device: {target['name']}")
            state_input = input("Set target state -> [1] True  [0] False: ").strip()

            if state_input in ['1', '0']:
                chosen_value = target["t_val"] if state_input == '1' else target["f_val"]
                
                payload_dict = {target["key"]: chosen_value}
                payload_json = json.dumps(payload_dict)

                client.publish(target["topic"], payload_json)
                print(f"Published -> Topic: '{target['topic']}' | Data: {payload_json}")
        
if __name__ == "__main__":
    run_simulator()

    