import React, { useState, useEffect, useCallback } from 'react';
import { WeeklyRecommendation, MonthlyRecommendation } from '../types';
import { apiService } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import MomentumIndicator from '../components/MomentumIndicator';

const Recommendations: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'weekly' | 'monthly'>('weekly');
  const [weeklyRecommendations, setWeeklyRecommendations] = useState<WeeklyRecommendation[]>([]);
  const [monthlyRecommendations, setMonthlyRecommendations] = useState<MonthlyRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [weekly, monthly] = await Promise.all([
        apiService.getWeeklyRecommendations(),
        apiService.getMonthlyRecommendations()
      ]);
      
      setWeeklyRecommendations(weekly);
      setMonthlyRecommendations(monthly);
      setLastUpdated(new Date());
    } catch (err) {
      setError('Failed to fetch recommendations data');
      console.error('Error fetching recommendations:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="large" message="Loading recommendations..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <ErrorMessage 
          message={error} 
          onRetry={fetchData}
        />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Investment Recommendations</h1>
            <p className="text-gray-600 mt-2">Top performing indices based on momentum analysis</p>
          </div>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh
          </button>
        </div>
        
        {lastUpdated && (
          <p className="text-sm text-gray-500">
            Last updated: {lastUpdated.toLocaleString()}
          </p>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('weekly')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'weekly'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Weekly Recommendations
          </button>
          <button
            onClick={() => setActiveTab('monthly')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'monthly'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Monthly Recommendations
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'weekly' ? (
        <WeeklyRecommendationsTable recommendations={weeklyRecommendations} />
      ) : (
        <MonthlyRecommendationsTable recommendations={monthlyRecommendations} />
      )}
    </div>
  );
};

// Weekly Recommendations Table Component
const WeeklyRecommendationsTable: React.FC<{ recommendations: WeeklyRecommendation[] }> = ({ recommendations }) => {
  const formatNumber = (value: number | null): string => {
    if (value === null || value === undefined) return 'N/A';
    return value.toFixed(2);
  };

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="px-6 py-4 bg-blue-50 border-b">
        <h2 className="text-xl font-semibold text-blue-900">Weekly Recommendations</h2>
        <p className="text-sm text-blue-700 mt-1">
          Sorted by 3-Week Cumulative Return (descending)
        </p>
      </div>
      
      {recommendations.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Week
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Recommendation Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Instrument
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Symbol
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  1W Return
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  3W Cumulative Return
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recommendations.map((rec, index) => (
                <tr key={`${rec.instrument}-${index}`} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {rec.week}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(rec.recommendation_date)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {rec.instrument}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {rec.symbol}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <MomentumIndicator 
                      value={rec.one_week_return} 
                      showArrow={true}
                      size="small"
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <MomentumIndicator 
                      value={rec.three_week_cumulative_return} 
                      showArrow={true}
                      showBackground={true}
                      size="small"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="p-8 text-center text-gray-500">
          No weekly recommendations available
        </div>
      )}
    </div>
  );
};

// Monthly Recommendations Table Component
const MonthlyRecommendationsTable: React.FC<{ recommendations: MonthlyRecommendation[] }> = ({ recommendations }) => {
  const formatNumber = (value: number | null): string => {
    if (value === null || value === undefined) return 'N/A';
    return value.toFixed(2);
  };

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="px-6 py-4 bg-green-50 border-b">
        <h2 className="text-xl font-semibold text-green-900">Monthly Recommendations</h2>
        <p className="text-sm text-green-700 mt-1">
          Sorted by 3-Month Cumulative Return (descending)
        </p>
      </div>
      
      {recommendations.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Month
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Recommendation Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Instrument
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Symbol
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  1M Return
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  3M Cumulative Return
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recommendations.map((rec, index) => (
                <tr key={`${rec.instrument}-${index}`} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {rec.month}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(rec.recommendation_date)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {rec.instrument}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {rec.symbol}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <MomentumIndicator 
                      value={rec.one_month_return} 
                      showArrow={true}
                      size="small"
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <MomentumIndicator 
                      value={rec.three_month_cumulative_return} 
                      showArrow={true}
                      showBackground={true}
                      size="small"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="p-8 text-center text-gray-500">
          No monthly recommendations available
        </div>
      )}
    </div>
  );
};

export default Recommendations;
