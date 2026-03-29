import axios from 'axios';
import { Index, ApiResponse, PerformanceResponse } from '../types';

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
};

export default api;
