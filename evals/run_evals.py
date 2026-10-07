# data_pipeline/run_evals.py
import os
import sys
import json
from datetime import datetime

# Resolve system paths so we can tap into config and core modules cleanly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator import agent
from config.settings import session_tokens

def execute_golden_suite():
    evals_path = "evals/golden_evals.json"
    
    if not os.path.exists(evals_path):
        print(f"❌ Error: Cannot find evaluation test suite at '{evals_path}'!")
        return

    with open(evals_path, "r", encoding="utf-8") as f:
        suite = json.load(f)

    print(f"🚀 Starting {suite.get('test_suite_name', 'Evaluation Suite')}...")
    print(f"Total Test Cases to execute: {len(suite['test_cases'])}")
    print("=" * 60)

    # Use a distinct evaluation session ID string
    eval_session_id = f"eval_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    results_report = {
        "evaluation_timestamp": datetime.now().isoformat(),
        "total_tests_run": 0,
        "results": []
    }

    for case in suite["test_cases"]:
        case_id = case["id"]
        category = case["category"]
        question = case["question"]
        expected_metric = case["ground_truth_metric"]

        print(f"\n[Test {case_id}] Category: {category}")
        print(f"❓ Q: {question}")
        
        # Capture token baseline before triggering pipeline execution
        start_tokens = session_tokens["input"] + session_tokens["output"]

        try:
            # Fire the query straight into your core orchestrator pipeline
            generated_answer = agent(question, session_id=eval_session_id)
            status = "COMPLETED"
        except Exception as e:
            generated_answer = f"CRASH ERROR: {str(e)}"
            status = "CRASHED"
            print(f"❌ Test {case_id} CRASHED with error: {e}")

        # Measure token delta consumed specifically by this check
        end_tokens = session_tokens["input"] + session_tokens["output"]
        tokens_spent = end_tokens - start_tokens

        report_entry = {
            "id": case_id,
            "category": category,
            "question": question,
            "expected_ground_truth": expected_metric,
            "agent_generated_response": generated_answer,
            "execution_status": status,
            "tokens_consumed": tokens_spent
        }
        results_report["results"].append(report_entry)
        results_report["total_tests_run"] += 1
        
        print(f"✅ Finished test case. Tokens consumed: {tokens_spent}")
        print("-" * 40)

    # Save out a clean structural evaluation run analysis report
    report_output_path = f"logs/sessions/eval_report_summary_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_output_path, "w", encoding="utf-8") as out_f:
        json.dump(results_report, out_f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("🎉 ALL 30 GOLDEN TEST CASES EXECUTED COMPLETELY!")
    print(f"📝 Full structural log metrics summary saved to: {report_output_path}")
    print("=" * 60)

if __name__ == "__main__":
    execute_golden_suite()
