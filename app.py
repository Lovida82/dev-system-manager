import streamlit as st
import pandas as pd
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import get_all_systems, get_dashboard_stats, get_all_services
from utils.charts import create_status_pie, create_progress_histogram, create_dept_bar

# 페이지 설정
st.set_page_config(
    page_title="개발시스템 관리",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0066CC 0%, #0052A3 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
        text-align: center;
    }
    .main-header h1 {
        color: white;
        margin: 0;
    }
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("<div class='main-header'><h1>🚀 개발시스템 현황 대시보드</h1></div>", unsafe_allow_html=True)


# 데이터 로드 (캐싱)
@st.cache_data(ttl=60)
def load_dashboard_data():
    systems = get_all_systems()
    stats = get_dashboard_stats()
    services = get_all_services()
    return systems, stats, services


systems, stats, services = load_dashboard_data()

# KPI 메트릭
st.subheader("📊 핵심 지표")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "전체 시스템",
        stats['total'],
        delta=f"+{stats['new_this_month']}건 (이번 달)" if stats['new_this_month'] > 0 else None,
        delta_color="normal"
    )

with col2:
    st.metric(
        "운영 중",
        stats['production'],
        delta=f"{stats['production_rate']:.1%}" if stats['total'] > 0 else "0%",
        delta_color="normal"
    )

with col3:
    st.metric(
        "개발 중",
        stats['developing'],
        delta=None
    )

with col4:
    st.metric(
        "평균 진행률",
        f"{stats['avg_progress']:.1%}",
        delta=None
    )

st.divider()

# 차트 영역
st.subheader("📈 시스템 현황")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**상태별 시스템 분포**")
    if systems:
        fig_status = create_status_pie(systems)
        st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.info("등록된 시스템이 없습니다.")

with col2:
    st.markdown("**진행률 분포**")
    if systems:
        fig_progress = create_progress_histogram(systems)
        st.plotly_chart(fig_progress, use_container_width=True)
    else:
        st.info("등록된 시스템이 없습니다.")

col3, col4 = st.columns(2)

with col3:
    st.markdown("**부서별 시스템 수**")
    if stats['dept_distribution']:
        fig_dept = create_dept_bar(stats['dept_distribution'])
        st.plotly_chart(fig_dept, use_container_width=True)
    else:
        st.info("부서 데이터가 없습니다.")

with col4:
    st.markdown("**서비스 비용 현황**")
    if services:
        total_cost = sum(s['monthly_cost'] for s in services)
        yearly_cost = total_cost * 12
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("월 비용", f"${total_cost:,.2f}")
        with col_b:
            st.metric("연간 비용", f"${yearly_cost:,.2f}")

        cost_df = pd.DataFrame(services)[['service_name', 'monthly_cost', 'plan_type']]
        cost_df.columns = ['서비스', '월 비용', '요금제']
        cost_df['월 비용'] = cost_df['월 비용'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(cost_df, hide_index=True, use_container_width=True)
    else:
        st.info("등록된 서비스가 없습니다.")

st.divider()

# 최근 활동 & 알림
st.subheader("📌 최근 활동 & 알림")

tab1, tab2, tab3 = st.tabs(["최근 수정", "주의 필요", "완료 임박"])

with tab1:
    if stats['recent_updates']:
        recent_df = pd.DataFrame(stats['recent_updates'])
        st.dataframe(
            recent_df,
            column_config={
                "system_name": st.column_config.TextColumn("시스템명", width="medium"),
                "status": st.column_config.TextColumn("상태", width="small"),
                "progress": st.column_config.ProgressColumn(
                    "진행률",
                    format="%.0f%%",
                    min_value=0,
                    max_value=100
                ),
                "updated_at": st.column_config.TextColumn("수정일시", width="medium")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("최근 수정된 시스템이 없습니다.")

with tab2:
    if stats['alert_systems']:
        st.warning(f"⚠️ {len(stats['alert_systems'])}개 시스템이 주의가 필요합니다.")
        alert_df = pd.DataFrame(stats['alert_systems'])
        st.dataframe(
            alert_df,
            column_config={
                "system_name": st.column_config.TextColumn("시스템명", width="medium"),
                "status": st.column_config.TextColumn("상태", width="small"),
                "progress": st.column_config.ProgressColumn(
                    "진행률",
                    format="%.0f%%",
                    min_value=0,
                    max_value=100
                ),
                "updated_at": st.column_config.TextColumn("마지막 수정", width="small"),
                "reason": st.column_config.TextColumn("주의 사유", width="medium")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.success("✅ 주의가 필요한 시스템이 없습니다.")

with tab3:
    if stats['upcoming_systems']:
        st.info(f"🎯 {len(stats['upcoming_systems'])}개 시스템이 곧 완료됩니다.")
        upcoming_df = pd.DataFrame(stats['upcoming_systems'])
        st.dataframe(
            upcoming_df,
            column_config={
                "system_name": st.column_config.TextColumn("시스템명", width="medium"),
                "status": st.column_config.TextColumn("상태", width="small"),
                "progress": st.column_config.ProgressColumn(
                    "진행률",
                    format="%.0f%%",
                    min_value=0,
                    max_value=100
                ),
                "target_date": st.column_config.TextColumn("목표일", width="small")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("완료 임박 시스템이 없습니다.")

# 사이드바
with st.sidebar:
    st.header("⚙️ 빠른 메뉴")

    if st.button("🔄 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    st.header("📖 사용 가이드")
    with st.expander("빠른 시작"):
        st.markdown("""
        1. **시스템 목록**: 모든 개발 시스템 조회 및 필터링
        2. **시스템 등록**: 새 시스템 추가/수정
        3. **비용 관리**: 서비스 비용 관리
        4. **통계 리포트**: 상세 통계 및 리포트
        5. **설정**: 앱 설정
        6. **Excel 관리**: Import/Export
        """)

    with st.expander("주요 기능"):
        st.markdown("""
        - ✅ 실시간 현황 조회
        - ✅ 다양한 필터링 옵션
        - ✅ Excel 완벽 호환
        - ✅ 변경 이력 추적
        - ✅ 자동 차트 생성
        - ✅ 알림 기능
        """)

    st.divider()

    # 상태별 요약
    st.header("📋 상태별 요약")
    for status, count in stats['status_counts'].items():
        if status == '운영 가능':
            st.success(f"{status}: {count}개")
        elif status == '개발 중':
            st.info(f"{status}: {count}개")
        elif status == '테스트 필요':
            st.warning(f"{status}: {count}개")
        else:
            st.error(f"{status}: {count}개")

# 푸터
st.divider()
st.caption("© 2026 개발시스템 관리 시스템 | Powered by Streamlit")
