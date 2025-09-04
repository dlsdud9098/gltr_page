import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Webtoon } from '../types/webtoon';
import { webtoonApi } from '../api/webtoonApi';
import '../styles/Gallery.css';

const Gallery: React.FC = () => {
  const [webtoons, setWebtoons] = useState<Webtoon[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [initialLoading, setInitialLoading] = useState(true);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadingRef = useRef<HTMLDivElement | null>(null);

  const fetchWebtoons = useCallback(async (pageNum: number) => {
    if (loading) return;
    
    setLoading(true);
    try {
      const data = await webtoonApi.getAllWebtoons(pageNum, 5);
      
      if (pageNum === 1) {
        setWebtoons(data.items);
      } else {
        setWebtoons(prev => [...prev, ...data.items]);
      }
      
      setHasMore(data.has_more);
      setPage(pageNum);
    } catch (error) {
      console.error('Failed to fetch webtoons:', error);
    } finally {
      setLoading(false);
      if (pageNum === 1) {
        setInitialLoading(false);
      }
    }
  }, [loading]);

  useEffect(() => {
    fetchWebtoons(1);
  }, []);

  useEffect(() => {
    if (!hasMore || loading) return;

    const options = {
      root: null,
      rootMargin: '100px',
      threshold: 0.1
    };

    observerRef.current = new IntersectionObserver((entries) => {
      const [target] = entries;
      if (target.isIntersecting && hasMore && !loading) {
        fetchWebtoons(page + 1);
      }
    }, options);

    if (loadingRef.current) {
      observerRef.current.observe(loadingRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [page, hasMore, loading, fetchWebtoons]);

  if (initialLoading) {
    return <div className="loading">로딩 중...</div>;
  }

  return (
    <div className="gallery-container">
      <h1 className="gallery-title">웹툰 갤러리</h1>
      <div className="gallery-grid">
        {webtoons.map((webtoon) => (
          <Link
            to={`/webtoon/${webtoon.id}`}
            key={webtoon.id}
            className="webtoon-card"
          >
            <div className="thumbnail-wrapper">
              <img
                src={`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}${webtoon.thumbnail}`}
                alt={webtoon.title}
                className="thumbnail"
                loading="lazy"
              />
            </div>
            <div className="webtoon-info">
              <h3 className="webtoon-title">{webtoon.title}</h3>
              <p className="webtoon-author">작가: {webtoon.author}</p>
              <p className="webtoon-episodes">
                {Array.isArray(webtoon.episodes) 
                  ? `${webtoon.episodes.length}화` 
                  : webtoon.total_episodes 
                    ? `${webtoon.total_episodes}화`
                    : typeof webtoon.episodes === 'number'
                      ? `${webtoon.episodes}화`
                      : '0화'}
              </p>
            </div>
          </Link>
        ))}
      </div>
      
      {hasMore && (
        <div ref={loadingRef} className="loading-more">
          {loading && <span>더 불러오는 중...</span>}
        </div>
      )}
      
      {!hasMore && webtoons.length > 0 && (
        <div className="end-message">
          모든 웹툰을 불러왔습니다
        </div>
      )}
    </div>
  );
};

export default Gallery;