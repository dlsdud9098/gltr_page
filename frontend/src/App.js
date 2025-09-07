import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import koKR from 'antd/locale/ko_KR';
import Layout from './components/Layout/Layout';
import MainPage from './pages/MainPage';
import WebtoonPage from './pages/WebtoonPage';
import EditorPage from './pages/EditorPage';
import MyWebtoonsPage from './pages/MyWebtoonsPage';
import CreatePage from './pages/CreatePage';
import './App.css';

function App() {
  return (
    <ConfigProvider locale={koKR}>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<MainPage />} />
          <Route path="/webtoon/:id" element={<WebtoonPage />} />
          <Route path="/webtoon/:id/edit" element={<EditorPage />} />
          <Route path="/create" element={<CreatePage />} />
          <Route path="/my-webtoons" element={<MyWebtoonsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </ConfigProvider>
  );
}

export default App;