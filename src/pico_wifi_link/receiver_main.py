"""Pico W B: host a Wi-Fi AP and toggle LED/buzzer on received UDP commands."""
import network
import socket
from machine import Pin
import time

WIFI_SSID = "PicoLink"
WIFI_PASSWORD = "pico-link-123"
PORT = 5005
LED = Pin("LED", Pin.OUT)
BUZZER = Pin(15, Pin.OUT)  # Active 2-wire buzzer: + to GP15, - to GND

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=WIFI_SSID, password=WIFI_PASSWORD)
while not ap.active():
    time.sleep_ms(100)
print("Wi-Fi AP ready:", ap.ifconfig())

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))
state = 0
LED.value(state)
BUZZER.value(0)
print("Waiting for commands on UDP", PORT)

while True:
    message, sender = sock.recvfrom(32)
    if message == b"T":
        state ^= 1
        LED.value(state)
        BUZZER.value(1)
        time.sleep_ms(100)
        BUZZER.value(0)
        print("Toggle from", sender, "LED state:", state)
