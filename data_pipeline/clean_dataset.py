# data_pipeline/clean_dataset.py
import pandas as pd
import numpy as np

def run_cleaning_pipeline():
    print("📖 Loading raw dataset: India_Menu.csv...")
    df = pd.read_csv("data_pipeline/India_Menu.csv")

    print("\n=== STAGE 1: INITIAL ANALYSIS ===")
    print(f"Total rows: {len(df)} | Total columns: {len(df.columns)}")
    
    # Fix 1 — Split serve size
    df['Serve Size Value'] = df['Per Serve Size'].str.extract(r'([\d.]+)').astype(float)
    df['Serve Size Unit'] = df['Per Serve Size'].str.extract(r'([a-zA-Z]+)')
    print("✅ Serve size parsing split complete!")

    # Fix 2 — Fill missing sodium using category means
    gourmet_avg = df[df['Menu Category'] == 'Gourmet Menu']['Sodium (mg)'].mean()
    df['Sodium (mg)'] = df['Sodium (mg)'].fillna(round(gourmet_avg, 2))
    print(f"✅ Missing sodium fields populated with mean: {gourmet_avg:.2f}")

    # Fix 3 — Clean special trademark typography characters
    df['Menu Items'] = df['Menu Items'].str.replace('™', '', regex=False)
    df['Menu Items'] = df['Menu Items'].str.replace('®', '', regex=False)
    df['Menu Items'] = df['Menu Items'].str.strip()
    print("✅ Special branding characters stripped successfully!")

    # Fix 4 — Address the shifted metadata on Row 27 (5 piece Chicken Strips)
    mask = df['Menu Items'] == '5 piece Chicken Strips'
    if mask.any():
        idx = df[mask].index[0]
        df.loc[idx, 'Sat Fat (g)'] = 28.54
        df.loc[idx, 'Trans fat (g)'] = 0.15
        df.loc[idx, 'Cholesterols (mg)'] = 75.26
        df.loc[idx, 'Total carbohydrate (g)'] = 6.7
        df.loc[idx, 'Total Sugars (g)'] = 0.73
        df.loc[idx, 'Added Sugars (g)'] = 0.72
        print("✅ Row 27 column shift corrections applied!")

    # Add estimated sodium boolean tracking flag
    df['Sodium_Estimated'] = False
    df.loc[mask, 'Sodium_Estimated'] = True

    # Save out the intermediate artifact
    output_path = "data_pipeline/India_Menu_Clean.csv"
    df.to_csv(output_path, index=False)
    print(f"\n🎉 STAGE 2 Complete: Clean dataset saved to '{output_path}'")

    print("\n=== FINAL DATA QUALITY REPORT ===")
    print(f"Processed Rows: {len(df)}")
    print(f"Remaining Missing values: {df.isnull().sum().sum()}")
    print(f"Negative values detected: {(df.select_dtypes('number') < 0).sum().sum()}")
    print("✅ Dataset preprocessing complete and ready for ingestion!")

if __name__ == "__main__":
    run_cleaning_pipeline()
