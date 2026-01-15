import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import get_all_systems, get_dashboard_stats, get_all_services
from utils.charts import create_status_pie, create_progress_histogram, create_dept_bar

# 페이지 설정
st.set_page_config(
    page_title="개발시스템 관리",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 모던 CSS 스타일
st.markdown("""
<style>
    /* 전체 폰트 크기 조정 */
    html, body, [class*="css"] {
        font-size: 14px;
    }

    /* 헤더 스타일 */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .main-header h1 {
        color: white;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
    }

    /* 메트릭 카드 */
    [data-testid="stMetric"] {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        color: #64748b;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 600;
        color: #1e293b;
    }

    /* 섹션 제목 */
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: #334155;
        margin: 1rem 0 0.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }

    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background: #f8fafc;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
    }

    /* 버튼 스타일 */
    .stButton > button {
        font-size: 0.875rem;
        border-radius: 6px;
    }

    /* 데이터프레임 */
    .stDataFrame {
        font-size: 0.875rem;
    }

    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.875rem;
        padding: 0.5rem 1rem;
    }

    /* 푸터 */
    .footer {
        font-size: 0.75rem;
        color: #94a3b8;
        text-align: center;
        padding: 1rem 0;
    }

    /* 상태 뱃지 */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    .status-production { background: #dcfce7; color: #166534; }
    .status-developing { background: #dbeafe; color: #1e40af; }
    .status-testing { background: #fef9c3; color: #854d0e; }
    .status-initial { background: #fee2e2; color: #991b1b; }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("""
<div class='main-header'>
    <h1>개발시스템 현황 대시보드</h1>
</div>
""", unsafe_allow_html=True)


# 데이터 로드
@st.cache_data(ttl=60)
def load_dashboard_data():
    systems = get_all_systems()
    stats = get_dashboard_stats()
    services = get_all_services()
    return systems, stats, services


systems, stats, services = load_dashboard_data()

# KPI 메트릭
st.markdown("<p class='section-title'>핵심 지표</p>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "전체 시스템",
        stats['total'],
        delta=f"+{stats['new_this_month']} 이번 달" if stats['new_this_month'] > 0 else None
    )

with col2:
    st.metric(
        "운영 중",
        stats['production'],
        delta=f"{stats['production_rate']:.0%}" if stats['total'] > 0 else "0%"
    )

with col3:
    st.metric("개발 중", stats['developing'])

with col4:
    st.metric("평균 진행률", f"{stats['avg_progress']:.0%}")

st.markdown("<br>", unsafe_allow_html=True)

# 차트 영역
st.markdown("<p class='section-title'>시스템 현황</p>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.caption("상태별 분포")
    if systems:
        fig_status = create_status_pie(systems)
        st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.info("등록된 시스템이 없습니다.")

with col2:
    st.caption("진행률 분포")
    if systems:
        fig_progress = create_progress_histogram(systems)
        st.plotly_chart(fig_progress, use_container_width=True)
    else:
        st.info("등록된 시스템이 없습니다.")

col3, col4 = st.columns(2)

with col3:
    st.caption("부서별 시스템 수")
    if stats['dept_distribution']:
        fig_dept = create_dept_bar(stats['dept_distribution'])
        st.plotly_chart(fig_dept, use_container_width=True)
    else:
        st.info("부서 데이터가 없습니다.")

with col4:
    st.caption("서비스 비용 현황")
    if services:
        total_cost = sum(s['monthly_cost'] for s in services)
        yearly_cost = total_cost * 12
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("월 비용", f"${total_cost:,.0f}")
        with col_b:
            st.metric("연간 비용", f"${yearly_cost:,.0f}")

        cost_df = pd.DataFrame(services)[['service_name', 'monthly_cost', 'plan_type']]
        cost_df.columns = ['서비스', '월 비용', '요금제']
        cost_df['월 비용'] = cost_df['월 비용'].apply(lambda x: f"${x:,.0f}")
        st.dataframe(cost_df, hide_index=True, use_container_width=True)
    else:
        st.info("등록된 서비스가 없습니다.")

st.markdown("<br>", unsafe_allow_html=True)

# 최근 활동
st.markdown("<p class='section-title'>최근 활동</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["최근 수정", "주의 필요", "완료 임박"])

with tab1:
    if stats['recent_updates']:
        recent_df = pd.DataFrame(stats['recent_updates'])
        st.dataframe(
            recent_df,
            column_config={
                "system_name": st.column_config.TextColumn("시스템명"),
                "status": st.column_config.TextColumn("상태"),
                "progress": st.column_config.ProgressColumn("진행률", format="%.0f%%", min_value=0, max_value=100),
                "updated_at": st.column_config.TextColumn("수정일")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("최근 수정된 시스템이 없습니다.")

with tab2:
    if stats['alert_systems']:
        st.warning(f"{len(stats['alert_systems'])}개 시스템 주의 필요")
        alert_df = pd.DataFrame(stats['alert_systems'])
        st.dataframe(alert_df, hide_index=True, use_container_width=True)
    else:
        st.success("주의가 필요한 시스템이 없습니다.")

with tab3:
    if stats['upcoming_systems']:
        upcoming_df = pd.DataFrame(stats['upcoming_systems'])
        st.dataframe(upcoming_df, hide_index=True, use_container_width=True)
    else:
        st.info("완료 임박 시스템이 없습니다.")

# 사이드바
with st.sidebar:
    st.markdown("### 빠른 메뉴")

    if st.button("새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

    st.markdown("### 상태별 요약")
    for status, count in stats['status_counts'].items():
        if count > 0:
            st.caption(f"{status}: {count}개")

# 푸터
st.markdown("<p class='footer'>Dev System Manager v1.0</p>", unsafe_allow_html=True)
