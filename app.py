#!/usr/bin/env python
# coding=utf-8
from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel, tool
import datetime
import pytz
import yaml
import requests
import os
from tools.final_answer import FinalAnswerTool
from Gradio_UI import GradioUI

HF_TOKEN = os.environ.get("HF_TOKEN", "")

# ================================================================
# 🛡️ SAFETY CHECK
# ================================================================
@tool
def safety_check(query: str) -> str:
    """Checks if a user query is appropriate. Always run this FIRST.
    Args:
        query: The user's message to check.
    """
    blocked = [
        "hate", "kill", "weapon", "drug", "racist", "porn",
        "illegal", "bomb", "terror", "violence", "abuse",
        "sex", "nude", "hack", "steal", "fraud"
    ]
    if any(word in query.lower() for word in blocked):
        return "BLOCKED: That's outside what I help with. I'm here for Germany life and language questions — let's keep it useful!"
    return "SAFE"

# ================================================================
# 🏛️ TOOL 1 — Germany Guide
# ================================================================
@tool
def germany_guide(topic: str) -> str:
    """Gives practical guidance on German bureaucracy, settling in, and daily life.
    Args:
        topic: The topic to get help with (e.g., 'health insurance', 'Anmeldung',
               'opening bank account', 'renting a flat', 'visa', 'tax').
    """
    headers = {
        "Authorization": f"Bearer {os.environ.get('HF_TOKEN', '')}",
        "Content-Type": "application/json"
    }
    prompt = (
        f"A newcomer to Germany is asking about: '{topic}'.\n\n"
        f"Give them a warm, practical, straight-talking answer. "
        f"Use short paragraphs. Where relevant, give numbered steps. "
        f"Mention any documents they need. "
        f"Add one insider tip most official websites won't mention. "
        f"End with one short encouraging sentence. "
        f"Do NOT start with 'Certainly!', 'Great question!', or 'As an AI'. "
        f"Write like a knowledgeable friend who has lived in Germany."
    )
    response = requests.post(
        "https://router.huggingface.co/v1/chat/completions",
        headers=headers,
        json={
            "model": "meta-llama/Llama-3.3-70B-Instruct",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 600,
            "temperature": 0.7
        }
    )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    return f"Could not fetch answer (status {response.status_code}). Try rephrasing."

# ================================================================
# 🗣️ TOOL 2 — Language Coach
# ================================================================
@tool
def language_coach(request: str) -> str:
    """Teaches practical German phrases, grammar, or cultural tips for real situations.
    Args:
        request: What language help is needed (e.g., 'phrases at the doctor',
                 'how to say excuse me', 'explain du vs Sie', 'supermarket phrases').
    """
    headers = {
        "Authorization": f"Bearer {os.environ.get('HF_TOKEN', '')}",
        "Content-Type": "application/json"
    }
    prompt = (
        f"A newcomer to Germany needs language help with: '{request}'.\n\n"
        f"Respond like a friendly language tutor. "
        f"For phrases: give German text, pronunciation in brackets, English meaning. "
        f"For grammar: explain simply with a real example. "
        f"Add a small cultural note if useful. "
        f"Keep it conversational — like a German friend who is also a teacher. "
        f"Never start with 'Certainly!' or 'Of course!' or 'As an AI'. "
        f"Max 2 sentences before getting into the actual phrases."
    )
    response = requests.post(
        "https://router.huggingface.co/v1/chat/completions",
        headers=headers,
        json={
            "model": "meta-llama/Llama-3.3-70B-Instruct",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.7
        }
    )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    return f"Could not fetch answer (status {response.status_code}). Try rephrasing."

# ================================================================
# 🔄 TOOL 3 — Translator
# ================================================================
@tool
def translate(text: str, direction: str) -> str:
    """Translates text between German and English with context.
    Args:
        text: The text to translate.
        direction: 'de_to_en' for German to English, 'en_to_de' for English to German,
                   'auto' to detect automatically.
    """
    headers = {
        "Authorization": f"Bearer {os.environ.get('HF_TOKEN', '')}",
        "Content-Type": "application/json"
    }
    if direction == "de_to_en":
        prompt = (
            f"Translate this German text to English: '{text}'\n"
            f"Give the translation first. Then in one sentence explain any cultural "
            f"nuance if relevant. Skip explanation if it's straightforward."
        )
    elif direction == "en_to_de":
        prompt = (
            f"Translate this English text to German: '{text}'\n"
            f"Give the translation first. If there are formal (Sie) and informal (du) "
            f"versions, show both briefly. Add pronunciation guide if it's tricky."
        )
    else:
        prompt = (
            f"Detect the language of '{text}' and translate it to the other language "
            f"(German or English). State which direction you translated."
        )
    response = requests.post(
        "https://router.huggingface.co/v1/chat/completions",
        headers=headers,
        json={
            "model": "meta-llama/Llama-3.3-70B-Instruct",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300,
            "temperature": 0.5
        }
    )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    return f"Could not translate (status {response.status_code}). Try rephrasing."

# ================================================================
# 📋 TOOL 4 — Checklist Generator
# ================================================================
@tool
def get_checklist(situation: str) -> str:
    """Generates a practical checklist for newcomer situations in Germany.
    Args:
        situation: The situation to get a checklist for (e.g., 'just arrived',
                   'starting a new job', 'renting a flat', 'opening a bank account').
    """
    headers = {
        "Authorization": f"Bearer {os.environ.get('HF_TOKEN', '')}",
        "Content-Type": "application/json"
    }
    prompt = (
        f"A newcomer to Germany needs a practical checklist for: '{situation}'.\n\n"
        f"Give a clear numbered checklist split into logical phases (e.g. Week 1 / Week 2-4). "
        f"For each item say briefly WHY it matters. "
        f"Include useful website links where relevant. "
        f"One insider tip at the end that most newcomers learn too late. "
        f"Tone: like a checklist your experienced expat friend emailed you. "
        f"No corporate language."
    )
    response = requests.post(
        "https://router.huggingface.co/v1/chat/completions",
        headers=headers,
        json={
            "model": "meta-llama/Llama-3.3-70B-Instruct",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 600,
            "temperature": 0.7
        }
    )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    return f"Could not generate checklist (status {response.status_code}). Try rephrasing."

# ================================================================
# ⏰ TOOL 5 — Timezone
# ================================================================
@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """Fetches the current local time in a specified timezone.
    Args:
        timezone: A valid timezone string (e.g., 'Europe/Berlin').
    """
    try:
        tz = pytz.timezone(timezone)
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"Current time in {timezone}: {local_time}"
    except Exception as e:
        return f"Couldn't fetch time for '{timezone}': {str(e)}"

# ================================================================
# 🤖 AGENT SETUP
# ================================================================
final_answer = FinalAnswerTool()

model = HfApiModel(
    max_tokens=1024,
    temperature=0.5,
    model_id='meta-llama/Llama-3.3-70B-Instruct',
    custom_role_conversions=None,
)

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)

agent = CodeAgent(
    model=model,
    tools=[
        final_answer,
        safety_check,
        germany_guide,
        language_coach,
        translate,
        get_checklist,
        DuckDuckGoSearchTool(),
        get_current_time_in_timezone,
    ],
    max_steps=4,
    verbosity_level=0,
    grammar=None,
    planning_interval=None,
    name="Wegweiser",
    description=(
        "You are Wegweiser — a practical guide for newcomers in Germany. "
        "Step 1: ALWAYS call safety_check first with the user's query. "
        "Step 2: Based on the topic, call EXACTLY ONE of these tools: "
        "- germany_guide: for ANY question about Germany, bureaucracy, visas, insurance, banking, housing, tax "
        "- language_coach: for German phrases, pronunciation, grammar, cultural tips "
        "- translate: for translating text between German and English "
        "- get_checklist: for step-by-step checklists about arriving, jobs, renting, banking "
        "Step 3: Take the tool output and call final_answer with it immediately. "
        "NEVER use web_search. NEVER skip calling a tool. NEVER add your own text."
    ),
    prompt_templates=prompt_templates
)

GradioUI(agent).launch()