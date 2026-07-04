;Header and description

(define (domain SHH_domain)

;remove requirements that are not needed
(:requirements :strips :typing :negative-preconditions :equality :conditional-effects)
(:types 
    game info band device - object
    sensor actuator - device
    game_led - actuator

)

;un-comment following line if constants are needed
(:constants )


(:predicates 
    (where_info ?b - info ?place - game)
    (where_thingy ?t - device ?place - game)

    ;game 0 -> Door close when 3 ppl enter
    ;game 1 -> Painting angle tilt 
    ;game 2 -> hand moving forward
    ;game 3 -> False painting
    ;game 4 -> Scaredy cat notif
    ;game 5 -> Riddle for torch;
    ;game 6 -> light shone at light sensor

    (door_closed)


    (actuate_device ?d - actuator)
    (sense_thing ?d - sensor)
    (get_info ?b - info)
    (is_complete ?g - game)
)

(:action game_1_activate
    :parameters 
        (
            ?game1_led - game_led
            ?game2_led - game_led
            ?game3_led - game_led
            ?game4_led - game_led
            ?game5_led - game_led
            ?g - game
        )
    :precondition (
        and
            (door_closed)
            (where_thingy ?game1_led ?g)
        ) 
    :effect (
        and
        (actuate_device ?game1_led)
        (not(actuate_device ?game2_led))
        (not(actuate_device ?game3_led))
        (not(actuate_device ?game4_led))
        (not(actuate_device ?game5_led))
      )
    ;:expansion
)

(:action game_1
    :parameters 
        (
            ?painting - sensor
            ?game1_led - game_led
            ?skeleton - actuator
            ?g - game
        )
    :precondition (
        and
        (actuate_device ?game1_led)
        (sense_thing ?painting)
        (where_thingy ?painting ?g)
        (where_thingy ?skeleton ?g)
        (where_thingy ?game1_led ?g)
        ) 
    :effect (
        and
        (actuate_device ?skeleton)
        (is_complete ?g)
      )
    ;:expansion
)

(:action game_2_activate
    :parameters 
        (
            ?game1_led - game_led
            ?game2_led - game_led
            ?game3_led - game_led
            ?game4_led - game_led
            ?game5_led - game_led
            ?g - game
        )
    :precondition (
        and
            (door_closed)
            (where_thingy ?game2_led ?g)
        ) 
    :effect (
        and
        (actuate_device ?game2_led)
        (not(actuate_device ?game1_led))
        (not(actuate_device ?game3_led))
        (not(actuate_device ?game4_led))
        (not(actuate_device ?game5_led))
      )
    ;:expansion
)


(:action game_2
    :parameters 
        (
            ?ultrasonic - sensor
            ?game2_led - game_led
            ?hand - actuator
            ?g - game
        )
    :precondition (
        and
        (sense_thing ?ultrasonic)
        (actuate_device ?game2_led)
        (where_thingy ?ultrasonic ?g)
        (where_thingy ?game2_led ?g)
        (where_thingy ?hand ?g)
        ) 
    :effect (
        and
        (actuate_device ?hand)
        (is_complete ?g)
      )
    ;:expansion
)

(:action game_3_activate
    :parameters 
        (
            ?game1_led - game_led
            ?game2_led - game_led
            ?game3_led - game_led
            ?game4_led - game_led
            ?game5_led - game_led
            ?g - game
        )
    :precondition (
           and
            (door_closed)
            (where_thingy ?game3_led ?g)
        ) 
    :effect (
        and
        (actuate_device ?game3_led)
        (not(actuate_device ?game2_led))
        (not(actuate_device ?game1_led))
        (not(actuate_device ?game4_led))
        (not(actuate_device ?game5_led))
      )
    ;:expansion
)

(:action game_3
    :parameters 
        (
            ?ultrasonic - sensor
            ?game3_led - game_led
            ?false_painting - actuator
            ?g - game
        )
    :precondition (
        and
        (sense_thing ?ultrasonic)
        (actuate_device ?game3_led)
        (where_thingy ?ultrasonic ?g)
        (where_thingy ?game3_led ?g)
        (where_thingy ?false_painting ?g)
        ) 
    :effect (
        and
        (actuate_device ?false_painting)
        (is_complete ?g)
      )
    ;:expansion
)

(:action game_4_activate
    :parameters 
        (
            ?game1_led - game_led
            ?game2_led - game_led
            ?game3_led - game_led
            ?game4_led - game_led
            ?game5_led - game_led
            ?g - game
        )
    :precondition (
        and
            (door_closed)
            (where_thingy ?game4_led ?g)
        ) 
    :effect (
        and
        (actuate_device ?game4_led)
        (not(actuate_device ?game2_led))
        (not(actuate_device ?game3_led))
        (not(actuate_device ?game1_led))
        (not(actuate_device ?game5_led))
      )
    ;:expansion
)

(:action game_4
    :parameters 
        (
            ?g - game
            ?band_notification - actuator
            ?is_there_scaredy_cat - info
            ?game4_led - game_led
        )
    :precondition (
        and
        (actuate_device ?game4_led)
        (where_thingy ?game4_led ?g)
        (get_info ?is_there_scaredy_cat)
        (where_thingy ?band_notification ?g)
        (where_info ?is_there_scaredy_cat ?g)
        ) 
    :effect (
        and
        (actuate_device ?band_notification)
        (is_complete ?g)
      )
    ;:expansion
)

(:action game_5_activate
    :parameters 
        (
            ?game1_led - game_led
            ?game2_led - game_led
            ?game3_led - game_led
            ?game4_led - game_led
            ?game5_led - game_led
            ?g - game
        )
    :precondition (
        and
            (door_closed)
            (where_thingy ?game5_led ?g)
        ) 
    :effect (
        and
        (actuate_device ?game5_led)
        (not(actuate_device ?game2_led))
        (not(actuate_device ?game3_led))
        (not(actuate_device ?game1_led))
        (not(actuate_device ?game4_led))
      )
    ;:expansion
)

(:action game_5
    :parameters 
        (
            ?g - game
            ?riddle - actuator
            ?riddle_timer_elapsed - info
            ?game5_led - game_led
        )
    :precondition (
        and
        (not(actuate_device ?riddle))
        (get_info ?riddle_timer_elapsed)
        (where_thingy ?riddle ?g)
        (where_info ?riddle_timer_elapsed ?g)
        (actuate_device ?game5_led)
        (where_thingy ?game5_led ?g)
        ) 
    :effect (
        and
        (actuate_device ?riddle)
        (is_complete ?g)
      )
    ;:expansion
)

(:action game_6
    :parameters 
        (
            ?g - game
            ?light_sensor - sensor
            ?game6_led - game_led
            ?exit_timer_elapsed - info
        )
    :precondition (
        and
        (not(actuate_device ?game6_led))
        (sense_thing ?light_sensor)
        (get_info ?exit_timer_elapsed)
        (where_thingy ?light_sensor ?g)
        (where_info ?exit_timer_elapsed ?g)
        (where_thingy ?game6_led ?g)
        ) 
    :effect (
        and
        (actuate_device ?game6_led)
        (is_complete ?g)
      )
    ;:expansion
)
)
