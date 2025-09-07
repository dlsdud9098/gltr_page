import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Row, Col, Card, Button, Input, Form, Modal, Upload, Tabs, Select, Spin } from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  SaveOutlined,
  PictureOutlined
} from '@ant-design/icons';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import api from '../services/api';
import toast from 'react-hot-toast';
import './EditorPage.css';

const { TextArea } = Input;
const { TabPane } = Tabs;
const { Option } = Select;

const EditorPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [webtoon, setWebtoon] = useState(null);
  const [episodes, setEpisodes] = useState({});
  const [selectedEpisode, setSelectedEpisode] = useState(1);
  const [loading, setLoading] = useState(true);
  const [editModal, setEditModal] = useState(false);
  const [editingScene, setEditingScene] = useState(null);
  const [aiModal, setAiModal] = useState(false);
  const [aiCommand, setAiCommand] = useState('');

  useEffect(() => {
    fetchWebtoonData();
  }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchWebtoonData = async () => {
    try {
      const [webtoonRes, episodesRes] = await Promise.all([
        api.get(`/api/webtoons/${id}`),
        api.get(`/api/episodes/webtoon/${id}`),
      ]);
      
      // Check if user owns this webtoon
      if (!webtoonRes.data.is_owner) {
        toast.error('이 웹툰을 편집할 권한이 없습니다.');
        navigate(`/webtoon/${id}`);
        return;
      }
      
      setWebtoon(webtoonRes.data);
      
      // Group episodes by episode_number
      const groupedEpisodes = episodesRes.data.reduce((acc, episode) => {
        if (!acc[episode.episode_number]) {
          acc[episode.episode_number] = [];
        }
        acc[episode.episode_number].push(episode);
        return acc;
      }, {});
      
      // Sort scenes within each episode
      Object.keys(groupedEpisodes).forEach(epNum => {
        groupedEpisodes[epNum].sort((a, b) => a.scene_order - b.scene_order);
      });
      
      setEpisodes(groupedEpisodes);
    } catch (error) {
      console.error('Failed to fetch webtoon data:', error);
      toast.error('웹툰 정보를 불러오는데 실패했습니다.');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const handleDragEnd = (result) => {
    if (!result.destination) return;

    const items = Array.from(episodes[selectedEpisode]);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    // Update scene_order
    const updatedItems = items.map((item, index) => ({
      ...item,
      scene_order: index + 1,
    }));

    setEpisodes({
      ...episodes,
      [selectedEpisode]: updatedItems,
    });

    // Save order to backend
    updateSceneOrder(updatedItems);
  };

  const updateSceneOrder = async (scenes) => {
    try {
      for (const scene of scenes) {
        await api.put(`/api/episodes/${scene.id}`, {
          scene_order: scene.scene_order,
        });
      }
      toast.success('순서가 변경되었습니다.');
    } catch (error) {
      console.error('Failed to update scene order:', error);
      toast.error('순서 변경에 실패했습니다.');
    }
  };

  const handleEditScene = (scene) => {
    setEditingScene(scene);
    form.setFieldsValue({
      dialogue: scene.dialogue,
      description: scene.description,
      narration: scene.narration,
      panel_layout: scene.panel_layout,
    });
    setEditModal(true);
  };

  const handleSaveScene = async (values) => {
    try {
      await api.put(`/api/episodes/${editingScene.id}`, values);
      toast.success('씬이 수정되었습니다.');
      setEditModal(false);
      fetchWebtoonData();
    } catch (error) {
      console.error('Failed to update scene:', error);
      toast.error('씬 수정에 실패했습니다.');
    }
  };

  const handleDeleteScene = async (sceneId) => {
    Modal.confirm({
      title: '씬 삭제',
      content: '정말로 이 씬을 삭제하시겠습니까?',
      okText: '삭제',
      cancelText: '취소',
      onOk: async () => {
        try {
          await api.delete(`/api/episodes/${sceneId}`);
          toast.success('씬이 삭제되었습니다.');
          fetchWebtoonData();
        } catch (error) {
          console.error('Failed to delete scene:', error);
          toast.error('씬 삭제에 실패했습니다.');
        }
      },
    });
  };

  const handleAddScene = () => {
    const newScene = {
      episode_number: selectedEpisode,
      scene_order: (episodes[selectedEpisode]?.length || 0) + 1,
      dialogue: '',
      description: '',
      narration: '',
    };
    
    setEditingScene(null);
    form.resetFields();
    form.setFieldsValue(newScene);
    setEditModal(true);
  };

  const handleCreateScene = async (values) => {
    try {
      await api.post('/api/episodes/', {
        webtoon_id: parseInt(id),
        episode_number: selectedEpisode,
        scene_order: (episodes[selectedEpisode]?.length || 0) + 1,
        ...values,
      });
      toast.success('새 씬이 추가되었습니다.');
      setEditModal(false);
      fetchWebtoonData();
    } catch (error) {
      console.error('Failed to create scene:', error);
      toast.error('씬 추가에 실패했습니다.');
    }
  };

  const handleImageUpload = async (file, sceneId) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      await api.post(`/api/episodes/${sceneId}/image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      toast.success('이미지가 업로드되었습니다.');
      fetchWebtoonData();
      return false; // Prevent default upload
    } catch (error) {
      console.error('Failed to upload image:', error);
      toast.error('이미지 업로드에 실패했습니다.');
      return false;
    }
  };

  const handleAIModify = async () => {
    if (!aiCommand.trim()) {
      toast.error('수정 명령어를 입력해주세요.');
      return;
    }

    try {
      // This would call the AI service to modify the scene
      toast.info('AI 수정 기능은 준비 중입니다.');
      setAiModal(false);
    } catch (error) {
      console.error('Failed to modify with AI:', error);
      toast.error('AI 수정에 실패했습니다.');
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <Spin size="large" />
      </div>
    );
  }

  if (!webtoon) {
    return null;
  }

  return (
    <div className="editor-page">
      <div className="editor-header">
        <h1>{webtoon.title} 편집</h1>
        <Button type="primary" icon={<SaveOutlined />} onClick={() => navigate(`/webtoon/${id}`)}>
          저장하고 나가기
        </Button>
      </div>

      <Row gutter={[24, 24]}>
        {/* Left Panel - Scene List */}
        <Col xs={24} lg={16}>
          <Card title="에피소드 씬 관리">
            <Tabs activeKey={String(selectedEpisode)} onChange={(key) => setSelectedEpisode(parseInt(key))}>
              {[1, 2, 3, 4].map(epNum => (
                <TabPane tab={`에피소드 ${epNum}`} key={epNum}>
                  <DragDropContext onDragEnd={handleDragEnd}>
                    <Droppable droppableId="scenes">
                      {(provided) => (
                        <div {...provided.droppableProps} ref={provided.innerRef}>
                          {episodes[epNum]?.map((scene, index) => (
                            <Draggable key={scene.id} draggableId={String(scene.id)} index={index}>
                              {(provided, snapshot) => (
                                <div
                                  ref={provided.innerRef}
                                  {...provided.draggableProps}
                                  {...provided.dragHandleProps}
                                  className={`scene-item ${snapshot.isDragging ? 'dragging' : ''}`}
                                >
                                  <div className="scene-content">
                                    <div className="scene-header">
                                      <span className="scene-number">씬 {scene.scene_order}</span>
                                      <div className="scene-actions">
                                        <Upload
                                          showUploadList={false}
                                          beforeUpload={(file) => handleImageUpload(file, scene.id)}
                                        >
                                          <Button icon={<PictureOutlined />} size="small">이미지</Button>
                                        </Upload>
                                        <Button
                                          icon={<EditOutlined />}
                                          size="small"
                                          onClick={() => handleEditScene(scene)}
                                        >
                                          수정
                                        </Button>
                                        <Button
                                          icon={<DeleteOutlined />}
                                          size="small"
                                          danger
                                          onClick={() => handleDeleteScene(scene.id)}
                                        >
                                          삭제
                                        </Button>
                                      </div>
                                    </div>
                                    {scene.image_url && (
                                      <img src={scene.image_url} alt={`Scene ${scene.scene_order}`} className="scene-thumbnail" />
                                    )}
                                    <div className="scene-text">
                                      {scene.dialogue && <p><strong>대사:</strong> {scene.dialogue}</p>}
                                      {scene.description && <p><strong>설명:</strong> {scene.description}</p>}
                                      {scene.narration && <p><strong>나레이션:</strong> {scene.narration}</p>}
                                    </div>
                                  </div>
                                </div>
                              )}
                            </Draggable>
                          )) || <div className="no-scenes">아직 씬이 없습니다.</div>}
                          {provided.placeholder}
                        </div>
                      )}
                    </Droppable>
                  </DragDropContext>
                  
                  <Button
                    type="dashed"
                    icon={<PlusOutlined />}
                    block
                    className="add-scene-button"
                    onClick={handleAddScene}
                  >
                    새 씬 추가
                  </Button>
                </TabPane>
              ))}
            </Tabs>
          </Card>
        </Col>

        {/* Right Panel - Tools */}
        <Col xs={24} lg={8}>
          <Card title="편집 도구" className="tools-panel">
            <div className="tool-section">
              <h3>이미지 생성</h3>
              <Button icon={<PictureOutlined />} block>
                AI 이미지 생성
              </Button>
            </div>

            <div className="tool-section">
              <h3>텍스트 수정</h3>
              <Button icon={<EditOutlined />} block onClick={() => setAiModal(true)}>
                AI로 텍스트 수정
              </Button>
            </div>

            <div className="tool-section">
              <h3>캐릭터 관리</h3>
              <Button icon={<PlusOutlined />} block>
                캐릭터 추가
              </Button>
            </div>

            <div className="tool-section">
              <h3>스타일 설정</h3>
              <Select defaultValue="default" style={{ width: '100%' }}>
                <Option value="default">기본 스타일</Option>
                <Option value="manga">만화 스타일</Option>
                <Option value="webtoon">웹툰 스타일</Option>
                <Option value="comic">코믹 스타일</Option>
              </Select>
            </div>
          </Card>

          <Card title="웹툰 정보" style={{ marginTop: 16 }}>
            <p><strong>제목:</strong> {webtoon.title}</p>
            <p><strong>작가:</strong> {webtoon.author_name || '익명'}</p>
            <p><strong>장르:</strong> {webtoon.genre || '미정'}</p>
            <p><strong>테마:</strong> {webtoon.theme || '미정'}</p>
            <p><strong>상태:</strong> {webtoon.status}</p>
          </Card>
        </Col>
      </Row>

      {/* Edit Scene Modal */}
      <Modal
        title={editingScene ? '씬 수정' : '새 씬 추가'}
        open={editModal}
        onCancel={() => setEditModal(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={editingScene ? handleSaveScene : handleCreateScene}
        >
          <Form.Item name="dialogue" label="대사">
            <TextArea rows={3} placeholder="캐릭터의 대사를 입력하세요..." />
          </Form.Item>
          <Form.Item name="description" label="장면 설명">
            <TextArea rows={3} placeholder="장면에 대한 설명을 입력하세요..." />
          </Form.Item>
          <Form.Item name="narration" label="나레이션">
            <TextArea rows={3} placeholder="나레이션을 입력하세요..." />
          </Form.Item>
          <Form.Item name="panel_layout" label="패널 레이아웃">
            <Select placeholder="레이아웃 선택">
              <Option value="single">단일 패널</Option>
              <Option value="vertical">세로 분할</Option>
              <Option value="horizontal">가로 분할</Option>
              <Option value="grid">그리드</Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              {editingScene ? '수정' : '추가'}
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* AI Modify Modal */}
      <Modal
        title="AI로 텍스트 수정"
        open={aiModal}
        onCancel={() => setAiModal(false)}
        onOk={handleAIModify}
        okText="수정"
        cancelText="취소"
      >
        <TextArea
          rows={4}
          value={aiCommand}
          onChange={(e) => setAiCommand(e.target.value)}
          placeholder="수정하고 싶은 내용을 자연어로 입력하세요. 예: '대사를 더 감정적으로 만들어줘', '설명을 더 자세하게 해줘'"
        />
      </Modal>
    </div>
  );
};

export default EditorPage;