import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Empty, Button, Tag, Statistic, Row, Col, Modal, Spin } from 'antd';
import {
  EditOutlined,
  BookOutlined,
  HeartOutlined,
  EyeOutlined,
  PlusOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import api from '../services/api';
import toast from 'react-hot-toast';
import './MyWebtoonsPage.css';

const MyWebtoonsPage = () => {
  const navigate = useNavigate();
  const [myWebtoons, setMyWebtoons] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({
    totalWebtoons: 0,
    totalViews: 0,
    totalLikes: 0,
  });

  useEffect(() => {
    fetchMyWebtoons();
  }, []);

  const fetchMyWebtoons = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/webtoons/my');
      setMyWebtoons(response.data);

      // Calculate stats
      const totalViews = response.data.reduce((sum, w) => sum + w.view_count, 0);
      const totalLikes = response.data.reduce((sum, w) => sum + w.like_count, 0);
      setStats({
        totalWebtoons: response.data.length,
        totalViews,
        totalLikes,
      });
    } catch (error) {
      console.error('Failed to fetch my webtoons:', error);
      toast.error('웹툰을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteWebtoon = (webtoonId) => {
    Modal.confirm({
      title: '웹툰 삭제',
      content: '정말로 이 웹툰을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.',
      okText: '삭제',
      okType: 'danger',
      cancelText: '취소',
      onOk: async () => {
        try {
          await api.delete(`/api/webtoons/${webtoonId}`);
          toast.success('웹툰이 삭제되었습니다.');
          fetchMyWebtoons();
        } catch (error) {
          console.error('Failed to delete webtoon:', error);
          toast.error('웹툰 삭제에 실패했습니다.');
        }
      },
    });
  };

  const WebtoonCard = ({ webtoon }) => (
    <Card
      hoverable
      className="webtoon-card"
      onClick={() => navigate(`/webtoon/${webtoon.id}`)}
      cover={
        webtoon.thumbnail_url ? (
          <img alt={webtoon.title} src={webtoon.thumbnail_url} />
        ) : (
          <div className="thumbnail-placeholder">
            <BookOutlined />
          </div>
        )
      }
      actions={[
        <EditOutlined key="edit" onClick={(e) => {
          e.stopPropagation();
          navigate(`/webtoon/${webtoon.id}/edit`);
        }} />,
        <DeleteOutlined key="delete" onClick={(e) => {
          e.stopPropagation();
          handleDeleteWebtoon(webtoon.id);
        }} />,
      ]}
    >
      <Card.Meta
        title={webtoon.title}
        description={
          <div className="webtoon-meta">
            <Tag color={webtoon.status === 'published' ? 'green' : 'orange'}>
              {webtoon.status === 'published' ? '공개' : '비공개'}
            </Tag>
            <div className="stats">
              <span><EyeOutlined /> {webtoon.view_count}</span>
              <span><HeartOutlined /> {webtoon.like_count}</span>
            </div>
          </div>
        }
      />
    </Card>
  );

  if (loading) {
    return (
      <div className="loading-container">
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="my-webtoons-page">
      <div className="page-header">
        <h1>내 웹툰</h1>
        <Row gutter={16} className="stats-row">
          <Col span={8}>
            <Statistic title="내 웹툰" value={stats.totalWebtoons} prefix={<BookOutlined />} />
          </Col>
          <Col span={8}>
            <Statistic title="총 조회수" value={stats.totalViews} prefix={<EyeOutlined />} />
          </Col>
          <Col span={8}>
            <Statistic title="총 좋아요" value={stats.totalLikes} prefix={<HeartOutlined />} />
          </Col>
        </Row>
      </div>

      <div className="webtoons-section">
        {myWebtoons.length > 0 ? (
          <div className="webtoons-grid">
            {myWebtoons.map((webtoon) => (
              <WebtoonCard key={webtoon.id} webtoon={webtoon} />
            ))}
            <Card
              hoverable
              className="add-webtoon-card"
              onClick={() => navigate('/create')}
            >
              <div className="add-content">
                <PlusOutlined style={{ fontSize: 48 }} />
                <p>새 웹툰 만들기</p>
              </div>
            </Card>
          </div>
        ) : (
          <Empty
            description="아직 생성한 웹툰이 없습니다"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            <Button type="primary" size="large" onClick={() => navigate('/create')}>
              첫 웹툰 만들기
            </Button>
          </Empty>
        )}
      </div>
    </div>
  );
};

export default MyWebtoonsPage;