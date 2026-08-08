import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ChanakyaApp from './ChanakyaApp';
import RedditApp from './reddit/RedditApp';
import { Hub } from './Hub';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Hub />} />
        <Route path="/chanakya/*" element={<ChanakyaApp />} />
        <Route path="/reddit/*" element={<RedditApp />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

export default App;
