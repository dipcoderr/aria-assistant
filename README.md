<div align="center">

# ✨ Aria AI Assistant

### 🌈 Your all-in-one companion for ideas, writing, and everyday tasks

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Visit_Aria-7C6FF7?style=for-the-badge)](https://aria-assistant-9f9e.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web_App-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![LangChain](https://img.shields.io/badge/LangChain-AI_Tools-1C3C3C?style=for-the-badge)](https://www.langchain.com/)
[![Render](https://img.shields.io/badge/Hosted_on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=111111)](https://render.com/)

**[🌐 Live App](https://aria-assistant-9f9e.onrender.com/)** ·
**[✨ Features](#-features)** ·
**[🛠️ Tech Stack](#️-tech-stack)** ·
**[🚀 Installation](#-installation)** ·
**[☁️ Deployment](#️-deployment)** ·
**[📁 Project Structure](#-project-structure)**

</div>

---

## 🌟 About Aria

Aria is a vibrant, browser-based AI assistant for writing, research, creative work, and everyday productivity. Built with Flask, LangChain, and LangGraph, it combines a polished chat experience with useful tools, document uploads, voice controls, and persistent conversation memory.

## ✨ Features

### 👤 Chat & productivity

- 💬 **AI conversations** — Chat with memory backed by PostgreSQL checkpoints
- 📄 **Document assistant** — Upload PDF, DOCX, TXT, or CSV files for analysis
- 🔊 **Spoken replies** — Listen to the latest response and future AI replies
- 🎤 **Voice input** — Dictate messages in supported browsers
- 🧹 **Conversation controls** — Start a fresh conversation and clear uploaded files

### ✍️ Writing & creativity

- 📝 **Summarize and improve** writing for clarity, tone, or brevity
- 🌐 **Translate** text and 📌 extract key points or action items
- 💡 **Brainstorm** ideas, create quizzes, and write stories or poems
- 🎨 **Generate images** from text descriptions
- 📋 **Create reports**, fill templates, and structure text as JSON

### 🧠 Reasoning & handy tools

- 🔎 **Search the web** for current information
- ⚖️ **Compare options**, explain concepts, and explore pros and cons
- 🧮 **Calculate** math and percentages
- 🔢 **Count words**, characters, sentences, and reading time
- 🕐 **Check the current time**, get a fun fact, or tell a joke

> 📎 Uploads are limited to **5 MB**. Voice input requires a compatible browser and available speech-recognition service.

## 🛠️ Tech Stack

### 🎨 Application

| Technology | Purpose |
| --- | --- |
| 🐍 **Python 3.12** | Application runtime |
| 🌶️ **Flask** | Web application and routes |
| 🧠 **LangChain** | Model integration and assistant tools |
| 🕸️ **LangGraph** | Agent orchestration and checkpointing |
| 💜 **HTML, CSS, JavaScript** | Responsive chat experience and browser voice controls |

### ☁️ Services

| Service | Purpose |
| --- | --- |
| 🦙 **Ollama Cloud** | OpenAI-compatible language model API |
| 🐘 **Supabase Postgres** | Persistent LangGraph conversation checkpoints |
| 🚀 **Render** | Free-tier web hosting |
| ⚙️ **Gunicorn** | Production WSGI server |

## 📋 Prerequisites

Before running Aria locally, make sure you have:

- 🐍 Python **3.12** or newer
- 🦙 An Ollama Cloud API key
- 🐘 A PostgreSQL database and connection URI, such as Supabase
- 🌐 A modern browser; Chrome or Edge is recommended for voice input

## 🚀 Installation

### 1. 📥 Clone the repository

```bash
git clone https://github.com/dipcoderr/aria-assistant.git
cd aria-assistant
```

### 2. 🧪 Create a virtual environment

```bash
python -m venv .venv
```

Activate it and install the dependencies:

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux**

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 🔐 Configure environment variables

Create a `.env` file in the repository root:

```dotenv
OLLAMA_API_KEY=your_ollama_cloud_api_key
SUPABASE_DB_URI=your_postgresql_connection_uri
FLASK_SECRET_KEY=your_long_random_secret
```

Replace the example values with your own credentials. **Never commit `.env` or publish API keys and database passwords.**

### 4. ▶️ Run Aria

```bash
python app.py
```

Visit **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

## ☁️ Deployment

Aria is configured for Render with the root-level [`render.yaml`](render.yaml) Blueprint and Render's **free web-service plan**.

1. In Render, select **New → Blueprint**.
2. Connect `dipcoderr/aria-assistant` and select the `main` branch.
3. Enter `OLLAMA_API_KEY` and `SUPABASE_DB_URI` in Render's secure setup form.
4. Deploy the Blueprint. It generates `FLASK_SECRET_KEY` automatically.

🔗 **[Launch the deployed app](https://aria-assistant-9f9e.onrender.com/)**

Render free services may spin down after inactivity, which can make the first request take longer to load.

## 🔑 Environment Variables

| Variable | Required | Description |
| --- | :---: | --- |
| `OLLAMA_API_KEY` | ✅ | API key for the Ollama Cloud model |
| `SUPABASE_DB_URI` | ✅ | PostgreSQL connection URI for conversation checkpoints |
| `FLASK_SECRET_KEY` | Recommended | Secret used to sign Flask sessions |
| `PORT` | No | Port supplied by Render; defaults to `5000` locally |
| `FLASK_DEBUG` | No | Set to `1` to enable Flask debug mode locally |

## 📁 Project Structure

```text
aria-assistant/
├── agent.py
├── app.py
├── render.yaml
├── requirements.txt
├── README.md
├── templates/
│   └── chat.html
└── uploads/
```

## 🔒 Privacy & file handling

- Chat messages and extracted document text are sent to the configured AI model provider.
- Conversation checkpoints are stored in the configured PostgreSQL database.
- Uploaded files are stored temporarily in the app's `uploads/` directory; that directory is excluded from Git.
- Never add credentials, private documents, or `.env` files to commits.

## 🤝 Contributing

Ideas and improvements are welcome:

1. Fork the repository.
2. Create a feature branch.
3. Make and test your changes.
4. Open a pull request with a clear summary.

## 💬 Support

Found a bug or have an idea? [Open an issue](https://github.com/dipcoderr/aria-assistant/issues).

---

<div align="center">

### 💜 Made for brighter ideas

If Aria helps you, consider giving the project a ⭐

</div>
