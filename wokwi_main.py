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
MQTT_BROKER = '10.110.66.148'
MQTT_CLIENT_ID = "Haunted house subscriber"
MQTT_TOPIC = 'hhouse/#'

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
    client = MQTTClient(client_id = MQTT_CLIENT_ID, server = MQTT_BROKER, port = 1883, keepalive = 70)
    client.set_callback(on_message)
    client.connect()
    client.subscribe(MQTT_TOPIC)
    print('Connected to MQTT broker and subscribed to topic!')
    return client

def on_message(topic, msg):
    print(topic)
    print(msg)
    #payload = json.loads(msg.payload.decode())
    if topic == b'hhouse/sensors/angle':
        message_dict = eval(str(msg.decode('utf-8')))
        if message_dict["angle"]:
            print("Painting Moved. Now dropping the skeleton")
            set_servo_angle(180, skeleton_servo)
        else:
            print("Painting not moved")
    elif topic == b'hhouse/sensors/ultrasonic_g2':
        message_dict = eval(str(msg.decode('utf-8')))
        if message_dict["ultasonic_g2"]:
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

try:
    while True:
        mqtt_client.check_msg()
        time.sleep(1)
except KeyboardInterrupt:
    print('Disconnected from MQTT broker')
    mqtt_client.disconnect()
