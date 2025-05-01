import streamlit as st
from pathlib import Path
import sys
from dotenv import load_dotenv
from pprint import pformat

# Load environment variables
load_dotenv()

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.core.nodes.plan_node import plan_node
from app.core.nodes.critique_node import critique_node
from app.core.nodes.revise_node import revise_node
from app.core.nodes.decision_node import decision_node
from langgraph.graph import StateGraph
from app.models.schemas import WorkflowState

st.set_page_config(page_title="Voicecraft Revision Workflow", layout="wide")
st.title("📝 Voicecraft: Iterative Text Revision Workflow")
st.markdown("Type or paste your draft below and click **Run Revision Workflow** to see step-by-step improvements, critiques, and decisions—streamed live!")

user_draft = st.text_area("Your Draft", height=200, value="This product is amazing and it will definitely make your life better. It's affordable, easy to use, and very stylish so you should buy it.")
run_button = st.button("Run Revision Workflow 🚦")

if run_button and user_draft.strip():
    # Build the graph (same as test_decision_loop.py)
    graph = StateGraph(WorkflowState)
    graph.add_node("plan", plan_node())
    graph.add_node("revise", revise_node())
    graph.add_node("critique", critique_node())
    graph.add_node("decision", decision_node())
    graph.set_entry_point("plan")
    graph.add_edge("plan", "revise")
    graph.add_edge("revise", "critique")
    graph.add_edge("critique", "decision")

    def route_decision(state):
        val = getattr(state, "revise_again", None)
        iteration = getattr(state, "iteration", 0)
        if iteration >= 3:
            return "__end__"
        if val is True:
            return "plan"
        return "__end__"

    graph.add_conditional_edges(
        "decision",
        route_decision,
        {
            "plan": "plan",
            "__end__": "__end__"
        }
    )
    app = graph.compile()
    input_state = {"current_text": user_draft, "iteration": 0}

    st.markdown("---")
    st.subheader("🔄 Streaming Workflow Output:")
    output_box = st.empty()
    final_state = {}
    output_lines = []
    for update in app.stream(input_state, stream_mode="updates"):
        node_name = next(iter(update.keys()))
        output_lines.append(f"🟢 Step: {node_name}")
        for node_output in update.values():
            if isinstance(node_output, dict):
                final_state.update(node_output)
        if "decision" in update:
            final_state["iteration"] = final_state.get("iteration", 0) + 1
        output_lines.append(pformat(update))
        output_lines.append("—" * 40)
        output_box.code("\n".join(output_lines))

    result = final_state if final_state else None
    st.markdown("---")
    st.subheader("🏁 Final Result")
    st.code(pformat(result))
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
