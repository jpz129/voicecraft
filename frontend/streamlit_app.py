# Streamlit chat app for Voicecraft: agentic, iterative text revision
import streamlit as st
import requests
import json
import uuid

# API endpoints for streaming workflow
API_URL = "http://127.0.0.1:8000/revise/stream"
FEEDBACK_API_URL = "http://127.0.0.1:8000/revise/feedback/stream"
CANCEL_URL = "http://127.0.0.1:8000/revise/cancel"

# Set up Streamlit page
st.set_page_config(page_title="Voicecraft Revision Workflow", layout="wide")
# style disabled inputs to appear greyed out
st.markdown("""
<style>
input[disabled] {
  background-color: #f0f0f0 !important;
  color: #a0a0a0 !important;
}
</style>
""", unsafe_allow_html=True)
st.title("📝 Voicecraft: Iterative Text Revision Workflow (API Mode)")
st.markdown("Type or paste your draft below and interact with the assistant to see step-by-step improvements, critiques, and decisions—streamed live from the FastAPI backend!")

# --- Session State Initialization ---
# Remove static default draft; initialize current_draft to empty
if "current_draft" not in st.session_state:
    st.session_state.current_draft = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False
if "request_id" not in st.session_state:
    st.session_state.request_id = None

# --- Chat UI ---
st.write("---")
# Display previous messages
for msg in st.session_state.get("messages", []):
    st.chat_message(msg["role"]).write(msg["content"])

# Chat Input placeholder: disabled while processing
input_slot = st.empty()
if st.session_state.get("processing", False):
    # greyed-out disabled input while processing
    input_slot.text_input("", placeholder="Processing...", disabled=True, key="disabled_input")
    prompt = None
elif "pending_prompt" not in st.session_state:
    # accept new input when not processing and no pending prompt
    prompt = input_slot.chat_input("Enter your draft or feedback...", key="chat_input")
    if prompt:
        st.session_state.pending_prompt = prompt
        st.session_state.processing = True
else:
    prompt = None

# --- Node labels and formatting for conversational output ---
node_labels = {
    "plan": "Planning how to improve your draft",
    "revise": "Revising your text",
    "critique": "Reviewing the revision for feedback",
    "decision": "Deciding if another round is needed",
    "qa": "Answering your question about the latest draft"
}

def format_node_output(node, node_output):
    # Suppress intent node messages
    if node == "intent":
        return None
    # Format each node's output as a conversational message
    if node == "qa" and "answer" in node_output:
        return f"❓ Answer to your question about the latest draft:\n{node_output['answer']}"
    if node == "plan" and "revision_plan" in node_output:
        return "📝 Revision Plan:\n" + "\n".join([f"{i+1}. {step}" for i, step in enumerate(node_output['revision_plan'])])
    elif node == "revise" and "revised_text" in node_output:
        return "✍️ Here is the improved draft:\n" + node_output['revised_text']
    elif node == "critique" and "critique_feedback" in node_output:
        return "🧐 Feedback on the revision:\n" + "\n".join([f"- {point}" for point in node_output['critique_feedback']])
    elif node == "decision" and "revise_again" in node_output:
        if node_output["revise_again"]:
            return "🔄 We'll do another round of improvements!"
        else:
            return "✅ No further revision needed. Workflow complete!"
    else:
        return None

# --- Handle pending prompt and streaming workflow ---
if st.session_state.get("processing") and "pending_prompt" in st.session_state:
    user_input = st.session_state.pending_prompt
    # append and display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    # prepare payload
    is_initial = len(st.session_state.messages) == 1
    if is_initial:
        st.session_state.current_draft = user_input
    request_id = str(uuid.uuid4())
    st.session_state.request_id = request_id  # save request ID in session
    endpoint = API_URL if is_initial else FEEDBACK_API_URL
    payload = {"draft": st.session_state.current_draft, "iteration_cap": 3, "request_id": request_id}
    if not is_initial:
        payload["user_feedback"] = user_input
    # stream responses
    try:
        with requests.post(endpoint, json=payload, stream=True, timeout=120) as resp:
            for line in resp.iter_lines():
                if not line:
                    continue
                update = json.loads(line.decode())
                node = update.get("step", next(iter(update.keys())))
                label = node_labels.get(node, node)
                status_msg = f"{label}..."
                st.session_state.messages.append({"role": "assistant", "content": status_msg})
                st.chat_message("assistant").write(status_msg)
                node_output = update.get("node_output", {}).get(node, {})
                formatted = format_node_output(node, node_output)
                if formatted:
                    st.session_state.messages.append({"role": "assistant", "content": formatted})
                    st.chat_message("assistant").write(formatted)
    except Exception as e:
        err = f"⚠️ An error occurred: {e}"
        st.session_state.messages.append({"role": "assistant", "content": err})
        st.chat_message("assistant").write(err)
    # cleanup
    st.session_state.processing = False
    del st.session_state.pending_prompt

# --- Stop button to cancel the request ---
if st.session_state.get("processing"):
    if st.button("⏹️ Stop"):
        try:
            # send cancel request to the server
            requests.post(CANCEL_URL, json={"request_id": st.session_state.request_id})
            st.session_state.processing = False
            st.success("✅ Request canceled.")
        except Exception as e:
            st.error(f"⚠️ Error canceling request: {e}")
