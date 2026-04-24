import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { apiService } from '../services/api';

interface PriceRow {
  date: string;
  [key: string]: string | number;
}

const PeriodDetail: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [priceData, setPriceData] = useState<PriceRow[]>([]);
  const [symbols, setSymbols] = useState<string[]>([]);
  const [strategyStart, setStrategyStart] = useState(0);
  const [strategyEnd, setStrategyEnd] = useState(0);
  const [niftybeesStart, setNiftybeesStart] = useState(0);
  const [niftybeesEnd, setNiftybeesEnd] = useState(0);

  const startDate = searchParams.get('start') || '';
  const endDate = searchParams.get('end') || '';
  const rec1 = searchParams.get('rec1') || '';
  const rec2 = searchParams.get('rec2') || '';
  const rec3 = searchParams.get('rec3') || '';
  const amount1 = parseFloat(searchParams.get('amt1') || '0');
  const amount2 = parseFloat(searchParams.get('amt2') || '0');
  const amount3 = parseFloat(searchParams.get('amt3') || '0');
  const final1 = parseFloat(searchParams.get('final1') || '0');
  const final2 = parseFloat(searchParams.get('final2') || '0');
  const final3 = parseFloat(searchParams.get('final3') || '0');
  const return1 = parseFloat(searchParams.get('ret1') || '0');
  const return2 = parseFloat(searchParams.get('ret2') || '0');
  const return3 = parseFloat(searchParams.get('ret3') || '0');

  useEffect(() => {
    loadPeriodData();
  }, [startDate, endDate, rec1, rec2, rec3]);

  const loadPeriodData = async () => {
    setLoading(true);
    try {
      const indices = await apiService.getIndices();
      const allSymbols = [rec1, rec2, rec3, 'NIFTYBEES'].filter(s => s);
      setSymbols(allSymbols);

      const symbolPrices: { [key: string]: { date: string; close_price: number }[] } = {};

      for (const symbol of allSymbols) {
        const index = indices.find((i: any) => i.symbol === symbol);
        if (!index) continue;

        const prices = await apiService.getDailyPrices(index.id, 200);
        const filteredPrices = prices
          .filter((p: any) => p.date >= startDate && p.date <= endDate)
          .map((p: any) => ({ date: p.date, close_price: p.close_price || 0 }));
        symbolPrices[symbol] = filteredPrices;
      }

      const dates = new Set<string>();
      allSymbols.forEach(sym => {
        if (symbolPrices[sym]) {
          symbolPrices[sym].forEach(p => dates.add(p.date));
        }
      });

      const sortedDates = Array.from(dates).sort();
      const priceRows: PriceRow[] = sortedDates.map(date => {
        const row: PriceRow = { date };
        allSymbols.forEach(sym => {
          const priceEntry = symbolPrices[sym]?.find((p: any) => p.date === date);
          row[sym] = priceEntry?.close_price || '-';
        });
        return row;
      });

      setPriceData(priceRows);
      setStrategyStart(parseFloat(searchParams.get('strategyStart') || '0'));
      setStrategyEnd(parseFloat(searchParams.get('strategyEnd') || '0'));
      setNiftybeesStart(parseFloat(searchParams.get('niftybeesStart') || '0'));
      setNiftybeesEnd(parseFloat(searchParams.get('niftybeesEnd') || '0'));

    } catch (error) {
      console.error('Error loading period data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPrice = (value: string | number) => {
    if (value === '-' || value === null || value === undefined) return '-';
    return Number(value).toFixed(2);
  };

  const getIndexName = (symbol: string) => {
    const names: { [key: string]: string } = {
      'NIFTYBEES': 'Niftybees',
      'SILVERBEES': 'SilverBees',
      'GOLDBEES': 'GoldBees',
      'MONQ50': 'Momentum 50',
      'SMALLCAP': 'SmallCap',
      'MODEFENCE': 'Modi Defence',
      'LIQUIDBEES': 'LiquidBees',
      'ITBEES': 'IT Bees',
      'HEALTHIETF': 'Health ETF',
      'PHARMABEES': 'Pharma Bees'
    };
    return names[symbol] || symbol;
  };

  const strategyReturn = strategyStart > 0 ? ((strategyEnd - strategyStart) / strategyStart) * 100 : 0;
  const niftybeesReturn = niftybeesStart > 0 ? ((niftybeesEnd - niftybeesStart) / niftybeesStart) * 100 : 0;

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link to="/whatif" className="text-blue-600 hover:text-blue-800 text-sm mb-2 inline-block">
            Back to What-If
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">
            Period Detail: {startDate} to {endDate}
          </h1>
        </div>
      </div>

      {/* Summary Section */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Investment Summary</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Strategy Summary */}
          <div className="border rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-500 mb-3">Strategy Performance</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Amount Invested:</span>
                <span className="font-medium">{formatCurrency(strategyStart)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Final Amount:</span>
                <span className="font-medium">{formatCurrency(strategyEnd)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Return:</span>
                <span className={`font-bold ${strategyReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {strategyReturn >= 0 ? '+' : ''}{strategyReturn.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>

          {/* Niftybees Summary */}
          <div className="border rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-500 mb-3">Niftybees (Benchmark)</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Amount Invested:</span>
                <span className="font-medium">{formatCurrency(niftybeesStart)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Final Amount:</span>
                <span className="font-medium">{formatCurrency(niftybeesEnd)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Return:</span>
                <span className={`font-bold ${niftybeesReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {niftybeesReturn >= 0 ? '+' : ''}{niftybeesReturn.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>

          {/* Instrument 1 */}
          {rec1 && (
            <div className="border rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-500 mb-1">{getIndexName(rec1)} (50%)</h3>
              <p className="text-xs text-gray-400 mb-3">{rec1}</p>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Invested:</span>
                  <span className="font-medium">{formatCurrency(amount1)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Final:</span>
                  <span className="font-medium">{formatCurrency(final1)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Return:</span>
                  <span className={`font-bold ${return1 >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {return1 >= 0 ? '+' : ''}{return1.toFixed(2)}%
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Instrument 2 */}
          {rec2 && (
            <div className="border rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-500 mb-1">{getIndexName(rec2)} (30%)</h3>
              <p className="text-xs text-gray-400 mb-3">{rec2}</p>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Invested:</span>
                  <span className="font-medium">{formatCurrency(amount2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Final:</span>
                  <span className="font-medium">{formatCurrency(final2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Return:</span>
                  <span className={`font-bold ${return2 >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {return2 >= 0 ? '+' : ''}{return2.toFixed(2)}%
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Instrument 3 */}
          {rec3 && (
            <div className="border rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-500 mb-1">{getIndexName(rec3)} (20%)</h3>
              <p className="text-xs text-gray-400 mb-3">{rec3}</p>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Invested:</span>
                  <span className="font-medium">{formatCurrency(amount3)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Final:</span>
                  <span className="font-medium">{formatCurrency(final3)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Return:</span>
                  <span className={`font-bold ${return3 >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {return3 >= 0 ? '+' : ''}{return3.toFixed(2)}%
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Daily Prices Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">Daily Prices</h2>
          <p className="text-sm text-gray-500">Closing prices for each day in the period</p>
        </div>
        <div className="overflow-x-auto max-h-96">
          <table className="min-w-full">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Date</th>
                {symbols.map(symbol => (
                  <th key={symbol} className="px-4 py-3 text-right text-sm font-medium text-gray-500">
                    {getIndexName(symbol)}
                    <br />
                    <span className="text-xs text-gray-400">{symbol}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y">
              {priceData.map((row) => (
                <tr key={row.date} className="hover:bg-gray-50">
                  <td className="px-4 py-2 text-sm text-gray-900">{row.date}</td>
                  {symbols.map(symbol => {
                    const price = row[symbol];
                    const isNumeric = typeof price === 'number';
                    return (
                      <td key={symbol} className="px-4 py-2 text-right text-sm text-gray-900">
                        {formatPrice(price)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {priceData.length === 0 && (
          <div className="px-6 py-8 text-center text-gray-500">
            No price data available for the selected period.
          </div>
        )}
      </div>
    </div>
  );
};

export default PeriodDetail;