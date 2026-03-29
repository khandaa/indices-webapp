import React from 'react';

interface MomentumIndicatorProps {
  value: number | null;
  showArrow?: boolean;
  showBackground?: boolean;
  size?: 'small' | 'medium' | 'large';
  className?: string;
}

const MomentumIndicator: React.FC<MomentumIndicatorProps> = ({ 
  value, 
  showArrow = true, 
  showBackground = false,
  size = 'medium',
  className = ''
}) => {
  if (value === null || value === undefined) {
    return <span className={`text-gray-500 ${className}`}>N/A</span>;
  }

  const isPositive = value >= 0;
  const formattedValue = `${isPositive ? '+' : ''}${value.toFixed(2)}%`;

  const sizeClasses = {
    small: 'text-xs',
    medium: 'text-sm',
    large: 'text-base'
  };

  const arrowSize = {
    small: 'w-2 h-2',
    medium: 'w-3 h-3',
    large: 'w-4 h-4'
  };

  const bgColorClass = showBackground 
    ? isPositive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
    : '';

  const textColorClass = showBackground
    ? ''
    : isPositive ? 'text-green-600' : 'text-red-600';

  const content = (
    <span className={`inline-flex items-center font-medium ${sizeClasses[size]} ${textColorClass} ${bgColorClass} ${className}`}>
      {showArrow && (
        <svg 
          className={`${arrowSize[size]} mr-1 ${isPositive ? 'text-green-500' : 'text-red-500'}`}
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          {isPositive ? (
            <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
          ) : (
            <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
          )}
        </svg>
      )}
      {formattedValue}
    </span>
  );

  if (showBackground) {
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full ${bgColorClass} ${className}`}>
        {content}
      </span>
    );
  }

  return content;
};

export default MomentumIndicator;
