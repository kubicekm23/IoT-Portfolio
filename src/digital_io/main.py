import machine
import time

LED_ONE = machine.Pin(15, machine.Pin.OUT)
LED_TWO = machine.Pin(16, machine.Pin.OUT)
BUTTON = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)

INTERVALS = [2000, 1000, 500, 250, 125, 62, 31] 


def main():
    speed = 0
    led_state = False
    last_blink = time.ticks_ms()

    last_reading = BUTTON.value()
    stable_button = last_reading
    last_change = last_blink

    LED_ONE.value(led_state)
    LED_TWO.value(not led_state)

    while True:
        now = time.ticks_ms()

        reading = BUTTON.value()

        if reading != last_reading:
            last_reading = reading
            last_change = now

        if time.ticks_diff(now, last_change) >= 30:
            if reading != stable_button:
                stable_button = reading

                if stable_button == 0:  # Button pressed
                    speed = (speed + 1) % len(INTERVALS)
                    last_blink = now
                    print("Interval:", INTERVALS[speed] / 1000, "seconds")

        if time.ticks_diff(now, last_blink) >= INTERVALS[speed] // 2:
            last_blink = now
            led_state = not led_state
            LED_ONE.value(led_state)
            LED_TWO.value(not led_state)

        time.sleep_ms(5)


main()