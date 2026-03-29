import React, { useState, useEffect, useCallback } from 'react';
import { WeeklyRecommendation, MonthlyRecommendation } from '../types';
import { apiService } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import MomentumIndicator from '../components/MomentumIndicator';

interface Top3WeeklyRecommendation {
  week: string;
  recommendation_date: string | null;
  top1: {
    instrument: string;
    symbol: string;
    weekly_return: number | null;
    three_week_cumulative_return: number | null;
  };
  top2: {
    instrument: string;
    symbol: string;
    weekly_return: number | null;
    three_week_cumulative_return: number | null;
  };
  top3: {
    instrument: string;
    symbol: string;
    weekly_return: number | null;
    three_week_cumulative_return: number | null;
  };
}

interface Top3MonthlyRecommendation {
  month: string;
  recommendation_date: string | null;
  top1: {
    instrument: string;
    symbol: string;
    monthly_return: number | null;
    three_month_cumulative_return: number | null;
  };
  top2: {
    instrument: string;
    symbol: string;
    monthly_return: number | null;
    three_month_cumulative_return: number | null;
  };
  top3: {
    instrument: string;
    symbol: string;
    monthly_return: number | null;
    three_month_cumulative_return: number | null;
  };
}

const Recommendations3: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'weekly' | 'monthly'>('weekly');
  const [weeklyRecommendations, setWeeklyRecommendations] = useState<Top3WeeklyRecommendation[]>([]);
  const [monthlyRecommendations, setMonthlyRecommendations] = useState<Top3MonthlyRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const processWeeklyData = (data: WeeklyRecommendation[]): Top3WeeklyRecommendation[] => {
    // Filter for past 12 months
    const twelveMonthsAgo = new Date();
    twelveMonthsAgo.setMonth(twelveMonthsAgo.getMonth() - 12);
    
    const filteredData = data.filter(rec => {
      if (!rec.recommendation_date) return false;
      return new Date(rec.recommendation_date) >= twelveMonthsAgo;
    });

    const groupedData: { [key: string]: WeeklyRecommendation[] } = {};
    
    // Group by week
    filteredData.forEach(rec => {
      const weekKey = rec.week;
      if (!groupedData[weekKey]) {
        groupedData[weekKey] = [];
      }
      groupedData[weekKey].push(rec);
    });

    // Process each week group
    const result: Top3WeeklyRecommendation[] = [];
    Object.keys(groupedData).forEach(week => {
      const weekData = groupedData[week];
      // Sort by 3W cumulative return (descending)
      const sorted = weekData.sort((a, b) => 
        (b.three_week_cumulative_return || 0) - (a.three_week_cumulative_return || 0)
      );
      
      // Take top 3
      const top3 = sorted.slice(0, 3);
      
      // Create recommendation object
      const rec: Top3WeeklyRecommendation = {
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
      
      result.push(rec);
    });

    return result.sort((a, b) => b.week.localeCompare(a.week));
  };

  const processMonthlyData = (data: MonthlyRecommendation[]): Top3MonthlyRecommendation[] => {
    // Filter for past 12 months
    const twelveMonthsAgo = new Date();
    twelveMonthsAgo.setMonth(twelveMonthsAgo.getMonth() - 12);
    
    const filteredData = data.filter(rec => {
      if (!rec.recommendation_date) return false;
      return new Date(rec.recommendation_date) >= twelveMonthsAgo;
    });

    const groupedData: { [key: string]: MonthlyRecommendation[] } = {};
    
    // Group by month
    filteredData.forEach(rec => {
      const monthKey = rec.month;
      if (!groupedData[monthKey]) {
        groupedData[monthKey] = [];
      }
      groupedData[monthKey].push(rec);
    });

    // Process each month group
    const result: Top3MonthlyRecommendation[] = [];
    Object.keys(groupedData).forEach(month => {
      const monthData = groupedData[month];
      // Sort by 3M cumulative return (descending)
      const sorted = monthData.sort((a, b) => 
        (b.three_month_cumulative_return || 0) - (a.three_month_cumulative_return || 0)
      );
      
      // Take top 3
      const top3 = sorted.slice(0, 3);
      
      // Create recommendation object
      const rec: Top3MonthlyRecommendation = {
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
      
      result.push(rec);
    });

    return result.sort((a, b) => b.month.localeCompare(a.month));
  };

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [weekly, monthly] = await Promise.all([
        apiService.getWeeklyRecommendations(),
        apiService.getMonthlyRecommendations()
      ]);
      
      setWeeklyRecommendations(processWeeklyData(weekly));
      setMonthlyRecommendations(processMonthlyData(monthly));
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
        <LoadingSpinner size="large" message="Loading top 3 recommendations..." />
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
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Top 3 Investment Recommendations</h1>
            <p className="text-gray-600 mt-2">Top 3 performing indices per week/month based on 3W/3M cumulative returns (Past 12 months)</p>
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
            Weekly Top 3
          </button>
          <button
            onClick={() => setActiveTab('monthly')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'monthly'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Monthly Top 3
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'weekly' ? (
        <WeeklyTop3Table recommendations={weeklyRecommendations} />
      ) : (
        <MonthlyTop3Table recommendations={monthlyRecommendations} />
      )}
    </div>
  );
};

// Weekly Top 3 Table Component
const WeeklyTop3Table: React.FC<{ recommendations: Top3WeeklyRecommendation[] }> = ({ recommendations }) => {
  const formatDate = (dateString: string | null): string => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="px-6 py-4 bg-blue-50 border-b">
        <h2 className="text-xl font-semibold text-blue-900">Weekly Top 3 Recommendations</h2>
        <p className="text-sm text-blue-700 mt-1">
          Top 3 instruments per week ranked by 3-Week Cumulative Return
        </p>
      </div>
      
      {recommendations.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Week
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Recommendation Date
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top1 Instrument Name (symbol)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top1 Weekly return(%)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top1 3W cumulative return(%)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top2 Instrument Name (symbol)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top2 Weekly return(%)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top2 3W cumulative return(%)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top3 Instrument Name (symbol)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top3 Weekly return(%)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top3 3W cumulative return(%)
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recommendations.map((rec, index) => (
                <tr key={`${rec.week}-${index}`} className="hover:bg-gray-50">
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                    {rec.week}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(rec.recommendation_date)}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {rec.top1.instrument} ({rec.top1.symbol})
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm">
                    <MomentumIndicator 
                      value={rec.top1.weekly_return} 
                      showArrow={true}
                      size="small"
                    />
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm">
                    <MomentumIndicator 
                      value={rec.top1.three_week_cumulative_return} 
                      showArrow={true}
                      showBackground={true}
                      size="small"
                    />
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {rec.top2.instrument} ({rec.top2.symbol})
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm">
                    <MomentumIndicator 
                      value={rec.top2.weekly_return} 
                      showArrow={true}
                      size="small"
                    />
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm">
                    <MomentumIndicator 
                      value={rec.top2.three_week_cumulative_return} 
                      showArrow={true}
                      showBackground={true}
                      size="small"
                    />
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {rec.top3.instrument} ({rec.top3.symbol})
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm">
                    <MomentumIndicator 
                      value={rec.top3.weekly_return} 
                      showArrow={true}
                      size="small"
                    />
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm">
                    <MomentumIndicator 
                      value={rec.top3.three_week_cumulative_return} 
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

// Monthly Top 3 Table Component
const MonthlyTop3Table: React.FC<{ recommendations: Top3MonthlyRecommendation[] }> = ({ recommendations }) => {
  const formatDate = (dateString: string | null): string => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="px-6 py-4 bg-green-50 border-b">
        <h2 className="text-xl font-semibold text-green-900">Monthly Top 3 Recommendations</h2>
        <p className="text-sm text-green-700 mt-1">
          Top 3 instruments per month ranked by 3-Month Cumulative Return
        </p>
      </div>
      
      {recommendations.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Month
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Recommendation Date
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top1 Instrument Name (symbol)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top1 Monthly return(%)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top1 3M cumulative return(%)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top2 Instrument Name (symbol)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top2 Monthly return(%)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top2 3M cumulative return(%)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top3 Instrument Name (symbol)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top3 Monthly return(%)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Top3 3M cumulative return(%)
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recommendations.map((rec, index) => (
                <tr key={`${rec.month}-${index}`} className="hover:bg-gray-50">
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                    {rec.month}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(rec.recommendation_date)}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {rec.top1.instrument} ({rec.top1.symbol})
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm">
                    <MomentumIndicator 
                      value={rec.top1.monthly_return} 
                      showArrow={true}
                      size="small"
                    />
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm">
                    <MomentumIndicator 
                      value={rec.top1.three_month_cumulative_return} 
                      showArrow={true}
                      showBackground={true}
                      size="small"
                    />
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {rec.top2.instrument} ({rec.top2.symbol})
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm">
                    <MomentumIndicator 
                      value={rec.top2.monthly_return} 
                      showArrow={true}
                      size="small"
                    />
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm">
                    <MomentumIndicator 
                      value={rec.top2.three_month_cumulative_return} 
                      showArrow={true}
                      showBackground={true}
                      size="small"
                    />
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {rec.top3.instrument} ({rec.top3.symbol})
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm">
                    <MomentumIndicator 
                      value={rec.top3.monthly_return} 
                      showArrow={true}
                      size="small"
                    />
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm">
                    <MomentumIndicator 
                      value={rec.top3.three_month_cumulative_return} 
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

export default Recommendations3;
