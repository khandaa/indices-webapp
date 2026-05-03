import axios from 'axios';
import { Index, ApiResponse, PerformanceResponse, DailyPriceResponse, WeeklyRecommendation, MonthlyRecommendation, RecommendationsResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5050';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Get all indices
  getIndices: async (): Promise<Index[]> => {
    try {
      const response = await api.get<ApiResponse>('/api/indices');
      return response.data.indices;
    } catch (error) {
      console.error('Error fetching indices:', error);
      throw error;
    }
  },

  // Get index details by ID
  getIndexDetails: async (id: number): Promise<Index> => {
    try {
      const response = await api.get<Index>(`/api/indices/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching index details:', error);
      throw error;
    }
  },

  // Get weekly top performers
  getWeeklyTopPerformers: async (): Promise<PerformanceResponse['top_performers']> => {
    try {
      const response = await api.get<PerformanceResponse>('/api/performance/weekly');
      return response.data.top_performers;
    } catch (error) {
      console.error('Error fetching weekly performers:', error);
      throw error;
    }
  },

  // Get monthly top performers
  getMonthlyTopPerformers: async (): Promise<PerformanceResponse['top_performers']> => {
    try {
      const response = await api.get<PerformanceResponse>('/api/performance/monthly');
      return response.data.top_performers;
    } catch (error) {
      console.error('Error fetching monthly performers:', error);
      throw error;
    }
  },

  // Health check
  healthCheck: async (): Promise<{ status: string }> => {
    try {
      const response = await api.get('/api/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },

  // Get daily prices for an index
  getDailyPrices: async (indexId: number, limit: number = 100): Promise<DailyPriceResponse['daily_prices']> => {
    try {
      const response = await api.get<DailyPriceResponse>(`/api/indices/${indexId}/daily-prices?limit=${limit}`);
      return response.data.daily_prices;
    } catch (error) {
      console.error('Error fetching daily prices:', error);
      throw error;
    }
  },

  // Get weekly recommendations
  getWeeklyRecommendations: async (): Promise<WeeklyRecommendation[]> => {
    try {
      const response = await api.get<RecommendationsResponse>('/api/recommendations/weekly');
      return response.data.recommendations as WeeklyRecommendation[];
    } catch (error) {
      console.error('Error fetching weekly recommendations:', error);
      throw error;
    }
  },

  // Get monthly recommendations
  getMonthlyRecommendations: async (): Promise<MonthlyRecommendation[]> => {
    try {
      const response = await api.get<RecommendationsResponse>('/api/recommendations/monthly');
      return response.data.recommendations as MonthlyRecommendation[];
    } catch (error) {
      console.error('Error fetching monthly recommendations:', error);
      throw error;
    }
  },

  // Get weekly recommendations with parameters
  getWeeklyRecommendationsWithParams: async (pastWeeks: number = 6, includeUpcoming: boolean = true) => {
    try {
      const response = await api.get('/api/recommendations/weekly', {
        params: { past_weeks: pastWeeks, include_upcoming: includeUpcoming }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching weekly recommendations:', error);
      throw error;
    }
  },

  // Get monthly recommendations with parameters
  getMonthlyRecommendationsWithParams: async (pastMonths: number = 4, includeUpcoming: boolean = true) => {
    try {
      const response = await api.get('/api/recommendations/monthly', {
        params: { past_months: pastMonths, include_upcoming: includeUpcoming }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching monthly recommendations:', error);
      throw error;
    }
  },

  // Get upcoming weekly recommendation
  getUpcomingWeeklyRecommendation: async () => {
    try {
      const response = await api.get('/api/recommendations/upcoming/weekly');
      return response.data;
    } catch (error) {
      console.error('Error fetching upcoming weekly:', error);
      throw error;
    }
  },

  // Get upcoming monthly recommendation
  getUpcomingMonthlyRecommendation: async () => {
    try {
      const response = await api.get('/api/recommendations/upcoming/monthly');
      return response.data;
    } catch (error) {
      console.error('Error fetching upcoming monthly:', error);
      throw error;
    }
  },

  // Check data freshness
  checkDataFreshness: async () => {
    try {
      const response = await api.get('/api/data/freshness');
      return response.data;
    } catch (error) {
      console.error('Error checking freshness:', error);
      throw error;
    }
  },

  // Get selected indices
  getSelectedIndices: async () => {
    try {
      const response = await api.get('/api/recommendations/selected');
      return response.data;
    } catch (error) {
      console.error('Error fetching selected indices:', error);
      throw error;
    }
  },

  // Add selected index
  addSelectedIndex: async (indexId: number, isSelected: boolean = true) => {
    try {
      const response = await api.post('/api/recommendations/selected', null, {
        params: { index_id: indexId, is_selected: isSelected }
      });
      return response.data;
    } catch (error) {
      console.error('Error adding selected index:', error);
      throw error;
    }
  },

  // Remove selected index
  removeSelectedIndex: async (indexId: number) => {
    try {
      const response = await api.delete(`/api/recommendations/selected/${indexId}`);
      return response.data;
    } catch (error) {
      console.error('Error removing selected index:', error);
      throw error;
    }
  },

  // Refresh data
  refreshData: async (range: string = "all") => {
    try {
      const response = await api.post('/api/recommendations/refresh', null, {
        params: { range }
      });
      return response.data;
    } catch (error) {
      console.error('Error refreshing data:', error);
      throw error;
    }
  },

  // What-If Simulation
  runSimulation: async (params: {
    initial_amount: number;
    start_date: string;
    end_date: string;
    frequency: string;
    allocation_1: number;
    allocation_2: number;
    allocation_3: number;
    save_scenario?: boolean;
    scenario_name?: string;
  }) => {
    try {
      const response = await api.get('/api/whatif/simulate', { params });
      return response.data;
    } catch (error) {
      console.error('Error running simulation:', error);
      throw error;
    }
  },

  getScenarios: async () => {
    try {
      const response = await api.get('/api/whatif/scenarios');
      return response.data;
    } catch (error) {
      console.error('Error getting scenarios:', error);
      throw error;
    }
  },

  getScenario: async (scenarioId: number) => {
    try {
      const response = await api.get(`/api/whatif/scenarios/${scenarioId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting scenario:', error);
      throw error;
    }
  },

  createScenario: async (scenario: {
    name: string;
    description?: string;
    initial_amount: number;
    frequency: string;
    allocation_1: number;
    allocation_2: number;
    allocation_3: number;
    start_date: string;
    end_date?: string;
  }) => {
    try {
      const response = await api.post('/api/whatif/scenarios', null, { params: scenario });
      return response.data;
    } catch (error) {
      console.error('Error creating scenario:', error);
      throw error;
    }
  },

  deleteScenario: async (scenarioId: number) => {
    try {
      const response = await api.delete(`/api/whatif/scenarios/${scenarioId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting scenario:', error);
      throw error;
    }
  },

  exportScenario: async (scenarioId: number) => {
    try {
      const response = await api.get(`/api/whatif/scenarios/${scenarioId}/export`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting scenario:', error);
      throw error;
    }
  },
};

export default api;
