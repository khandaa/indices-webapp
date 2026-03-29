import React, { useState, useEffect } from 'react';
import DataTable from '../components/DataTable';
import ColumnToggle from '../components/ColumnToggle';
import { apiService } from '../services/api';
import { Index, ColumnConfig } from '../types';

const IndicesPage: React.FC = () => {
  const [indices, setIndices] = useState<Index[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortColumn, setSortColumn] = useState<string>('name');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [columnConfig, setColumnConfig] = useState<ColumnConfig>({
    name: true,
    symbol: true,
    current_price: true,
    daily_change: true,
    weekly_change: true,
    monthly_change: true,
    yearly_change: true,
    daily_change_percent: false,
    weekly_change_percent: false,
    monthly_change_percent: false,
    yearly_change_percent: false,
  });

  // Load column config from localStorage on mount
  useEffect(() => {
    const savedConfig = localStorage.getItem('columnConfig');
    if (savedConfig) {
      try {
        setColumnConfig(JSON.parse(savedConfig));
      } catch (error) {
        console.error('Error loading column config:', error);
      }
    }
  }, []);

  // Save column config to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('columnConfig', JSON.stringify(columnConfig));
  }, [columnConfig]);

  // Fetch indices data
  const fetchIndices = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getIndices();
      setIndices(data);
    } catch (error) {
      setError('Failed to fetch indices data');
      console.error('Error fetching indices:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIndices();
  }, []);

  // Sort functionality
  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  // Column toggle functionality
  const handleColumnToggle = (column: keyof ColumnConfig) => {
    setColumnConfig(prev => ({
      ...prev,
      [column]: !prev[column],
    }));
  };

  // Sort indices
  const sortedIndices = React.useMemo(() => {
    return [...indices].sort((a, b) => {
      const aValue = a[sortColumn as keyof Index];
      const bValue = b[sortColumn as keyof Index];

      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
      }

      return 0;
    });
  }, [indices, sortColumn, sortDirection]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="text-red-800">{error}</div>
        <button
          onClick={fetchIndices}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Indices Performance</h1>
        <div className="space-x-2">
          <button
            onClick={fetchIndices}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      <ColumnToggle 
        columnConfig={columnConfig} 
        onColumnToggle={handleColumnToggle} 
      />

      <DataTable
        indices={sortedIndices}
        columnConfig={columnConfig}
        onSort={handleSort}
        sortColumn={sortColumn}
        sortDirection={sortDirection}
      />

      <div className="mt-6 text-sm text-gray-500">
        Showing {sortedIndices.length} indices
      </div>
    </div>
  );
};

export default IndicesPage;
