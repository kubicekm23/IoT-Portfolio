"""Small RP2040 I2C target-mode helper for MicroPython (polling, one-byte commands).

MicroPython's standard RP2 machine.I2C API provides controller mode only.
This helper configures the RP2040 I2C peripheral directly as a target.
"""
import machine
import time

IO_BANK0_BASE = 0x40014000
I2C0_BASE = 0x40044000
I2C1_BASE = 0x40048000
REG_CON = 0x00
REG_SAR = 0x08
REG_DATA_CMD = 0x10
REG_RAW_INTR_STAT = 0x34
REG_ENABLE = 0x6C
REG_STATUS = 0x70
REG_RXFLR = 0x78
REG_CLR_RD_REQ = 0x50
ALIAS_SET = 0x2000
ALIAS_CLR = 0x3000


class I2CSlave:
    def __init__(self, bus_id=0, address=0x42, sda=0, scl=1):
        if bus_id not in (0, 1):
            raise ValueError("bus_id must be 0 or 1")
        if not 0 <= address <= 0x7F:
            raise ValueError("I2C address must be 7-bit")
        self.base = I2C0_BASE if bus_id == 0 else I2C1_BASE

        # RP2040 GPIO function 3 connects the selected pins to I2C.
        for pin in (sda, scl):
            machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
            control = IO_BANK0_BASE + 8 * pin + 4
            machine.mem32[control | ALIAS_CLR] = 0x1F
            machine.mem32[control | ALIAS_SET] = 0x03

        machine.mem32[self.base | ALIAS_CLR | REG_ENABLE] = 1
        machine.mem32[self.base | ALIAS_CLR | REG_SAR] = 0x1FF
        machine.mem32[self.base | ALIAS_SET | REG_SAR] = address
        # Enable target, 7-bit addressing, disable controller mode.
        machine.mem32[self.base | ALIAS_CLR | REG_CON] = 0x49
        machine.mem32[self.base | ALIAS_SET | REG_ENABLE] = 1

    def wait_for_data(self, timeout_ms=100):
        start = time.ticks_ms()
        while not (machine.mem32[self.base + REG_STATUS] & 0x08):
            if time.ticks_diff(time.ticks_ms(), start) >= timeout_ms:
                return False
            time.sleep_ms(1)
        return True

    def read_byte(self):
        # Wait until at least one received byte is available.
        while machine.mem32[self.base + REG_RXFLR] & 0x1F == 0:
            time.sleep_us(50)
        return machine.mem32[self.base + REG_DATA_CMD] & 0xFF
