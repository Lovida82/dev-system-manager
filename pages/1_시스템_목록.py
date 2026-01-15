import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_all_systems, delete_system, get_all_departments, get_all_platforms

st.set_page_config(page_title="시스템 목록", layout="wide")

# CSS
st.markdown("""
<style>
    html, body, [class*="css"] { font-size: 14px; }
    .page-title { font-size: 1.25rem; font-weight: 600; color: #1e293b; margin-bottom: 1rem; }
    [data-testid="stMetric"] { background: #f8fafc; padding: 0.75rem; border-radius: 8px; border: 1px solid #e2e8f0; }
    .stButton > button { font-size: 0.875rem; border-radius: 6px; }
    .delete-btn button { background-color: #dc2626 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)


# 삭제 확인 다이얼로그
@st.dialog("시스템 삭제 확인")
def confirm_delete_dialog(system_name, system_id):
    st.warning(f"**'{system_name}'** 시스템을 삭제하시겠습니까?")
    st.caption("삭제된 시스템은 복구할 수 없습니다.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("취소", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("삭제", use_container_width=True, type="primary"):
            delete_system(system_id)
            st.cache_data.clear()
            st.session_state['delete_success'] = system_name
            st.rerun()


# 삭제 성공 메시지 표시
if 'delete_success' in st.session_state:
    st.success(f"'{st.session_state['delete_success']}' 시스템이 삭제되었습니다.")
    del st.session_state['delete_success']

st.markdown("<p class='page-title'>시스템 목록</p>", unsafe_allow_html=True)


@st.cache_data(ttl=30)
def load_systems():
    return get_all_systems()


systems = load_systems()

# 필터 사이드바
with st.sidebar:
    st.markdown("### 필터")

    status_options = ["초기 개발", "개발 중", "테스트 필요", "운영 가능"]
    status_filter = st.multiselect("상태", options=status_options, default=status_options)

    all_departments = get_all_departments()
    dept_filter = st.multiselect("사용 부서", options=all_departments) if all_departments else []

    progress_range = st.slider("진행률", 0, 100, (0, 100), 5, format="%d%%")

    frontend_platforms = ["전체"] + get_all_platforms("frontend")
    frontend_filter = st.selectbox("Front-end", options=frontend_platforms)

    backend_platforms = ["전체"] + get_all_platforms("backend")
    backend_filter = st.selectbox("Back-end", options=backend_platforms)

    if st.button("필터 초기화", use_container_width=True):
        st.rerun()

# 검색
search_query = st.text_input("검색", placeholder="시스템명 또는 내용 검색...")

# 뷰 모드 및 정렬
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    view_mode = st.radio("표시 방식", ["테이블", "카드", "칸반"], horizontal=True)

with col2:
    sort_by = st.selectbox("정렬", ["최근 수정일", "시스템명", "진행률", "생성일"])

with col3:
    sort_order = st.selectbox("순서", ["내림차순", "오름차순"])

# 데이터 필터링
if systems:
    df = pd.DataFrame(systems)

    if status_filter:
        df = df[df['status'].isin(status_filter)]

    if dept_filter:
        def has_department(depts):
            if not depts:
                return False
            return any(d in depts for d in dept_filter)
        df = df[df['departments'].apply(has_department)]

    df = df[(df['progress'] * 100 >= progress_range[0]) & (df['progress'] * 100 <= progress_range[1])]

    if frontend_filter != "전체":
        df = df[df['frontend_platform'] == frontend_filter]

    if backend_filter != "전체":
        df = df[df['backend_platform'] == backend_filter]

    if search_query:
        q = search_query.lower()
        df = df[
            df['system_name'].str.lower().str.contains(q, na=False) |
            df['description'].str.lower().str.contains(q, na=False)
        ]

    sort_map = {"최근 수정일": "updated_at", "시스템명": "system_name", "진행률": "progress", "생성일": "created_at"}
    df = df.sort_values(sort_map[sort_by], ascending=(sort_order == "오름차순"))

    st.caption(f"총 {len(df)}개 시스템")

    if len(df) == 0:
        st.info("조건에 맞는 시스템이 없습니다.")
    elif view_mode == "테이블":
        display_df = df.copy()
        display_df['progress_pct'] = display_df['progress'] * 100
        display_df['departments_str'] = display_df['departments'].apply(lambda x: ', '.join(x) if x else '')
        display_df['updated_at_str'] = pd.to_datetime(display_df['updated_at']).dt.strftime('%Y-%m-%d %H:%M')

        st.dataframe(
            display_df[['system_name', 'description', 'url', 'departments_str', 'progress_pct', 'status', 'owner', 'updated_at_str']],
            column_config={
                "system_name": st.column_config.TextColumn("시스템명"),
                "description": st.column_config.TextColumn("서비스 개요"),
                "url": st.column_config.LinkColumn("URL"),
                "departments_str": st.column_config.TextColumn("부서"),
                "progress_pct": st.column_config.ProgressColumn("진행률", format="%.0f%%", min_value=0, max_value=100),
                "status": st.column_config.TextColumn("상태"),
                "owner": st.column_config.TextColumn("담당자"),
                "updated_at_str": st.column_config.TextColumn("수정일")
            },
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        selected = st.selectbox("작업할 시스템", ["선택"] + df['system_name'].tolist())

        if selected != "선택":
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("편집", use_container_width=True):
                    st.session_state['edit_system'] = selected
                    st.switch_page("pages/2_시스템_등록.py")
            with col2:
                with st.container():
                    st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                    if st.button("삭제", use_container_width=True, key="table_delete"):
                        sys_data = df[df['system_name'] == selected].iloc[0]
                        confirm_delete_dialog(selected, sys_data['id'])
                    st.markdown('</div>', unsafe_allow_html=True)

    elif view_mode == "카드":
        cols = st.columns(3)
        for idx, (_, row) in enumerate(df.iterrows()):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"**{row['system_name']}**")
                    st.caption(row['description'][:80] + "..." if len(str(row['description'])) > 80 else row['description'])
                    st.progress(row['progress'], text=f"{row['progress']*100:.0f}%")
                    st.caption(f"{row['status']} | {row['owner'] or '-'}")

                    # 편집/삭제 버튼
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("편집", key=f"edit_card_{row['id']}", use_container_width=True):
                            st.session_state['edit_system'] = row['system_name']
                            st.switch_page("pages/2_시스템_등록.py")
                    with btn_col2:
                        if st.button("삭제", key=f"del_card_{row['id']}", use_container_width=True):
                            confirm_delete_dialog(row['system_name'], row['id'])

    elif view_mode == "칸반":
        statuses = ["초기 개발", "개발 중", "테스트 필요", "운영 가능"]
        cols = st.columns(len(statuses))

        for idx, status in enumerate(statuses):
            with cols[idx]:
                st.markdown(f"**{status}**")
                status_df = df[df['status'] == status]
                st.caption(f"{len(status_df)}개")

                for _, row in status_df.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**{row['system_name']}**")
                        st.progress(row['progress'])
                        st.caption(f"{row['progress']*100:.0f}%")

                        # 편집/삭제 버튼
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if st.button("편집", key=f"edit_kb_{row['id']}", use_container_width=True):
                                st.session_state['edit_system'] = row['system_name']
                                st.switch_page("pages/2_시스템_등록.py")
                        with btn_col2:
                            if st.button("삭제", key=f"del_kb_{row['id']}", use_container_width=True):
                                confirm_delete_dialog(row['system_name'], row['id'])
else:
    st.info("등록된 시스템이 없습니다.")
    if st.button("시스템 등록하기"):
        st.switch_page("pages/2_시스템_등록.py")
