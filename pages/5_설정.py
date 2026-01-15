import streamlit as st
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_all_systems, get_system_history

st.set_page_config(page_title="설정", layout="wide")

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

st.markdown("<p class='page-title'>설정</p>", unsafe_allow_html=True)

# 탭 구성
tab1, tab2, tab3 = st.tabs(["사용자 설정", "변경 이력", "시스템 설정"])

with tab1:
    st.markdown("<p class='section-title'>사용자 설정</p>", unsafe_allow_html=True)

    # 사용자 이름 설정
    if 'user_name' not in st.session_state:
        st.session_state.user_name = '조성우'

    user_name = st.text_input("사용자 이름", value=st.session_state.user_name)

    if st.button("저장", key="save_user"):
        st.session_state.user_name = user_name
        st.success(f"사용자 이름이 '{user_name}'(으)로 저장되었습니다.")

    st.divider()

    # 기본 설정
    st.markdown("<p class='section-title'>기본 설정</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        default_status = st.selectbox(
            "기본 상태",
            options=["초기 개발", "개발 중", "테스트 필요", "운영 가능"],
            index=1
        )

        default_owner = st.text_input("기본 담당자", value="조성우")

    with col2:
        items_per_page = st.number_input(
            "페이지당 항목 수",
            min_value=5,
            max_value=100,
            value=20,
            step=5
        )

        auto_refresh = st.checkbox("자동 새로고침 (60초)", value=False)

with tab2:
    st.markdown("<p class='section-title'>변경 이력 조회</p>", unsafe_allow_html=True)

    systems = get_all_systems()

    if systems:
        system_names = [s['system_name'] for s in systems]
        selected_system = st.selectbox("시스템 선택", options=system_names)

        selected_data = next((s for s in systems if s['system_name'] == selected_system), None)

        if selected_data:
            history = get_system_history(selected_data['id'])

            if history:
                st.write(f"**총 {len(history)}건의 변경 이력**")

                for h in history:
                    with st.expander(
                        f"{h['changed_at'].strftime('%Y-%m-%d %H:%M') if h['changed_at'] else 'N/A'} - {h['field_name']}",
                        expanded=False
                    ):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**필드:** {h['field_name']}")
                            st.write(f"**변경자:** {h['changed_by'] or '시스템'}")
                        with col2:
                            st.write(f"**이전 값:** {h['old_value'] or '(없음)'}")
                            st.write(f"**새 값:** {h['new_value'] or '(없음)'}")

                        if h['comment']:
                            st.write(f"**코멘트:** {h['comment']}")
            else:
                st.info("변경 이력이 없습니다.")
    else:
        st.info("등록된 시스템이 없습니다.")

with tab3:
    st.markdown("<p class='section-title'>시스템 설정</p>", unsafe_allow_html=True)

    # 데이터베이스 정보
    st.markdown("**데이터베이스 정보**")

    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'dev_systems.db')

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**DB 경로:** `{db_path}`")
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path)
            st.write(f"**DB 크기:** {db_size / 1024:.2f} KB")
            st.write(f"**마지막 수정:** {datetime.fromtimestamp(os.path.getmtime(db_path)).strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.warning("데이터베이스 파일이 없습니다.")

    with col2:
        total_systems = len(systems) if systems else 0
        st.write(f"**총 시스템 수:** {total_systems}개")

    st.divider()

    # 캐시 관리
    st.markdown("**캐시 관리**")

    if st.button("캐시 초기화", use_container_width=False):
        st.cache_data.clear()
        st.success("캐시가 초기화되었습니다.")
        st.rerun()

    st.divider()

    # 데이터 백업
    st.markdown("**데이터 백업**")

    if st.button("DB 백업 다운로드", use_container_width=False):
        if os.path.exists(db_path):
            with open(db_path, 'rb') as f:
                db_data = f.read()

            st.download_button(
                label="다운로드",
                data=db_data,
                file_name=f"dev_systems_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                mime="application/octet-stream"
            )
        else:
            st.error("데이터베이스 파일을 찾을 수 없습니다.")

    st.divider()

    # 앱 정보
    st.markdown("**앱 정보**")
    st.write("**버전:** 1.0.0")
    st.write("**프레임워크:** Streamlit")
    st.write("**데이터베이스:** SQLite + SQLAlchemy")
    st.write("**차트:** Plotly")

# 사이드바
with st.sidebar:
    st.markdown("### 도움말")

    with st.expander("사용자 설정"):
        st.markdown("""
        - **사용자 이름**: 시스템 등록/수정 시 기록되는 이름
        - **기본 설정**: 새 시스템 등록 시 기본값
        """)

    with st.expander("변경 이력"):
        st.markdown("""
        - 시스템별 모든 변경사항 추적
        - 필드별 이전/이후 값 확인 가능
        - 변경자 및 시간 기록
        """)

    with st.expander("시스템 설정"):
        st.markdown("""
        - **캐시 초기화**: 데이터 갱신 문제 시 사용
        - **DB 백업**: 데이터 안전 보관용
        """)
