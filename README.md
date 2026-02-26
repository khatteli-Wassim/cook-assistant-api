# What To Cook — Backend API

The backend for the "What To Cook" app. An AI assistant that helps you figure out what to cook based on a meal name, your available ingredients, or just surprises you with something random.

Built with FastAPI, LangChain, and LangGraph. Powered by OpenAI.

**Live API:** [cook-assistant-api-liard.vercel.app](https://cook-assistant-api-liard.vercel.app)

---

## What it does

- Give it a meal name → get ingredients and instructions
- Give it ingredients → get meal suggestions
- Give it nothing → get a random meal proposal

---

## Stack

- FastAPI
- LangGraph — orchestrates the workflow
- LangChain — prompt templates and output parsing
- OpenAI GPT-3.5
- Vercel

---

## Running locally

You need Python 3.11+ and an OpenAI API key.
```bash
git clone https://github.com/khatteli-Wassim/cook-assistant-api.git
cd cook-assistant-api

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

Create a `.env` file:
```env
OPENAI_API_KEY=your_key_here
```

Start the server:
```bash
uvicorn app.main:app --reload
```

Runs at `http://localhost:8000` — docs at `http://localhost:8000/docs`

---
