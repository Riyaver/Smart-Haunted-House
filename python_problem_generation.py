import sys
import unified_planning
from unified_planning.shortcuts import *
from unified_planning.io import PDDLReader
from unified_planning.engines import PlanGenerationResultStatus
import json
up.shortcuts.get_environment().credits_stream = None
def generate_problem(mqtt_live_state):
    
    reader = PDDLReader()
    problem = reader.parse_problem("domain.pddl")
    
    game_type = problem.user_type("game")
    sensor_type = problem.user_type("sensor")
    actuator_type = problem.user_type("actuator")
    info_type = problem.user_type("info")
    band_type = problem.user_type("band")
    
    band1 = Object("band1", band_type)
    band2 = Object("band2", band_type)
    band3 = Object("band3", band_type)
    
    game0 = Object("game0", game_type) 
    game1 = Object("game1", game_type)
    game2 = Object("game2", game_type)
    game3 = Object("game3", game_type)
    game4 = Object("game4", game_type)
    game5 = Object("game5", game_type)
    game6 = Object("game6", game_type)
    
    pir = Object("pir_sensor", sensor_type)
    light_sensor = Object("light_sensor", sensor_type)
    angle =  Object("angle_sensor", sensor_type)
    ultrasonic_g2 = Object("ultrasonic_g2_sensor", sensor_type)
    ultrasonic_g3 = Object("ultrasonic_g3_sensor", sensor_type)
    #is_there_scaredy_cat = Object("sc_g4_sensor", sensor_type)

    scaredy_cat_notif = Object("scaredy_cat_act", actuator_type)
    door = Object("door_lock", actuator_type)
    red_led = Object("red_led", actuator_type)
    skeleton = Object("skeleton_drop", actuator_type)
    hand = Object("hand_move", actuator_type)
    false_painting = Object("fale_pain", actuator_type)

    scaredy_cat = Object("scaredy_cat_sense", info_type)
    riddle = Object("riddle_display", actuator_type)
    riddle_timer = Object("riddle_timer_elapsed", info_type)
    exit_timer = Object("exit_timer_elapsed", info_type)
    
    g1_led = Object("game1_led", actuator_type)
    g2_led = Object("game2_led", actuator_type)
    g3_led = Object("game3_led", actuator_type)
    g4_led = Object("game4_led", actuator_type)
    g5_led = Object("game5_led", actuator_type)
    g6_led = Object("game6_led", actuator_type)
    
    
    problem.add_objects([
        band1, game0, game1, game2, game3, game4, game5, game6, band2, band3,
        pir, light_sensor, angle, ultrasonic_g2, ultrasonic_g3, is_there_scaredy_cat, door, red_led, g1_led, g2_led, g5_led, g6_led,
        skeleton, hand, riddle, riddle_timer, exit_timer,false_painting, scaredy_cat, scaredy_cat_notif, g3_led, g4_led
    ])
    

    where_thingy = problem.fluent("where_thingy")
    where_info = problem.fluent("where_info")
    sense_thing = problem.fluent("sense_thing")
    actuate_device = problem.fluent("actuate_device")
    game_0_are_3_ppl_there = problem.fluent("game_0_are_3_ppl_there")
    get_info = problem.fluent("get_info")
    is_complete = problem.fluent("is_complete")
    
    # problem.set_initial_value(where_thingy(pir, game0), True)
    # problem.set_initial_value(where_thingy(door, game0), True)
    
    problem.set_initial_value(where_thingy(angle, game1), True)
    problem.set_initial_value(where_thingy(g1_led, game1), True)
    problem.set_initial_value(where_thingy(skeleton, game1), True)
    
    problem.set_initial_value(where_thingy(ultrasonic_g2, game2), True)
    problem.set_initial_value(where_thingy(g2_led, game2), True)
    problem.set_initial_value(where_thingy(hand, game2), True)
    
    problem.set_initial_value(where_thingy(ultrasonic_g3, game3), True)
    problem.set_initial_value(where_thingy(g3_led, game3), True)
    problem.set_initial_value(where_thingy(false_painting, game3), True)

    problem.set_initial_value(where_thingy(scaredy_cat_notif, game4), True)
    problem.set_initial_value(where_info(scaredy_cat, game4), True)

    problem.set_initial_value(where_thingy(g5_led, game5), True)
    problem.set_initial_value(where_thingy(riddle, game5), True)
    problem.set_initial_value(where_info(riddle_timer, game5), True)
    
    problem.set_initial_value(where_thingy(light_sensor, game6), True)
    problem.set_initial_value(where_thingy(g6_led, game6), True)
    problem.set_initial_value(where_info(exit_timer, game6), True)

    

    # if mqtt_live_state.get("pir_triggered_3_people"):
    #     problem.set_initial_value(game_0_are_3_ppl_there(game0), True)
        
    # if mqtt_live_state.get("door_g0_sensor_active"):
    #     problem.set_initial_value(sense_thing(pir), True)
        
    if mqtt_live_state.get("angle_g1_sensor_active"):
        problem.set_initial_value(sense_thing(angle), True)

    if mqtt_live_state.get("ultrasonic_g2_sensor_active"):
        problem.set_initial_value(sense_thing(ultrasonic_g2), True)

    if mqtt_live_state.get("ultrasonic_g3_sensor_active"):
        problem.set_initial_value(sense_thing(ultrasonic_g3), True)

    if mqtt_live_state.get("scaredy_cat_g4_active"):
        problem.set_initial_value(sense_thing(is_there_scaredy_cat), True)
        
    if mqtt_live_state.get("riddle_g5_active"):
        problem.set_initial_value(get_info(riddle_timer), True)
        
    if mqtt_live_state.get("exit_timeout_reached"):
        problem.set_initial_value(get_info(exit_timer), True)
        
    if mqtt_live_state.get("light_g6_sensor_active"):
        problem.set_initial_value(sense_thing(light_sensor), True)
        
    if mqtt_live_state.get("red_led_active"):
        problem.set_initial_value(actuate_device(red_led), True)

    all_games_complete = And(
        is_complete(game1),
        is_complete(game2),
        is_complete(game5),
        is_complete(game6)
    )
    timeout_reached = actuate_device(red_led)
    
    problem.add_goal(Or(all_games_complete, timeout_reached))
    
    with OneshotPlanner(name='fast-downward') as planner:
        result = planner.solve(problem)
        print(f"[Engine Status]: {result.status.name}")
        
        if result.status in [PlanGenerationResultStatus.SOLVED_SATISFICING, PlanGenerationResultStatus.SOLVED_OPTIMALLY]:
            return result.plan.actions
        else:
            print("Failed to plan")
            return []

if __name__ == "__main__":
    mock_mqtt_live = {
        "pir_triggered_3_people": True,
        "door_sensor_active": True,
        "angle_g1_sensor_active": True,
        "ultrasonic_g3_sensor_active": True,
        "ultrasonic_g2_sensor_active": True,
        "scaredy_cat_g4_active": True,
        "riddle_timeout_reached": True,
        "exit_timeout_reached": True,
        "light_sensor_active": True,
        "red_led_active": False 
    }
    
    actions_sequence = generate_problem(mock_mqtt_live)
    
    print("\nPlan taken: ")
    for action in actions_sequence:
        print(f"Action: {action.action.name} -> Target Parameters: {action.actual_parameters}")