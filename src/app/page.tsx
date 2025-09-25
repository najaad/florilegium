'use client';
import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

type Overview = {
  totals: { books: number; pages: number };
  byMonth: { month: string; count: number }[];
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
  currentlyReading: { title: string; author: string; progress: number }[];
  topGenres: { name: string; count: number }[];
  topAuthors: { name: string; count: number }[];
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
              <div className="bg-primary/10 border border-primary/20 rounded-lg p-4 overflow-hidden">
                <div className="flex items-center justify-center">
                  <div className="text-lg font-semibold text-primary mr-4">
                    You are currently reading {data.currentlyReading.length} book{data.currentlyReading.length !== 1 ? 's' : ''}:
                  </div>
                  <div className="flex-1 overflow-hidden">
                    <div className="animate-scroll whitespace-nowrap">
                      {data.currentlyReading.map((book, index) => (
                        <span key={book.title} className="inline-block mr-8 text-base-content">
                          <span className="font-medium">{book.title}</span> by <span className="font-medium">{book.author}</span>
                          {index < data.currentlyReading.length - 1 && <span className="mx-4 text-primary">|</span>}
                        </span>
                      ))}
                      {/* Duplicate for seamless loop */}
                      {data.currentlyReading.map((book, index) => (
                        <span key={`${book.title}-duplicate`} className="inline-block mr-8 text-base-content">
                          <span className="font-medium">{book.title}</span> by <span className="font-medium">{book.author}</span>
                          {index < data.currentlyReading.length - 1 && <span className="mx-4 text-primary">|</span>}
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
          <div className="bg-base-200 shadow-xl rounded-lg p-8">
            <h2 className="text-2xl font-bold text-center mb-6">Books per Month</h2>
            <div className="w-full h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data?.byMonth || []}>
                  <XAxis dataKey="month" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#51796f" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Reading Stats Card */}
          <div className="bg-base-200 shadow-xl rounded-lg p-8">
            <h2 className="text-2xl font-bold text-center mb-6">Reading Stats</h2>
            
            {/* Top Section - Daily/Weekly/Monthly */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="bg-primary/10 rounded-xl p-4 text-center border border-primary/20">
                <div className="text-3xl font-bold text-primary mb-1">{data?.readingStats.pagesPerDay || 0}</div>
                <div className="text-sm font-medium opacity-80">pages/day</div>
              </div>
              <div className="bg-secondary/10 rounded-xl p-4 text-center border border-secondary/20">
                <div className="text-3xl font-bold text-secondary mb-1">{data?.readingStats.pagesPerWeek || 0}</div>
                <div className="text-sm font-medium opacity-80">pages/week</div>
              </div>
              <div className="bg-accent/10 rounded-xl p-4 text-center border border-accent/20">
                <div className="text-3xl font-bold text-accent mb-1">{data?.readingStats.pagesPerMonth || 0}</div>
                <div className="text-sm font-medium opacity-80">pages/month</div>
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
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Genres */}
          <div className="bg-base-200 shadow-xl rounded-lg p-8">
            <h2 className="text-2xl font-bold text-center mb-6">Top Genres</h2>
            <div className="space-y-4">
              {data?.topGenres.map((genre, index) => {
                const colors = ['bg-primary', 'bg-secondary', 'bg-accent', 'bg-neutral'];
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

          {/* Top Authors */}
          <div className="bg-base-200 shadow-xl rounded-lg p-8">
            <h2 className="text-2xl font-bold text-center mb-6">Top Authors</h2>
            <div className="space-y-4">
              {data?.topAuthors.map((author, index) => {
                const colors = ['bg-primary text-primary-content', 'bg-secondary text-secondary-content', 'bg-accent text-accent-content', 'bg-neutral text-neutral-content'];
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
        </div>

      </section>
    </main>
  );
}