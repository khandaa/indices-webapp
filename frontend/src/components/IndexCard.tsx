import React from 'react';
import { Index } from '../types';

interface IndexCardProps {
  index: Index;
  onClick?: () => void;
  className?: string;
  variant?: 'default' | 'compact' | 'detailed';
}

const IndexCard: React.FC<IndexCardProps> = ({ 
  index, 
  onClick, 
  className = '',
  variant = 'default'
}) => {
  const formatPrice = (price: number | null) => {
    if (price === null) return 'N/A';
    return price.toFixed(2);
  };

  const formatChange = (change: number | null, changePercent: number | null) => {
    if (change === null || changePercent === null) return 'N/A';
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(2)} (${sign}${changePercent.toFixed(2)}%)`;
  };

  const getChangeColor = (change: number | null) => {
    if (change === null) return 'text-gray-500';
    return change >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const getChangeBgColor = (change: number | null) => {
    if (change === null) return 'bg-gray-100';
    return change >= 0 ? 'bg-green-50' : 'bg-red-50';
  };

  if (variant === 'compact') {
    return (
      <div 
        className={`p-3 border border-gray-200 rounded-lg hover:shadow-md transition-shadow cursor-pointer ${className}`}
        onClick={onClick}
      >
        <div className="flex justify-between items-center">
          <div>
            <h3 className="font-semibold text-gray-900">{index.name}</h3>
            <p className="text-sm text-gray-600">{index.symbol}</p>
          </div>
          <div className="text-right">
            <p className="font-semibold text-gray-900">{formatPrice(index.current_price)}</p>
            <p className={`text-sm ${getChangeColor(index.daily_change)}`}>
              {formatChange(index.daily_change, index.daily_change_percent)}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (variant === 'detailed') {
    return (
      <div 
        className={`p-4 border border-gray-200 rounded-lg hover:shadow-lg transition-shadow cursor-pointer ${className}`}
        onClick={onClick}
      >
        <div className="mb-3">
          <h3 className="text-lg font-semibold text-gray-900">{index.name}</h3>
          <p className="text-sm text-gray-600">{index.symbol}</p>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Current Price</p>
            <p className="font-semibold text-gray-900">{formatPrice(index.current_price)}</p>
          </div>
          
          <div>
            <p className="text-sm text-gray-500">Daily Change</p>
            <p className={`font-semibold ${getChangeColor(index.daily_change)}`}>
              {formatChange(index.daily_change, index.daily_change_percent)}
            </p>
          </div>
          
          <div>
            <p className="text-sm text-gray-500">Weekly Change</p>
            <p className={`font-semibold ${getChangeColor(index.weekly_change)}`}>
              {formatChange(index.weekly_change, index.weekly_change_percent)}
            </p>
          </div>
          
          <div>
            <p className="text-sm text-gray-500">Monthly Change</p>
            <p className={`font-semibold ${getChangeColor(index.monthly_change)}`}>
              {formatChange(index.monthly_change, index.monthly_change_percent)}
            </p>
          </div>
        </div>
        
        {index.calculation_date && (
          <p className="text-xs text-gray-500 mt-3">
            Last updated: {new Date(index.calculation_date).toLocaleDateString()}
          </p>
        )}
      </div>
    );
  }

  return (
    <div 
      className={`p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow cursor-pointer ${className}`}
      onClick={onClick}
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="font-semibold text-gray-900">{index.name}</h3>
          <p className="text-sm text-gray-600">{index.symbol}</p>
        </div>
        <div className={`px-2 py-1 rounded ${getChangeBgColor(index.daily_change)}`}>
          <p className={`font-semibold ${getChangeColor(index.daily_change)}`}>
            {formatChange(index.daily_change, index.daily_change_percent)}
          </p>
        </div>
      </div>
      
      <div className="grid grid-cols-3 gap-2 text-center">
        <div>
          <p className="text-xs text-gray-500">Price</p>
          <p className="font-semibold text-gray-900">{formatPrice(index.current_price)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Weekly</p>
          <p className={`font-semibold ${getChangeColor(index.weekly_change)}`}>
            {formatChange(index.weekly_change, index.weekly_change_percent)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Monthly</p>
          <p className={`font-semibold ${getChangeColor(index.monthly_change)}`}>
            {formatChange(index.monthly_change, index.monthly_change_percent)}
          </p>
        </div>
      </div>
    </div>
  );
};

export default IndexCard;
