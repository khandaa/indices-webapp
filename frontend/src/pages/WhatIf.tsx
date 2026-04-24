import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { apiService } from '../services/api';

interface SimulationResult {
  period_number: number;
  period_start_date: string;
  period_end_date: string;
  recommendation_1_symbol: string;
  recommendation_2_symbol: string;
  recommendation_3_symbol: string;
  strategy_value_start: number;
  strategy_value_end: number;
  niftybees_value_start: number;
  niftybees_value_end: number;
}

interface SimulationSummary {
  initial_amount: number;
  final_strategy_value: number;
  final_niftybees_value: number;
  strategy_return_percent: number;
  niftybees_return_percent: number;
  outperformance: number;
}

interface SavedScenario {
  id: number;
  name: string;
  initial_amount: number;
  frequency: string;
  start_date: string;
  end_date: string;
  allocation_1: number;
  allocation_2: number;
  allocation_3: number;
}

const WhatIf: React.FC = () => {
  const [initialAmount, setInitialAmount] = useState(100000);
  const [frequency, setFrequency] = useState('weekly');
  const [startDate, setStartDate] = useState('2026-01-01');
  const [endDate, setEndDate] = useState('2026-04-01');
  const [allocation1, setAllocation1] = useState(50);
  const [allocation2, setAllocation2] = useState(30);
  const [allocation3, setAllocation3] = useState(20);
  const [scenarioName, setScenarioName] = useState('');
  
  const [results, setResults] = useState<SimulationResult[]>([]);
  const [summary, setSummary] = useState<SimulationSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [savedScenarios, setSavedScenarios] = useState<SavedScenario[]>([]);
  const [showScenarioModal, setShowScenarioModal] = useState(false);

  useEffect(() => {
    loadSavedScenarios();
  }, []);

  const loadSavedScenarios = async () => {
    try {
      const data = await apiService.getScenarios();
      setSavedScenarios(data.scenarios || []);
    } catch (error) {
      console.error('Error loading scenarios:', error);
    }
  };

  const runSimulation = async () => {
    if (allocation1 + allocation2 + allocation3 !== 100) {
      alert('Allocation percentages must sum to 100%');
      return;
    }

    setLoading(true);
    try {
      const data = await apiService.runSimulation({
        initial_amount: initialAmount,
        start_date: startDate,
        end_date: endDate,
        frequency,
        allocation_1: allocation1,
        allocation_2: allocation2,
        allocation_3: allocation3,
        save_scenario: !!scenarioName,
        scenario_name: scenarioName || undefined,
      });
      
      setResults(data.simulation.results);
      setSummary(data.simulation.summary);
      
      if (scenarioName) {
        await loadSavedScenarios();
        setScenarioName('');
      }
    } catch (error) {
      console.error('Error running simulation:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadScenario = async (scenarioId: number) => {
    try {
      const data = await apiService.getScenario(scenarioId);
      const scenario = data.scenario;
      
      setInitialAmount(scenario.initial_amount);
      setFrequency(scenario.frequency);
      setStartDate(scenario.start_date);
      setEndDate(scenario.end_date || '');
      setAllocation1(scenario.allocation_1);
      setAllocation2(scenario.allocation_2);
      setAllocation3(scenario.allocation_3);
      setScenarioName(scenario.name);
      
      if (data.results && data.results.length > 0) {
        setResults(data.results);
        calculateSummary(data.results, scenario.initial_amount);
      }
      
      setShowScenarioModal(false);
    } catch (error) {
      console.error('Error loading scenario:', error);
    }
  };

  const calculateSummary = (res: SimulationResult[], initial: number) => {
    const last = res[res.length - 1];
    setSummary({
      initial_amount: initial,
      final_strategy_value: last.strategy_value_end,
      final_niftybees_value: last.niftybees_value_end,
      strategy_return_percent: ((last.strategy_value_end - initial) / initial * 100),
      niftybees_return_percent: ((last.niftybees_value_end - initial) / initial * 100),
      outperformance: ((last.strategy_value_end - last.niftybees_value_end) / initial * 100),
    });
  };

  const deleteScenario = async (scenarioId: number) => {
    try {
      await apiService.deleteScenario(scenarioId);
      await loadSavedScenarios();
    } catch (error) {
      console.error('Error deleting scenario:', error);
    }
  };

  const exportCSV = async (scenarioId: number) => {
    try {
      const blob = await apiService.exportScenario(scenarioId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `whatif_simulation_${Date.now()}.csv`;
      a.click();
    } catch (error) {
      console.error('Error exporting:', error);
    }
  };

  const getChartData = () => {
    return results.map(r => ({
      date: r.period_end_date,
      strategy: r.strategy_value_end,
      niftybees: r.niftybees_value_end,
    }));
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(value);
  };

  const totalAllocation = allocation1 + allocation2 + allocation3;
  const isValidAllocation = totalAllocation === 100;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">What-If Investment Simulator</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Scenario Configuration</h2>
            
            {/* Initial Amount */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Initial Investment (₹)
              </label>
              <input
                type="number"
                value={initialAmount}
                onChange={(e) => setInitialAmount(Number(e.target.value))}
                className="w-full border rounded px-3 py-2"
                min={1000}
              />
            </div>
            
            {/* Frequency */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Strategy Frequency
              </label>
              <div className="flex gap-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    checked={frequency === 'weekly'}
                    onChange={() => setFrequency('weekly')}
                    className="mr-2"
                  />
                  Weekly
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    checked={frequency === 'monthly'}
                    onChange={() => setFrequency('monthly')}
                    className="mr-2"
                  />
                  Monthly
                </label>
              </div>
            </div>
            
            {/* Date Range */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full border rounded px-3 py-2"
              />
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date (optional)
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full border rounded px-3 py-2"
              />
            </div>
            
            {/* Allocations */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Allocation (must sum to 100%)
              </label>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm w-32">Top Recommendation:</span>
                  <input
                    type="number"
                    value={allocation1}
                    onChange={(e) => setAllocation1(Number(e.target.value))}
                    className="w-20 border rounded px-2 py-1"
                    min={0}
                    max={100}
                  />
                  <span>%</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm w-32">Second Recommendation:</span>
                  <input
                    type="number"
                    value={allocation2}
                    onChange={(e) => setAllocation2(Number(e.target.value))}
                    className="w-20 border rounded px-2 py-1"
                    min={0}
                    max={100}
                  />
                  <span>%</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm w-32">Third Recommendation:</span>
                  <input
                    type="number"
                    value={allocation3}
                    onChange={(e) => setAllocation3(Number(e.target.value))}
                    className="w-20 border rounded px-2 py-1"
                    min={0}
                    max={100}
                  />
                  <span>%</span>
                </div>
              </div>
              {!isValidAllocation && (
                <p className="text-red-500 text-sm mt-1">
                  Total: {totalAllocation}% (must be 100%)
                </p>
              )}
            </div>
            
            {/* Scenario Name */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Scenario Name (optional)
              </label>
              <input
                type="text"
                value={scenarioName}
                onChange={(e) => setScenarioName(e.target.value)}
                placeholder="e.g., Jan 2026 Portfolio"
                className="w-full border rounded px-3 py-2"
              />
            </div>
            
            {/* Buttons */}
            <div className="flex gap-2">
              <button
                onClick={runSimulation}
                disabled={loading || !isValidAllocation}
                className={`flex-1 px-4 py-2 rounded font-medium ${
                  loading || !isValidAllocation
                    ? 'bg-gray-400 text-white cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {loading ? 'Running...' : 'Run Simulation'}
              </button>
              <button
                onClick={() => setShowScenarioModal(true)}
                className="px-4 py-2 border rounded hover:bg-gray-50"
              >
                Load
              </button>
            </div>
          </div>
        </div>
        
        {/* Results Panel */}
        <div className="lg:col-span-2">
          {summary ? (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white rounded-lg shadow p-4">
                  <p className="text-sm text-gray-500">Initial Investment</p>
                  <p className="text-xl font-bold">{formatCurrency(summary.initial_amount)}</p>
                </div>
                <div className={`bg-white rounded-lg shadow p-4 ${summary.strategy_return_percent >= 0 ? 'border-l-4 border-green-500' : 'border-l-4 border-red-500'}`}>
                  <p className="text-sm text-gray-500">Strategy Value</p>
                  <p className="text-xl font-bold">{formatCurrency(summary.final_strategy_value)}</p>
                  <p className={`text-sm ${summary.strategy_return_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {summary.strategy_return_percent >= 0 ? '+' : ''}{summary.strategy_return_percent.toFixed(2)}%
                  </p>
                </div>
                <div className="bg-white rounded-lg shadow p-4">
                  <p className="text-sm text-gray-500">Niftybees Value</p>
                  <p className="text-xl font-bold">{formatCurrency(summary.final_niftybees_value)}</p>
                  <p className={`text-sm ${summary.niftybees_return_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {summary.niftybees_return_percent >= 0 ? '+' : ''}{summary.niftybees_return_percent.toFixed(2)}%
                  </p>
                </div>
                <div className={`bg-white rounded-lg shadow p-4 ${summary.outperformance >= 0 ? 'border-l-4 border-green-500' : 'border-l-4 border-red-500'}`}>
                  <p className="text-sm text-gray-500">Outperformance</p>
                  <p className="text-xl font-bold">
                    {summary.outperformance >= 0 ? '+' : ''}{summary.outperformance.toFixed(2)}%
                  </p>
                  <p className="text-sm text-gray-500">vs Niftybees</p>
                </div>
              </div>
              
              {/* Chart */}
              <div className="bg-white rounded-lg shadow p-4">
                <h3 className="text-lg font-semibold mb-4">Portfolio Value Over Time</h3>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={getChartData()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                      <Legend />
                      <Line type="monotone" dataKey="strategy" stroke="#3b82f6" strokeWidth={2} name="Strategy" />
                      <Line type="monotone" dataKey="niftybees" stroke="#f59e0b" strokeWidth={2} name="Niftybees" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
              
              {/* Detailed Table */}
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="px-4 py-3 border-b flex justify-between items-center">
                  <h3 className="text-lg font-semibold">Detailed Results</h3>
                  {savedScenarios.length > 0 && (
                    <button
                      onClick={() => exportCSV(savedScenarios[0]?.id)}
                      className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                    >
                      Export CSV
                    </button>
                  )}
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left">Period</th>
                        <th className="px-4 py-2 text-left">Dates</th>
                        <th className="px-4 py-2 text-left">Recommendations</th>
                        <th className="px-4 py-2 text-right">Strategy</th>
                        <th className="px-4 py-2 text-right">Niftybees</th>
                        <th className="px-4 py-2 text-right">Return</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {results.map((r) => {
                        const strategyReturn = ((r.strategy_value_end - r.strategy_value_start) / r.strategy_value_start * 100);
                        return (
                          <tr key={r.period_number} className="hover:bg-gray-50">
                            <td className="px-4 py-2">{r.period_number}</td>
                            <td className="px-4 py-2">
                              {r.period_start_date} to {r.period_end_date}
                            </td>
                            <td className="px-4 py-2">
                              <span className="text-blue-600">{r.recommendation_1_symbol || '-'}</span>,{' '}
                              <span className="text-green-600">{r.recommendation_2_symbol || '-'}</span>,{' '}
                              <span className="text-orange-600">{r.recommendation_3_symbol || '-'}</span>
                            </td>
                            <td className="px-4 py-2 text-right">
                              {formatCurrency(r.strategy_value_end)}
                            </td>
                            <td className="px-4 py-2 text-right">
                              {formatCurrency(r.niftybees_value_end)}
                            </td>
                            <td className={`px-4 py-2 text-right ${strategyReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {strategyReturn >= 0 ? '+' : ''}{strategyReturn.toFixed(2)}%
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500">
              <p className="text-lg">Configure your scenario and run the simulation to see results.</p>
              <p className="mt-2 text-sm">The simulation will compare a weekly/monthly recommendation strategy against buying and holding Niftybees.</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Load Scenario Modal */}
      {showScenarioModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Saved Scenarios</h3>
              <button onClick={() => setShowScenarioModal(false)} className="text-gray-500 hover:text-gray-700">
                X
              </button>
            </div>
            {savedScenarios.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No saved scenarios yet.</p>
            ) : (
              <div className="space-y-2 max-h-80 overflow-y-auto">
                {savedScenarios.map((s) => (
                  <div key={s.id} className="flex items-center justify-between p-3 border rounded hover:bg-gray-50">
                    <div>
                      <p className="font-medium">{s.name}</p>
                      <p className="text-sm text-gray-500">
                        {formatCurrency(s.initial_amount)} | {s.frequency} | {s.allocation_1}/{s.allocation_2}/{s.allocation_3}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => loadScenario(s.id)}
                        className="px-3 py-1 bg-blue-600 text-white rounded text-sm"
                      >
                        Load
                      </button>
                      <button
                        onClick={() => deleteScenario(s.id)}
                        className="px-3 py-1 bg-red-600 text-white rounded text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default WhatIf;