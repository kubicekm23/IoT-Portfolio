from machine import Pin, I2C
import time

# HC-SR04-style ultrasonic sensor: TRIG -> GP8, ECHO -> GP9
TRIG = Pin(8, Pin.OUT)
ECHO = Pin(9, Pin.IN)
TRIG.value(0)

# MAX7219 matrix: DIN -> GP11, CS/LOAD -> GP10, CLK -> GP12
MATRIX_DIN = Pin(11, Pin.OUT)
MATRIX_CS = Pin(10, Pin.OUT, value=1)
MATRIX_CLK = Pin(12, Pin.OUT, value=0)

# LCD remains on I2C1: SDA -> GP14, SCL -> GP15
i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
devices = i2c.scan()
if not devices:
    raise Exception("No I2C LCD found")
LCD_ADDR = devices[0]
print("LCD found at:", hex(LCD_ADDR))

LCD_BACKLIGHT = 0x08
LCD_ENABLE = 0x04
LCD_RS = 0x01
LCD_CMD = 0
LCD_DATA = 1


def lcd_write4(data):
    i2c.writeto(LCD_ADDR, bytes([data | LCD_BACKLIGHT]))
    i2c.writeto(LCD_ADDR, bytes([data | LCD_BACKLIGHT | LCD_ENABLE]))
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
    lcd_command(0x28)
    lcd_command(0x0C)
    lcd_command(0x01)
    time.sleep_ms(2)
    lcd_command(0x06)


def lcd_set_cursor(row, col):
    address = (0x00 if row == 0 else 0x40) + col
    lcd_command(0x80 | address)


def lcd_line(row, text):
    text = str(text)[:16]
    text += " " * (16 - len(text))
    lcd_set_cursor(row, 0)
    for char in text:
        lcd_char(char)


def get_distance():
    # Send the 10 us trigger pulse.
    TRIG.value(0)
    time.sleep_us(2)
    TRIG.value(1)
    time.sleep_us(10)
    TRIG.value(0)

    # Bound both waits so a missing echo cannot freeze the display.
    timeout = time.ticks_add(time.ticks_us(), 30000)
    while ECHO.value() == 0:
        if time.ticks_diff(timeout, time.ticks_us()) <= 0:
            return None

    start = time.ticks_us()
    timeout = time.ticks_add(start, 30000)
    while ECHO.value() == 1:
        if time.ticks_diff(timeout, time.ticks_us()) <= 0:
            return None

    pulse_us = time.ticks_diff(time.ticks_us(), start)
    return pulse_us * 0.0343 / 2


def max7219_write(register, value):
    MATRIX_CS.value(0)
    for data in (register, value):
        for bit in range(7, -1, -1):
            MATRIX_CLK.value(0)
            MATRIX_DIN.value((data >> bit) & 1)
            MATRIX_CLK.value(1)
    MATRIX_CS.value(1)
    MATRIX_CLK.value(0)


def matrix_show(rows):
    for row, pixels in enumerate(rows):
        max7219_write(row + 1, pixels)


def matrix_init():
    max7219_write(0x0F, 0x00)
    max7219_write(0x09, 0x00)
    max7219_write(0x0B, 0x07)
    max7219_write(0x0A, 0x04)
    max7219_write(0x0C, 0x01)
    matrix_show((0,) * 8)


def matrix_distance_bar(distance_cm):
    # Scale the nominal sensor range (20 to 100 cm) to zero through eight
    # lit columns. Closer objects fill more of the matrix.
    if distance_cm is None:
        columns = 0
    else:
        distance_cm = min(100, max(20, distance_cm))
        columns = int((100 - distance_cm) * 8 / 80 + 0.5)

    row = ((0xFF << (8 - columns)) & 0xFF) if columns else 0
    matrix_show((row,) * 8)


lcd_init()
matrix_init()
lcd_line(0, "Ultrasonic goof")
lcd_line(1, "Starting...")
time.sleep_ms(700)

while True:
    distance = get_distance()
    lcd_line(0, "Distance:")
    if distance is None:
        lcd_line(1, "No echo :(")
    else:
        lcd_line(1, "{:.1f} cm ^_^".format(distance))
        print("Distance: {:.1f} cm".format(distance))

    matrix_distance_bar(distance)
    time.sleep_ms(100)
