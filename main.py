from modules.record import SoundRecorder
from modules.req import FileUploader
from modules.window import WindowCanvasManager
from queue import Queue
from threading import Thread
import asyncio

if __name__ == "__main__":
    file_path_queue = Queue()
    voice_angle_queue = Queue()
    transcribed_text_queue = Queue()
    url = "http://192.168.11.53:80/api/transcribe"

    recoder = SoundRecorder(file_path_queue, voice_angle_queue)
    recoder.start_recording()
    create_wav_file_thread = Thread(target=recoder.run)
    create_wav_file_thread.start()

    file_uploader = FileUploader(file_path_queue, transcribed_text_queue, url)
    file_upload_thread = Thread(
        target=asyncio.run, args=(file_uploader.run(),)
    )
    file_upload_thread.start()

    window = WindowCanvasManager()
    drow_voice_angle_arc_and_text_forever_thread = Thread(
        target=window.draw_voice_angle_arc_and_text_forever,
        args=(voice_angle_queue, transcribed_text_queue),
    )
    drow_voice_angle_arc_and_text_forever_thread.start()
    window.run()
