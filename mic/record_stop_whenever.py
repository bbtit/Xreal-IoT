import pyaudio
import wave

# 録音に関する設定
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
INDEX = 1
WIDTH = 2

frames = []


def audio_callback(in_data, frame_count, time_info, status):
    frames.append(in_data)
    return (in_data, pyaudio.paContinue)


stream = None  # streamの初期化
try:
    audio = pyaudio.PyAudio()

    # 録音開始
    stream = audio.open(
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=INDEX,
        format=audio.get_format_from_width(WIDTH),
        stream_callback=audio_callback,
    )
    while True:
        pass


finally:
    print("正常に終了")
    if stream:  # streamが初期化されているか確認
        stream.stop_stream()
        stream.close()
    if audio:
        audio.terminate()

    # ファイルに保存
    waveFile = wave.open("test_audio.wav", "wb")
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b"".join(frames))
    waveFile.close()
