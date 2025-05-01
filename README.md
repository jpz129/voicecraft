# Voicecraft: Iterative Text Revision Workflow

Welcome to Voicecraft! This project is an advanced, modular workflow for iterative text revision, critique, and improvement, powered by LLMs and LangGraph. Below you'll find an overview of the current system, its structure, and how it works.

## 🚦 What is Voicecraft?
Voicecraft is a framework for:
- Generating revision plans for user drafts
- Revising text based on those plans
- Critiquing the revised text
- Deciding whether to loop for further improvement (with a configurable iteration cap)
- Streaming step-by-step progress for transparency and debugging

## 🗂️ Project Structure
- **app/core/nodes/**: Modular nodes for each workflow step (plan, revise, critique, decision, etc.)
- **app/core/prompts/**: Prompt templates for each node, designed for LLMs
- **app/models/schemas.py**: Pydantic models for structured state and node outputs
- **app/core/graph.py**: (If present) Graph construction logic
- **experiments/**: Scripts to run and test the workflow, including streaming and iteration cap
- **frontend/**: Streamlit app for interactive use (if enabled)
- **services/**, **retrieval/**, **scripts/**: Additional utilities and integrations

## 🛠️ Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jpz129/voicecraft
   cd voicecraft
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(This will install LangGraph, LangChain, Pydantic, Hugging Face Hub, Streamlit, and other LLM workflow dependencies.)*

4. **Set up environment variables:**
   - Copy `.env.example` to `.env` (if present) and fill in your Hugging Face API key and endpoint:
     ```bash
     cp .env.example .env
     # Then edit .env to set HF_ENDPOINT_URL and HUGGINGFACEHUB_API_TOKEN
     ```
   - Or create `.env` manually with:
     ```env
     HF_ENDPOINT_URL=your-hf-endpoint-url
     HUGGINGFACEHUB_API_TOKEN=your-hf-api-token
     ```

5. **(Optional) Run the Streamlit frontend:**
   ```bash
   streamlit run frontend/streamlit_app.py
   ```
   *(This launches the interactive web UI if you want to use it.)*

## 🤖 Model & Endpoint
- This project is currently configured to use the `mistral-7b-instruct-v0-3-cik` model via a Hugging Face Inference Endpoint.
- **You can use any Hugging Face Inference Endpoint you have set up**—just set the `HF_ENDPOINT_URL` and `HUGGINGFACEHUB_API_TOKEN` in your `.env` file.

## 🔄 How the Workflow Operates
1. **User provides a draft** (e.g., a product pitch)
2. **plan_node**: Generates a revision plan
3. **revise_node**: Revises the text according to the plan
4. **critique_node**: Provides actionable feedback on the revision
5. **decision_node**: Decides if another revision cycle is needed
6. **Loop**: If needed, the workflow loops back to planning (up to a max of 3 iterations)
7. **Streaming**: Each step is streamed and printed in real time for transparency

## 🚀 FastAPI Integration

Voicecraft now includes a modular FastAPI backend for scalable, production-ready API access to the revision workflow.

### How to Run the FastAPI App

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000)

### API Endpoints
- `POST /revise` — Run the full revision workflow and get the result as JSON.
- `POST /revise/stream` — Stream step-by-step workflow updates as JSON lines (for real-time feedback in clients).

### Example Request (Python)
```python
import requests
resp = requests.post("http://127.0.0.1:8000/revise", json={"draft": "Your text here", "iteration_cap": 3})
print(resp.json())
```

### Example Streaming Request
```python
import requests
with requests.post("http://127.0.0.1:8000/revise/stream", json={"draft": "Your text here"}, stream=True) as resp:
    for line in resp.iter_lines():
        print(line.decode())
```

### Frontend Integration
- The Streamlit app in `frontend/streamlit_app.py` is now configured to use the FastAPI backend for all workflow execution and streaming.
- You can also build your own frontend or integrate with other services using the API.

## 🧩 Key Features
- **Modular Nodes**: Each step is a reusable, testable component
- **Pydantic State**: All workflow state is validated and structured
- **Iteration Cap**: Prevents infinite loops (default: 3 cycles)
- **Streaming Output**: See each step as it happens, with clear emoji-enhanced printouts
- **Prompt Engineering**: Carefully crafted prompts for each node, with robust output parsing

## 🧪 How to Run an Experiment
Run the main experiment script to see the workflow in action:

```bash
python experiments/test_decision_loop.py
```

You'll see:
- The initial draft
- The revision plan
- The revised text
- Critique feedback
- The decision to revise again or finish
- All steps streamed in real time with clear labels and emojis

## 🛠️ Customization & Next Steps
- **Prompts**: Tweak prompts in `app/core/prompts/` for different writing tasks
- **Iteration Cap**: Change the cap in `route_decision` in `test_decision_loop.py`
- **Add Nodes**: Extend with new nodes (e.g., retrieval, ab testing)
- **Frontend**: Use the Streamlit app for interactive revision (see `frontend/`)

## 🧭 Next Steps & Roadmap

- **Enhance User Feedback Influence:**
  - Currently, user feedback is appended to the planning prompt and influences the revision plan. Next, we want to make user feedback more deeply integrated and influential throughout the workflow, possibly by:
    - Passing user feedback to the revise and critique nodes/prompts as well.
    - Adjusting prompt engineering so feedback is more directly reflected in each step.
    - Experimenting with weighting or prioritizing user feedback in the revision logic.
- **Advanced Feedback Loops:**
  - Allow multi-turn, conversational feedback and revision cycles.
  - Track and display feedback history and its effect on each revision.
- **Better State Visualization:**
  - Continue improving frontend and backend state logging and visualization.
- **Retrieval & AB Testing:**
  - Integrate retrieval-augmented generation and AB testing modules for more robust writing support.
- **Productionization:**
  - Add authentication, rate limiting, and deployment scripts for public or team use.
- **Community & Extensibility:**
  - Make it easy for others to add new nodes, prompts, or workflows.

---

**Voicecraft is a living project!**
- Modular, extensible, and ready for new features.
- Designed for transparency, reliability, and rapid iteration.

_Questions or ideas? Open an issue or start hacking!_
