import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_all_systems, get_dashboard_stats, get_all_services

st.set_page_config(page_title="통계 리포트", layout="wide")

# CSS
st.markdown("""
<style>
    html, body, [class*="css"] { font-size: 14px; }
    .page-title { font-size: 1.25rem; font-weight: 600; color: #1e293b; margin-bottom: 1rem; }
    .section-title { font-size: 1rem; font-weight: 600; color: #334155; margin: 1rem 0 0.5rem 0; }
    [data-testid="stMetric"] { background: #f8fafc; padding: 0.75rem; border-radius: 8px; border: 1px solid #e2e8f0; }
    .stButton > button { font-size: 0.875rem; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<p class='page-title'>통계 리포트</p>", unsafe_allow_html=True)


# 데이터 로드
@st.cache_data(ttl=60)
def load_data():
    systems = get_all_systems()
    stats = get_dashboard_stats()
    services = get_all_services()
    return systems, stats, services


systems, stats, services = load_data()

if not systems:
    st.info("등록된 시스템이 없습니다. 시스템을 먼저 등록해주세요.")
    st.stop()

df = pd.DataFrame(systems)

# 리포트 기간 선택
st.sidebar.markdown("### 리포트 설정")
report_period = st.sidebar.selectbox(
    "기간",
    ["전체", "최근 1주일", "최근 1개월", "최근 3개월", "최근 6개월", "최근 1년"]
)

# 기간에 따른 필터링
if report_period != "전체":
    period_days = {
        "최근 1주일": 7,
        "최근 1개월": 30,
        "최근 3개월": 90,
        "최근 6개월": 180,
        "최근 1년": 365
    }
    cutoff_date = datetime.now() - timedelta(days=period_days[report_period])
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df[df['created_at'] >= cutoff_date]

# 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(["개요", "상세 분석", "부서별", "비용 분석"])

with tab1:
    st.markdown("<p class='section-title'>전체 현황 요약</p>", unsafe_allow_html=True)

    # KPI
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("총 시스템", len(df))
    with col2:
        production = len(df[df['status'] == '운영 가능'])
        st.metric("운영 중", production, delta=f"{production/len(df)*100:.0f}%" if len(df) > 0 else "0%")
    with col3:
        avg_progress = df['progress'].mean() * 100 if len(df) > 0 else 0
        st.metric("평균 진행률", f"{avg_progress:.1f}%")
    with col4:
        total_cost = sum(s['monthly_cost'] for s in services)
        st.metric("월 총 비용", f"${total_cost:,.2f}")

    st.divider()

    # 상태별 분포
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**상태별 시스템 수**")
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']

        color_map = {
            '초기 개발': '#FF6B6B',
            '개발 중': '#4ECDC4',
            '테스트 필요': '#FFE66D',
            '운영 가능': '#95E1D3'
        }

        fig = px.pie(
            status_counts,
            values='count',
            names='status',
            color='status',
            color_discrete_map=color_map,
            hole=0.4
        )
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**진행률 분포**")
        df['progress_pct'] = df['progress'] * 100

        fig = px.histogram(
            df,
            x='progress_pct',
            nbins=10,
            color_discrete_sequence=['#0066CC']
        )
        fig.update_layout(
            xaxis_title='진행률 (%)',
            yaxis_title='시스템 수',
            margin=dict(t=20, b=40, l=40, r=20),
            height=350
        )
        fig.update_xaxes(range=[0, 100], dtick=10)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("<p class='section-title'>상세 분석</p>", unsafe_allow_html=True)

    # 플랫폼별 분석
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Front-end 플랫폼 분포**")
        frontend_counts = df['frontend_platform'].fillna('미지정').value_counts().reset_index()
        frontend_counts.columns = ['platform', 'count']

        fig = px.bar(
            frontend_counts,
            x='count',
            y='platform',
            orientation='h',
            color='count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            xaxis_title='시스템 수',
            yaxis_title='플랫폼',
            margin=dict(t=20, b=40, l=100, r=20),
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Back-end 플랫폼 분포**")
        backend_counts = df['backend_platform'].fillna('미지정').value_counts().reset_index()
        backend_counts.columns = ['platform', 'count']

        fig = px.bar(
            backend_counts,
            x='count',
            y='platform',
            orientation='h',
            color='count',
            color_continuous_scale='Greens'
        )
        fig.update_layout(
            xaxis_title='시스템 수',
            yaxis_title='플랫폼',
            margin=dict(t=20, b=40, l=100, r=20),
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # 상태-진행률 매트릭스
    st.markdown("**상태별 평균 진행률**")

    status_progress = df.groupby('status')['progress'].mean().reset_index()
    status_progress['progress'] = status_progress['progress'] * 100
    status_progress.columns = ['상태', '평균 진행률']

    fig = px.bar(
        status_progress,
        x='상태',
        y='평균 진행률',
        color='평균 진행률',
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(
        yaxis_title='평균 진행률 (%)',
        margin=dict(t=20, b=40, l=40, r=20),
        height=350,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("<p class='section-title'>부서별 분석</p>", unsafe_allow_html=True)

    # 부서 데이터 추출
    dept_data = []
    for _, row in df.iterrows():
        if row['departments']:
            for dept in row['departments']:
                dept_data.append({
                    'department': dept,
                    'system_name': row['system_name'],
                    'status': row['status'],
                    'progress': row['progress']
                })

    if dept_data:
        dept_df = pd.DataFrame(dept_data)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**부서별 시스템 수**")
            dept_counts = dept_df.groupby('department').size().reset_index(name='count')
            dept_counts = dept_counts.sort_values('count', ascending=True)

            fig = px.bar(
                dept_counts,
                x='count',
                y='department',
                orientation='h',
                color='count',
                color_continuous_scale='Purples'
            )
            fig.update_layout(
                xaxis_title='시스템 수',
                yaxis_title='부서',
                margin=dict(t=20, b=40, l=100, r=20),
                height=350,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**부서별 평균 진행률**")
            dept_progress = dept_df.groupby('department')['progress'].mean().reset_index()
            dept_progress['progress'] = dept_progress['progress'] * 100
            dept_progress = dept_progress.sort_values('progress', ascending=True)

            fig = px.bar(
                dept_progress,
                x='progress',
                y='department',
                orientation='h',
                color='progress',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(
                xaxis_title='평균 진행률 (%)',
                yaxis_title='부서',
                margin=dict(t=20, b=40, l=100, r=20),
                height=350,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # 부서별 상세 테이블
        st.markdown("**부서별 시스템 목록**")
        selected_dept = st.selectbox("부서 선택", options=dept_df['department'].unique())

        filtered = dept_df[dept_df['department'] == selected_dept]
        display = filtered[['system_name', 'status', 'progress']].copy()
        display['progress'] = display['progress'] * 100
        display.columns = ['시스템명', '상태', '진행률(%)']

        st.dataframe(display, hide_index=True, use_container_width=True)

    else:
        st.info("부서 데이터가 없습니다.")

with tab4:
    st.markdown("<p class='section-title'>비용 분석</p>", unsafe_allow_html=True)

    if services:
        services_df = pd.DataFrame(services)
        total_cost = services_df['monthly_cost'].sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("월 총 비용", f"${total_cost:,.2f}")
        with col2:
            st.metric("연간 예상 비용", f"${total_cost * 12:,.2f}")
        with col3:
            cost_per_system = total_cost / len(df) if len(df) > 0 else 0
            st.metric("시스템당 비용", f"${cost_per_system:,.2f}")

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**서비스별 비용 비중**")
            fig = px.pie(
                services_df,
                values='monthly_cost',
                names='service_name',
                hole=0.4
            )
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**비용 순위**")
            sorted_services = services_df.sort_values('monthly_cost', ascending=True)

            fig = px.bar(
                sorted_services,
                x='monthly_cost',
                y='service_name',
                orientation='h',
                color='monthly_cost',
                color_continuous_scale='Reds'
            )
            fig.update_layout(
                xaxis_title='월 비용 (USD)',
                yaxis_title='서비스',
                margin=dict(t=20, b=40, l=100, r=20),
                height=350,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        # 비용 테이블
        st.divider()
        st.markdown("**상세 비용 내역**")
        cost_table = services_df[['service_name', 'plan_type', 'monthly_cost', 'currency']].copy()
        cost_table['연간 비용'] = cost_table['monthly_cost'] * 12
        cost_table.columns = ['서비스', '요금제', '월 비용', '통화', '연간 비용']
        st.dataframe(cost_table, hide_index=True, use_container_width=True)

    else:
        st.info("등록된 서비스가 없습니다.")

# 리포트 다운로드
st.divider()
st.markdown("<p class='section-title'>리포트 다운로드</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("Excel 리포트 다운로드", use_container_width=True):
        from utils.excel_handler import export_to_excel
        excel_data = export_to_excel(systems)
        st.download_button(
            label="다운로드",
            data=excel_data,
            file_name=f"개발시스템_리포트_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

with col2:
    if st.button("CSV 다운로드", use_container_width=True):
        from utils.excel_handler import export_to_csv
        csv_data = export_to_csv(systems)
        st.download_button(
            label="다운로드",
            data=csv_data,
            file_name=f"개발시스템_리포트_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
