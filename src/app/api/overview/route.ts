import { NextResponse } from 'next/server';

export async function GET() {
  // Complete mock data structure - this shows exactly what your Python API needs to provide
  const mockData = {
    // Main stats
    totals: { books: 12, pages: 3847 },
    
    // Chart data
    byMonth: [
      { month: 'Jan', count: 2 },
      { month: 'Feb', count: 1 },
      { month: 'Mar', count: 3 },
      { month: 'Apr', count: 2 },
      { month: 'May', count: 1 },
      { month: 'Jun', count: 3 },
    ],
    
    // Reading stats (daily/weekly/monthly averages)
    readingStats: {
      pagesPerDay: 15,
      pagesPerWeek: 105,
      pagesPerMonth: 450,
      averageBookLength: 320,
      fastestRead: { pages: 180, days: 3 },
      longestBook: 650
    },
    
    // Goals data
    goals: {
      books: {
        annual: { current: 12, target: 24 },
        monthly: { current: 2, target: 4 }
      },
      pages: {
        annual: { current: 1000, target: 2000 },
        monthly: { current: 150, target: 200 }
      }
    },
    
    // Currently reading books
    currentlyReading: [
      { title: 'The Seven Husbands of Evelyn Hugo', author: 'Taylor Jenkins Reid', progress: 65 },
      { title: 'Project Hail Mary', author: 'Andy Weir', progress: 30 },
      { title: 'The Way of Kings', author: 'Brandon Sanderson', progress: 15 }
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
    ]
  };

  return NextResponse.json(mockData);
}
