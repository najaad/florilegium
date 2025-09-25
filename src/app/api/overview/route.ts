import { NextResponse } from 'next/server';

export async function GET() {
  // Simple mock data - this will be replaced with real Python backend later
  const mockData = {
    totals: { books: 12, pages: 3847 },
    byMonth: [
      { month: 'Jan', count: 2 },
      { month: 'Feb', count: 1 },
      { month: 'Mar', count: 3 },
      { month: 'Apr', count: 2 },
      { month: 'May', count: 1 },
      { month: 'Jun', count: 3 },
    ]
  };

  return NextResponse.json(mockData);
}
