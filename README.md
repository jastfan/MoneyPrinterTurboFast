<div align="center">

# ⚡ MoneyPrinterTurboFast v2.0
### The Ultimate 100% Local, Autonomous AI Content Creator Studio
**Turn Long Videos into Viral Shorts, Reels & TikToks on Complete Autopilot — Zero Cloud Fees.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-brightgreen.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-orange.svg)](CONTRIBUTING.md)
[![GitHub Stars](https://img.shields.io/github/stars/jastfan/MoneyPrinterTurboFast?style=social)](https://github.com/jastfan/MoneyPrinterTurboFast)

<p align="center">
  <b>Competitor Tracking (0 Quota)</b> • 
  <b>AI Hook Detection</b> • 
  <b>Face-Tracking Smart Reframe</b> • 
  <b>GFPGAN + Real-ESRGAN HD</b> • 
  <b>Dynamic Captions</b> • 
  <b>Multi-Platform Drip Publisher</b>
</p>

⭐ **If you find this project useful, please give it a Star! It helps the project grow.** ⭐

---

### 🔥 1. AI Auto-Split with Viral Retention Scoring (96/100)
<img src="1-viral-shorts.jpg" width="950" alt="Generated Shorts with Viral Scores"/>

<br><br>

| 🎯 2. Face Reframe & Dynamic Captions | ⚡ 3. Multi-Format High-Res Fetcher |
| :---: | :---: |
| <img src="2-live-editor.jpg" width="460" alt="Face Reframe Editor with Captions"/> | <img src="3-stream-fetcher.jpg" width="460" alt="High Res Format Selection"/> |

---

</div>

## 📌 What is MoneyPrinterTurboFast?

**MoneyPrinterTurboFast** is a complete, self-hosted, all-in-one AI automation pipeline that monitors competitor YouTube channels, detects high-retention viral hooks, automatically reframes horizontal videos into 9:16 vertical Shorts using AI face tracking, enhances face quality with GFPGAN + Real-ESRGAN, overlays animated word-by-word captions, and drip-publishes them across **YouTube Shorts, Instagram Reels, TikTok, and X (Twitter)**.

All processing runs **100% locally on your machine**. Your footage is never uploaded to third-party cloud servers.

---

## 💡 Why MoneyPrinterTurboFast? (Comparison)

| Feature | SaaS Tools (OpusClip / Vizard) | Original MoneyPrinter | ⚡ MoneyPrinterTurboFast v2.0 |
| :--- | :---: | :---: | :---: |
| **Monthly Cost** | **$30 – $60 / month** | Free (OpenAI API fees) | **100% Free Forever ($0)** |
| **Data Privacy** | Cloud servers (Uploaded) | Local | **100% Local & Private** |
| **Competitor Monitoring** | ❌ No | ❌ No | **✅ 0-Quota RSS Feed Tracker** |
| **AI Hook Detection** | Closed proprietary AI | ❌ No (manual timestamps) | **✅ Gemini Multi-Key Pool** |
| **Speaker Face Reframe** | Basic crop | ❌ No | **✅ OpenCV DNN Face Tracking** |
| **AI HD Restoration** | ❌ No | ❌ No | **✅ Real-ESRGAN + GFPGAN v1.4** |
| **Subtitles / Captions** | Burned-in (watermarked) | Basic SRT | **✅ Dynamic TimedText Captions** |
| **Direct Multi-Publishing** | Paid add-on | ❌ No | **✅ Automated Drip Scheduler** |

---

## 🛠️ Complete System Workflow

1. **Competitor Tracker** (`creator_tracker.py`): Tracks competitor YouTube channels via free RSS feeds with 0 API quota consumed.
2. **High-Res Downloader** (`downloader2.py`): Bypasses bot detection & extracts the best video and audio streams.
3. **AI Viral Hook Finder** (`hook_detector2.py`): Analyzes transcripts with a Gemini multi-key pool to detect 90%+ retention hooks.
4. **Face-Tracking Reframe** (`RenderDetect.py`): OpenCV Caffe DNN tracks active speakers and centers them in 9:16 vertical format.
5. **AI HD Facial Restoration** (`ai_enhance.py`): GFPGAN v1.4 face restoration + Real-ESRGAN upscaling for crystal-clear 1080p/4K exports.
6. **Word-Level Captions** (`word_captions.py`): Synced animated Alex Hormozi-style subtitles extracted from timedtext.
7. **AI Metadata & SEO** (`claude_metadata.py`): Claude & Gemini generate viral, high-CTR titles, descriptions, and hashtags.
8. **Drip-Publish Studio** (`publish_module.py`): Automated scheduling across YouTube Shorts, Reels, TikTok, and X.

---

## ✨ Core Features & Modules

- 📡 **0-Quota Competitor Tracker**: Background monitor for new competitor drops with zero quota usage.
- 🧠 **AI Hook Detection**: Auto-clips high-retention segments using an RPM-throttled Gemini key pool.
- 🎯 **OpenCV Face Reframe**: Automatic vertical 9:16 crop that follows the active speaker.
- 🪄 **AI HD Facial Restoration**: GFPGAN + Real-ESRGAN passes for sharp, non-pixelated exports.
- 💬 **Dynamic Word Captions**: Bouncing subtitles synced perfectly with audio dialogue.
- 📅 **Multi-Platform Auto-Scheduler**: Drip-schedule posts (e.g. 1 video every 4 hours) with OAuth integration.

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/jastfan/MoneyPrinterTurboFast.git
cd MoneyPrinterTurboFast
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Configuration
```bash
cp .env.example .env
```
*(Open `.env` to add your free Gemini API key, or keep defaults for local mode).*

### 4. Launch the Studio
```bash
python app.py
```
Open your browser and navigate to: **`http://localhost:5000`**

---

## 💻 System Requirements

- **Python**: 3.9, 3.10, or 3.11
- **FFmpeg**: Bundled automatically via `imageio-ffmpeg` (no manual install needed)
- **GPU (Recommended)**: NVIDIA GPU with CUDA for ultra-fast AI upscaling (CPU mode supported)
- **Disk Space**: ~3GB for model weights (auto-downloaded on first run)

---

## 🤝 Contributing

Contributions make the open-source community an amazing place to learn, inspire, and create.
Please check our [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.
