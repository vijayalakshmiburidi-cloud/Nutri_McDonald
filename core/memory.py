# core/memory.py
# Import shared assets from our config module
from config.settings import groq_client, track_tokens

def resolve_context_with_memory(question, conversation_history):
    """
    Analyzes the user's question for pronouns. If found, uses the 
    isolated conversation history to rewrite it into a standalone question.
    """
    # Check pronouns first — saves API tokens if none are found!
    pronouns = ["it ", "its ", "that ", "those ", "this ", "they ", "them ", "the same"]
    q_lower  = question.lower() + " "

    has_pronoun = any(p in q_lower for p in pronouns)

    # No pronoun OR no history → skip LLM call entirely!
    if not has_pronoun or not conversation_history:
        return question  # 0 tokens consumed!

    # Has pronoun → resolve using context window
    history_str = ""
    for i, turn in enumerate(conversation_history[-2:], 1):
        history_str += (
            f"Turn {i} - User: {turn['question']}\n"
            f"Agent: {turn['answer'][:150]}...\n"
        )

    prompt = f"""Context Resolver:
Read history and rewrite question to be standalone.
Replace pronouns (it/that/those/its) with actual names.

History:
{history_str}

Question: {question}

Rules:
1. If question is already standalone → return EXACTLY as is!
2. Replace pronouns with actual item/category names
3. Return ONLY the resolved question. Nothing else.

Resolved Question:"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    track_tokens(response, "Resolver")

    resolved = response.choices[0].message.content.strip()

    if resolved != question:
        print(f"🧠 [Memory] '{question}' → '{resolved}'")
    return resolved
