import time
import json
import paho.mqtt.client as mqtt

import threading

import grovepi
from grove_rgb_lcd import *

MQTT_PORT = 8883
MQTT_BROKER = "157cc16c2b0443d0931cfacc745a094f.s1.eu.hivemq.cloud"
MQTT_USER = "SHH"
MQTT_PASSWORD = "grp16_shh"

PIR_PORT = 8 #Digital
ANGLE_SENSOR_PORT = 0 #Analog
ULTRASONIC_G2_PORT = 4 #Digital
LIGHT_SENSOR_PORT = 1 #Analog
BUZZER_PORT = 2
BUTTON_PORT= 3

NUMBER_OF_PEOPLE = 3
ANGLE_THRESHOLD = 500
ULTRASONIC_G2_DISTANCE_CM = 2
LIGHT_THRESHOLD = 600

RED_LED_PORT = 7
GREEN_LED_PORT = 5

grovepi.pinMode(RED_LED_PORT, "OUTPUT")
grovepi.pinMode(GREEN_LED_PORT, "OUTPUT")
grovepi.pinMode(BUTTON_PORT, "INPUT")
grovepi.pinMode(PIR_PORT, "INPUT")
grovepi.pinMode(BUZZER_PORT, "OUTPUT")

sensor_state = {
    "door_sensor_active": False,
    "angle_g1_sensor_active": False,
    "ultrasonic_g2_sensor_active": False,
    "ultrasonic_g3_sensor_active": False,
    "light_g6_sensor_active": False
}

pir_people_count = 0
previous_pir_value = 0

lefteye = [0b00100,
	0b00010,
	0b01000,
	0b01100,
	0b01110,
	0b01110,
	0b01110,
	0b00000]

righteye = [0b00100,
	0b01000,
	0b00010,
	0b00110,
	0b01110,
	0b01110,
	0b01110,
	0b00000]

eye = [0b00000,
	0b01110,
	0b01110,
	0b01110,
	0b01110,
	0b01110,
	0b01110,
	0b00000]

line = [0b00000,
	0b00000,
	0b00000,
	0b11111,
	0b00000,
	0b00000,
	0b00000,
	0b00000]

left_smile = [0b01000,
	0b00100,
	0b00010,
	0b00001,
	0b00000,
	0b00000,
	0b00000,
	0b00000]

right_smile = [0b00010,
	0b00100,
	0b01000,
	0b10000,
	0b00000,
	0b00000,
	0b00000,
	0b00000]

fang = [0b00000,
	0b00000,
	0b00000,
	0b11111,
	0b01110,
	0b00100,
	0b00000,
	0b00000]

def set_lcd_mad():
    setRGB(255,0,0)
    #setText('       ' + chr(0) + chr(0) + '\n' +'      '  + chr(1) + chr(1) + chr(1) + chr(1) )
    #sleep(0.5)
    setText('       ' + chr(5) + chr(6) + '\n' +'      '  + chr(2) + chr(4) + chr(4) + chr(3) )

def set_lcd_happy():
    setRGB(0,255,0)
    setText('       ' + chr(0) + chr(0) + '\n' +'      ' + chr(2) + chr(1) + chr(1) + chr(3) )

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))

        print("\n[MQTT] Topic:", msg.topic)
        print("[MQTT] Payload:", msg.payload)

        status = payload.get("status")
        target_device = payload.get("device_id")
        action = payload.get("action")

        print(status,target_device,action)

        if status != "TRIGGERED":
            print(
               "[MQTT] Ignoring message with status: "
               .format({status}))
            return

        if action != "ACTIVATE":
            print(
               "[MQTT] Ignoring unsupported action: "
               .format({action})
            )
            return

        if target_device is None:
            print("[MQTT ERROR] device_id is missing")
            return

        # Extract current room from:
        # house/actuators/game1/device
        topic_parts = msg.topic.split("/")
        print(topic_parts)

        if len(topic_parts) != 4:
            print("[MQTT ERROR] Invalid topic: ", msg.topic)
            return

        current_room = topic_parts[2]

        print(
           "[ACTUATOR] Activating {target_device} inside", current_room)

        if target_device == "red_led":

            grovepi.digitalWrite(RED_LED_PORT,1)

            time.sleep(0.5)

            print("[ACTUATOR] Red LED ON")

        elif target_device == "green_led":

            grovepi.digitalWrite(GREEN_LED_PORT,1)

            time.sleep(0.5)

            print("[ACTUATOR] Green LED ON")

        elif target_device in ["skeleton_drop"]:

            print("[ACTUATOR] Dropping skeleton")

            #client.publish()

            #grovepi.servoWrite(SKELETON_SERVO_PORT,SKELETON_DROP_ANGLE)

            time.sleep(1)

            print("[ACTUATOR] Skeleton dropped")

        elif target_device in ["hand","hand_move"]:

            print("[ACTUATOR] Moving hand")

            #grovepi.servoWrite(HAND_SERVO_PORT,HAND_MOVE_ANGLE)

            time.sleep(0.5)

            #grovepi.servoWrite(HAND_SERVO_PORT,HAND_INITIAL_ANGLE)

            time.sleep(0.5)

            #grovepi.servoWrite(HAND_SERVO_PORT,HAND_MOVE_ANGLE)

            time.sleep(0.5)

            #grovepi.servoWrite(HAND_SERVO_PORT,HAND_INITIAL_ANGLE)

            print("[ACTUATOR] Hand movement completed")

        elif target_device in ["false_paint","false_painting"]:

            print("[ACTUATOR] Opening false painting")

            time.sleep(1)

            set_lcd_mad()


        else:
            print(
               "[ACTUATOR ERROR] Unknown device:".format({target_device})
            )
            return

    except ValueError:
        print(
           "[MQTT ERROR] Invalid JSON: "
        )

    except IOError as error:
        print("[GROVEPI ERROR]", error)

    except Exception as error:
        print("[ACTUATOR ERROR]", error)

def sensor():
    global pir_people_count
    global sensor_state
    global previous_pir_value
    global PIR_PORT
    global ANGLE_SENSOR_PORT
    global ULTRASONIC_G2_PORT
    global LIGHT_SENSOR_PORT
    global BUZZER_PORT
    global BUTTON_PORT

    global NUMBER_OF_PEOPLE
    global ANGLE_THRESHOLD
    global ULTRASONIC_G2_DISTANCE_CM
    global LIGHT_THRESHOLD
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
                        "house/sensors/door_sensor_active",
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
                            "house/sensors/angle",
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
                            "house/sensors/ultrasonic_g2",
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

                    button_state = grovepi.digitalRead(BUTTON_PORT)


                    if (button_state==1):

                        sensor_state["ultrasonic_g3_sensor_active"] = True

                        client.publish(
                            "house/sensors/ultrasonic_g3",
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

                    if raw_light_value >= LIGHT_THRESHOLD:

                        sensor_state[
                            "light_g6_sensor_active"
                        ] = True

                        client.publish(
                            "house/sensors/light",
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

        except KeyboardInterrupt:
            print("\nStopping sensor publisher")
            grovepi.digitalWrite(BUZZER_PORT, 0)
            client.loop_stop()
            client.disconnect()
            break

        except Exception as error:
            print("Sensor error: ", error)

setText('')
create_char(0, eye)
create_char(1, line)
create_char(2, left_smile)
create_char(3, right_smile)
create_char(4, fang)
create_char(5, lefteye)
create_char(6, righteye)

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.tls_set()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.on_message = on_message
client.subscribe("house/actuators/+/device")


print("GrovePi sensor publisher started")
print("[MQTT] GrovePi actuator controller started")
print("[MQTT] Subscribed to house/actuators/+/device")

time.sleep(2)

grovepi.digitalWrite(RED_LED_PORT, 0)
grovepi.digitalWrite(GREEN_LED_PORT, 0)

set_lcd_happy()



t1 = threading.Thread(target=client.loop_forever)
t1.start()

try:
    print('Sensors')
    sensor()

except KeyboardInterrupt:
    print("\n[SYSTEM] Sensor controller stopped")

    #grovepi.digitalWrite(
        #RED_LED_PORT, 0)

    #grovepi.digitalWrite(
        #GREEN_LED_PORT, 0)

    client.disconnect()

#client.loop_start()

t1.join()



time.sleep(0.5)
