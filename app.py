from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel, load_tool, tool
import datetime
import pytz
import yaml
from tools.final_answer import FinalAnswerTool
from Gradio_UI import GradioUI

# ================================================================
# 🛡️ SAFETY CHECK — Block offensive/irrelevant queries
# ================================================================
@tool
def safety_check(query: str) -> str:
    """Checks if a user query is appropriate and related to Germany/language topics.
    Always run this tool FIRST before answering any user question.
    Args:
        query: The user's question or message to check.
    """
    offensive_keywords = [
        "hate", "kill", "weapon", "drug", "racist", "porn",
        "illegal", "bomb", "terror", "violence", "abuse",
        "sex", "nude", "hack", "steal", "fraud"
    ]
    
    query_lower = query.lower()
    for word in offensive_keywords:
        if word in query_lower:
            return "BLOCKED: This question is outside the scope of what I help with. I'm here to help newcomers settle into Germany — things like paperwork, daily life, and learning German. Let's keep it helpful and respectful!"
    
    return "SAFE: Query is appropriate. Proceed with answering."

# ================================================================
# 🏛️ TOOL 1 — Germany Bureaucracy & Life Guide
# ================================================================
@tool
def germany_guide(topic: str) -> str:
    """Provides guidance on German bureaucracy, settling in, and daily life topics.
    Args:
        topic: What the user needs help with (e.g., 'Anmeldung', 'health insurance',
               'opening bank account', 'just arrived checklist', 'renting a flat').
    """
    return (
        f"A newcomer to Germany is asking about: '{topic}'.\n\n"
        f"Give them a warm, practical, straight-talking answer. "
        f"Use short paragraphs — no walls of text. "
        f"Where relevant, give a numbered step-by-step breakdown. "
        f"Mention any important documents they need. "
        f"Add one or two real tips that most official websites won't tell them "
        f"(e.g. book Bürgeramt slots early, N26 is easiest for bank accounts, etc). "
        f"End with one short encouraging sentence. "
        f"Do NOT start with 'Certainly!' or 'Great question!' or 'As an AI'. "
        f"Write like a knowledgeable friend who has lived in Germany, not a customer service bot."
    )

# ================================================================
# 🗣️ TOOL 2 — German Language Coach
# ================================================================
@tool
def language_coach(request: str) -> str:
    """Teaches practical German phrases, grammar tips, or translations for real-life situations.
    Args:
        request: What language help is needed (e.g., 'phrases at the doctor',
                 'how to say excuse me politely', 'translate this sentence',
                 'explain du vs Sie', 'supermarket phrases').
    """
    return (
        f"A newcomer to Germany needs language help with: '{request}'.\n\n"
        f"Respond like a friendly language tutor — warm but direct. "
        f"For phrases: give the German text, a simple pronunciation guide in brackets, "
        f"and the English meaning. Group them naturally by situation. "
        f"For grammar or translation questions: explain it simply with a real example. "
        f"Add a small cultural note if it's useful "
        f"(e.g. Germans say 'Mahlzeit' at lunchtime even to strangers). "
        f"Keep it conversational — like texting a German friend who is also a teacher. "
        f"Never start with 'Certainly!' or 'Of course!' or 'As an AI'. "
        f"Max 3 sentences of explanation before getting into the actual phrases or answer."
    )

# ================================================================
# 🔄 TOOL 3 — German ↔ English Translator
# ================================================================
@tool
def translate(text: str, direction: str) -> str:
    """Translates text between German and English, with context explanation.
    Args:
        text: The text to translate.
        direction: Either 'de_to_en' (German to English) or 'en_to_de' (English to German).
    """
    if direction == "de_to_en":
        return (
            f"Translate this German text to English: '{text}'\n\n"
            f"Give the translation clearly first. "
            f"Then in ONE sentence, explain any cultural or contextual nuance "
            f"if the phrase means something beyond its literal translation "
            f"(e.g. formal vs informal register, idioms, official jargon). "
            f"If it's a straightforward translation with no special nuance, skip the explanation. "
            f"Write naturally — not like a dictionary entry."
        )
    elif direction == "en_to_de":
        return (
            f"Translate this English text to German: '{text}'\n\n"
            f"Give the translation clearly first. "
            f"If there are two natural ways to say it (formal 'Sie' vs informal 'du'), "
            f"show both and briefly explain when to use each. "
            f"Add pronunciation guide in brackets if it's a tricky phrase. "
            f"Write naturally — not like a dictionary entry."
        )
    else:
        return (
            f"The user wants to translate '{text}' but didn't specify direction clearly. "
            f"Detect the language automatically and translate it to the other language "
            f"(German ↔ English). Explain which direction you translated and why."
        )

# ================================================================
# 📋 TOOL 4 — Situation Checklist Generator
# ================================================================
@tool
def get_checklist(situation: str) -> str:
    """Generates a practical checklist for common newcomer situations in Germany.
    Args:
        situation: The situation to get a checklist for (e.g., 'just arrived in Germany',
                   'starting a new job', 'renting a flat', 'visiting a doctor',
                   'opening a bank account').
    """
    return (
        f"A newcomer to Germany needs a practical checklist for: '{situation}'.\n\n"
        f"Give them a clear, numbered checklist. "
        f"Split it into logical phases if needed (e.g. Before / During / After, "
        f"or Week 1 / Week 2-4). "
        f"For each item mention WHY it matters in one short phrase — "
        f"not just what to do but why they shouldn't skip it. "
        f"Include any useful website links (e.g. service.berlin.de, make-it-in-germany.com). "
        f"One practical insider tip at the end that most newcomers learn too late. "
        f"Tone: like a checklist your experienced expat friend emailed you before you moved. "
        f"No corporate language. No 'It is important to note that...'"
    )

# ================================================================
# ⏰ TOOL 5 — Current Time in Any Timezone
# ================================================================
@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """Fetches the current local time in a specified timezone.
    Args:
        timezone: A valid timezone string (e.g., 'Europe/Berlin', 'Asia/Kolkata').
    """
    try:
        tz = pytz.timezone(timezone)
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Couldn't fetch time for '{timezone}': {str(e)}"

# ================================================================
# 🤖 MODEL SETUP
# ================================================================
final_answer = FinalAnswerTool()

model = HfApiModel(
    max_tokens=2096,
    temperature=0.7,   # slightly higher = more natural, less robotic
    model_id='Qwen/Qwen2.5-Coder-32B-Instruct',
    custom_role_conversions=None,
)

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)

# ================================================================
# 🧠 AGENT — with system personality baked in via description
# ================================================================
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
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name="Wegweiser",  # German for "signpost / guide"
    description=(
        "You are Wegweiser — a practical, warm, no-nonsense guide for people "
        "settling into life in Germany. You help with bureaucracy, daily life, "
        "German language, and cultural nuances. "
        "You always run safety_check first on every user message before doing anything else. "
        "If safety_check returns BLOCKED, stop immediately and return that message. "
        "You speak like a knowledgeable friend — direct, helpful, occasionally a little dry humour — "
        "never like a corporate chatbot. "
        "You never start responses with 'Certainly!', 'Great question!', 'Of course!', or 'As an AI'. "
        "You never use bullet point walls. You write in short, clear paragraphs. "
        "You only help with topics related to Germany, German language, and expat life. "
        "If someone asks something completely unrelated, politely redirect them. "
        "Offensive, harmful, or inappropriate requests get a firm but friendly refusal."
    ),
    prompt_templates=prompt_templates
)

GradioUI(agent).launch()