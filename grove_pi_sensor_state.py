import time
import json
import grovepi
import paho.mqtt.client as mqtt


MQTT_BROKER = "localhost"
MQTT_PORT = 1883


PIR_PORT = 2 #Digital
ANGLE_SENSOR_PORT = 0 #Analog 
ULTRASONIC_G2_PORT = 4 #Digital 
ULTRASONIC_G3_PORT = 7 #Digital
LIGHT_SENSOR_PORT = 1 #Analog
BUZZER_PORT = 8 

NUMBER_OF_PEOPLE = 3
ANGLE_THRESHOLD = 500
ULTRASONIC_G2_DISTANCE_CM = 30
ULTRASONIC_G3_DISTANCE_CM = 30
LIGHT_THRESHOLD = 600

#pir buzzer 

sensor_state = {
    "door_sensor_active": False,
    "angle_g1_sensor_active": False,
    "ultrasonic_g2_sensor_active": False,
    "ultrasonic_g3_sensor_active": False,
    "light_g6_sensor_active": False
}

pir_people_count = 0
previous_pir_value = 0


client = mqtt.Client()

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()


grovepi.pinMode(PIR_PORT, "INPUT")
grovepi.pinMode(BUZZER_PORT, "OUTPUT")


print("GrovePi sensor publisher started")


while True:

    try:
        # PIR SENSOR
        if not sensor_state["door_sensor_active"]:

            pir_value = grovepi.digitalRead(PIR_PORT)

            if pir_value == 1 and previous_pir_value == 0:
                pir_people_count += 1
                print("People detected:".format({pir_people_count}/{NUMBER_OF_PEOPLE}) )

            previous_pir_value = pir_value

            if pir_people_count >= NUMBER_OF_PEOPLE:

                print("Buzzer ON")
                grovepi.digitalWrite(BUZZER_PORT, 1)

                time.sleep(0.2)

                sensor_state["door_sensor_active"] = True

                client.publish(
                    "house/sensor/door_sensor_active",
                    json.dumps({
                        "state_name": "door_sensor_active",
                        "value": True
                    })
                )

                print("Three people detected")
                print("Door closed")
                print("Game sensors are now active")
                print("Published: door_sensor_active = True")

                print("Buzzer OFF")
                grovepi.digitalWrite(BUZZER_PORT, 0)


        #ALL SENSORS ACTIVE 
        if sensor_state["door_sensor_active"]:

            if not sensor_state["angle_g1_sensor_active"]:

                raw_angle_value = grovepi.analogRead(ANGLE_SENSOR_PORT)

                if raw_angle_value >= ANGLE_THRESHOLD:

                    sensor_state["angle_g1_sensor_active"] = True

                    client.publish(
                        "house/sensor/angle_g1_sensor_active",
                        json.dumps({
                            "state_name":
                                "angle_g1_sensor_active",
                            "value": True
                        })
                    )

                    print("Published: "
                          "angle_g1_sensor_active = True")


            # ULTRASONIC SENSOR GAME 2
            if not sensor_state["ultrasonic_g2_sensor_active"]:

                distance_g2 = grovepi.ultrasonicRead(
                    ULTRASONIC_G2_PORT
                )

                if (0 < distance_g2 <= ULTRASONIC_G2_DISTANCE_CM):

                    sensor_state["ultrasonic_g2_sensor_active"] = True

                    client.publish(
                        "house/sensor/ultrasonic_g2_sensor_active",
                        json.dumps({
                            "state_name":
                                "ultrasonic_g2_sensor_active",
                            "value": True
                        })
                    )

                    print(
                        "Published: "
                        "ultrasonic_g2_sensor_active = True"
                    )


            # ULTRASONIC SENSOR GAME 3
            if not sensor_state["ultrasonic_g3_sensor_active"]:

                distance_g3 = grovepi.ultrasonicRead(
                    ULTRASONIC_G3_PORT
                )

                if (0 < distance_g3 <= ULTRASONIC_G3_DISTANCE_CM):

                    sensor_state["ultrasonic_g3_sensor_active"] = True

                    client.publish(
                        "house/sensor/ultrasonic_g3_sensor_active",
                        json.dumps({
                            "state_name":
                                "ultrasonic_g3_sensor_active",
                            "value": True
                        })
                    )

                    print(
                        "Published: "
                        "ultrasonic_g3_sensor_active = True"
                    )


            # LIGHT SENSOR
            if not sensor_state["light_g6_sensor_active"]:

                raw_light_value = grovepi.analogRead(LIGHT_SENSOR_PORT)

                if raw_light_value <= LIGHT_THRESHOLD:

                    sensor_state[
                        "light_g6_sensor_active"
                    ] = True

                    client.publish(
                        "house/sensor/light_g6_sensor_active",
                        json.dumps({
                            "state_name":
                                "light_g6_sensor_active",
                            "value": True
                        })
                    )

                    print(
                        "Published: "
                        "light_g6_sensor_active = True"
                    )


    except IOError as error:
        print("GrovePi error:".format({error}))

    except Exception as error:
        print("Sensor error: ".format({error}))

    except KeyboardInterrupt:
        print("\nStopping sensor publisher")
        grovepi.digitalWrite(BUZZER_PORT, 0)
        client.loop_stop()
        client.disconnect()
        break

time.sleep(0.5)
