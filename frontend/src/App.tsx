import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { SessionProvider } from './context/SessionContext';
import { SessionErrorBoundary } from './components/SessionErrorBoundary';
import { Header } from './components/Header';
import { MobileNav } from './components/MobileNav';
import { LandingPage } from './pages/LandingPage';
import { LiveProtectionPage } from './pages/LiveProtectionPage';
import { SessionSummaryPage } from './pages/SessionSummaryPage';
import { HistoryPage } from './pages/HistoryPage';
import { SafetyCenterPage } from './pages/SafetyCenterPage';

export const App: React.FC = () => {
  return (
    <SessionProvider>
      <Router>
        <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans pb-16 md:pb-0">
          <Header />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/safety" element={<SafetyCenterPage />} />
              <Route path="/session/:sessionId" element={
                <SessionErrorBoundary>
                  <LiveProtectionPage />
                </SessionErrorBoundary>
              } />
              <Route path="/session/:sessionId/summary" element={
                <SessionErrorBoundary>
                  <SessionSummaryPage />
                </SessionErrorBoundary>
              } />
            </Routes>
          </main>
          <MobileNav />
        </div>
      </Router>
    </SessionProvider>
  );
};

export default App;
