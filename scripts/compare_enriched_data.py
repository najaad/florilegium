#!/usr/bin/env python3
"""
Compare enriched data before and after library update.
This script helps validate that only expected changes occurred.
"""

import pandas as pd
import json
from typing import Dict, List, Any

def compare_csv_files(original_path: str, new_path: str) -> Dict[str, Any]:
    """Compare two enriched CSV files and identify differences."""
    print("🔍 Comparing enriched CSV files...")
    
    try:
        df_original = pd.read_csv(original_path)
        df_new = pd.read_csv(new_path)
        
        print(f"📊 Original: {len(df_original)} books")
        print(f"📊 New: {len(df_new)} books")
        
        # Basic stats
        differences = {
            "row_count_change": len(df_new) - len(df_original),
            "new_books": [],
            "modified_books": [],
            "removed_books": [],
            "summary": {}
        }
        
        # Find new books (by title + author combination)
        original_books = set()
        for _, row in df_original.iterrows():
            key = f"{str(row.get('Title', '')).strip()}|{str(row.get('Author', '')).strip()}"
            original_books.add(key)
        
        new_books = set()
        for _, row in df_new.iterrows():
            key = f"{str(row.get('Title', '')).strip()}|{str(row.get('Author', '')).strip()}"
            new_books.add(key)
        
        # Find truly new books
        truly_new = new_books - original_books
        for book_key in truly_new:
            title, author = book_key.split('|', 1)
            differences["new_books"].append({
                "title": title,
                "author": author
            })
        
        # Find removed books
        removed = original_books - new_books
        for book_key in removed:
            title, author = book_key.split('|', 1)
            differences["removed_books"].append({
                "title": title,
                "author": author
            })
        
        # Check for modified books (same title+author but different data)
        common_books = original_books & new_books
        for book_key in common_books:
            title, author = book_key.split('|', 1)
            
            # Find rows in both dataframes
            orig_row = None
            new_row = None
            
            for _, row in df_original.iterrows():
                if (str(row.get('Title', '')).strip() == title and 
                    str(row.get('Author', '')).strip() == author):
                    orig_row = row
                    break
            
            for _, row in df_new.iterrows():
                if (str(row.get('Title', '')).strip() == title and 
                    str(row.get('Author', '')).strip() == author):
                    new_row = row
                    break
            
            if orig_row is not None and new_row is not None:
                # Compare key fields
                changes = []
                key_fields = ['Genre', 'Date Read', 'Exclusive Shelf', 'Read Count', 'Number of Pages']
                
                for field in key_fields:
                    if field in orig_row and field in new_row:
                        orig_val = str(orig_row.get(field, '')).strip()
                        new_val = str(new_row.get(field, '')).strip()
                        if orig_val != new_val:
                            changes.append({
                                "field": field,
                                "original": orig_val,
                                "new": new_val
                            })
                
                if changes:
                    differences["modified_books"].append({
                        "title": title,
                        "author": author,
                        "changes": changes
                    })
        
        # Summary
        differences["summary"] = {
            "total_books_original": len(df_original),
            "total_books_new": len(df_new),
            "new_books_count": len(differences["new_books"]),
            "removed_books_count": len(differences["removed_books"]),
            "modified_books_count": len(differences["modified_books"]),
            "net_change": len(df_new) - len(df_original)
        }
        
        return differences
        
    except Exception as e:
        print(f"❌ Error comparing CSV files: {e}")
        return {"error": str(e)}

def compare_json_files(original_path: str, new_path: str) -> Dict[str, Any]:
    """Compare structured reading data JSON files."""
    print("🔍 Comparing structured reading data...")
    
    try:
        with open(original_path, 'r') as f:
            data_original = json.load(f)
        
        with open(new_path, 'r') as f:
            data_new = json.load(f)
        
        differences = {
            "totals_changed": {},
            "monthly_changes": {},
            "genre_changes": {},
            "author_changes": {},
            "summary": {}
        }
        
        # Compare totals
        if data_original.get('totals') != data_new.get('totals'):
            differences["totals_changed"] = {
                "original": data_original.get('totals', {}),
                "new": data_new.get('totals', {})
            }
        
        # Compare monthly data
        orig_monthly = data_original.get('byMonth', [])
        new_monthly = data_new.get('byMonth', [])
        
        if orig_monthly != new_monthly:
            differences["monthly_changes"] = {
                "original": orig_monthly,
                "new": new_monthly
            }
        
        # Compare top genres
        orig_genres = data_original.get('topGenres', [])
        new_genres = data_new.get('topGenres', [])
        
        if orig_genres != new_genres:
            differences["genre_changes"] = {
                "original": orig_genres,
                "new": new_genres
            }
        
        # Compare top authors
        orig_authors = data_original.get('topAuthors', [])
        new_authors = data_new.get('topAuthors', [])
        
        if orig_authors != new_authors:
            differences["author_changes"] = {
                "original": orig_authors,
                "new": new_authors
            }
        
        return differences
        
    except Exception as e:
        print(f"❌ Error comparing JSON files: {e}")
        return {"error": str(e)}

def main():
    """Main comparison function."""
    print("🔍 Comparing enriched data before and after library update...")
    print("=" * 60)
    
    # Compare CSV files
    csv_differences = compare_csv_files(
        'validate/goodreads_enriched_backup.csv',
        'data/goodreads_enriched.csv'
    )
    
    print("\n📊 CSV COMPARISON RESULTS:")
    print("-" * 40)
    
    if "error" in csv_differences:
        print(f"❌ Error: {csv_differences['error']}")
    else:
        summary = csv_differences.get("summary", {})
        print(f"📚 Books: {summary.get('total_books_original', 0)} → {summary.get('total_books_new', 0)} (change: {summary.get('net_change', 0)})")
        print(f"➕ New books: {summary.get('new_books_count', 0)}")
        print(f"➖ Removed books: {summary.get('removed_books_count', 0)}")
        print(f"🔄 Modified books: {summary.get('modified_books_count', 0)}")
        
        # Show new books
        if csv_differences.get("new_books"):
            print(f"\n📖 NEW BOOKS ({len(csv_differences['new_books'])}):")
            for book in csv_differences["new_books"]:
                print(f"   • {book['title']} by {book['author']}")
        
        # Show removed books
        if csv_differences.get("removed_books"):
            print(f"\n🗑️  REMOVED BOOKS ({len(csv_differences['removed_books'])}):")
            for book in csv_differences["removed_books"]:
                print(f"   • {book['title']} by {book['author']}")
        
        # Show modified books
        if csv_differences.get("modified_books"):
            print(f"\n🔄 MODIFIED BOOKS ({len(csv_differences['modified_books'])}):")
            for book in csv_differences["modified_books"]:
                print(f"   • {book['title']} by {book['author']}")
                for change in book.get("changes", []):
                    print(f"     {change['field']}: '{change['original']}' → '{change['new']}'")
    
    # Compare JSON files
    json_differences = compare_json_files(
        'validate/structured_reading_data_backup.json',
        'data/structured_reading_data.json'
    )
    
    print("\n📊 JSON COMPARISON RESULTS:")
    print("-" * 40)
    
    if "error" in json_differences:
        print(f"❌ Error: {json_differences['error']}")
    else:
        if json_differences.get("totals_changed"):
            print("📈 TOTALS CHANGED:")
            orig = json_differences["totals_changed"]["original"]
            new = json_differences["totals_changed"]["new"]
            print(f"   Books: {orig.get('books', 0)} → {new.get('books', 0)}")
            print(f"   Pages: {orig.get('pages', 0)} → {new.get('pages', 0)}")
        
        if json_differences.get("monthly_changes"):
            print("📅 MONTHLY DATA CHANGED")
        
        if json_differences.get("genre_changes"):
            print("📚 GENRE RANKINGS CHANGED")
        
        if json_differences.get("author_changes"):
            print("👤 AUTHOR RANKINGS CHANGED")
        
        if not any([
            json_differences.get("totals_changed"),
            json_differences.get("monthly_changes"),
            json_differences.get("genre_changes"),
            json_differences.get("author_changes")
        ]):
            print("✅ No changes detected in structured data")
    
    print("\n" + "=" * 60)
    print("🎯 VALIDATION COMPLETE")
    
    # Overall assessment
    if csv_differences.get("summary", {}).get("net_change", 0) > 0:
        print(f"✅ Expected: {csv_differences['summary']['net_change']} new book(s) added")
    elif csv_differences.get("summary", {}).get("net_change", 0) < 0:
        print(f"⚠️  Unexpected: {abs(csv_differences['summary']['net_change'])} book(s) removed")
    else:
        print("✅ No net change in book count")

if __name__ == "__main__":
    main()
