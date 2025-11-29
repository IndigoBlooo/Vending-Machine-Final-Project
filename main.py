*****Vending Machine Final Project*****

import network
import time
import machine
from machine import Pin, PWM, I2C
import ubinascii
import ssd1306


**** MQTT Implementation ****
try:
    from umqtt.robust import MQTTClient
except:
    from umqtt.simple import MQTTClient

***** Wifi and MQTT Broker Configuration *****

WIFI_SSID = "******"
WIFI_PASS = "******"

MQTT_BROKER = "******"
MQTT_PORT = 1883
CLIENT_ID = b"esp32_vend_" + ubinascii.hexlify(machine.unique_id())

TOPIC_STATUS = b"vending/slot1/status"
TOPIC_CMD = b"vending/slot1/cmd"


***** Screen Configuration *****
I2C_SCL = 22
I2C_SDA = 21

***** Keypad Rows and Collums *****
