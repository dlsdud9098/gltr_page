import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, Select, Upload, Steps, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import api from '../services/api';
import toast from 'react-hot-toast';
import './CreatePage.css';

const { TextArea } = Input;
const { Option } = Select;
const { Step } = Steps;
const { Title, Text } = Typography;

const CreatePage = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [aiText, setAiText] = useState('');


  const handleCreateWebtoon = async (values) => {
    setLoading(true);
    try {
      const response = await api.post('/api/webtoons/', {
        title: values.title,
        description: values.description,
        author_name: values.author_name || '익명',
        genre: values.genre,
        theme: values.theme,
        story_style: values.story_style,
      });

      toast.success('웹툰이 생성되었습니다!');
      
      // If AI text exists, generate scenes
      if (aiText) {
        // This would call the text2cuts service
        toast.info('AI 장면 생성 기능은 준비 중입니다.');
      }
      
      navigate(`/webtoon/${response.data.id}/edit`);
    } catch (error) {
      console.error('Failed to create webtoon:', error);
      toast.error('웹툰 생성에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    {
      title: '기본 정보',
      content: (
        <div className="step-content">
          <Form.Item
            name="title"
            label="웹툰 제목"
            rules={[{ required: true, message: '제목을 입력해주세요!' }]}
          >
            <Input placeholder="웹툰 제목을 입력하세요" size="large" />
          </Form.Item>

          <Form.Item
            name="author_name"
            label="작가명 (선택사항)"
          >
            <Input placeholder="작가명을 입력하세요 (비워두면 '익명')" size="large" />
          </Form.Item>

          <Form.Item
            name="description"
            label="설명"
            rules={[{ required: true, message: '설명을 입력해주세요!' }]}
          >
            <TextArea rows={4} placeholder="웹툰에 대한 설명을 입력하세요" />
          </Form.Item>

          <Form.Item
            name="genre"
            label="장르"
            rules={[{ required: true, message: '장르를 선택해주세요!' }]}
          >
            <Select placeholder="장르 선택" size="large">
              <Option value="romance">로맨스</Option>
              <Option value="action">액션</Option>
              <Option value="fantasy">판타지</Option>
              <Option value="comedy">코미디</Option>
              <Option value="thriller">스릴러</Option>
              <Option value="drama">드라마</Option>
              <Option value="horror">호러</Option>
              <Option value="slice_of_life">일상</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="theme"
            label="테마"
          >
            <Input placeholder="테마를 입력하세요 (예: 학원, 무협, SF)" size="large" />
          </Form.Item>

          <Form.Item
            name="story_style"
            label="스토리 스타일"
          >
            <Select placeholder="스토리 스타일 선택" size="large">
              <Option value="linear">선형적</Option>
              <Option value="episodic">에피소드형</Option>
              <Option value="omnibus">옴니버스</Option>
              <Option value="mystery">미스터리</Option>
            </Select>
          </Form.Item>
        </div>
      ),
    },
    {
      title: 'AI 스토리 생성',
      content: (
        <div className="step-content">
          <div className="ai-section">
            <Title level={4}>AI를 활용한 스토리 생성 (선택사항)</Title>
            <Text type="secondary">
              텍스트를 입력하면 AI가 자동으로 웹툰 장면을 생성합니다.
            </Text>
            
            <div className="ai-input-section">
              <TextArea
                rows={10}
                value={aiText}
                onChange={(e) => setAiText(e.target.value)}
                placeholder="스토리를 자유롭게 입력하세요. AI가 이를 바탕으로 웹툰 장면을 생성합니다.

예시:
'한 소년이 마법학교에 입학하게 되었다. 첫날부터 이상한 일들이 벌어지기 시작했고, 소년은 자신에게 특별한 능력이 있다는 것을 깨닫게 된다...'"
              />
              
              <div className="ai-options">
                <Select defaultValue="gpt4" style={{ width: 200 }}>
                  <Option value="gpt4">GPT-4</Option>
                  <Option value="claude">Claude</Option>
                  <Option value="gltr">GLTR</Option>
                </Select>
                
                <Button type="primary" icon={<PlusOutlined />}>
                  AI 장면 생성
                </Button>
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      title: '썸네일',
      content: (
        <div className="step-content">
          <div className="thumbnail-section">
            <Title level={4}>썸네일 업로드 (선택사항)</Title>
            <Text type="secondary">
              나중에 편집 페이지에서도 업로드할 수 있습니다.
            </Text>
            
            <Upload
              name="thumbnail"
              listType="picture-card"
              className="thumbnail-uploader"
              showUploadList={false}
              beforeUpload={() => false}
            >
              <div>
                <PlusOutlined />
                <div style={{ marginTop: 8 }}>썸네일 업로드</div>
              </div>
            </Upload>
          </div>
        </div>
      ),
    },
  ];

  const next = () => {
    form.validateFields().then(() => {
      setCurrentStep(currentStep + 1);
    });
  };

  const prev = () => {
    setCurrentStep(currentStep - 1);
  };

  const handleFinish = () => {
    form.validateFields().then((values) => {
      handleCreateWebtoon(values);
    });
  };

  return (
    <div className="create-page">
      <Card className="create-card">
        <div className="create-header">
          <Title level={2}>새 웹툰 만들기</Title>
          <Text type="secondary">단계별로 웹툰을 생성해보세요</Text>
        </div>

        <Steps current={currentStep} className="steps-container">
          {steps.map((item) => (
            <Step key={item.title} title={item.title} />
          ))}
        </Steps>

        <Form
          form={form}
          layout="vertical"
          className="create-form"
        >
          <div className="steps-content">{steps[currentStep].content}</div>
        </Form>

        <div className="steps-action">
          {currentStep > 0 && (
            <Button onClick={prev}>
              이전
            </Button>
          )}
          {currentStep < steps.length - 1 && (
            <Button type="primary" onClick={next}>
              다음
            </Button>
          )}
          {currentStep === steps.length - 1 && (
            <Button type="primary" onClick={handleFinish} loading={loading}>
              웹툰 생성
            </Button>
          )}
        </div>
      </Card>
    </div>
  );
};

export default CreatePage;