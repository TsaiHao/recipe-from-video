# Recipe - 烹饪视频转食谱工具

一个命令行工具，可以将 Bilibili、YouTube、抖音等平台的烹饪视频自动转换为结构化的中文食谱（1人份）。

工作流程：**下载视频 → 提取音频 → 语音识别 → AI 生成食谱 → 输出**

## 示例

输入一个B站烹饪视频链接：

```bash
uv run recipe https://www.bilibili.com/video/BV1xoAhzxEuZ --stt volcano
```

输出结构化的中文食谱：

```markdown
# 东北乱炖

*1人份*

## 食材

| 食材 | 用量 | 必需 |
|------|------|------|
| 西红柿 | 1个（大滚刀块） | 是 |
| 土豆 | 100克（约3-4两） | 是 |
| 尖椒 | 1根（一寸五长段） | 是 |
| 茄子 | 1/4个（大滚刀块） | 是 |
| ...  | ...  | ...  |

## 步骤

1. 准备食材：西红柿切大滚刀块；土豆一切四瓣，切成约1公分厚的滚刀片...
2. 炸土豆：锅中烧油至五到六成热（约150-180°C），关火，利用余温将土豆炸熟...
3. ...

## 营养成分（估算）

- 热量: 450.0 kcal
- 蛋白质: 25.0 g
- 脂肪: 28.0 g
- ...
```

完整示例输出见 [example_output.md](example_output.md)。

## 安装

### 1. 安装 uv（Python 包管理器）

**Linux / macOS / WSL:**

打开终端，运行：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

安装完成后，重启终端或运行 `source ~/.bashrc`（Linux）/ `source ~/.zshrc`（macOS）使命令生效。

**Windows:**

打开 PowerShell，运行：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

安装完成后，重启 PowerShell。

验证安装成功：

```bash
uv --version
```

### 2. 安装外部工具

本工具依赖 `yt-dlp`（下载视频）和 `ffmpeg`（处理音频），需要单独安装。

**Linux/WSL (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install ffmpeg
uv tool install yt-dlp
```

**Linux (Fedora):**

```bash
sudo dnf install ffmpeg
uv tool install yt-dlp
```

**macOS (需先安装 [Homebrew](https://brew.sh)):**

```bash
brew install ffmpeg yt-dlp
```

**Windows (需先安装 [Scoop](https://scoop.sh)):**

```powershell
scoop install ffmpeg yt-dlp
```

### 3. 下载项目并安装依赖

```bash
git clone <本项目地址>
cd recipe
uv sync
```

### 4. 配置 API 密钥

本工具需要大语言模型（LLM）的 API 密钥才能工作。

将示例配置文件复制为 `.env`：

```bash
cp env.example .env
```

用文本编辑器打开 `.env` 文件，填入你的密钥：

```bash
# 必填 - DeepSeek（用于 AI 生成食谱）
DEEPSEEK_API_KEY=你的密钥

# 使用线上语音识别服务需要填写下面的API KEY（推荐 Volcano，速度最快）

# 火山引擎语音识别
VOLCANO_APP_KEY=你的AppKey
VOLCANO_ACCESS_KEY=你的AccessKey
```

**如何获取密钥：**

| 服务 | 用途 | 申请地址 |
|------|------|----------|
| DeepSeek | AI 生成食谱（必需） | https://platform.deepseek.com |
| 火山引擎 | 语音识别（推荐） | https://console.volcengine.com/speech/app |
| Cloudflare Workers AI | 语音识别（备选） | https://dash.cloudflare.com |

> **注意：** `.env` 文件包含你的私密密钥，请勿将其提交到 Git 或分享给他人。

## 使用方法

### 基本用法

```bash
# 从B站视频生成食谱（使用火山引擎语音识别）
uv run recipe https://www.bilibili.com/video/BV1xoAhzxEuZ --stt volcano

# 从本地视频/音频文件生成，使用本地Whisper语音识别
uv run recipe ./我的烹饪视频.mp4 --stt whisper-local

# YouTube 视频也可以
uv run recipe https://www.youtube.com/watch?v=xxxx --stt volcano
```

### 输出格式

```bash
# 默认输出 Markdown 格式（适合阅读）
uv run recipe <视频链接> --stt volcano

# 输出 JSON 格式（适合程序处理）
uv run recipe <视频链接> --stt volcano --output-format json
```

### 语音识别引擎选择

```bash
# 查看所有可用的语音识别引擎
uv run recipe --list-stt

# 使用火山引擎（推荐，速度快，中文识别好）
uv run recipe <视频链接> --stt volcano

# 使用本地 Whisper（无需 API 密钥，但速度较慢）
uv run recipe <视频链接> --stt whisper-local
```

### 其他选项

```bash
# 开启调试日志（排查问题时使用）
uv run recipe <视频链接> --stt volcano --debug

# 跳过缓存，强制重新下载和识别
uv run recipe <视频链接> --stt volcano --no-cache

# 指定 ffmpeg 路径（如果 ffmpeg 不在系统 PATH 中）
uv run recipe <视频链接> --ffmpeg-location /usr/local/bin/ffmpeg

# 查看所有选项
uv run recipe --help
```

### 缓存机制

工具会自动缓存下载的视频、提取的音频和识别的文字到 `./cache/` 目录。再次处理相同的视频时，会跳过已完成的步骤，大幅节省时间。

使用 `--no-cache` 可以忽略缓存，强制重新执行所有步骤。
