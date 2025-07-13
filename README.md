# Emberv3 — AI Coding Assistant Framework

Emberv3 is a minimal yet extensible workspace designed for creating AI-powered developer assistants. It combines background agents, environment management, and LLM pre-warming so you can focus on building delightful AI features instead of boilerplate.

## ✨ Key Features

• **Background Agents** — Declarative agent definitions in `cursor.config.json` automate context loading, environment watching, and model warm-up.
• **LLM Pre-loading** — `preload.py` warms your quantized model at startup for snappy responses.
• **Env & Dependency Management** — Simple `.env` and `requirements_complete.txt` keep secrets and packages tidy.
• **Personality Injection** — `ember-personality.txt` ensures consistent tone and expertise across sessions.

## 🛠️ Quick Start

1. **Clone & enter workspace**
   ```bash
   git clone <repo-url> && cd Emberv3
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements_complete.txt
   ```
3. **Configure environment**
   ```bash
   cp .env.example .env  # then edit values
   ```
4. **Run preloader (optional warm-up check)**
   ```bash
   python preload.py
   ```
5. **Open in Cursor** — The background agents will wire themselves up automatically.

## 🧩 Project Structure

```text
├── cursor.config.json      # Background agent definitions
├── preload.py              # LLM warm-up script
├── ember-personality.txt   # Immutable AI persona
├── requirements_complete.txt
├── .env.example            # Environment variable template
└── README.md               # You are here
```

## 🔐 Environment Variables

| Variable     | Description                       |
|--------------|-----------------------------------|
| `API_KEY`    | Your model provider API key       |
| `MODEL_NAME` | Name / path of the quantized LLM  |

Copy `.env.example` to `.env` and fill in the values.

## 🤝 Contributing

Pull requests are welcome! Please open an issue first to discuss major changes.

---

Made with ❤️ & 🔥 by the Ember team.