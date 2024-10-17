from ttcontrol import *
import random

enable_ui_in(True)
write_ui_in(1)
select_design(1)

manual_clock()
counter = read_uo_out()
for i in range(1000):
    manual_clock()
    counter = (counter + 1) & 0xFF
    val = read_uo_out()
    if val != counter:
        print(f"Got {val}, expected {counter}")
        break
else:
    print("Counter OK")

enable_uio_in([True]*8)
write_ui_in(0)
for i in range(1000):
    r = random.randint(0, 255)
    write_uio_in(r)
    manual_clock()
    val = read_uo_out()
    if val != r:
        print(f"Got {val}, expected {r}")
        break
else:
    print("Loopback OK")
