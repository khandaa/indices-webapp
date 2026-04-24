import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';
import { apiService } from '../services/api';

interface IndexInfo {
  id: number;
  name: string;
  symbol: string;
  current_price?: number;
  weekly_change_percent?: number;
  monthly_change_percent?: number;
  yearly_change_percent?: number;
}

interface PriceData {
  date: string;
  close_price: number;
  daily_change_percent: number | null;
}

type SortOption = 'name' | 'weekly' | 'monthly' | 'yearly';
type ViewMode = 'table' | 'chart';

const Comparison: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [indices, setIndices] = useState<IndexInfo[]>([]);
  const [selectedIndices, setSelectedIndices] = useState<number[]>([]);
  const [viewMode, setViewMode] = useState<ViewMode>('table');
  const [chartType, setChartType] = useState<'line' | 'bar'>('line');
  const [comparisonData, setComparisonData] = useState<Record<number, PriceData[]>>({});
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState('30');
  const [sortBy, setSortBy] = useState<SortOption>('weekly');
  const [normalizePrices, setNormalizePrices] = useState(true);

  useEffect(() => {
    loadIndices();
  }, []);

  useEffect(() => {
    const indicesParam = searchParams.get('indices');
    if (indicesParam) {
      const symbols = indicesParam.split(',');
      const selected = indices
        .filter(idx => symbols.includes(idx.symbol))
        .map(idx => idx.id);
      if (selected.length > 0) {
        setSelectedIndices(prev => Array.from(new Set([...prev, ...selected])));
      }
    }
  }, [searchParams, indices]);

  useEffect(() => {
    if (selectedIndices.length > 0) {
      loadComparisonData();
    }
  }, [selectedIndices, dateRange]);

  const loadIndices = async () => {
    try {
      const data = await apiService.getIndices();
      const indexData = data.map((i: any) => ({
        id: i.id,
        name: i.name,
        symbol: i.symbol,
        current_price: i.current_price,
        weekly_change_percent: i.weekly_change_percent,
        monthly_change_percent: i.monthly_change_percent,
        yearly_change_percent: i.yearly_change_percent
      }));
      setIndices(indexData);
    } catch (error) {
      console.error('Error loading indices:', error);
    }
  };

  const loadComparisonData = async () => {
    setLoading(true);
    try {
      const limit = parseInt(dateRange);
      const data: Record<number, PriceData[]> = {};
      
      for (const indexId of selectedIndices) {
        const prices = await apiService.getDailyPrices(indexId, limit);
        data[indexId] = prices.map((p: any) => ({
          date: p.date,
          close_price: p.close_price,
          daily_change_percent: p.daily_change_percent
        }));
      }
      
      setComparisonData(data);
    } catch (error) {
      console.error('Error loading comparison data:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleIndex = (indexId: number) => {
    setSelectedIndices(prev => 
      prev.includes(indexId)
        ? prev.filter(id => id !== indexId)
        : [...prev, indexId]
    );
  };

  const formatPercent = (value: number | null | undefined): string => {
    if (value === null || value === undefined) return 'N/A';
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getSortedIndices = (): IndexInfo[] => {
    return [...indices].sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'weekly':
          return (b.weekly_change_percent || 0) - (a.weekly_change_percent || 0);
        case 'monthly':
          return (b.monthly_change_percent || 0) - (a.monthly_change_percent || 0);
        case 'yearly':
          return (b.yearly_change_percent || 0) - (a.yearly_change_percent || 0);
        default:
          return 0;
      }
    });
  };

  const getAllDates = (): string[] => {
    if (Object.keys(comparisonData).length === 0) return [];
    const firstIndexData = comparisonData[selectedIndices[0]] || [];
    return firstIndexData.map(d => d.date).reverse();
  };

  const getChartData = () => {
    const dates = getAllDates();
    
    // For normalization: get starting prices for each index
    const startPrices: Record<number, number> = {};
    if (normalizePrices) {
      selectedIndices.forEach(id => {
        const data = comparisonData[id] || [];
        if (data.length > 0) {
          startPrices[id] = data[data.length - 1].close_price;
        }
      });
    }
    
    return dates.map(date => {
      const point: Record<string, string | number> = { date };
      selectedIndices.forEach(id => {
        const data = comparisonData[id] || [];
        const dayData = data.find(d => d.date === date);
        const index = indices.find(i => i.id === id);
        if (dayData && index && dayData.close_price != null) {
          let value = dayData.close_price;
          // Normalize: show percentage change from start
          if (normalizePrices && startPrices[id]) {
            value = ((dayData.close_price - startPrices[id]) / startPrices[id]) * 100;
          }
          point[index.symbol] = value;
        }
      });
      return point;
    });
  };

  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Performance Comparison</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('table')}
            className={`px-3 py-1 rounded text-sm ${
              viewMode === 'table' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
            }`}
          >
            Table
          </button>
          <button
            onClick={() => setViewMode('chart')}
            className={`px-3 py-1 rounded text-sm ${
              viewMode === 'chart' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
            }`}
          >
            Chart
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
        {/* Index Selector */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Select Indices</h3>
            {/* Sort Options */}
            <div className="mb-3">
              <label className="text-xs text-gray-500 mb-1 block">Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortOption)}
                className="w-full border rounded px-2 py-1 text-sm"
              >
                <option value="name">Name (A-Z)</option>
                <option value="weekly">Weekly Return</option>
                <option value="monthly">Monthly Return</option>
                <option value="yearly">Yearly Return</option>
              </select>
            </div>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {getSortedIndices().map(index => (
                <label
                  key={index.id}
                  className={`flex items-center p-2 rounded cursor-pointer ${
                    selectedIndices.includes(index.id) ? 'bg-blue-50' : 'hover:bg-gray-50'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedIndices.includes(index.id)}
                    onChange={() => toggleIndex(index.id)}
                    className="h-4 w-4 text-blue-600 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">{index.symbol}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-sm font-medium text-gray-700">
                {viewMode === 'table' ? 'Performance Table' : 'Performance Chart'}
              </h3>
              <div className="flex gap-2 items-center">
                {viewMode === 'chart' && (
                  <div className="flex gap-1">
                    <label className="flex items-center gap-1 text-xs">
                      <input
                        type="checkbox"
                        checked={normalizePrices}
                        onChange={(e) => setNormalizePrices(e.target.checked)}
                        className="h-3 w-3"
                      />
                      <span>Normalized</span>
                    </label>
                    <button
                      onClick={() => setChartType('line')}
                      className={`px-2 py-1 rounded text-xs ${
                        chartType === 'line' ? 'bg-blue-600 text-white' : 'bg-gray-200'
                      }`}
                    >
                      Line
                    </button>
                    <button
                      onClick={() => setChartType('bar')}
                      className={`px-2 py-1 rounded text-xs ${
                        chartType === 'bar' ? 'bg-blue-600 text-white' : 'bg-gray-200'
                      }`}
                    >
                      Bar
                    </button>
                  </div>
                )}
                <select
                  value={dateRange}
                  onChange={(e) => setDateRange(e.target.value)}
                  className="border rounded px-2 py-1 text-sm"
                >
                  <option value="7">Last 7 days</option>
                  <option value="30">Last 30 days</option>
                  <option value="90">Last 90 days</option>
                  <option value="180">Last 6 months</option>
                  <option value="365">Last 1 year</option>
                </select>
              </div>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p className="mt-2 text-gray-600">Loading...</p>
              </div>
            ) : selectedIndices.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                Select at least one index to compare
              </div>
            ) : viewMode === 'table' ? (
              <div className="overflow-x-auto">
                {/* Default Summary Table */}
                <table className="min-w-full text-sm mb-6">
                  <thead>
                    <tr className="border-b bg-gray-50">
                      <th className="py-2 text-left text-gray-500 font-medium">Instrument</th>
                      <th className="py-2 text-right text-gray-500 font-medium">This Week</th>
                      <th className="py-2 text-right text-gray-500 font-medium">This Month</th>
                      <th className="py-2 text-right text-gray-500 font-medium">This Year</th>
                    </tr>
                  </thead>
<tbody>
                    {getSortedIndices()
                      .filter(i => selectedIndices.includes(i.id))
                      .map(index => (
                        <tr key={index.id} className="border-b hover:bg-gray-50">
                          <td className="py-2 font-medium text-gray-900">{index.name}</td>
                          <td className={`py-2 text-right font-medium ${
                            (index.weekly_change_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {formatPercent(index.weekly_change_percent)}
                          </td>
                          <td className={`py-2 text-right font-medium ${
                            (index.monthly_change_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {formatPercent(index.monthly_change_percent)}
                          </td>
                          <td className={`py-2 text-right font-medium ${
                            (index.yearly_change_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {formatPercent(index.yearly_change_percent)}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  {chartType === 'line' ? (
                    <LineChart data={getChartData()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip formatter={(value) => [`${Number(value).toFixed(2)}${normalizePrices ? '%' : ''}`, normalizePrices ? 'Change %' : 'Close Price']} />
                      <Legend />
                      {selectedIndices.map((id, idx) => {
                        const index = indices.find(i => i.id === id);
                        return (
                          <Line
                            key={id}
                            type="monotone"
                            dataKey={index?.symbol}
                            stroke={colors[idx % colors.length]}
                            strokeWidth={2}
                            dot={false}
                          />
                        );
                      })}
                    </LineChart>
                  ) : (
                    <BarChart data={getChartData()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip formatter={(value) => [`${Number(value).toFixed(2)}${normalizePrices ? '%' : ''}`, normalizePrices ? 'Change %' : 'Close Price']} />
                      <Legend />
                      {selectedIndices.map((id, idx) => {
                        const index = indices.find(i => i.id === id);
                        return (
                          <Bar
                            key={id}
                            dataKey={index?.symbol}
                            fill={colors[idx % colors.length]}
                          />
                        );
                      })}
                    </BarChart>
                  )}
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Comparison;