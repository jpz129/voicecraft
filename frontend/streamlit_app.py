import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:8000/revise/stream"
FEEDBACK_API_URL = "http://127.0.0.1:8000/revise/feedback/stream"

st.set_page_config(page_title="Voicecraft Revision Workflow", layout="wide")
st.title("📝 Voicecraft: Iterative Text Revision Workflow (API Mode)")
st.markdown("Type or paste your draft below and click **Run Revision Workflow** to see step-by-step improvements, critiques, and decisions—streamed live from the FastAPI backend!")

# Initialize session state for draft, feedback, and results
if "current_draft" not in st.session_state:
    st.session_state.current_draft = "This product is amazing and it will definitely make your life better. It's affordable, easy to use, and very stylish so you should buy it."
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "feedback" not in st.session_state:
    st.session_state.feedback = ""

user_draft = st.text_area("Your Draft", height=200, value=st.session_state.current_draft, key="draft_input")
run_button = st.button("Run Revision Workflow 🚦")

if run_button and user_draft.strip():
    st.session_state.current_draft = user_draft
    st.markdown("---")
    st.subheader("🔄 Streaming Workflow Output (from FastAPI):")
    output_box = st.empty()
    final_state = {}
    output_lines = []
    try:
        with requests.post(API_URL, json={"draft": user_draft, "iteration_cap": 3}, stream=True, timeout=120) as resp:
            for line in resp.iter_lines():
                if line:
                    update = json.loads(line.decode("utf-8"))
                    node_name = next(iter(update.keys()))
                    output_lines.append(f"🟢 Step: {node_name}")
                    for node_output in update.values():
                        if isinstance(node_output, dict):
                            final_state.update(node_output)
                    output_lines.append(json.dumps(update, indent=2))
                    output_lines.append("—" * 40)
                    output_box.code("\n".join(output_lines))
                    # Show the workflow state after each step
                    st.markdown(f"**Workflow State after `{node_name}` step:**")
                    st.code(json.dumps(final_state, indent=2), language="json")
    except Exception as e:
        st.error(f"Error streaming from API: {e}")
        st.stop()

    result = final_state if final_state else None
    st.session_state.last_result = result
    st.session_state.current_draft = result.get("revised_text", user_draft) if result else user_draft
    st.session_state.feedback = ""
    st.markdown("---")
    st.subheader("🏁 Final Result")
    st.code(json.dumps(result, indent=2))
    st.markdown("**Original Draft:**")
    st.write(user_draft)
    st.markdown("**Final Revision Plan:**")
    if result and result.get("revision_plan"):
        for step in result["revision_plan"]:
            st.write(f"🔹 {step}")
    st.markdown("**Final Revised Text:**")
    st.write(result.get("revised_text", "No revised text available") if result else "No revised text available")
    st.markdown("**Final Critique Feedback:**")
    if result and result.get("critique_feedback"):
        for point in result["critique_feedback"]:
            st.write(f"💡 {point}")
    st.markdown("**Final Decision (Should Revise Again?):**")
    if result:
        if result.get('revise_again') is True:
            st.success("🔁 The workflow decided: Revise again! (Looping back to plan node, unless iteration cap is reached)")
        elif result.get('revise_again') is False:
            st.info("✅ The workflow decided: No further revision needed. Workflow complete!")
        else:
            st.warning("⚠️ Unable to determine decision from workflow output.")

st.markdown("---")
st.subheader("💬 Provide Feedback for Further Revision")
feedback = st.text_area("What else would you like to change? (Optional)", value=st.session_state.feedback, key="feedback_input")
feedback_button = st.button("Submit Feedback and Rerun Workflow 🔄")

# Always use the latest revised text as the draft for feedback rounds
current_draft = st.session_state.current_draft

if feedback_button and feedback.strip():
    st.session_state.feedback = feedback
    st.markdown("---")
    st.subheader("🔄 Streaming Feedback Workflow Output (from FastAPI):")
    feedback_output_box = st.empty()
    feedback_final_state = {}
    feedback_output_lines = []
    try:
        with requests.post(FEEDBACK_API_URL, json={"draft": current_draft, "iteration_cap": 3, "user_feedback": feedback}, stream=True, timeout=120) as resp:
            for line in resp.iter_lines():
                if line:
                    update = json.loads(line.decode("utf-8"))
                    node_name = next(iter(update.keys()))
                    feedback_output_lines.append(f"🟢 Step: {node_name}")
                    for node_output in update.values():
                        if isinstance(node_output, dict):
                            feedback_final_state.update(node_output)
                    feedback_output_lines.append(json.dumps(update, indent=2))
                    feedback_output_lines.append("—" * 40)
                    feedback_output_box.code("\n".join(feedback_output_lines))
                    # Show the workflow state after each step
                    st.markdown(f"**Workflow State after `{node_name}` step:**")
                    st.code(json.dumps(feedback_final_state, indent=2), language="json")
    except Exception as e:
        st.error(f"Error streaming from API: {e}")
        st.stop()

    feedback_result = feedback_final_state if feedback_final_state else None
    st.session_state.last_result = feedback_result
    st.session_state.current_draft = feedback_result.get("revised_text", current_draft) if feedback_result else current_draft
    st.session_state.feedback = ""
    st.markdown("---")
    st.subheader("🏁 Final Result After Feedback")
    st.code(json.dumps(feedback_result, indent=2))
    st.markdown("**Original Draft:**")
    st.write(current_draft)
    st.markdown("**Final Revision Plan:**")
    if feedback_result and feedback_result.get("revision_plan"):
        for step in feedback_result["revision_plan"]:
            st.write(f"🔹 {step}")
    st.markdown("**Final Revised Text:**")
    st.write(feedback_result.get("revised_text", "No revised text available") if feedback_result else "No revised text available")
    st.markdown("**Final Critique Feedback:**")
    if feedback_result and feedback_result.get("critique_feedback"):
        for point in feedback_result["critique_feedback"]:
            st.write(f"💡 {point}")
    st.markdown("**Final Decision (Should Revise Again?):**")
    if feedback_result:
        if feedback_result.get('revise_again') is True:
            st.success("🔁 The workflow decided: Revise again! (Looping back to plan node, unless iteration cap is reached)")
        elif feedback_result.get('revise_again') is False:
            st.info("✅ The workflow decided: No further revision needed. Workflow complete!")
        else:
            st.warning("⚠️ Unable to determine decision from workflow output.")
