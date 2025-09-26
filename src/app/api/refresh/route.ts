import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // Try multiple paths to find structured data - check public directory first for Vercel
    const possiblePaths = [
      path.join(process.cwd(), 'public', 'structured_reading_data.json'),      // Primary (Vercel-friendly path)
      path.join(process.cwd(), 'data', 'structured_reading_data.json'),       // Fallback for local dev
      path.join(process.cwd(), '..', 'data', 'structured_reading_data.json'),
    ];

    for (const dataPath of possiblePaths) {
      if (fs.existsSync(dataPath)) {
        const fileContents = fs.readFileSync(dataPath, 'utf8');
        const realData = JSON.parse(fileContents);
        
        console.log(`📊 Loaded real reading data from ${dataPath}`);
        return NextResponse.json(realData);
      }
    }
    
    console.log('⚠️ structured_reading_data.json not found in any expected location');
  } catch (error) {
    console.error('Error loading structured reading data:', error);
  }

  // Fallback to mock data if real data unavailable
  console.log('🔄 Using mock data as fallback');
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
      { name: 'Sci-Fi', count: 2 },
      { name: 'Thriller', count: 2 },
      { name: 'Historical Fiction', count: 1 }
    ],
    
    topAuthors: [
      { name: 'Brandon Sanderson', count: 3 },
      { name: 'Agatha Christie', count: 2 },
      { name: 'Jane Austen', count: 2 },
      { name: 'Isaac Asimov', count: 1 },
      { name: 'Neil Gaiman', count: 1 },
      { name: 'Ursula K. Le Guin', count: 1 }
    ],
    
    // Annual Reading Forecast data (consistent with frequent reader)
    lastYearTotals: { books: 52, pages: 16640 },
    currentYearStart: '2024-01-01',
    
    // Longest books by genre (top 3)
    longestBooksByGenre: [
      { genre: 'Fantasy', title: 'The Way of Kings', author: 'Brandon Sanderson', pages: 1007 },
      { genre: 'Mystery', title: 'The Murder of Roger Ackroyd', author: 'Agatha Christie', pages: 320 },
      { genre: 'Romance', title: 'Pride and Prejudice', author: 'Jane Austen', pages: 432 }
    ],
    
    // Genre reading patterns
    consistentGenres: [
      { name: 'Fantasy', currentYear: 5, pastYears: 6, totalBooks: 11 },
      { name: 'Mystery', currentYear: 3, pastYears: 4, totalBooks: 7 },
      { name: 'Romance', currentYear: 2, pastYears: 3, totalBooks: 5 }
    ],
    
    // Author reading patterns
    consistentAuthors: [
      { name: 'Brandon Sanderson', currentYear: 3, pastYears: 4, totalBooks: 7 },
      { name: 'Agatha Christie', currentYear: 2, pastYears: 3, totalBooks: 5 },
      { name: 'Jane Austen', currentYear: 2, pastYears: 2, totalBooks: 4 }
    ],
    
            longestBooksByAuthor: [
              { author: 'Brandon Sanderson', title: 'The Way of Kings', pages: 1007 },
              { author: 'Agatha Christie', title: 'The Murder of Roger Ackroyd', pages: 320 },
              { author: 'Jane Austen', title: 'Pride and Prejudice', pages: 432 }
            ],
            
            // TBR (To Be Read) list for randomizer
            tbrList: [
              { title: 'The Midnight Library', author: 'Matt Haig', genre: 'Fiction' },
              { title: 'Circe', author: 'Madeline Miller', genre: 'Fantasy' },
              { title: 'The Seven Husbands of Evelyn Hugo', author: 'Taylor Jenkins Reid', genre: 'Historical Fiction' },
              { title: 'Project Hail Mary', author: 'Andy Weir', genre: 'Sci-Fi' },
              { title: 'The Way of Kings', author: 'Brandon Sanderson', genre: 'Fantasy' },
              { title: 'Dune', author: 'Frank Herbert', genre: 'Sci-Fi' },
              { title: 'The Silent Patient', author: 'Alex Michaelides', genre: 'Thriller' },
              { title: 'Educated', author: 'Tara Westover', genre: 'Memoir' },
              { title: 'The Book Thief', author: 'Markus Zusak', genre: 'Historical Fiction' },
              { title: 'The Night Circus', author: 'Erin Morgenstern', genre: 'Fantasy' },
              { title: 'Where the Crawdads Sing', author: 'Delia Owens', genre: 'Fiction' },
              { title: 'The Alchemist', author: 'Paulo Coelho', genre: 'Fiction' }
            ]
  };

  return NextResponse.json(mockData);
}
