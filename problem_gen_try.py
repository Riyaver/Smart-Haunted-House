import json
import paho.mqtt.client as mqtt
from unified_planning.shortcuts import *
from unified_planning.io import PDDLReader

reader = PDDLReader()
domain = reader.parse_domain('domain.pddl')

Game = domain.type('game')
Device = domain.type('device')


where_thingy = domain.fluent('where_thingy')
game_2_ultrasonic_sensed = domain.fluent('game_2_ultrasonic_sensed')
game_2_did_hand_move = domain.fluent('game_2_did_hand_move')

g2 = Object('game2', Game)
ultrasonic = Object('ultrasonic_sensor', Device)
hand_act = Object('hand_actuator', Device)

sensor_triggered_state = False

def solve_on_the_spot(client):
    problem = Problem('SHH_Fast_Execution', domain)
    problem.add_objects([g2, ultrasonic, hand_act])
    
    problem.set_initial_value(where_thingy(ultrasonic, g2), True)
    problem.set_initial_value(where_thingy(hand_act, g2), True)
    problem.set_initial_value(game_2_did_hand_move(hand_act), False)
    problem.set_initial_value(game_2_ultrasonic_sensed(ultrasonic), sensor_triggered_state)
    
    problem.add_goal(game_2_did_hand_move(hand_act))
    
    with OneshotPlanner(name='fast-downward') as planner:
        result = planner.solve(problem)
        if result.status in PlanGenerationResultStatus.SUCCESSFUL_STATUSES:
            for action_instance in result.plan.actions:
                if action_instance.action.name == "trigger_game_2_hand":
                    client.publish("haunted_house/actuators/game2/hand", json.dumps({"action": "ACTUATE"}))

def on_message(client, userdata, msg):
    global sensor_triggered_state
    payload = json.loads(msg.payload.decode())
    
    if msg.topic == "haunted_house/sensors/game2/ultrasonic":
        new_state = payload.get("triggered", False)
        if new_state != sensor_triggered_state:
            sensor_triggered_state = new_state
            if sensor_triggered_state:
                solve_on_the_spot(client)

client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("haunted_house/sensors/+/+")

print("listeninggg")
client.loop_forever() 