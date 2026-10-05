"""Pico W A: button sends a toggle command to Pico W B over Wi-Fi UDP."""
import network
import socket
from machine import Pin
import time

WIFI_SSID = "PicoLink"
WIFI_PASSWORD = "pico-link-123"
RECEIVER_IP = "192.168.4.1"
PORT = 5005
BUTTON = Pin(14, Pin.IN, Pin.PULL_UP)  # Button between GP14 and GND

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)
deadline = time.ticks_add(time.ticks_ms(), 20_000)
while not wlan.isconnected():
    if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
        raise RuntimeError("Could not connect to PicoLink access point")
    time.sleep_ms(250)
print("Connected:", wlan.ifconfig())

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
last_button = BUTTON.value()
while True:
    reading = BUTTON.value()
    if last_button == 1 and reading == 0:
        sock.sendto(b"T", (RECEIVER_IP, PORT))
        print("Toggle sent")
        time.sleep_ms(30)
        while BUTTON.value() == 0:
            time.sleep_ms(5)
        time.sleep_ms(30)
        reading = 1
    last_button = reading
    time.sleep_ms(5)
