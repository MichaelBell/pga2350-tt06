from machine import Pin, ADC
from pimoroni_i2c import PimoroniI2C
from time import sleep_us

PINS_PGA_TT = {"sda": 18, "scl": 19}

i2c = PimoroniI2C(**PINS_PGA_TT)

def set_dac(idx, voltage, max_voltage=1.8):
    if voltage > max_voltage:
        raise Exception(f"{voltage}V higher than maximum")
    
    if idx < 0 or idx > 1:
        raise Exception(f"Invalid DAC idx")
    
    voltage_val = int((voltage / 3.3) * (2**12))
    data = bytearray((voltage_val >> 8, voltage_val))
    
    i2c.writeto(13 + idx, data)
    
def read_adc(adc):
    return 3.3 * (adc.read_u16() / 65535)

def test():
    set_dac(0, 1.0)
    set_dac(1, 0.5)

    adc5 = ADC(5)
    adc6 = ADC(6)
    print(f"A6: {read_adc(adc6)}, A5: {read_adc(adc5)}")

    for millivolt in range(0, 1800, 10):
        set_dac(0, millivolt * .001)
        sleep_us(100)
        print(f"Requested {millivolt}mV, got {read_adc(adc6)*1000:.0f}mV")

             
