from ttcontrol import *
import random

enable_ui_in(True)
write_ui_in(0b11100001)

select_design(396)

machine.freq(160000000)

# PIO program to drive the inputs and clock at full speed through HSTX
@rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW,)*8, sideset_init=(rp2.PIO.OUT_LOW,)*2, autopull=True, pull_thresh=32, out_shiftdir=rp2.PIO.SHIFT_RIGHT)
def drive_uin_prog():
    out(pins, 8)            .side(1)

# PIO program to drive the inputs synchronized with the bidirs
@rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW,)*8, autopull=False, pull_thresh=32, out_shiftdir=rp2.PIO.SHIFT_RIGHT)
def drive_uin_sync():
    pull(block)
    irq(4)
    wait(1, irq, 5)
    out(pins, 8)
    out(pins, 8)
    out(pins, 8)
    out(pins, 8)

# PIO program to drive the bidirs synchronized with the inputs
@rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW,)*8, autopull=False, pull_thresh=32, out_shiftdir=rp2.PIO.SHIFT_RIGHT)
def drive_uio_sync():
    pull(block)
    wait(1, irq, 4)
    irq(5) [1]
    out(pins, 8)
    out(pins, 8)
    out(pins, 8)
    out(pins, 8)

# Setup the PIO clock driver
sm1 = rp2.StateMachine(0, drive_uin_prog, out_base=ui_in[0], sideset_base=clk_pin)
sm1.active(1)
sm1.put(0) # Set inputs to 0 and ensure clock is low before HSTX is attached

sm_in = rp2.StateMachine(1, drive_uin_sync, out_base=ui_in[0])
sm_in.active(1)

sm_io = rp2.StateMachine(2, drive_uio_sync, out_base=uio[7])
sm_io.active(1)

# Set up HSTX clock output on gpio 17 (clk), coupled with PIO 0
machine.mem32[0x400c0000] = 0x10000010  # Coupled mode, shifting disabled
machine.mem32[0x400c0018] = 0x1d1e      # GPIO 17 set to coupled PIO outputs for 17 and 18 for
                                        # the second and first half of the clock cycle respectively
machine.mem32[0x4002808c] = 0           # Select HSTX for GPIO17
machine.mem32[0x40038048] = 0x10        # Enable GPIO17 pad for output

def write_row(row, val):
    sm_in.put(row | (row << 8) | 0x8000)
    sm_io.put(val | (val << 8))

for i in range(32):
    write_row(i, i+1)

machine.freq(40000000)

sm1.put(0x20202020)

if False:
    def write_row2(row1, val1, row2, val2):
        sm_in.put(row1 | (row1 << 8) | (row2 << 16) | (row2 << 24) | 0x80008000)
        sm_io.put(val1 | (val1 << 8) | (val2 << 16) | (val2 << 24))

    while True:
        for j in range(2,258):
            machine.freq(150000000)
            for i in range(0,32,2):
                write_row2(i | 0x20, (i+j) & 0xFF, i+1 | 0x20, (i+1+j) & 0xFF)
            
            machine.freq(40000000)
            time.sleep_ms(10)
