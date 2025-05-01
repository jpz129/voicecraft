import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:8000/revise/stream"

st.set_page_config(page_title="Voicecraft Revision Workflow", layout="wide")
st.title("📝 Voicecraft: Iterative Text Revision Workflow (API Mode)")
st.markdown("Type or paste your draft below and click **Run Revision Workflow** to see step-by-step improvements, critiques, and decisions—streamed live from the FastAPI backend!")

user_draft = st.text_area("Your Draft", height=200, value="This product is amazing and it will definitely make your life better. It's affordable, easy to use, and very stylish so you should buy it.")
run_button = st.button("Run Revision Workflow 🚦")

if run_button and user_draft.strip():
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
    except Exception as e:
        st.error(f"Error streaming from API: {e}")
        st.stop()

    result = final_state if final_state else None
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
