import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Tabs, List, Avatar, Button, Empty, Tag, Statistic, Row, Col, Form, Input, Modal } from 'antd';
import {
  UserOutlined,
  EditOutlined,
  BookOutlined,
  HeartOutlined,
  EyeOutlined,
  PlusOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import toast from 'react-hot-toast';
import './ProfilePage.css';

const { TabPane } = Tabs;

const ProfilePage = () => {
  const navigate = useNavigate();
  const { user, checkAuth } = useAuth();
  const [myWebtoons, setMyWebtoons] = useState([]);
  const [likedWebtoons, setLikedWebtoons] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editModal, setEditModal] = useState(false);
  const [form] = Form.useForm();
  const [stats, setStats] = useState({
    totalWebtoons: 0,
    totalViews: 0,
    totalLikes: 0,
  });

  useEffect(() => {
    fetchUserData();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchUserData = async () => {
    setLoading(true);
    try {
      // Fetch user's webtoons
      const webtoonsRes = await api.get('/api/webtoons/my');
      setMyWebtoons(webtoonsRes.data);

      // Calculate stats
      const totalViews = webtoonsRes.data.reduce((sum, w) => sum + w.view_count, 0);
      const totalLikes = webtoonsRes.data.reduce((sum, w) => sum + w.like_count, 0);
      setStats({
        totalWebtoons: webtoonsRes.data.length,
        totalViews,
        totalLikes,
      });

      // Fetch liked webtoons
      const interactionsRes = await api.get('/api/interactions/my', {
        params: { interaction_type: 'like' },
      });
      
      // Get details of liked webtoons
      const likedIds = interactionsRes.data.map(i => i.webtoon_id);
      const likedDetails = await Promise.all(
        likedIds.map(id => api.get(`/api/webtoons/${id}`))
      );
      setLikedWebtoons(likedDetails.map(res => res.data));
    } catch (error) {
      console.error('Failed to fetch user data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (values) => {
    try {
      await api.put(`/api/users/${user.id}`, values);
      toast.success('프로필이 업데이트되었습니다.');
      setEditModal(false);
      checkAuth(); // Refresh user data
    } catch (error) {
      console.error('Failed to update profile:', error);
      toast.error('프로필 업데이트에 실패했습니다.');
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
          fetchUserData();
        } catch (error) {
          console.error('Failed to delete webtoon:', error);
          toast.error('웹툰 삭제에 실패했습니다.');
        }
      },
    });
  };

  const WebtoonCard = ({ webtoon, showActions = false }) => (
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
      actions={
        showActions
          ? [
              <EditOutlined key="edit" onClick={(e) => {
                e.stopPropagation();
                navigate(`/webtoon/${webtoon.id}/edit`);
              }} />,
              <DeleteOutlined key="delete" onClick={(e) => {
                e.stopPropagation();
                handleDeleteWebtoon(webtoon.id);
              }} />,
            ]
          : []
      }
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

  return (
    <div className="profile-page">
      <div className="profile-header">
        <Card>
          <div className="profile-info">
            <Avatar size={100} icon={<UserOutlined />} />
            <div className="profile-details">
              <h1>{user?.username}</h1>
              <p>{user?.email}</p>
              <Tag color="blue">{user?.role === 'creator' ? '크리에이터' : '일반 사용자'}</Tag>
              <Button
                icon={<EditOutlined />}
                onClick={() => {
                  form.setFieldsValue({
                    username: user.username,
                    email: user.email,
                  });
                  setEditModal(true);
                }}
              >
                프로필 수정
              </Button>
            </div>
          </div>
          
          <Row gutter={16} className="profile-stats">
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
        </Card>
      </div>

      <Card className="profile-content">
        <Tabs defaultActiveKey="1">
          <TabPane tab="내 웹툰" key="1">
            {myWebtoons.length > 0 ? (
              <div className="webtoons-grid">
                {myWebtoons.map((webtoon) => (
                  <WebtoonCard key={webtoon.id} webtoon={webtoon} showActions />
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
                <Button type="primary" onClick={() => navigate('/create')}>
                  첫 웹툰 만들기
                </Button>
              </Empty>
            )}
          </TabPane>
          
          <TabPane tab="좋아요한 웹툰" key="2">
            {likedWebtoons.length > 0 ? (
              <div className="webtoons-grid">
                {likedWebtoons.map((webtoon) => (
                  <WebtoonCard key={webtoon.id} webtoon={webtoon} />
                ))}
              </div>
            ) : (
              <Empty
                description="아직 좋아요한 웹툰이 없습니다"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            )}
          </TabPane>
          
          <TabPane tab="통계" key="3">
            <div className="statistics-section">
              <h3>웹툰별 통계</h3>
              <List
                loading={loading}
                dataSource={myWebtoons}
                renderItem={(webtoon) => (
                  <List.Item>
                    <List.Item.Meta
                      title={webtoon.title}
                      description={`장르: ${webtoon.genre || '미정'}`}
                    />
                    <div className="webtoon-stats">
                      <Statistic title="조회수" value={webtoon.view_count} />
                      <Statistic title="좋아요" value={webtoon.like_count} />
                    </div>
                  </List.Item>
                )}
              />
            </div>
          </TabPane>
        </Tabs>
      </Card>

      {/* Edit Profile Modal */}
      <Modal
        title="프로필 수정"
        open={editModal}
        onCancel={() => setEditModal(false)}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleUpdateProfile}
        >
          <Form.Item
            name="username"
            label="사용자명"
            rules={[{ required: true, message: '사용자명을 입력해주세요!' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="email"
            label="이메일"
            rules={[
              { required: true, message: '이메일을 입력해주세요!' },
              { type: 'email', message: '올바른 이메일 형식이 아닙니다!' },
            ]}
          >
            <Input />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              저장
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ProfilePage;