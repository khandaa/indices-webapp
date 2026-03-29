import React from 'react';
import { Index, ColumnConfig } from '../types';

interface DataTableProps {
  indices: Index[];
  columnConfig: ColumnConfig;
  onSort: (column: string) => void;
  sortColumn: string;
  sortDirection: 'asc' | 'desc';
}

const DataTable: React.FC<DataTableProps> = ({
  indices,
  columnConfig,
  onSort,
  sortColumn,
  sortDirection,
}) => {
  const formatNumber = (value: number | null, decimals: number = 2): string => {
    if (value === null || value === undefined) return 'N/A';
    return value.toFixed(decimals);
  };

  const formatPercent = (value: number | null): string => {
    if (value === null || value === undefined) return 'N/A';
    const formatted = formatNumber(value, 2);
    return `${formatted}%`;
  };

  const getChangeClass = (value: number | null): string => {
    if (value === null || value === undefined) return '';
    return value >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const renderSortIcon = (column: string) => {
    if (sortColumn !== column) return '';
    return sortDirection === 'asc' ? ' ↑' : ' ↓';
  };

  const renderSortableHeader = (column: string, label: string) => {
    if (!columnConfig[column as keyof ColumnConfig]) return null;
    return (
      <th
        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
        onClick={() => onSort(column)}
      >
        {label}{renderSortIcon(column)}
      </th>
    );
  };

  return (
    <div className="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
      <table className="min-w-full divide-y divide-gray-300">
        <thead className="bg-gray-50">
          <tr>
            {renderSortableHeader('name', 'Name')}
            {renderSortableHeader('symbol', 'Symbol')}
            {renderSortableHeader('current_price', 'Current Price')}
            {renderSortableHeader('daily_change', 'Daily Change')}
            {renderSortableHeader('daily_change_percent', 'Daily %')}
            {renderSortableHeader('weekly_change', 'Weekly Change')}
            {renderSortableHeader('weekly_change_percent', 'Weekly %')}
            {renderSortableHeader('monthly_change', 'Monthly Change')}
            {renderSortableHeader('monthly_change_percent', 'Monthly %')}
            {renderSortableHeader('yearly_change', 'Yearly Change')}
            {renderSortableHeader('yearly_change_percent', 'Yearly %')}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {indices.map((index) => (
            <tr key={index.id} className="hover:bg-gray-50">
              {columnConfig.name && (
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {index.name}
                </td>
              )}
              {columnConfig.symbol && (
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {index.symbol}
                </td>
              )}
              {columnConfig.current_price && (
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatNumber(index.current_price)}
                </td>
              )}
              {columnConfig.daily_change && (
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${getChangeClass(index.daily_change)}`}>
                  {formatNumber(index.daily_change)}
                </td>
              )}
              {columnConfig.daily_change_percent && (
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${getChangeClass(index.daily_change_percent)}`}>
                  {formatPercent(index.daily_change_percent)}
                </td>
              )}
              {columnConfig.weekly_change && (
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${getChangeClass(index.weekly_change)}`}>
                  {formatNumber(index.weekly_change)}
                </td>
              )}
              {columnConfig.weekly_change_percent && (
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${getChangeClass(index.weekly_change_percent)}`}>
                  {formatPercent(index.weekly_change_percent)}
                </td>
              )}
              {columnConfig.monthly_change && (
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${getChangeClass(index.monthly_change)}`}>
                  {formatNumber(index.monthly_change)}
                </td>
              )}
              {columnConfig.monthly_change_percent && (
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${getChangeClass(index.monthly_change_percent)}`}>
                  {formatPercent(index.monthly_change_percent)}
                </td>
              )}
              {columnConfig.yearly_change && (
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${getChangeClass(index.yearly_change)}`}>
                  {formatNumber(index.yearly_change)}
                </td>
              )}
              {columnConfig.yearly_change_percent && (
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${getChangeClass(index.yearly_change_percent)}`}>
                  {formatPercent(index.yearly_change_percent)}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
