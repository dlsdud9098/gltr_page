import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Webtoon } from '../types/webtoon';
import { webtoonApi } from '../api/webtoonApi';
import '../styles/WebtoonDetail.css';

const WebtoonDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [webtoon, setWebtoon] = useState<Webtoon | null>(null);
  const [loading, setLoading] = useState(true);
  const [drawingText, setDrawingText] = useState('');
  const [llmQuestion, setLlmQuestion] = useState('');
  const [editResponse, setEditResponse] = useState<any>(null);

  useEffect(() => {
    const fetchWebtoon = async () => {
      if (!id) return;
      
      try {
        const data = await webtoonApi.getWebtoonById(parseInt(id));
        setWebtoon(data);
      } catch (error) {
        console.error('Failed to fetch webtoon:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchWebtoon();
  }, [id]);

  const handleEdit = async () => {
    if (!id) return;
    
    try {
      const response = await webtoonApi.editWebtoon(parseInt(id), {
        drawing: drawingText || undefined,
        llm_question: llmQuestion || undefined
      });
      setEditResponse(response);
      setTimeout(() => setEditResponse(null), 3000);
    } catch (error) {
      console.error('Failed to edit webtoon:', error);
    }
  };

  if (loading) {
    return <div className="loading">로딩 중...</div>;
  }

  if (!webtoon) {
    return <div className="error">웹툰을 찾을 수 없습니다.</div>;
  }

  return (
    <div className="detail-container">
      <button onClick={() => navigate('/')} className="back-button">
        ← 목록으로
      </button>
      
      <div className="detail-content">
        <div className="webtoon-viewer">
          <h1 className="detail-title">{webtoon.title}</h1>
          <div className="images-container">
            {webtoon.images && webtoon.images.length > 0 ? (
              webtoon.images.map((image, index) => (
                <img
                  key={index}
                  src={`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}${image}`}
                  alt={`${webtoon.title} - ${index + 1}컷`}
                  className="webtoon-image"
                />
              ))
            ) : Array.isArray(webtoon.episodes) && webtoon.episodes.length > 0 ? (
              webtoon.episodes[0].images.map((image, index) => (
                <img
                  key={index}
                  src={`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}${image}`}
                  alt={`${webtoon.title} - ${index + 1}컷`}
                  className="webtoon-image"
                />
              ))
            ) : (
              <p>이미지가 없습니다.</p>
            )}
          </div>
        </div>
        
        <div className="edit-panel">
          <div className="info-section">
            <h2>웹툰 정보</h2>
            <p className="detail-description">{webtoon.description}</p>
            <p className="detail-author">작가: {webtoon.author}</p>
            <p className="detail-episodes">
              에피소드: {Array.isArray(webtoon.episodes) 
                ? `${webtoon.episodes.length}화` 
                : webtoon.total_episodes 
                  ? `${webtoon.total_episodes}화`
                  : typeof webtoon.episodes === 'number'
                    ? `${webtoon.episodes}화`
                    : '0화'}
            </p>
          </div>
          
          <div className="edit-section">
            <h2>웹툰 편집</h2>
            
            <div className="edit-group">
              <label htmlFor="drawing">그림 추가/편집</label>
              <textarea
                id="drawing"
                value={drawingText}
                onChange={(e) => setDrawingText(e.target.value)}
                placeholder="그림을 추가하거나 편집할 내용을 입력하세요..."
                rows={4}
              />
            </div>
            
            <div className="edit-group">
              <label htmlFor="llm">AI 질문</label>
              <textarea
                id="llm"
                value={llmQuestion}
                onChange={(e) => setLlmQuestion(e.target.value)}
                placeholder="웹툰 이미지에 대해 AI에게 질문하세요..."
                rows={4}
              />
            </div>
            
            <button onClick={handleEdit} className="edit-button">
              편집 요청 보내기
            </button>
            
            {editResponse && (
              <div className="edit-response">
                <p>{editResponse.message}</p>
                {editResponse.drawing_status && <p>{editResponse.drawing_status}</p>}
                {editResponse.llm_response && <p>{editResponse.llm_response}</p>}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebtoonDetail;