# core/orchestrator.py
import os
import json
from datetime import datetime

# Import core settings and token metrics utilities
from config.settings import session_tokens, logger

# Import cognitive modules
from core.memory import resolve_context_with_memory
from core.router import route_question

# Import backend tools
from tools.sql_engine import sql_tool
from tools.rag_engine import rag_tool

def agent(user_input, session_id=None):
    """
    The Main Orchestrator Pipeline. It dynamically coordinates session file paths, 
    memory resolution, routing classification checks, and multi-tool execution chains.
    """
    # Ensure fallback identity exists if no session ID is passed (e.g. terminal runs)
    if not session_id:
        session_id = "local_standalone_run"

    # 1. ORCHESTRATE SESSION LOG ISOLATION PATHS
    os.makedirs("logs/sessions", exist_ok=True)
    session_file = f"logs/sessions/session_{session_id}.json"

    # Load session log data strictly tied to this isolated instance ID
    if os.path.exists(session_file):
        with open(session_file, "r", encoding="utf-8") as f:
            session_data = json.load(f)
    else:
        session_data = {
            "session_id" : session_id,
            "start_time" : datetime.now().isoformat(),
            "end_time"   : None,
            "total_turns": 0,
            "token_usage": {"input": 0, "output": 0, "total": 0},
            "turns": []
        }

    # Extract dynamic user history array locally
    conversation_history = session_data["turns"]

    print(f"\n{'='*50}")
    print(f"👤 You: {user_input}")

    # Capture start snapshots for token evaluation metrics
    start_input  = session_tokens["input"]
    start_output = session_tokens["output"]

    # 2. ORCHESTRATE INTENT BARRIER (Blocks out-of-scope/general knowledge queries)
    clean_q = user_input.strip().lower()
    is_general_q = True
    
    # Check if the query is relevant to the dataset
    menu_keywords = ["menu", "burger", "wrap", "mccafe", "beverage", "dessert", "calorie", "protein", "fat", "sodium", "carb", "sugar", "item", "food", "drink", "eat", "price"]
    
    # Check keyword lists first before triggering deep routing logic
    if any(kw in clean_q for kw in menu_keywords) or route_question(user_input) in ["SQL", "BOTH"]:
        is_general_q = False

    if is_general_q:
        decision = "OUT_OF_SCOPE"
        answer = "I do not have that information in my current menu dataset. Please ask about McDonald's India menu items, nutrition data, or category recommendations!"
    else:
        # Step A: Resolve pronouns using this dynamic user's isolated history array
        resolved = resolve_context_with_memory(user_input, conversation_history)

        # Step B: Route question
        decision = route_question(resolved)

        # Step C: Execute right tool pipeline matching layout
        if decision == "SQL":
            sql_ans = sql_tool(resolved)
            if "Agent Error" in sql_ans:
                answer = sql_ans
            elif any(w in resolved.lower() for w in ["how many", "count", "total"]):
                answer = sql_ans
            else:
                answer = rag_tool(resolved, sql_context=sql_ans)
                
        elif decision == "RAG":
            answer = rag_tool(resolved)
            
        else: # BOTH Execution Flow Chain
            sql_ans = sql_tool(resolved)
            answer  = rag_tool(resolved, sql_context=sql_ans)

    print(f"\n🤖 Answer:\n{answer}")

    # 3. ORCHESTRATE STATS & METRICS LOGGING
    current_turn_input  = session_tokens["input"] - start_input
    current_turn_output = session_tokens["output"] - start_output
    turn_tokens = {
        "input" : current_turn_input,
        "output": current_turn_output,
        "total" : current_turn_input + current_turn_output
    }

    # Save turn details to our local isolated structure arrays
    new_turn = {
        "turn_number"      : len(conversation_history) + 1,
        "timestamp"        : datetime.now().isoformat(),
        "original_question": user_input,
        "resolved_question": user_input if is_general_q else resolved,
        "routing_decision" : decision,
        "answer"           : answer,
        "tokens_used"      : turn_tokens
    }
    
    # Format log schemas
    session_data["turns"].append(new_turn)
    session_data["total_turns"] = len(session_data["turns"])
    session_data["token_usage"]["input"]  += turn_tokens["input"]
    session_data["token_usage"]["output"] += turn_tokens["output"]
    session_data["token_usage"]["total"]  += turn_tokens["total"]
    session_data["end_time"] = datetime.now().isoformat()

    # Save tracking data to disk instantly
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)
    print(f"📁 Session saved: {session_file}")

    return answer
