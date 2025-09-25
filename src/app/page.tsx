'use client';
import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

type Overview = {
  totals: { books: number; pages: number };
  byMonth: { month: string; count: number }[];
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
          <div className="max-w-md mx-auto">
            <h1 className="text-5xl font-bold">Reading Tracker</h1>
            <p className="py-6 text-lg">Welcome to your personal reading dashboard. Track your books, celebrate your progress, and discover your reading patterns.</p>
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
            <div className="text-sm opacity-90">Total pages</div>
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

          {/* Reading Goals Card */}
          <div className="bg-base-200 shadow-xl rounded-lg p-8">
            <h2 className="text-2xl font-bold text-center mb-6">Reading Goals</h2>
            <div className="space-y-6">
              <div className="text-center">
                <div className="text-4xl font-bold mb-2">12/24</div>
                <div className="text-lg font-semibold mb-2">Annual Goal</div>
                <div className="relative w-full bg-base-100 rounded-full h-6 overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all duration-500 ease-out"
                    style={{ width: '50%' }}
                  ></div>
                </div>
                <div className="text-sm opacity-70 mt-2">50% complete</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold mb-2">3/4</div>
                <div className="text-lg font-semibold mb-2">Monthly Goal</div>
                <div className="relative w-full bg-base-100 rounded-full h-6 overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all duration-500 ease-out"
                    style={{ width: '75%' }}
                  ></div>
                </div>
                <div className="text-sm opacity-70 mt-2">75% complete</div>
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
              <div className="flex items-center justify-between p-4 bg-base-100 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-6 h-6 bg-primary rounded-full"></div>
                  <span className="text-lg font-semibold">Fiction</span>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">5</div>
                  <div className="text-sm opacity-70">42%</div>
                </div>
              </div>
              <div className="flex items-center justify-between p-4 bg-base-100 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-6 h-6 bg-secondary rounded-full"></div>
                  <span className="text-lg font-semibold">Mystery</span>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">3</div>
                  <div className="text-sm opacity-70">25%</div>
                </div>
              </div>
              <div className="flex items-center justify-between p-4 bg-base-100 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-6 h-6 bg-accent rounded-full"></div>
                  <span className="text-lg font-semibold">Fantasy</span>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">2</div>
                  <div className="text-sm opacity-70">17%</div>
                </div>
              </div>
              <div className="flex items-center justify-between p-4 bg-base-100 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-6 h-6 bg-neutral rounded-full"></div>
                  <span className="text-lg font-semibold">Non-fiction</span>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">2</div>
                  <div className="text-sm opacity-70">17%</div>
                </div>
              </div>
            </div>
          </div>

          {/* Top Authors */}
          <div className="bg-base-200 shadow-xl rounded-lg p-8">
            <h2 className="text-2xl font-bold text-center mb-6">Top Authors</h2>
            <div className="space-y-4">
              <div className="flex items-center space-x-4 p-4 bg-base-100 rounded-lg">
                <div className="bg-primary text-primary-content rounded-full w-12 h-12 flex items-center justify-center">
                  <span className="text-sm font-bold">TJ</span>
                </div>
                <div className="flex-1">
                  <div className="text-lg font-semibold">Taylor Jenkins Reid</div>
                  <div className="text-sm opacity-70">3 books read</div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">25%</div>
                </div>
              </div>
              <div className="flex items-center space-x-4 p-4 bg-base-100 rounded-lg">
                <div className="bg-secondary text-secondary-content rounded-full w-12 h-12 flex items-center justify-center">
                  <span className="text-sm font-bold">AW</span>
                </div>
                <div className="flex-1">
                  <div className="text-lg font-semibold">Andy Weir</div>
                  <div className="text-sm opacity-70">2 books read</div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">17%</div>
                </div>
              </div>
              <div className="flex items-center space-x-4 p-4 bg-base-100 rounded-lg">
                <div className="bg-accent text-accent-content rounded-full w-12 h-12 flex items-center justify-center">
                  <span className="text-sm font-bold">BS</span>
                </div>
                <div className="flex-1">
                  <div className="text-lg font-semibold">Brandon Sanderson</div>
                  <div className="text-sm opacity-70">2 books read</div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">17%</div>
                </div>
              </div>
              <div className="flex items-center space-x-4 p-4 bg-base-100 rounded-lg">
                <div className="bg-neutral text-neutral-content rounded-full w-12 h-12 flex items-center justify-center">
                  <span className="text-sm font-bold">+5</span>
                </div>
                <div className="flex-1">
                  <div className="text-lg font-semibold">5 other authors</div>
                  <div className="text-sm opacity-70">1 book each</div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">42%</div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </section>
    </main>
  );
}