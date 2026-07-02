;Header and description

(define (domain SHH_domain)

;remove requirements that are not needed
(:requirements :strips :fluents :durative-actions :timed-initial-literals :typing :conditional-effects :negative-preconditions :duration-inequalities :equality)

(:types 
    game info band device - object
    sensor actuator - device

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


    (actuate_device ?d - actuator)
    (sense_thing ?d - sensor)
    (get_info ?b - info)
    (is_complete ?g - game)

    ;(game_in_progress)
    
    ;(game_0_door_open ?d - game)
    ;(guiding_led ?l - device)
    (game_0_door_closed ?d - device)
    (game_0_sound_boom ?d - device)
    (game_0_light_blink ?d - device)
    (game_0_heartbeat_light_higher ?d - device)
    (game_0_heartbeat_sound_higher ?d - device)
    (game_0_sound_scary ?d - device)
    (game_0_light_scary ?d - device)
    (game_0_are_3_ppl_there ?p - game)
    (game_0_measure_sound_heartbeat ?d - device)
    (game_0_measure_light_heartbeat ?d - device)

    (game_0_measure_heartbeat)

    ;game 1
    (game_1_painting_is_moved ?p - device)
    (game_1_is_skeleton_dropped ?s - device)
    (is_game_1_guiding_led_on ?d)
    
    ;game_2
    (game_2_ultrasonic_sensed ?d - device)
    (game_2_did_hand_move ?d - device)
    (is_game_2_guiding_led_on ?d)

    ;game_3
    (game_3_ultrasonic_sensed ?d - device)
    (game_3_did_false_painting_move ?d - device)
    (is_game_3_guiding_led_on ?d)

    ;game_4
    (game_4_is_there_scaredy_cat ?p  - band)
    (game_4_is_scary_notif_triggered ?d - device)
    (is_game_4_guiding_led_on ?d - device)

    ;game_5
    (game_5_is_riddle_sent ?d - device)
    (is_game_5_guiding_led_on ?d)

    ;game_6
    (game_6_is_ligh_sensor_active ?d - device)
    (game_6_is_exit_led_on  ?d - device)



     ;Goal
    (room_end_door_open) 
)
   

(:functions 
    (ppl_in_the_room ?p - band)
)


; (:action game_0_pir_sense_door_close
;     :parameters 
;         (
;             ?r - game
;             ?ppl - band
;         )
;     :precondition (
;         and
;         ;and(= (ppl_in_the_room ?r) 5)
;         (game_0_are_3_ppl_there ?r)
;         (not (game_0_door_closed))
;         ) 
;     :effect (
;         and
;         (game_0_door_closed)
;         (where_ppl ?ppl ?r)
;         )
;     ;:expansion
; )

; (:action game_0_sound_go_boom
;     :parameters 
;         (
;             ?g - game
;         )
;     :precondition (
;         and
;         (game_0_door_closed)
;         ;(game_0_are_3_ppl_there ?r)
;         ) 
;     :effect (
;         and
;         (game_0_sound_boom ?g)
;         (game_0_measure_sound_heartbeat)
;         )
;     ;:expansion
; )

; (:action game_0_light_go_blink
;     :parameters 
;         (
;             ?r - device
;         )
;     :precondition (
;         and
;         (game_0_door_closed)
;         (game_0_sound_boom ?r)
;         ) 
;     :effect (
;         and
;         (game_0_light_blink ?r)
;         (game_0_measure_light_heartbeat)
;         )
;     ;:expansion
; )

; (:action game_0_sound_scarier_do_again
;     :parameters 
;         (
;             ?r - game
;             ?ppl - band
;         )
;     :precondition (
;         and
;         (game_0_door_closed)
;         (game_0_sound_boom ?r)
;         (game_0_light_blink ?r)
;         (game_0_heartbeat_sound_higher ?r)
;         (not(game_0_heartbeat_light_higher ?r))
;         ) 
;     :effect (
;         game_0_sound_scary ?r
;         )
;     ;:expansion
; )

; (:action game_0_light_scarier_do_again
;     :parameters 
;         (
;             ?r - game
;             ?ppl - band
;         )
;     :precondition (
;         and
;         (game_0_door_closed)
;         (game_0_light_blink ?r)
;         (not(game_0_heartbeat_sound_higher ?r))
;         (game_0_heartbeat_light_higher ?r)
;         ) 
;     :effect (
;         game_0_light_scary ?r
;         )
;     ;:expansion
; )



(:action game_1_activate
    :parameters 
        (
            ?door - sensor
            ?game1_led - actuator
            ?game2_led - actuator
            ?game3_led - actuator
            ?game4_led - actuator
            ?game5_led - actuator
            ?g - game
        )
    :precondition (
        and
            (sense_thing ?door)
            (where_thingy ?door ?g)
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
            ?game1_led - actuator
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
            ?door - sensor
            ?game1_led - actuator
            ?game2_led - actuator
            ?game3_led - actuator
            ?game4_led - actuator
            ?game5_led - actuator
            ?g - game
        )
    :precondition (
        and
            (sense_thing ?door)
            (where_thingy ?door ?g)
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
            ?game2_led - actuator
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
            ?door - sensor
            ?game1_led - actuator
            ?game2_led - actuator
            ?game3_led - actuator
            ?game4_led - actuator
            ?game5_led - actuator
            ?g - game
        )
    :precondition (
           and
            (sense_thing ?door)
            (where_thingy ?door ?g)
            (where_thingy ?game3_led ?g)
        ) 
    :effect (
        and
        (actuate_device ?game3_led)
        (not(actuate_device ?game2_led))
        (not(actuate_device ?game3_led))
        (not(actuate_device ?game4_led))
        (not(actuate_device ?game5_led))
      )
    ;:expansion
)

(:action game_3
    :parameters 
        (
            ?ultrasonic - sensor
            ?game3_led - actuator
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
            ?door - sensor
            ?game1_led - actuator
            ?game2_led - actuator
            ?game3_led - actuator
            ?game4_led - actuator
            ?game5_led - actuator
            ?g - game
        )
    :precondition (
        and
            (sense_thing ?door)
            (where_thingy ?door ?g)
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
        )
    :precondition (
        and
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
            ?door - sensor
            ?game1_led - actuator
            ?game2_led - actuator
            ?game3_led - actuator
            ?game4_led - actuator
            ?game5_led - actuator
            ?g - game
        )
    :precondition (
        and
            (sense_thing ?door)
            (where_thingy ?door ?g)
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
        )
    :precondition (
        and
        (not(actuate_device ?riddle))
        (get_info ?riddle_timer_elapsed)
        (where_thingy ?riddle ?g)
        (where_info ?riddle_timer_elapsed ?g)
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
            ?game6_led - actuator
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