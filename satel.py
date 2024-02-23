import os
import re
import serial
import paho.mqtt.client as mqtt
from time import sleep

mqtt_host = os.getenv('MQTT_HOST', 'localhost')
mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
topic_prefix = os.getenv('TOPIC_PREFIX', 'satel')
device = os.getenv('DEVICE', '/dev/ttyS0')
DEBUG = os.getenv('DEBUG', 'False') == 'True'  # Konwersja string na bool
mqtt_user = os.getenv('MQTT_USER', '***')
mqtt_password = os.getenv('MQTT_PASSWORD', '***')

MSG_TEMPLATE = '{{"sensor_name":"{}", "state":"{}"}}'

# Ustawienie portu szeregowego
def set_interface_attribs(serial_port, baudrate=2400):
    serial_port.baudrate = baudrate
    serial_port.timeout = 1  # Timeout na odczyt

def sensor_name(s):
    return {
        1: "entry_doors",
        2: "kitchen",  
        3: "living_room",
        4: "upstairs"
    }.get(s, "-")

def action(line):
    if "NARUSZENIE CZUJNIKA" in line:
        return "ON"
    elif "KONIEC NARUSZENIA CZUJNIKA" in line:
        return "OFF"
    elif "!!!     ALARM Z CZUJNIKA      !!!" in line:
        return "ALARM"
    else:
        return "OTHER"

def parse_line(line):
    pattern = r"\s-\s(.*)WE\.(\d\d)$"
    match = re.search(pattern, line)
    if match:
        event, sensor = match.groups()
        input = int(sensor)
        msg = MSG_TEMPLATE.format(sensor_name(input), action(event), action(event))
        mqtt_topic = f"{topic_prefix}/{sensor_name(input)}"
        if DEBUG:
            print(f"publishing MQTT host: {mqtt_host}, topic: {mqtt_topic}, msg: {msg}")
        client.publish(mqtt_topic, msg)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

client = mqtt.Client()
client.on_connect = on_connect

if mqtt_user and mqtt_password:
    client.username_pw_set(mqtt_user, mqtt_password)

client.connect(mqtt_host, mqtt_port, 60)

# Non-blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
client.loop_start()

try:
    with serial.Serial(device) as ser:
        set_interface_attribs(ser)
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                if DEBUG: print(f"Satel: {line}")
                parse_line(line)
except serial.SerialException as e:
    print(f"Serial error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    client.loop_stop()
