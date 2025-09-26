import pandas as pd
import re
from typing import Tuple

def clean_book_title_series(title: str) -> Tuple[str, str, str]:
    """
    Split book title from series name and number.
    
    Example: "Reveal Me (Shatter Me, #5.5)" 
    Returns: ("Reveal Me", "Shatter Me", "5.5")
    """
    if not title or title.strip() == '':
        return title, '', ''
    
    # More comprehensive patterns to handle various formats
    import re
    
    title = title.strip()
    
    # Pattern 1: "Title (Series Name #5.5)" format
    pattern1 = r'^(.+?)\s*\(([^#,]+)[,\s]*#(\d+\.?\d*)\)\s*$'
    match1 = re.match(pattern1, title)
    if match1:
        book_title = match1.group(1).strip()
        series_name = match1.group(2).strip()
        series_number = match1.group(3).strip()
        return book_title, series_name, series_number
    
    # Pattern 2: "Title (Series Name, #5.5)" format  
    pattern2 = r'^(.+?)\s*\(([^,#]+),\s*#(\d+\.?\d*)\)\s*$'
    match2 = re.match(pattern2, title)
    if match2:
        book_title = match2.group(1).strip()
        series_name = match2.group(2).strip()
        series_number = match2.group(3).strip()
        return book_title, series_name, series_number
    
    # Pattern 3: "Title (Series Name 5.5)" - without # symbol
    pattern3 = r'^(.+?)\s*\(([^,#]+)\s+(\d+\.?\d*)\)\s*$'
    match3 = re.match(pattern3, title)
    if match3:
        book_title = match3.group(1).strip()
        series_name = match3.group(2).strip()
        series_number = match3.group(3).strip()
        return book_title, series_name, series_number
    
    # Pattern 4: Just look for parentheses and extract what's inside
    match4 = re.match(r'^(.+?)\s*\(([^)]+)\)\s*$', title)
    if match4:
        # Try to extract number from the parentheses content
        parenthetical = match4.group(2).strip()
        # Look for numbers in the parenthetical
        number_match = re.search(r'[#\s]*(\d+\.?\d*)', parenthetical)
        if number_match:
            book_title = match4.group(1).strip()
            series_number = number_match.group(1)
            # Remove number from series name and clean up
            series_name = re.sub(r'[#,\s]*\d+\.?\d*', '', parenthetical).strip()
            return book_title, series_name, series_number
    
    # No series info found, return original title
    return title, '', ''

def check_empty_columns(df):
    """
    Check for columns with no data and warn user.
    Returns list of empty column names.
    """
    empty_columns = []
    
    # Check for columns that are completely empty (NaN) or just contains empty strings
    for col in df.columns:
        # Fill NaN with empty string, then strip whitespace, then check if all empty
        empty_count = (df[col].fillna('').astype(str).str.strip().values == '').sum()
        total_count = len(df)
        
        if empty_count == total_count:
            empty_columns.append(col)
    
    return empty_columns


def remove_empty_columns(df, empty_columns):
    """
    Remove empty columns but warn user first.
    """
    # Get data types and NA counts
    col_stats = [
        f"'{col}': {len(df)}/{(len(df))} values are empty"
        for col in empty_columns
    ]
    
    print(f"\n⚠️  Warning: Found {len(empty_columns)} empty columns that will be removed:")
    for col in empty_columns:
        print(f"   • {col}")
    
    # Remove them from DataFrame
    df_cleaned = df.drop(columns=empty_columns)
    
    print(f"✅ Removed {len(empty_columns)} empty columns. DataFrame reduced from {len(df.columns)} to {len(df_cleaned.columns)} columns.")
    
    return df_cleaned


def preprocess_goodreads_data():
    """
    Clean and preprocess Goodreads CSV:
    1. Separate main title from series info
    2. Clean up any other data issues
    3. Remove empty columns
    """
    print("🧹 Starting data preprocessing...")
    
    # Read the original Goodreads export
    df = pd.read_csv('data/goodreads_library_export.csv')
    
    print(f"📚 Processing {len(df)} books...")
    
    # Add new columns if they don't exist
    if 'Book Title' not in df.columns:
        df['Book Title'] = '' 
    if 'Series Name' not in df.columns:
        df['Series Name'] = ''
    if 'Series Number' not in df.columns:
        df['Series Number'] = ''
    
    # Process each book
    for idx, row in df.iterrows():
        title = row.get('Title', '')
        
        # Extract clean title and series info
        clean_title, series_name, series_number = clean_book_title_series(title)
        
        # Update the dataframe
        df.at[idx, 'Book Title'] = clean_title
        df.at[idx, 'Series Name'] = series_name 
        df.at[idx, 'Series Number'] = series_number
        
        # Also keep original title in Title column but update if we parsed a cleaner version
        if clean_title != title:
            df.at[idx, 'Title'] = clean_title  # Replace with cleaned version
    
    # 📋 **Check for empty columns**
    print("\n🔍 Checking for empty columns...")
    empty_columns = check_empty_columns(df)
    
    if empty_columns:
        df = remove_empty_columns(df, empty_columns)
    else:
        print("✅ No empty columns found, keeping all data.")
    
    # Save the preprocessed data
    df.to_csv('data/goodreads_preprocessed.csv', index=False)
    
    print(f"\n💾 Preprocessing complete! Saved to data/goodreads_preprocessed.csv")
    print(f"   Final CSV has {len(df)} books and {len(df.columns)} columns")
    
    # Show some examples of what we found
    series_books = df[df['Series Name'] != ''] if 'Series Name' in df.columns else pd.DataFrame()
    if not series_books.empty:
        print(f"\n📖 Found {len(series_books)} books with series information:")
        for idx, row in series_books.head(5).iterrows():
            print(f"  • {row['Book Title']} ({row['Series Name']} #{row['Series Number']})")
    
    return df

if __name__ == "__main__":
    preprocess_goodreads_data()
