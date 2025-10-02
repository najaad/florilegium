#!/usr/bin/env python3
"""
Apply overrides to goodreads_enriched.csv before data preparation.
Loads override.json and updates specific book fields.
"""

import pandas as pd
import json
from typing import Dict, Any, Optional

def load_overrides(overrides_file: str = 'scripts/override.json') -> Dict[str, Any]:
    """Load overrides from JSON file."""
    try:
        with open(overrides_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('book_overrides', {}).get('overrides', [])
    except FileNotFoundError:
        print(f"📁 Override file not found: {overrides_file}")
        return []
    except Exception as e:
        print(f"❌ Error loading overrides: {e}")
        return []

def robust_match_override(title: str, author: str, override: Dict[str, Any]) -> Optional[int]:
    """Enhanced matching logic that handles title variations and partial matches."""
    override_title = override.get('title', '').lower().strip()
    override_author = override.get('author', '').lower().strip()
    
    # Clean current book data
    book_title = str(title).lower().strip()
    book_author = str(author).lower().strip()
    
    # Normalize author names for better matching
    def normalize_author(name: str) -> str:
        name = name.strip().lower()
        # Remove common suffixes and parenthetical text
        import re
        name = re.sub(r'\s*(goodreads author)', '', name)
        name = re.sub(r'\s*\(.*\)', '', name)
        name = re.sub(r'\s*,\s*$', '', name)  # Remove trailing comma
        return name.strip()
    
    book_author_norm = normalize_author(book_author)
    override_author_norm = normalize_author(override_author)
    
    # 1. Exact title match (original method)
    if override_title == book_title:
        # Check author if provided in override
        if not override_author or override_author_norm in book_author_norm or book_author_norm in override_author_norm:
            return 2  # High confidence
        return 1  # Medium confidence (title matches, author mismatch)
    
    # 2. Base title matching (for series with parens issue)
    # Extract clean title from complex titles like "Title (Series Name #1)"
    def extract_base_title(full_title: str) -> str:
        import re
        # Remove parenthetical content that might be series info
        clean = re.sub(r'\s*\([^)]*#[^)]*\)$', '', str(full_title))
        clean = re.sub(r'\s*\([^)]*#(\d+.\d*)\),?\s*$', '', clean)
        return clean.strip().lower()
    
    override_base = extract_base_title(override_title)
    book_base = extract_base_title(book_title)
    
    if override_base == book_base:
        if not override_author or override_author_norm in book_author_norm or book_author_norm in override_author_norm:
            return 2  # High confidence (base titles match)
        return 1  # Medium confidence
    
    # 3. Partial title substring matching
    if (override_title in book_title or book_title in override_title) and len(override_title) > 5:
        if not override_author or override_author_norm in book_author_norm or book_author_norm in override_author_norm:
            return 1  # Medium confidence
    
    return 0  # No match


def apply_overrides_to_csv(csv_path: str = 'data/goodreads_enriched.csv'):
    """
    Apply book overrides to the enriched CSV file with robust matching.
    """
    print("🔧 Applying book overrides with robust matching...")
    
    # Load overrides
    overrides = load_overrides()
    
    if not overrides:
        print("📂 No overrides found to apply")
        return
    
    print(f"📋 Found {len(overrides)} overrides to apply")
    
    # Load the CSV
    try:
        df = pd.read_csv(csv_path)
        print(f"📖 Loaded CSV with {len(df)} books")
    except FileNotFoundError:
        print(f"❌ Could not load {csv_path}")
        return
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return
    
    applied_count = 0
    
    # Apply each override
    for override in overrides:
        title = override.get('title', '').strip()
        author = override.get('author', '').strip() 
        fields = override.get('fields', {})
        note = override.get('note', '')
        
        if not title:
            continue
            
        # Enhanced matching for titles that vary between exports
        matches = []
        for idx, row in df.iterrows():
            row_title = str(row.get('Title', '')).strip()
            row_author = str(row.get('Author', '')).strip()
            
            confidence = robust_match_override(row_title, row_author, override)
            if confidence > 0:
                matches.append((idx, row_title, row_author, confidence))
        
        # Sort by confidence (high = 2, medium = 1)
        matches.sort(key=lambda x: x[3], reverse=True)
            
        if not matches:
            print(f"⚠️  No matching book found for: '{title}' by {author}")
            continue
        elif len(matches) > 1 and matches[0][3] == matches[1][3]:
            # Multiple high-confidence matches found
            print(f"⚠️  Multiple high-confidence matches for '{title}' by {author}: {len(matches)} books")
            for idx, book_title, book_author, conf in matches:
                if conf >= 2:
                    print(f"     {idx}: {book_title} by {book_author} (match confidence: {conf})")
            print(f"     👆 Using first high-confidence match:")
            
        # Apply the overrides to the best match
        best_match = matches[0]
        row_idx = best_match[0]
        
        success = False
        for field, value in fields.items():
            if field in df.columns:
                # Handle type conversion for numeric fields
                if field == "Read Count" and isinstance(value, str):
                    try:
                        value = int(value)
                    except ValueError:
                        print(f"⚠️  Invalid Read Count: {value} (skipping)")
                        continue
                df.at[row_idx, field] = value
                success = True
            else:
                print(f"⚠️  Column not found: {field} (skipping)")
        
        if success:
            applied_count += 1
    
    # Save the updated CSV
    if applied_count > 0:
        try:
            df.to_csv(csv_path, index=False)
            print(f"💾 Saved updated CSV with {applied_count} overrides applied")
        except Exception as e:
            print(f"❌ Error saving CSV: {e}")
    else:
        print("ℹ️  No overrides were applied")

if __name__ == "__main__":
    apply_overrides_to_csv()
