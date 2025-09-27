#!/usr/bin/env python3
"""
Analyze current enriched state to detect recent changes.
Since we missed backing up before the change, let's look at the current state.
"""

import pandas as pd
import os
from datetime import datetime

def analyze_current_state():
    """Analyze the current enriched data to understand what changed."""
    print("🔍 Analyzing current enriched CSV state...")
    print("=" * 50)
    
    try:
        df = pd.read_csv('data/goodreads_enriched.csv')
        print(f"📊 Current enriched CSV: {len(df)} books")
        print(f"📅 File modified: {os.path.getmtime('data/goodreads_enriched.csv')}")
        
        # Check for recent additions by examining key indicators
        current_year = 2025
        
        # Look for books read in current year vs others
        recent_books = 0
        older_books = 0
        blank_dates = 0
        
        for idx, row in df.iterrows():
            date_read = str(row.get('Date Read', '')).strip()
            shelf = str(row.get('Exclusive Shelf', '')).lower().strip()
            
            if shelf == 'read' and date_read and date_read != 'nan':
                if str(current_year) in date_read:
                    recent_books += 1
                else:
                    older_books += 1
            elif shelf == 'read':
                blank_dates += 1
        
        print(f"\n📚 Breakdown of read books:")
        print(f"   Recent ({current_year}): {recent_books}")
        print(f"   Older: {older_books}")
        print(f"   Blank dates: {blank_dates}")
        
        # Check for books with manual overrides applied
        override_indicators = []
        total_genre_assigned = 0
        unknown_genres = 0
        
        for idx, row in df.iterrows():
            genre = str(row.get('Genre', '')).strip()
            title = str(row.get('Title', '')).strip()
            
            if genre and genre not in ['', 'nan', 'Unknown']:
                total_genre_assigned += 1
            else:
                unknown_genres += 1
                
            # Look for known override indicators
            if 'Mockingjay' in title or 'Catching Fire' in title or 'Hunger Games' in title:
                date_read = str(row.get('Date Read', '')).strip()
                if date_read and '2025' in date_read:
                    override_indicators.append(title)
        
        print(f"\n🎯 Genre assignment stats:")
        print(f"   Assigned genres: {total_genre_assigned}")
        print(f"   Unknown genres: {unknown_genres}")
        
        if override_indicators:
            print(f"\n🔧 Override indicators found:")
            for book in override_indicators:
                print(f"   ✅ {book}")
        
        # Try to detect if this is the result of a recent processing
        recent_processing = False
        if recent_books > 0 and total_genre_assigned > len(df) * 0.8:  # Most books have genres
            recent_processing = True
            
        if recent_processing:
            print(f"\n✅ This appears to be recently processed data (good genre coverage)")
        else:
            print(f"\n⚠️  This may be older data")
            
        return {
            "total_books": len(df),
            "recent_read": recent_books,
            "assigned_genres": total_genre_assigned,
            "is_recent": recent_processing
        }
        
    except Exception as e:
        print(f"❌ Error analyzing state: {e}")
        return None

def suggest_proper_workflow():
    """Suggest how to properly validate changes going forward."""
    print("\n🔄 PROPER VALIDATION WORKFLOW:")
    print("=" * 50)
    print("1. 📎 Upload NEW library CSV")
    print("2. 💾 BACKUP current enriched data BEFORE processing")
    print("3. 🚀 Run 'python scripts/main.py'")  
    print("4. 🔍 Compare with 'python scripts/validate_changes.py'")
    print("\n💡 The issue: We backed up AFTER processing, not before!")

if __name__ == "__main__":
    result = analyze_current_state()
    if result:
        print(f"\n📋 Current processing state detected:")
        print(f"   Total books: {result['total_books']}")
        print(f"   Recent reads: {result['recent_read']}")
        print(f"   Genres assigned: {result['assigned_genres']}")
        
    suggest_proper_workflow()
