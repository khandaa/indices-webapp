import React from 'react';
import { ColumnConfig } from '../types';

interface ColumnToggleProps {
  columnConfig: ColumnConfig;
  onColumnToggle: (column: keyof ColumnConfig) => void;
}

const ColumnToggle: React.FC<ColumnToggleProps> = ({ columnConfig, onColumnToggle }) => {
  const columnLabels: { [key in keyof ColumnConfig]: string } = {
    name: 'Name',
    symbol: 'Symbol',
    current_price: 'Current Price',
    daily_change: 'Daily Change',
    weekly_change: 'Weekly Change',
    monthly_change: 'Monthly Change',
    yearly_change: 'Yearly Change',
    daily_change_percent: 'Daily %',
    weekly_change_percent: 'Weekly %',
    monthly_change_percent: 'Monthly %',
    yearly_change_percent: 'Yearly %',
    three_week_cumulative_return: '3W Return',
    three_month_cumulative_return: '3M Return',
  };

  const presets = [
    {
      name: 'Basic',
      config: {
        name: true,
        symbol: true,
        current_price: true,
        daily_change: true,
        weekly_change: false,
        monthly_change: false,
        yearly_change: false,
        daily_change_percent: true,
        weekly_change_percent: false,
        monthly_change_percent: false,
        yearly_change_percent: false,
        three_week_cumulative_return: false,
        three_month_cumulative_return: false,
      } as ColumnConfig,
    },
    {
      name: 'Detailed',
      config: {
        name: true,
        symbol: true,
        current_price: true,
        daily_change: true,
        weekly_change: true,
        monthly_change: true,
        yearly_change: true,
        daily_change_percent: true,
        weekly_change_percent: true,
        monthly_change_percent: true,
        yearly_change_percent: true,
        three_week_cumulative_return: true,
        three_month_cumulative_return: true,
      } as ColumnConfig,
    },
    {
      name: 'Percentages Only',
      config: {
        name: true,
        symbol: true,
        current_price: true,
        daily_change: false,
        weekly_change: false,
        monthly_change: false,
        yearly_change: false,
        daily_change_percent: true,
        weekly_change_percent: true,
        monthly_change_percent: true,
        yearly_change_percent: true,
        three_week_cumulative_return: true,
        three_month_cumulative_return: true,
      } as ColumnConfig,
    },
    {
      name: 'Momentum',
      config: {
        name: true,
        symbol: true,
        current_price: true,
        daily_change: true,
        weekly_change: true,
        monthly_change: true,
        yearly_change: false,
        daily_change_percent: true,
        weekly_change_percent: true,
        monthly_change_percent: true,
        yearly_change_percent: false,
        three_week_cumulative_return: true,
        three_month_cumulative_return: true,
      } as ColumnConfig,
    },
  ];

  const applyPreset = (preset: typeof presets[0]) => {
    Object.entries(preset.config).forEach(([column, value]) => {
      onColumnToggle(column as keyof ColumnConfig);
    });
  };

  const resetToDefault = () => {
    const defaultConfig: ColumnConfig = {
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
      three_week_cumulative_return: false,
      three_month_cumulative_return: false,
    };

    Object.entries(defaultConfig).forEach(([column, value]) => {
      if (value !== columnConfig[column as keyof ColumnConfig]) {
        onColumnToggle(column as keyof ColumnConfig);
      }
    });
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900">Column Configuration</h3>
        <div className="space-x-2">
          {presets.map((preset) => (
            <button
              key={preset.name}
              onClick={() => applyPreset(preset)}
              className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
            >
              {preset.name}
            </button>
          ))}
          <button
            onClick={resetToDefault}
            className="px-3 py-1 text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-md transition-colors"
          >
            Reset to Default
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {Object.entries(columnLabels).map(([column, label]) => (
          <label key={column} className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={columnConfig[column as keyof ColumnConfig]}
              onChange={() => onColumnToggle(column as keyof ColumnConfig)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">{label}</span>
          </label>
        ))}
      </div>
    </div>
  );
};

export default ColumnToggle;
