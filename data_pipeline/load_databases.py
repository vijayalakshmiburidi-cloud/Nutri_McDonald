# data_pipeline/load_to_databases.py
import os
import sys
import pandas as pd
import re

# Resolve our system root configurations path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import engine, collection, embed_model

def format_sql_headers(df):
    """Maps custom column headers to align perfectly with agent_final.py's expected schemas"""
    column_mapping = {
        'menu_category': 'menu_category',
        'menu_items': 'menu_item',          # Maps 'Menu Items' cleanly to 'menu_item'
        'energy__kcal_': 'energy_kcal',     # Maps 'Energy (kCal)' directly to 'energy_kcal'
        'protein__g_': 'protein_g',
        'total_fat__g_': 'total_fat_g',
        'sodium__mg_': 'sodium_mg',
        'total_carbohydrate__g_': 'total_carbs_g', # Maps 'Total carbohydrate (g)' to 'total_carbs_g'
        'total_sugars__g_': 'total_sugars_g'
    }
    
    raw_cleaned = []
    for col in df.columns:
        c = col.lower().strip()
        c = re.sub(r'[^a-z0-9_]', '_', c)
        c = re.sub(r'_+', '_', c).strip('_')
        raw_cleaned.append(c)
    
    df.columns = raw_cleaned
    # Rename specifically targeted columns to match tool schemas
    df = df.rename(columns=column_mapping)
    return df

def push_to_infrastructure():
    clean_csv = "data_pipeline/India_Menu_Clean.csv"
    
    if not os.path.exists(clean_csv):
        print(f"❌ Error: Missing '{clean_csv}'. Run clean_dataset.py first!")
        return

    print("🔌 Reading preprocessed dataset...")
    df = pd.read_csv(clean_csv)
    df = format_sql_headers(df)

    # 1. PUSH TO MYSQL
    print("🗄️ Ingesting structured data into MySQL 'menu' table...")
    df.to_sql('menu', con=engine, if_exists='replace', index=False)
    print("✅ MySQL relational database populated successfully!")

    # 2. PUSH TO CHROMADB VECTOR ENGINE
    print("🧠 Generating text context embeddings for ChromaDB vector spaces...")
    documents = []
    metadatas = []
    ids = []

    for idx, row in df.iterrows():
        item = row.get('menu_item', 'Unknown Item')
        cat = row.get('menu_category', 'Regular Menu')
        kcal = row.get('energy_kcal', 0)
        protein = row.get('protein_g', 0)
        fat = row.get('total_fat_g', 0)
        carbs = row.get('total_carbs_g', 0)
        sodium = row.get('sodium_mg', 0)

        narrative_chunk = (
            f"Menu Item: {item} belongs to the category '{cat}'. "
            f"Nutritional profile per portion size: It delivers {kcal} kCal energy, "
            f"{protein}g protein, {fat}g total fat, {carbs}g carbohydrates, and {sodium}mg sodium."
        )
        documents.append(narrative_chunk)
        metadatas.append({"item_name": str(item), "category": str(cat)})
        ids.append(f"id_{idx}")

    embeddings = embed_model.encode(documents).tolist()

    # Flush old indexes to prevent metadata bloating collisions
    try:
        collection.delete(ids=ids)
    except Exception:
        pass

    collection.add(
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print("✅ ChromaDB semantic collection indexes built completely!")
    print("\n🎉 DATABASES REFRESHED AND ALIGNED FOR WORK!")

if __name__ == "__main__":
    push_to_infrastructure()
