;Header and description

(define (domain SHH_domain)

;remove requirements that are not needed
(:requirements :strips :typing :negative-preconditions :equality :conditional-effects :disjunctive-preconditions)
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

    (is_for_game4 ?d - object)
    (is_for_game5 ?d - object)
    (is_for_game6 ?d - object)


    (actuate_device ?d - actuator)
    (sense_thing ?d - sensor)
    (get_info ?b - info)
    (is_complete ?g - game)
)



(:action game_activate
    :parameters 
        (
            ?led - game_led 
            ?g - game   
        )
    :precondition (
        and
            (door_closed)
            (where_thingy ?led ?g)
    ) 
    :effect (
        and
        (actuate_device ?led)
        (forall (?i - game_led)
            (when (not (= ?i ?led))
                (not (actuate_device ?i))
            )
        )
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
        (not (= ?skeleton ?game1_led))
        ) 
    :effect (
        and
        (actuate_device ?skeleton)
        (is_complete ?g)
      )
    ;:expansion
)

(:action game_4
    :parameters 
        (
            ?g - game
            ?band_notification - actuator
            ?game4_led - game_led
            ?scaredy_cat - info
        )
    :precondition (
        and
        (actuate_device ?game4_led)
        (where_thingy ?game4_led ?g)
        (get_info ?scaredy_cat)
        (where_thingy ?band_notification ?g)
        (is_for_game4 ?g)
        (not (= ?band_notification ?game4_led))
        ) 
    :effect (
        and
        (actuate_device ?band_notification)
        (is_complete ?g)
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
        (where_thingy ?riddle ?g)
        (where_info ?riddle_timer_elapsed ?g)
        (actuate_device ?game5_led)
        (where_thingy ?game5_led ?g)
        (is_for_game5 ?g)
        (get_info ?riddle_timer_elapsed)
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
        (is_for_game6 ?g)
        ) 
    :effect (
        and
        (actuate_device ?game6_led)
        (is_complete ?g)
      )
    ;:expansion
)
)
