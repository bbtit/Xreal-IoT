"""
play a sound and record at the same time.
"""
import threading
import wave

import playsound
import pyaudio


def record(
    record_start_event: threading.Event, finish_record_event: threading.Event
):
    RESPEAKER_RATE = 16000
    RESPEAKER_CHANNELS = 1
    RESPEAKER_WIDTH = 2
    RESPEAKER_INDEX = 2  # input device id
    CHUNK = 1024
    WAVE_OUTPUT_FILENAME = "output.wav"

    p = pyaudio.PyAudio()

    stream = p.open(
        rate=RESPEAKER_RATE,
        format=p.get_format_from_width(RESPEAKER_WIDTH),
        channels=RESPEAKER_CHANNELS,
        input=True,
        input_device_index=RESPEAKER_INDEX,
    )

    record_start_event.set()
    print("* recording")

    frames = []

    while not finish_record_event.is_set():
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, "wab")
    wf.setnchannels(RESPEAKER_CHANNELS)
    wf.setsampwidth(
        p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH))
    )
    wf.setframerate(RESPEAKER_RATE)
    wf.writeframes(b"".join(frames))
    wf.close()


def play_sound(
    file_path,
    record_start_event: threading.Event,
    finish_record_event: threading.Event,
):
    record_start_event.wait()
    playsound.playsound(file_path)
    finish_record_event.set()


if __name__ == "__main__":
    record_start_event = threading.Event()
    finish_record_event = threading.Event()

    play_sound_thread = threading.Thread(
        target=play_sound,
        args=(
            "weather.mp3",
            record_start_event,
            finish_record_event,
        ),
    )
    record_thread = threading.Thread(
        target=record, args=(record_start_event, finish_record_event)
    )

    record_thread.start()
    play_sound_thread.start()
