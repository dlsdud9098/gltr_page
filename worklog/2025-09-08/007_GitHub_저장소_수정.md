# 007_GitHub_저장소_수정

**날짜**: 2025-09-08  
**시간**: GitHub 이슈 해결  
**프로젝트**: gltr_page

## 문제점
사용자가 https://github.com/gltr-company/worklog.git에 commit & push가 안됐다고 문의

## 원인 분석
1. **원격 저장소 불일치**: 
   - 기존: https://github.com/dlsdud9098/gltr_page.git
   - 요구: https://github.com/gltr-company/worklog.git

2. **일지 저장 위치 문제**: 
   - 일지가 git 프로젝트 범위 밖에 저장됨
   - 경로: /home/apic/Documents/gltr_days/일지/

## 해결 작업
1. ✅ 원격 저장소 URL 변경
2. ✅ 프로젝트 내부에 worklog/ 디렉토리 생성
3. ✅ 일지 파일을 프로젝트 내부로 복사
4. ✅ git add, commit, push 성공

## 결과
- GitHub 저장소 https://github.com/gltr-company/worklog.git에 성공적으로 push 완료
- 앞으로 일지는 프로젝트 내부 worklog/ 디렉토리에 저장 예정
