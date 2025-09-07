import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Input, Button, Card, Typography } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import './RegisterPage.css';

const { Title, Text } = Typography;

const RegisterPage = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    setLoading(true);
    const success = await register(values.username, values.email, values.password);
    setLoading(false);
    
    if (success) {
      navigate('/login');
    }
  };

  return (
    <div className="register-page">
      <Card className="register-card">
        <div className="register-header">
          <Title level={2}>회원가입</Title>
          <Text type="secondary">새로운 계정을 만들어보세요!</Text>
        </div>

        <Form
          name="register"
          className="register-form"
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
              {
                min: 3,
                message: '사용자명은 최소 3자 이상이어야 합니다!',
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
            name="email"
            rules={[
              {
                required: true,
                message: '이메일을 입력해주세요!',
              },
              {
                type: 'email',
                message: '올바른 이메일 형식이 아닙니다!',
              },
            ]}
          >
            <Input
              prefix={<MailOutlined className="site-form-item-icon" />}
              placeholder="이메일"
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
              {
                min: 6,
                message: '비밀번호는 최소 6자 이상이어야 합니다!',
              },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined className="site-form-item-icon" />}
              placeholder="비밀번호"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            dependencies={['password']}
            rules={[
              {
                required: true,
                message: '비밀번호 확인을 입력해주세요!',
              },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('비밀번호가 일치하지 않습니다!'));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined className="site-form-item-icon" />}
              placeholder="비밀번호 확인"
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              className="register-form-button"
              loading={loading}
              size="large"
              block
            >
              회원가입
            </Button>
          </Form.Item>

          <div className="register-footer">
            <Text>이미 계정이 있으신가요? </Text>
            <Link to="/login">로그인</Link>
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default RegisterPage;