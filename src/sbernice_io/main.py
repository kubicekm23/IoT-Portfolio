from machine import Pin, I2C
import time


# HC-SR04
TRIG = Pin(8, Pin.OUT)
ECHO = Pin(9, Pin.IN)

TRIG.value(0)


# I2C LCD
i2c = I2C(
    1,
    sda=Pin(14),
    scl=Pin(15),
    freq=400000
)

devices = i2c.scan()

if not devices:
    raise Exception("No I2C LCD found")

LCD_ADDR = devices[0]
print("LCD found at:", hex(LCD_ADDR))


# PCF8574 LCD bits
LCD_BACKLIGHT = 0x08
LCD_ENABLE = 0x04
LCD_RS = 0x01

LCD_CMD = 0
LCD_DATA = 1


def lcd_write4(data):
    i2c.writeto(LCD_ADDR, bytes([data | LCD_BACKLIGHT]))
    i2c.writeto(
        LCD_ADDR,
        bytes([data | LCD_BACKLIGHT | LCD_ENABLE])
    )
    time.sleep_us(1)
    i2c.writeto(LCD_ADDR, bytes([data | LCD_BACKLIGHT]))
    time.sleep_us(50)


def lcd_send(value, mode):
    high = value & 0xF0
    low = (value << 4) & 0xF0

    if mode == LCD_DATA:
        high |= LCD_RS
        low |= LCD_RS

    lcd_write4(high)
    lcd_write4(low)


def lcd_command(cmd):
    lcd_send(cmd, LCD_CMD)


def lcd_char(char):
    lcd_send(ord(char), LCD_DATA)


def lcd_init():
    time.sleep_ms(50)

    lcd_write4(0x30)
    time.sleep_ms(5)

    lcd_write4(0x30)
    time.sleep_us(150)

    lcd_write4(0x30)
    lcd_write4(0x20)

    # 4-bit, 2 lines, 5x8 font
    lcd_command(0x28)

    # Display on, cursor off
    lcd_command(0x0C)

    # Clear display
    lcd_command(0x01)
    time.sleep_ms(2)

    # Entry mode
    lcd_command(0x06)


def lcd_clear():
    lcd_command(0x01)
    time.sleep_ms(2)


def lcd_set_cursor(row, col):
    if row == 0:
        address = 0x00 + col
    else:
        address = 0x40 + col

    lcd_command(0x80 | address)


def lcd_print(text):
    for char in str(text):
        lcd_char(char)


def lcd_line(row, text):
    text = str(text)[:16]

    # Pad manually to exactly 16 characters
    text = text + (" " * (16 - len(text)))

    lcd_set_cursor(row, 0)
    lcd_print(text)


# -----------------------------
# Distance measurement
# -----------------------------
def get_distance():
    # Trigger pulse
    TRIG.value(0)
    time.sleep_us(2)

    TRIG.value(1)
    time.sleep_us(10)
    TRIG.value(0)

    # Wait for echo to go HIGH
    timeout = time.ticks_add(time.ticks_us(), 30000)

    while ECHO.value() == 0:
        if time.ticks_diff(timeout, time.ticks_us()) <= 0:
            return None

    start = time.ticks_us()

    # Wait for echo to go LOW
    timeout = time.ticks_add(start, 30000)

    while ECHO.value() == 1:
        if time.ticks_diff(timeout, time.ticks_us()) <= 0:
            return None

    end = time.ticks_us()

    pulse_time = time.ticks_diff(end, start)

    # Speed of sound ~343 m/s
    # Divide by 2 because sound travels there and back
    distance_cm = pulse_time * 0.0343 / 2

    return distance_cm


# -----------------------------
# Main
# -----------------------------
lcd_init()

lcd_line(0, "HC-SR04")
lcd_line(1, "Starting...")
time.sleep(1)

while True:
    distance = get_distance()

    lcd_line(0, "Distance:")

    if distance is None:
        lcd_line(1, "No echo")
    else:
        lcd_line(1, "{:.1f} cm".format(distance))
        print("Distance: {:.1f} cm".format(distance))

    time.sleep_ms(250)