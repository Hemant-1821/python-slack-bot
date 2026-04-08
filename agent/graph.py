from langgraph.graph import StateGraph, MessagesState, END, START
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.mongodb import MongoDBSaver
from typing import Any


def create_graph(model_with_tools: Any, client, tools: list):
    """
    Creates and compiles a LangGraph workflow with MongoDB checkpointing.

    Args:
        model_with_tools: A LangChain model instance with tools bound to it
        client: MongoDB client instance
        tools: List of tools to use in the graph
    """

    checkpointer = MongoDBSaver(client, db_name="sample_mflix") #
    tool_node = ToolNode(tools)
    model_called_in_loop = 0

    def should_continue(state: MessagesState):
        nonlocal model_called_in_loop

        messages = state["messages"]
        last_message = messages[-1]

        # Check for malformed function call
        response_metadata = getattr(last_message, "response_metadata", {}) or {}
        if response_metadata.get("finishReason") == "MALFORMED_FUNCTION_CALL":
            if model_called_in_loop < 2:
                model_called_in_loop += 1
                return "agent"
            else:
                print("Retries exceeded the limit of 2", messages)
                return END

        model_called_in_loop = 0

        # Check if there are tool calls
        tool_calls = getattr(last_message, "tool_calls", None)
        if tool_calls and isinstance(tool_calls, list) and len(tool_calls) > 0:
            return "tools"

        return END

    async def call_model(state: MessagesState):
        messages = state["messages"]
        response = await model_with_tools.ainvoke(messages)
        return {"messages": [response]}

    workflow = (
        StateGraph(MessagesState)
        .add_node("agent", call_model)
        .add_node("tools", tool_node)
        .add_edge(START, "agent")
        .add_conditional_edges("agent", should_continue, ["tools", "agent", END])
        .add_edge("tools", "agent")
    )

    app = workflow.compile(checkpointer=checkpointer)
    return app