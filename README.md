# 🤖 BRIO Lite — AI-Powered OTC Operations Agent

> **Google Gen AI Academy APAC Edition 2026 — Build with Gemini Track**

An intelligent, agentic AI assistant for **Order-to-Cash (OTC)** business operations, powered by **Google Gemini 2.0 Flash** with multi-step function calling.

---

## 🚀 What It Does

BRIO Lite is an **AI Agent** — not just a chatbot. It autonomously calls business tools to:

| Capability | Example Query |
|---|---|
| 📦 Order Tracking | *"What's the status of ORD-2026-002?"* |
| 🔧 Warranty Claims | *"Check warranty claim WC-2026-501"* |
| 🏪 Dealer Profiles | *"Get profile for DLR-205"* |
| 📋 DR Creation | *"Create a DR for DLR-101 — 50 units Turanza T005"* |
| 📊 Listing & Reports | *"Show all orders"* / *"List all dealers by tier"* |

---

## 🧠 Why It's "Agentic"

Unlike a simple chatbot, BRIO Lite uses **Gemini's Function Calling** to:
1. Understand intent from natural language
2. **Autonomously decide** which tool(s) to call
3. Execute those tools (order lookup, warranty check, DR creation, etc.)
4. Synthesize the results into a clear response

This is the **core of AI Agents** — perceive → decide → act → respond.

---

## ⚡ Quick Start (Local)

### 1. Get your Gemini API Key
→ Go to [aistudio.google.com](https://aistudio.google.com) → **Get API Key** → Create key (free tier is sufficient)

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

### 4. Open in browser
→ [http://localhost:8501](http://localhost:8501)

### 5. Paste your API key in the sidebar → Start chatting!

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **AI Model** | Google Gemini 2.0 Flash |
| **Agentic Framework** | Gemini Function Calling (auto loop) |
| **Frontend** | Streamlit |
| **Language** | Python 3.9+ |
| **Deployment** | Local / Google Cloud Run / Streamlit Cloud |

---

## ☁️ Deploy to Streamlit Cloud (Free, 5 min)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Connect your GitHub repo, set `app.py` as the main file
4. Add secret: `GEMINI_API_KEY = "your-key"` in **Advanced settings → Secrets**
5. Deploy → Share the public URL!

---

## 📁 Project Structure

```
brio-lite/
├── app.py              # Main Streamlit app + Gemini agent
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🎯 Sample Queries to Try

```
"Show me all current orders"
"What's the ETA for order ORD-2026-001?"
"Check warranty claim WC-2026-501"
"Get the full profile for dealer DLR-205"
"List all dealers and their tiers"
"Which orders have been delivered?"
"Create a DR for dealer DLR-101 for 50 units of Turanza T005 for Q2 restocking"
"Are there any fleet accounts?"
```

---

## 🏗️ Architecture

```
User Input (Natural Language)
        ↓
  Gemini 2.0 Flash
  (Intent Understanding)
        ↓
  Function Calling Engine
  ┌─────────────────────────────┐
  │  check_order_status()       │
  │  check_warranty_claim()     │
  │  get_dealer_profile()       │
  │  list_all_orders()          │
  │  list_all_dealers()         │
  │  create_dr_request()        │
  └─────────────────────────────┘
        ↓
  Gemini synthesizes results
        ↓
  Natural Language Response → User
```

---

*Built for the Google Gen AI Academy APAC Edition 2026 — "Build with Gemini" Track*
