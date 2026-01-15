import streamlit as st
from datetime import date
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_all_systems, get_system_by_name, create_system, update_system
from utils.validators import validate_system_data

st.set_page_config(page_title="시스템 등록", layout="wide")

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

st.markdown("<p class='page-title'>시스템 등록 / 수정</p>", unsafe_allow_html=True)

# 편집 모드 확인
edit_mode = False
system_data = {}

if 'edit_system' in st.session_state and st.session_state['edit_system']:
    edit_mode = True
    system_data = get_system_by_name(st.session_state['edit_system']) or {}

# 모드 선택
mode = st.radio(
    "모드",
    ["신규 등록", "기존 시스템 수정"],
    horizontal=True,
    index=1 if edit_mode else 0
)

if mode == "기존 시스템 수정":
    systems = get_all_systems()
    system_names = [s['system_name'] for s in systems]

    if system_names:
        default_idx = 0
        if edit_mode and system_data.get('system_name') in system_names:
            default_idx = system_names.index(system_data['system_name'])

        system_to_edit = st.selectbox(
            "수정할 시스템 선택",
            options=system_names,
            index=default_idx
        )
        system_data = get_system_by_name(system_to_edit) or {}
    else:
        st.warning("등록된 시스템이 없습니다. 신규 등록을 선택해주세요.")
        system_data = {}
else:
    system_data = {}
    if 'edit_system' in st.session_state:
        del st.session_state['edit_system']

st.divider()

# 폼
with st.form("system_form"):
    st.markdown("<p class='section-title'>기본 정보</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        system_name = st.text_input(
            "시스템명 *",
            value=system_data.get('system_name', ''),
            placeholder="예: 제안제도 시스템"
        )

        url = st.text_input(
            "URL",
            value=system_data.get('url', ''),
            placeholder="https://example.com"
        )

        department_options = ["생산기획팀", "생산팀", "개발팀", "위수탁팀", "SCM팀", "물류팀", "전사"]
        departments = st.multiselect(
            "사용 부서",
            options=department_options,
            default=system_data.get('departments', [])
        )

        owner = st.text_input(
            "담당자",
            value=system_data.get('owner', '조성우')
        )

    with col2:
        status_options = ["초기 개발", "개발 중", "테스트 필요", "운영 가능"]
        current_status = system_data.get('status', '개발 중')
        status_idx = status_options.index(current_status) if current_status in status_options else 1

        status = st.selectbox(
            "상태 *",
            options=status_options,
            index=status_idx
        )

        current_progress = system_data.get('progress', 0.0)
        if isinstance(current_progress, (int, float)):
            progress_value = float(current_progress)
        else:
            progress_value = 0.0

        progress = st.slider(
            "진행률 *",
            min_value=0.0,
            max_value=1.0,
            value=progress_value,
            step=0.05,
            format="%.0f%%"
        )

        col_a, col_b = st.columns(2)
        with col_a:
            start_date_val = system_data.get('start_date')
            if start_date_val and not isinstance(start_date_val, date):
                start_date_val = None
            start_date = st.date_input(
                "시작일",
                value=start_date_val
            )
        with col_b:
            target_date_val = system_data.get('target_date')
            if target_date_val and not isinstance(target_date_val, date):
                target_date_val = None
            target_date = st.date_input(
                "목표 완료일",
                value=target_date_val
            )

    description = st.text_area(
        "서비스 개요 *",
        value=system_data.get('description', ''),
        height=100,
        placeholder="시스템의 목적과 주요 기능을 설명해주세요"
    )

    st.markdown("<p class='section-title'>기술 스택</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Front-end**")
        frontend_options = ["", "Netlify", "Vercel", "Firebase", "GitHub Pages", "Local Test", "기타"]
        current_frontend = system_data.get('frontend_platform', '')
        frontend_idx = frontend_options.index(current_frontend) if current_frontend in frontend_options else 0

        frontend_platform = st.selectbox(
            "플랫폼",
            options=frontend_options,
            index=frontend_idx,
            key="frontend_platform"
        )

        frontend_plan = st.text_input(
            "요금제",
            value=system_data.get('frontend_plan', ''),
            placeholder="예: 무료, Pro $12/월",
            key="frontend_plan"
        )

    with col2:
        st.markdown("**Back-end**")
        backend_options = ["", "Firebase", "Supabase", "AWS", "GCP", "Heroku", "기타"]
        current_backend = system_data.get('backend_platform', '')
        backend_idx = backend_options.index(current_backend) if current_backend in backend_options else 0

        backend_platform = st.selectbox(
            "플랫폼",
            options=backend_options,
            index=backend_idx,
            key="backend_platform"
        )

        backend_plan = st.text_input(
            "요금제",
            value=system_data.get('backend_plan', ''),
            placeholder="예: 무료(과금결제), Standard $25/월",
            key="backend_plan"
        )

    api_info = st.text_input(
        "API 정보",
        value=system_data.get('api_info', ''),
        placeholder="예: GPT API, Google Maps API"
    )

    notes = st.text_area(
        "비고",
        value=system_data.get('notes', ''),
        height=100,
        placeholder="특이사항, 추가 정보 등"
    )

    # 제출 버튼
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        submitted = st.form_submit_button(
            "저장",
            use_container_width=True,
            type="primary"
        )
    with col2:
        cancelled = st.form_submit_button(
            "취소",
            use_container_width=True
        )

if submitted:
    # 데이터 준비
    data = {
        'system_name': system_name,
        'description': description,
        'url': url,
        'departments': departments,
        'progress': progress,
        'status': status,
        'frontend_platform': frontend_platform,
        'frontend_plan': frontend_plan,
        'backend_platform': backend_platform,
        'backend_plan': backend_plan,
        'api_info': api_info,
        'owner': owner,
        'start_date': start_date,
        'target_date': target_date,
        'notes': notes
    }

    # 유효성 검증
    validation = validate_system_data(data)

    if not validation['valid']:
        for error in validation['errors']:
            st.error(error)
    else:
        # 저장
        if mode == "신규 등록":
            # 중복 확인
            existing = get_system_by_name(system_name)
            if existing:
                st.error(f"'{system_name}' 시스템명이 이미 존재합니다.")
            else:
                create_system(data)
                st.success(f"'{system_name}' 시스템이 등록되었습니다!")
                # 세션 초기화
                if 'edit_system' in st.session_state:
                    del st.session_state['edit_system']
                st.cache_data.clear()
        else:
            update_system(system_data['id'], data, changed_by=owner)
            st.success(f"'{system_name}' 시스템이 수정되었습니다!")
            st.cache_data.clear()

if cancelled:
    if 'edit_system' in st.session_state:
        del st.session_state['edit_system']
    st.switch_page("pages/1_시스템_목록.py")
