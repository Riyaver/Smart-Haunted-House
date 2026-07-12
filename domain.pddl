(define (domain SHH_domain)

(:requirements :strips :typing :negative-preconditions :equality :conditional-effects :disjunctive-preconditions :universal-preconditions)
(:types 
    game info band device - object
    sensor actuator - device
    game_led - actuator
)

(:constants )

(:predicates 
    (where_info ?b - info ?place - game)
    (where_thingy ?t - device ?place - game)
    (door_closed)
    (is_sandbox ?g - game)
    (is_for_game4 ?d - object)
    (is_for_game5 ?d - object)
    (actuate_device ?d - actuator)
    (sense_thing ?d - sensor)
    (get_info ?b - info)
    (is_complete ?g - game)
    (light_locked) 
    (goal) 

    (disable_game ?g - game)
)

(:action game_activate
    :parameters (
        ?led - game_led 
        ?g - game   
    )
    :precondition (and
        (door_closed)
        (where_thingy ?led ?g)
        (not (light_locked)) 
        (not (is_complete ?g))
    ) 
    :effect (and
        (actuate_device ?led)
        (light_locked) 
        (forall (?i - game_led)
            (when (not (= ?i ?led))
                (not (actuate_device ?i))
            )
        )
    )
)

(:action solve_physical_sensor_game
    :parameters (
        ?s - sensor
        ?led - game_led
        ?a - actuator
        ?g - game
    )
    :precondition (and
        (is_sandbox ?g) 
        (actuate_device ?led)
        (sense_thing ?s)
        (where_thingy ?s ?g)
        (where_thingy ?a ?g)
        (where_thingy ?led ?g)
        (not (= ?a ?led))
        (not (disable_game ?g))
    ) 
    :effect (and
        (actuate_device ?a)
        (is_complete ?g)
        (not (light_locked)) 
    )
)

(:action game_4
    :parameters (
        ?scaredy_cat - info
        ?game4_led - game_led
        ?band_notification - actuator
        ?g - game
    )
    :precondition (and
        (actuate_device ?game4_led)
        (where_thingy ?game4_led ?g)
        (get_info ?scaredy_cat)
        (where_thingy ?band_notification ?g)
        (is_for_game4 ?g)
        (not (= ?band_notification ?game4_led))
        (not (disable_game ?g))
    ) 
    :effect (and
        (actuate_device ?band_notification)
        (is_complete ?g)
        (not (light_locked)) 
    )
)

(:action game_5
    :parameters (
        ?riddle_timer_elapsed - info
        ?game5_led - game_led
        ?riddle - actuator
        ?g - game
    )
    :precondition (and
        (not(actuate_device ?riddle))
        (where_thingy ?riddle ?g)
        (where_info ?riddle_timer_elapsed ?g)
        (actuate_device ?game5_led)
        (where_thingy ?game5_led ?g)
        (is_for_game5 ?g)
        (get_info ?riddle_timer_elapsed)
        (not (disable_game ?g))
    ) 
    :effect (and
        (actuate_device ?riddle)
        (is_complete ?g)
        (not (light_locked))
    )
)

(:action game_6_exit
    :parameters (
        ?s - sensor
        ?led - game_led
        ?green_led - actuator
        ?g6 - game
    )
    :precondition (and
        (actuate_device ?led)
        (sense_thing ?s)
        (where_thingy ?s ?g6)
        (where_thingy ?led ?g6)
        (where_thingy ?green_led ?g6)
        (not (disable_game ?g6))
        
    ) 
    :effect (and
        (actuate_device ?green_led)
        (is_complete ?g6)
        (not (light_locked)) 
    )
)
)
