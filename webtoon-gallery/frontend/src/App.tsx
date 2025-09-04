import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Gallery from './components/Gallery';
import WebtoonDetail from './components/WebtoonDetail';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Gallery />} />
          <Route path="/webtoon/:id" element={<WebtoonDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
