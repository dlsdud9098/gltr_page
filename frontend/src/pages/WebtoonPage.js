import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Row, Col, Card, Button, Spin, Empty, Tabs, Input, Form, 
  Badge, Avatar, List, Divider, Carousel, message,
  Drawer, Space, Tooltip
} from 'antd';
import { 
  HeartOutlined, HeartFilled, 
  ShareAltOutlined, MessageOutlined, 
  SendOutlined, FileImageOutlined,
  SmileOutlined,
  LeftOutlined, RightOutlined
} from '@ant-design/icons';
import api from '../services/api';
import toast from 'react-hot-toast';
import './WebtoonPage.css';

const { TextArea } = Input;

const WebtoonPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [webtoon, setWebtoon] = useState(null);
  const [scenes, setScenes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSceneGroup, setSelectedSceneGroup] = useState(null);
  const [interactionTab, setInteractionTab] = useState('chat');
  const [chatMessages, setChatMessages] = useState([]);
  const [unreadMessages, setUnreadMessages] = useState(3); // 임시 데이터
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [mobileDrawer, setMobileDrawer] = useState(false);
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);
  const carouselRef = useRef(null);
  const chatEndRef = useRef(null);

  // Canvas for drawing
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    fetchWebtoonData();
    fetchRecommendations();
    initializeChatMessages();
    fetchComments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchWebtoonData = async () => {
    try {
      const [webtoonRes, scenesRes] = await Promise.all([
        api.get(`/api/webtoons/${id}`),
        api.get(`/api/scenes/webtoon/${id}`),
      ]);
      
      setWebtoon(webtoonRes.data);
      
      // Scenes를 10개씩 그룹으로 나누기 (에피소드처럼 표시)
      const groupedScenes = {};
      scenesRes.data.forEach(scene => {
        const groupNum = Math.floor((scene.scene_number - 1) / 10) + 1;
        if (!groupedScenes[groupNum]) {
          groupedScenes[groupNum] = [];
        }
        groupedScenes[groupNum].push(scene);
      });
      
      Object.keys(groupedScenes).forEach(groupNum => {
        groupedScenes[groupNum].sort((a, b) => a.scene_number - b.scene_number);
      });
      
      setScenes(groupedScenes);
      
      const firstGroupNum = Object.keys(groupedScenes)[0];
      if (firstGroupNum) {
        setSelectedSceneGroup(parseInt(firstGroupNum));
      }
    } catch (error) {
      console.error('Failed to fetch webtoon data:', error);
      toast.error('웹툰 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    try {
      const response = await api.get('/api/webtoons?page=1&per_page=6');
      setRecommendations(response.data.webtoons.filter(w => w.id !== parseInt(id)));
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    }
  };

  const fetchComments = async () => {
    try {
      const response = await api.get(`/api/interactions/comments/webtoon/${id}`);
      setComments(response.data);
    } catch (error) {
      console.error('Failed to fetch comments:', error);
    }
  };

  const handleSubmitComment = async () => {
    if (!commentText.trim()) return;
    
    setSubmittingComment(true);
    try {
      await api.post('/api/interactions/comments', {
        webtoon_id: parseInt(id),
        content: commentText,
        author_name: '독자'
      });
      
      setCommentText('');
      toast.success('댓글이 작성되었습니다!');
      fetchComments(); // 댓글 목록 새로고침
    } catch (error) {
      console.error('Failed to submit comment:', error);
      toast.error('댓글 작성에 실패했습니다.');
    } finally {
      setSubmittingComment(false);
    }
  };

  const initializeChatMessages = async () => {
    try {
      // 기존 채팅 메시지 불러오기
      const response = await api.get(`/api/chat/messages/webtoon/${id}`);
      if (response.data && response.data.length > 0) {
        const messages = response.data.map(msg => ({
          id: msg.id,
          sender: msg.sender_type,
          avatar: msg.sender_type === 'character' ? '🦸' : null,
          name: msg.sender_name,
          message: msg.message,
          timestamp: msg.created_at,
          read: msg.is_read
        }));
        setChatMessages(messages);
      } else {
        // 메시지가 없으면 초기 인사 메시지 생성
        const initMessage = {
          webtoon_id: parseInt(id),
          sender_type: 'character',
          sender_name: '주인공',
          message: '안녕하세요! 저는 이 웹툰의 주인공입니다. 궁금한 점이 있으면 물어보세요!'
        };
        await api.post('/api/chat/messages', initMessage);
        initializeChatMessages(); // 다시 불러오기
      }
      
      // 읽지 않은 메시지 수 가져오기
      const unreadResponse = await api.get(`/api/chat/unread-count/webtoon/${id}`);
      setUnreadMessages(unreadResponse.data.unread_count);
    } catch (error) {
      console.error('Failed to load chat messages:', error);
      // 오류 시 기본 메시지 표시
      setChatMessages([
        {
          id: 1,
          sender: 'character',
          avatar: '🦸',
          name: '주인공',
          message: '안녕하세요! 저는 이 웹툰의 주인공입니다. 궁금한 점이 있으면 물어보세요!',
          timestamp: new Date().toISOString(),
          read: false
        }
      ]);
    }
  };

  const handleShare = () => {
    const shareUrl = window.location.href;
    navigator.clipboard.writeText(shareUrl);
    message.success('링크가 복사되었습니다!');
  };

  const handleLike = async () => {
    try {
      const response = await api.post(`/api/interactions/like?webtoon_id=${id}`);
      
      if (response.data.liked) {
        setWebtoon(prev => ({ 
          ...prev, 
          like_count: prev.like_count + 1,
          is_liked: true 
        }));
        toast.success('좋아요!');
      } else {
        setWebtoon(prev => ({ 
          ...prev, 
          like_count: Math.max(0, prev.like_count - 1),
          is_liked: false 
        }));
      }
    } catch (error) {
      console.error('Failed to toggle like:', error);
      toast.error('좋아요 처리에 실패했습니다.');
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    try {
      // 사용자 메시지 추가
      const userMessage = {
        id: Date.now(),
        sender: 'user',
        message: inputMessage,
        timestamp: new Date().toISOString(),
        read: true
      };

      setChatMessages(prev => [...prev, userMessage]);
      setInputMessage('');
      setIsTyping(true);

      // API로 메시지 전송
      await api.post('/api/chat/messages', {
        webtoon_id: parseInt(id),
        sender_type: 'user',
        sender_name: '독자',
        message: inputMessage
      });

      // AI 응답 기다리기
      setTimeout(async () => {
        // 채팅 메시지 다시 불러오기 (AI 응답 포함)
        const messagesResponse = await api.get(`/api/chat/messages/webtoon/${id}`);
        const messages = messagesResponse.data.map(msg => ({
          id: msg.id,
          sender: msg.sender_type,
          avatar: msg.sender_type === 'character' ? '🦸' : null,
          name: msg.sender_name,
          message: msg.message,
          timestamp: msg.created_at,
          read: msg.is_read
        }));
        setChatMessages(messages);
        setIsTyping(false);
        
        // 메시지 읽음 처리
        const unreadIds = messages
          .filter(msg => msg.sender === 'character' && !msg.read)
          .map(msg => msg.id);
        
        if (unreadIds.length > 0) {
          await api.post('/api/chat/messages/batch-read', unreadIds);
          setUnreadMessages(0);
        }
      }, 1500);
    } catch (error) {
      console.error('Failed to send message:', error);
      toast.error('메시지 전송에 실패했습니다.');
      setIsTyping(false);
    }
  };

  // Drawing functions
  const startDrawing = (e) => {
    if (interactionTab !== 'draw') return;
    setIsDrawing(true);
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const ctx = canvas.getContext('2d');
    ctx.beginPath();
    ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
  };

  const draw = (e) => {
    if (!isDrawing || interactionTab !== 'draw') return;
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const ctx = canvas.getContext('2d');
    ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
    ctx.stroke();
  };

  const stopDrawing = () => {
    setIsDrawing(false);
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <Spin size="large" />
      </div>
    );
  }

  if (!webtoon) {
    return <Empty description="웹툰을 찾을 수 없습니다." />;
  }

  // Mobile View (YouTube Style)
  if (isMobile) {
    return (
      <div className="webtoon-page-mobile">
        {/* Mobile Header */}
        <div className="mobile-header">
          <Button icon={<LeftOutlined />} onClick={() => navigate(-1)} />
          <h2>{webtoon.title}</h2>
          <Button icon={<ShareAltOutlined />} onClick={handleShare} />
        </div>

        {/* Horizontal Carousel for Scenes */}
        <div className="mobile-carousel-container">
          <Carousel ref={carouselRef} dots={false}>
            {selectedSceneGroup && scenes[selectedSceneGroup]?.map((scene) => (
              <div key={scene.id} className="mobile-scene-slide">
                {scene.image_url ? (
                  <img src={scene.image_url} alt={`Scene ${scene.scene_order}`} />
                ) : (
                  <div className="scene-placeholder-mobile">
                    <FileImageOutlined style={{ fontSize: 48 }} />
                    <p>씬 {scene.scene_number}</p>
                  </div>
                )}
              </div>
            ))}
          </Carousel>
          <div className="carousel-controls">
            <Button 
              icon={<LeftOutlined />} 
              onClick={() => carouselRef.current?.prev()}
              shape="circle"
            />
            <Button 
              icon={<RightOutlined />} 
              onClick={() => carouselRef.current?.next()}
              shape="circle"
            />
          </div>
        </div>

        {/* Mobile Interaction Area */}
        <div className="mobile-interaction">
          <div className="mobile-actions">
            <Button 
              icon={webtoon.is_liked ? <HeartFilled /> : <HeartOutlined />}
              onClick={handleLike}
              type={webtoon.is_liked ? 'primary' : 'default'}
            >
              {webtoon.like_count}
            </Button>
            <Badge count={unreadMessages} size="small">
              <Button 
                icon={<MessageOutlined />}
                onClick={() => setMobileDrawer(true)}
              >
                채팅
              </Button>
            </Badge>
            <Button icon={<SmileOutlined />}>낙서</Button>
          </div>

          {/* Mobile Chat Input */}
          <div className="mobile-chat-input">
            <Input
              placeholder="캐릭터에게 질문해보세요..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onPressEnter={handleSendMessage}
              suffix={
                <Button 
                  icon={<SendOutlined />} 
                  type="text"
                  onClick={handleSendMessage}
                />
              }
            />
          </div>
        </div>

        {/* Mobile Recommendations */}
        <div className="mobile-recommendations">
          <h3>추천 웹툰</h3>
          <div className="recommendation-scroll">
            {recommendations.map(rec => (
              <Card
                key={rec.id}
                hoverable
                className="recommendation-card-mobile"
                onClick={() => navigate(`/webtoon/${rec.id}`)}
                cover={
                  rec.thumbnail ? (
                    <img alt={rec.title} src={rec.thumbnail} />
                  ) : (
                    <div className="thumbnail-placeholder-mobile">
                      <FileImageOutlined />
                    </div>
                  )
                }
              >
                <Card.Meta 
                  title={rec.title}
                  description={`${rec.genre || '장르 미정'}`}
                />
              </Card>
            ))}
          </div>
        </div>

        {/* Mobile Chat Drawer */}
        <Drawer
          title={
            <Badge count={unreadMessages} size="small">
              <span>캐릭터와 대화</span>
            </Badge>
          }
          placement="bottom"
          height="70%"
          open={mobileDrawer}
          onClose={() => setMobileDrawer(false)}
        >
          <div className="mobile-chat-container">
            <div className="chat-messages">
              {chatMessages.map(msg => (
                <div key={msg.id} className={`chat-message ${msg.sender}`}>
                  {msg.sender === 'character' && (
                    <Avatar>{msg.avatar}</Avatar>
                  )}
                  <div className="message-content">
                    <div className="message-bubble">
                      {msg.message}
                    </div>
                    {!msg.read && msg.sender === 'character' && (
                      <span className="unread-indicator">1</span>
                    )}
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
          </div>
        </Drawer>
      </div>
    );
  }

  // Desktop View (Notion Style)
  return (
    <div className="webtoon-page-desktop">
      <Row gutter={0}>
        {/* Left Panel - Webtoon Viewer */}
        <Col span={16} className="left-panel">
          <div className="webtoon-header-desktop">
            <div className="header-info">
              <h1>{webtoon.title}</h1>
              <Space>
                <span className="author">by {webtoon.author_name || '익명'}</span>
                <span className="genre">{webtoon.genre || '장르 미정'}</span>
              </Space>
            </div>
            <Space>
              <Tooltip title="공유하기">
                <Button 
                  icon={<ShareAltOutlined />} 
                  onClick={handleShare}
                  shape="circle"
                />
              </Tooltip>
              <Button
                icon={webtoon.is_liked ? <HeartFilled /> : <HeartOutlined />}
                onClick={handleLike}
                type={webtoon.is_liked ? 'primary' : 'default'}
              >
                {webtoon.like_count}
              </Button>
            </Space>
          </div>

          {/* Scenes Tabs */}
          <Tabs 
            activeKey={String(selectedSceneGroup)} 
            onChange={(key) => setSelectedSceneGroup(parseInt(key))}
            className="episode-tabs"
          >
            {Object.keys(scenes).map(groupNum => (
              <Tabs.TabPane tab={`Part ${groupNum}`} key={groupNum}>
                <div className="episode-viewer">
                  {scenes[groupNum].map((scene) => (
                    <div key={scene.id} className="scene-vertical">
                      {scene.image_url ? (
                        <img
                          src={scene.image_url}
                          alt={`Scene ${scene.scene_number}`}
                          className="scene-image-vertical"
                        />
                      ) : (
                        <div className="scene-placeholder-vertical">
                          <FileImageOutlined style={{ fontSize: 64 }} />
                          <p>씬 {scene.scene_number}</p>
                        </div>
                      )}
                      {(scene.dialogues?.length > 0 || scene.narration) && (
                        <div className="scene-text-overlay">
                          {scene.dialogues?.map((dialogue, idx) => (
                            <div key={idx} className="dialogue">
                              <strong>{dialogue.who_speaks}:</strong> {dialogue.dialogue}
                            </div>
                          ))}
                          {scene.narration && <div className="narration">{scene.narration}</div>}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </Tabs.TabPane>
            ))}
          </Tabs>

          {/* Recommendations at Bottom */}
          <div className="desktop-recommendations">
            <Divider />
            <h2>다른 웹툰 추천</h2>
            <Row gutter={[16, 16]}>
              {recommendations.slice(0, 4).map(rec => (
                <Col span={6} key={rec.id}>
                  <Card
                    hoverable
                    onClick={() => navigate(`/webtoon/${rec.id}`)}
                    cover={
                      rec.thumbnail ? (
                        <img alt={rec.title} src={rec.thumbnail} />
                      ) : (
                        <div className="thumbnail-placeholder">
                          <FileImageOutlined />
                        </div>
                      )
                    }
                  >
                    <Card.Meta 
                      title={rec.title}
                      description={rec.genre || '장르 미정'}
                    />
                  </Card>
                </Col>
              ))}
            </Row>
          </div>
        </Col>

        {/* Right Panel - Interaction Tools */}
        <Col span={8} className="right-panel">
          <div className="interaction-container">
            <Tabs 
              activeKey={interactionTab}
              onChange={setInteractionTab}
              className="interaction-tabs"
            >
              <Tabs.TabPane 
                tab={
                  <Badge count={unreadMessages} size="small">
                    <span>질문하기</span>
                  </Badge>
                } 
                key="chat"
              >
                <div className="chat-container">
                  <div className="chat-messages">
                    {chatMessages.map(msg => (
                      <div key={msg.id} className={`chat-message ${msg.sender}`}>
                        {msg.sender === 'character' && (
                          <Avatar className="chat-avatar">{msg.avatar}</Avatar>
                        )}
                        <div className="message-content">
                          {msg.sender === 'character' && (
                            <div className="message-name">{msg.name}</div>
                          )}
                          <div className="message-bubble">
                            {msg.message}
                          </div>
                          {!msg.read && msg.sender === 'character' && (
                            <span className="unread-indicator">1</span>
                          )}
                        </div>
                      </div>
                    ))}
                    {isTyping && (
                      <div className="chat-message character">
                        <Avatar className="chat-avatar">🦸</Avatar>
                        <div className="message-content">
                          <div className="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={chatEndRef} />
                  </div>
                  <div className="chat-input">
                    <Input.Group compact>
                      <Input
                        style={{ width: 'calc(100% - 40px)' }}
                        placeholder="캐릭터에게 질문해보세요..."
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onPressEnter={handleSendMessage}
                      />
                      <Button 
                        type="primary" 
                        icon={<SendOutlined />}
                        onClick={handleSendMessage}
                      />
                    </Input.Group>
                  </div>
                </div>
              </Tabs.TabPane>

              <Tabs.TabPane tab="댓글달기" key="comment">
                <div className="comment-section">
                  <Form onFinish={handleSubmitComment}>
                    <Form.Item>
                      <TextArea 
                        rows={4} 
                        placeholder="이 웹툰에 대한 생각을 공유해주세요..."
                        value={commentText}
                        onChange={(e) => setCommentText(e.target.value)}
                      />
                    </Form.Item>
                    <Form.Item>
                      <Button 
                        type="primary" 
                        htmlType="submit" 
                        block 
                        loading={submittingComment}
                      >
                        댓글 작성
                      </Button>
                    </Form.Item>
                  </Form>
                  <Divider />
                  <List
                    dataSource={comments}
                    renderItem={item => {
                      const timeAgo = new Date(item.created_at).toLocaleString('ko-KR');
                      return (
                        <List.Item>
                          <List.Item.Meta
                            avatar={<Avatar>{item.author_name[0]}</Avatar>}
                            title={item.author_name}
                            description={
                              <>
                                <div>{item.content}</div>
                                <small>{timeAgo}</small>
                              </>
                            }
                          />
                        </List.Item>
                      );
                    }}
                  />
                </div>
              </Tabs.TabPane>

              <Tabs.TabPane tab="낙서하기" key="draw">
                <div className="drawing-section">
                  <div className="drawing-tools">
                    <Button onClick={clearCanvas}>지우기</Button>
                    <Button type="primary">저장</Button>
                  </div>
                  <canvas
                    ref={canvasRef}
                    width={350}
                    height={400}
                    className="drawing-canvas"
                    onMouseDown={startDrawing}
                    onMouseMove={draw}
                    onMouseUp={stopDrawing}
                    onMouseLeave={stopDrawing}
                  />
                  <div className="drawing-hint">
                    마우스로 자유롭게 그려보세요!
                  </div>
                </div>
              </Tabs.TabPane>
            </Tabs>
          </div>
        </Col>
      </Row>
    </div>
  );
};

export default WebtoonPage;