#!/usr/bin/env python3
"""
Google Books API Enrichment Script

This script handles API calls to Google Books API for books that 
don't have manual genre assignments.
"""

import pandas as pd
import requests
import time
import os
from typing import Optional

def get_book_genre(isbn13: str, isbn: str, title: str) -> Optional[str]:
    """
    Fetch genre information from Google Books API using ISBN.
    """
    api_key = os.getenv('GOOGLE_BOOKS_API_KEY')
    if not api_key:
        print("Error: GOOGLE_BOOKS_API_KEY environment variable not set")
        return None
        
    # Try ISBN13 first, then ISBN   
    for isbn_to_try in [isbn13, isbn]:
        if not isbn_to_try or isbn_to_try in ['=""="""', '', '=""""', '=""', '="""""', ""]:
            continue
            
        try:
            # Better ISBN cleaning (remove quotes, equals signs, and other characters)
            clean_isbn = isbn_to_try.replace('=""', '').replace('="""', '').replace('="', '').replace('"', '').strip()
            # Remove leading equals if still there
            if clean_isbn.startswith('='):
                clean_isbn = clean_isbn[1:]
            if not clean_isbn:
                continue
                
            print(f"🌐 API lookup: ISBN {clean_isbn} for '{title}'")
            
            # Google Books API request
            url = "https://www.googleapis.com/books/v1/volumes"
            params = {
                'q': f"isbn:{clean_isbn}",
                'key': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('items') and len(data['items']) > 0:
                    book = data['items'][0]
                    volume_info = book.get('volumeInfo', {})
                    categories = volume_info.get('categories', [])
                    
                    if categories:
                        # Use the first category, clean it up
                        genre = categories[0]
                        # Remove common prefixes like "Fiction" -> just keep the specific genre
                        if '/' in genre:
                            # Take the most specific (rightmost) part
                            genre = genre.split('/')[-1].strip()
                        return genre
            
            # If not found with ISBN, try title search
            print(f"📝 ISBN failed, trying title search for '{title}'")
            params = {
                'q': f'intitle:{title}',
                'key': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if data.get('items') and len(data['items']) > 0:
                    book = data['items'][0]
                    volume_info = book.get('volumeInfo', {})
                    categories = volume_info.get('categories', [])
                    
                    if categories:
                        genre = categories[0]
                        if '/' in genre:
                            genre = genre.split('/')[-1].strip()
                        print(f"✅ Found genre via title: '{genre}'")
                        return genre
                        
        except Exception as e:
            print(f"❌ Error fetching data for ISBN {clean_isbn}: {e}")
            continue
    
    print(f"⚠️  No genre found for '{title}'")
    return None

def is_valid_genre(genre: str) -> bool:
    """Check if a genre string is valid (not empty/unknown/nan)."""
    if pd.isna(genre) or not genre or str(genre).lower().strip() in ['unknown', 'nan', 'none', '']:
        return False
    return len(str(genre).strip()) > 0

def enrich_with_api(csv_path: str = 'data/goodreads_enriched.csv') -> None:
    """
    Apply Google Books API enrichment to books without manual genres.
    """
    print("🌐 Starting Google Books API enrichment...")
    
    try:
        df = pd.read_csv(csv_path)
        print(f"📖 Loaded {len(df)} books")
    except FileNotFoundError:
        print("❌ Enriched CSV does not exist. Run manual_genres.py first to create it.")
        return
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return
    
    # Find books that need enrichment by excluding books with valid genres first
    # Don't include anything we already assigned genres to in manual_genres.py
    def is_invalid_genre(genre_str: str) -> bool:
        if pd.isna(genre_str) or str(genre_str).strip() == '':
            return True
        genre_normalized = str(genre_str).lower().strip()
        return genre_normalized in ['unknown', 'nan', 'none', '']
    
    # Apply this filter to find only books that still need API enrichment
    needs_enrichment = df[df['Genre'].apply(is_invalid_genre)].copy()
    
    print(f"🔍 Found {len(needs_enrichment)} books needing API enrichment")

    # DEBUG: Print sample genre status (commented out for performance):
    # check_sample = df.head(20)
    # print(f"\nSample Genre Check before enrichment:")
    # for idx, row in check_sample.iterrows(): 
    #     genre_val = str(row['Genre']) 
    #     is_inv = is_invalid_genre(genre_val)
    #     print(f"'{row['Title'][:20]}..' = '{genre_val}' (invalid={is_inv})")
    # print()
    
    # Final double-check personal archives allowed already
    valid_enrich_targets = []
    
    for idx, row in needs_enrichment.iterrows():
        genre_str = row['Genre']
        if is_invalid_genre(genre_str):
            valid_enrich_targets.append((idx, row))
            # Optionally print only for first 5 books or keep debug off)
            # print(f"Going to enrich: '{row['Title']}' ({row.get('Genre', 'NaN')})")
        else:
            # Additional book that must be already valid - log only if called
            pass  
    
    if len(valid_enrich_targets) == 0:
        print(f"✨ All books already have valid genres! API_SKIPPING.")
        return
    
    # Show the user which books need API enrichment
    print(f"\n📋 Books that need Google Books API enrichment:")
    print(f"   Total: {len(valid_enrich_targets)} books")
    print("=" * 60)
    for i, (idx, row) in enumerate(valid_enrich_targets):
        author = str(row.get('Author', 'Unknown Author')).strip()
        title = str(row.get('Title', 'Unknown Title')).strip()
        current_genre = str(row.get('Genre', 'Unknown')).strip()
        isbn13 = str(row.get('ISBN13', 'N/A')).strip()
        print(f"{i+1:2d}. '{title}' by {author} (ISBN13: {isbn13}, Genre: {current_genre})")
        
        print("=" * 60)
        print(f"\n💰 This will make {len(valid_enrich_targets)} API calls to Google Books API.")
        print("🤖 Auto-continuing with Google Books API enrichment...")
        
        # Auto-continue for non-interactive environments
        response = 'yes'
        
    actually_needs_api = df.iloc[[x[0] for x in valid_enrich_targets]]
    
    updated_count = 0
    api_calls_made = 0
        
    for idx, row in actually_needs_api.iterrows():
        title = str(row.get('Title', '')).strip()
        isbn13 = str(row.get('ISBN13', '')).strip()
        isbn = str(row.get('ISBN', '')).strip()
        current_genre = str(row.get('Genre', '')).strip()
        
        if not title:
            continue
            
        print(f"🔍 Processing: '{title}'")
        
        # Try API lookup
        api_genre = get_book_genre(isbn13, isbn, title)
        api_calls_made += 1
        
        if api_genre:
            df.at[idx, 'Genre'] = api_genre
            updated_count += 1
            print(f"✅ Updated '{title}' -> '{api_genre}'")
        else:
            print(f"❌ No genre found for '{title}'")
        
        # Rate limiting
        time.sleep(0.1)
    
    # Save results
    try:
        df.to_csv(csv_path, index=False)
        print(f"📊 Enrichment Summary:")
        print(f"   🌐 API calls made: {api_calls_made}")
        print(f"   ✅ Books updated: {updated_count}")
        print(f"   📚 Total books with genres: {len(df[df['Genre'].notna() & ~(df['Genre'].astype(str).str.lower().str.strip().isin(['unknown', 'nan', 'none']))])}")
        print(f"   ❓ Books still without genres: {len(df) - len(df[df['Genre'].notna() & ~(df['Genre'].astype(str).str.lower().str.strip().isin(['unknown', 'nan', 'none']))])}")
    except Exception as e:
        print(f"❌ Error saving CSV: {e}")

if __name__ == "__main__":
    import sys
    sys.path.append('.')
    
    # Run enrichment
    enrich_with_api()
