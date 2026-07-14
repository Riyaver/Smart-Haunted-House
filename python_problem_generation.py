import sys
import unified_planning
from unified_planning.shortcuts import *
from unified_planning.io import PDDLReader
from unified_planning.engines import PlanGenerationResultStatus
from unified_planning.model import Fluent
import json

get_environment().credits_stream = None

def generate_problem(mqtt_live_state):

    games = ["game" + str(i+1) for i in range(6)]
    
    reader = PDDLReader()
    problem = reader.parse_problem("domain.pddl")
    
    game_type = problem.user_type("game")
    sensor_type = problem.user_type("sensor")
    actuator_type = problem.user_type("actuator")
    info_type = problem.user_type("info")
    band_type = problem.user_type("band")
    game_led_type = problem.user_type("game_led")
    
    game1 = Object("game1", game_type)
    game2 = Object("game2", game_type)
    game3 = Object("game3", game_type)
    game4 = Object("game4", game_type)
    game5 = Object("game5", game_type)
    game6 = Object("game6", game_type)
    final_timer = Object("final_timer", game_type)
    
    pir = Object("pir_sensor", sensor_type)
    light_sensor = Object("light_sensor", sensor_type)
    angle =  Object("angle_sensor", sensor_type)
    ultrasonic_g2 = Object("ultrasonic_g2_sensor", sensor_type)
    ultrasonic_g3 = Object("ultrasonic_g3_sensor", sensor_type)
    timer_done = Object("timer_over", sensor_type)

    scaredy_cat_notif = Object("scaredy_cat_act", actuator_type)
    door = Object("door_lock", actuator_type)
    red_led = Object("red_led", actuator_type)
    green_led = Object("green_led", actuator_type)
    skeleton = Object("skeleton_drop", actuator_type)
    hand = Object("hand_move", actuator_type)
    false_painting = Object("false_paint", actuator_type)

    scaredy_cat = Object("scaredy_cat_sense", info_type)
    riddle = Object("riddle_display", actuator_type)
    riddle_timer = Object("riddle_timer_elapsed", info_type)
    
    g1_led = Object("game1_led", game_led_type)
    g2_led = Object("game2_led", game_led_type)
    g3_led = Object("game3_led", game_led_type)
    g4_led = Object("game4_led", game_led_type)
    g5_led = Object("game5_led", game_led_type)
    g6_led = Object("game6_led", game_led_type)
    t_led = Object("timer_led", game_led_type)
    
    problem.add_objects([
         game1, game2, game3, game4, game5, game6, final_timer,
        pir, light_sensor, angle, ultrasonic_g2, ultrasonic_g3, timer_done, door, red_led, green_led, g1_led, g2_led, g5_led, g6_led,
        skeleton, hand, riddle, riddle_timer, false_painting, scaredy_cat, scaredy_cat_notif, g3_led, g4_led, t_led
    ])
    
    where_thingy = problem.fluent("where_thingy")
    where_info = problem.fluent("where_info")
    sense_thing = problem.fluent("sense_thing")
    actuate_device = problem.fluent("actuate_device")
    get_info = problem.fluent("get_info")
    is_complete = problem.fluent("is_complete")
    door_closed = problem.fluent("door_closed")
    is_sandbox = problem.fluent("is_sandbox")
    light_locked = problem.fluent("light_locked")

    is_for_game4 = problem.fluent("is_for_game4")
    is_for_game5 = problem.fluent("is_for_game5")

    disable_game = problem.fluent("disable_game")
    
    problem.set_initial_value(is_sandbox(game1), True)
    problem.set_initial_value(is_sandbox(game2), True)
    problem.set_initial_value(is_sandbox(game3), True)
    problem.set_initial_value(is_sandbox(game6), True)
    problem.set_initial_value(is_sandbox(final_timer), True)

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
    problem.set_initial_value(where_thingy(g4_led, game4), True)
    problem.set_initial_value(where_info(scaredy_cat, game4), True)
    problem.set_initial_value(is_for_game4(game4), True)

    problem.set_initial_value(where_thingy(g5_led, game5), True)
    problem.set_initial_value(where_thingy(riddle, game5), True)
    problem.set_initial_value(where_info(riddle_timer, game5), True)
    problem.set_initial_value(is_for_game5(game5), True)
    
    problem.set_initial_value(where_thingy(light_sensor, game6), True)
    problem.set_initial_value(where_thingy(g6_led, game6), True)
    problem.set_initial_value(where_thingy(green_led, game6), True)

    problem.set_initial_value(where_thingy(timer_done, final_timer), True)
    problem.set_initial_value(where_thingy(t_led, final_timer), True)
    problem.set_initial_value(where_thingy(red_led, final_timer), True)

    for completed_room in mqtt_live_state.get("completed_games", []):
        if completed_room == "game1": 
            problem.set_initial_value(is_complete(game1), True)
            problem.set_initial_value(disable_game(game1), True)
        elif completed_room == "game2":
            problem.set_initial_value(is_complete(game2), True)
            problem.set_initial_value(disable_game(game2), True)
        elif completed_room == "game3":
            problem.set_initial_value(is_complete(game3), True)
            problem.set_initial_value(disable_game(game3), True)
        elif completed_room == "game4":
            problem.set_initial_value(is_complete(game4), True)
            problem.set_initial_value(disable_game(game4), True)
        elif completed_room == "game5":
            problem.set_initial_value(is_complete(game5), True)
            problem.set_initial_value(disable_game(game5), True)
        elif completed_room == "game6":
            problem.set_initial_value(is_complete(game6), True)
            problem.set_initial_value(disable_game(game6), True)

    if mqtt_live_state.get("door_sensor_active"):
        problem.set_initial_value(door_closed, True)
        
    if mqtt_live_state.get("angle_g1_sensor_active"):
        problem.set_initial_value(sense_thing(angle), True)

    if mqtt_live_state.get("ultrasonic_g2_sensor_active"):
        problem.set_initial_value(sense_thing(ultrasonic_g2), True)

    if mqtt_live_state.get("ultrasonic_g3_sensor_active"):
        problem.set_initial_value(sense_thing(ultrasonic_g3), True)

    if mqtt_live_state.get("scaredy_cat_g4_active"):
        problem.set_initial_value(get_info(scaredy_cat), True)
        
    if mqtt_live_state.get("riddle_g5_active"):
        problem.set_initial_value(get_info(riddle_timer), True)
        
    if mqtt_live_state.get("light_g6_sensor_active"):
        problem.set_initial_value(sense_thing(light_sensor), True)
    
    if mqtt_live_state.get("game_over"):
        problem.set_initial_value(sense_thing(timer_done), True)
        
    problem.set_initial_value(light_locked, False)
    
    active_led_name = mqtt_live_state.get("active_led_game")
    if active_led_name:
        problem.set_initial_value(light_locked, True)
        if active_led_name == "game1": problem.set_initial_value(actuate_device(g1_led), True)
        elif active_led_name == "game2": problem.set_initial_value(actuate_device(g2_led), True)
        elif active_led_name == "game3": problem.set_initial_value(actuate_device(g3_led), True)
        elif active_led_name == "game4": problem.set_initial_value(actuate_device(g4_led), True)
        elif active_led_name == "game5": problem.set_initial_value(actuate_device(g5_led), True)
        elif active_led_name == "game6": problem.set_initial_value(actuate_device(g6_led), True)

    goal_conditions = []
    completed_list = mqtt_live_state.get("completed_games", [])

    if "game1" not in completed_list: goal_conditions.append(is_complete(game1))
    if "game2" not in completed_list: goal_conditions.append(is_complete(game2))
    if "game3" not in completed_list: goal_conditions.append(is_complete(game3))
    if "game4" not in completed_list: goal_conditions.append(is_complete(game4))
    if "game5" not in completed_list: goal_conditions.append(is_complete(game5))
    if "game6" not in completed_list: goal_conditions.append(is_complete(game6))

    goal_conditions.append(is_complete(final_timer))

    if goal_conditions:
        if len(goal_conditions) > 1:
            problem.add_goal(Or(goal_conditions))
        else:
            problem.add_goal(goal_conditions[0])

    with OneshotPlanner(name='fast-downward') as planner:
        result = planner.solve(problem)
        if result.status in [PlanGenerationResultStatus.SOLVED_SATISFICING, PlanGenerationResultStatus.SOLVED_OPTIMALLY]:
            actions = result.plan.actions
            if len(actions) == 0:
                return [], True, result.status
            return actions, False, result.status
        return [], False, result.status