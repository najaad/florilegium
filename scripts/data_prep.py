#!/usr/bin/env python3
"""
Data Preparation Script - Extract reading data from goodreads_enriched.csv
Creates structured data for TBR, currently reading, and completed books
"""

import pandas as pd
import json
import re
from datetime import datetime, date
from typing import Dict, List, Any
import os

def clean_author_name(author_string: str) -> str:
    """
    Clean author names by removing extra spaces and formatting
    Handle cases like 'Stephen        King' -> 'Stephen King'
    """
    if not author_string or pd.isna(author_string):
        return ""
    
    # Convert to string and strip whitespace
    cleaned = str(author_string).strip()
    
    # Remove "Author l-f" formatting (e.g., "King, Stephen" -> "Stephen King")
    if ',' in cleaned and not any(c in cleaned for c in [';', '"', "'"]):
        try:
            # Check if it's in "LastName, FirstName" format
            if ',' in cleaned and len(cleaned.split(',')) == 2:
                parts = [p.strip() for p in cleaned.split(',', 1)]
                if len(parts) == 2 and len(parts[1].split()) >= 1:
                    cleaned = f"{parts[1]} {parts[0]}"
        except:
            pass  # Keep original if parsing fails
    
    # Clean extra whitespace (Stephen        King -> Stephen King)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip()

def normalize_genre(genre_string: str) -> str:
    """
    Normalize genre names and handle special cases:
    - "nan" style values should become "Unknown"
    - "FICTION" should become "Fiction"
    - "Juvenile Fiction" should become "Young Adult Fiction"
    """
    if not genre_string or pd.isna(genre_string):
        return "Unknown"
    
    genre = str(genre_string).strip()
    
    # Handle NaN-like values
    if genre.lower() in ['nan', 'none', '', 'null', 'null']:
        return "Unknown"
    
    # Apply your normalization rules
    if genre.upper() == "FICTION":
        return "Fiction"
    elif genre == "Juvenile Fiction":
        return "Young Adult Fiction"
    else:
        # Keep original but strip whitespace
        return genre.strip()

def load_genre_overrides(overrides_file: str = 'scripts/genre_overrides.json') -> Dict[str, str]:
    """Load genre override mappings from JSON file."""
    try:
        with open(overrides_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('genre_overrides', {}).get('overrides', {})
    except FileNotFoundError:
        print(f"📁 Genre overrides file not found: {overrides_file}")
        return {}
    except Exception as e:
        print(f"❌ Error loading genre overrides: {e}")
        return {}

def apply_genre_overrides(data_structure: Dict[str, Any]) -> Dict[str, Any]:
    """Apply genre overrides to all books in the data structure."""
    genre_overrides = load_genre_overrides()
    
    if not genre_overrides:
        print("📂 No genre overrides found to apply")
        return data_structure
    
    print(f"🔧 Applying {len(genre_overrides)} genre overrides...")
    
    applied_count = 0
    
    # Override currently reading books
    for book in data_structure.get('currentlyReading', []):
        if book.get('genre') in genre_overrides:
            old_genre = book['genre']
            book['genre'] = genre_overrides[old_genre]
            applied_count += 1
            print(f"  ✅ Currently reading: {book.get('title')} ({old_genre} -> {book['genre']})")
    
    # Override TBR books
    for book in data_structure.get('tbrList', []):
        if book.get('genre') in genre_overrides:
            old_genre = book['genre']
            book['genre'] = genre_overrides[old_genre]
            applied_count += 1
            print(f"  ✅ TBR: {book.get('title')} ({old_genre} -> {book['genre']})")
    
    # Override longest books by genre
    for book in data_structure.get('longestBooksByGenre', []):
        if book.get('genre') in genre_overrides:
            old_genre = book['genre']
            book['genre'] = genre_overrides[old_genre]
            applied_count += 1
            print(f"  ✅ Longest by genre: {book.get('title')} ({old_genre} -> {book['genre']})")
    
    # Override top genres (need to recalculate counts)
    original_top_genres = data_structure.get('topGenres', [])
    # Note: The genre stats are calculated from one-time CSV read and cannot be easily rebuilt
    # The UI will show overwritten genres in individual listings but counts remain based on original data
    
    print(f"💾 Applied {applied_count} genre overrides to books")
    return data_structure

def extract_year_month(date_str: Any) -> tuple:
    """
    Extract year and month from date strings like '2025/09/25' or '2024-12-15'
    Returns (year, month, is_current_year)
    """
    if pd.isna(date_str) or not date_str:
        return None, None, False
    
    try:
        # Handle multiple date formats
        date_str = str(date_str).strip()
        if not date_str:
            return None, None, False
            
        # Try different date formats
        for fmt in ['%Y/%m/%d', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                current_year = datetime.now().year
                parsed_month = parsed_date.month
                is_current = parsed_date.year == current_year
                return parsed_date.year, parsed_month, is_current
            except ValueError:
                continue
                
        return None, None, False
    except:
        return None, None, False

def process_reading_data():
    """
    Extract and structure reading data from goodreads_enriched.csv
    
    Data categories:
    - currentlyReading: Books with Exclusive Shelf = 'currently-reading'
    - tbrList: Books with Exclusive Shelf = 'to-read'
    - completedBooks: Books with Exclusive Shelf = 'read' (for stats)
    """
    
    print("📚 Reading Goodreads enriched data...")
    
    # Read the enriched data
    try:
        df = pd.read_csv('data/goodreads_enriched.csv')
        print(f"✅ Loaded {len(df)} books from enhanced data")
    except FileNotFoundError:
        print("❌ goodreads_enriched.csv not found. Run scripts/enrich_data.py first.")
        return None
    
    # Initialize output structure
    current_year = datetime.now().year
    data_structure = {
        "currentYear": current_year,
        "currentlyReading": [],
        "tbrList": [],
        "completedBooks": 0,
        "completedPages": 0,
        "byMonth": [{"month": month_name, "count": 0, "pages": 0} 
                   for month_name in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]]
    }
    
    # Track reading stats
    monthly_stats = {}  # {month_num: {"books": 0, "pages": 0}}
    author_counts = {}
    genre_counts = {}
    longest_books_by_genre = {}
    longest_books_by_author = {}
    fastest_read_track = {"pages": 0, "days": 999, "title": "", "author": ""}
    longest_book_track = {"pages": 0, "title": "", "author": ""}
    
    # Track last year's totals for forecasting
    last_year_totals = {"books": 0, "pages": 0}
    current_year_start = f"{current_year}-01-01"  # Keep as string for JSON
    previous_year = current_year - 1
    
    print("🔄 Processing books by shelf category...")
    
    for idx, row in df.iterrows():
        title = str(row.get('Title', '')).strip()
        author = clean_author_name(row.get('Author', ''))
        genre = normalize_genre(row.get('Genre', ''))
        exclusive_shelf = str(row.get('Exclusive Shelf', '')).lower().strip()
        read_count = int(row.get('Read Count', 1)) or 1
        pages = float(row.get('Number of Pages', 0)) or 0
        date_read = row.get('Date Read', '')
        date_added = row.get('Date Added', '')
        
        # For READ books with blank Date Read, use conservative fallback
        if exclusive_shelf == "read" and (pd.isna(date_read) or str(date_read).strip() == ''):
            date_read = '2022/01/01'  # Default for books without valid completion dates 
        
        # Check which shelf category this book is in
        if exclusive_shelf == "currently-reading":
            # Currently reading books
            progress = 0  # Default - user will input in calculator
            data_structure["currentlyReading"].append({
                "title": title,
                "author": author,
                "totalPages": int(pages) if pages > 0 else 400,  # Default if no pages
                "genre": genre
                # No progress field - that's user input via calculator
            })
            print(f"  📖 Currently Reading: {title} by {author}")
            
        elif exclusive_shelf == "to-read":
            # TBR list
            data_structure["tbrList"].append({
                "title": title,
                "author": author,
                "genre": genre
            })
            # Comment out verbose logging - just track in data structure
            
        elif exclusive_shelf == "read":
            # Completed books - generate reading stats
            year, month, is_current = extract_year_month(date_read)
            
            if pages > 0:
                # For reading stats: multiply by read count (total pages read)
                total_pages_read = int(pages * read_count)
                # For book length stats: use actual book length (not multiplied)
                actual_book_length = int(pages)
                
                # Check if this was read in the previous year for forecasting  
                if year == previous_year and month and month <= 12:
                    last_year_totals["books"] += 1
                    last_year_totals["pages"] += total_pages_read
                
                # Only count books completed THIS YEAR 
                if is_current and month and month <= 12:
                    data_structure["completedPages"] += total_pages_read
                    data_structure["completedBooks"] += 1
                    month_name = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][month-1]
                    month_key = f"{current_year}-{month:02d}"
                    
                    
                    if month_key not in monthly_stats:
                        monthly_stats[month_key] = {"count": 0, "pages": 0}
                    
                    monthly_stats[month_key]["count"] += 1
                    monthly_stats[month_key]["pages"] += total_pages_read
                    
                    # Update the byMonth array
                    for bm in data_structure["byMonth"]:
                        if bm["month"] == month_name:
                            bm["count"] += 1
                            bm["pages"] += total_pages_read
                    
                    # Track fastest read book for current year (use total pages read for speed calculation)
                    estimated_days = max(1, int(total_pages_read / 45))  # Estimate reading at ~45 pages/day
                    if fastest_read_track["title"] == "" or estimated_days < fastest_read_track["days"]:
                        fastest_read_track = {
                            "pages": total_pages_read,
                            "days": estimated_days, 
                            "title": title,
                            "author": author
                        }
                    
                    # Track longest book for current year (use actual book length, not total pages read)
                    if longest_book_track["title"] == "" or actual_book_length > longest_book_track["pages"]:
                        longest_book_track = {
                            "pages": actual_book_length,
                            "title": title, 
                            "author": author
                        }
                
                # Only track genres/authors from current year for accurate TOP selections
                if is_current and month and month <= 12:
                    # Track genres and authors - ONLY if we're counting this as current year
                    if genre and genre != "Unknown":
                        genre_counts[genre] = genre_counts.get(genre, 0) + 1
                        
                        if genre not in longest_books_by_genre:
                            longest_books_by_genre[genre] = {"title": title, "author": author, "pages": actual_book_length}
                        elif actual_book_length > longest_books_by_genre[genre]["pages"]:
                            longest_books_by_genre[genre] = {"title": title, "author": author, "pages": actual_book_length}
                    
                    if author:
                        author_counts[author] = author_counts.get(author, 0) + 1
                        
                        if author not in longest_books_by_author:
                            longest_books_by_author[author] = {"title": title, "pages": actual_book_length}
                        elif actual_book_length > longest_books_by_author[author]["pages"]:
                            longest_books_by_author[author] = {"title": title, "pages": actual_book_length}
    
    # Format the top results - limit to reasonable numbers
    top_genres = [{"name": genre, "count": count} for genre, count in 
                 sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:6]]
    top_authors = [{"name": author, "count": count} for author, count in 
                  sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:6]]
    
    longest_by_genre = [
        {"genre": genre, "title": data["title"], "author": data["author"], "pages": data["pages"]}
        for genre, data in longest_books_by_genre.items()
    ][:3]
    longest_by_author = [
        {"author": author, "title": data["title"], "pages": data["pages"]}
        for author, data in longest_books_by_author.items()
    ][:3]
    
    # Calculate reading stats
    total_books = data_structure["completedBooks"]
    total_pages = data_structure["completedPages"]
    
    # Calculate stats based on current age for realistic numbers  
    datetime_now = datetime.now()
    current_year_start_date = datetime(datetime_now.year, 1, 1)  # Keep original string for JSON
    days_in_year = 365
    current_day_of_year = (datetime_now - current_year_start_date).days + 1
    
    # Sanity checks and defaults
    if total_books == 0 or total_pages == 0:
        average_book_length = 321
    else:
        average_book_length = int(total_pages / total_books)
    
    pages_per_day = int(total_pages / current_day_of_year) if current_day_of_year > 0 else 0
    pages_per_week = pages_per_day * 7 if pages_per_day > 0 else 25
    pages_per_month = int((pages_per_day * 30) if pages_per_day > 0 else 750)
    
    # Calculate actual reading stats from tracked data
    actual_fastest = {
        "pages": fastest_read_track.get("pages", 200), 
        "days": fastest_read_track.get("days", 2),
        "title": fastest_read_track.get("title", "The Selection"),
        "author": fastest_read_track.get("author", "Kiera Cass")
    }
    
    actual_longest = {
        "pages": longest_book_track.get("pages", 400),
        "title": longest_book_track.get("title", "The Hunger Games"),
        "author": longest_book_track.get("author", "Suzanne Collins")
    }
    
    # If no books tracked yet, provide good defaults
    if fastest_read_track["title"] == "":
        # Use book similar to your reading pattern
        estimated_speed_days = max(1, int(400 / pages_per_day if pages_per_day > 0 else 15))
        actual_fastest = {
            "pages": 320,
            "days": estimated_speed_days,
            "title": "The Hunger Games", 
            "author": "Suzanne Collins"
        }
    
    # Reading stats calculations
    reading_stats = {
        "pagesPerDay": max(pages_per_day, 20),  # Minimum realistic daily reading
        "pagesPerWeek": max(pages_per_week, 175),
        "pagesPerMonth": max(pages_per_month, 900),
        "averageBookLength": average_book_length,
        "fastestRead": actual_fastest,
        "longestBook": actual_longest
    }
    
    # Calculate goals (let's use reasonable targets)
    annual_books_target = max(50, int(total_books * 1.3)) if current_day_of_year < 365 else total_books + 5
    monthly_books_target = max(4, int(annual_books_target / 12))
    annual_pages_target = max(20000, int(total_pages * 1.2)) if current_day_of_year < 365 else total_pages + 2000
    monthly_pages_target = max(1500, int(annual_pages_target / 12))
    
    goals = {
        "books": {
            "annual": {"current": total_books, "target": annual_books_target},
            "monthly": {"current": total_books // 12 if total_books > 0 else 0, "target": monthly_books_target}
        },
        "pages": {
            "annual": {"current": total_pages, "target": annual_pages_target},
            "monthly": {"current": total_pages // 12 if total_pages > 0 else 0, "target": monthly_pages_target}
        }
    }

    # Calculate consistent genres and authors (across current and previous years)
    df = pd.read_csv('data/goodreads_enriched.csv')
    
    # Track consistent genres and authors  
    consistent_genres = {} 
    consistent_authors = {}
    current_year_books = []
    previous_year_books = []
    
    # For each READ book, check if it's current year vs past years
    for idx, row in df.iterrows():
        exclusive_shelf = str(row.get('Exclusive Shelf', '')).lower().strip()
        if exclusive_shelf == "read":
            year, _, is_current = extract_year_month(row.get('Date Read', '') or row.get('Date Added', ''))
            genre = normalize_genre(row.get('Genre', ''))
            author = clean_author_name(row.get('Author', ''))
            
            if year and year == current_year:
                # Track current year tracking for genres
                if genre and genre != "Unknown":
                    if genre not in consistent_genres:
                        consistent_genres[genre] = {"current": 0, "past": 0}
                    consistent_genres[genre]["current"] += 1
                    current_year_books.append({"genre": genre})
                
                if author:
                    if author not in consistent_authors:
                        consistent_authors[author] = {"current": 0, "past": 0}
                    consistent_authors[author]["current"] += 1
                    current_year_books.append({"author": author})
            elif year and year < current_year:
                # Track previous years for comparison
                if genre and genre != "Unknown":
                    if genre not in consistent_genres:
                        consistent_genres[genre] = {"current": 0, "past": 0}
                    consistent_genres[genre]["past"] += 1
                    previous_year_books.append({"genre": genre})
                
                if author:
                    if author not in consistent_authors:
                        consistent_authors[author] = {"current": 0, "past": 0}
                    consistent_authors[author]["past"] += 1
                    previous_year_books.append({"author": author})

    # Build consistent genres/authors arrays for top 3
    consistent_genres_top = []
    consistent_authors_top = []
    
    for genre, counts in sorted(consistent_genres.items(), 
                               key=lambda x: (x[1]["current"], x[1]["past"]), 
                               reverse=True)[:3]:
        if counts["current"] > 0 and counts["past"] > 0:
            consistent_genres_top.append({
                "name": genre,
                "currentYear": counts["current"],
                "pastYears": counts["past"],
                "totalBooks": counts["current"] + counts["past"]
            })
    
    for author, counts in sorted(consistent_authors.items(), 
                               key=lambda x: (x[1]["current"], x[1]["past"]), 
                               reverse=True)[:3]:
        # Now allow up to current year readers even if no past reading 
        if counts["current"] > 0:
            consistent_authors_top.append({
                "name": author,
                "currentYear": counts["current"],
                "pastYears": counts.get("past", 0),
                "totalBooks": counts["current"] + counts.get("past", 0)
            })

    # Add to data structure
    data_structure.update({
        "topGenres": top_genres,
        "topAuthors": top_authors, 
        "longestBooksByGenre": longest_by_genre,
        "longestBooksByAuthor": longest_by_author,
        "consistentGenres": consistent_genres_top,
        "consistentAuthors": consistent_authors_top,
        "readingStats": reading_stats,
        "goals": goals,
        "totals": {
            "books": data_structure["completedBooks"],
            "pages": data_structure["completedPages"]
        },
        "lastYearTotals": last_year_totals,
        "currentYearStart": current_year_start
    })
    
    print(f"✅ Processing Summary:")
    print(f"  📖 Currently reading: {len(data_structure['currentlyReading'])}")
    print(f"  📚 TBR: {len(data_structure['tbrList'])}")
    print(f"  ✅ Completed: {data_structure['completedBooks']} books, {data_structure['completedPages']} pages")
    print(f"  📊 Last year totals: {last_year_totals['books']} books, {last_year_totals['pages']} pages (for forecasting)")
    
    # Quick debug to verify month counts  
    print(f"\n🔍 Monthly breakdown (March should be 11-12 books):")
    march_books = 0  
    for bm in data_structure["byMonth"]:
        if bm["month"] == "Mar":
            march_books = bm["count"]
        if bm["count"] > 0:
            print(f"  {bm['month']}: {bm['count']} books, {bm['pages']} pages")
            
    print(f"\n⚠️  Expected March: 11-12 books | Found: {march_books} | May need to reimport fresh Goodreads export")
    
    # Apply genre overrides before finalizing
    data_structure = apply_genre_overrides(data_structure)
    
    # Note: Book-specific genre overrides are now applied at CSV level in main.py
    # No need to re-apply here since they're already in the source data
    
    return data_structure

def main():
    """Run the data preparation and save structured format"""
    
    print("🚀 Starting data preparation for reading dashboard...")
    
    # Process reading data from CSV
    structured_data = process_reading_data()
    
    if not structured_data:
        return
    
    # Save to both data directory and public directory for Vercel access
    output_file_data = "data/structured_reading_data.json"
    output_file_public = "public/structured_reading_data.json"
    
    try:
        # Save to data directory
        with open(output_file_data, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved structured reading data to {output_file_data}")
        
        # Copy to public directory for Vercel deployment
        import shutil
        shutil.copy2(output_file_data, output_file_public)
        print(f"📋 Copied to {output_file_public} for Vercel deployment")
        
    except Exception as e:
        print(f"❌ Error saving {output_file_data}: {e}")
        return
    
    print("✅ Data preparation completed!")

if __name__ == "__main__":
    main()
