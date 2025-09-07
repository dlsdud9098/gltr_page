import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import InfiniteScroll from 'react-infinite-scroll-component';
import { Card, Spin, Empty } from 'antd';
import { HeartOutlined, EyeOutlined } from '@ant-design/icons';
import api from '../services/api';
import './MainPage.css';

const { Meta } = Card;

const MainPage = () => {
  const [webtoons, setWebtoons] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);

  const fetchWebtoons = useCallback(async () => {
    if (loading) return;
    
    setLoading(true);
    try {
      const response = await api.get('/api/webtoons/', {
        params: {
          page,
          per_page: 8,
        },
      });
      
      const newWebtoons = response.data.webtoons;
      
      if (page === 1) {
        setWebtoons(newWebtoons);
      } else {
        setWebtoons(prev => [...prev, ...newWebtoons]);
      }
      
      setHasMore(webtoons.length + newWebtoons.length < response.data.total);
      setPage(prev => prev + 1);
    } catch (error) {
      console.error('Failed to fetch webtoons:', error);
    } finally {
      setLoading(false);
    }
  }, [page, loading, webtoons.length]);

  useEffect(() => {
    fetchWebtoons();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const WebtoonCard = ({ webtoon }) => (
    <Link to={`/webtoon/${webtoon.id}`} className="webtoon-card-link">
      <Card
        hoverable
        className="webtoon-card"
        cover={
          webtoon.thumbnail_url ? (
            <img
              alt={webtoon.title}
              src={webtoon.thumbnail_url}
              className="webtoon-thumbnail"
            />
          ) : (
            <div className="webtoon-thumbnail-placeholder">
              <span>썸네일</span>
            </div>
          )
        }
      >
        <Meta
          title={webtoon.title}
          description={
            <div className="webtoon-meta">
              <div className="webtoon-author">
                작가: {webtoon.author_name || '익명'}
              </div>
              <div className="webtoon-stats">
                <span>
                  <EyeOutlined /> {webtoon.view_count}
                </span>
                <span>
                  <HeartOutlined /> {webtoon.like_count}
                </span>
              </div>
            </div>
          }
        />
      </Card>
    </Link>
  );

  return (
    <div className="main-page">
      <div className="container">
        <h1 className="page-title">웹툰 목록</h1>
        
        {webtoons.length === 0 && !loading ? (
          <Empty description="아직 등록된 웹툰이 없습니다." />
        ) : (
          <InfiniteScroll
            dataLength={webtoons.length}
            next={fetchWebtoons}
            hasMore={hasMore}
            loader={
              <div className="loading-spinner">
                <Spin size="large" />
              </div>
            }
            endMessage={
              <p style={{ textAlign: 'center', padding: '20px' }}>
                <b>모든 웹툰을 불러왔습니다.</b>
              </p>
            }
          >
            <div className="webtoon-grid">
              {webtoons.map((webtoon) => (
                <WebtoonCard key={webtoon.id} webtoon={webtoon} />
              ))}
            </div>
          </InfiniteScroll>
        )}
      </div>
    </div>
  );
};

export default MainPage;