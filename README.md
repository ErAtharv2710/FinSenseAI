# 💰 FinSenseAI — Intelligent Financial Literacy Coach (India Focused)

FinSenseAI is an interactive AI-powered financial literacy assistant designed specifically for Indian users (16–28 years).  
It uses **Google Gemini**, **FastAPI**, and a custom **Electron desktop UI** to deliver clear, safe, and structured financial education.

---

# 🚀 Overview

FinSenseAI provides:

- Indian financial literacy explanations  
- Safe educational responses (non-personalized)  
- Structured Markdown-to-HTML formatted answers  
- Modern ChatGPT-style chat UI  
- Electron desktop app with sidebar navigation  
- FastAPI backend integrated with Gemini AI  

---

# 🧠 Features

## 🔹 AI Chat Assistant ("Finny")
- Gemini-powered conversational AI  
- Indian contextual responses (₹, CIBIL, SIP, PPF, NPS)  
- Hard safety guardrails  
- Markdown → HTML conversion  
- Persistent chat session  

## 🔹 Clean Electron Desktop UI
- Sidebar navigation: Dashboard, New Chat, History, Account  
- Smooth chat interface  
- Dark GitHub-style theme  
- Fully responsive  

## 🔹 FastAPI Backend
- `/chat` endpoint for Gemini conversations  
- CORS-enabled for Electron  
- `/health` endpoint  
- Database bypassed for hackathon build  

---

# 📁 Project Structure

```
FinSenseAI/
│
├── backend/
│   ├── app.py            
│   ├── settings.py       
│
├── frontend/
│   ├── index.html        
│   ├── renderer.js       
│   ├── styles.css        
│
├── main.js               
├── package.json          
├── README.md
└── .env                  
```

---

# ⚙ Installation & Setup

## 1️⃣ Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/FinSenseAI.git
cd FinSenseAI
```

## 2️⃣ Backend Setup
```bash
pip install fastapi uvicorn google-genai pydantic-settings
```

Create `.env`:
```
GEMINI_API_KEY=YOUR_KEY
SECRET_KEY=your_secret_key
```

Run backend:
```bash
cd backend
python app.py
```

---

# (Rest of README Content Continues...)

