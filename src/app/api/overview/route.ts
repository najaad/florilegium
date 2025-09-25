import { NextResponse } from 'next/server';

export async function GET() {
  // Complete mock data structure - this shows exactly what your Python API needs to provide
  const mockData = {
    // Main stats (43 books through September)
    totals: { books: 43, pages: 13760 },
    
    // Chart data (realistic distribution for a frequent reader)
    byMonth: [
      { month: 'Jan', count: 4, pages: 1280 },
      { month: 'Feb', count: 3, pages: 960 },
      { month: 'Mar', count: 5, pages: 1600 },
      { month: 'Apr', count: 4, pages: 1280 },
      { month: 'May', count: 6, pages: 1920 },
      { month: 'Jun', count: 5, pages: 1600 },
      { month: 'Jul', count: 7, pages: 2240 },
      { month: 'Aug', count: 6, pages: 1920 },
      { month: 'Sep', count: 3, pages: 960 },
      { month: 'Oct', count: 0, pages: 0 },
      { month: 'Nov', count: 0, pages: 0 },
      { month: 'Dec', count: 0, pages: 0 },
    ],
    
    // Reading stats (calculated from 43 books, 13760 pages over 9 months)
    readingStats: {
      pagesPerDay: 50, // 13760 pages / 275 days (9 months) = ~50 pages/day
      pagesPerWeek: 350, // 50 * 7 = 350 pages/week
      pagesPerMonth: 1529, // 13760 / 9 = ~1529 pages/month
      averageBookLength: 320, // 13760 / 43 = 320 pages/book
      fastestRead: { pages: 400, days: 2 },
      longestBook: 850
    },
    
    // Goals data (ambitious but achievable for a frequent reader)
    goals: {
      books: {
        annual: { current: 43, target: 60 },
        monthly: { current: 3, target: 5 }
      },
      pages: {
        annual: { current: 13760, target: 20000 },
        monthly: { current: 960, target: 1500 }
      }
    },
    
    // Currently reading books
    currentlyReading: [
      { 
        title: 'The Seven Husbands of Evelyn Hugo', 
        author: 'Taylor Jenkins Reid', 
        progress: 65,
        totalPages: 400
      },
      { 
        title: 'Project Hail Mary', 
        author: 'Andy Weir', 
        progress: 30,
        totalPages: 500
      },
      { 
        title: 'The Way of Kings', 
        author: 'Brandon Sanderson', 
        progress: 15,
        totalPages: 1007
      }
    ],
    
    // Top genres and authors
    topGenres: [
      { name: 'Fantasy', count: 5 },
      { name: 'Mystery', count: 3 },
      { name: 'Romance', count: 2 },
      { name: 'Sci-Fi', count: 2 }
    ],
    
    topAuthors: [
      { name: 'Brandon Sanderson', count: 3 },
      { name: 'Agatha Christie', count: 2 },
      { name: 'Jane Austen', count: 2 },
      { name: 'Isaac Asimov', count: 1 }
    ],
    
    // Annual Reading Forecast data (consistent with frequent reader)
    lastYearTotals: { books: 52, pages: 16640 },
    currentYearStart: '2024-01-01'
  };

  return NextResponse.json(mockData);
}
