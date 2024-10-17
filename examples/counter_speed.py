from ttcontrol import *
import random

import dac

dac.set_dac(0, 1.6)
time.sleep_ms(10)

enable_ui_in(True)
write_ui_in(1)
select_design(1)

time.sleep_ms(10)
dac.set_dac(0, 1.7)
time.sleep_ms(10)

# PIO program to drive the clock.  Put a value n and it clocks n+1 times
# Reads 0 when done.
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, autopull=True, pull_thresh=32, autopush=True, push_thresh=32)
def clock_prog():
    out(x, 32)              .side(0)
    label("clock_loop")
    nop()                   .side(1)
    jmp(x_dec, "clock_loop").side(0)
    in_(null, 32)           .side(0)

# Setup the PIO clock driver
sm = rp2.StateMachine(0, clock_prog, sideset_base=machine.Pin(GPIO_PROJECT_CLK))
sm.active(1)

# Higher core voltage
machine.mem32[0x40100004] = 0x5afea050
machine.mem32[0x4010000c] = 0x5afe00f0  # c0 = 1.15V, d0 = 1.2V, etc

# Drive strength on the clock
#machine.mem32[0x4001c004] = 0x56  # 66 = 8mA, 56 = 4mA

def run_test(freq, fast=False):
    # Multiply requested project clock frequency by 2 to get RP2040 clock
    freq *= 2
    
    if freq > 390_000_000:
        raise ValueError("Too high a frequency requested")
    
    machine.freq(freq)
    time.sleep_ms(2)

    try:
        # Run 1 clock
        print(f"Clock test, start at {read_uo_out()}... ", end ="")
        start_val = read_uo_out()
        sm.put(0)
        sm.get()
        print(f" done. Value: {read_uo_out()}")
        #if tt.output_byte != ((start_val + 1) & 0xFF):
        #    return 1
    
        errors = 0
        if False:
            for _ in range(100):
                start_val = read_uo_out()
                sm.put(0)
                sm.get()
                if read_uo_out() != ((start_val + 1) & 0xFF):
                    errors += 1
            return errors

        for _ in range(10):
            last = read_uo_out()
            
            # Run clock for approx 0.25 or 1 second, sending a multiple of 256 clocks plus 1.
            clocks = (freq // 2048) * 256 if fast else (freq // 512) * 256
            t = time.ticks_us()
            sm.put(clocks + 1)
            sm.get()
            t = time.ticks_us() - t
            print(f"Clocked for {t}us: ", end = "")
                
            # Check the counter has incremented by 2.
            if read_uo_out() != (last + 2) & 0xFF: # and read_uo_out() != (last + 1) & 0xFF:
                print("Error: ", end="")
                errors += 1
            print(read_uo_out())
            
            if not fast:
                # Sleep so the 7-seg display can be read
                time.sleep(0.5)
    finally:
        if freq > 133_000_000:
            machine.freq(133_000_000)
        
    return errors

if __name__ == "__main__":
    freq = 150_000_000
    while True:
        print(f"\nRun at {freq/1000000}MHz project clock\n")
        errors = run_test(freq, True)
        print(errors)
        if errors > 0: break
        freq += 2_000_000