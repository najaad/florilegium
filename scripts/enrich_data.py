import pandas as pd
import requests
import time
import json
import os
from typing import Dict, List, Optional
import numpy as np

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
                
            print(f"Trying ISBN: {clean_isbn} for book: {title}")
            
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
                        # Get the best genre from categories
                        best_genre = None
                        for category in categories:
                            genre = category.split('/')[-1].strip()
                            if genre:
                                best_genre = genre
                                break
                        
                        if best_genre:
                            print(f"Found genre '{best_genre}' for {title}")
                            return best_genre
                        
            elif response.status_code == 429:
                print(f"Rate limited, waiting...")
                time.sleep(2)
                
        except Exception as e:
            print(f"Error fetching genre for {isbn_to_try}: {e}")
            continue
    
    # Final fallback: search by title if all ISBNs failed
    try:
        print(f"No ISBN matches, trying title search for: {title}")
        url = "https://www.googleapis.com/books/v1/volumes"
        params = {
            'q': f'intitle:"{title}"',
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('items') and len(data['items']) > 0:
                # Find book that matches most closely to title
                best_book = None
                for item in data['items']:
                    book_title = item.get('volumeInfo', {}).get('title', '').lower()
                    if title.lower() in book_title or book_title in title.lower():
                        best_book = item
                        break
                
                # If no exact match, take first result
                if not best_book:
                    best_book = data['items'][0]
                
                if best_book:
                    categories = best_book.get('volumeInfo', {}).get('categories', [])
                    
                    if categories:
                        # Get best genre from categories
                        for category in categories:
                            genre = category.split('/')[-1].strip()
                            if genre:
                                print(f"Found genre '{genre}' for {title} via title search")
                                return genre
                                
    except Exception as e:
        print(f"Error in title search for {title}: {e}")
            
    return None

def load_manual_genres():
    """
    Load manual genre assignments from helper JSON file.
    """
    manual_genres_path = 'scripts/manual_genres.json'
    try:
        with open(manual_genres_path, 'r') as f:
            data = json.load(f)
            return data.get('manual_genre_lookups', {}).get('books', [])
    except FileNotFoundError:
        print("ℹ️  No manual_genres.json found - creating empty file")
        with open(manual_genres_path, 'w') as f:
            json.dump({
                "manual_genre_lookups": {
                    "description": "Manual genre assignments for books that failed automated lookup",
                    "books": []
                }
            }, f, indent=2)
        return []
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

def load_or_create_enriched_csv():
    """
    Load existing enriched CSV if it exists, preserving genres from cache.
    If not exists, create from preprocessed data with empty genres.
    """
    if os.path.exists('data/goodreads_enriched.csv'):
        try:
            df_enriched = pd.read_csv('data/goodreads_enriched.csv')
            if not df_enriched.empty and 'Genre' in df_enriched.columns:
                # IMP: Never recreate - always preserve existing enriched data as source of truth
                print(f"📚 PRESERVED existing enriched CSV with {len(df_enriched)} books")
                return df_enriched
        except Exception as e:
            print(f"⚠️  Could not load enriched CSV safely: {e}")
    
    print("📚 Creating NEW enriched CSV from preprocessed file")
    df_preprocessed = pd.read_csv('data/goodreads_preprocessed.csv')
    if 'Genre' not in df_preprocessed.columns:
        df_preprocessed['Genre'] = ''
    df_preprocessed.to_csv('data/goodreads_enriched.csv', index=False)
    return df_preprocessed

def enrich_goodreads_data():
    """
    Enhanced enrichment with caching and manual lookup integration:
    1. Check if book exists in enriched CSV and has genre → skip
    2. If book exists but no genre → check manual lookup first
    3. If book doesn't exist → add to bottom and try genre lookup
    4. Use API as last resort
    """
    print("🧹 Starting smart enrichment with caching...")
    
    # Load data sources
    df_preprocessed = pd.read_csv('data/goodreads_preprocessed.csv')
    df_enriched = load_or_create_enriched_csv()
    manual_genres = load_manual_genres()
    
    print(f"📖 Preprocessed books: {len(df_preprocessed)}")
    print(f"📖 Already enriched books: {len(df_enriched)}")
    print(f"📖 Manual genre lookups: {len(manual_genres)}")
    
    # Build lookup dictionaries for faster searches
    title_to_genre = {}
    isbn_to_genre = {}
    title_to_unknown = set()
    
    if not df_enriched.empty:
        print(f"🔍 Analyzing enriched data for skip logic...")
        for idx, row in df_enriched.iterrows():
            title = str(row.get('Title', '')).lower().strip()
            isbn13 = str(row.get('ISBN13', '')).strip()
            genre = row.get('Genre', '')
            
            if title and pd.notna(genre) and genre:
                if genre != 'Unknown':
                    # Books with real genres: skip if re-processed
                    title_to_genre[title] = genre
                    if isbn13 and isbn13 != 'N/A':
                        isbn_to_genre[isbn13] = genre
                else:
                    # Books with "Unknown" : allow reprocessing
                    title_to_unknown.add(title)
                    print(f"✓ Will reprocess 'Unknown' book: {row.get('Title')}") 
    
    print(f"  Found {len(title_to_genre)} books with real genres")
    print(f"  Found {len(title_to_unknown)} books with Unknown genres")
    
    # Track statistics
    skipped_books = 0
    manual_lookup_success = 0
    api_calls_made = 0
    no_genre_books = []
    
    # Initial stats for reporting
    already_enriched_before = 0
    if not df_enriched.empty:
        already_enriched_before = len(df_enriched[
            df_enriched['Genre'].notna() & 
            (df_enriched['Genre'] != '') & 
            (df_enriched['Genre'] != 'Unknown')
        ])
    
    # Process each preprocessed book
    for idx, row in df_preprocessed.iterrows():
        title_orig = str(row.get('Title', ''))
        author_orig = str(row.get('Author', ''))
        isbn13_orig = str(row.get('ISBN13', '')).strip()
        
        # Skip if ISBN(13) empty 
        if not isbn13_orig or isbn13_orig in ['NaN', 'nan', 'N/A']:
            print(f"⏭️  Skipping {title_orig} - no ISBN")
            continue
        
        title_key = title_orig.lower().strip()
        
        # Look for the book in enriched cache to see what genre it has
        found_existing = False
        current_genre = None
        for enriched_idx, enriched_row in df_enriched.iterrows():
            enriched_title = str(enriched_row.get('Title', '')).lower().strip()
            enriched_isbn13 = str(enriched_row.get('ISBN13', '')).strip()
            
            if enriched_title == title_key or enriched_isbn13 == isbn13_orig:
                found_existing = True
                current_genre = enriched_row.get('Genre', '')
                break
        
        # Check if book has a valid genre and skip if it does 
        def is_valid_genre(g):
            if pd.isna(g) or not g or str(g).lower() in ['nan', 'none', '', 'unknown', 'null']:
                return False
            s = str(g).strip()
            return len(s) > 0 and s.lower() not in ['unknown','nan','none','null']
        
        # CRITICAL: Skip books that already have valid genres in enriched cache
        if found_existing and is_valid_genre(current_genre):
            skipped_books += 1
            continue
            
        # Determine if we need to update or add entry  
        existing_book = None
        if found_existing:
            # Re-locate enriched row index for updating  
            for enriched_idx, enriched_row in df_enriched.iterrows():
                enriched_title = str(enriched_row.get('Title', '')).lower().strip()
                enriched_isbn13 = str(enriched_row.get('ISBN13', '')).strip()
                if enriched_title == title_key or enriched_isbn13 == isbn13_orig:
                    existing_book = enriched_idx
                    break
        
        # Look up genre - ONLY for books that need processing
        genre = 'Unknown'  # Default fallback
        
        # 1. Manual lookup first (fast, no API cost)
        manual_genre = find_manual_genre(title_orig, author_orig, isbn13_orig, manual_genres)
        if manual_genre:
            genre = manual_genre
            manual_lookup_success += 1
        # 2. API only for books that failed manual lookup 
        else:
            # ONLY if no manual match found 
            isbn_val = str(row.get('ISBN', ''))
            api_result = get_book_genre(isbn13_orig, isbn_val, title_orig)
            if api_result:
                genre = api_result
                api_calls_made += 1
        
        # Track failed book lookups
        if genre == 'Unknown':
            no_genre_books.append({
                'title': title_orig,
                'author': author_orig, 
                'isbn13': isbn13_orig,
                'isbn': str(row.get('ISBN', ''))
            })
        
        # Add or update entry in enriched CSV
        if existing_book is None:
            new_row = row.copy()
            new_row['Genre'] = genre
            df_enriched = pd.concat([df_enriched, new_row.to_frame().T], ignore_index=True)
        else:
            df_enriched.at[existing_book, 'Genre'] = genre
        
        # Periodic save to prevent data loss  
        if (idx + 1) % 20 == 0:
            df_enriched.to_csv('data/goodreads_enriched.csv', index=False)
            print(f"💾 Progress: {(idx + 1)/len(df_preprocessed)*100:.1f}% processed")
    
    # Final save
    df_enriched.to_csv('data/goodreads_enriched.csv', index=False)
    
    # Summary
    enriched_with_genre = df_enriched[
        df_enriched['Genre'].notna() & 
        (df_enriched['Genre'] != '') & 
        (df_enriched['Genre'] != 'Unknown')
    ]
    
    newly_enriched = len(enriched_with_genre) - already_enriched_before
    
    print(f"\n📋 ENRICHMENT SUMMARY")
    print(f"="*60)
    print(f"📖 Total preprocessed books: {len(df_preprocessed)}")
    print(f"💾 Already enriched before: {already_enriched_before}")
    print(f"📋 Manual lookups this run: {manual_lookup_success}")
    print(f"🌐 API calls this run: {api_calls_made}")
    print(f"⏭️  Skipped (already enriched): {skipped_books}")
    print(f"✅ Total books with genres now: {len(enriched_with_genre)}")
    print(f"📈 Newly enriched this run: {newly_enriched}")
    print(f"❌ Books still without genres: {len(no_genre_books)}")
    
    if no_genre_books:
        print(f"\n🔍 BOOKS WITHOUT GENRES ({len(no_genre_books)}):")
        print(f"="*60)
        for i, book in enumerate(no_genre_books, 1):
            print(f"{i:2}. '{book['title']}' by {book['author']}")
            if book['isbn13'] != 'N/A': 
                print(f"     ISBN13: {book['isbn13']}")
            if book['isbn'] != 'N/A' and book['isbn'] != book['isbn13']:
                print(f"     ISBN: {book['isbn']}")
            print()
    
    print(f"💾 Enrichment complete! Saved to data/goodreads_enriched.csv")
    
    return df_enriched

def enrich_single_book(title: str, isbn13: str = '', isbn: str = '') -> Dict:
    """
    Enrich a single book for testing.
    """
    genre = get_book_genre(isbn13, isbn, title)
    
    return {
        'title': title,
        'isbn13': isbn13,
        'isbn': isbn,
        'genre': genre or 'Unknown'
    }

# Usage example for testing single book
if __name__ == "__main__":
    # Test with one book first
    test_result = enrich_single_book(
        "The Seven Husbands of Evelyn Hugo",
        "9781501137265",
        "1501137263"
    )
    print("Test result:", test_result)
    
    # Uncomment the next line to enrich all books:
    enrich_goodreads_data()
