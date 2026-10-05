"""Pico B: receive I2C toggle commands and switch its LED and active buzzer."""
from machine import Pin
from i2c_slave import I2CSlave
import time

I2C_ADDRESS = 0x42
LED = Pin("LED", Pin.OUT)
BUZZER = Pin(15, Pin.OUT)  # Active 2-wire buzzer: + to GP15, - to GND

# I2C0 pins GP0 (SDA), GP1 (SCL). Pull each bus line up to 3V3 with 4.7k.
bus = I2CSlave(0, address=I2C_ADDRESS, sda=0, scl=1)
state = 0
LED.value(state)
BUZZER.value(0)
print("I2C receiver ready at 0x42")

while True:
    if bus.wait_for_data(100):
        command = bus.read_byte()
        if command == ord("T"):
            state ^= 1
            LED.value(state)
            BUZZER.value(1)
            time.sleep_ms(100)
            BUZZER.value(0)
            print("LED state:", state)
