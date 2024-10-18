from ttcontrol import *
import random

import dac

#dac.set_dac(0, 1.7, 1.9)

# Factory test
select_design(1)

machine.freq(238000000)

# PIO program to run the clock for 32 cycles out of every 34, looping a specified number of times
@rp2.asm_pio(sideset_init=(rp2.PIO.OUT_LOW,)*2, autopull=True, pull_thresh=32, autopush=True, push_thresh=32, out_shiftdir=rp2.PIO.SHIFT_RIGHT)
def clock_prog():
    out(x, 32)              .side(0)
    label("clock_loop")
    nop()                   .side(1) [7]
    nop()                   .side(1) [7]
    nop()                   .side(1) [7]
    nop()                   .side(1) [7]
    jmp(x_dec, "clock_loop").side(0)
    in_(null, 32)           .side(0)

# Setup the PIO clock driver
sm = rp2.StateMachine(0, clock_prog, sideset_base=clk_pin)
sm.active(1)
sm.put(0) # Initialize clock before HSTX is attached
sm.get()

# Set up HSTX clock output on gpio 17 (clk), coupled with PIO 0
machine.mem32[0x400c0000] = 0x10000010  # Coupled mode, shifting disabled
machine.mem32[0x400c0018] = 0x1d1e      # GPIO 17 set to coupled PIO outputs for 17 and 18 for
                                        # the second and first half of the clock cycle respectively
machine.mem32[0x4002808c] = 0           # Select HSTX for GPIO17
machine.mem32[0x40038048] = 0x10        # Enable GPIO17 pad for output

reset_project()
enable_ui_in(True)
write_ui_in(1)
sm.put(0)
sm.get()
print(read_uo_out())
sm.put(2)
sm.get()
print(read_uo_out())

last_val = read_uo_out()
for i in range(100):
    sm.put(8)
    sm.get()
    val = read_uo_out()
    diff = (val - last_val) & 0xFF
    if diff != 32 and diff != 31 and diff != 30:
        print("Error: ", end="")
    print(f"{diff}")
    last_val = val
else:
    print("OK")