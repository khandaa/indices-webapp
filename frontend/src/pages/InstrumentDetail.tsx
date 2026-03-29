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
  
  // New states for return calculations
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [weeklyReturn, setWeeklyReturn] = useState<number | null>(null);
  const [monthlyReturn, setMonthlyReturn] = useState<number | null>(null);
  const [cumulativeReturn, setCumulativeReturn] = useState<number | null>(null);
  const [niftyReturn, setNiftyReturn] = useState<number | null>(null);

  // Calculate returns since selected date
  const calculateReturnsSinceDate = useCallback(async (date: string) => {
    if (!id) return;

    try {
      // Get daily prices and filter from selected date onwards
      const allPricesData = await apiService.getDailyPrices(parseInt(id), 500);
      const selectedDateTime = new Date(date).getTime();
      const pricesData = allPricesData.filter(price => new Date(price.date).getTime() >= selectedDateTime);

      if (pricesData.length < 2) {
        setWeeklyReturn(null);
        setMonthlyReturn(null);
        setCumulativeReturn(null);
        setNiftyReturn(null);
        return;
      }

      const firstPrice = pricesData[0]?.close_price;
      const lastPrice = pricesData[pricesData.length - 1]?.close_price;

      if (!firstPrice || !lastPrice) {
        setWeeklyReturn(null);
        setMonthlyReturn(null);
        setCumulativeReturn(null);
        setNiftyReturn(null);
        return;
      }

      // Calculate total return
      const totalReturn = ((lastPrice - firstPrice) / firstPrice) * 100;
      setCumulativeReturn(totalReturn);

      // Calculate weekly return (assuming 5 trading days per week)
      const weeksPassed = (pricesData.length / 5);
      const weeklyReturnRate = Math.pow(1 + totalReturn / 100, 1 / weeksPassed) - 1;
      setWeeklyReturn(weeklyReturnRate * 100);

      // Calculate monthly return (assuming 21 trading days per month)
      const monthsPassed = (pricesData.length / 21);
      const monthlyReturnRate = Math.pow(1 + totalReturn / 100, 1 / monthsPassed) - 1;
      setMonthlyReturn(monthlyReturnRate * 100);

      // Get NIFTY data for comparison (assuming NIFTY has id=1)
      try {
        const allNiftyData = await apiService.getDailyPrices(1, 500);
        const niftyData = allNiftyData.filter(price => new Date(price.date).getTime() >= selectedDateTime);
        if (niftyData.length >= 2) {
          const niftyFirstPrice = niftyData[0]?.close_price;
          const niftyLastPrice = niftyData[niftyData.length - 1]?.close_price;
          if (niftyFirstPrice && niftyLastPrice) {
            const niftyReturn = ((niftyLastPrice - niftyFirstPrice) / niftyFirstPrice) * 100;
            setNiftyReturn(niftyReturn);
          }
        }
      } catch (err) {
        console.error('Error fetching NIFTY data:', err);
      }

    } catch (err) {
      console.error('Error calculating returns:', err);
    }
  }, [id]);

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
  }, [id]);

  useEffect(() => {
    if (index && id) {
      // Calculate returns for default date (365 days ago) only once when index loads
      const defaultDate = new Date();
      defaultDate.setDate(defaultDate.getDate() - 365);
      calculateReturnsSinceDate(defaultDate.toISOString().split('T')[0]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [index]);

  const formatNumber = (value: number | null): string => {
    if (value === null || value === undefined) return 'N/A';
    return value.toFixed(2);
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString();
  };

  // Calendar component
  const Calendar: React.FC<{ selectedDate: string; onDateChange: (date: string) => void }> = ({ selectedDate, onDateChange }) => {
    const [currentMonth, setCurrentMonth] = useState(new Date());
    const [showCalendar, setShowCalendar] = useState(false);

    const getDaysInMonth = (date: Date) => {
      const year = date.getFullYear();
      const month = date.getMonth();
      const firstDay = new Date(year, month, 1).getDay();
      const daysInMonth = new Date(year, month + 1, 0).getDate();

      const days = [];
      let day = 1;

      // Add empty cells for days before month starts
      for (let i = 0; i < firstDay; i++) {
        days.push(null);
      }

      // Add days of the month
      while (day <= daysInMonth) {
        days.push(day);
        day++;
      }

      return days;
    };

    const handleDateClick = (day: number | null) => {
      if (day) {
        const newDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
        onDateChange(newDate.toISOString().split('T')[0]);
        setShowCalendar(false);
      }
    };

    const goToPreviousMonth = () => {
      setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
    };

    const goToNextMonth = () => {
      setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
    };

    const goToPreviousYear = () => {
      setCurrentMonth(new Date(currentMonth.getFullYear() - 1, currentMonth.getMonth(), 1));
    };

    const goToNextYear = () => {
      setCurrentMonth(new Date(currentMonth.getFullYear() + 1, currentMonth.getMonth(), 1));
    };

    return (
      <div className="relative">
        <button
          onClick={() => setShowCalendar(!showCalendar)}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors mb-4"
        >
          Select Date: {new Date(selectedDate).toLocaleDateString()}
        </button>

        {showCalendar && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl p-6 m-4 max-w-md">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-2">
                  <button
                    onClick={goToPreviousYear}
                    className="px-2 py-1 text-gray-600 hover:bg-gray-100 rounded"
                    title="Previous Year"
                  >
                    «
                  </button>
                  <button
                    onClick={goToPreviousMonth}
                    className="px-2 py-1 text-gray-600 hover:bg-gray-100 rounded"
                    title="Previous Month"
                  >
                    ‹
                  </button>
                </div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                </h3>
                <div className="flex items-center gap-2">
                  <button
                    onClick={goToNextMonth}
                    className="px-2 py-1 text-gray-600 hover:bg-gray-100 rounded"
                    title="Next Month"
                  >
                    ›
                  </button>
                  <button
                    onClick={goToNextYear}
                    className="px-2 py-1 text-gray-600 hover:bg-gray-100 rounded"
                    title="Next Year"
                  >
                    »
                  </button>
                </div>
                <button
                  onClick={() => setShowCalendar(false)}
                  className="text-gray-400 hover:text-gray-600 ml-2"
                >
                  ×
                </button>
              </div>

              <div className="grid grid-cols-7 gap-1">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day, index) => (
                  <div key={day} className="text-center text-sm font-medium text-gray-700 p-2">
                    {day}
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-7 gap-1">
                {getDaysInMonth(currentMonth).map((day, index) => (
                  <button
                    key={index}
                    onClick={() => handleDateClick(day)}
                    className={`p-2 text-sm rounded ${
                      day === null
                        ? 'text-gray-400'
                        : day === new Date(selectedDate).getDate() &&
                          currentMonth.getMonth() === new Date(selectedDate).getMonth() &&
                          currentMonth.getFullYear() === new Date(selectedDate).getFullYear()
                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    } transition-colors`}
                    disabled={day === null}
                  >
                    {day || ''}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    );
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

      {/* Date Selection and Return Tiles */}
      <div className="mb-8">
        <Calendar 
          selectedDate={selectedDate}
          onDateChange={(date) => {
            setSelectedDate(date);
            calculateReturnsSinceDate(date);
          }}
        />
        
        {/* Return Tiles */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Weekly Return</h3>
            <p className="text-2xl font-bold text-gray-900">
              {weeklyReturn !== null ? `${weeklyReturn.toFixed(2)}%` : 'N/A'}
            </p>
            <p className="text-xs text-gray-600 mt-1">
              Since {new Date(selectedDate).toLocaleDateString()}
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Monthly Return</h3>
            <p className="text-2xl font-bold text-gray-900">
              {monthlyReturn !== null ? `${monthlyReturn.toFixed(2)}%` : 'N/A'}
            </p>
            <p className="text-xs text-gray-600 mt-1">
              Since {new Date(selectedDate).toLocaleDateString()}
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Cumulative Return</h3>
            <p className="text-2xl font-bold text-gray-900">
              {cumulativeReturn !== null ? `${cumulativeReturn.toFixed(2)}%` : 'N/A'}
            </p>
            <p className="text-xs text-gray-600 mt-1">
              Since {new Date(selectedDate).toLocaleDateString()}
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500 mb-2">NIFTY Return</h3>
            <p className="text-2xl font-bold text-gray-900">
              {niftyReturn !== null ? `${niftyReturn.toFixed(2)}%` : 'N/A'}
            </p>
            <p className="text-xs text-gray-600 mt-1">
              Since {new Date(selectedDate).toLocaleDateString()}
            </p>
          </div>
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
