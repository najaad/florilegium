#!/usr/bin/env python3
"""
Manual Genre Assignment Script

This script handles manual genre lookups from manual_genres.json
and updates the enriched CSV with known genre assignments.
"""

import pandas as pd
import json
from typing import List, Dict, Optional

def load_manual_genres(file_path: str = 'scripts/manual_genres.json') -> List[Dict]:
    """Load manual genre assignments from JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data.get('manual_genre_lookups', {}).get('books', [])
    except Exception as e:
        print(f"⚠️  Error loading manual genres: {e}")
        return []

def find_manual_genre(title: str, author: str, isbn13: str, manual_genres: List[Dict]) -> Optional[str]:
    """
    Check if a book exists in manual genre lookup file.
    """
    if not manual_genres:
        return None
    
    title_normalized = title.lower().strip()
    
    for book in manual_genres:
        # Match by ISBN13 first (if provided)	
        if book.get('isbn13') == str(isbn13) and book.get('isbn13'):
            return book.get('genre')
        
        # PRECISE title-only matching (case-insensitive, trimmed)	
        book_title_normalized = book.get('title', '').lower().strip()
        if book_title_normalized == title_normalized:
            print(f"🔍 Manual lookup matched: '{book.get('title')} -> {book.get('genre')}")
            return book.get('genre')

    return None

def apply_manual_genres(csv_path: str = 'data/goodreads_enriched.csv') -> None:
    """
    Apply manual genre assignments to enriched CSV.
    If enriched CSV doesn't exist yet, copy from preprocessed data.
    """
    print("📋 Starting manual genre assignment...")
    
    # Load data - if enriched CSV doesn't exist, copy from preprocessed
    try:
        df = pd.read_csv(csv_path)
        print(f"📖 Loaded existing enriched CSV with {len(df)} books")
    except (FileNotFoundError, Exception):
        print("📖 Enriched CSV not found - copying from preprocessed data...")
        try:
            df = pd.read_csv('data/goodreads_preprocessed.csv').copy()
            # Add Genre column if not present
            if 'Genre' not in df.columns:
                df['Genre'] = ''
            # Save as enriched CSV for next steps
            df.to_csv(csv_path, index=False)
            print(f"📖 Created enriched CSV with {len(df)} books")
        except Exception as e:
            print(f"❌ Error creating enriched CSV: {e}")
            return
    
    manual_genres = load_manual_genres()
    print(f"📋 Loaded {len(manual_genres)} manual genre assignments")
    
    # Track changes
    updated_count = 0
    
    for idx, row in df.iterrows():
        title = str(row.get('Title', '')).strip()
        author = str(row.get('Author', '')).strip()
        isbn13 = str(row.get('ISBN13', '')).strip()
        current_genre = str(row.get('Genre', '')).strip()
        
        # Skip if already has a valid genre
        if current_genre and current_genre not in ['Unknown', 'nan', '']:
            continue
            
        # Try manual lookup
        manual_genre = find_manual_genre(title, author, isbn13, manual_genres)
        if manual_genre:
            df.at[idx, 'Genre'] = manual_genre
            updated_count += 1
            print(f"✅ Updated '{title}' -> '{manual_genre}'")
    
    # Save updated CSV
    try:
        df.to_csv(csv_path, index=False)
        print(f"💾 Updated CSV with {updated_count} manual genre assignments")
        print(f"📊 Final stats:")
        print(f"   📚 Books with genres: {len(df[df['Genre'].notna() & ~(df['Genre'] == 'Unknown')])}")
        print(f"   ❓ Books without genres: {len(df[(df['Genre'].isna()) | (df['Genre'] == 'Unknown')])}")
    except Exception as e:
        print(f"❌ Error saving CSV: {e}")

if __name__ == "__main__":
    apply_manual_genres()
