import os
from pathlib import Path
import time
from flask import Flask, jsonify, request, redirect
import whisper
import re
import threading
import torchaudio
import torch
from speechbrain.pretrained import EncoderClassifier
from speechbrain.pretrained.interfaces import SpeakerRecognition

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'m4a', 'mp3', 'wav'}
OBS_PASSWORD = 'mystrongpass'
TARGET_SOURCE_NAME = '音声認識の字幕'
# CSS_TEMPLATE_PATH = 'static/jimaku.css'
WHISPER_MODEL_NAME = 'large'  # tiny, base, small, medium, large
WHISPER_DEVICE = 'cuda'  # cpu, cuda

# Whisperモデルの準備
print('loading whisper model', WHISPER_MODEL_NAME, WHISPER_DEVICE)
whisper_model = whisper.load_model(WHISPER_MODEL_NAME, device=WHISPER_DEVICE)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app = Flask(__name__, static_url_path='/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# 話者認識モデルの準備
base_dir = Path("C:/Users/pg_ma/BBwhisper/content/best_model3")
classifier = EncoderClassifier.from_hparams(
    source=str(base_dir), 
    hparams_file=str(base_dir / 'hparams_inference_sr16000_5people_myvoice.yaml'), 
    savedir=str(base_dir),
    run_opts={"device": "cuda"}
)


verification = SpeakerRecognition.from_hparams(
    source = "speechbrain/spkrec-ecapa-voxceleb",
    savedir = "pretrained_model/spkrec-ecapa-voxceleb",
    run_opts = "cuda"
)

lock = threading.Lock()

prev_file_for_recognition = None

def combine_audio_files(wav1, wav2, upload_folder, fs, ext='wav'):
    # 音声データを結合
    combined_wav = torch.cat((wav1, wav2), dim=1)  # 次元1（時間軸）に沿って結合
    
    # 結合したファイルの保存先ファイル名を生成
    filename = str(int(time.time())) + '.' + ext
    saved_filename = os.path.join(upload_folder, filename)
    
    # 結合した音声データをファイルに保存
    torchaudio.save(saved_filename, combined_wav, fs)

    # 保存したファイルのパスを返す
    return saved_filename



@app.route('/')
def index():
    return redirect('/index.html')


@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    # time_sta = time.perf_counter()
    # print('start transcribe ' + str(time_sta))
    # print("Here is time_sta")
    file = request.files['file']
    # print("Here is file")
    ext = file.filename.rsplit('.', 1)[1].lower()  # 拡張子
    # print("Here is ext")
    if ext and ext in ALLOWED_EXTENSIONS:
        filename = str(int(time.time())) + '.' + ext
        saved_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(saved_filename)
        lock.acquire()
        result = whisper_model.transcribe(
            saved_filename, fp16=False, language='ja'
        )
        lock.release()
        # print('time='+ str(time.perf_counter() - time_sta))
        # print(result)
        # send_jimaku(result['text'])
        # print(result['text'])
        with open("output.txt", 'a') as file:
            file.write(result['text'] + "\n")
        print(result['text'])
        return result, 200
    result = {'error': 'something wrong'}
    print(result)
    return result, 400


@app.route('/api/predict_speaker', methods=['POST'])
def predict():
    file = request.files['file']
    ext = file.filename.rsplit('.', 1)[1].lower()  # 拡張子
    if ext and ext in ALLOWED_EXTENSIONS:
        filename = str(int(time.time())) + '.' + ext
        saved_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(saved_filename)
        lock.acquire()
        signal, fs = torchaudio.load(saved_filename)
        output_probs, score, index, text_lab = classifier.classify_batch(signal)
        lock.release()
        print(f"Predict: {text_lab[0]}")
        # result = {"output_probs" : output_probs, "score" : score, "index" : index, "text_lab" : text_lab[0]}
        result = {"text_lab" : text_lab[0]}
        return result, 200
    result = {'error': 'something wrong'}
    print(result)
    return result, 400


@app.route('/api/transcribe_and_predict', methods=['POST'])
def transcribe_and_predict():
    global prev_file_for_recognition
    file = request.files['file']
    ext = file.filename.rsplit('.', 1)[1].lower()  # 拡張子を取得
    if ext and ext in ALLOWED_EXTENSIONS:
        filename = str(int(time.time())) + '.' + ext
        saved_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(saved_filename)

        file_for_recognition = saved_filename
        file_for_transcribe = saved_filename


        # 音声ファイル結合判定
        if prev_file_for_recognition:
            wav1, fs = torchaudio.load(prev_file_for_recognition)
            wav2, fs = torchaudio.load(saved_filename)
            score, prediction = verification.verify_batch(
                wavs1 = wav1,
                wavs2 = wav2,
                threshold = 0.5
            )
            print(f"Prediction:{prediction}, Score:{score}")
            if prediction:
                combine_file_for_recognition = combine_audio_files(wav1, wav2, app.config['UPLOAD_FOLDER'], fs)
                lock.acquire()
                signal, fs = torchaudio.load(combine_file_for_recognition)
                output_probs, score, index, text_lab = classifier.classify_batch(signal)
                lock.release()
            else:
                lock.acquire()
                signal, fs = torchaudio.load(file_for_recognition)
                output_probs, score, index, text_lab = classifier.classify_batch(signal)
                lock.release()
        else:
            lock.acquire()
            signal, fs = torchaudio.load(file_for_recognition)
            output_probs, score, index, text_lab = classifier.classify_batch(signal)
            lock.release()

        # 文字起こしを行う
        lock.acquire()
        whisper_result = whisper_model.transcribe(file_for_transcribe, fp16=False, language='ja')
        lock.release()

        # 文字起こしと話者認識の結果を組み合わせる
        # combined_result = {
        #     'transcription': whisper_result['text'],
        #     'speaker_label': text_lab[0]
        # }

        whisper_result['text'] = text_lab[0] + " " + whisper_result['text']
        print(whisper_result['text'])

        prev_file_for_recognition = file_for_transcribe

        return whisper_result, 200

    result = {'error': 'Invalid file extension or no file provided'}
    return jsonify(result), 400


app.run(host='0.0.0.0', port=80)
