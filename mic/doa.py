from mic.tuning import Tuning
import usb.core
import usb.util
import time

dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
dev.set_configuration()
if dev:
    Mic_tuning = Tuning(dev)
    while True:
        try:
            print(Mic_tuning.direction)
            time.sleep(1)
        except KeyboardInterrupt:
            break
