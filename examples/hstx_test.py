from ttcontrol import *
import random

import dac

dac.set_dac(0, 1.7, 1.9)

# 4-bit pipelined multiplier
select_design(296)
#select_design(1)

machine.freq(133000000)

# PIO program to drive the inputs and clock at full speed through HSTX
@rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW,)*8, sideset_init=(rp2.PIO.OUT_LOW,)*2, autopull=False, pull_thresh=8, out_shiftdir=rp2.PIO.SHIFT_RIGHT)
def out1_prog():
    pull(block)             
    nop()                   .side(1) # Clock through HSTX is delayed by two cycles?
    nop()                   .side(0)
    out(pins, 8)            .side(0)

# PIO program to drive the inputs and clock at full speed through HSTX
@rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW,)*8, sideset_init=(rp2.PIO.OUT_LOW,)*2, autopull=False, pull_thresh=16, out_shiftdir=rp2.PIO.SHIFT_RIGHT)
def out2_prog():
    pull(block)             
    nop()                   .side(1) [1] # Clock through HSTX is delayed by two cycles?
    nop()                   .side(1)
    out(pins, 8)            .side(0)
    out(pins, 8)            .side(0)

# PIO program to drive the inputs and clock at full speed through HSTX
@rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW,)*8, sideset_init=(rp2.PIO.OUT_LOW,)*2, autopull=False, pull_thresh=32, out_shiftdir=rp2.PIO.SHIFT_RIGHT)
def out4_prog():
    pull(block)             
    nop()                   .side(1) [1] # Clock through HSTX is delayed by two cycles?
    out(pins, 8)            .side(1)
    out(pins, 8)            .side(1)
    out(pins, 8)            .side(0)
    out(pins, 8)            .side(0)

# Setup the PIO clock driver
sm1 = rp2.StateMachine(0, out1_prog, out_base=ui_in[0], sideset_base=clk_pin)
sm1.active(1)
sm1.put(0) # Set inputs to 0 and ensure clock is low before HSTX is attached

sm2 = rp2.StateMachine(1, out2_prog, out_base=ui_in[0], sideset_base=clk_pin)
sm2.active(1)

sm4 = rp2.StateMachine(2, out4_prog, out_base=ui_in[0], sideset_base=clk_pin)
sm4.active(1)

# Set up HSTX clock output on gpio 17 (clk), coupled with PIO 0
machine.mem32[0x400c0000] = 0x10000010  # Coupled mode, shifting disabled
machine.mem32[0x400c0018] = 0x1d1e      # GPIO 17 set to coupled PIO outputs for 17 and 18 for
                                        # the second and first half of the clock cycle respectively
machine.mem32[0x4002808c] = 0           # Select HSTX for GPIO17
machine.mem32[0x40038048] = 0x10        # Enable GPIO17 pad for output

for i in range(10000):
    a = random.randint(0,15)
    b = random.randint(0,15)    
    c = random.randint(0,15)
    d = random.randint(0,15)    
    sm2.put(a | (b << 4) | (c << 8) | (d << 12))
    ab = read_uo_out()
    if ab != a*b: print(f"AB: Expected {a*b}, got {ab}")
    sm1.put(0)
    cd = read_uo_out()
    if cd != c*d: print(f"CD: Expected {c*d}, got {cd} (ab was {a*b})")
    