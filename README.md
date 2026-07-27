# 🧺 Laundry WhatsApp Bot

A WhatsApp chatbot for **Eco Rinse Laundry** built using **FastAPI**, **Google ADK**, and the **WhatsApp Cloud API**.

The bot can:

* 📋 Show available laundry services
* 🚚 Schedule laundry pickups
* 📍 Collect customer location
* 🕒 Allow customers to choose a pickup time slot
* ✅ Confirm or cancel pickup requests
* 🤖 Answer laundry-related queries using an AI agent

---

## Tech Stack

* Python 3.11+
* FastAPI
* Google ADK
* LiteLLM / Gemini
* WhatsApp Cloud API
* Docker

---

## Project Structure

```text
.
├── agent/
│   ├── agent.py
│   ├── agent_config.py
│   └── services/
├── my_agent/
│   ├── routers/
│   ├── services/
│   ├── session/
│   ├── utils/
│   ├── app.py
│   └── config.py
├── requirements.txt
├── Dockerfile
├── start.sh
└── .gitignore
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/suman277/laundry-whatsapp-bot.git
cd laundry-whatsapp-bot
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**macOS / Linux**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root and add the following variables:

```env
VERIFY_TOKEN=
PHONE_NUMBER_ID=
WHATSAPP_TOKEN=

GOOGLE_GENAI_USE_VERTEXAI=
GOOGLE_API_KEY=

BASE_URL=
VERSION=

IS_LITELLM=
LLM_MODEL_NAME=
LLM_MODEL_API_KEY=
```

---

## Running the Application

Start the FastAPI server:

```bash
uvicorn my_agent.app:app --reload --port 8000
```

The application will be available at:

```text
http://localhost:8000
```

---

## Features

* WhatsApp Cloud API Integration
* AI-powered conversation handling
* Interactive reply buttons
* Interactive list messages
* Pickup scheduling workflow
* Location request support
* Session management
* Docker support

---

## Future Improvements

* Customer order tracking
* Pricing catalogue
* Order history
* Admin dashboard
* Payment integration
* Database-backed session storage
* Multi-language support

---

## License

This project is intended for learning and development purposes.
