export interface Index {
  id: number;
  name: string;
  symbol: string;
  current_price: number | null;
  daily_change: number | null;
  weekly_change: number | null;
  monthly_change: number | null;
  yearly_change: number | null;
  daily_change_percent: number | null;
  weekly_change_percent: number | null;
  monthly_change_percent: number | null;
  yearly_change_percent: number | null;
  three_week_cumulative_return: number | null;
  three_month_cumulative_return: number | null;
  calculation_date: string | null;
}

export interface TopPerformer {
  id: number;
  name: string;
  symbol: string;
  current_price: number | null;
  weekly_change?: number | null;
  weekly_change_percent?: number | null;
  monthly_change?: number | null;
  monthly_change_percent?: number | null;
  calculation_date: string | null;
}

export interface ApiResponse {
  indices: Index[];
}

export interface PerformanceResponse {
  top_performers: TopPerformer[];
}

export interface DailyPrice {
  date: string;
  open_price: number | null;
  close_price: number | null;
  high_price: number | null;
  low_price: number | null;
  volume: number | null;
  daily_change_percent: number | null;
  change_from_previous: number | null;
}

export interface DailyPriceResponse {
  daily_prices: DailyPrice[];
}

export interface WeeklyRecommendation {
  week: string;
  recommendation_date: string | null;
  instrument: string;
  symbol: string;
  one_week_return: number | null;
  three_week_cumulative_return: number | null;
}

export interface MonthlyRecommendation {
  month: string;
  recommendation_date: string | null;
  instrument: string;
  symbol: string;
  one_month_return: number | null;
  three_month_cumulative_return: number | null;
}

export interface RecommendationsResponse {
  recommendations: WeeklyRecommendation[] | MonthlyRecommendation[];
}

export interface ColumnConfig {
  name: boolean;
  symbol: boolean;
  current_price: boolean;
  daily_change: boolean;
  weekly_change: boolean;
  monthly_change: boolean;
  yearly_change: boolean;
  daily_change_percent: boolean;
  weekly_change_percent: boolean;
  monthly_change_percent: boolean;
  yearly_change_percent: boolean;
  three_week_cumulative_return: boolean;
  three_month_cumulative_return: boolean;
}
