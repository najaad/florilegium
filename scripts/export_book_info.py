#!/usr/bin/env python3
"""
Export helper script that takes goodreads_enriched.csv and outputs a clean CSV
with fields: name, author, isbn, genre
"""

import pandas as pd
from typing import Optional

def export_book_info(input_file: str = 'data/goodreads_enriched.csv', 
                     output_file: str = 'data/books_summary.csv'):
    """
    Export key book information from enriched Goodreads data.
    
    Args:
        input_file: Path to enriched CSV file
        output_file: Output CSV file with clean book info
    """
    print("📖 Exporting book information...")
    
    # Load the enriched data
    try:
        df = pd.read_csv(input_file)
        print(f"✅ Loaded {len(df)} books from {input_file}")
    except FileNotFoundError:
        print(f"❌ Input file not found: {input_file}")
        return False
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False
    
    # Create output dataframe with clean columns
    output_df = pd.DataFrame({
        'name': df['Title'].fillna('Unknown'),
        'author': df['Author'].fillna('Unknown'),
        'isbn': df['ISBN13'].fillna('N/A'),
        'genre': df['Genre'].fillna('Unknown')
    })
    
    # Clean up the data
    output_df['name'] = output_df['name'].astype(str).str.strip()
    output_df['author'] = output_df['author'].astype(str).str.strip()
    output_df['isbn'] = output_df['isbn'].astype(str).str.strip()
    output_df['genre'] = output_df['genre'].astype(str).str.strip()
    
    # Clean up ISBN formatting (remove CSV artifacts)
    output_df['isbn'] = output_df['isbn'].str.replace(r'["""]', '', regex=True)  # Remove quotes
    output_df['isbn'] = output_df['isbn'].str.replace(r'^=\?"?([^"]*)"?$', r'\1', regex=True)  # Remove Excel formatting
    output_df['isbn'] = output_df['isbn'].str.replace('=', '')  # Remove remaining equals signs
    output_df['isbn'] = output_df['isbn'].str.strip()  # Remove whitespace
    
    # Normalize missing ISBNs
    output_df['isbn'] = output_df['isbn'].replace(['', 'nan', 'N/A', 'NaN', 'N A'], 'N/A')
    
    # Save the cleaned output
    try:
        output_df.to_csv(output_file, index=False)
        print(f"💾 Exported clean book info to: {output_file}")
        print(f"📊 Summary: {len(output_df)} books exported")
        
        # Show a sample of the exported data
        print("\n📖 Sample exported data:")
        print(output_df.head(3).to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving output: {e}")
        return False

def main():
    """Run the book information export"""
    export_book_info()
    
if __name__ == "__main__":
    main()
