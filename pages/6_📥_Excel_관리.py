import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_all_systems
from utils.excel_handler import import_from_excel, export_to_excel, export_to_csv, create_empty_template, get_db_columns, get_all_columns

st.set_page_config(page_title="Excel 관리", page_icon="📥", layout="wide")

st.title("📥 Excel Import / Export")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📤 가져오기", "📥 내보내기", "📄 템플릿"])

with tab1:
    st.header("📤 Excel 파일 가져오기")

    uploaded_file = st.file_uploader(
        "엑셀 파일 선택",
        type=['xlsx', 'xls'],
        help="xlsx 또는 xls 형식의 파일을 업로드하세요"
    )

    if uploaded_file:
        try:
            # 시트 목록 확인
            xl = pd.ExcelFile(uploaded_file)
            sheet_names = xl.sheet_names

            st.success(f"✅ 파일 로드 성공: {uploaded_file.name}")

            # 시트 선택
            selected_sheet = st.selectbox("시트 선택", options=sheet_names)

            # 헤더 행 선택
            header_row = st.number_input("헤더 행 (0부터 시작)", min_value=0, max_value=10, value=0)

            # 데이터 로드
            df = pd.read_excel(uploaded_file, sheet_name=selected_sheet, header=header_row)

            st.write(f"**총 {len(df)}행 x {len(df.columns)}열**")

            # 미리보기
            st.subheader("📋 미리보기 (상위 10행)")
            st.dataframe(df.head(10), use_container_width=True)

            st.divider()

            # 컬럼 매핑
            st.subheader("🔗 컬럼 매핑")
            st.info("Excel 컬럼을 DB 컬럼에 매핑하세요. '건너뛰기'를 선택하면 해당 필드는 비워집니다.")

            excel_columns = ["건너뛰기"] + df.columns.tolist()
            db_columns = get_db_columns()

            mapping = {}

            # 자동 매핑 시도
            auto_mapping = {
                'system_name': ['시스템명', 'system_name', '시스템', 'name'],
                'description': ['서비스 개요', 'description', '설명', '개요'],
                'url': ['url', 'URL', '주소', '링크'],
                'departments': ['사용 부서', 'departments', '부서'],
                'progress': ['진행률', 'progress', '진행'],
                'status': ['상태', 'status'],
                'frontend_platform': ['Front-end', 'frontend', 'FE 플랫폼'],
                'backend_platform': ['Back-end', 'backend', 'BE 플랫폼'],
                'owner': ['담당자', 'owner', '담당'],
                'notes': ['비고', 'notes', '메모']
            }

            col1, col2 = st.columns(2)

            for idx, db_col in enumerate(db_columns):
                # 자동 매핑 시도
                default_idx = 0
                for excel_col in excel_columns[1:]:
                    excel_col_lower = str(excel_col).lower()
                    if db_col in auto_mapping:
                        for keyword in auto_mapping[db_col]:
                            if keyword.lower() in excel_col_lower:
                                default_idx = excel_columns.index(excel_col)
                                break
                    if default_idx > 0:
                        break

                target_col = col1 if idx % 2 == 0 else col2
                with target_col:
                    mapping[db_col] = st.selectbox(
                        f"DB: {db_col}",
                        options=excel_columns,
                        index=default_idx,
                        key=f"map_{db_col}"
                    )

            st.divider()

            # 중복 처리 방식
            duplicate_strategy = st.radio(
                "중복된 시스템명 처리 방식",
                options=["덮어쓰기", "건너뛰기", "새로 추가"],
                horizontal=True,
                help="이미 존재하는 시스템명이 있을 때 처리 방법"
            )

            # Import 실행
            st.divider()

            if st.button("🚀 가져오기 실행", type="primary", use_container_width=True):
                with st.spinner("데이터 가져오는 중..."):
                    result = import_from_excel(
                        df=df,
                        mapping=mapping,
                        strategy=duplicate_strategy
                    )

                    st.success(f"""
                    ✅ Import 완료!
                    - 성공: {result['success']}건
                    - 실패: {result['failed']}건
                    - 건너뜀: {result['skipped']}건
                    """)

                    if result['errors']:
                        with st.expander("❌ 오류 상세", expanded=True):
                            for error in result['errors']:
                                st.error(error)

                    st.cache_data.clear()

        except Exception as e:
            st.error(f"❌ 파일 처리 중 오류: {str(e)}")

with tab2:
    st.header("📥 Excel 파일 내보내기")

    systems = get_all_systems()

    if systems:
        col1, col2 = st.columns(2)

        with col1:
            export_format = st.selectbox(
                "파일 형식",
                options=["Excel (.xlsx)", "CSV (.csv)"]
            )

        with col2:
            include_deleted = st.checkbox("삭제된 시스템 포함", value=False)

        # 컬럼 선택
        st.subheader("📋 내보낼 컬럼 선택")

        all_columns = get_all_columns()

        # 기본 선택 컬럼
        default_columns = [
            'system_name', 'description', 'url', 'departments',
            'progress', 'status', 'frontend_platform', 'backend_platform',
            'owner', 'notes'
        ]

        selected_columns = st.multiselect(
            "컬럼",
            options=all_columns,
            default=[c for c in default_columns if c in all_columns]
        )

        st.divider()

        # Export 실행
        if st.button("📥 파일 생성", type="primary", use_container_width=True):
            with st.spinner("파일 생성 중..."):
                # 데이터 로드
                export_data = get_all_systems(include_deleted=include_deleted)

                if export_format == "Excel (.xlsx)":
                    output = export_to_excel(export_data, columns=selected_columns)
                    filename = f"개발시스템_현황_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                else:
                    output = export_to_csv(export_data, columns=selected_columns)
                    filename = f"개발시스템_현황_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    mime = "text/csv"

                st.download_button(
                    label="⬇️ 다운로드",
                    data=output,
                    file_name=filename,
                    mime=mime,
                    use_container_width=True
                )

        # 미리보기
        st.divider()
        st.subheader("📋 데이터 미리보기")

        preview_df = pd.DataFrame(systems)
        if selected_columns:
            preview_cols = [c for c in selected_columns if c in preview_df.columns]
            preview_df = preview_df[preview_cols]

        st.dataframe(preview_df.head(5), use_container_width=True)
        st.caption(f"총 {len(systems)}개 시스템")

    else:
        st.info("내보낼 데이터가 없습니다. 시스템을 먼저 등록해주세요.")

with tab3:
    st.header("📄 빈 템플릿 다운로드")

    st.write("새로운 시스템을 엑셀로 작성 후 가져오기 할 수 있습니다.")

    st.markdown("""
    **템플릿 사용 방법:**
    1. 아래 버튼을 클릭하여 템플릿 다운로드
    2. 엑셀에서 데이터 입력
    3. '가져오기' 탭에서 파일 업로드
    4. 컬럼 매핑 후 가져오기 실행
    """)

    st.divider()

    # 템플릿 컬럼 설명
    st.subheader("📋 컬럼 설명")

    column_descriptions = {
        'system_name': '시스템명 (필수) - 고유한 이름',
        'description': '서비스 개요 (필수) - 시스템 설명',
        'url': 'URL - 시스템 접속 주소',
        'departments': '사용 부서 - 쉼표로 구분 (예: 개발팀, 기획팀)',
        'progress': '진행률 - 0~100 사이의 숫자',
        'status': '상태 - 초기 개발/개발 중/테스트 필요/운영 가능',
        'frontend_platform': 'Front-end 플랫폼 - Netlify, Vercel 등',
        'frontend_plan': 'Front-end 요금제',
        'backend_platform': 'Back-end 플랫폼 - Firebase, Supabase 등',
        'backend_plan': 'Back-end 요금제',
        'api_info': 'API 정보 - 사용 중인 외부 API',
        'owner': '담당자',
        'start_date': '시작일 - YYYY-MM-DD 형식',
        'target_date': '목표 완료일 - YYYY-MM-DD 형식',
        'notes': '비고'
    }

    for col, desc in column_descriptions.items():
        st.write(f"- **{col}**: {desc}")

    st.divider()

    if st.button("📄 템플릿 다운로드", type="primary", use_container_width=True):
        template = create_empty_template()
        st.download_button(
            label="⬇️ 다운로드",
            data=template,
            file_name="개발시스템_입력양식.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# 사이드바
with st.sidebar:
    st.header("💡 Excel 관리 팁")

    with st.expander("가져오기 주의사항"):
        st.markdown("""
        - **필수 필드**: 시스템명, 서비스 개요
        - **진행률**: 0~100 또는 0~1 (자동 변환)
        - **부서**: 쉼표로 구분
        - **날짜**: YYYY-MM-DD 형식 권장
        """)

    with st.expander("내보내기 활용"):
        st.markdown("""
        - 주간/월간 리포트 생성
        - 백업용 데이터 저장
        - 다른 팀과 데이터 공유
        - 오프라인 작업 후 재업로드
        """)

    with st.expander("대용량 파일 처리"):
        st.markdown("""
        - **권장 크기**: 1,000행 이하
        - **대용량 시**: 파일 분할 업로드
        - **느린 경우**: 불필요한 컬럼 제거
        """)
