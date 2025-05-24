import argparse
import io
import sys
import time
import tkinter as tk
import wave

import dxcam
import Levenshtein
import ormsgpack
import pyaudio
import requests
import torch
from paddleocr import PaddleOCR
from pydub import AudioSegment
from pydub.playback import play

sys.path.append("./fish_speech")
from fish_speech.utils.file import audio_to_bytes, read_ref_text
from fish_speech.utils.schema import ServeReferenceAudio, ServeTTSRequest


class TTSClient:
    def __init__(self, api_url, api_key, config):
        self.api_url = api_url
        self.api_key = api_key
        self.config = config

    def synthesize(self, text):
        """调用语音合成服务并实时播放"""
        data = {
            "text": text,
            "references": [
                ServeReferenceAudio(
                    audio=ref_audio if ref_audio is not None else b"",
                    text=ref_text
                ) for ref_text, ref_audio in zip(
                    self.config['ref_texts'],
                    self.config['byte_audios']
                )
            ],
            "reference_id": self.config['reference_id'],
            "format": self.config['format'],
            "max_new_tokens": self.config['max_new_tokens'],
            "chunk_length": self.config['chunk_length'],
            "top_p": self.config['top_p'],
            "repetition_penalty": self.config['repetition_penalty'],
            "temperature": self.config['temperature'],
            "streaming": True,  # 启用流式传输
            "use_memory_cache": self.config['use_memory_cache'],
            "seed": self.config['seed']
        }

        try:
            response = requests.post(
                self.api_url,
                data=ormsgpack.packb(
                    ServeTTSRequest(**data),
                    option=ormsgpack.OPT_SERIALIZE_PYDANTIC
                ),
                stream=True,  # 启用流式传输
                headers={
                    "authorization": f"Bearer {self.api_key}",
                    "content-type": "application/msgpack",
                },
            )

            if response.status_code == 200:
                p = pyaudio.PyAudio()
                audio_format = pyaudio.paInt16  # 假设使用16位PCM格式
                stream = p.open(
                    format=audio_format,
                    channels=1,
                    rate=44100,
                    output=True
                )

                stream_stopped_flag = False

                try:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            stream.write(chunk)
                        else:
                            if not stream_stopped_flag:
                                stream.stop_stream()
                                stream_stopped_flag = True
                finally:
                    stream.close()
                    p.terminate()
            else:
                print(f"语音合成失败，状态码：{response.status_code} - {response.text}")
        except Exception as e:
            print(f"请求异常：{str(e)}")


class ScreenRecorder:
    def __init__(self, tts_client: TTSClient):
        self.region: tuple = (0, 0, 0, 0)
        self.cam = dxcam.create()
        self.is_recording = False
        # 初始化PaddleOCR，使用中英文识别模型
        self.cam = dxcam.create()
        self.is_recording = False
        self.ocr = PaddleOCR(use_textline_orientation=True, lang="ch")
        self.tts_client = tts_client
        self.last_text = ""  # 用于去重

    def select_region(self):
        """创建区域选择窗口"""
        root = tk.Tk()
        root.attributes('-fullscreen', True)
        root.attributes('-alpha', 0.3)
        root.configure(bg='white')

        canvas = tk.Canvas(root, cursor="cross", bg='grey11')
        canvas.pack(fill=tk.BOTH, expand=True)

        start_x, start_y = 0, 0
        rect: int = 0

        def on_press(event):
            nonlocal start_x, start_y, rect
            start_x, start_y = event.x, event.y
            rect = canvas.create_rectangle(start_x, start_y, 1, 1, outline='red', width=2)

        def on_drag(event):
            nonlocal start_x, start_y, rect
            canvas.coords(rect, start_x, start_y, event.x, event.y)

        def on_release(event):
            nonlocal self
            x1 = min(start_x, event.x)
            y1 = min(start_y, event.y)
            x2 = max(start_x, event.x)
            y2 = max(start_y, event.y)
            self.region = (x1, y1, x2, y2)
            root.destroy()

        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        root.mainloop()

    def start_record(self, fps=5):
        """开始录制并进行OCR识别"""
        if not self.region:
            raise ValueError("未选择录制区域")

        x1, y1, x2, y2 = self.region
        self.cam.start(target_fps=fps, region=(x1, y1, x2, y2))

        try:
            while self.is_recording:
                frame = self.cam.get_latest_frame()
                if frame is not None:
                    self.process_frame(frame)
                    time.sleep(1/fps)
        except KeyboardInterrupt:
            self.stop_record()

    def process_frame(self, frame):
        """处理帧并进行OCR识别"""
        result = self.ocr.predict(frame)

        if result and result[0]:
            current_text = " ".join(
                [result[0]['rec_texts'][line] for line in range(len(result[0]['rec_texts'])) if result[0]['rec_scores'][line] > 0.5]  # 置信度过滤
            )

            if not self.last_text or (len(current_text) >= 3 and Levenshtein.ratio(current_text, self.last_text) < 0.5):
                print(f"识别到新文本：{current_text}")
                self.last_text = current_text
                self.tts_client.synthesize(current_text)

    def stop_record(self):
        self.is_recording = False
        self.cam.stop()

def parse_args():
    parser = argparse.ArgumentParser(
        description="Send a WAV file and text to a server and receive synthesized audio.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--url",
        "-u",
        type=str,
        default="http://127.0.0.1:8080/v1/tts",
        help="URL of the server",
    )
    parser.add_argument(
        "--api_key",
        type=str,
        default="YOUR_API_KEY",
        help="API key for authentication",
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    # ref_audios = ['audio/纳西坦.wav']
    # ref_texts = ['在一无所知中，梦里的一天结束了，一个新的轮回便会开始。']
    ref_audios = ['audio/钟离.wav']
    ref_texts = ['在全稻妻范围内收缴所有神之眼，镶嵌在千手白眼神像的手中。']
    byte_audios = []
    if ref_audios is None:
        byte_audios = []
    else:
        byte_audios = [audio_to_bytes(ref_audio) for ref_audio in ref_audios]
    if ref_texts is None:
        ref_texts = []
    else:
        ref_texts = [read_ref_text(ref_text) for ref_text in ref_texts]
    # TTS 配置
    tts_config = {
        "reference_id": None,
        "ref_texts": ref_texts,
        "byte_audios": byte_audios,
        "format": "wav",
        "max_new_tokens": 1024,
        "chunk_length": 200,
        "top_p": 0.7,
        "repetition_penalty": 1.2,
        "temperature": 0.7,
        "use_memory_cache": "off",
        "seed": 123
    }

    # 初始化TTS客户端
    tts_client = TTSClient(
        api_url=args.url,
        api_key=args.api_key,
        config=tts_config
    )

    # 初始化录屏器
    recorder = ScreenRecorder(tts_client)

    # 选择区域
    print("请用鼠标拖选要录制的区域...")
    recorder.select_region()

    # 开始识别和语音合成
    print("开始OCR识别和语音合成（按Ctrl+C停止）...")
    recorder.is_recording = True
    recorder.start_record(fps=5)
