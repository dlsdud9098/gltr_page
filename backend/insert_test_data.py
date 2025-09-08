"""
테스트 웹툰 데이터 삽입 스크립트
"""
from database import get_db_session
from models import Webtoon, Scene, Dialogue
import uuid
from datetime import datetime

def insert_test_data():
    with get_db_session() as db:
        # 테스트 웹툰 생성
        webtoon1 = Webtoon(
            id=uuid.uuid4(),
            title="우리가 사랑한 계절",
            summary="청춘의 사랑과 이별을 그린 감성 웹툰",
            description="대학 시절 만난 두 사람의 아름답고도 아픈 사랑 이야기",
            thumbnail_url="/images/sample_thumbnail_1.jpg",
            author_name="김작가",
            genre="로맨스",
            theme="청춘, 사랑",
            story_style="감성적",
            number_of_cuts=10,
            status="published",
            view_count=1250,
            like_count=89,
            session_id="test_session_1",
            created_at=datetime.utcnow()
        )
        
        webtoon2 = Webtoon(
            id=uuid.uuid4(),
            title="마법사의 여행",
            summary="신비로운 마법 세계를 여행하는 모험 이야기",
            description="젊은 마법사가 세계를 구하기 위해 떠나는 대모험",
            thumbnail_url="/images/sample_thumbnail_2.jpg",
            author_name="박작가",
            genre="판타지",
            theme="모험, 성장",
            story_style="서사적",
            number_of_cuts=15,
            status="published",
            view_count=2340,
            like_count=156,
            session_id="test_session_2",
            created_at=datetime.utcnow()
        )
        
        webtoon3 = Webtoon(
            id=uuid.uuid4(),
            title="도시의 미스터리",
            summary="대도시에서 일어나는 미스터리한 사건들",
            description="탐정이 되어 도시의 숨겨진 비밀을 파헤치는 스릴러",
            thumbnail_url="/images/sample_thumbnail_3.jpg",
            author_name="이작가",
            genre="미스터리",
            theme="추리, 스릴러",
            story_style="긴장감 있는",
            number_of_cuts=12,
            status="published",
            view_count=1890,
            like_count=234,
            session_id="test_session_3",
            created_at=datetime.utcnow()
        )
        
        # 웹툰 추가
        db.add(webtoon1)
        db.add(webtoon2)
        db.add(webtoon3)
        
        # 각 웹툰에 샘플 씬 추가
        for webtoon in [webtoon1, webtoon2, webtoon3]:
            for i in range(3):
                scene = Scene(
                    id=uuid.uuid4(),
                    webtoon_id=webtoon.id,
                    scene_number=i+1,
                    title=f"씬 {i+1}",
                    description=f"{webtoon.title}의 {i+1}번째 장면",
                    scene_description=f"이 장면은 {webtoon.title}의 중요한 부분입니다.",
                    image_url=f"/images/scene_{i+1}.jpg",
                    narration=f"장면 {i+1}의 나레이션",
                    created_at=datetime.utcnow()
                )
                db.add(scene)
                
                # 각 씬에 대화 추가
                for j in range(2):
                    dialogue = Dialogue(
                        id=uuid.uuid4(),
                        scene_id=scene.id,
                        who_speaks=f"캐릭터{j+1}",
                        dialogue=f"이것은 샘플 대화 {j+1}입니다.",
                        fact_or_fiction="fiction",
                        dialogue_order=j+1,
                        created_at=datetime.utcnow()
                    )
                    db.add(dialogue)
        
        db.commit()
        print("✅ 테스트 데이터가 성공적으로 삽입되었습니다!")
        print(f"- 웹툰 3개")
        print(f"- 각 웹툰당 씬 3개")
        print(f"- 각 씬당 대화 2개")

if __name__ == "__main__":
    insert_test_data()