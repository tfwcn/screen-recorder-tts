# screen-recorder-tts

RPG 游戏字幕语音实时合成，让无声文字游戏变有声！

欢迎大佬们提 PR，一起完善这个项目！！！

Real-time TTS for RPG game subtitles, turning silent text games into audio experiences!

Welcome to contribute to this project by submitting PRs!

en | [简体中文](README.zh.md)

## Pull Submodules

```bash
git submodule init
git submodule update
```

## 1. Install Dependencies

```bash
# Create environment
conda create --name screen-recorder-tts python=3.12 -y
# Activate environment
conda activate screen-recorder-tts

# Install paddleocr
pip install torch torchvision torchaudio -i https://download.pytorch.org/whl/cu126

# Install paddlepaddle
pip install paddlepaddle-gpu==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/

# Install paddleocr
pip install paddleocr

# Install dependencies
pip install -r requirements.txt
```

## 2. Start TTS Service, Docker is recommended

```bash
# Create container
docker run -it --name fish-speech --gpus all -p {your port}:8080 -v {project directory}/checkpoints:/opt/fish-speech/checkpoints -v {project directory}/audio:/opt/fish-speech/audio fishaudio/fish-speech:latest-dev zsh
```

### Run the following commands inside the container

- Download model dependencies

```bash
huggingface-cli download fishaudio/fish-speech-1.5 --local-dir checkpoints/fish-speech-1.5
```

- For users in mainland China, download through the mirror.

```bash
HF_ENDPOINT=https://hf-mirror.com huggingface-cli download fishaudio/fish-speech-1.5 --local-dir checkpoints/fish-speech-1.5
```

- Start service

```bash
python -m tools.api_server --listen 0.0.0.0:8080 --llama-checkpoint-path "checkpoints/fish-speech-1.5" --decoder-checkpoint-path "checkpoints/fish-speech-1.5/firefly-gan-vq-fsq-8x1024-21hz-generator.pth" --decoder-config-name firefly_gan_vq --compile

```

Other service deployment methods can be found in the [README](https://speech.fish.audio/zh/#macos)

## 3. Start Script

```bash
python main.py --url http://127.0.0.1:8080/v1/tts
```

After starting, select the text area, and any text that appears in the area will be automatically synthesized and played.

## 4. Configuration

- Audio can be modified in main.py

```python
if __name__ == "__main__":
    args = parse_args()

    # ref_audios = ['audio/纳西坦.wav']
    # ref_texts = ['在一无所知中，梦里的一天结束了，一个新的轮回便会开始。']
    ref_audios = ['audio/钟离.wav']
    ref_texts = ['在全稻妻范围内收缴所有神之眼，镶嵌在千手白眼神像的手中。']
```

## 👩‍👩‍👧‍👦 贡献者

<a href="https://github.com/tfwcn/screen-recorder-tts/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=tfwcn/screen-recorder-tts&max=400&columns=20"  width="40"/>
</a>

## 🌟 Star

[![Star History Chart](https://api.star-history.com/svg?repos=tfwcn/screen-recorder-tts&type=Date)](https://star-history.com/#tfwcn/screen-recorder-tts&Date)

## 📄 许可协议

本项目的发布受[Apache 2.0 license](LICENSE)许可认证。
