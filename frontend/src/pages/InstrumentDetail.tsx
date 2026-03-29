import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Index, DailyPrice } from '../types';
import { apiService } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import MomentumIndicator from '../components/MomentumIndicator';

const InstrumentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [index, setIndex] = useState<Index | null>(null);
  const [dailyPrices, setDailyPrices] = useState<DailyPrice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchData = useCallback(async () => {
    if (!id) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const [indexData, pricesData] = await Promise.all([
        apiService.getIndexDetails(parseInt(id)),
        apiService.getDailyPrices(parseInt(id), 200) // Get last 200 days
      ]);
      
      setIndex(indexData);
      setDailyPrices(pricesData);
      setLastUpdated(new Date());
    } catch (err) {
      setError('Failed to fetch instrument data');
      console.error('Error fetching instrument details:', err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const formatNumber = (value: number | null): string => {
    if (value === null || value === undefined) return 'N/A';
    return value.toFixed(2);
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatVolume = (value: number | null): string => {
    if (value === null || value === undefined) return 'N/A';
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K`;
    }
    return value.toString();
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="large" message="Loading instrument details..." />
      </div>
    );
  }

  if (error || !index) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <ErrorMessage 
          message={error || 'Instrument not found'} 
          onRetry={fetchData}
        />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate(-1)}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              ← Back
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{index.name}</h1>
              <p className="text-gray-600">{index.symbol}</p>
            </div>
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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Current Price</h3>
          <p className="text-2xl font-bold text-gray-900">
            {formatNumber(index.current_price)}
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Daily Change</h3>
          <MomentumIndicator 
            value={index.daily_change_percent} 
            showArrow={true}
            showBackground={true}
            size="large"
          />
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Weekly Change</h3>
          <MomentumIndicator 
            value={index.weekly_change_percent} 
            showArrow={true}
            showBackground={true}
            size="large"
          />
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Monthly Change</h3>
          <MomentumIndicator 
            value={index.monthly_change_percent} 
            showArrow={true}
            showBackground={true}
            size="large"
          />
        </div>
      </div>

      {/* Daily Prices Table */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Daily Price History</h2>
          <p className="text-sm text-gray-600 mt-1">Last {dailyPrices.length} trading days</p>
        </div>
        
        {dailyPrices.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Open
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Close
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    High
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Low
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Volume
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Daily % Change
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    % Change from Previous
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {dailyPrices.map((price, index) => (
                  <tr key={`${price.date}-${index}`} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(price.date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatNumber(price.open_price)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatNumber(price.close_price)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatNumber(price.high_price)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatNumber(price.low_price)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatVolume(price.volume)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <MomentumIndicator 
                        value={price.daily_change_percent} 
                        showArrow={true}
                        size="small"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <MomentumIndicator 
                        value={price.change_from_previous} 
                        showArrow={true}
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
            No daily price data available
          </div>
        )}
      </div>

      {/* Momentum Metrics */}
      {(index.three_week_cumulative_return || index.three_month_cumulative_return) && (
        <div className="mt-8 bg-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">Momentum Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {index.three_week_cumulative_return && (
              <div className="text-center">
                <p className="text-sm text-blue-700 mb-1">3-Week Cumulative Return</p>
                <MomentumIndicator 
                  value={index.three_week_cumulative_return} 
                  showArrow={true}
                  showBackground={true}
                  size="large"
                />
              </div>
            )}
            {index.three_month_cumulative_return && (
              <div className="text-center">
                <p className="text-sm text-blue-700 mb-1">3-Month Cumulative Return</p>
                <MomentumIndicator 
                  value={index.three_month_cumulative_return} 
                  showArrow={true}
                  showBackground={true}
                  size="large"
                />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default InstrumentDetail;
