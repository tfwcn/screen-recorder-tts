# screen-recorder-tts

RPG 游戏字幕语音实时合成，让无声文字游戏变有声！

欢迎大佬们提 PR，一起完善这个项目！！！

Real-time TTS for RPG game subtitles, turning silent text games into audio experiences!

Welcome to contribute to this project by submitting PRs!

[en](README.md) | 简体中文

## 拉取子模块

```bash
git submodule init
git submodule update
```

## 1. 安装依赖

```bash
# 创建环境
conda create --name screen-recorder-tts python=3.12 -y
# 激活环境
conda activate screen-recorder-tts

# 安装torch
pip install torch torchvision torchaudio -i https://download.pytorch.org/whl/cu126

# 安装paddlepaddle
pip install paddlepaddle-gpu==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/

# 安装paddleocr
pip install paddleocr

# 安装依赖
pip install -r requirements.txt
```

## 2. 启动语音合成服务，推荐用 Docker 启动

```bash
# 创建容器
docker run -it --name fish-speech --gpus all -p {你的端口}:8080 -v {项目目录}/checkpoints:/opt/fish-speech/checkpoints -v {项目目录}/audio:/opt/fish-speech/audio fishaudio/fish-speech:latest-dev zsh
```

### 在容器内执行下面命令

- 下载模型依赖

```bash
huggingface-cli download fishaudio/fish-speech-1.5 --local-dir checkpoints/fish-speech-1.5
```

- 对于中国大陆用户，可以通过镜像站下载。

```bash
HF_ENDPOINT=https://hf-mirror.com huggingface-cli download fishaudio/fish-speech-1.5 --local-dir checkpoints/fish-speech-1.5
```

- 启动服务

```bash
python -m tools.api_server --listen 0.0.0.0:8080 --llama-checkpoint-path "checkpoints/fish-speech-1.5" --decoder-checkpoint-path "checkpoints/fish-speech-1.5/firefly-gan-vq-fsq-8x1024-21hz-generator.pth" --decoder-config-name firefly_gan_vq --compile

```

其他服务部署方式请参考[README](https://speech.fish.audio/zh/#macos)

## 3. 启动脚本

```bash
python main.py --url http://127.0.0.1:8080/v1/tts
```

启动后框选文字区域，后续在区域内出现的文字会自动进行语音合成并播放。

## 4. 配置

- 音频可以在 main.py 中修改

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
