# ---- Vending Machine Final Project ----

import network
import time
from machine import Pin, PWM, I2C
import ssd1306


# ---- MQTT Implementation ----
try:
    from umqtt.robust import MQTTClient
except:
    from umqtt.simple import MQTTClient

# ----- Wifi and MQTT Broker Configuration -----

WIFI_SSID = "******"
WIFI_PASS = "******"

MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883 
MQTT_CLIENT_ID = "esp32-vender-01"

MQTT_TOPIC_STATUS = b"vender/slot1/status"
MQTT_TOPIC_EVENT = b"vender/slot1/event"

# ---- Remote Vending ----

COMMAND_TOPIC = b"vender/slot1/command"

def on_message(topic, msg):
    print("Got message:", topic, msg)
    if topic == COMMAND_TOPIC and msg == b"vend":
        vend_snack(mqtt_client)

client.set_callback(on_message)
client.subscribe(COMMAND_TOPIC)


# ---- Screen Configuration ----
# VCC=3.3v, GND, SDA=21, SCL=22
I2C_SCL = 22
I2C_SDA = 21

i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))
oled = ssd1306.SSD1306_I2C(128,64, i2c)

def display(line1, line2):
    oled.fill(0)
    oled.text("Vending Machine", 0, 0)
    oled.text(line1, 0, 25)
    oled.text(line2, 0, 45)
    oled.show()

# ---- Keypad Rows and Collums ----
#Rows 1 - 4
ROW_PINS = [32, 33, 25, 26]
# Collums 1 - 4 
COL_PINS = [19, 18, 5, 23]

# Wire ABCD side to GPIO 23

# ---- Keypad Configuration ----
rows = [Pin(p, Pin.OUT) for p in ROW_PINS]
for r in rows:
    r.value(1)
cols = [Pin(p, Pin.IN, Pin.PULL_UP)for p in COL_PINS]

KEYMAP = [
    ['1','2','3','A'],
    ['4','5','6','B'],
    ['7','8','9','C'],
    ['*','0','#','D']
]

#---- Servo Setup ----

SERVO_PIN = 27
servo_pwm = PWM(Pin(SERVO_PIN), freq=50)

def set_servo_angle(angle):
    min_duty = 40
    max_duty = 115
    duty = int(min_duty + (angle/180.0)*(max_duty-min_duty))
    try:
        servo_pwm.duty(duty)
    except AttributeError:
        servo_pwm.duty_u16(int(duty * 64))


# ---- Keypad Scanning ----
def scan_keypad():
    for r in range(4):
        rows[r].value(0)
        for c in range(4):
            if cols[c].value() == 0:
                rows[r].value(1)
                return KEYMAP[r][c]
        rows[r].value(1)
    return None

snack_available = False

# ---- WiFi Connection ----
def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    
    while not wlan.isconnected():
           time.sleep(1)
           
    print("WiFi Connected:", wlan.ifconfig())
    return wlan

# ---- MQTT Configuration ----

mqtt_client = None

def mqtt_connect():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.connect()
    print("MQTT Connected")
    return client

# ---- Vending Routine ----
def vend_snack(client):
    global snack_available

    if not snack_available:
        print("No snack loaded!")
        client.publish(MQTT_TOPIC_EVENT, b"vend_attempt_empty")
        display("EMPTY", "Load snack (A)")
        return
    
    print("Vending...")
    client.publish(MQTT_TOPIC_EVENT, b"vend_start")

# ---- Activating the servo motor ----

    set_servo_angle(45)
    time.sleep(1)
    set_servo_angle(0)

    snack_available = False
    client.publish(MQTT_TOPIC_STATUS, b"empty")
    
    display("Slot Empty!", "Load snack")


# ---- Main Function Loop ----
def main():
    global snack_available

    wifi_connect()
    client = mqtt_connect()

    display ("Ready", "Press A to load")

    last_key = None

    while True:
        key = scan_keypad()

        if key and key != last_key:
            print("Key pressed:", key)


            # A = Load Snack
            if key == "A":
                snack_available = True
                client.publish(MQTT_TOPIC_STATUS, b"loaded")
                display("Snack Loaded", "Ready to Vend")

            elif key == '#':
                vend_snack(client)

        last_key = key
        time.sleep(0.1)

main()
