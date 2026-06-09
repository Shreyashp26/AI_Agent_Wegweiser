from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel, load_tool, tool
import datetime
import requests
import pytz
import yaml
from tools.final_answer import FinalAnswerTool
from Gradio_UI import GradioUI

# ---- TOOL 1: Your custom tool (modified to be useful) ----
@tool
def get_weather_info(city: str) -> str:
    """A tool that returns a weather forecast link for a given city.
    Args:
        city: The name of the city to get weather for (e.g., 'Dublin').
    """
    return f"Check the weather for {city} here: https://wttr.in/{city}"

# ---- TOOL 2: Timezone tool (keep as-is, it works!) ----
@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    try:
        tz = pytz.timezone(timezone)
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"

# ---- Model + Final Answer setup ----
final_answer = FinalAnswerTool()

model = HfApiModel(
    max_tokens=2096,
    temperature=0.5,
    model_id='Qwen/Qwen2.5-Coder-32B-Instruct',
    custom_role_conversions=None,
)

# ---- Load image generation tool from Hub ----
image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

# ---- Load system prompt ----
with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)

# ---- Create the Agent ----
agent = CodeAgent(
    model=model,
    tools=[
        final_answer,                  # ✅ always keep this
        DuckDuckGoSearchTool(),        # ✅ web search
        image_generation_tool,         # ✅ image generation
        get_current_time_in_timezone,  # ✅ timezone checker
        get_weather_info,              # ✅ your custom tool
    ],
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)

GradioUI(agent).launch()