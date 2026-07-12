(define (domain SHH_domain)

<<<<<<< HEAD
(:requirements :strips :typing :negative-preconditions :equality :conditional-effects :disjunctive-preconditions)
=======
(:requirements :strips :typing :negative-preconditions :equality :conditional-effects :disjunctive-preconditions :universal-preconditions)
>>>>>>> fab95d7a85f7cac19ae50428dc6246872a69326f
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
<<<<<<< HEAD
=======
    (goal) 

    (disable_game ?g - game)
>>>>>>> fab95d7a85f7cac19ae50428dc6246872a69326f
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

<<<<<<< HEAD
(:action human_triggers_any_sensor
    :parameters (?s - sensor ?led - game_led ?g - game)
    :precondition (and
        (door_closed)
        (where_thingy ?s ?g)
        (where_thingy ?led ?g)
        (actuate_device ?led) 
    )
    :effect (and
        (sense_thing ?s)
    )
)

(:action human_triggers_any_info
    :parameters (?i - info ?led - game_led ?g - game)
    :precondition (and
        (door_closed)
        (where_info ?i ?g)
        (where_thingy ?led ?g)
        (actuate_device ?led)
    )
    :effect (and
        (get_info ?i)
    )
)

=======
>>>>>>> fab95d7a85f7cac19ae50428dc6246872a69326f
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
<<<<<<< HEAD
=======
        (not (disable_game ?g))
>>>>>>> fab95d7a85f7cac19ae50428dc6246872a69326f
    ) 
    :effect (and
        (actuate_device ?a)
        (is_complete ?g)
        (not (light_locked)) 
    )
)

(:action game_4
    :parameters (
<<<<<<< HEAD
        ?g - game
        ?band_notification - actuator
        ?game4_led - game_led
        ?scaredy_cat - info
=======
        ?scaredy_cat - info
        ?game4_led - game_led
        ?band_notification - actuator
        ?g - game
>>>>>>> fab95d7a85f7cac19ae50428dc6246872a69326f
    )
    :precondition (and
        (actuate_device ?game4_led)
        (where_thingy ?game4_led ?g)
        (get_info ?scaredy_cat)
        (where_thingy ?band_notification ?g)
        (is_for_game4 ?g)
        (not (= ?band_notification ?game4_led))
<<<<<<< HEAD
=======
        (not (disable_game ?g))
>>>>>>> fab95d7a85f7cac19ae50428dc6246872a69326f
    ) 
    :effect (and
        (actuate_device ?band_notification)
        (is_complete ?g)
        (not (light_locked)) 
    )
)

(:action game_5
    :parameters (
<<<<<<< HEAD
        ?g - game
        ?riddle - actuator
        ?riddle_timer_elapsed - info
        ?game5_led - game_led
=======
        ?riddle_timer_elapsed - info
        ?game5_led - game_led
        ?riddle - actuator
        ?g - game
>>>>>>> fab95d7a85f7cac19ae50428dc6246872a69326f
    )
    :precondition (and
        (not(actuate_device ?riddle))
        (where_thingy ?riddle ?g)
        (where_info ?riddle_timer_elapsed ?g)
        (actuate_device ?game5_led)
        (where_thingy ?game5_led ?g)
        (is_for_game5 ?g)
        (get_info ?riddle_timer_elapsed)
<<<<<<< HEAD
=======
        (not (disable_game ?g))
>>>>>>> fab95d7a85f7cac19ae50428dc6246872a69326f
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
<<<<<<< HEAD
        ?g1 - game
        ?g2 - game
        ?g3 - game
        ?g4 - game
        ?g5 - game
=======
>>>>>>> fab95d7a85f7cac19ae50428dc6246872a69326f
    )
    :precondition (and
        (actuate_device ?led)
        (sense_thing ?s)
        (where_thingy ?s ?g6)
        (where_thingy ?led ?g6)
        (where_thingy ?green_led ?g6)
<<<<<<< HEAD
<<<<<<< HEAD
        (is_complete ?g1)
        (is_complete ?g2)
        (is_complete ?g3)
        (is_complete ?g4)
        (is_complete ?g5)
=======
=======
        (forall (?i - game)
              ( and(not (= ?i ?g6)) (is_complete ?i) ) 
        )
>>>>>>> a2adc22fe857b2e7489c9c0104ec11cfdf2c91e5
        (not (disable_game ?g6))
        
>>>>>>> fab95d7a85f7cac19ae50428dc6246872a69326f
    ) 
    :effect (and
        (actuate_device ?green_led)
        (is_complete ?g6)
        (not (light_locked)) 
    )
<<<<<<< HEAD
=======
)
>>>>>>> fab95d7a85f7cac19ae50428dc6246872a69326f
)
)