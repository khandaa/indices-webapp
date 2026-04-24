import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface IndexInfo {
  id: number;
  name: string;
  symbol: string;
  index_type: string;
}

interface SelectedIndex {
  index_id: number;
  name: string;
  symbol: string;
  is_selected: boolean;
}

const IndexSelection: React.FC = () => {
  const [allIndices, setAllIndices] = useState<IndexInfo[]>([]);
  const [selectedIndices, setSelectedIndices] = useState<SelectedIndex[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const indices = await apiService.getIndices();
      setAllIndices(indices.map((i: any) => ({
        id: i.id,
        name: i.name,
        symbol: i.symbol,
        index_type: i.index_type || 'sector'
      })));
      
      const selected = await apiService.getSelectedIndices();
      setSelectedIndices(selected.selected_indices || []);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const isIndexSelected = (indexId: number): boolean => {
    return selectedIndices.some(s => s.index_id === indexId && s.is_selected);
  };

  const toggleSelection = (indexId: number) => {
    setSelectedIndices(prev => {
      const exists = prev.find(s => s.index_id === indexId);
      if (exists) {
        return prev.map(s => 
          s.index_id === indexId 
            ? { ...s, is_selected: !s.is_selected }
            : s
        );
      } else {
        const index = allIndices.find(i => i.id === indexId);
        if (index) {
          return [...prev, { index_id: indexId, name: index.name, symbol: index.symbol, is_selected: true }];
        }
        return prev;
      }
    });
    setSaved(false);
  };

  const selectAll = async () => {
    setSaving(true);
    try {
      const indexIds = allIndices.map(i => i.id);
      for (const indexId of indexIds) {
        await apiService.addSelectedIndex(indexId, true);
      }
      setSelectedIndices(allIndices.map(i => ({ index_id: i.id, name: i.name, symbol: i.symbol, is_selected: true })));
      setSaved(true);
    } catch (error) {
      console.error('Error selecting all:', error);
    } finally {
      setSaving(false);
    }
  };

  const deselectAll = async () => {
    setSaving(true);
    try {
      for (const selected of selectedIndices) {
        await apiService.removeSelectedIndex(selected.index_id);
      }
      setSelectedIndices([]);
      setSaved(true);
    } catch (error) {
      console.error('Error deselecting all:', error);
    } finally {
      setSaving(false);
    }
  };

  const filteredIndices = allIndices.filter(i => 
    i.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    i.symbol.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const grouped = filteredIndices.reduce((acc, index) => {
    const type = index.index_type || 'other';
    if (!acc[type]) acc[type] = [];
    acc[type].push(index);
    return acc;
  }, {} as Record<string, IndexInfo[]>);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Index Selection</h1>
        <div className="flex gap-2">
          <button
            onClick={selectAll}
            disabled={saving || allIndices.length === 0}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            Select All
          </button>
          <button
            onClick={deselectAll}
            disabled={saving || selectedIndices.length === 0}
            className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50"
          >
            Deselect All
          </button>
        </div>
      </div>

      <div className="mb-6">
        <input
          type="text"
          placeholder="Search indices..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full max-w-md px-4 py-2 border rounded-lg"
        />
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(grouped).map(([type, indices]) => (
            <div key={type} className="bg-white rounded-lg shadow">
              <div className="px-6 py-3 bg-gray-50 border-b">
                <h2 className="text-lg font-semibold text-gray-900 capitalize">
                  {type.replace('_', ' ')}
                </h2>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {indices.map(index => (
                    <label
                      key={index.id}
                      className={`flex items-center p-3 rounded-lg border cursor-pointer ${
                        isIndexSelected(index.id)
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={isIndexSelected(index.id)}
                        onChange={() => toggleSelection(index.id)}
                        className="h-4 w-4 text-blue-600 rounded"
                      />
                      <div className="ml-3">
                        <span className="block text-sm font-medium text-gray-900">{index.name}</span>
                        <span className="block text-xs text-gray-500">{index.symbol}</span>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {saved && (
        <div className="fixed bottom-4 right-4 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg">
          Selection saved!
        </div>
      )}
    </div>
  );
};

export default IndexSelection;