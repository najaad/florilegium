import json
import pandas as pd
from datetime import datetime, date
import os

def handler(request):
    """
    Main API endpoint that processes CSV data and returns structured data for the UI.
    Currently uses mock data - replace with real CSV processing as needed.
    """
    
    # TODO: Replace this with your actual CSV processing
    # Example: df = pd.read_csv('your-books-data.csv')
    
    # For now, return the same mock data structure
    # This ensures your UI works while you build the CSV processing
    
    mock_data = {
        # Main stats (43 books through September)
        "totals": {"books": 43, "pages": 13760},
        
        # Chart data (realistic distribution for a frequent reader)
        "byMonth": [
            {"month": "Jan", "count": 4, "pages": 1280},
            {"month": "Feb", "count": 3, "pages": 960},
            {"month": "Mar", "count": 5, "pages": 1600},
            {"month": "Apr", "count": 4, "pages": 1280},
            {"month": "May", "count": 6, "pages": 1920},
            {"month": "Jun", "count": 5, "pages": 1600},
            {"month": "Jul", "count": 7, "pages": 2240},
            {"month": "Aug", "count": 6, "pages": 1920},
            {"month": "Sep", "count": 3, "pages": 960},
            {"month": "Oct", "count": 0, "pages": 0},
            {"month": "Nov", "count": 0, "pages": 0},
            {"month": "Dec", "count": 0, "pages": 0},
        ],
        
        # Reading stats (calculated from 43 books, 13760 pages over 9 months)
        "readingStats": {
            "pagesPerDay": 50,  # 13760 pages / 275 days (9 months) = ~50 pages/day
            "pagesPerWeek": 350,  # 50 * 7 = 350 pages/week
            "pagesPerMonth": 1529,  # 13760 / 9 = ~1529 pages/month
            "averageBookLength": 320,  # 13760 / 43 = 320 pages/book
            "fastestRead": {"pages": 400, "days": 2},
            "longestBook": 850
        },
        
        # Goals data (ambitious but achievable for a frequent reader)
        "goals": {
            "books": {
                "annual": {"current": 43, "target": 60},
                "monthly": {"current": 3, "target": 5}
            },
            "pages": {
                "annual": {"current": 13760, "target": 20000},
                "monthly": {"current": 960, "target": 1500}
            }
        },
        
        # Currently reading books
        "currentlyReading": [
            {
                "title": "The Seven Husbands of Evelyn Hugo",
                "author": "Taylor Jenkins Reid",
                "progress": 65,
                "totalPages": 400
            },
            {
                "title": "Project Hail Mary",
                "author": "Andy Weir",
                "progress": 30,
                "totalPages": 500
            },
            {
                "title": "The Way of Kings",
                "author": "Brandon Sanderson",
                "progress": 15,
                "totalPages": 1007
            }
        ],
        
        # Top genres and authors
        "topGenres": [
            {"name": "Fantasy", "count": 5},
            {"name": "Mystery", "count": 3},
            {"name": "Romance", "count": 2},
            {"name": "Sci-Fi", "count": 2},
            {"name": "Thriller", "count": 2},
            {"name": "Historical Fiction", "count": 1}
        ],
        
        "topAuthors": [
            {"name": "Brandon Sanderson", "count": 3},
            {"name": "Agatha Christie", "count": 2},
            {"name": "Jane Austen", "count": 2},
            {"name": "Isaac Asimov", "count": 1},
            {"name": "Neil Gaiman", "count": 1},
            {"name": "Ursula K. Le Guin", "count": 1}
        ],
        
        # Annual Reading Forecast data (consistent with frequent reader)
        "lastYearTotals": {"books": 52, "pages": 16640},
        "currentYearStart": "2024-01-01",
        
        # Longest books by genre (top 3)
        "longestBooksByGenre": [
            {"genre": "Fantasy", "title": "The Way of Kings", "author": "Brandon Sanderson", "pages": 1007},
            {"genre": "Mystery", "title": "The Murder of Roger Ackroyd", "author": "Agatha Christie", "pages": 320},
            {"genre": "Romance", "title": "Pride and Prejudice", "author": "Jane Austen", "pages": 432}
        ],
        
        # Genre reading patterns
        "consistentGenres": [
            {"name": "Fantasy", "currentYear": 5, "pastYears": 6, "totalBooks": 11},
            {"name": "Mystery", "currentYear": 3, "pastYears": 4, "totalBooks": 7},
            {"name": "Romance", "currentYear": 2, "pastYears": 3, "totalBooks": 5}
        ],
        
        # Author reading patterns
        "consistentAuthors": [
            {"name": "Brandon Sanderson", "currentYear": 3, "pastYears": 4, "totalBooks": 7},
            {"name": "Agatha Christie", "currentYear": 2, "pastYears": 3, "totalBooks": 5},
            {"name": "Jane Austen", "currentYear": 2, "pastYears": 2, "totalBooks": 4}
        ],
        
        "longestBooksByAuthor": [
            {"author": "Brandon Sanderson", "title": "The Way of Kings", "pages": 1007},
            {"author": "Agatha Christie", "title": "The Murder of Roger Ackroyd", "pages": 320},
            {"author": "Jane Austen", "title": "Pride and Prejudice", "pages": 432}
        ],
        
        # TBR (To Be Read) list for randomizer
        "tbrList": [
            {"title": "The Midnight Library", "author": "Matt Haig", "genre": "Fiction"},
            {"title": "Circe", "author": "Madeline Miller", "genre": "Fantasy"},
            {"title": "The Seven Husbands of Evelyn Hugo", "author": "Taylor Jenkins Reid", "genre": "Historical Fiction"},
            {"title": "Project Hail Mary", "author": "Andy Weir", "genre": "Sci-Fi"},
            {"title": "The Way of Kings", "author": "Brandon Sanderson", "genre": "Fantasy"},
            {"title": "Dune", "author": "Frank Herbert", "genre": "Sci-Fi"},
            {"title": "The Silent Patient", "author": "Alex Michaelides", "genre": "Thriller"},
            {"title": "Educated", "author": "Tara Westover", "genre": "Memoir"},
            {"title": "The Book Thief", "author": "Markus Zusak", "genre": "Historical Fiction"},
            {"title": "The Night Circus", "author": "Erin Morgenstern", "genre": "Fantasy"},
            {"title": "Where the Crawdads Sing", "author": "Delia Owens", "genre": "Fiction"},
            {"title": "The Alchemist", "author": "Paulo Coelho", "genre": "Fiction"}
        ]
    }
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(mock_data)
    }


# Example CSV processing functions (uncomment and modify as needed)
def process_csv_data(csv_file_path):
    """
    Example function to process your CSV file.
    Replace the mock data above with calls to this function.
    """
    try:
        # Read your CSV file
        df = pd.read_csv(csv_file_path)
        
        # Example processing - adjust based on your CSV structure
        totals = {
            "books": len(df),
            "pages": df['pages'].sum() if 'pages' in df.columns else 0
        }
        
        # Process by month
        if 'date_read' in df.columns:
            df['date_read'] = pd.to_datetime(df['date_read'])
            df['month'] = df['date_read'].dt.strftime('%b')
            
            by_month = df.groupby('month').agg({
                'title': 'count',
                'pages': 'sum'
            }).reset_index()
            
            by_month_data = []
            for _, row in by_month.iterrows():
                by_month_data.append({
                    "month": row['month'],
                    "count": int(row['title']),
                    "pages": int(row['pages'])
                })
        else:
            by_month_data = []
        
        return {
            "totals": totals,
            "byMonth": by_month_data,
            # Add more processing as needed
        }
        
    except Exception as e:
        print(f"Error processing CSV: {e}")
        return None


def calculate_reading_stats(df):
    """
    Calculate reading statistics from your CSV data.
    """
    if df.empty:
        return {}
    
    # Calculate pages per day, week, month
    total_pages = df['pages'].sum() if 'pages' in df.columns else 0
    total_days = (datetime.now() - df['date_read'].min()).days if 'date_read' in df.columns else 1
    
    return {
        "pagesPerDay": round(total_pages / total_days, 1),
        "pagesPerWeek": round(total_pages / total_days * 7, 1),
        "pagesPerMonth": round(total_pages / total_days * 30, 1),
        "averageBookLength": round(total_pages / len(df), 1),
        "fastestRead": {"pages": df['pages'].max(), "days": 1},  # Example
        "longestBook": df['pages'].max() if 'pages' in df.columns else 0
    }
