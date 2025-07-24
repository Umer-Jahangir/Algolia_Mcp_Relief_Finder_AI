import React, { useState } from 'react';
import { Navigation } from './components/Navigation.jsx';
import { HomeScreen } from './components/HomeScreen.jsx';
import { DisasterDashboard } from './components/DisasterDashboard.jsx';
import { ReliefFinder } from './components/ReliefFinder.jsx';
import { RoutePlanner } from './components/RoutePlanner.jsx';
import { SafetyInfo } from './components/SafetyInfo.jsx';
import { AIChat } from './components/AIChat.jsx';

export default function App() {
  const [currentPage, setCurrentPage] = useState('home');

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'home':
        return <HomeScreen onNavigate={setCurrentPage} />;
      case 'dashboard':
        return <DisasterDashboard />;
      case 'relief':
        return <ReliefFinder />;
      case 'route':
        return <RoutePlanner />;
      case 'safety':
        return <SafetyInfo />;
      case 'chat':
        return <AIChat />;
      default:
        return <HomeScreen onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-lg">
        {renderCurrentPage()}
        <Navigation currentPage={currentPage} onNavigate={setCurrentPage} />
      </div>
    </div>
  );
}