import React, { useState } from 'react';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Studio } from './pages/Studio';
import { Library } from './pages/Library';
import { History } from './pages/History';

const App: React.FC = () => {
  const [activePage, setActivePage] = useState('dashboard');
  const [selectedQuote, setSelectedQuote] = useState<string>("");

  const handleSelectQuote = (quote: string) => {
    setSelectedQuote(quote);
    setActivePage('studio');
  };

  const renderContent = () => {
    switch (activePage) {
      case 'dashboard':
        return <Dashboard />;
      case 'studio':
        return <Studio initialQuote={selectedQuote} />;
      case 'library':
        return <Library onSelectQuote={handleSelectQuote} />;
      case 'history':
        return <History />;
      default:
        return (
          <div className="flex items-center justify-center h-full text-slate-500">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-slate-300 mb-2">Coming Soon</h2>
              <p>The {activePage} module is under construction.</p>
            </div>
          </div>
        );
    }
  };

  return (
    <Layout activePage={activePage} setActivePage={setActivePage}>
      {renderContent()}
    </Layout>
  );
};

export default App;