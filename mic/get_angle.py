from time import sleep
import usb.core
import usb.util
import struct
import pyaudio


class SoundRecorder:
    PARAMETERS = {
        "DOAANGLE": (
            21,
            0,
            "int",
            359,
            0,
            "ro",
            "DOA angle. Current value. \
            Orientation depends on build configuration.",
        ),
        "SPEECHDETECTED": (
            19,
            22,
            "int",
            1,
            0,
            "ro",
            "Speech detection status.",
            "0 = false (no speech detected)",
            "1 = true (speech detected)",
        ),
    }

    DEVICE = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    TIMEOUT = 100000
    RESPEAKER_RATE = 16000
    RESPEAKER_CHANNELS = 1
    RESPEAKER_WIDTH = 2
    RESPEAKER_INDEX = 2
    CHUNK = 1024
    DEQUE_SIZE = 6

    def __init__(self):
        self.file_number = 0
        self.p = pyaudio.PyAudio()

    def read_parameter(self, param_name):
        try:
            data = self.PARAMETERS[param_name]
        except KeyError:
            return

        id = data[0]

        cmd = 0x80 | data[1]
        if data[2] == "int":
            cmd |= 0x40

        length = 8

        response = self.DEVICE.ctrl_transfer(
            usb.util.CTRL_IN
            | usb.util.CTRL_TYPE_VENDOR
            | usb.util.CTRL_RECIPIENT_DEVICE,
            0,
            cmd,
            id,
            length,
            self.TIMEOUT,
        )

        response = struct.unpack(b"ii", response.tobytes())

        if data[2] == "int":
            result = response[0]
        else:
            result = response[0] * (2.0 ** response[1])

        return result


if __name__ == "__main__":
    recorder = SoundRecorder()
    while True:
        print(recorder.read_parameter("DOAANGLE"))
        sleep(1)
