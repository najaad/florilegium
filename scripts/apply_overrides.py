#!/usr/bin/env python3
"""
Apply overrides to goodreads_enriched.csv before data preparation.
Loads override.json and updates specific book fields.
"""

import pandas as pd
import json
from typing import Dict, Any

def load_overrides(overrides_file: str = 'scripts/override.json') -> Dict[str, Any]:
    """Load overrides from JSON file."""
    try:
        with open(overrides_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('book_overrides', {}).get('overrides', [])
    except FileNotFoundError:
        print(f"📁 Override file not found: {overrides_file}")
        return []
    except Exception as e:
        print(f"❌ Error loading overrides: {e}")
        return []

def apply_overrides_to_csv(csv_path: str = 'data/goodreads_enriched.csv'):
    """
    Apply book overrides to the enriched CSV file.
    """
    print("🔧 Applying book overrides...")
    
    # Load overrides
    overrides = load_overrides()
    
    if not overrides:
        print("📂 No overrides found to apply")
        return
    
    print(f"📋 Found {len(overrides)} overrides to apply")
    
    # Load the CSV
    try:
        df = pd.read_csv(csv_path)
        print(f"📖 Loaded CSV with {len(df)} books")
    except FileNotFoundError:
        print(f"❌ Could not load {csv_path}")
        return
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return
    
    applied_count = 0
    
    # Apply each override
    for override in overrides:
        title = override.get('title', '').strip()
        author = override.get('author', '').strip() 
        fields = override.get('fields', {})
        note = override.get('note', '')
        
        if not title:
            continue
            
        # Find matching books by title (and author if provided)
        matches = []
        for idx, row in df.iterrows():
            row_title = str(row.get('Title', '')).strip()
            row_author = str(row.get('Author', '')).strip()
            
            if title.lower() == row_title.lower():
                if not author or author.lower() in row_author.lower():
                    matches.append((idx, row))
        
        if not matches:
            print(f"⚠️  No matching book found for: '{title}'")
            continue
        elif len(matches) > 1:
            print(f"⚠️  Multiple matches for '{title}': {len(matches)} books")
            for idx, row in matches:
                print(f"     {idx}: {row.get('Title', '')} by {row.get('Author', '')}")
            continue
        
        # Apply the overrides to the first/only match
        row_idx = matches[0][0]
        original_row = df.iloc[row_idx].copy()
        
        for field, value in fields.items():
            if field in df.columns:
                # Handle type conversion for numeric fields
                if field == "Read Count" and isinstance(value, str):
                    try:
                        value = int(value)
                    except ValueError:
                        print(f"⚠️  Invalid Read Count: {value} (skipping)")
                        continue
                df.at[row_idx, field] = value
                print(f"✅ Updated '{title}': {field} = {value}")
            else:
                print(f"⚠️  Column not found: {field} (skipping)")
        
        applied_count += 1
        if note:
            print(f"   📝 Note: {note}")
    
    # Save the updated CSV
    if applied_count > 0:
        try:
            df.to_csv(csv_path, index=False)
            print(f"💾 Saved updated CSV with {applied_count} overrides applied")
        except Exception as e:
            print(f"❌ Error saving CSV: {e}")
    else:
        print("ℹ️  No overrides were applied")

if __name__ == "__main__":
    apply_overrides_to_csv()
