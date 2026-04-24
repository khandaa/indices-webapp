import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiService } from '../services/api';

interface WeekData {
  week: string;
  week_display: string;
  start_date: string;
  end_date: string;
  is_past: boolean;
  data_available: boolean;
  recommendations: {
    rank: number;
    index_id: number;
    name: string;
    symbol: string;
    weekly_change_percent: number | null;
    three_week_cumulative_return: number | null;
  }[];
  niftybees: {
    weekly_change_percent: number | null;
    three_week_cumulative_return: number | null;
  } | null;
}

interface MonthData {
  month: string;
  month_display: string;
  start_date: string;
  end_date: string;
  is_past: boolean;
  data_available: boolean;
  recommendations: {
    rank: number;
    index_id: number;
    name: string;
    symbol: string;
    monthly_change_percent: number | null;
    three_month_cumulative_return: number | null;
  }[];
  niftybees: {
    monthly_change_percent: number | null;
    three_month_cumulative_return: number | null;
  } | null;
}

interface FreshnessData {
  indices: {
    index_id: number;
    name: string;
    symbol: string;
    last_data_date: string | null;
    is_fresh: boolean;
    needs_refresh: boolean;
  }[];
  summary: {
    total: number;
    fresh: number;
    needs_refresh: number;
  };
}

const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'weekly' | 'monthly'>('weekly');
  const [pastWeeks, setPastWeeks] = useState(6);
  const [pastMonths, setPastMonths] = useState(4);
  const [includeUpcoming, setIncludeUpcoming] = useState(true);
  const [weeklyData, setWeeklyData] = useState<WeekData[]>([]);
  const [monthlyData, setMonthlyData] = useState<MonthData[]>([]);
  const [freshness, setFreshness] = useState<FreshnessData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, [activeTab, pastWeeks, pastMonths, includeUpcoming]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'weekly') {
        const data = await apiService.getWeeklyRecommendationsWithParams(pastWeeks, includeUpcoming);
        setWeeklyData(data.weeks || []);
      } else {
        const data = await apiService.getMonthlyRecommendationsWithParams(pastMonths, includeUpcoming);
        setMonthlyData(data.months || []);
      }
      const freshnessData = await apiService.checkDataFreshness();
      setFreshness(freshnessData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await apiService.refreshData(activeTab === 'weekly' ? 'weekly' : 'monthly');
      await loadData();
    } catch (error) {
      console.error('Error refreshing data:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const formatPercent = (value: number | null | undefined): string => {
    if (value === null || value === undefined) return 'N/A';
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const isFresh = freshness?.summary?.fresh !== undefined && freshness.summary.fresh > 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <button
          onClick={handleRefresh}
          disabled={refreshing || isFresh}
          className={`px-4 py-2 rounded-md font-medium ${
            refreshing
              ? 'bg-gray-400 text-white cursor-wait'
              : isFresh
              ? 'bg-green-100 text-green-800 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {refreshing ? 'Refreshing...' : isFresh ? 'Data Fresh' : 'Refresh Data'}
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('weekly')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'weekly'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Weekly Recommendations
          </button>
          <button
            onClick={() => setActiveTab('monthly')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'monthly'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Monthly Recommendations
          </button>
        </nav>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        {activeTab === 'weekly' ? (
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Past weeks:</label>
            <select
              value={pastWeeks}
              onChange={(e) => setPastWeeks(Number(e.target.value))}
              className="border rounded px-2 py-1"
            >
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Past months:</label>
            <select
              value={pastMonths}
              onChange={(e) => setPastMonths(Number(e.target.value))}
              className="border rounded px-2 py-1"
            >
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>
        )}
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={includeUpcoming}
            onChange={(e) => setIncludeUpcoming(e.target.checked)}
            className="rounded"
          />
          <span className="text-sm text-gray-600">Include upcoming</span>
        </label>
      </div>

      {/* Content */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      ) : activeTab === 'weekly' ? (
        <div className="space-y-8">
          {weeklyData.map((week) => (
            <div key={week.week} className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 bg-gray-50 border-b">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {week.week_display}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {week.start_date} to {week.end_date}
                      {week.is_past && <span className="ml-2 px-2 py-0.5 bg-gray-200 rounded text-xs">Past</span>}
                      {!week.is_past && <span className="ml-2 px-2 py-0.5 bg-blue-100 rounded text-xs">Upcoming</span>}
                    </p>
                  </div>
                  {!week.data_available && (
                    <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded text-sm">
                      Data not available
                    </span>
                  )}
                </div>
              </div>
              {week.data_available && (
                <div className="px-6 py-4">
                  <table className="min-w-full">
                    <thead>
                      <tr className="text-left text-xs font-medium text-gray-500 uppercase">
                        <th className="py-2 w-16">Rank</th>
                        <th className="py-2">Index</th>
                        <th className="py-2">Symbol</th>
                        <th className="py-2">Weekly Change %</th>
                        <th className="py-2">3W Cumulative %</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {week.recommendations.map((rec) => (
                        <tr key={rec.rank}>
                          <td className="py-2 font-semibold text-gray-900">#{rec.rank}</td>
                          <td className="py-2">
                            <Link
                              to={`/comparison?indices=${rec.symbol},NIFTYBEES`}
                              className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
                            >
                              {rec.name}
                            </Link>
                          </td>
                          <td className="py-2 text-gray-600">{rec.symbol}</td>
                          <td className={`py-2 font-medium ${(rec.weekly_change_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatPercent(rec.weekly_change_percent)}
                          </td>
                          <td className={`py-2 font-medium ${(rec.three_week_cumulative_return || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatPercent(rec.three_week_cumulative_return)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {week.niftybees && (
                    <div className="mt-4 pt-4 border-t">
                      <h4 className="text-sm font-medium text-gray-500 mb-2">Niftybees Comparison</h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <span className="text-xs text-gray-500">Weekly Change %</span>
                          <p className={`font-medium ${(week.niftybees.weekly_change_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatPercent(week.niftybees.weekly_change_percent)}
                          </p>
                        </div>
                        <div>
                          <span className="text-xs text-gray-500">3W Cumulative %</span>
                          <p className={`font-medium ${(week.niftybees.three_week_cumulative_return || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatPercent(week.niftybees.three_week_cumulative_return)}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-8">
          {monthlyData.map((month) => (
            <div key={month.month} className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 bg-gray-50 border-b">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {month.month_display}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {month.start_date} to {month.end_date}
                      {month.is_past && <span className="ml-2 px-2 py-0.5 bg-gray-200 rounded text-xs">Past</span>}
                      {!month.is_past && <span className="ml-2 px-2 py-0.5 bg-blue-100 rounded text-xs">Upcoming</span>}
                    </p>
                  </div>
                  {!month.data_available && (
                    <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded text-sm">
                      Data not available
                    </span>
                  )}
                </div>
              </div>
              {month.data_available && (
                <div className="px-6 py-4">
                  <table className="min-w-full">
                    <thead>
                      <tr className="text-left text-xs font-medium text-gray-500 uppercase">
                        <th className="py-2 w-16">Rank</th>
                        <th className="py-2">Index</th>
                        <th className="py-2">Symbol</th>
                        <th className="py-2">Monthly Change %</th>
                        <th className="py-2">3M Cumulative %</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {month.recommendations.map((rec) => (
                        <tr key={rec.rank}>
                          <td className="py-2 font-semibold text-gray-900">#{rec.rank}</td>
                          <td className="py-2">
                            <Link
                              to={`/comparison?indices=${rec.symbol},NIFTYBEES`}
                              className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
                            >
                              {rec.name}
                            </Link>
                          </td>
                          <td className="py-2 text-gray-600">{rec.symbol}</td>
                          <td className={`py-2 font-medium ${(rec.monthly_change_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatPercent(rec.monthly_change_percent)}
                          </td>
                          <td className={`py-2 font-medium ${(rec.three_month_cumulative_return || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatPercent(rec.three_month_cumulative_return)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {month.niftybees && (
                    <div className="mt-4 pt-4 border-t">
                      <h4 className="text-sm font-medium text-gray-500 mb-2">Niftybees Comparison</h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <span className="text-xs text-gray-500">Monthly Change %</span>
                          <p className={`font-medium ${(month.niftybees.monthly_change_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatPercent(month.niftybees.monthly_change_percent)}
                          </p>
                        </div>
                        <div>
                          <span className="text-xs text-gray-500">3M Cumulative %</span>
                          <p className={`font-medium ${(month.niftybees.three_month_cumulative_return || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatPercent(month.niftybees.three_month_cumulative_return)}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dashboard;