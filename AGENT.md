# 🤖 SYSTEM RULES & ARCHITECTURE FILE FOR AI COLLABORATORS

## 🚨 SYSTEM CRITICAL CONSTRAINT (DO NOT VIOLATE)
* **Zero Global State History:** `conversation_history = []` must NEVER be instantiated at the module level.
* **Session Isolation Requirement:** All tracking variables (`turns`, `history`) must remain strictly isolated to the incoming local `session_id` argument to prevent concurrent state leaks between multi-device users.

## 📂 Project Directory Architecture
* `config/settings.py` -> Manages global connections (`create_engine`), models (`groq_client`), and internal token counting trackers.
* `data_pipeline/` -> `clean_dataset.py` processes raw files to `India_Menu_Clean.csv`. `load_to_databases.py` populates relational and vector databases.
* `tools/` -> `sql_engine.py` handles the self-healing 3-attempt SQL execution loop. `rag_engine.py` queries ChromaDB vectors.
* `core/` -> `memory.py` resolves pronoun dependencies. `router.py` classifies keywords. `orchestrator.py` handles user logs and executes tools.
* `main_UI.py` -> Root Gradio interface file using `gr.State` to generate dynamic UUID tokens per browser connection stream.

## 🔄 AI Function Signatures
* **Backend Pipeline:** `def agent(user_input, session_id=None):` inside `core/orchestrator.py`.
* **Interface Mapper:** `def chat(message, history, session_id):` inside `main_UI.py`.
* **Positional Execution Order:** The UI functions must pass variables positionally: `agent(clean_message, session_id)`.

## 🛡️ Intent Classification Scope Gates
* Before running vector metrics or text generation models, evaluate `user_input` against general conversational phrases. 
* If a query falls completely outside of food menu properties (e.g. asking for scripts or general knowledge facts), immediately intercept the loop with `OUT_OF_SCOPE` routing and return the custom string: *"I do not have that information in my current menu dataset..."* using 0 active LLM API tokens.
