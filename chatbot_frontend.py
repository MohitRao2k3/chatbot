
import uuid
import streamlit as st

from langchain_core.messages import HumanMessage, AIMessage

from langgraph.store.postgres import PostgresStore
from langgraph.checkpoint.postgres import PostgresSaver

from chatbot_backend import builder, DB_URI


# --------------------------------------------------
# Utilities
# --------------------------------------------------

USER_ID = "u1"


def generate_thread_id():
    return str(uuid.uuid4())


def get_config(thread_id):
    return {
        "configurable": {
            "thread_id": thread_id,
            "user_id": USER_ID,
        }
    }


def retrieve_all_threads(checkpointer):
    threads = set()

    for checkpoint in checkpointer.list(None):
        thread_id = (
            checkpoint.config
            .get("configurable", {})
            .get("thread_id")
        )

        if thread_id:
            threads.add(thread_id)

    return sorted(threads, reverse=True)


def load_conversation(graph, thread_id):
    state = graph.get_state(get_config(thread_id))
    messages = state.values.get("messages", [])

    history = []

    for msg in messages:
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "assistant"
        else:
            continue

        content = msg.content

        # Basic text-only chat display
        if isinstance(content, str):
            history.append({
                "role": role,
                "content": content,
            })

    return history


def reset_chat():
    st.session_state.thread_id = generate_thread_id()
    st.session_state.message_history = []


# --------------------------------------------------
# Streamlit application
# --------------------------------------------------

st.set_page_config(
    page_title="Chatbot",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠ChatBot")


# Keep database connections open while this script runs.
with (
    PostgresStore.from_conn_string(DB_URI) as store,
    PostgresSaver.from_conn_string(DB_URI) as checkpointer,
):
    # Initialize database tables.
    store.setup()
    checkpointer.setup()

    # Compile with BOTH long-term memory and conversation history.
    graph = builder.compile(
        store=store,
        checkpointer=checkpointer,
    )

    # ----------------------------------------------
    # Session state
    # ----------------------------------------------

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = generate_thread_id()

    if "message_history" not in st.session_state:
        st.session_state.message_history = []

    # ----------------------------------------------
    # Sidebar
    # ----------------------------------------------

    st.sidebar.title("LangGraph Chatbot")

    if st.sidebar.button("➕ New Chat", use_container_width=True):
        reset_chat()
        st.rerun()

    st.sidebar.header("My Conversations")

    thread_ids = retrieve_all_threads(checkpointer)

    # Include the current thread even before its first checkpoint.
    if st.session_state.thread_id not in thread_ids:
        thread_ids.insert(0, st.session_state.thread_id)

    for thread_id in thread_ids:
        if st.sidebar.button(
            f"💬 {thread_id[:8]}",
            key=f"thread_{thread_id}",
            use_container_width=True,
        ):
            st.session_state.thread_id = thread_id
            st.session_state.message_history = load_conversation(
                graph, thread_id
            )
            st.rerun()

    # ----------------------------------------------
    # Main chat
    # ----------------------------------------------

    for message in st.session_state.message_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask me anything...")

    if user_input:
        st.session_state.message_history.append({
            "role": "user",
            "content": user_input,
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        config = get_config(st.session_state.thread_id)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            answer_parts = []

            try:
                # Stream model messages from the graph.
                for chunk, metadata in graph.stream(
                    {
                        "messages": [
                            HumanMessage(content=user_input)
                        ]
                    },
                    config=config,
                    stream_mode="messages",
                ):
                    # Ignore output from other graph nodes.
                    if metadata.get("langgraph_node") != "chat":
                        continue

                    # Only display text generated by the chat model.
                    if not isinstance(chunk, AIMessage):
                        continue

                    content = chunk.content

                    if isinstance(content, str):
                        answer_parts.append(content)

                    elif isinstance(content, list):
                        for block in content:
                            if (
                                isinstance(block, dict)
                                and block.get("type") == "text"
                            ):
                                answer_parts.append(
                                    block.get("text", "")
                                )

                    response_placeholder.markdown(
                        "".join(answer_parts) + "▌"
                    )

                answer = "".join(answer_parts)
                response_placeholder.markdown(answer or
                    "I couldn't generate a text response.")

                st.session_state.message_history.append({
                    "role": "assistant",
                    "content": answer,
                })

            except Exception as e:
                st.error(f"Something went wrong: {e}")
