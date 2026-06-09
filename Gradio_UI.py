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

from smolagents.agent_types import AgentAudio, AgentImage, AgentText, handle_agent_output_types
from smolagents.agents import ActionStep, MultiStepAgent
from smolagents.memory import MemoryStep
from smolagents.utils import _is_package_available


def pull_messages_from_step(step_log: MemoryStep):
    """Extract ChatMessage objects from agent steps"""
    import gradio as gr

    if isinstance(step_log, ActionStep):
        step_number = f"Step {step_log.step_number}" if step_log.step_number is not None else ""

        if hasattr(step_log, "model_output") and step_log.model_output is not None:
            model_output = step_log.model_output.strip()
            model_output = re.sub(r"```\s*<end_code>", "```", model_output)
            model_output = re.sub(r"<end_code>\s*```", "```", model_output)
            model_output = re.sub(r"```\s*\n\s*<end_code>", "```", model_output)
            model_output = model_output.strip()

        if hasattr(step_log, "tool_calls") and step_log.tool_calls is not None:
            first_tool_call = step_log.tool_calls[0]
            used_code = first_tool_call.name == "python_interpreter"
            parent_id = f"call_{len(step_log.tool_calls)}"

            args = first_tool_call.arguments
            if isinstance(args, dict):
                content = str(args.get("answer", str(args)))
            else:
                content = str(args).strip()

            if used_code:
                content = re.sub(r"```.*?\n", "", content)
                content = re.sub(r"\s*<end_code>\s*", "", content)
                content = content.strip()
                if not content.startswith("```python"):
                    content = f"```python\n{content}\n```"

            parent_message_tool = gr.ChatMessage(
                role="assistant",
                content=content,
                metadata={
                    "title": f"🛠️ Used tool {first_tool_call.name}",
                    "id": parent_id,
                    "status": "pending",
                },
            )
            yield parent_message_tool

            if hasattr(step_log, "observations") and (
                step_log.observations is not None and step_log.observations.strip()
            ):
                log_content = step_log.observations.strip()
                if log_content:
                    log_content = re.sub(r"^Execution logs:\s*", "", log_content)
                    yield gr.ChatMessage(
                        role="assistant",
                        content=f"{log_content}",
                        metadata={"title": "📝 Execution Logs", "parent_id": parent_id, "status": "done"},
                    )

            if hasattr(step_log, "error") and step_log.error is not None:
                yield gr.ChatMessage(
                    role="assistant",
                    content=str(step_log.error),
                    metadata={"title": "💥 Error", "parent_id": parent_id, "status": "done"},
                )

            parent_message_tool.metadata["status"] = "done"

        elif hasattr(step_log, "error") and step_log.error is not None:
            yield gr.ChatMessage(
                role="assistant",
                content=str(step_log.error),
                metadata={"title": "💥 Error"}
            )


def stream_to_gradio(
    agent,
    task: str,
    reset_agent_memory: bool = False,
    additional_args: Optional[dict] = None,
):
    if not _is_package_available("gradio"):
        raise ModuleNotFoundError(
            "Please install 'gradio' extra to use the GradioUI: `pip install 'smolagents[gradio]'`"
        )
    import gradio as gr

    total_input_tokens = 0
    total_output_tokens = 0

    for step_log in agent.run(task, stream=True, reset=reset_agent_memory, additional_args=additional_args):
        if hasattr(agent.model, "last_input_token_count"):
            total_input_tokens += agent.model.last_input_token_count
            total_output_tokens += agent.model.last_output_token_count
            if isinstance(step_log, ActionStep):
                step_log.input_token_count = agent.model.last_input_token_count
                step_log.output_token_count = agent.model.last_output_token_count

        for message in pull_messages_from_step(step_log):
            yield message

    final_answer = step_log
    final_answer = handle_agent_output_types(final_answer)

    if isinstance(final_answer, AgentText):
        yield gr.ChatMessage(
            role="assistant",
            content=f"{final_answer.to_string()}",  # ← no "Final answer:" prefix
        )
    elif isinstance(final_answer, AgentImage):
        yield gr.ChatMessage(
            role="assistant",
            content={"path": final_answer.to_string(), "mime_type": "image/png"},
        )
    elif isinstance(final_answer, AgentAudio):
        yield gr.ChatMessage(
            role="assistant",
            content={"path": final_answer.to_string(), "mime_type": "audio/wav"},
        )
    else:
        yield gr.ChatMessage(role="assistant", content=str(final_answer))


class GradioUI:
    """Custom Wegweiser UI"""

    def __init__(self, agent: MultiStepAgent, file_upload_folder: str | None = None):
        if not _is_package_available("gradio"):
            raise ModuleNotFoundError(
                "Please install 'gradio' extra to use the GradioUI: `pip install 'smolagents[gradio]'`"
            )
        self.agent = agent
        self.file_upload_folder = file_upload_folder
        if self.file_upload_folder is not None:
            if not os.path.exists(file_upload_folder):
                os.mkdir(file_upload_folder)

    # ✅ FIXED — properly indented inside the class
    def interact_with_agent(self, prompt, messages):
        import gradio as gr

        messages.append(gr.ChatMessage(role="user", content=prompt))
        yield messages

        final_response = ""
        for msg in stream_to_gradio(self.agent, task=prompt, reset_agent_memory=False):
            if hasattr(msg, "content") and isinstance(msg.content, str):
                # Skip step numbers, tool calls, logs, dividers
                if msg.content.startswith("**Step"):
                    continue
                if msg.content.strip() == "-----":
                    continue
                if "<span style=" in msg.content:
                    continue
                if hasattr(msg, "metadata") and msg.metadata:
                    continue
                # Capture the actual answer
                content = msg.content.replace("**Final answer:**", "").strip()
                if content:
                    final_response = content

        if final_response:
            messages.append(gr.ChatMessage(role="assistant", content=final_response))

        yield messages

    def log_user_message(self, text_input, file_uploads_log):
        return (
            text_input + (
                f"\nYou have been provided with these files, which might be helpful or not: {file_uploads_log}"
                if len(file_uploads_log) > 0
                else ""
            ),
            "",
        )

    def launch(self, **kwargs):
        import gradio as gr

        custom_css = """
        .gradio-container {
            background: linear-gradient(135deg, #0f1923 0%, #1a2a3a 100%) !important;
            font-family: 'Segoe UI', sans-serif !important;
        }
        .wegweiser-header {
            text-align: center;
            padding: 32px 20px 16px 20px;
        }
        .wegweiser-title {
            font-size: 2.8rem;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.5px;
            margin: 0;
        }
        .wegweiser-title span {
            color: #F5A623;
        }
        .wegweiser-subtitle {
            font-size: 1rem;
            color: #8a9bb0;
            margin-top: 6px;
            margin-bottom: 0;
        }
        .wegweiser-flag {
            font-size: 1.8rem;
            margin-bottom: 6px;
        }
        .suggestions-row {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            padding: 16px 20px;
        }
        .suggestion-card {
            background: #1e2d3d;
            border: 1px solid #2a3f55;
            border-radius: 12px;
            padding: 12px 16px;
            cursor: pointer;
            transition: all 0.2s ease;
            max-width: 220px;
            text-align: left;
        }
        .suggestion-card:hover {
            background: #243547;
            border-color: #F5A623;
            transform: translateY(-2px);
        }
        .suggestion-icon {
            font-size: 1.3rem;
            margin-bottom: 4px;
        }
        .suggestion-text {
            font-size: 0.82rem;
            color: #c5d3e0;
            line-height: 1.3;
        }
        .chatbot-wrap {
            border-radius: 16px !important;
            border: 1px solid #2a3f55 !important;
            background: #131f2b !important;
        }
        .input-row textarea {
            background: #1a2a3a !important;
            border: 1px solid #2a3f55 !important;
            border-radius: 12px !important;
            color: #e8f0f7 !important;
            font-size: 0.95rem !important;
        }
        .input-row textarea:focus {
            border-color: #F5A623 !important;
        }
        .wegweiser-footer {
            text-align: center;
            padding: 12px;
            color: #4a6070;
            font-size: 0.78rem;
        }
        """

        with gr.Blocks(
            fill_height=True,
            css=custom_css,
            title="Wegweiser — Germany Newcomer Guide"
        ) as demo:

            stored_messages = gr.State([])
            file_uploads_log = gr.State([])

            gr.HTML("""
                <div class="wegweiser-header">
                    <div class="wegweiser-flag">🇩🇪</div>
                    <h1 class="wegweiser-title">Weg<span>weiser</span></h1>
                    <p class="wegweiser-subtitle">
                        Your no-nonsense guide to settling into Germany —
                        bureaucracy, daily life, and survival German, all in one place.
                    </p>
                </div>
            """)

            gr.HTML("""
                <div class="suggestions-row">
                    <div class="suggestion-card" onclick="document.querySelector('textarea').value=this.querySelector('.suggestion-text').innerText; document.querySelector('textarea').dispatchEvent(new Event('input'))">
                        <div class="suggestion-icon">🏛️</div>
                        <div class="suggestion-text">I just arrived in Germany. What should I do first?</div>
                    </div>
                    <div class="suggestion-card" onclick="document.querySelector('textarea').value=this.querySelector('.suggestion-text').innerText; document.querySelector('textarea').dispatchEvent(new Event('input'))">
                        <div class="suggestion-icon">📋</div>
                        <div class="suggestion-text">What is Anmeldung and how do I complete it?</div>
                    </div>
                    <div class="suggestion-card" onclick="document.querySelector('textarea').value=this.querySelector('.suggestion-text').innerText; document.querySelector('textarea').dispatchEvent(new Event('input'))">
                        <div class="suggestion-icon">🏥</div>
                        <div class="suggestion-text">How does health insurance work in Germany?</div>
                    </div>
                    <div class="suggestion-card" onclick="document.querySelector('textarea').value=this.querySelector('.suggestion-text').innerText; document.querySelector('textarea').dispatchEvent(new Event('input'))">
                        <div class="suggestion-icon">🗣️</div>
                        <div class="suggestion-text">Give me German phrases for visiting a doctor</div>
                    </div>
                    <div class="suggestion-card" onclick="document.querySelector('textarea').value=this.querySelector('.suggestion-text').innerText; document.querySelector('textarea').dispatchEvent(new Event('input'))">
                        <div class="suggestion-icon">🔄</div>
                        <div class="suggestion-text">Translate: Ich verstehe das nicht</div>
                    </div>
                    <div class="suggestion-card" onclick="document.querySelector('textarea').value=this.querySelector('.suggestion-text').innerText; document.querySelector('textarea').dispatchEvent(new Event('input'))">
                        <div class="suggestion-icon">🏦</div>
                        <div class="suggestion-text">How do I open a bank account in Germany?</div>
                    </div>
                    <div class="suggestion-card" onclick="document.querySelector('textarea').value=this.querySelector('.suggestion-text').innerText; document.querySelector('textarea').dispatchEvent(new Event('input'))">
                        <div class="suggestion-icon">💼</div>
                        <div class="suggestion-text">What do I need before starting a new job?</div>
                    </div>
                    <div class="suggestion-card" onclick="document.querySelector('textarea').value=this.querySelector('.suggestion-text').innerText; document.querySelector('textarea').dispatchEvent(new Event('input'))">
                        <div class="suggestion-icon">🏠</div>
                        <div class="suggestion-text">What documents do I need to rent a flat?</div>
                    </div>
                </div>
            """)

            chatbot = gr.Chatbot(
                label="",
                type="messages",
                avatar_images=(
                    None,
                    "https://huggingface.co/datasets/agents-course/course-images/resolve/main/en/communication/Alfred.png",
                ),
                resizable=True,
                scale=1,
                elem_classes=["chatbot-wrap"],
                placeholder=(
                    "<div style='text-align:center; color:#4a6070; padding: 40px 20px;'>"
                    "<div style='font-size:2.5rem'>🗺️</div>"
                    "<div style='font-size:1rem; margin-top:8px;'>Ask me anything about life in Germany.<br>"
                    "Click a card above or type your question below.</div>"
                    "</div>"
                ),
            )

            with gr.Row(elem_classes=["input-row"]):
                text_input = gr.Textbox(
                    lines=1,
                    placeholder="Ask about Anmeldung, health insurance, German phrases, translations...",
                    label="",
                    scale=9,
                    container=False,
                )

            gr.HTML("""
                <div class="wegweiser-footer">
                    Built with smolagents · Qwen2.5 · Hugging Face &nbsp;|&nbsp;
                    Wegweiser means <em>"signpost"</em> in German &nbsp;🗺️
                </div>
            """)

            text_input.submit(
                self.log_user_message,
                [text_input, file_uploads_log],
                [stored_messages, text_input],
            ).then(
                self.interact_with_agent,
                [stored_messages, chatbot],
                [chatbot]
            )

        demo.launch(debug=True, share=True, **kwargs)


__all__ = ["stream_to_gradio", "GradioUI"]