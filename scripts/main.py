#!/usr/bin/env python3
"""
Main workflow script: runs preprocessing, enrichment, validation, and data prep.
"""
import subprocess
import sys
import os
import pandas as pd

def run_script(script_name: str, description: str, interactive: bool = False) -> bool:
    """
    Run a Python script and handle errors.
    """
    print(f"🚀 {description}...")
    
    try:
        # For interactive scripts, don't capture output and allow user input
        if interactive:
            result = subprocess.run([sys.executable, script_name], 
                                  cwd=os.getcwd())  # Run from current directory (project root)
        else:
            result = subprocess.run([sys.executable, script_name], 
                                  capture_output=True, 
                                  text=True, 
                                  cwd=os.getcwd())  # Run from current directory (project root)
            
            if result.returncode == 0:
                print(f"✅ {description} completed successfully!")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                print(f"❌ {description} failed!")
                print(f"STDERR: {result.stderr}")
                return False
        
        if interactive:
            if result.returncode == 0:
                print(f"✅ {description} completed successfully!")
                return True
            else:
                print(f"❌ {description} failed!")
                return False
            
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def validate_enriched_data() -> bool:
    """
    Validate that enrich_data.py completed successfully with all books having genres.
    Returns True if successful, False if errors found.
    """
    print("🔍 Validating enriched data...")
    
    try:
        # Read enriched data
        df = pd.read_csv('data/goodreads_enriched.csv')
        total_books = len(df)
        
        if total_books == 0:
            print("❌ Validation failed: No books found in enriched CSV")
            return False
        
        # Check for books without genres
        books_without_genres = df[df['Genre'].isna() | (df['Genre'] == '') | (df['Genre'] == 'Unknown')]
        books_unknown_count = len(books_without_genres)
        
        # Count books with valid genres
        valid_genres = df[df['Genre'].notna() & (df['Genre'] != '') & (df['Genre'] != 'Unknown')]
        books_with_genres = len(valid_genres)
        
        print(f"📊 Enrichment validation results:")
        print(f"   📚 Total books: {total_books}")
        print(f"   ✅ Books with genres: {books_with_genres}")
        print(f"   ❓ Books without genres: {books_unknown_count}")
        print(f"   📈 Success rate: {(books_with_genres/total_books)*100:.1f}%")
        
        # List books without genres if any
        if books_unknown_count > 0:
            print(f"\n❌ Books still missing genres:")
            for idx, row in books_without_genres.iterrows():
                title = str(row.get('Title', 'Unknown'))
                author = str(row.get('Author', 'Unknown'))
                genre = str(row.get('Genre', 'None'))
                print(f"   • '{title}' by {author} - Genre: {genre}")
        
        # Check if we have reasonable success rate
        success_rate_threshold = 90  # At least 90% should have genres
        if books_with_genres / total_books * 100 >= success_rate_threshold:
            print(f"✅ Validation passed: {books_with_genres}/{total_books} books enriched ({books_with_genres/total_books*100:.1f}%)")
            return True
        else:
            print(f"❌ Validation failed: Only {books_with_genres/total_books*100:.1f}% books have genres (minimum {success_rate_threshold}%)")
            return False
            
    except FileNotFoundError:
        print("❌ Validation failed: goodreads_enriched.csv not found")
        return False
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        return False

def main():
    """
    Run the complete data processing workflow.
    """
    print("🎯 Starting Florilegium Data Processing Workflow")
    print("=" * 50)
    
    # Step 1: Clean and preprocess the data
    if not run_script("scripts/clean_data.py", "Data cleaning and preprocessing"):
        print("❌ Data cleaning failed. Stopping workflow!")
        return
    
    print()
    
    # Step 2: Apply manual genres first
    if not run_script("scripts/manual_genres.py", "Manual genre assignment"):
        print("❌ Manual genre assignment failed. Stopping workflow!")
        return
    
    print()
    
    # Step 3: Enrich remaining books with Google Books API (interactive for user approval)
    if not run_script("scripts/google_api_enrich.py", "Google Books API enrichment", interactive=True):
        print("❌ Google Books API enrichment failed. Stopping workflow!")
        return
    
    print()
    
    # Step 3: Validate enrichment completed successfully
    if not validate_enriched_data():
        print("❌ Data enrichment validation failed!")
        print("💡 Tip: Check missing genres above, may need to add to manual_genres.json")
        return
    
    print()
    
    # Step 4: Apply book overrides before data preparation
    if not run_script("scripts/apply_overrides.py", "Applying book overrides"):
        print("❌ Book overrides application failed. Stopping workflow!")
        return
    
    print()
    
    # Step 5: Apply book-specific genre overrides to CSV
    if not run_script("scripts/apply_book_genre_overrides.py", "Applying book-specific genre overrides"):
        print("❌ Book-specific genre overrides application failed. Stopping workflow!")
        return
    
    print()
    
    # Step 6: Run data preparation for dashboard
    if not run_script("scripts/data_prep.py", "Data preparation for dashboard"):
        print("❌ Data preparation failed. Stopping workflow!")
        return
    
    print()
    
    # Vercel deployment is automatic via GitHub merge → skip prompt
    print("⏭️ Skipping manual deployment (Vercel auto-deploys from GitHub)")
    
    print()
    print("🎉 Workflow completed successfully!")
    print("📊 Files updated:")
    print("   • data/goodreads_preprocessed.csv (cleaned titles & series)")
    print("   • data/goodreads_enriched.csv (with genres)")
    print("   • data/structured_reading_data.json (dashboard-ready data)")
    print()
    print("🚀 Ready for dashboard! Merge to GitHub for auto-deploy to Vercel")

if __name__ == "__main__":
    main()
