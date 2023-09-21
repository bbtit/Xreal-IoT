from ..modules.record import SoundRecorder
from time import sleep
from queue import Queue

if __name__ == "__main__":
    file_path_queue = Queue()
    voice_angle_queue = Queue()
    recorder = SoundRecorder(file_path_queue, voice_angle_queue)
    while True:
        print(recorder.read_parameter("DOAANGLE"))
        sleep(1)
