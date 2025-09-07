import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Input, Button, Card, Typography } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import './LoginPage.css';

const { Title, Text } = Typography;

const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    setLoading(true);
    const success = await login(values.username, values.password);
    setLoading(false);
    
    if (success) {
      navigate('/');
    }
  };

  return (
    <div className="login-page">
      <Card className="login-card">
        <div className="login-header">
          <Title level={2}>로그인</Title>
          <Text type="secondary">GLTR Webtoon Platform에 오신 것을 환영합니다!</Text>
        </div>

        <Form
          name="login"
          className="login-form"
          onFinish={onFinish}
          autoComplete="off"
          layout="vertical"
        >
          <Form.Item
            name="username"
            rules={[
              {
                required: true,
                message: '사용자명을 입력해주세요!',
              },
            ]}
          >
            <Input
              prefix={<UserOutlined className="site-form-item-icon" />}
              placeholder="사용자명"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              {
                required: true,
                message: '비밀번호를 입력해주세요!',
              },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined className="site-form-item-icon" />}
              placeholder="비밀번호"
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              className="login-form-button"
              loading={loading}
              size="large"
              block
            >
              로그인
            </Button>
          </Form.Item>

          <div className="login-footer">
            <Text>아직 계정이 없으신가요? </Text>
            <Link to="/register">회원가입</Link>
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default LoginPage;