'use client';
import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

type Overview = {
  totals: { books: number; pages: number };
  byMonth: { month: string; count: number; pages: number }[];
  readingStats: {
    pagesPerDay: number;
    pagesPerWeek: number;
    pagesPerMonth: number;
    averageBookLength: number;
    fastestRead: { pages: number; days: number };
    longestBook: number;
  };
  goals: {
    books: {
      annual: { current: number; target: number };
      monthly: { current: number; target: number };
    };
    pages: {
      annual: { current: number; target: number };
      monthly: { current: number; target: number };
    };
  };
  currentlyReading: { title: string; author: string; progress: number; totalPages: number }[];
  topGenres: { name: string; count: number }[];
  topAuthors: { name: string; count: number }[];
  lastYearTotals: { books: number; pages: number };
  currentYearStart: string;
};

export default function Home() {
  const [data, setData] = useState<Overview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch from our mock API endpoint
    fetch('/api/overview')
      .then(r => r.json())
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <span className="loading loading-dots loading-lg" />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-base-100">
      {/* Header */}
      <div className="navbar bg-primary text-primary-content shadow-lg">
        <div className="flex-1">
          <a className="btn btn-ghost text-xl text-primary-content">💕 Hi Shannon!</a>
        </div>
        <div className="flex-none gap-2">
          <div className="dropdown dropdown-end">
            <div tabIndex={0} role="button" className="btn btn-ghost btn-circle avatar">
              <div className="w-10 rounded-full bg-primary-content text-primary">
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Welcome Section */}
      <div className="hero bg-base-200 py-12">
        <div className="hero-content text-center">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-8xl font-bold mb-4">Reading Tracker</h1>
            <p className="py-6 text-3xl mb-8">Welcome to your personal reading dashboard. Track your books, celebrate your progress, and discover your reading patterns.</p>
            
                    {/* Scrolling Currently Reading Banner */}
                    {data?.currentlyReading && data.currentlyReading.length > 0 && (
                      <div className="bg-primary/10 border border-primary/20 rounded-lg p-3 md:p-4 overflow-hidden">
                        <div className="flex flex-col md:flex-row items-center justify-center">
                          <div className="text-sm md:text-lg font-semibold text-primary mb-2 md:mb-0 md:mr-4">
                            You are currently reading {data.currentlyReading.length} book{data.currentlyReading.length !== 1 ? 's' : ''}:
                          </div>
                          <div className="flex-1 overflow-hidden w-full">
                            <div className="animate-scroll whitespace-nowrap">
                              {data.currentlyReading.map((book, index) => (
                                <span key={book.title} className="inline-block mr-6 md:mr-8 text-sm md:text-base text-base-content">
                                  <span className="font-medium">{book.title}</span> by <span className="font-medium">{book.author}</span>
                                  {index < data.currentlyReading.length - 1 && <span className="mx-2 md:mx-4 text-primary">|</span>}
                                </span>
                              ))}
                              {/* Duplicate for seamless loop */}
                              {data.currentlyReading.map((book, index) => (
                                <span key={`${book.title}-duplicate`} className="inline-block mr-6 md:mr-8 text-sm md:text-base text-base-content">
                                  <span className="font-medium">{book.title}</span> by <span className="font-medium">{book.author}</span>
                                  {index < data.currentlyReading.length - 1 && <span className="mx-2 md:mx-4 text-primary">|</span>}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <section className="max-w-7xl mx-auto p-6 space-y-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-primary text-primary-content rounded-lg shadow-lg p-8 text-center">
            <div className="text-lg font-semibold mb-2">Books Read</div>
            <div className="text-6xl font-bold mb-2">{data?.totals.books ?? 0}</div>
            <div className="text-sm opacity-90">This year</div>
          </div>

          <div className="bg-secondary text-secondary-content rounded-lg shadow-lg p-8 text-center">
            <div className="text-lg font-semibold mb-2">Pages Read</div>
            <div className="text-6xl font-bold mb-2">{data?.totals.pages?.toLocaleString() ?? 0}</div>
            <div className="text-sm opacity-90">Total pages this year</div>
          </div>

          <div className="bg-accent text-accent-content rounded-lg shadow-lg p-8 text-center">
            <div className="text-lg font-semibold mb-2">Avg per Month</div>
            <div className="text-6xl font-bold mb-2">
              {data?.byMonth ? Math.round(data.byMonth.reduce((sum, month) => sum + month.count, 0) / data.byMonth.length) : 0}
            </div>
            <div className="text-sm opacity-90">Books per month</div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Reading Progress Chart */}
                  <div className="bg-base-200 shadow-xl rounded-lg p-4 md:p-8">
                    <h2 className="text-2xl font-bold text-center mb-6">Books per Month</h2>
                    <div className="w-full h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={data?.byMonth || []} margin={{ left: 5, right: 5, top: 5, bottom: 5 }}>
                          <XAxis dataKey="month" fontSize={12} />
                          <YAxis allowDecimals={false} fontSize={12} width={30} />
                          <Tooltip />
                          <Bar dataKey="count" fill="#51796f" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                    
                    {/* Chart Stats */}
                    <div className="grid grid-cols-2 gap-4 mt-6">
                      <div className="bg-primary/10 rounded-xl p-4 text-center border border-primary/20">
                        <div className="text-2xl font-bold text-primary mb-1">
                          {data?.byMonth.reduce((max, month) => month.count > max.count ? month : max, { count: 0, month: 'None' }).month}
                        </div>
                        <div className="text-sm font-medium opacity-80">
                          {data?.byMonth.reduce((max, month) => month.count > max.count ? month : max, { count: 0, month: 'None' }).count} Books
                        </div>
                        <div className="text-xs opacity-60 mt-1">Most books read</div>
                      </div>
                      <div className="bg-secondary/10 rounded-xl p-4 text-center border border-secondary/20">
                        <div className="text-2xl font-bold text-secondary mb-1">
                          {data?.byMonth.reduce((max, month) => month.pages > max.pages ? month : max, { pages: 0, month: 'None' }).month}
                        </div>
                        <div className="text-sm font-medium opacity-80">
                          {data?.byMonth.reduce((max, month) => month.pages > max.pages ? month : max, { pages: 0, month: 'None' }).pages} Pages
                        </div>
                        <div className="text-xs opacity-60 mt-1">Most pages read</div>
                      </div>
                    </div>
                  </div>

          {/* Reading Stats Card */}
          <div className="bg-base-200 shadow-xl rounded-lg p-4 md:p-8">
            <h2 className="text-2xl font-bold text-center mb-6">Reading Stats</h2>
            
            {/* Top Section - Daily/Weekly/Monthly */}
            <div className="grid grid-cols-3 gap-2 md:gap-4 mb-6">
              <div className="bg-primary/10 rounded-xl p-2 md:p-4 text-center border border-primary/20">
                <div className="text-xl md:text-3xl font-bold text-primary mb-1">{data?.readingStats.pagesPerDay || 0}</div>
                <div className="text-xs md:text-sm font-medium opacity-80">pages/day</div>
              </div>
              <div className="bg-secondary/10 rounded-xl p-2 md:p-4 text-center border border-secondary/20">
                <div className="text-xl md:text-3xl font-bold text-secondary mb-1">{data?.readingStats.pagesPerWeek || 0}</div>
                <div className="text-xs md:text-sm font-medium opacity-80">pages/week</div>
              </div>
              <div className="bg-accent/10 rounded-xl p-2 md:p-4 text-center border border-accent/20">
                <div className="text-xl md:text-3xl font-bold text-accent mb-1">{data?.readingStats.pagesPerMonth || 0}</div>
                <div className="text-xs md:text-sm font-medium opacity-80">pages/month</div>
              </div>
            </div>

            {/* Bottom Section - Records */}
            <div className="space-y-4">
              <div className="bg-base-100 rounded-xl p-4 border border-base-300">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm opacity-70 mb-1">Average Book Length</div>
                    <div className="text-xl font-bold text-primary">{data?.readingStats.averageBookLength || 0} pages</div>
                  </div>
                  <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                    <div className="w-6 h-6 bg-primary rounded-full"></div>
                  </div>
                </div>
              </div>
              
              <div className="bg-base-100 rounded-xl p-4 border border-base-300">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm opacity-70 mb-1">Fastest Read</div>
                    <div className="text-xl font-bold text-secondary">
                      {data?.readingStats.fastestRead.pages || 0} pages in {data?.readingStats.fastestRead.days || 0} days
                    </div>
                  </div>
                  <div className="w-12 h-12 bg-secondary/10 rounded-full flex items-center justify-center">
                    <div className="w-6 h-6 bg-secondary rounded-full"></div>
                  </div>
                </div>
              </div>
              
              <div className="bg-base-100 rounded-xl p-4 border border-base-300">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm opacity-70 mb-1">Longest Book</div>
                    <div className="text-xl font-bold text-accent">{data?.readingStats.longestBook || 0} pages</div>
                  </div>
                  <div className="w-12 h-12 bg-accent/10 rounded-full flex items-center justify-center">
                    <div className="w-6 h-6 bg-accent rounded-full"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Goals Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Books Goals Card */}
          <div className="bg-base-200 shadow-xl rounded-lg p-8">
            <h2 className="text-2xl font-bold text-center mb-6">Books Goals</h2>
            <div className="space-y-6">
              <div className="text-center">
                <div className="text-4xl font-bold mb-2">
                  {data?.goals.books.annual.current || 0}/{data?.goals.books.annual.target || 0}
                </div>
                <div className="text-lg font-semibold mb-2">Annual Goal</div>
                <div className="relative w-full bg-base-100 rounded-full h-6 overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all duration-500 ease-out"
                    style={{ 
                      width: `${data?.goals.books.annual.target ? 
                        (data.goals.books.annual.current / data.goals.books.annual.target) * 100 : 0}%` 
                    }}
                  ></div>
                </div>
                <div className="text-sm opacity-70 mt-2">
                  {data?.goals.books.annual.target ? 
                    Math.round((data.goals.books.annual.current / data.goals.books.annual.target) * 100) : 0}% complete
                </div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold mb-2">
                  {data?.goals.books.monthly.current || 0}/{data?.goals.books.monthly.target || 0}
                </div>
                <div className="text-lg font-semibold mb-2">Monthly Goal</div>
                <div className="relative w-full bg-base-100 rounded-full h-6 overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all duration-500 ease-out"
                    style={{ 
                      width: `${data?.goals.books.monthly.target ? 
                        (data.goals.books.monthly.current / data.goals.books.monthly.target) * 100 : 0}%` 
                    }}
                  ></div>
                </div>
                <div className="text-sm opacity-70 mt-2">
                  {data?.goals.books.monthly.target ? 
                    Math.round((data.goals.books.monthly.current / data.goals.books.monthly.target) * 100) : 0}% complete
                </div>
              </div>
            </div>
          </div>

          {/* Pages Goals Card */}
          <div className="bg-base-200 shadow-xl rounded-lg p-8">
            <h2 className="text-2xl font-bold text-center mb-6">Pages Goals</h2>
            <div className="space-y-6">
              <div className="text-center">
                <div className="text-4xl font-bold mb-2">
                  {(data?.goals.pages.annual.current || 0).toLocaleString()}/{(data?.goals.pages.annual.target || 0).toLocaleString()}
                </div>
                <div className="text-lg font-semibold mb-2">Annual Goal</div>
                <div className="relative w-full bg-base-100 rounded-full h-6 overflow-hidden">
                  <div
                    className="h-full bg-secondary rounded-full transition-all duration-500 ease-out"
                    style={{ 
                      width: `${data?.goals.pages.annual.target ? 
                        (data.goals.pages.annual.current / data.goals.pages.annual.target) * 100 : 0}%` 
                    }}
                  ></div>
                </div>
                <div className="text-sm opacity-70 mt-2">
                  {data?.goals.pages.annual.target ? 
                    Math.round((data.goals.pages.annual.current / data.goals.pages.annual.target) * 100) : 0}% complete
                </div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold mb-2">
                  {data?.goals.pages.monthly.current || 0}/{data?.goals.pages.monthly.target || 0}
                </div>
                <div className="text-lg font-semibold mb-2">Monthly Goal</div>
                <div className="relative w-full bg-base-100 rounded-full h-6 overflow-hidden">
                  <div
                    className="h-full bg-secondary rounded-full transition-all duration-500 ease-out"
                    style={{ 
                      width: `${data?.goals.pages.monthly.target ? 
                        (data.goals.pages.monthly.current / data.goals.pages.monthly.target) * 100 : 0}%` 
                    }}
                  ></div>
                </div>
                <div className="text-sm opacity-70 mt-2">
                  {data?.goals.pages.monthly.target ? 
                    Math.round((data.goals.pages.monthly.current / data.goals.pages.monthly.target) * 100) : 0}% complete
                </div>
              </div>
            </div>
          </div>
        </div>

                {/* Reading Insights */}
                <div className="space-y-6">
                  {/* Genres Row */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Top Genres */}
                    <div className="bg-base-200 shadow-xl rounded-lg p-8">
                      <h2 className="text-2xl font-bold text-center mb-6">Top Genres</h2>
                      <div className="space-y-4">
                        {data?.topGenres.map((genre, index) => {
                          const colors = ['bg-primary', 'bg-secondary', 'bg-accent', 'bg-base-content'];
                          const totalBooks = data.totals.books;
                          const percentage = totalBooks ? Math.round((genre.count / totalBooks) * 100) : 0;
                          return (
                            <div key={genre.name} className="flex items-center justify-between p-4 bg-base-100 rounded-lg">
                              <div className="flex items-center space-x-4">
                                <div className={`w-6 h-6 ${colors[index % colors.length]} rounded-full`}></div>
                                <span className="text-lg font-semibold">{genre.name}</span>
                              </div>
                              <div className="text-right">
                                <div className="text-2xl font-bold">{genre.count}</div>
                                <div className="text-sm opacity-70">{percentage}%</div>
                              </div>
                            </div>
                          );
                        }) || (
                          <div className="text-center text-gray-500 p-4">No genre data available</div>
                        )}
                      </div>
                    </div>

                    {/* Genre Placeholder */}
                    <div className="bg-base-200 shadow-xl rounded-lg p-8">
                      <h2 className="text-2xl font-bold text-center mb-6">Coming Soon</h2>
                      <div className="text-center py-12">
                        <div className="text-6xl mb-4">hiiiii</div>
                        <p className="text-lg opacity-70">Next genre insight will go here!</p>
                        <p className="text-sm opacity-50 mt-2">imagine more genre analytics</p>
                      </div>
                    </div>
                  </div>

                  {/* Authors Row */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Top Authors */}
                    <div className="bg-base-200 shadow-xl rounded-lg p-8">
                      <h2 className="text-2xl font-bold text-center mb-6">Top Authors</h2>
                      <div className="space-y-4">
                        {data?.topAuthors.map((author, index) => {
                          const colors = ['bg-primary text-primary-content', 'bg-secondary text-secondary-content', 'bg-accent text-accent-content', 'bg-base-content text-base-100'];
                          const totalBooks = data.totals.books;
                          const percentage = totalBooks ? Math.round((author.count / totalBooks) * 100) : 0;
                          const initials = author.name.split(' ').map(n => n[0]).join('').toUpperCase();
                          return (
                            <div key={author.name} className="flex items-center space-x-4 p-4 bg-base-100 rounded-lg">
                              <div className={`${colors[index % colors.length]} rounded-full w-12 h-12 flex items-center justify-center`}>
                                <span className="text-sm font-bold">{initials}</span>
                              </div>
                              <div className="flex-1">
                                <div className="text-lg font-semibold">{author.name}</div>
                                <div className="text-sm opacity-70">{author.count} book{author.count !== 1 ? 's' : ''} read</div>
                              </div>
                              <div className="text-right">
                                <div className="text-2xl font-bold">{percentage}%</div>
                              </div>
                            </div>
                          );
                        }) || (
                          <div className="text-center text-gray-500 p-4">No author data available</div>
                        )}
                      </div>
                    </div>

                    {/* Author Placeholder */}
                    <div className="bg-base-200 shadow-xl rounded-lg p-8">
                      <h2 className="text-2xl font-bold text-center mb-6">Coming Soon</h2>
                      <div className="text-center py-12">
                        <div className="text-6xl mb-4">bloop</div>
                        <p className="text-lg opacity-70">soon more author insight will go here!</p>
                        <p className="text-sm opacity-50 mt-2">imagine more author analytics</p>
                      </div>
                    </div>
                  </div>
                </div>

        {/* Interactive Tools Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Pacing Calculator */}
          <div className="bg-base-200 shadow-xl rounded-lg p-8">
            <h2 className="text-2xl font-bold text-center mb-6">Pacing Calculator</h2>
            <PacingCalculator books={data?.currentlyReading || []} />
          </div>

                  {/* Annual Reading Forecast */}
                  <div className="bg-base-200 shadow-xl rounded-lg p-8">
                    <h2 className="text-2xl font-bold text-center mb-6">Annual Reading Forecast</h2>
                    <AnnualReadingForecast data={data} />
                  </div>
        </div>

      </section>
      </main>
  );
}

// Pacing Calculator Component
function PacingCalculator({ books }: { books: { title: string; author: string; progress: number; totalPages: number }[] }) {
  const [selectedBook, setSelectedBook] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<number>(0);
  const [goalDate, setGoalDate] = useState<string>('');
  const [timeframe, setTimeframe] = useState<'week' | 'month' | 'year' | 'custom'>('month');

  const selectedBookData = books.find(book => book.title === selectedBook);
  const today = new Date();
  
  // Calculate goal date based on timeframe
  const getGoalDate = () => {
    const date = new Date(today);
    switch (timeframe) {
      case 'week':
        date.setDate(date.getDate() + 7);
        break;
      case 'month':
        date.setMonth(date.getMonth() + 1);
        break;
      case 'year':
        date.setFullYear(date.getFullYear() + 1);
        break;
      case 'custom':
        return goalDate ? new Date(goalDate) : null;
    }
    return date;
  };

  const calculatePacing = () => {
    if (!selectedBookData || currentPage <= 0 || currentPage >= selectedBookData.totalPages) {
      return null;
    }

    const goalDateObj = getGoalDate();
    if (!goalDateObj) return null;

    const daysRemaining = Math.ceil((goalDateObj.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    if (daysRemaining <= 0) return null;

    const pagesRemaining = selectedBookData.totalPages - currentPage;
    const pagesPerDay = pagesRemaining / daysRemaining;

    return {
      daysRemaining,
      pagesRemaining,
      pagesPerDay,
      isRealistic: pagesPerDay <= 50,
      isEasy: pagesPerDay <= 20,
      goalDate: goalDateObj.toLocaleDateString()
    };
  };

  const pacing = calculatePacing();

  return (
    <div className="space-y-6">
      {/* Book Selector */}
      <div className="bg-base-100 rounded-xl p-4 md:p-6 border border-base-300 shadow-sm">
        <label className="block text-lg font-semibold text-base-content mb-4">Choose Your Book</label>
        <div className="relative">
          <select 
            className="w-full px-4 py-3 bg-white border-2 border-base-300 rounded-lg text-base-content hover:border-primary/50 focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200 appearance-none cursor-pointer text-sm md:text-base"
            value={selectedBook}
            onChange={(e) => {
              setSelectedBook(e.target.value);
              setCurrentPage(0);
            }}
          >
            <option value="">Pick a book to calculate pacing...</option>
            {books.map((book) => (
              <option key={book.title} value={book.title}>
                {book.title} by {book.author}
              </option>
            ))}
          </select>
          <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
            <svg className="w-5 h-5 text-base-content/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </div>

      {/* Current Page Input */}
      {selectedBookData && (
        <div className="bg-base-100 rounded-xl p-6 border border-base-300 shadow-sm">
          <label className="block text-lg font-semibold text-base-content mb-4">
            Current Page (Total: {selectedBookData.totalPages} pages)
          </label>
          <input 
            type="number" 
            className="w-full px-4 py-3 bg-white border-2 border-base-300 rounded-lg text-base-content placeholder-base-content/50 hover:border-primary/50 focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200"
            value={currentPage || ''}
            onChange={(e) => setCurrentPage(parseInt(e.target.value) || 0)}
            min="1"
            max={selectedBookData.totalPages - 1}
            placeholder="Enter your current page..."
          />
        </div>
      )}

      {/* Timeframe Selector */}
      <div className="bg-base-100 rounded-xl p-6 border border-base-300 shadow-sm">
        <label className="block text-lg font-semibold text-base-content mb-4">Goal Timeframe</label>
        <div className="grid grid-cols-2 gap-3 mb-4">
          {(['week', 'month', 'year', 'custom'] as const).map((tf) => (
            <button
              key={tf}
              className={`
                relative px-4 py-3 rounded-lg font-medium text-sm transition-all duration-200 transform
                ${timeframe === tf 
                  ? 'bg-primary text-primary-content shadow-lg scale-105 border-2 border-primary' 
                  : 'bg-base-200 text-base-content hover:bg-base-300 hover:scale-102 border-2 border-transparent hover:border-primary/30'
                }
                focus:outline-none focus:ring-2 focus:ring-primary/20
              `}
              onClick={() => setTimeframe(tf)}
            >
              <span className="relative z-10">{tf.charAt(0).toUpperCase() + tf.slice(1)}</span>
              {timeframe === tf && (
                <div className="absolute inset-0 bg-gradient-to-r from-primary to-primary/80 rounded-lg opacity-90"></div>
              )}
            </button>
          ))}
        </div>
        {timeframe === 'custom' && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-base-content mb-2">Select Target Date</label>
            <div className="relative">
              <input 
                type="date" 
                className="w-full px-4 py-3 bg-white border-2 border-base-300 rounded-lg text-base-content hover:border-primary/50 focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200 text-lg"
                value={goalDate}
                onChange={(e) => setGoalDate(e.target.value)}
                min={today.toISOString().split('T')[0]}
              />
              <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      {pacing && (
        <div className="bg-gradient-to-br from-primary/10 to-secondary/10 rounded-xl p-6 border border-primary/20">
          <div className="text-center">
            <div className="text-4xl font-bold text-primary mb-2">
              {pacing.pagesPerDay.toFixed(1)} pages/day
            </div>
            <div className="text-lg opacity-80 mb-4">
              {pacing.pagesRemaining} pages remaining in {pacing.daysRemaining} days
            </div>
            <div className={`badge badge-lg ${pacing.isEasy ? 'badge-success' : pacing.isRealistic ? 'badge-warning' : 'badge-error'}`}>
              {pacing.isEasy ? 'Easy Goal' : pacing.isRealistic ? 'Challenging Goal' : 'Ambitious Goal'}
            </div>
            <div className="text-sm opacity-60 mt-3">
              Target: {pacing.goalDate}
            </div>
          </div>
        </div>
      )}

      {/* Helpful Tips */}
      {selectedBookData && !pacing && (
        <div className="bg-base-100 rounded-xl p-4 border border-base-300">
          <div className="text-center text-sm opacity-70">
            Enter your current page number to see your reading pace!
          </div>
        </div>
      )}
    </div>
  );
}

// Annual Reading Forecast Component
function AnnualReadingForecast({ data }: { data: Overview | null }) {
  if (!data) return null;

  const currentDate = new Date();
  const currentMonth = currentDate.getMonth() + 1; // 1-12
  const currentYear = currentDate.getFullYear();
  
  // Calculate monthly averages based on completed months
  const completedMonths = currentMonth - 1; // Months that have fully passed
  const monthsRemaining = 12 - currentMonth; // Months left in the year
  
  // For January, use last year's data
  const isJanuary = currentMonth === 1;
  
  let booksPerMonth: number;
  let pagesPerMonth: number;
  let estimatedBooks: number;
  let estimatedPages: number;
  
  if (isJanuary) {
    // In January, use last year's totals as baseline
    booksPerMonth = data.lastYearTotals.books / 12;
    pagesPerMonth = data.lastYearTotals.pages / 12;
    estimatedBooks = Math.round(booksPerMonth * 12);
    estimatedPages = Math.round(pagesPerMonth * 12);
  } else {
    // Calculate based on current year's progress
    booksPerMonth = completedMonths > 0 ? data.totals.books / completedMonths : 0;
    pagesPerMonth = completedMonths > 0 ? data.totals.pages / completedMonths : 0;
    estimatedBooks = Math.round(data.totals.books + (booksPerMonth * monthsRemaining));
    estimatedPages = Math.round(data.totals.pages + (pagesPerMonth * monthsRemaining));
  }
  
  // Calculate average book length for conversion
  const averageBookLength = data.totals.books > 0 ? data.totals.pages / data.totals.books : 320;
  const estimatedBooksFromPages = Math.round(estimatedPages / averageBookLength);

  return (
    <div className="space-y-6">
      {/* Books Forecast */}
      <div className="bg-base-100 rounded-xl p-6 border border-base-300 shadow-sm">
        <div className="text-center">
          <div className="text-3xl font-bold text-primary mb-2">
            {estimatedBooks} books
          </div>
          <div className="text-sm opacity-70 mb-4">Estimated by year-end</div>
          <div className="text-lg font-semibold text-base-content mb-2">
            Based on {isJanuary ? 'last year' : `${completedMonths} completed month${completedMonths !== 1 ? 's' : ''}`}
          </div>
          <div className="text-sm opacity-60">
            {isJanuary ? 
              `Last year: ${data.lastYearTotals.books} books (${(data.lastYearTotals.books / 12).toFixed(1)}/month)` :
              `Current pace: ${booksPerMonth.toFixed(1)} books/month`
            }
          </div>
        </div>
      </div>

      {/* Pages Forecast */}
      <div className="bg-base-100 rounded-xl p-6 border border-base-300 shadow-sm">
        <div className="text-center">
          <div className="text-3xl font-bold text-secondary mb-2">
            {estimatedPages.toLocaleString()} pages
          </div>
          <div className="text-sm opacity-70 mb-4">Estimated by year-end</div>
          <div className="text-lg font-semibold text-base-content mb-2">
            Based on {isJanuary ? 'last year' : `${completedMonths} completed month${completedMonths !== 1 ? 's' : ''}`}
          </div>
          <div className="text-sm opacity-60">
            {isJanuary ? 
              `Last year: ${data.lastYearTotals.pages.toLocaleString()} pages (${(data.lastYearTotals.pages / 12).toLocaleString()}/month)` :
              `Current pace: ${pagesPerMonth.toLocaleString()} pages/month`
            }
          </div>
        </div>
      </div>

      {/* Cross-Reference */}
      <div className="bg-gradient-to-br from-accent/10 to-primary/10 rounded-xl p-4 border border-accent/20">
        <div className="text-center">
          <div className="text-sm font-semibold text-accent mb-2">Cross-Reference Check</div>
          <div className="text-xs opacity-70">
            Pages estimate converts to ~{estimatedBooksFromPages} books 
            (based on your {averageBookLength.toFixed(0)}-page average)
          </div>
        </div>
      </div>
    </div>
  );
}