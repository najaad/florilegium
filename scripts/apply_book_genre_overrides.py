#!/usr/bin/env python3
"""
Apply book-specific genre overrides to goodreads_enriched.csv
This script runs after enrichment but before data_prep.py to ensure 
all genre assignments are finalized at the source level.
"""

import pandas as pd
import json
import os
from typing import Dict, List, Any, Optional


def load_book_genre_overrides(overrides_file: str = 'scripts/book_genre_overrides.json') -> List[Dict[str, Any]]:
    """Load book-specific genre overrides from JSON file."""
    try:
        with open(overrides_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('book_genre_overrides', {}).get('overrides', [])
    except FileNotFoundError:
        print(f"📁 Book genre overrides file not found: {overrides_file}")
        return []
    except Exception as e:
        print(f"❌ Error loading book genre overrides: {e}")
        return []


def match_book(title: str, author: str, override: Dict[str, Any]) -> bool:
    """Check if a book matches the override criteria."""
    override_title = override.get('title', '').lower().strip()
    override_author = override.get('author', '').lower().strip()
    
    # Clean our data
    book_title = str(title).lower().strip()
    book_author = str(author).lower().strip()
    
    # Exact title match
    if override_title == book_title:
        # If author specified in override, check that too
        if override_author:
            return override_author in book_author or book_author in override_author
        return True
    
    # Partial title match (for titles that might have different punctuation)
    if override_title in book_title or book_title in override_title:
        if override_author:
            return override_author in book_author or book_author in override_author
        return True
    
    return False


def apply_book_genre_overrides_to_csv(csv_path: str = 'data/goodreads_enriched.csv') -> None:
    """
    Apply book-specific genre overrides directly to the CSV file.
    This ensures the source data is already correctly categorized.
    """
    print("🔧 Applying book-specific genre overrides to CSV...")
    
    # Load overrides
    book_overrides = load_book_genre_overrides()
    
    if not book_overrides:
        print("📂 No book-specific genre overrides found to apply")
        return
    
    # Load the CSV
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return
    
    try:
        df = pd.read_csv(csv_path)
        print(f"📖 Loaded CSV with {len(df)} books")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return
    
    applied_count = 0
    
    # Apply overrides to each book in CSV
    for idx, row in df.iterrows():
        book_title = str(row.get('Title', '')).strip()
        book_author = str(row.get('Author', '')).strip()
        
        # Check if this book matches any override
        for override in book_overrides:
            if match_book(book_title, book_author, override):
                # Apply the override
                old_genre = str(row.get('Genre', '')).strip()
                new_genre = override.get('genre', 'Unknown').strip()
                
                df.at[idx, 'Genre'] = new_genre
                applied_count += 1
                print(f"  ✅ Updated '{book_title}' by {book_author}: {old_genre} -> {new_genre}")
                break  # Only match one override per book
    
    if applied_count > 0:
        # Save updated CSV
        try:
            df.to_csv(csv_path, index=False)
            print(f"💾 Saved CSV with {applied_count} book-specific genre overrides applied")
        except Exception as e:
            print(f"❌ Error saving updated CSV: {e}")
    else:
        print("📊 No book-specific genre overrides matched in CSV")


def main():
    """Main execution function."""
    print("🚀 Applying book-specific genre overrides to enriched CSV...")
    apply_book_genre_overrides_to_csv()
    print("✅ Book-specific genre overrides completed")


if __name__ == "__main__":
    main()
