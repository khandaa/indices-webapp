import React, { useState, useEffect, useCallback } from 'react';
import { TopPerformer } from '../types';
import { apiService } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import MomentumIndicator from '../components/MomentumIndicator';

const MonthlyDashboard: React.FC = () => {
  const [topPerformers, setTopPerformers] = useState<TopPerformer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const performers = await apiService.getMonthlyTopPerformers();
      setTopPerformers(performers);
      setLastUpdated(new Date());
    } catch (err) {
      setError('Failed to fetch monthly performance data');
      console.error('Error fetching monthly performers:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

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
        <LoadingSpinner size="large" message="Loading monthly performance data..." />
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
            <h1 className="text-3xl font-bold text-gray-900">Monthly Performance Dashboard</h1>
            <p className="text-gray-600 mt-2">Top performing indices this month</p>
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
            <div className="absolute top-2 left-2 w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
              {index + 1}
            </div>
            <div className="pt-8 p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
              <div className="mb-3">
                <h3 className="font-semibold text-gray-900">{performer.name}</h3>
                <p className="text-sm text-gray-600">{performer.symbol}</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900">
                  {formatNumber(performer.current_price)}
                </p>
                <MomentumIndicator
                  value={performer.monthly_change_percent ?? null}
                  showArrow={true}
                  showBackground={true}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Detailed Performance Table */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Monthly Performance Details</h2>
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
                    Monthly Change
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Monthly %
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {topPerformers.map((performer, index) => (
                  <tr key={performer.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center justify-center w-8 h-8 bg-green-100 text-green-800 rounded-full font-semibold text-sm">
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
                      {formatNumber(performer.monthly_change ?? null)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <MomentumIndicator 
                        value={performer.monthly_change_percent ?? null}
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
            No monthly performance data available
          </div>
        )}
      </div>

      {/* Performance Summary */}
      <div className="mt-8 bg-green-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-green-900 mb-3">Monthly Performance Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-sm text-green-700 mb-1">Top Performer</p>
            <p className="text-xl font-bold text-green-900">
              {topPerformers[0]?.name || 'N/A'}
            </p>
            <p className="text-sm text-green-600">
              {topPerformers[0] ? formatPercent(topPerformers[0].monthly_change_percent ?? null) : 'N/A'}
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-green-700 mb-1">Average Monthly Return</p>
            <p className="text-xl font-bold text-green-900">
              {topPerformers.length > 0 
                ? formatPercent(topPerformers.reduce((sum, p) => sum + (p.monthly_change_percent || 0), 0) / topPerformers.length)
                : 'N/A'
              }
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-green-700 mb-1">Total Indices Tracked</p>
            <p className="text-xl font-bold text-green-900">
              {topPerformers.length}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MonthlyDashboard;
