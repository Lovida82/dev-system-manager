# Dev System Manager

개발시스템 현황 관리 포털 - Streamlit 기반 웹 애플리케이션

## 소개

엑셀 기반 개발시스템 현황 관리를 대체하는 웹 애플리케이션입니다.
실시간 시스템 현황 관리, 팀원 간 정보 공유, 시스템 라이프사이클 이력 추적이 가능합니다.

## 주요 기능

- **대시보드**: KPI 메트릭, 상태별 분포 차트, 최근 활동 알림
- **시스템 목록**: 테이블/카드/칸반 뷰, 다중 필터, 검색
- **시스템 등록**: 폼 기반 등록/수정, 유효성 검증
- **비용 관리**: 서비스별 비용 추적 및 시각화
- **통계 리포트**: 상세 분석, 부서별 통계, 비용 분석
- **Excel 관리**: Import/Export, 템플릿 다운로드
- **변경 이력**: 모든 수정사항 자동 기록

## 기술 스택

- **Frontend/Backend**: Streamlit
- **Database**: SQLite + SQLAlchemy
- **Charts**: Plotly
- **Data**: Pandas, OpenPyXL

## 설치 및 실행

### 요구사항

- Python 3.10+

### 설치

```bash
# 저장소 클론
git clone https://github.com/Lovida82/dev-system-manager.git
cd dev-system-manager

# 가상환경 생성 (선택)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 의존성 설치
pip install -r requirements.txt
```

### 실행

```bash
# 방법 1: 직접 실행
python -m streamlit run app.py

# 방법 2: bat 파일 실행 (Windows)
run.bat
```

브라우저에서 http://localhost:8501 접속

## 프로젝트 구조

```
dev_system_manager/
├── app.py                    # 메인 대시보드
├── pages/
│   ├── 1_📋_시스템_목록.py
│   ├── 2_➕_시스템_등록.py
│   ├── 3_💰_비용_관리.py
│   ├── 4_📊_통계_리포트.py
│   ├── 5_⚙️_설정.py
│   └── 6_📥_Excel_관리.py
├── database/
│   ├── models.py             # SQLAlchemy 모델
│   └── db.py                 # DB 연결 및 CRUD
├── utils/
│   ├── charts.py             # Plotly 차트
│   ├── validators.py         # 입력 검증
│   └── excel_handler.py      # Excel Import/Export
├── data/                     # SQLite DB 저장
├── .streamlit/
│   └── config.toml           # Streamlit 설정
├── requirements.txt
└── run.bat                   # Windows 실행 스크립트
```

## 스크린샷

### 대시보드
- KPI 메트릭 (전체 시스템, 운영 중, 개발 중, 평균 진행률)
- 상태별 시스템 분포 파이 차트
- 진행률 분포 히스토그램
- 부서별 시스템 수
- 서비스 비용 현황

### 시스템 목록
- 테이블 뷰: 정렬, 필터링 가능한 데이터 테이블
- 카드 뷰: 시각적인 카드 레이아웃
- 칸반 뷰: 상태별 칸반 보드

## 라이선스

MIT License
