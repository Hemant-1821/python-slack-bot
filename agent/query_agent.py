from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.graph import create_graph
from constants import system_prompt
import os
from dotenv import load_dotenv

load_dotenv()


def _to_plain_text(content) -> str | None:
    if isinstance(content, str):
        text = content.strip()
        return text or None

    if isinstance(content, dict):
        text_value = content.get("text")
        if isinstance(text_value, str):
            text = text_value.strip()
            return text or None
        return None

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                value = item.strip()
                if value:
                    parts.append(value)
                continue

            if isinstance(item, dict):
                text_value = item.get("text")
                if isinstance(text_value, str):
                    value = text_value.strip()
                    if value:
                        parts.append(value)

        if parts:
            return "\n".join(parts)

    return None


async def query_agent(text: str, user_id: str, client, tools) -> str | None:
    model_with_tools = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    ).bind_tools(tools)
    graph_instance = create_graph(model_with_tools, client, tools)

    # Keep checkpoints in a dedicated namespace to avoid stale format collisions.
    graph_config = {"configurable": {"thread_id": user_id, "checkpoint_ns": "slack-bot-v1"}}

    try:
        state = await graph_instance.aget_state(config=graph_config)
    except ValueError:
        # Old/incompatible checkpoint data can fail deserialization; continue with fresh state.
        state = None

    messages = []

    # Check if system message already exists
    has_system = any(
        m.type == "system" for m in ((state.values.get("messages") if state else None) or [])
    )

    if not has_system:
        messages.append(SystemMessage(content=system_prompt))

    messages.append(HumanMessage(content=text))

    last_chunk = None

    async for chunk in graph_instance.astream(
        {"messages": messages},
        config=graph_config,
        stream_mode="values",
    ):
        last_chunk = chunk

    if last_chunk and last_chunk.get("messages"):
        return _to_plain_text(last_chunk["messages"][-1].content)

    return None