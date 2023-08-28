from modules.record import SoundRecorder
from modules.req import FileUploader
from modules.window import WindowCanvasManager
from queue import Queue

if __name__ == "__main__":
    file_path_queue = Queue()
    voice_angle_queue = Queue()
    transcribed_text_queue = Queue()
    url = "http://192.168.11.53:80/api/transcribe"

    recoder = SoundRecorder(file_path_queue, voice_angle_queue)
    recoder.start_recording()
    recoder.run()

    uploader = FileUploader(file_path_queue, transcribed_text_queue, url)

    window = WindowCanvasManager()
    window.draw_voice_angle_arc_forever(voice_angle_queue)
    window.draw_transcribed_text_forever(transcribed_text_queue)
    window.run()
