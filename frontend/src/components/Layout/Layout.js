import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { Layout as AntLayout, Menu } from 'antd';
import {
  HomeOutlined,
  PlusCircleOutlined,
  BookOutlined,
} from '@ant-design/icons';
import './Layout.css';

const { Header, Content, Footer } = AntLayout;

const Layout = () => {
  const navigate = useNavigate();

  return (
    <AntLayout className="layout">
      <Header className="header">
        <div className="header-container">
          <div className="logo" onClick={() => navigate('/')}>
            GLTR Webtoon
          </div>
          
          <Menu theme="dark" mode="horizontal" className="nav-menu">
            <Menu.Item key="home" icon={<HomeOutlined />} onClick={() => navigate('/')}>
              홈
            </Menu.Item>
            <Menu.Item key="create" icon={<PlusCircleOutlined />} onClick={() => navigate('/create')}>
              새 웹툰
            </Menu.Item>
            <Menu.Item key="my-webtoons" icon={<BookOutlined />} onClick={() => navigate('/my-webtoons')}>
              내 웹툰
            </Menu.Item>
          </Menu>
        </div>
      </Header>

      <Content className="content">
        <Outlet />
      </Content>

      <Footer className="footer">
        <div className="footer-content">
          <p>GLTR Webtoon Platform ©2024</p>
          <p>AI를 활용한 창의적인 웹툰 제작 플랫폼</p>
        </div>
      </Footer>
    </AntLayout>
  );
};

export default Layout;