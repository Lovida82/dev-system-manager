import re
from datetime import date


def validate_system_data(data):
    """시스템 데이터 유효성 검증"""
    errors = []

    # 필수 필드 검증
    if not data.get('system_name'):
        errors.append("시스템명은 필수입니다.")
    elif len(data['system_name']) > 200:
        errors.append("시스템명은 200자를 초과할 수 없습니다.")

    if not data.get('description'):
        errors.append("서비스 개요는 필수입니다.")

    if not data.get('status'):
        errors.append("상태는 필수입니다.")
    elif data['status'] not in ['초기 개발', '개발 중', '테스트 필요', '운영 가능']:
        errors.append("유효하지 않은 상태값입니다.")

    # 진행률 검증
    progress = data.get('progress', 0)
    if not isinstance(progress, (int, float)):
        errors.append("진행률은 숫자여야 합니다.")
    elif progress < 0 or progress > 1:
        errors.append("진행률은 0~1 사이의 값이어야 합니다.")

    # URL 검증 (선택)
    url = data.get('url')
    if url:
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not url_pattern.match(url):
            errors.append("유효하지 않은 URL 형식입니다.")

    # 날짜 검증
    start_date = data.get('start_date')
    target_date = data.get('target_date')

    if start_date and target_date:
        if isinstance(start_date, date) and isinstance(target_date, date):
            if start_date > target_date:
                errors.append("시작일이 목표 완료일보다 늦을 수 없습니다.")

    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_service_data(data):
    """서비스 데이터 유효성 검증"""
    errors = []

    # 필수 필드 검증
    if not data.get('service_name'):
        errors.append("서비스명은 필수입니다.")
    elif len(data['service_name']) > 100:
        errors.append("서비스명은 100자를 초과할 수 없습니다.")

    # 비용 검증
    monthly_cost = data.get('monthly_cost', 0)
    if not isinstance(monthly_cost, (int, float)):
        errors.append("월 비용은 숫자여야 합니다.")
    elif monthly_cost < 0:
        errors.append("월 비용은 0 이상이어야 합니다.")

    # 통화 검증
    currency = data.get('currency', 'USD')
    if currency not in ['USD', 'KRW', 'EUR', 'JPY']:
        errors.append("지원하지 않는 통화입니다.")

    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_required_fields(data, required_fields):
    """필수 필드 존재 여부 검증"""
    missing = []
    for field in required_fields:
        if not data.get(field):
            missing.append(field)

    return {
        'valid': len(missing) == 0,
        'missing_fields': missing
    }


def sanitize_string(value, max_length=None):
    """문자열 정제"""
    if value is None:
        return ''

    value = str(value).strip()

    # XSS 방지를 위한 기본 정제
    value = value.replace('<', '&lt;').replace('>', '&gt;')

    if max_length and len(value) > max_length:
        value = value[:max_length]

    return value


def normalize_progress(value):
    """진행률 정규화 (0~1 범위로)"""
    if value is None:
        return 0.0

    try:
        value = float(value)
    except (ValueError, TypeError):
        return 0.0

    # 100 단위로 입력된 경우 변환
    if value > 1:
        value = value / 100

    # 범위 제한
    return max(0.0, min(1.0, value))
