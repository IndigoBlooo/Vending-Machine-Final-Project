# Vending-Machine-Final-Project
This is my final project for my scripting class. My project is a 1 slot vending machine. (for now)
I had attempted to get two servo's to work, but for simplicity, I decided to keep it to 1. The goal of my project is to first be able to properly connect to WiFi and MQTT. After a successful connection, the attatched OLED screen will display "Vending Machine" and at the bottom of the screen it will say, "Press (A) to load" pressing this will then manually "load" the snack into its designated slot. I also implemented a simple inventory system of 5 snacks per snack slot that can be reloaded by pressing 'A' 5 times. Once you press '1' to dispense snack, the inventory count will go down until there are no snacks present, which it will then display on the OLED "Empty Slot". 

Components Used:
- ESP32
- 4x4 Keypad
- SG90 Servo Motor
- SSD1306 OLED Screen
- Breadboard
- Jumper Wires
