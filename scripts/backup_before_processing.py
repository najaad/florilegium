#!/usr/bin/env python3
"""
Creates proper backup BEFORE processing new library data.
Run this BEFORE updating your library CSV and running main.py.
"""

import shutil
import os
from datetime import datetime

def backup_before_processing():
    """Create backup of enriched data before running main.py with new library"""
    print("💾 Creating backup BEFORE processing...")
    print("=" * 50)
    
    # Check if files exist
    if not os.path.exists('data/goodreads_enriched.csv'):
        print("❌ No enriched CSV found. Run enrichment first.")
        return False
        
    if not os.path.exists('data/structured_reading_data.json'):
        print("❌ No structured data found. Run data_prep.py first.")
        return False
    
    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"validate/backup_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    
    try:
        # Backup main files
        shutil.copy2('data/goodreads_enriched.csv', f"{backup_dir}/goodreads_enriched_original.csv")
        shutil.copy2('data/structured_reading_data.json', f"{backup_dir}/structured_reading_data_original.json")
        
        # Also update the standard backup location for comparison scripts
        shutil.copy2('data/goodreads_enriched.csv', 'validate/goodreads_enriched_backup.csv')
        shutil.copy2('data/structured_reading_data.json', 'validate/structured_reading_data_backup.json')
        
        print(f"✅ Backup created at: {backup_dir}")
        print(f"📁 Also updated standard backup: validate/goodreads_enriched_backup.csv")
        
        # Show status
        if os.path.exists('data/goodreads_library_export.csv'):
            original_size = os.path.getsize('data/goodreads_library_export.csv')
            print(f"📊 Original CSV size: {original_size:,} bytes")
            print(f"💡 NOW: Upload your new library export to 'data/goodreads_library_export.csv'")
            print(f"💡 THEN: Run 'python scripts/main.py'")
            print(f"💡 FINALLY: Run 'python scripts/validate_changes.py'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False

if __name__ == "__main__":
    backup_before_processing()
