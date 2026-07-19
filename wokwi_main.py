import network
import time
from machine import Pin, PWM
from umqtt.simple import MQTTClient
import json

true = True
false = False

# WiFi configuration
WIFI_SSID = 'Wokwi-GUEST'
WIFI_PASSWORD = ''

# Servo configuration
HAND_SERVO_PIN = 33
SKELETON_SERVO_PIN = 32
SERVO_MIN_DUTY = 40   # Minimum duty cycle for 0 degrees (this value may need adjustment for your servo)
SERVO_MAX_DUTY = 115  # Maximum duty cycle for 180 degrees (this value may need adjustment for your servo)

# MQTT configuration
MQTT_CLIENT_ID = "Haunted house subscriber"
MQTT_TOPIC = 'house/actuators/#'
MQTT_PORT = 8883
MQTT_BROKER = "157cc16c2b0443d0931cfacc745a094f.s1.eu.hivemq.cloud"
MQTT_USER = b"SHH"
MQTT_PASSWORD = b"grp16_shh"

ssl_paramss={'server_hostname': '157cc16c2b0443d0931cfacc745a094f.s1.eu.hivemq.cloud'}

def set_servo_angle(angle, servo):
    duty = SERVO_MIN_DUTY + (SERVO_MAX_DUTY - SERVO_MIN_DUTY) * angle // 180
    servo.duty(duty)
    print('Servo angle set to:', angle)

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('WiFi connected!')

def connect_mqtt():
    client = MQTTClient(client_id = MQTT_CLIENT_ID, server = MQTT_BROKER, port = MQTT_PORT, keepalive = 70, user = MQTT_USER, password = MQTT_PASSWORD, ssl = True, ssl_params = ssl_paramss)
    client.set_callback(on_message)
    client.connect()
    client.subscribe(MQTT_TOPIC)
    print('Connected to MQTT broker and subscribed to topic!')
    return client

def on_message(topic, msg):
    print(topic)
    print(msg)
    #payload = json.loads(msg.payload.decode())
    if topic == b'house/actuators/game1/device':
        message_dict = eval(str(msg.decode('utf-8')))
        if message_dict["status"]:
            print("Painting Moved. Now dropping the skeleton")
            set_servo_angle(180, skeleton_servo)
        else:
            print("Painting not moved")
    elif topic == b'house/actuators/game2/device':
        message_dict = eval(str(msg.decode('utf-8')))
        if message_dict["status"]:
            print("Sensor triggered. Moving Hand")
            set_servo_angle(180, hand_servo)
        else:
            print("Painting not moved")

connect_wifi(WIFI_SSID, WIFI_PASSWORD)

mqtt_client = connect_mqtt()

hand_servo = PWM(Pin(HAND_SERVO_PIN), freq=50)
set_servo_angle(90, hand_servo)
skeleton_servo = PWM(Pin(SKELETON_SERVO_PIN), freq=50)
set_servo_angle(90, skeleton_servo)

while True:
    try:
        mqtt_client.check_msg()
        time.sleep(1)
    except KeyboardInterrupt:
        print('Disconnected from MQTT broker')
        mqtt_client.disconnect()
    except OSError as err:
        print("OsError")
        mqtt_client = connect_mqtt()    
