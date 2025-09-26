#!/usr/bin/env python3
"""
Vercel Deployment & Communication Script

This script handles uploading structured data to Vercel and communicating
with the Next.js API endpoints for production deployment.
"""

import json
import requests
import os
import subprocess
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Test for required dependencies
try:
    import requests
except ImportError:
    print("❌ Missing dependency: pip install requests")
    sys.exit(1)

def load_structured_data(file_path: str = "data/structured_reading_data.json") -> Optional[Dict[Any, Any]]:
    """
    Load structured reading data from JSON file.
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {file_path} not found")
        print("💡 Run scripts/data_prep.py first to generate the data")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return None

def validate_required_sections(data: Dict[Any, Any]) -> bool:
    """
    Validate that the structured data has all required sections.
    """
    required_sections = [
        'currentlyReading', 'tbrList', 'totals', 'byMonth',
        'readingStats', 'goals', 'topGenres', 'topAuthors'
    ]
    
    missing = []
    for section in required_sections:
        if section not in data:
            missing.append(section)
    
    if missing:
        print(f"❌ Missing required sections: {missing}")
        return False
    
    print(f"✅ All required sections present")
    return True

def check_vercel_environment() -> bool:
    """
    Check if Vercel is properly set up.
    """
    try:
        result = subprocess.run(['vercel', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Vercel CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Vercel CLI not found or not working")
            return False
    except FileNotFoundError:
        print("❌ Vercel CLI not installed")
        return False
    except Exception as e:
        print(f"❌ Error checking Vercel: {e}")
        return False

def check_api_endpoints(project_url: str = None) -> bool:
    """
    Test if the API endpoints are working.
    """
    # Try to detect Vercel URL if not provided
    if not project_url:
        try:
            result = subprocess.run(['vercel', 'ls'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'florilegium' in line.lower():
                        # Extract URL from stdout format
                        parts = line.split()
                        if len(parts) > 0:
                            project_url = parts[0].strip()
                            break
        except Exception:
            pass
    
    if not project_url:
        print("⚠️  Could not detect Vercel project URL")
        print("💡 You may need to deploy manually: vercel --prod")
        return False
    
    print(f"🔗 Testing API endpoints for {project_url}")
    
    # Test the refresh API endpoint (if you have one)
    try:
        test_url = f"{project_url}/api/refresh"
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            print("✅ API endpoint responding correctly")
            return True
        else:
            print(f"⚠️  API returned status {response.status_code}")
    except Exception as e:
        print(f"⚠️  Could not test API endpoint: {e}")
    
    return True

def deploy_to_vercel() -> bool:
    """
    Deploy the updated app to Vercel.
    """
    print("🚀 Deploying to Vercel...")
    
    try:
        # Run vercel deploy with production flag
        result = subprocess.run(['vercel', '--prod', '--yes'], 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            # Extract deployment URL from output
            output_lines = result.stdout.split('\n')
            deployment_url = None
            for line in output_lines:
                if 'https://' in line and 'vercel.app' in line:
                    deployment_url = line.strip()
                    break
            
            if deployment_url:
                print(f"✅ Deployment successful!")
                print(f"🌐 URL: {deployment_url}")
                return True
            else:
                print("✅ Deployment completed but URL not detected")
                return True
        else:
            print(f"❌ Deployment failed:")
            print(f"STDERR: {result.stderr}")
            print(f"STDOUT: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Deployment timed out (longer than 2 minutes)")
        return False
    except Exception as e:
        print(f"❌ Error running deployment: {e}")
        return False

def sync_data_to_vercel(data: Dict[Any, Any]) -> bool:
    """
    Sync the structured data to Vercel (trigger refresh API).
    """
    print("📡 Syncing data to Vercel...")
    
    try:
        project_urls = [
            "https://florilegium.vercel.app",  # Update with your actual domain
            "https://florilegium-git-main-yourusername.vercel.app"  # Default pattern
        ]
        
        # Try each possible URL
        for url in project_urls:
            try:
                sync_url = f"{url}/api/refresh"
                response = requests.post(sync_url, json=data, timeout=30)
                
                if response.status_code == 200:
                    print(f"✅ Data synced successfully to {url}")
                    return True
                else:
                    print(f"⚠️  Sync failed for {url}: {response.status_code}")
                    
            except requests.RequestException:
                continue
        
        print("⚠️  Could not sync data - URL may need manual update")
        return False
        
    except Exception as e:
        print(f"❌ Error syncing data: {e}")
        return False

def main():
    """
    Main deployment workflow: validate data → check Vercel → deploy → sync.
    """
    print("🎯 Vercel Deployment & Communication Workflow")
    print("=" * 60)
    
    # Step 1: Load and validate structured data
    print("📚 Loading structured data...")
    data = load_structured_data()
    if not data:
        print("❌ No data to deploy!")
        return False
    
    print("🔍 Validating data structure...")
    if not validate_required_sections(data):
        print("❌ Data validation failed!")
        return False
    
    # Step 2: Check Vercel availability
    print("\n🔧 Checking Vercel setup...")
    if not check_vercel_environment():
        print("💡 Install Vercel CLI: npm install -g vercel")
        return False
    
    # Step 3: Deploy to Vercel 
    print("\n🚀 Deploying to production...")
    if not deploy_to_vercel():
        print("❌ Deployment failed!")
        return False
    
    # Step 4: Sync data with the deployed app
    print("\n📡 Syncing data...")
    if sync_data_to_vercel(data):
        print("✅ Data sync successful!")
    else:
        print("⚠️  Data sync failed - you may need to manually trigger refresh")
    
    print("\n🎉 Deployment workflow completed!")
    print("💡 Tip: Your app should be live and updated!")
    
    return True

if __name__ == "__main__":
    main()
