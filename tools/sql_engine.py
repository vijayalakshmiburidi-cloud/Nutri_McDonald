# tools/sql_engine.py
import pandas as pd
# Import shared assets from our config module
from config.settings import engine, groq_client, track_tokens

def sql_tool(question):
    """
    Generates and executes a MySQL query based on the user's question.
    Includes a 3-attempt self-healing retry loop if an error occurs.
    """
    schema = """menu(menu_category,menu_item,
energy_kcal,protein_g,total_fat_g,
sodium_mg,total_carbs_g,total_sugars_g)
Categories:'Regular Menu','McCafe Menu',
'Breakfast Menu','Gourmet Menu',
'Beverages Menu','Desserts Menu',
'Condiments Menu'"""

    messages = [{
        "role": "user",
        "content": f"""MySQL SELECT query only.
Schema: {schema}
Rules:
1. Raw SQL only — no markdown no backticks
2. Use LIKE '%%text%%' not '%text%'
3. For general selection queries, always include menu_item in the SELECT clause.
4. CRITICAL: For aggregation/count queries (e.g., 'how many', 'total', 'count'), select ONLY the aggregation function (e.g., SELECT COUNT(*) FROM menu...) and do NOT include menu_item unless explicitly asked to group by it.
4. LIMIT 5 unless count query
Question: {question}
SQL:"""
    }]

    for attempt in range(1, 4):
        print(f"[SQL] Attempt {attempt}/3...")

        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            temperature=0,
        )
        track_tokens(response, "SQL")

        sql = (response.choices[0].message.content
               .strip()
               .replace("```sql", "")
               .replace("```", "")
               .strip()
               .rstrip(';'))

        print(f"[SQL] {sql}")

        if not sql or len(sql) < 10:
            messages.append({
                "role": "assistant",
                "content": sql
            })
            messages.append({
                "role": "user",
                "content": "Empty response! Write SQL now!"
            })
            continue

        try:
            result = pd.read_sql(sql, engine)
            if result.empty:
                messages.append({
                    "role": "assistant",
                    "content": sql
                })
                messages.append({
                    "role": "user",
                    "content": "0 rows. Use broader LIKE '%%text%%'"
                })
                continue

            print(f"[SQL] ✅ Success attempt {attempt}!")
            return result.to_string(index=False)

        except Exception as e:
            messages.append({
                "role": "assistant",
                "content": sql
            })
            messages.append({
                "role": "user",
                "content": f"Error:{e}\nFix and retry!"
            })

    return "Agent Error: SQL failed after 3 attempts."
