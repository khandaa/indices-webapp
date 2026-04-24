import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
// import IndicesPage from './pages/IndicesPage';
// import WeeklyDashboard from './pages/WeeklyDashboard';
// import MonthlyDashboard from './pages/MonthlyDashboard';
import InstrumentDetail from './pages/InstrumentDetail';
// import Recommendations from './pages/Recommendations';
// import Recommendations3 from './pages/recommendations-3';
// import CombinedRecommendations from './pages/combined-recommendations';
// import RecommendationsTable from './pages/recommendations-table';
import Dashboard from './pages/Dashboard';
import IndexSelection from './pages/IndexSelection';
import Comparison from './pages/Comparison';
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
                      to="/dashboard"
                      className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                    >
                      Dashboard
                    </Link>
                    <Link
                      to="/index-selection"
                      className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                    >
                      Index Selection
                    </Link>
                    <Link
                      to="/comparison"
                      className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                    >
                      Comparison
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
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/index-selection" element={<IndexSelection />} />
                <Route path="/comparison" element={<Comparison />} />
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
