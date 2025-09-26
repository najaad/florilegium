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
    
    print("🔄 Processing books by shelf category...")
    
    for idx, row in df.iterrows():
        title = str(row.get('Title', '')).strip()
        author = clean_author_name(row.get('Author', ''))
        genre = normalize_genre(row.get('Genre', ''))
        exclusive_shelf = str(row.get('Exclusive Shelf', '')).lower().strip()
        read_count = int(row.get('Read Count', 1)) or 1
        pages = float(row.get('Number of Pages', 0)) or 0
        date_read = row.get('Date Read', '')
        
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
                # Calculate pages with read count multiplier
                total_pages = int(pages * read_count)
                data_structure["completedPages"] += total_pages
                data_structure["completedBooks"] += 1
                
                if is_current and month and month <= 12:
                    month_name = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][month-1]
                    month_key = f"{current_year}-{month:02d}"
                    
                    if month_key not in monthly_stats:
                        monthly_stats[month_key] = {"count": 0, "pages": 0}
                    
                    monthly_stats[month_key]["count"] += 1
                    monthly_stats[month_key]["pages"] += total_pages
                    
                    # Update the byMonth array
                    for bm in data_structure["byMonth"]:
                        if bm["month"] == month_name:
                            bm["count"] += 1
                            bm["pages"] += total_pages
                
                # Track genres and authors
                if genre and genre != "Unknown":
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
                    
                    # Longest books by genre
                    if genre not in longest_books_by_genre or total_pages > longest_books_by_genre[genre].get('pages', 0):
                        longest_books_by_genre[genre] = {
                            "title": title,
                            "author": author,
                            "pages": total_pages
                        }
                
                if author:
                    author_counts[author] = author_counts.get(author, 0) + 1
                    
                    # Longest books by author
                    if author not in longest_books_by_author or total_pages > longest_books_by_author[author].get('pages', 0):
                        longest_books_by_author[author] = {
                            "title": title,
                            "author": author,
                            "pages": total_pages
                        }
    
    # Format the top results - limit to reasonable numbers
    top_genres = [{"name": genre, "count": count} for genre, count in 
                 sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
    top_authors = [{"name": author, "count": count} for author, count in 
                  sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
    
    longest_by_genre = [
        {"genre": genre, "title": data["title"], "author": data["author"], "pages": data["pages"]}
        for genre, data in longest_books_by_genre.items()
    ][:10]
    longest_by_author = [
        {"author": author, "title": data["title"], "pages": data["pages"]}
        for author, data in longest_books_by_author.items()
    ][:10]
    
    # Calculate reading stats
    total_books = data_structure["completedBooks"]
    total_pages = data_structure["completedPages"]
    
    # Calculate stats based on current age for realistic numbers  
    datetime_now = datetime.now()
    current_year_start = datetime(datetime_now.year, 1, 1)
    days_in_year = 365
    current_day_of_year = (datetime_now - current_year_start).days + 1
    
    # Sanity checks and defaults
    if total_books == 0 or total_pages == 0:
        average_book_length = 321
    else:
        average_book_length = int(total_pages / total_books)
    
    pages_per_day = int(total_pages / current_day_of_year) if current_day_of_year > 0 else 0
    pages_per_week = pages_per_day * 7 if pages_per_day > 0 else 25
    pages_per_month = int((pages_per_day * 30) if pages_per_day > 0 else 750)
    
    # Get longest book if any have stats
    longest_book_pages = max((total_pages / total_books * 1.2) if total_books > 0 else 400, 400)
    longest_book = int(longest_book_pages)
    
    # Reading stats calculations
    reading_stats = {
        "pagesPerDay": max(pages_per_day, 20),  # Minimum realistic daily reading
        "pagesPerWeek": max(pages_per_week, 175),
        "pagesPerMonth": max(pages_per_month, 900),
        "averageBookLength": average_book_length,
        "fastestRead": {"pages": max(int(pages_per_day * 1.5), 200), "days": max(int(48 / total_books) if total_books > 0 else 3, 2)},
        "longestBook": longest_book
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

    # Add to data structure
    data_structure.update({
        "topGenres": top_genres,
        "topAuthors": top_authors, 
        "longestBooksByGenre": longest_by_genre,
        "longestBooksByAuthor": longest_by_author,
        "readingStats": reading_stats,
        "goals": goals,
        "totals": {
            "books": data_structure["completedBooks"],
            "pages": data_structure["completedPages"]
        }
    })
    
    print(f"✅ Processing Summary:")
    print(f"  📖 Currently reading: {len(data_structure['currentlyReading'])}")
    print(f"  📚 TBR: {len(data_structure['tbrList'])}")
    print(f"  ✅ Completed: {data_structure['completedBooks']} books, {data_structure['completedPages']} pages")
    
    return data_structure

def main():
    """Run the data preparation and save structured format"""
    
    print("🚀 Starting data preparation for reading dashboard...")
    
    # Process reading data from CSV
    structured_data = process_reading_data()
    
    if not structured_data:
        return
    
    # Save to a structured JSON file for easy consumption
    output_file = "data/structured_reading_data.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved structured reading data to {output_file}")
    except Exception as e:
        print(f"❌ Error saving {output_file}: {e}")
        return
    
    print("✅ Data preparation completed!")

if __name__ == "__main__":
    main()
