#!/usr/bin/env python3
"""
Quick validation script to run after library update.
This will compare the current enriched data with the backup.
"""

import subprocess
import sys
import os

def main():
    """Run the comparison and show results."""
    print("🔍 Validating changes after library update...")
    print("=" * 50)
    
    # Check if backup files exist
    if not os.path.exists('validate/goodreads_enriched_backup.csv'):
        print("❌ Backup files not found. Run this after creating backups.")
        return
    
    if not os.path.exists('data/goodreads_enriched.csv'):
        print("❌ Current enriched data not found. Run main.py first.")
        return
    
    # Run the comparison
    try:
        result = subprocess.run([
            sys.executable, 'scripts/compare_enriched_data.py'
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
            
    except Exception as e:
        print(f"❌ Error running comparison: {e}")

if __name__ == "__main__":
    main()
