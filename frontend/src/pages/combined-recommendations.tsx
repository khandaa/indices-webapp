import React, { useState, useEffect, useCallback } from 'react';
import { WeeklyRecommendation, MonthlyRecommendation } from '../types';
import { apiService } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import MomentumIndicator from '../components/MomentumIndicator';

interface CombinedRecommendation {
  week: string;
  month: string;
  recommendation_date: string | null;
  weekly_top1: {
    instrument: string;
    symbol: string;
    weekly_return: number | null;
    three_week_cumulative_return: number | null;
  };
  weekly_top2: {
    instrument: string;
    symbol: string;
    weekly_return: number | null;
    three_week_cumulative_return: number | null;
  };
  weekly_top3: {
    instrument: string;
    symbol: string;
    weekly_return: number | null;
    three_week_cumulative_return: number | null;
  };
  monthly_top1: {
    instrument: string;
    symbol: string;
    monthly_return: number | null;
    three_month_cumulative_return: number | null;
  };
  monthly_top2: {
    instrument: string;
    symbol: string;
    monthly_return: number | null;
    three_month_cumulative_return: number | null;
  };
  monthly_top3: {
    instrument: string;
    symbol: string;
    monthly_return: number | null;
    three_month_cumulative_return: number | null;
  };
}

const CombinedRecommendations: React.FC = () => {
  const [recommendations, setRecommendations] = useState<CombinedRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const processWeeklyData = (data: WeeklyRecommendation[]): { [key: string]: any } => {
    // Filter for past 12 months
    const twelveMonthsAgo = new Date();
    twelveMonthsAgo.setMonth(twelveMonthsAgo.getMonth() - 12);
    
    const filteredData = data.filter(rec => {
      if (!rec.recommendation_date) return false;
      return new Date(rec.recommendation_date) >= twelveMonthsAgo;
    });

    const groupedData: { [key: string]: WeeklyRecommendation[] } = {};
    
    filteredData.forEach(rec => {
      const weekKey = rec.week;
      if (!groupedData[weekKey]) {
        groupedData[weekKey] = [];
      }
      groupedData[weekKey].push(rec);
    });

    const result: { [key: string]: any } = {};
    Object.keys(groupedData).forEach(week => {
      const weekData = groupedData[week];
      const sorted = weekData.sort((a, b) => 
        (b.three_week_cumulative_return || 0) - (a.three_week_cumulative_return || 0)
      );
      
      const top3 = sorted.slice(0, 3);
      
      result[week] = {
        week: week,
        recommendation_date: top3[0]?.recommendation_date || null,
        top1: {
          instrument: top3[0]?.instrument || '',
          symbol: top3[0]?.symbol || '',
          weekly_return: top3[0]?.one_week_return || null,
          three_week_cumulative_return: top3[0]?.three_week_cumulative_return || null
        },
        top2: {
          instrument: top3[1]?.instrument || '',
          symbol: top3[1]?.symbol || '',
          weekly_return: top3[1]?.one_week_return || null,
          three_week_cumulative_return: top3[1]?.three_week_cumulative_return || null
        },
        top3: {
          instrument: top3[2]?.instrument || '',
          symbol: top3[2]?.symbol || '',
          weekly_return: top3[2]?.one_week_return || null,
          three_week_cumulative_return: top3[2]?.three_week_cumulative_return || null
        }
      };
    });

    return result;
  };

  const processMonthlyData = (data: MonthlyRecommendation[]): { [key: string]: any } => {
    // Filter for past 12 months
    const twelveMonthsAgo = new Date();
    twelveMonthsAgo.setMonth(twelveMonthsAgo.getMonth() - 12);
    
    const filteredData = data.filter(rec => {
      if (!rec.recommendation_date) return false;
      return new Date(rec.recommendation_date) >= twelveMonthsAgo;
    });

    const groupedData: { [key: string]: MonthlyRecommendation[] } = {};
    
    filteredData.forEach(rec => {
      const monthKey = rec.month;
      if (!groupedData[monthKey]) {
        groupedData[monthKey] = [];
      }
      groupedData[monthKey].push(rec);
    });

    const result: { [key: string]: any } = {};
    Object.keys(groupedData).forEach(month => {
      const monthData = groupedData[month];
      const sorted = monthData.sort((a, b) => 
        (b.three_month_cumulative_return || 0) - (a.three_month_cumulative_return || 0)
      );
      
      const top3 = sorted.slice(0, 3);
      
      result[month] = {
        month: month,
        recommendation_date: top3[0]?.recommendation_date || null,
        top1: {
          instrument: top3[0]?.instrument || '',
          symbol: top3[0]?.symbol || '',
          monthly_return: top3[0]?.one_month_return || null,
          three_month_cumulative_return: top3[0]?.three_month_cumulative_return || null
        },
        top2: {
          instrument: top3[1]?.instrument || '',
          symbol: top3[1]?.symbol || '',
          monthly_return: top3[1]?.one_month_return || null,
          three_month_cumulative_return: top3[1]?.three_month_cumulative_return || null
        },
        top3: {
          instrument: top3[2]?.instrument || '',
          symbol: top3[2]?.symbol || '',
          monthly_return: top3[2]?.one_month_return || null,
          three_month_cumulative_return: top3[2]?.three_month_cumulative_return || null
        }
      };
    });

    return result;
  };

  const extractMonthFromWeek = (week: string): string => {
    // Assuming week format is like "2024-W01" or similar
    // Extract year and week number to determine month
    const match = week.match(/(\d{4})-W(\d{2})/);
    if (match) {
      const year = parseInt(match[1]);
      const weekNum = parseInt(match[2]);
      
      // Calculate month from week number
      const firstDayOfYear = new Date(year, 0, 1);
      const daysOffset = (weekNum - 1) * 7;
      const weekDate = new Date(firstDayOfYear.getTime() + daysOffset * 24 * 60 * 60 * 1000);
      const month = weekDate.getMonth() + 1;
      return `${year}-${month.toString().padStart(2, '0')}`;
    }
    return week; // fallback
  };

  const combineData = (weeklyData: { [key: string]: any }, monthlyData: { [key: string]: any }): CombinedRecommendation[] => {
    const combined: CombinedRecommendation[] = [];
    
    Object.keys(weeklyData).forEach(week => {
      const month = extractMonthFromWeek(week);
      const monthlyRec = monthlyData[month];
      
      combined.push({
        week: week,
        month: month,
        recommendation_date: weeklyData[week].recommendation_date,
        weekly_top1: weeklyData[week].top1,
        weekly_top2: weeklyData[week].top2,
        weekly_top3: weeklyData[week].top3,
        monthly_top1: monthlyRec?.top1 || { instrument: '', symbol: '', monthly_return: null, three_month_cumulative_return: null },
        monthly_top2: monthlyRec?.top2 || { instrument: '', symbol: '', monthly_return: null, three_month_cumulative_return: null },
        monthly_top3: monthlyRec?.top3 || { instrument: '', symbol: '', monthly_return: null, three_month_cumulative_return: null }
      });
    });

    return combined.sort((a, b) => b.week.localeCompare(a.week));
  };

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [weekly, monthly] = await Promise.all([
        apiService.getWeeklyRecommendations(),
        apiService.getMonthlyRecommendations()
      ]);
      
      const processedWeekly = processWeeklyData(weekly);
      const processedMonthly = processMonthlyData(monthly);
      const combined = combineData(processedWeekly, processedMonthly);
      
      setRecommendations(combined);
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
        <LoadingSpinner size="large" message="Loading combined recommendations..." />
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
            <h1 className="text-3xl font-bold text-gray-900">Combined Weekly & Monthly Recommendations</h1>
            <p className="text-gray-600 mt-2">Top 3 weekly and monthly recommendations with monthly data repeated for each week (Past 12 months)</p>
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

      {/* Combined Table */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="px-6 py-4 bg-purple-50 border-b">
          <h2 className="text-xl font-semibold text-purple-900">Combined Recommendations View</h2>
          <p className="text-sm text-purple-700 mt-1">
            Weekly recommendations with corresponding monthly top 3 performers
          </p>
        </div>
        
        {recommendations.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Week
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Month
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Recommendation Date
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-l-2 border-blue-200">
                    Weekly Top1 (symbol)
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Weekly Top1 Return(%)
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Weekly Top1 3W Cum(%)
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Weekly Top2 (symbol)
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Weekly Top2 Return(%)
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Weekly Top2 3W Cum(%)
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Weekly Top3 (symbol)
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Weekly Top3 Return(%)
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Weekly Top3 3W Cum(%)
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-l-2 border-green-200">
                    Monthly Top1 (symbol)
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Monthly Top1 Return(%)
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Monthly Top1 3M Cum(%)
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Monthly Top2 (symbol)
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Monthly Top2 Return(%)
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Monthly Top2 3M Cum(%)
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Monthly Top3 (symbol)
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Monthly Top3 Return(%)
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Monthly Top3 3M Cum(%)
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recommendations.map((rec, index) => (
                  <tr key={`${rec.week}-${index}`} className="hover:bg-gray-50">
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">
                      {rec.week}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">
                      {rec.month}
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900">
                      {rec.recommendation_date ? new Date(rec.recommendation_date).toLocaleDateString() : 'N/A'}
                    </td>
                    {/* Weekly Recommendations */}
                    <td className="px-3 py-4 whitespace-nowrap text-sm font-medium text-gray-900 border-l-2 border-blue-100">
                      {rec.weekly_top1.instrument} ({rec.weekly_top1.symbol})
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm">
                      <MomentumIndicator 
                        value={rec.weekly_top1.weekly_return} 
                        showArrow={true}
                        size="small"
                      />
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm">
                      <MomentumIndicator 
                        value={rec.weekly_top1.three_week_cumulative_return} 
                        showArrow={true}
                        showBackground={true}
                        size="small"
                      />
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {rec.weekly_top2.instrument} ({rec.weekly_top2.symbol})
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm">
                      <MomentumIndicator 
                        value={rec.weekly_top2.weekly_return} 
                        showArrow={true}
                        size="small"
                      />
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm">
                      <MomentumIndicator 
                        value={rec.weekly_top2.three_week_cumulative_return} 
                        showArrow={true}
                        showBackground={true}
                        size="small"
                      />
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {rec.weekly_top3.instrument} ({rec.weekly_top3.symbol})
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm">
                      <MomentumIndicator 
                        value={rec.weekly_top3.weekly_return} 
                        showArrow={true}
                        size="small"
                      />
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm">
                      <MomentumIndicator 
                        value={rec.weekly_top3.three_week_cumulative_return} 
                        showArrow={true}
                        showBackground={true}
                        size="small"
                      />
                    </td>
                    {/* Monthly Recommendations */}
                    <td className="px-3 py-4 whitespace-nowrap text-sm font-medium text-gray-900 border-l-2 border-green-100">
                      {rec.monthly_top1.instrument} ({rec.monthly_top1.symbol})
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm">
                      <MomentumIndicator 
                        value={rec.monthly_top1.monthly_return} 
                        showArrow={true}
                        size="small"
                      />
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm">
                      <MomentumIndicator 
                        value={rec.monthly_top1.three_month_cumulative_return} 
                        showArrow={true}
                        showBackground={true}
                        size="small"
                      />
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {rec.monthly_top2.instrument} ({rec.monthly_top2.symbol})
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm">
                      <MomentumIndicator 
                        value={rec.monthly_top2.monthly_return} 
                        showArrow={true}
                        size="small"
                      />
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm">
                      <MomentumIndicator 
                        value={rec.monthly_top2.three_month_cumulative_return} 
                        showArrow={true}
                        showBackground={true}
                        size="small"
                      />
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {rec.monthly_top3.instrument} ({rec.monthly_top3.symbol})
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm">
                      <MomentumIndicator 
                        value={rec.monthly_top3.monthly_return} 
                        showArrow={true}
                        size="small"
                      />
                    </td>
                    <td className="px-3 py-4 whitespace-nowrap text-sm">
                      <MomentumIndicator 
                        value={rec.monthly_top3.three_month_cumulative_return} 
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
            No recommendations available
          </div>
        )}
      </div>
    </div>
  );
};

export default CombinedRecommendations;
