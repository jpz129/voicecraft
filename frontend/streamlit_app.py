# Streamlit chat app for Voicecraft: agentic, iterative text revision
import streamlit as st
import requests
import json

# API endpoints for streaming workflow
API_URL = "http://127.0.0.1:8000/revise/stream"
FEEDBACK_API_URL = "http://127.0.0.1:8000/revise/feedback/stream"

# Set up Streamlit page
st.set_page_config(page_title="Voicecraft Revision Workflow", layout="wide")
st.title("📝 Voicecraft: Iterative Text Revision Workflow (API Mode)")
st.markdown("Type or paste your draft below and interact with the assistant to see step-by-step improvements, critiques, and decisions—streamed live from the FastAPI backend!")

# --- Session State Initialization ---
# Remove static default draft; initialize current_draft to empty
if "current_draft" not in st.session_state:
    st.session_state.current_draft = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Chat UI ---
st.write("---")

# Display all previous chat messages (user and assistant)
for msg in st.session_state.get("messages", []):
    st.chat_message(msg["role"]).write(msg["content"])

# --- Node labels and formatting for conversational output ---
node_labels = {
    "plan": "📝 Revision Plan",
    "revise": "✍️ Revised Draft",
    "critique": "🧐 Critique Feedback",
    "decision": "🤔 Decision"
}

def format_node_output(node, node_output):
    # Format each node's output as a conversational message
    if node == "plan" and "revision_plan" in node_output:
        return f"{node_labels[node]}:\n" + "\n".join([f"{i+1}. {step}" for i, step in enumerate(node_output['revision_plan'])])
    elif node == "revise" and "revised_text" in node_output:
        return f"{node_labels[node]}:\n{node_output['revised_text']}"
    elif node == "critique" and "critique_feedback" in node_output:
        return f"{node_labels[node]}:\n" + "\n".join([f"- {point}" for point in node_output['critique_feedback']])
    elif node == "decision" and "revise_again" in node_output:
        if node_output["revise_again"]:
            return f"{node_labels[node]}: Let's revise again! (Looping back to plan, unless iteration cap is reached.)"
        else:
            return f"{node_labels[node]}: No further revision needed. Workflow complete!"
    else:
        return f"{node_labels.get(node, node)}: (No details to display.)"

# --- Chat Input and Streaming Workflow ---
# User enters a draft or feedback as a chat message
if prompt := st.chat_input("Enter your draft or feedback..."):
    # Add user message to chat history
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    # Determine if this is the initial draft or a feedback round
    is_initial = len(st.session_state.get("messages", [])) == 1
    # On first message, treat input as the draft
    if is_initial:
        st.session_state.current_draft = prompt
    endpoint = API_URL if is_initial else FEEDBACK_API_URL
    # Always send the latest revised draft (or initial user input) as "draft"
    payload = {"draft": st.session_state.current_draft, "iteration_cap": 3}
    if not is_initial:
        payload["user_feedback"] = prompt
    # Stream workflow results from the backend and display as assistant chat
    assistant_msg = st.chat_message("assistant")
    full_response = ""
    try:
        with requests.post(endpoint, json=payload, stream=True, timeout=120) as resp:
            for line in resp.iter_lines():
                if line:
                    update = json.loads(line.decode())
                    node = update.get("step", next(iter(update.keys())))
                    node_output = update.get("node_output", {}).get(node, {})
                    # Format and display as a conversational message
                    message = format_node_output(node, node_output)
                    assistant_msg.write(message)
                    # Track the latest revised text for the next round
                    if isinstance(node_output, dict) and "revised_text" in node_output:
                        full_response = node_output["revised_text"]
    except Exception as e:
        assistant_msg.write(f"Error: {e}")
    # Add the final revised text as an assistant message for the next round
    if full_response:
        st.session_state.current_draft = full_response
        st.session_state["messages"].append({"role": "assistant", "content": full_response})
        st.chat_message("assistant").write(full_response)
