# Contributing to MoneyPrinterTurboFast

Thank you for considering contributing to MoneyPrinterTurboFast! 

MoneyPrinterTurboFast is an open-source, local-first AI automation studio designed to turn long-form videos into high-retention vertical Shorts, Reels, and TikToks. The project is modular, easy to run, and requires zero paid SaaS subscriptions.

---

## 🧭 Ways to Help

- 🐛 Report Bugs: Open an issue on GitHub detailing your OS, Python version, and error traceback.
- 💡 Suggest Features: Open an issue with the enhancement label detailing what content creators need.
- 🔧 Pick Up a Good First Issue: Check out issues tagged with good first issue.
- 🌍 Test Platforms: Test video links from YouTube, TikTok, Instagram, and Facebook and report edge cases.
- 🪄 Improve AI Models & Captions: Optimize face-tracking, caption animations, or viral hook prompts.
- 📝 Documentation: Add screenshots, video tutorials, installation notes, or translation support.

---

## 🛠️ Development Setup

1. Fork and Clone the Repository:
   git clone https://github.com/jastfan/MoneyPrinterTurboFast.git
   cd MoneyPrinterTurboFast

2. Create a Virtual Environment:
   python -m venv venv
   Windows: venv\Scripts\activate
   Linux/Mac: source venv/bin/activate

3. Install Dependencies:
   pip install -r requirements.txt

4. Setup Configuration:
   cp .env.example .env
   (Add your free Gemini API key in .env if testing Hook Detection)

5. Run the Studio Locally:
   python app.py
   Open http://localhost:5000 in your browser.

---

## 📤 Submitting a Pull Request

1. Create a feature branch:
   git checkout -b feature/your-feature-name

2. Make your changes and test locally end-to-end (Fetch -> Hook Detect -> Face Reframe -> AI Enhance -> Export).

3. Commit your changes:
   git commit -m "feat: your feature description"

4. Push to your fork:
   git push origin feature/your-feature-name

5. Open a Pull Request on GitHub against the main branch.

---

## 📐 Code Style & Architecture Guidelines

- Local-First & Privacy: Features must run locally on the user's machine without mandatory cloud subscriptions.
- No Heavy Build Steps: The web dashboard is built with vanilla HTML/CSS/JS. Avoid introducing npm/Webpack pipelines.
- Lazy AI Model Loading: AI model weights in ai_enhance.py should only load into memory when explicitly triggered.
- Clean Fallbacks: Ensure the code gracefully falls back to local manual modes when API keys are missing.
