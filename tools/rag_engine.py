# tools/rag_engine.py
# Import shared assets from our config module
from config.settings import collection, embed_model, groq_client, track_tokens

def rag_tool(question, sql_context=None):
    """
    Queries ChromaDB vectors to find relevant menu background details,
    combines them with any exact SQL data, and formats a natural answer.
    """
    # Generate embeddings for the question
    q_vector = embed_model.encode([question]).tolist()
    
    # Query the database for the top 2 matches
    results = collection.query(
        query_embeddings=q_vector,
        n_results=2
    )

    chunks = results['documents'][0] if results['documents'] else []
    context = "\n---\n".join(chunks)

    full_context = f"Menu Info:\n{context}"
    if sql_context:
        full_context += f"\n\nExact Data:\n{sql_context}"

    prompt = f"""McDonald's India assistant.
Context: {full_context}
Rules: Use exact numbers. 2-3 sentences only.
Q: {question}
A:"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    track_tokens(response, "RAG")

    return response.choices[0].message.content.strip()
