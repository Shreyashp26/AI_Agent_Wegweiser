# 🗺️ Wegweiser — Germany Newcomer AI Agent

> *Wegweiser means "signpost" in German — because that's exactly what this is.*

[![Hugging Face Spaces](https://img.shields.io/badge/🤗%20Hugging%20Face-Live%20Demo-orange)](https://huggingface.co/spaces/Shrey26/Shreyash_agent_template)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![smolagents](https://img.shields.io/badge/smolagents-Hugging%20Face-yellow)](https://github.com/huggingface/smolagents)
[![Model](https://img.shields.io/badge/LLM-Llama%203.3%2070B-green)](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct)

---

## 🖼️ Interface

![Wegweiser UI](assets/screenshot.png)

> *Add your screenshot here — see instructions at the bottom of this README.*

---

## 🇩🇪 What Is This?

Moving to Germany is exciting. The paperwork is not.

Wegweiser is an AI agent built to help internationals navigate the real challenges of settling into German life — from registering your address to learning how to politely say "excuse me" at the Bürgeramt.

It combines a large language model with a set of purpose-built tools, so instead of giving you a generic chatbot answer, it picks the right tool for your question and gives you something actually useful.

---

## ✨ What It Can Do

| Ask it... | It uses... |
|---|---|
| "I just arrived in Germany, what do I do?" | 📋 Checklist generator |
| "What is Anmeldung?" | 🏛️ Germany bureaucracy guide |
| "How does health insurance work?" | 🏛️ Germany bureaucracy guide |
| "Give me phrases for visiting a doctor" | 🗣️ Language coach |
| "Translate: Ich verstehe das nicht" | 🔄 German ↔ English translator |
| "What documents do I need to rent a flat?" | 📋 Checklist generator |

---

## 🧠 How It Works

Wegweiser is a **CodeAgent** built with [smolagents](https://github.com/huggingface/smolagents). Every user message triggers this flow:

```
User message
     ↓
safety_check()        ← blocks offensive/irrelevant queries
     ↓
Agent picks tool      ← LLM decides which tool fits the question
     ↓
Tool calls LLM API    ← generates a real, contextual answer
     ↓
final_answer()        ← clean response back to user
```

The agent uses **Meta Llama 3.3 70B** as its brain — both for reasoning about which tool to use, and for generating the actual answers inside each tool.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Agent framework | [smolagents](https://github.com/huggingface/smolagents) |
| LLM | Meta Llama 3.3 70B Instruct |
| LLM API | Hugging Face Inference Router |
| UI | Gradio (custom dark theme) |
| Deployment | Hugging Face Spaces |
| Language | Python 3.11+ |

---

## 🔧 Tools Built

### 🛡️ `safety_check`
Runs on every message first. Blocks offensive, harmful, or off-topic queries before anything else happens.

### 🏛️ `germany_guide`
Answers questions about German bureaucracy and daily life. Covers Anmeldung, health insurance, visas, taxes, banking, renting, and more. Writes like a knowledgeable expat friend — not a government website.

### 🗣️ `language_coach`
Teaches survival German for real situations. Gives German text, pronunciation guide in brackets, English translation, and a cultural note where relevant.

### 🔄 `translate`
Translates between German and English with context. Shows formal (Sie) and informal (du) versions where relevant, and flags any cultural nuance beyond the literal meaning.

### 📋 `get_checklist`
Generates step-by-step checklists for common newcomer situations — arriving, starting a job, renting a flat, opening a bank account. Split into phases with a reason for each step.

### ⏰ `get_current_time_in_timezone`
Returns current time for any timezone. Useful for Berlin, home country comparisons, etc.

---

## 🚀 Try It Live

👉 **[Open on Hugging Face Spaces](https://huggingface.co/spaces/Shrey26/Shreyash_agent_template)**

No setup needed — just open and start asking.

---

## 💻 Run It Locally

```bash
# 1. Clone the repo
git clone https://github.com/Shrey26/wegweiser-germany-agent
cd wegweiser-germany-agent

# 2. Install dependencies
pip install smolagents gradio pytz requests ddgs

# 3. Set your Hugging Face token
export HF_TOKEN=your_token_here

# 4. Run
python app.py
```

Then open `http://localhost:7860` in your browser.

---

## 📁 Project Structure

```
wegweiser-germany-agent/
│
├── app.py              ← Agent + all tools
├── Gradio_UI.py        ← Custom dark UI
├── prompts.yaml        ← Agent prompt templates
├── requirements.txt    ← Dependencies
│
├── tools/
│   └── final_answer.py ← FinalAnswer tool
│
└── assets/
    └── screenshot.png  ← UI screenshot (add yours here)
```

---

## 📸 How to Add Your Screenshot

1. Open your live Space on Hugging Face
2. Take a screenshot of the interface (with a question answered)
3. In your GitHub repo, create a folder called `assets/`
4. Upload the screenshot and name it `screenshot.png`
5. The image will automatically appear at the top of this README

---

## 🌍 Why I Built This

Germany has over 300,000 international arrivals per year. The bureaucracy is real, the language barrier is real, and most official resources are either in German or painfully dry. Wegweiser was built to be the knowledgeable expat friend that answers your 11pm "wait, what even IS a Steuer-ID?" panic with something actually useful.

---

## 👤 Built By

**Shreyash Patil**
MSc Artificial Intelligence — Dublin City University
[LinkedIn](https://linkedin.com/in/shreyash-patil) · [Hugging Face](https://huggingface.co/Shrey26)

---

## 📄 License

MIT — use it, fork it, build on it.
