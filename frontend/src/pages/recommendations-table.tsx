import React, { useState, useEffect, useCallback } from 'react';
import { WeeklyRecommendation, MonthlyRecommendation } from '../types';
import { apiService } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import MomentumIndicator from '../components/MomentumIndicator';

interface RecommendationRow {
  recommendation_id: string;
  recommendation_date: string | null;
  recommendation_month: string;
  recommendation_week: string;
  index_id: number;
  index_name: string;
  index_symbol: string;
  weekly_return_percentage: number | null;
  three_week_cumulative_return_percentage: number | null;
  weekly_recommendation_rank: number | null;
  monthly_return_percentage: number | null;
  three_month_cumulative_return_percentage: number | null;
  monthly_recommendation_rank: number | null;
  last_update_date: string;
}

const RecommendationsTable: React.FC = () => {
  const [recommendations, setRecommendations] = useState<RecommendationRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const generateRecommendationId = (date: string, symbol: string, type: string): string => {
    const dateStr = date ? new Date(date).toISOString().split('T')[0] : 'unknown';
    return `${type}_${dateStr}_${symbol}`;
  };

  const extractMonthFromWeek = (week: string): string => {
    const match = week.match(/(\d{4})-W(\d{2})/);
    if (match) {
      const year = parseInt(match[1]);
      const weekNum = parseInt(match[2]);
      const firstDayOfYear = new Date(year, 0, 1);
      const daysOffset = (weekNum - 1) * 7;
      const weekDate = new Date(firstDayOfYear.getTime() + daysOffset * 24 * 60 * 60 * 1000);
      const month = weekDate.getMonth() + 1;
      return `${year}-${month.toString().padStart(2, '0')}`;
    }
    return week;
  };

  const processRecommendations = (
    weeklyData: WeeklyRecommendation[], 
    monthlyData: MonthlyRecommendation[]
  ): RecommendationRow[] => {
    // Filter for past 12 months
    const twelveMonthsAgo = new Date();
    twelveMonthsAgo.setMonth(twelveMonthsAgo.getMonth() - 12);

    const result: RecommendationRow[] = [];
    const currentDateTime = new Date().toISOString();

    // Process weekly recommendations
    const weeklyGrouped: { [key: string]: WeeklyRecommendation[] } = {};
    weeklyData.filter(rec => {
      if (!rec.recommendation_date) return false;
      return new Date(rec.recommendation_date) >= twelveMonthsAgo;
    }).forEach(rec => {
      const weekKey = rec.week;
      if (!weeklyGrouped[weekKey]) {
        weeklyGrouped[weekKey] = [];
      }
      weeklyGrouped[weekKey].push(rec);
    });

    Object.keys(weeklyGrouped).forEach(week => {
      const weekData = weeklyGrouped[week];
      const sorted = weekData.sort((a, b) => 
        (b.three_week_cumulative_return || 0) - (a.three_week_cumulative_return || 0)
      );

      sorted.forEach((rec, index) => {
        const row: RecommendationRow = {
          recommendation_id: generateRecommendationId(rec.recommendation_date || '', rec.symbol, 'weekly'),
          recommendation_date: rec.recommendation_date,
          recommendation_month: extractMonthFromWeek(rec.week),
          recommendation_week: rec.week,
          index_id: 0, // Will need to be populated from actual data if available
          index_name: rec.instrument,
          index_symbol: rec.symbol,
          weekly_return_percentage: rec.one_week_return,
          three_week_cumulative_return_percentage: rec.three_week_cumulative_return,
          weekly_recommendation_rank: index + 1,
          monthly_return_percentage: null,
          three_month_cumulative_return_percentage: null,
          monthly_recommendation_rank: null,
          last_update_date: currentDateTime
        };
        result.push(row);
      });
    });

    // Process monthly recommendations
    const monthlyGrouped: { [key: string]: MonthlyRecommendation[] } = {};
    monthlyData.filter(rec => {
      if (!rec.recommendation_date) return false;
      return new Date(rec.recommendation_date) >= twelveMonthsAgo;
    }).forEach(rec => {
      const monthKey = rec.month;
      if (!monthlyGrouped[monthKey]) {
        monthlyGrouped[monthKey] = [];
      }
      monthlyGrouped[monthKey].push(rec);
    });

    Object.keys(monthlyGrouped).forEach(month => {
      const monthData = monthlyGrouped[month];
      const sorted = monthData.sort((a, b) => 
        (b.three_month_cumulative_return || 0) - (a.three_month_cumulative_return || 0)
      );

      sorted.forEach((rec, index) => {
        // Check if this row already exists from weekly data
        const existingRow = result.find(r => 
          r.index_symbol === rec.symbol && 
          r.recommendation_month === rec.month
        );

        if (existingRow) {
          // Update existing row with monthly data
          existingRow.monthly_return_percentage = rec.one_month_return;
          existingRow.three_month_cumulative_return_percentage = rec.three_month_cumulative_return;
          existingRow.monthly_recommendation_rank = index + 1;
        } else {
          // Create new row for monthly-only recommendation
          const row: RecommendationRow = {
            recommendation_id: generateRecommendationId(rec.recommendation_date || '', rec.symbol, 'monthly'),
            recommendation_date: rec.recommendation_date,
            recommendation_month: rec.month,
            recommendation_week: '',
            index_id: 0, // Will need to be populated from actual data if available
            index_name: rec.instrument,
            index_symbol: rec.symbol,
            weekly_return_percentage: null,
            three_week_cumulative_return_percentage: null,
            weekly_recommendation_rank: null,
            monthly_return_percentage: rec.one_month_return,
            three_month_cumulative_return_percentage: rec.three_month_cumulative_return,
            monthly_recommendation_rank: index + 1,
            last_update_date: currentDateTime
          };
          result.push(row);
        }
      });
    });

    return result.sort((a, b) => {
      const dateA = a.recommendation_date ? new Date(a.recommendation_date) : new Date(0);
      const dateB = b.recommendation_date ? new Date(b.recommendation_date) : new Date(0);
      return dateB.getTime() - dateA.getTime();
    });
  };

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [weekly, monthly] = await Promise.all([
        apiService.getWeeklyRecommendations(),
        apiService.getMonthlyRecommendations()
      ]);
      
      const processed = processRecommendations(weekly, monthly);
      setRecommendations(processed);
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

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const formatDateTime = (dateString: string): string => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="large" message="Loading recommendations table..." />
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
    <div className="max-w-full mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Comprehensive Recommendations Table</h1>
            <p className="text-gray-600 mt-2">Complete view of all weekly and monthly recommendations with rankings (Past 12 months)</p>
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

      {/* Table */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="px-6 py-4 bg-indigo-50 border-b">
          <h2 className="text-xl font-semibold text-indigo-900">All Recommendations</h2>
          <p className="text-sm text-indigo-700 mt-1">
            Complete dataset with weekly and monthly recommendations combined
          </p>
        </div>
        
        {recommendations.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Recommendation ID
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Recommendation Date
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Month
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Week
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Index Name
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Symbol
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Weekly Return %
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    3W Cumulative %
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Weekly Rank
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Monthly Return %
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    3M Cumulative %
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Monthly Rank
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Update
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recommendations.map((rec, index) => (
                  <tr key={`${rec.recommendation_id}-${index}`} className="hover:bg-gray-50">
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">
                      {rec.recommendation_id}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(rec.recommendation_date)}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">
                      {rec.recommendation_month}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">
                      {rec.recommendation_week || '-'}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {rec.index_name}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">
                      {rec.index_symbol}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm">
                      {rec.weekly_return_percentage !== null ? (
                        <MomentumIndicator 
                          value={rec.weekly_return_percentage} 
                          showArrow={true}
                          size="small"
                        />
                      ) : (
                        '-'
                      )}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm">
                      {rec.three_week_cumulative_return_percentage !== null ? (
                        <MomentumIndicator 
                          value={rec.three_week_cumulative_return_percentage} 
                          showArrow={true}
                          showBackground={true}
                          size="small"
                        />
                      ) : (
                        '-'
                      )}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">
                      {rec.weekly_recommendation_rank !== null ? `#${rec.weekly_recommendation_rank}` : '-'}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm">
                      {rec.monthly_return_percentage !== null ? (
                        <MomentumIndicator 
                          value={rec.monthly_return_percentage} 
                          showArrow={true}
                          size="small"
                        />
                      ) : (
                        '-'
                      )}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm">
                      {rec.three_month_cumulative_return_percentage !== null ? (
                        <MomentumIndicator 
                          value={rec.three_month_cumulative_return_percentage} 
                          showArrow={true}
                          showBackground={true}
                          size="small"
                        />
                      ) : (
                        '-'
                      )}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">
                      {rec.monthly_recommendation_rank !== null ? `#${rec.monthly_recommendation_rank}` : '-'}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDateTime(rec.last_update_date)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center text-gray-500">
            No recommendations available
          </div>
        )}
      </div>
    </div>
  );
};

export default RecommendationsTable;
