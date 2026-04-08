from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.graph import create_graph
from constants import system_prompt
import os
from dotenv import load_dotenv

load_dotenv()

async def query_agent(text: str, user_id: str, tools) -> str | None:
    model_with_tools = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    ).bind_tools(tools)
    graph_instance = create_graph(model_with_tools)

    state = await graph_instance.aget_state(
        config={"configurable": {"thread_id": user_id}}
    )

    messages = []

    # Check if system message already exists
    has_system = any(
        m.type == "system"
        for m in (state.values.get("messages") or [])
    )

    if not has_system:
        messages.append(SystemMessage(content=system_prompt))

    messages.append(HumanMessage(content=text))

    last_chunk = None

    async for chunk in graph_instance.astream(
        {"messages": messages},
        config={"configurable": {"thread_id": user_id}},
        stream_mode="values",
    ):
        last_chunk = chunk

    if last_chunk and last_chunk.get("messages"):
        return last_chunk["messages"][-1].content

    return None