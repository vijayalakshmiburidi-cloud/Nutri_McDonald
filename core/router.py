# core/router.py

def route_question(question):
    """
    Examines keywords within the cleaned question to route it 
    to either SQL data extraction, semantic RAG processing, or BOTH.
    """
    q = question.lower()

    sql_kw = [
        "lowest", "highest", "least", "most",
        "minimum", "maximum", "how many", "count",
        "under", "below", "above", "over",
        "less than", "more than", "calories",
        "protein", "fat", "sodium", "carbs",
        "sugar", "top", "healthiest", "lightest",
        "heaviest", "compare", "list all",
        "show all", "which has", "high protein",                   
        "high calorie", "low calorie", "high fat", "low fat"      
    ]
    rag_kw = [
        "tell me", "what is", "describe",
        "explain", "recommend", "suggest",
        "available", "options", "about",
        "like", "difference", "special"
    ]

    sql_score = sum(1 for k in sql_kw if k in q)
    rag_score = sum(1 for k in rag_kw if k in q)

    print(f"[Router] SQL:{sql_score} RAG:{rag_score}", end=" → ")

    if sql_score > 0 and rag_score > 0:
        decision = "BOTH"
    elif sql_score > 0:
        decision = "SQL"
    else:
        decision = "RAG"

    print(f"Decision: {decision}")
    return decision
