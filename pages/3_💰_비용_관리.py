import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_all_services, create_service, update_service, delete_service
from utils.charts import create_cost_pie
from utils.validators import validate_service_data

st.set_page_config(page_title="비용 관리", page_icon="💰", layout="wide")

st.title("💰 서비스 비용 관리")


# 데이터 로드
@st.cache_data(ttl=30)
def load_services():
    return get_all_services()


services = load_services()

# 서비스 추가
with st.expander("➕ 새 서비스 추가", expanded=False):
    with st.form("service_form"):
        col1, col2 = st.columns(2)

        with col1:
            service_name = st.text_input("서비스명 *", placeholder="예: Claude API")
            plan_type = st.text_input("요금제", placeholder="예: Pro 플랜")
            payment_method = st.text_input("결제 방식", placeholder="예: 신용카드, 자동이체")

        with col2:
            monthly_cost = st.number_input("월 비용", min_value=0.0, step=0.01, format="%.2f")
            currency = st.selectbox("통화", ["USD", "KRW", "EUR", "JPY"], index=0)
            renewal_date = st.date_input("갱신일")

        notes = st.text_area("비고", placeholder="추가 메모...")

        if st.form_submit_button("➕ 추가", type="primary", use_container_width=True):
            data = {
                'service_name': service_name,
                'plan_type': plan_type,
                'monthly_cost': monthly_cost,
                'currency': currency,
                'renewal_date': renewal_date,
                'payment_method': payment_method,
                'notes': notes
            }

            validation = validate_service_data(data)
            if not validation['valid']:
                for error in validation['errors']:
                    st.error(error)
            else:
                create_service(data)
                st.success(f"✅ {service_name} 추가됨")
                st.cache_data.clear()
                st.rerun()

st.divider()

# 현재 서비스 목록
st.subheader("📋 현재 사용 중인 서비스")

if services:
    # 총 비용 계산
    services_df = pd.DataFrame(services)
    total_cost = services_df['monthly_cost'].sum()

    # KPI
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("월 총 비용", f"${total_cost:,.2f}")
    with col2:
        st.metric("서비스 수", f"{len(services)}개")
    with col3:
        yearly_cost = total_cost * 12
        st.metric("연간 예상 비용", f"${yearly_cost:,.2f}")

    st.divider()

    # 서비스 테이블
    display_df = services_df[['service_name', 'plan_type', 'monthly_cost', 'currency', 'renewal_date', 'payment_method', 'notes']].copy()
    display_df.columns = ['서비스명', '요금제', '월 비용', '통화', '갱신일', '결제 방식', '비고']

    st.dataframe(
        display_df,
        column_config={
            "서비스명": st.column_config.TextColumn("서비스명", width="medium"),
            "요금제": st.column_config.TextColumn("요금제", width="medium"),
            "월 비용": st.column_config.NumberColumn("월 비용", format="%.2f", width="small"),
            "통화": st.column_config.TextColumn("통화", width="small"),
            "갱신일": st.column_config.DateColumn("갱신일", width="small"),
            "결제 방식": st.column_config.TextColumn("결제 방식", width="medium"),
            "비고": st.column_config.TextColumn("비고", width="large"),
        },
        use_container_width=True,
        hide_index=True
    )

    # 서비스 수정
    st.divider()
    st.subheader("✏️ 서비스 수정")

    service_to_edit = st.selectbox(
        "수정할 서비스 선택",
        options=["선택하세요"] + services_df['service_name'].tolist(),
        key="edit_service_select"
    )

    if service_to_edit != "선택하세요":
        edit_data = services_df[services_df['service_name'] == service_to_edit].iloc[0].to_dict()

        with st.form("edit_service_form"):
            col1, col2 = st.columns(2)

            with col1:
                edit_service_name = st.text_input(
                    "서비스명 *",
                    value=edit_data['service_name']
                )
                edit_plan_type = st.text_input(
                    "요금제",
                    value=edit_data['plan_type'] or ''
                )
                edit_payment_method = st.text_input(
                    "결제 방식",
                    value=edit_data['payment_method'] or ''
                )

            with col2:
                edit_monthly_cost = st.number_input(
                    "월 비용",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    value=float(edit_data['monthly_cost'])
                )
                currency_options = ["USD", "KRW", "EUR", "JPY"]
                edit_currency = st.selectbox(
                    "통화",
                    currency_options,
                    index=currency_options.index(edit_data['currency']) if edit_data['currency'] in currency_options else 0
                )
                edit_renewal_date = st.date_input(
                    "갱신일",
                    value=edit_data['renewal_date'] if edit_data['renewal_date'] else None
                )

            edit_notes = st.text_area(
                "비고",
                value=edit_data['notes'] or ''
            )

            if st.form_submit_button("💾 수정 저장", type="primary", use_container_width=True):
                updated_data = {
                    'service_name': edit_service_name,
                    'plan_type': edit_plan_type,
                    'monthly_cost': edit_monthly_cost,
                    'currency': edit_currency,
                    'renewal_date': edit_renewal_date,
                    'payment_method': edit_payment_method,
                    'notes': edit_notes
                }

                validation = validate_service_data(updated_data)
                if not validation['valid']:
                    for error in validation['errors']:
                        st.error(error)
                else:
                    update_service(edit_data['id'], updated_data)
                    st.success(f"✅ {edit_service_name} 수정됨")
                    st.cache_data.clear()
                    st.rerun()

    # 서비스 삭제
    st.divider()
    st.subheader("🗑️ 서비스 삭제")

    col1, col2 = st.columns([3, 1])
    with col1:
        service_to_delete = st.selectbox(
            "삭제할 서비스 선택",
            options=["선택하세요"] + services_df['service_name'].tolist(),
            key="delete_service_select"
        )
    with col2:
        st.write("")
        st.write("")
        if st.button("🗑️ 삭제", use_container_width=True, type="primary"):
            if service_to_delete != "선택하세요":
                service_data = services_df[services_df['service_name'] == service_to_delete].iloc[0]
                delete_service(service_data['id'])
                st.success(f"✅ {service_to_delete} 삭제됨")
                st.cache_data.clear()
                st.rerun()

    st.divider()

    # 시각화
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 서비스별 비용 비중")
        fig = create_cost_pie(services)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📈 비용 순위")
        sorted_df = services_df.sort_values('monthly_cost', ascending=True)

        fig = px.bar(
            sorted_df,
            x='monthly_cost',
            y='service_name',
            orientation='h',
            labels={'monthly_cost': '월 비용 (USD)', 'service_name': '서비스'},
            color='monthly_cost',
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            showlegend=False,
            margin=dict(t=20, b=40, l=100, r=20),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("등록된 서비스가 없습니다. 새 서비스를 추가해주세요.")

# 사이드바
with st.sidebar:
    st.header("💡 비용 관리 팁")

    with st.expander("무료 vs 유료 서비스"):
        st.markdown("""
        **무료 티어 활용:**
        - Firebase: Spark Plan
        - Supabase: Free tier
        - Vercel: Hobby Plan
        - Netlify: Free tier

        **유료 전환 기준:**
        - 트래픽 초과
        - 스토리지 한도
        - 팀 협업 필요
        """)

    with st.expander("비용 절감 방법"):
        st.markdown("""
        1. **연간 결제** - 할인 적용
        2. **사용량 모니터링** - 불필요한 리소스 정리
        3. **적정 티어 선택** - 오버스펙 방지
        4. **무료 대안 검토** - 오픈소스 활용
        """)
