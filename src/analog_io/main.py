import machine
import time

LED = machine.PWM(machine.Pin(15))
POT = machine.ADC(machine.Pin(26))

# 1000 Hz je vypínaní zapínaní, ale ještě pak v loopu se nastavuje jak dlouho je zapnuto
LED.freq(1000)

def main():
    while True:
        LED.duty_u16(POT.read_u16())
        time.sleep(0.01)

main()