import pandas as pd
from io import BytesIO
from datetime import datetime
import os
import sys

# 상위 디렉토리 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def import_from_excel(df, mapping, strategy='덮어쓰기'):
    """Excel 파일에서 데이터 가져오기"""
    from database.db import get_system_by_name, create_system, update_system

    result = {
        'success': 0,
        'failed': 0,
        'skipped': 0,
        'errors': []
    }

    for idx, row in df.iterrows():
        try:
            # 매핑에 따라 데이터 변환
            data = {}

            for db_col, excel_col in mapping.items():
                if excel_col and excel_col != '건너뛰기':
                    value = row.get(excel_col)

                    # NaN 처리
                    if pd.isna(value):
                        value = None

                    # 진행률 변환
                    if db_col == 'progress' and value is not None:
                        try:
                            value = float(value)
                            if value > 1:
                                value = value / 100
                        except (ValueError, TypeError):
                            value = 0.0

                    # 부서 리스트 변환
                    if db_col == 'departments' and value is not None:
                        if isinstance(value, str):
                            value = [d.strip() for d in value.split(',') if d.strip()]
                        else:
                            value = []

                    # 날짜 변환
                    if db_col in ['start_date', 'target_date'] and value is not None:
                        if isinstance(value, str):
                            try:
                                value = datetime.strptime(value, '%Y-%m-%d').date()
                            except ValueError:
                                value = None
                        elif hasattr(value, 'date'):
                            value = value.date()

                    data[db_col] = value

            # 필수 필드 확인
            if not data.get('system_name'):
                result['errors'].append(f"행 {idx + 1}: 시스템명이 없습니다.")
                result['failed'] += 1
                continue

            # 기존 시스템 확인
            existing = get_system_by_name(data['system_name'])

            if existing:
                if strategy == '덮어쓰기':
                    update_system(existing['id'], data)
                    result['success'] += 1
                elif strategy == '건너뛰기':
                    result['skipped'] += 1
                else:  # '새로 추가'
                    # 이름에 번호 추가
                    data['system_name'] = f"{data['system_name']} ({idx + 1})"
                    create_system(data)
                    result['success'] += 1
            else:
                create_system(data)
                result['success'] += 1

        except Exception as e:
            result['errors'].append(f"행 {idx + 1}: {str(e)}")
            result['failed'] += 1

    return result


def export_to_excel(systems, columns=None):
    """시스템 데이터를 Excel로 내보내기"""
    if not systems:
        df = pd.DataFrame()
    else:
        df = pd.DataFrame(systems)

        # 컬럼 선택
        if columns:
            df = df[[c for c in columns if c in df.columns]]

        # 진행률 퍼센트 변환
        if 'progress' in df.columns:
            df['progress'] = df['progress'].apply(lambda x: f"{x * 100:.0f}%" if x else "0%")

        # 부서 리스트 문자열 변환
        if 'departments' in df.columns:
            df['departments'] = df['departments'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else ''
            )

        # 날짜 형식 변환
        for col in ['start_date', 'target_date', 'created_at', 'updated_at']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')

    # Excel 파일 생성
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='시스템 목록')

        # 컬럼 너비 자동 조정
        worksheet = writer.sheets['시스템 목록']
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).map(len).max() if len(df) > 0 else 0,
                len(col)
            ) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)

    output.seek(0)
    return output.getvalue()


def export_to_csv(systems, columns=None):
    """시스템 데이터를 CSV로 내보내기"""
    if not systems:
        df = pd.DataFrame()
    else:
        df = pd.DataFrame(systems)

        if columns:
            df = df[[c for c in columns if c in df.columns]]

        # 진행률 퍼센트 변환
        if 'progress' in df.columns:
            df['progress'] = df['progress'].apply(lambda x: f"{x * 100:.0f}%" if x else "0%")

        # 부서 리스트 문자열 변환
        if 'departments' in df.columns:
            df['departments'] = df['departments'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else ''
            )

    return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')


def create_empty_template():
    """빈 Excel 템플릿 생성"""
    columns = {
        'system_name': '시스템명',
        'description': '서비스 개요',
        'url': 'URL',
        'departments': '사용 부서 (쉼표로 구분)',
        'progress': '진행률 (0~100)',
        'status': '상태 (초기 개발/개발 중/테스트 필요/운영 가능)',
        'frontend_platform': 'Front-end 플랫폼',
        'frontend_plan': 'Front-end 요금제',
        'backend_platform': 'Back-end 플랫폼',
        'backend_plan': 'Back-end 요금제',
        'api_info': 'API 정보',
        'owner': '담당자',
        'start_date': '시작일 (YYYY-MM-DD)',
        'target_date': '목표 완료일 (YYYY-MM-DD)',
        'notes': '비고'
    }

    # 예시 데이터
    sample_data = {
        'system_name': '예시 시스템',
        'description': '시스템 설명을 입력하세요',
        'url': 'https://example.com',
        'departments': '개발팀, 기획팀',
        'progress': 50,
        'status': '개발 중',
        'frontend_platform': 'Vercel',
        'frontend_plan': '무료',
        'backend_platform': 'Supabase',
        'backend_plan': '무료',
        'api_info': 'REST API',
        'owner': '홍길동',
        'start_date': '2024-01-01',
        'target_date': '2024-06-30',
        'notes': '추가 메모'
    }

    df = pd.DataFrame([sample_data])

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='시스템 입력')

        # 컬럼 헤더에 설명 추가
        worksheet = writer.sheets['시스템 입력']
        for idx, (col_name, description) in enumerate(columns.items()):
            cell = worksheet.cell(row=1, column=idx + 1)
            cell.value = col_name
            cell.comment = None  # openpyxl Comment 추가 가능

        # 컬럼 너비 조정
        for idx, col in enumerate(df.columns):
            worksheet.column_dimensions[chr(65 + idx)].width = 20

    output.seek(0)
    return output.getvalue()


def get_db_columns():
    """DB 컬럼 목록 반환"""
    return [
        'system_name',
        'description',
        'url',
        'departments',
        'progress',
        'status',
        'frontend_platform',
        'frontend_plan',
        'backend_platform',
        'backend_plan',
        'api_info',
        'owner',
        'start_date',
        'target_date',
        'notes'
    ]


def get_all_columns():
    """내보내기용 전체 컬럼 목록"""
    return [
        'id',
        'system_name',
        'description',
        'url',
        'departments',
        'progress',
        'status',
        'frontend_platform',
        'frontend_plan',
        'backend_platform',
        'backend_plan',
        'api_info',
        'owner',
        'start_date',
        'target_date',
        'notes',
        'is_deleted',
        'created_at',
        'updated_at',
        'created_by'
    ]
