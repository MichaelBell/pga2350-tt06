import time
from machine import ADC, Pin

from ttcontrol import *
import dac

dac.set_dac(0, 1.8)
time.sleep_ms(10)

a0, a1, a2 = ADC(Pin(45)), ADC(Pin(44)), ADC(Pin(43))

enable_ui_in(True)
write_ui_in(0)
select_design(271)

def read_adc(adc):
    return 3.3 * (adc.read_u16() / 65535)

# Enable ringo
write_ui_in(0x60)
ringo = []
for i in range(100):
    ringo.append(read_adc(a0))
write_ui_in(0x0)

print(ringo)
