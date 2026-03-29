import React, { useState, useEffect } from 'react';
import { TopPerformer } from '../types';
import { apiService } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import IndexCard from '../components/IndexCard';
import MomentumIndicator from '../components/MomentumIndicator';

const WeeklyDashboard: React.FC = () => {
  const [topPerformers, setTopPerformers] = useState<TopPerformer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const performers = await apiService.getWeeklyTopPerformers();
      setTopPerformers(performers);
      setLastUpdated(new Date());
    } catch (err) {
      setError('Failed to fetch weekly performance data');
      console.error('Error fetching weekly performers:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const formatNumber = (value: number | null): string => {
    if (value === null || value === undefined) return 'N/A';
    return value.toFixed(2);
  };

  const formatPercent = (value: number | null): string => {
    if (value === null || value === undefined) return 'N/A';
    const formatted = formatNumber(value);
    return `${formatted}%`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="large" message="Loading weekly performance data..." />
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
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Weekly Performance Dashboard</h1>
            <p className="text-gray-600 mt-2">Top performing indices this week</p>
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

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {topPerformers.map((performer, index) => (
          <div key={performer.id} className="relative">
            <div className="absolute top-2 left-2 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
              {index + 1}
            </div>
            <IndexCard
              index={performer}
              variant="detailed"
              className="pt-8"
            />
          </div>
        ))}
      </div>

      {/* Detailed Performance Table */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Weekly Performance Details</h2>
        </div>
        
        {topPerformers.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rank
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Symbol
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Current Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Weekly Change
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Weekly %
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {topPerformers.map((performer, index) => (
                  <tr key={performer.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-800 rounded-full font-semibold text-sm">
                        {index + 1}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {performer.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {performer.symbol}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatNumber(performer.current_price)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {formatNumber(performer.weekly_change)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <MomentumIndicator 
                        value={performer.weekly_change_percent} 
                        showArrow={true}
                        showBackground={true}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center text-gray-500">
            No weekly performance data available
          </div>
        )}
      </div>

      {/* Performance Summary */}
      <div className="mt-8 bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">Weekly Performance Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-sm text-blue-700 mb-1">Top Performer</p>
            <p className="text-xl font-bold text-blue-900">
              {topPerformers[0]?.name || 'N/A'}
            </p>
            <p className="text-sm text-blue-600">
              {topPerformers[0] ? formatPercent(topPerformers[0].weekly_change_percent) : 'N/A'}
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-blue-700 mb-1">Average Weekly Return</p>
            <p className="text-xl font-bold text-blue-900">
              {topPerformers.length > 0 
                ? formatPercent(topPerformers.reduce((sum, p) => sum + (p.weekly_change_percent || 0), 0) / topPerformers.length)
                : 'N/A'
              }
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-blue-700 mb-1">Total Indices Tracked</p>
            <p className="text-xl font-bold text-blue-900">
              {topPerformers.length}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WeeklyDashboard;
