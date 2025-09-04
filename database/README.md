# GLTR Webtoon Database Schema

웹툰 생성 시스템을 위한 데이터베이스 스키마 및 ORM 모델입니다.

## 📁 파일 구조

```
database/
├── schema/
│   ├── mysql_schema.sql      # MySQL 데이터베이스 스키마
│   └── postgresql_schema.sql # PostgreSQL 데이터베이스 스키마
├── models.py                  # SQLAlchemy ORM 모델
├── utils.py                   # 데이터베이스 유틸리티 함수
└── README.md                  # 이 파일
```

## 🏗️ 데이터베이스 구조

### 테이블 구조

#### 1. **webtoons** (메인 웹툰 정보)
- 사용자 입력 프롬프트와 LLM 프롬프트
- 테마, 스타일, 언어 설정
- 팩트 체크 및 리뷰 상태
- 장면 수정 요청

#### 2. **scenes** (씬/장면 정보)
- 웹툰별 각 씬 정보
- 씬 요약 및 내레이터 텍스트
- 팩트 체크 상태

#### 3. **scene_characters** (씬별 캐릭터)
- 각 씬의 캐릭터 대사
- 캐릭터 이름 및 순서
- 가변적인 캐릭터 수 지원 (1명, 3명, 5명 등)

#### 4. **analyses** (분석 내용)
- 웹툰별 분석 정보
- 분석 유형 및 내용
- 순서 관리

## 🚀 설치 및 사용법

### 1. 필요한 패키지 설치

```bash
uv pip install sqlalchemy pymysql psycopg2-binary
```

### 2. 데이터베이스 생성

#### MySQL
```bash
mysql -u root -p < database/schema/mysql_schema.sql
```

#### PostgreSQL
```bash
psql -U postgres -d your_database < database/schema/postgresql_schema.sql
```

### 3. Python에서 사용

```python
from database.models import DatabaseConnection
from database.utils import WebtoonDBManager

# 데이터베이스 연결
# MySQL
db_url = "mysql+pymysql://user:password@localhost/gltr_webtoon"
# PostgreSQL
# db_url = "postgresql://user:password@localhost/gltr_webtoon"

# 연결 초기화
db_conn = DatabaseConnection(db_url)
db_conn.create_tables()  # 테이블 생성

# 매니저 초기화
manager = WebtoonDBManager(db_conn)

# 웹툰 데이터 생성
webtoon_data = {
    'user_prompt': '사용자 입력...',
    'llm_prompt': 'LLM 프롬프트...',
    'theme': '경제',
    'style': 'blog',
    'scenes': [
        {
            'scene_number': 1,
            'narrator': '내레이션...',
            'characters': [
                {
                    'character_order': 1,
                    'character_name': '김민수',
                    'dialogue': '대사...'
                }
            ]
        }
    ]
}

# 웹툰 생성
webtoon_id = manager.create_webtoon_with_scenes(webtoon_data)

# 웹툰 조회
webtoon = manager.get_webtoon_complete(webtoon_id)
```

## 📊 주요 기능

### WebtoonDBManager 클래스

- `create_webtoon_with_scenes()`: 웹툰과 모든 관련 데이터 생성
- `get_webtoon_complete()`: 웹툰 전체 정보 조회
- `update_scene_dialogue()`: 씬 대사 업데이트
- `search_webtoons()`: 조건별 웹툰 검색
- `get_statistics()`: 데이터베이스 통계 조회

## 🔍 쿼리 예제

### 팩트 체크 완료된 웹툰 조회
```python
results = manager.search_webtoons(fact_check=True)
```

### 특정 스타일의 웹툰 조회
```python
blog_webtoons = manager.search_webtoons(style='blog')
```

### 통계 조회
```python
stats = manager.get_statistics()
print(f"총 웹툰 수: {stats['total_webtoons']}")
print(f"스타일별 분포: {stats['styles']}")
```

## 📝 데이터 구조 예시

```python
{
    'user_prompt': '원본 뉴스 텍스트...',
    'llm_prompt': 'LLM에 전달된 프롬프트...',
    'prompt_summary': '요약...',
    'theme': '경제 활성화',
    'style': 'blog',
    'number_of_cuts': 8,
    'scenes': [
        {
            'scene_number': 1,
            'narrator': '내레이션 텍스트',
            'characters': [
                {
                    'character_order': 1,
                    'character_name': '김민수',
                    'dialogue': '대사 내용',
                    'fact_check': True
                },
                {
                    'character_order': 2,
                    'character_name': '박지영',
                    'dialogue': '대사 내용',
                    'fact_check': False
                }
            ]
        }
    ],
    'analyses': [
        {
            'type': 'economic_impact',
            'content': '경제 영향 분석 내용...'
        }
    ]
}
```

## 🔧 마이그레이션

데이터베이스 스키마 변경 시:

1. 백업 생성
2. 새 스키마 적용
3. 데이터 마이그레이션
4. 검증

## 📌 주의사항

- 캐릭터 수가 가변적이므로 `scene_characters` 테이블로 정규화
- 모든 삭제는 CASCADE로 설정되어 있음
- 타임스탬프는 자동으로 관리됨
- UTF-8 인코딩 사용 (한국어 지원)

## 🤝 지원

문제가 있거나 추가 기능이 필요한 경우 이슈를 등록해주세요.
