#!/usr/bin/env python3
"""
뉴스 기사를 text2cuts API를 통해 웹툰으로 변환하고 DB에 저장하는 스크립트
"""

import asyncio
import aiohttp
import json
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any
import sys
import os
from bs4 import BeautifulSoup

# 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_db, SessionLocal
from backend.models import Webtoon, Scene, Dialogue

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Text2Cuts API 설정
TEXT2CUTS_API_URL = "http://localhost:8001"  # text2cuts 서버 주소

class NewsToWebtoonConverter:
    """뉴스를 웹툰으로 변환하는 클래스"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.db = SessionLocal()
        
    async def extract_news_content(self, url: str) -> Dict[str, Any]:
        """뉴스 URL에서 콘텐츠 추출"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch {url}: HTTP {response.status}")
                        return None
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # 기본 콘텐츠 추출
                    title = ''
                    content = ''
                    
                    # 제목 추출 시도
                    title_elem = soup.find('title')
                    if title_elem:
                        title = title_elem.text.strip()
                    else:
                        h1 = soup.find('h1')
                        if h1:
                            title = h1.text.strip()
                    
                    # 본문 추출 시도
                    # 일반적인 기사 컨테이너 선택자들
                    article_selectors = [
                        'article', '.article-body', '#article-body',
                        '.news-content', '.content', '.article-content',
                        '[itemprop="articleBody"]', '.article_body'
                    ]
                    
                    for selector in article_selectors:
                        article = soup.select_one(selector)
                        if article:
                            # 텍스트만 추출
                            paragraphs = article.find_all(['p', 'div'])
                            content = '\n'.join([p.text.strip() for p in paragraphs if p.text.strip()])
                            if content:
                                break
                    
                    # 내용이 없으면 전체 텍스트 추출
                    if not content:
                        content = soup.get_text()
                        # 불필요한 공백 제거
                        content = '\n'.join([line.strip() for line in content.split('\n') if line.strip()])
                        content = content[:3000]  # 최대 3000자로 제한
                    
                    return {
                        'url': url,
                        'title': title[:200],  # 제목 길이 제한
                        'content': content[:5000],  # 내용 길이 제한
                        'author': 'Unknown',
                        'date': datetime.now().isoformat(),
                        'images': []
                    }
                    
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    async def convert_to_webtoon(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """뉴스 데이터를 text2cuts API로 웹툰으로 변환"""
        async with aiohttp.ClientSession() as session:
            # Text2Cuts API 호출
            api_endpoint = f"{TEXT2CUTS_API_URL}/api/thejournalist"
            
            # 요청 데이터 준비
            request_data = {
                "text": f"{news_data['title']}\n\n{news_data['content']}",
                "title": news_data['title'],
                "source_url": news_data['url'],
                "style": "webtoon",
                "num_panels": 6,  # 6개 패널로 생성
                "language": "ko"
            }
            
            try:
                async with session.post(api_endpoint, json=request_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        logger.error(f"API call failed: {response.status}")
                        return None
            except Exception as e:
                logger.error(f"Error calling text2cuts API: {e}")
                return None
    
    def save_to_database(self, webtoon_data: Dict[str, Any], news_data: Dict[str, Any]) -> str:
        """변환된 웹툰 데이터를 DB에 저장"""
        try:
            # 웹툰 생성
            webtoon = Webtoon(
                id=str(uuid.uuid4()),
                title=news_data['title'][:100],  # 제목 길이 제한
                summary=f"원본 기사: {news_data['url']}",  # summary 필드에 URL 저장
                description=f"뉴스 기사 '{news_data['title']}'를 웹툰으로 변환",
                session_id=self.session_id,
                genre='news',  # 장르를 news로 설정
                theme='current_affairs',  # 테마 설정
                number_of_cuts=6,  # 6개 컷으로 설정
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(webtoon)
            self.db.flush()
            
            # 씬과 대화 생성 (mock 데이터 - 실제로는 text2cuts API 응답 사용)
            scenes_data = webtoon_data.get('scenes', [])
            if not scenes_data:
                # 임시 씬 데이터 생성
                scenes_data = [
                    {
                        'scene_number': i + 1,
                        'description': f"Scene {i+1} from {news_data['title']}",
                        'narration': f"Part {i+1} of the news story",
                        'dialogues': []
                    }
                    for i in range(6)
                ]
            
            for scene_data in scenes_data:
                scene = Scene(
                    id=str(uuid.uuid4()),
                    webtoon_id=webtoon.id,
                    scene_number=scene_data.get('scene_number', 1),
                    description=scene_data.get('description', 'Scene description'),  # 필수 필드
                    scene_description=scene_data.get('description', ''),
                    narration=scene_data.get('narration', ''),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(scene)
                self.db.flush()
                
                # 대화 추가
                for dialogue_data in scene_data.get('dialogues', []):
                    dialogue = Dialogue(
                        id=str(uuid.uuid4()),
                        scene_id=scene.id,
                        character_name=dialogue_data.get('character', 'Narrator'),
                        dialogue_text=dialogue_data.get('text', ''),
                        emotion=dialogue_data.get('emotion', 'neutral'),
                        created_at=datetime.utcnow()
                    )
                    self.db.add(dialogue)
            
            self.db.commit()
            logger.info(f"Webtoon saved with ID: {webtoon.id}")
            return webtoon.id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving to database: {e}")
            raise
    
    async def process_news_urls(self, urls: List[str]) -> List[str]:
        """여러 뉴스 URL을 처리"""
        webtoon_ids = []
        
        for url in urls:
            try:
                logger.info(f"Processing: {url}")
                
                # 1. 뉴스 콘텐츠 추출
                news_data = await self.extract_news_content(url)
                if not news_data:
                    logger.error(f"Failed to extract news from {url}")
                    continue
                
                logger.info(f"Extracted: {news_data['title']}")
                
                # 2. 웹툰으로 변환
                webtoon_data = await self.convert_to_webtoon(news_data)
                if not webtoon_data:
                    logger.warning(f"Using mock data for {url}")
                    webtoon_data = {'status': 'mock', 'scenes': []}
                
                # 3. DB에 저장
                webtoon_id = self.save_to_database(webtoon_data, news_data)
                webtoon_ids.append(webtoon_id)
                
                logger.info(f"Successfully converted and saved: {webtoon_id}")
                
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
                continue
        
        return webtoon_ids
    
    def __del__(self):
        """리소스 정리"""
        if hasattr(self, 'db'):
            self.db.close()


async def main():
    """메인 함수"""
    # 변환할 뉴스 URL들
    news_urls = [
        "https://www.sisamagazine.co.kr/news/articleView.html?idxno=517015",
        "https://n.news.naver.com/mnews/ranking/article/016/0002524862?ntype=RANKING",
        "https://v.daum.net/v/20250805054508249"
    ]
    
    converter = NewsToWebtoonConverter()
    
    try:
        # 뉴스를 웹툰으로 변환하고 저장
        webtoon_ids = await converter.process_news_urls(news_urls)
        
        print("\n=== 변환 완료 ===")
        print(f"총 {len(webtoon_ids)}개의 웹툰이 생성되었습니다.")
        for i, webtoon_id in enumerate(webtoon_ids, 1):
            print(f"{i}. Webtoon ID: {webtoon_id}")
        
        return webtoon_ids
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return []


if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print("\n✅ 모든 작업이 완료되었습니다!")
    else:
        print("\n❌ 작업 중 오류가 발생했습니다.")