import machine
import time

led = machine.Pin(15, machine.Pin.OUT) #configure LED Pin as an output pin and create and led object for Pin class
led_two = machine.Pin(16, machine.Pin.OUT)

while True:
    led_two.value(0)
    led.value(1)  #turn on the LED
    time.sleep(1)   #wait for one second
    led.value(0)  #turn off the LED
    led_two.value(1)
    time.sleep(1)   #wait for one second