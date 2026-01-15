import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_all_systems, delete_system, get_all_departments, get_all_platforms

st.set_page_config(page_title="시스템 목록", page_icon="📋", layout="wide")

st.title("📋 시스템 목록")

# 데이터 로드
@st.cache_data(ttl=30)
def load_systems():
    return get_all_systems()

systems = load_systems()

# 필터 사이드바
with st.sidebar:
    st.header("🔍 필터")

    # 상태 필터
    status_options = ["초기 개발", "개발 중", "테스트 필요", "운영 가능"]
    status_filter = st.multiselect(
        "상태",
        options=status_options,
        default=status_options
    )

    # 부서 필터
    all_departments = get_all_departments()
    if all_departments:
        dept_filter = st.multiselect(
            "사용 부서",
            options=all_departments
        )
    else:
        dept_filter = []

    # 진행률 필터
    progress_range = st.slider(
        "진행률",
        min_value=0,
        max_value=100,
        value=(0, 100),
        step=5,
        format="%d%%"
    )

    # 플랫폼 필터
    frontend_platforms = ["전체"] + get_all_platforms("frontend")
    frontend_filter = st.selectbox(
        "Front-end 플랫폼",
        options=frontend_platforms
    )

    backend_platforms = ["전체"] + get_all_platforms("backend")
    backend_filter = st.selectbox(
        "Back-end 플랫폼",
        options=backend_platforms
    )

    if st.button("🔄 필터 초기화", use_container_width=True):
        st.rerun()

# 메인 영역
# 검색
search_query = st.text_input("🔎 시스템명 또는 내용 검색", placeholder="검색어 입력...")

# 뷰 모드 및 정렬
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    view_mode = st.radio(
        "표시 방식",
        options=["테이블", "카드", "칸반"],
        horizontal=True
    )

with col2:
    sort_by = st.selectbox(
        "정렬 기준",
        options=["최근 수정일", "시스템명", "진행률", "생성일"]
    )

with col3:
    sort_order = st.selectbox("순서", ["내림차순", "오름차순"])

# 데이터 필터링
if systems:
    df = pd.DataFrame(systems)

    # 상태 필터
    if status_filter:
        df = df[df['status'].isin(status_filter)]

    # 부서 필터
    if dept_filter:
        def has_department(depts):
            if not depts:
                return False
            return any(d in depts for d in dept_filter)
        df = df[df['departments'].apply(has_department)]

    # 진행률 필터
    df = df[(df['progress'] * 100 >= progress_range[0]) & (df['progress'] * 100 <= progress_range[1])]

    # 플랫폼 필터
    if frontend_filter != "전체":
        df = df[df['frontend_platform'] == frontend_filter]

    if backend_filter != "전체":
        df = df[df['backend_platform'] == backend_filter]

    # 검색
    if search_query:
        search_query = search_query.lower()
        df = df[
            df['system_name'].str.lower().str.contains(search_query, na=False) |
            df['description'].str.lower().str.contains(search_query, na=False)
        ]

    # 정렬
    sort_column_map = {
        "최근 수정일": "updated_at",
        "시스템명": "system_name",
        "진행률": "progress",
        "생성일": "created_at"
    }
    sort_col = sort_column_map[sort_by]
    ascending = sort_order == "오름차순"
    df = df.sort_values(sort_col, ascending=ascending)

    # 결과 수
    st.write(f"**총 {len(df)}개 시스템**")

    if len(df) == 0:
        st.info("조건에 맞는 시스템이 없습니다.")
    elif view_mode == "테이블":
        # 테이블 뷰
        display_df = df.copy()
        display_df['progress_pct'] = display_df['progress'] * 100
        display_df['departments_str'] = display_df['departments'].apply(
            lambda x: ', '.join(x) if x else ''
        )
        # 날짜 형식 변환
        display_df['updated_at_str'] = pd.to_datetime(display_df['updated_at']).dt.strftime('%Y-%m-%d %H:%M')

        st.dataframe(
            display_df[['system_name', 'description', 'url', 'departments_str', 'progress_pct', 'status', 'owner', 'updated_at_str']],
            column_config={
                "system_name": st.column_config.TextColumn("시스템명", width="medium"),
                "description": st.column_config.TextColumn("서비스 개요", width="large"),
                "url": st.column_config.LinkColumn("URL", width="small"),
                "departments_str": st.column_config.TextColumn("사용 부서", width="medium"),
                "progress_pct": st.column_config.ProgressColumn(
                    "진행률",
                    format="%.0f%%",
                    min_value=0,
                    max_value=100
                ),
                "status": st.column_config.TextColumn("상태", width="small"),
                "owner": st.column_config.TextColumn("담당자", width="small"),
                "updated_at_str": st.column_config.TextColumn("수정일", width="medium")
            },
            use_container_width=True,
            hide_index=True
        )

        # 시스템 선택 및 작업
        st.divider()
        selected_system = st.selectbox(
            "작업할 시스템 선택",
            options=["선택하세요"] + df['system_name'].tolist()
        )

        if selected_system != "선택하세요":
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✏️ 편집", use_container_width=True):
                    st.session_state['edit_system'] = selected_system
                    st.switch_page("pages/2_➕_시스템_등록.py")
            with col2:
                if st.button("🗑️ 삭제", use_container_width=True, type="primary"):
                    system_data = df[df['system_name'] == selected_system].iloc[0]
                    delete_system(system_data['id'])
                    st.success(f"'{selected_system}' 시스템이 삭제되었습니다.")
                    st.cache_data.clear()
                    st.rerun()
            with col3:
                if st.button("📊 상세보기", use_container_width=True):
                    st.session_state['view_system'] = selected_system
                    # 상세 모달 표시
                    system_data = df[df['system_name'] == selected_system].iloc[0].to_dict()
                    with st.expander(f"📋 {selected_system} 상세 정보", expanded=True):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write(f"**시스템명:** {system_data['system_name']}")
                            st.write(f"**상태:** {system_data['status']}")
                            st.write(f"**진행률:** {system_data['progress']*100:.0f}%")
                            st.write(f"**담당자:** {system_data['owner']}")
                            if system_data['url']:
                                st.write(f"**URL:** [{system_data['url']}]({system_data['url']})")
                        with col_b:
                            st.write(f"**Front-end:** {system_data['frontend_platform'] or '-'}")
                            st.write(f"**Back-end:** {system_data['backend_platform'] or '-'}")
                            st.write(f"**API:** {system_data['api_info'] or '-'}")
                            if system_data['departments']:
                                st.write(f"**부서:** {', '.join(system_data['departments'])}")
                        st.write("**서비스 개요:**")
                        st.write(system_data['description'])
                        if system_data['notes']:
                            st.write("**비고:**")
                            st.write(system_data['notes'])

    elif view_mode == "카드":
        # 카드 뷰
        cols = st.columns(3)
        for idx, (_, row) in enumerate(df.iterrows()):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.subheader(row['system_name'])
                    st.caption(row['description'][:100] + "..." if len(row['description']) > 100 else row['description'])
                    st.progress(row['progress'], text=f"{row['progress']*100:.0f}%")

                    status_colors = {
                        '운영 가능': '🟢',
                        '개발 중': '🔵',
                        '테스트 필요': '🟡',
                        '초기 개발': '🔴'
                    }
                    st.write(f"**상태:** {status_colors.get(row['status'], '⚪')} {row['status']}")

                    if row['departments']:
                        st.write(f"**부서:** {', '.join(row['departments'][:2])}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("상세", key=f"detail_{idx}", use_container_width=True):
                            st.session_state['edit_system'] = row['system_name']
                            st.switch_page("pages/2_➕_시스템_등록.py")
                    with col2:
                        if row['url']:
                            st.link_button("열기", row['url'], use_container_width=True)

    elif view_mode == "칸반":
        # 칸반 보드
        statuses = ["초기 개발", "개발 중", "테스트 필요", "운영 가능"]
        cols = st.columns(len(statuses))

        for idx, status in enumerate(statuses):
            with cols[idx]:
                status_colors = {
                    '운영 가능': '🟢',
                    '개발 중': '🔵',
                    '테스트 필요': '🟡',
                    '초기 개발': '🔴'
                }
                st.subheader(f"{status_colors.get(status, '')} {status}")
                status_df = df[df['status'] == status]

                st.caption(f"{len(status_df)}개 시스템")

                for _, row in status_df.iterrows():
                    with st.container(border=True):
                        st.write(f"**{row['system_name']}**")
                        st.progress(row['progress'])
                        st.caption(f"{row['progress']*100:.0f}% 완료")
                        if row['owner']:
                            st.caption(f"담당: {row['owner']}")

else:
    st.info("등록된 시스템이 없습니다. 시스템 등록 페이지에서 새 시스템을 추가해주세요.")
    if st.button("➕ 시스템 등록하기"):
        st.switch_page("pages/2_➕_시스템_등록.py")
