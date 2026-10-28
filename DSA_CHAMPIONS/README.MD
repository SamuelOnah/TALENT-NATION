# 🎫 Campus Ticket AI Analyzer

A modular, multi-provider AI-powered tool designed to streamline campus tech support ticket creation and analysis. It routes ticket descriptions through your choice of leading AI models (**Google Gemini**, **OpenRouter**, or **Groq**) to deliver instant troubleshooting suggestions.

Available as both a **Command-Line Interface (CLI)** and a **Web-Based Terminal (Streamlit)**.

---

## 🚀 Features

* **Multi-Provider AI Routing**: Seamlessly switch between Gemini (`gemini-2.5-flash`), OpenRouter (`openai/gpt-4o-mini`), and Groq (`openai/gpt-oss-20b`).
* **Secure Credential Management**: Keeps sensitive API keys safe using local `.env` configuration and strict Git ignore rules.
* **Local Persistence**: Automatically saves and logs all support tickets locally in `tickets.json` with unique incremental IDs.
* **Dual Interface**: Run via the classic CLI script (`layer1.py`) or launch a modern browser interface (`app.py`).

---

## 🛠️ Tech Stack & Dependencies

* **Python 3.10+**
* **Google GenAI SDK** (`google-genai`)
* **OpenAI SDK** (`openai`)
* **Groq SDK** (`groq`)
* **Streamlit** (`streamlit`)
* **Environment Management** (`python-dotenv`)

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/SamuelOnah/TALENT-NATION.git](https://github.com/SamuelOnah/TALENT-NATION.git)
cd TALENT-NATION/DSA_CHAMPIONS