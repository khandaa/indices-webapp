import React from 'react';

const Strategy: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Investment Strategy</h1>
      
      <div className="prose prose-lg max-w-none">
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Momentum-Based Investment Approach</h2>
          <p className="text-gray-600 mb-4">
            Our investment strategy is based on the principle of <strong>momentum</strong> - the tendency of 
            assets that have performed well in the recent past to continue performing well in the near future. 
            This approach is grounded in academic research and practical observation of market behavior.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Methodology: 3-Week and 3-Month Rolling Returns</h2>
          
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4">
            <h3 className="font-semibold text-blue-800 mb-2">Key Metrics</h3>
            <ul className="list-disc list-inside text-blue-700 space-y-1">
              <li><strong>3-Week (3W) Rolling Return:</strong> Cumulative return over the last 21 trading days</li>
              <li><strong>3-Month (3M) Rolling Return:</strong> Cumulative return over the last ~63 trading days</li>
            </ul>
          </div>

          <p className="text-gray-600 mb-4">
            Unlike simple weekly or monthly returns which only measure performance within a specific period, 
            our rolling return methodology provides a smoother, more comprehensive view of recent performance 
            trends.
          </p>

          <h3 className="text-xl font-medium text-gray-700 mb-2">Why Rolling Returns?</h3>
          <ul className="list-disc list-inside text-gray-600 space-y-2 mb-4">
            <li>Smooths out volatility by considering multiple time windows</li>
            <li>Captures sustained trends rather than one-time movements</li>
            <li>Reduces the impact of a single day's performance on the overall assessment</li>
            <li>Provides a more stable basis for comparison across different indices</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">How We Rank Indices</h2>
          
          <div className="grid md:grid-cols-2 gap-4 mb-4">
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="font-semibold text-green-800 mb-2">Weekly Recommendations</h3>
              <p className="text-green-700 text-sm">
                Indices are ranked by their <strong>3-Week Rolling Return</strong>. 
                This captures medium-term momentum and helps identify indices showing 
                consistent weekly strength.
              </p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <h3 className="font-semibold text-purple-800 mb-2">Monthly Recommendations</h3>
              <p className="text-purple-700 text-sm">
                Indices are ranked by their <strong>3-Month Rolling Return</strong>. 
                This captures longer-term momentum trends and helps identify 
                sustained performance over quarters.
              </p>
            </div>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Niftybees as Benchmark</h2>
          <p className="text-gray-600 mb-4">
            <strong>Niftybees (NIFTYBEES)</strong> serves as our primary benchmark. This ETF tracks the Nifty 50 index, 
            representing the 50 largest companies on the National Stock Exchange (NSE) of India. By comparing 
            each index's performance against Niftybees, you can assess whether an index is outperforming or 
            underperforming the broader market.
          </p>
          <div className="bg-gray-100 p-4 rounded-lg">
            <h3 className="font-medium text-gray-800 mb-2">What to Look For</h3>
            <ul className="list-disc list-inside text-gray-600 space-y-1">
              <li>An index with a 3W/3M return significantly higher than Niftybees' indicates strong momentum</li>
              <li>Consistent outperformance over multiple periods suggests sustainable momentum</li>
              <li>Compare both the magnitude and consistency of returns</li>
            </ul>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Investment Considerations</h2>
          
          <div className="space-y-4">
            <div className="border-l-4 border-yellow-500 pl-4">
              <h3 className="font-medium text-gray-800">Past Performance</h3>
              <p className="text-gray-600 text-sm">
                Historical momentum does not guarantee future results. Markets can reverse trends quickly.
              </p>
            </div>
            
            <div className="border-l-4 border-yellow-500 pl-4">
              <h3 className="font-medium text-gray-800">Sector Concentration</h3>
              <p className="text-gray-600 text-sm">
                Many indices are sector-specific (IT, Banking, Pharma, etc.). Consider your overall portfolio 
                allocation before adding concentrated sector exposure.
              </p>
            </div>
            
            <div className="border-l-4 border-yellow-500 pl-4">
              <h3 className="font-medium text-gray-800">Volatility</h3>
              <p className="text-gray-600 text-sm">
                Higher momentum often comes with higher volatility. Smallcap and thematic indices tend to be 
                more volatile than large-cap indices.
              </p>
            </div>
            
            <div className="border-l-4 border-yellow-500 pl-4">
              <h3 className="font-medium text-gray-800">Liquidity</h3>
              <p className="text-gray-600 text-sm">
                Consider the trading volume and bid-ask spreads of the ETF. Liquid ETFs are easier to buy and sell 
                at fair prices.
              </p>
            </div>
          </div>
        </section>

        <section className="bg-blue-100 p-6 rounded-lg">
          <h2 className="text-xl font-semibold text-blue-900 mb-3">Summary</h2>
          <p className="text-blue-800">
            Our system identifies indices with the strongest recent momentum using a 3-week and 3-month 
            rolling return framework. These recommendations should be used as a starting point for research, 
            not as direct investment advice. Always consider your risk tolerance, investment horizon, and 
            existing portfolio allocation before making investment decisions.
          </p>
        </section>
      </div>
    </div>
  );
};

export default Strategy;