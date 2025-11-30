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
# VCC=3.3v, GND, SDA=21, SCL=22
I2C_SCL = 22
I2C_SDA = 21

i2c = I2C(0, scl=Pin(22), sda=(21))
oled = ssd1306.SSD1306_I2C(128,64, i2c)

def update_display():
    oled.fill(0)
    oled.text("Vending Machine", 0, 0)
    oled.text("Slot 1:", 0, 20)
    oled.text("AVAILABLE"   if snack_available else "EMPTY", 0, 35)
    oled.show()

***** Keypad Rows and Collums *****
#Rows 1 - 4
ROW_PINS = [32,33,25,26]
# Collums 1 - 4 
COL_PINS = [19,18,5,23]

# Wire ABCD side to GPIO 23

*****Keypad Configuration*******
rows = [Pin(p, Pin.OUT) for p in ROW_PINS]
cols = [Pin(p, Pin.IN, Pin.PULL_UP)for p in COL_PINS]

KEYMAP = [
    ['1','2','3','A'],
    ['4','5','6','B'],
    ['7','8','9','C'],
    ['*','0','#','D']
]

****Servo Setup*****

SERVO_PIN = 17
servo_pwm = PWM(Pin(SERVO_PIN), freq=50)

def set_servo_angle(angle):
    min_duty = 40
    max_duty = 115
    duty = int(min_duty + (angle/180.0)*(max_duty-min_duty))
    try:
        servo_pwm.duty(duty)
    except AttributeError:
        servo_pwm.duty_u16(int(duty * 64))


****Keypad Scanning****
def scan_keypad(timeout=5):
    start = time.ticks_ms()
    while true:
        for r_idx, r in enumerate(rows):
            for rr in rows:
                rr.value(1)
            r.value(0)

            for c_idx, c in enumerate(cols):
                if c.value() == 0:
                    time.sleep_ms(50)
                    while c.value() == 0:
                        time.sleep_ms(10)
                    return KEYMAP[r_idx][c_idx]
        
        if time.ticks_diff(time.ticks_ms(), start) > timeout*1000:
            return None



****WiFi Connection****
def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        oled.fill(0); oled.text("WiFi Connecting...,0,0); oled.show()
        wlan.connect(WIFI_SSID, WIFI_PASS)
        timeout = 15
        start = time.time()
        while not wlan.isconnected():
           time.sleep(1)
           if time.time() - start > timeout:
               break
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        oled.fill(0); oled.text("WiFi Failed to connect",0,0); oled.show()
        return False

****MQTT Configuration*****

mqtt_client = None

def mqtt_connect():
    global mqtt_client
    try:
        mqtt_client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, keepalive=60)
        mqtt_client.set_callback(on_mqtt_message)
        mqtt_client.connect()
        mqtt_client.subscribe(TOPIC_CMD)
        print ("MQTT Successfully Connected!")
        return True
    except Exception as e:
        print ("MQTT Connected Failed:", e)
        return False

def on_mqtt_message(topic, msg):
    print("MQTT msg", topic, msg)
    if topic == TOPIC_CMD and msg.decode() == "VEND":
        oled.fill(0); oled.text("Remote vend....",0,0); oled.show()
        do_vend()
    else if topic == TOPIC_CMD and msg.decode() == "STATUS":
        publish_status()

*****Vending Routine*****
def vend_snack(client):
    global snack_available

    if not snack_available:
        print("No snack loaded!")
        client.publish(MQTT_TOPIC_EVENTS, b"vend_attempt_empty")
        return
    
    print("Vending...")
    client.publish(MQTT_TOPIC_EVENTS, b"vend_start")

******Activating the servo motor*******

    servo_angle(60)
    time.sleep(1)
    servo_angle(0)

    snack_available = False
    client.publish(MQTT_TOPIC_STATUS, b"empty")
    update_display()


******Main Function Loop*********
def main():
    global snack_available

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)

    while not wlan.isconnected():
        time.sleep(0.5)
    print("WiFi Connected:", wlan.ifconfig())

    client = connect_mqtt()
    update_display()

    last_key = None

    while True:
        key = scan_keypad()

        if key and key != last_key:
            print("Pressed:", key)


            # A = Load Snack
            if key == 'A'
                snack_available = True
                client.publish(MQTT_TOPIC_STATUS, b"loaded")
                update_display()

            else if key == '#':
                vend_snack(client)

        last_key = key
        time.sleep(0.1)

main()