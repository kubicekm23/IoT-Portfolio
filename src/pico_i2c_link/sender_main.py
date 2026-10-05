"""Pico A: press the button to toggle Pico B's LED and buzzer over I2C."""
from machine import I2C, Pin
import time

I2C_ADDRESS = 0x42
BUTTON = Pin(14, Pin.IN, Pin.PULL_UP)  # Button between GP14 and GND

# Wire GP0 (SDA) and GP1 (SCL) to the other Pico's matching pins.
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100_000)
time.sleep_ms(500)

last_button = BUTTON.value()
while True:
    reading = BUTTON.value()
    if last_button == 1 and reading == 0:
        try:
            i2c.writeto(I2C_ADDRESS, b"T")
            print("Toggle sent")
        except OSError:
            print("Receiver not found; check I2C wiring")
        time.sleep_ms(30)  # debounce
        while BUTTON.value() == 0:
            time.sleep_ms(5)
        time.sleep_ms(30)
        reading = 1
    last_button = reading
    time.sleep_ms(5)
