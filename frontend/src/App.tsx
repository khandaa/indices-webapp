import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import IndicesPage from './pages/IndicesPage';
import WeeklyDashboard from './pages/WeeklyDashboard';
import MonthlyDashboard from './pages/MonthlyDashboard';
import InstrumentDetail from './pages/InstrumentDetail';
import Recommendations from './pages/Recommendations';
import Recommendations3 from './pages/recommendations-3';
import CombinedRecommendations from './pages/combined-recommendations';
import RecommendationsTable from './pages/recommendations-table';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="App min-h-screen bg-gray-50">
          {/* Navigation */}
          <nav className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex">
                  <div className="flex-shrink-0 flex items-center">
                    <h1 className="text-xl font-bold text-gray-900">Indices Web App</h1>
                  </div>
                  <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                    <Link
                      to="/"
                      className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                    >
                      Indices
                    </Link>
                    <Link
                      to="/weekly"
                      className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                    >
                      Weekly Dashboard
                    </Link>
                    <Link
                      to="/monthly"
                      className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                    >
                      Monthly Dashboard
                    </Link>
                    <Link
                      to="/recommendations"
                      className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                    >
                      Recommendations
                    </Link>
                    <Link
                      to="/recommendations-3"
                      className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                    >
                      Top 3 Recommendations
                    </Link>
                    <Link
                      to="/combined-recommendations"
                      className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                    >
                      Combined Recommendations
                    </Link>
                    <Link
                      to="/recommendations-table"
                      className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                    >
                      All Recommendations
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main>
            <ErrorBoundary>
              <Routes>
                <Route path="/" element={<IndicesPage />} />
                <Route path="/weekly" element={<WeeklyDashboard />} />
                <Route path="/monthly" element={<MonthlyDashboard />} />
                <Route path="/recommendations" element={<Recommendations />} />
                <Route path="/recommendations-3" element={<Recommendations3 />} />
                <Route path="/combined-recommendations" element={<CombinedRecommendations />} />
                <Route path="/recommendations-table" element={<RecommendationsTable />} />
                <Route path="/instrument/:id" element={<InstrumentDetail />} />
              </Routes>
            </ErrorBoundary>
          </main>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
