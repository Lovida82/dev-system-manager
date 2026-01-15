import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from .models import Base, System, SystemHistory, Service, Attachment, Comment

# DB 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, 'dev_systems.db')


def get_engine():
    """SQLAlchemy 엔진 반환"""
    return create_engine(f"sqlite:///{DB_PATH}", echo=False)


def get_session():
    """새 세션 생성"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    """데이터베이스 초기화 (테이블 생성)"""
    engine = get_engine()
    Base.metadata.create_all(engine)


# ============== 시스템 CRUD ==============

def get_all_systems(include_deleted=False):
    """모든 시스템 조회"""
    session = get_session()
    try:
        query = session.query(System)
        if not include_deleted:
            query = query.filter(System.is_deleted == False)
        systems = query.order_by(System.updated_at.desc()).all()
        return [s.to_dict() for s in systems]
    finally:
        session.close()


def get_system_by_id(system_id):
    """ID로 시스템 조회"""
    session = get_session()
    try:
        system = session.query(System).filter(System.id == system_id).first()
        return system.to_dict() if system else None
    finally:
        session.close()


def get_system_by_name(system_name):
    """이름으로 시스템 조회"""
    session = get_session()
    try:
        system = session.query(System).filter(System.system_name == system_name).first()
        return system.to_dict() if system else None
    finally:
        session.close()


def create_system(data):
    """시스템 생성"""
    session = get_session()
    try:
        system = System(
            system_name=data.get('system_name'),
            description=data.get('description', ''),
            url=data.get('url'),
            departments=data.get('departments', []),
            progress=data.get('progress', 0.0),
            status=data.get('status', '개발 중'),
            frontend_platform=data.get('frontend_platform'),
            frontend_plan=data.get('frontend_plan'),
            backend_platform=data.get('backend_platform'),
            backend_plan=data.get('backend_plan'),
            api_info=data.get('api_info'),
            owner=data.get('owner'),
            start_date=data.get('start_date'),
            target_date=data.get('target_date'),
            notes=data.get('notes'),
            created_by=data.get('created_by', '')
        )
        session.add(system)
        session.commit()

        # 이력 기록
        record_history(
            system_id=system.id,
            field_name='created',
            old_value='',
            new_value='시스템 생성',
            changed_by=data.get('created_by', '')
        )

        return system.id
    finally:
        session.close()


def update_system(system_id, data, changed_by=''):
    """시스템 수정 및 이력 기록"""
    session = get_session()
    try:
        system = session.query(System).filter(System.id == system_id).first()

        if system:
            # 변경사항 추적
            for key, new_value in data.items():
                if hasattr(system, key):
                    old_value = getattr(system, key)
                    if old_value != new_value:
                        # 이력 기록
                        record_history(
                            system_id=system_id,
                            field_name=key,
                            old_value=str(old_value) if old_value is not None else '',
                            new_value=str(new_value) if new_value is not None else '',
                            changed_by=changed_by
                        )
                        setattr(system, key, new_value)

            system.updated_at = datetime.now()
            session.commit()
            return True
        return False
    finally:
        session.close()


def delete_system(system_id, deleted_by=''):
    """시스템 삭제 (소프트 삭제)"""
    session = get_session()
    try:
        system = session.query(System).filter(System.id == system_id).first()
        if system:
            system.is_deleted = True
            system.updated_at = datetime.now()
            session.commit()

            record_history(
                system_id=system_id,
                field_name='deleted',
                old_value='active',
                new_value='deleted',
                changed_by=deleted_by
            )
            return True
        return False
    finally:
        session.close()


# ============== 서비스 CRUD ==============

def get_all_services():
    """모든 서비스 조회"""
    session = get_session()
    try:
        services = session.query(Service).order_by(Service.monthly_cost.desc()).all()
        return [s.to_dict() for s in services]
    finally:
        session.close()


def create_service(data):
    """서비스 생성"""
    session = get_session()
    try:
        service = Service(
            service_name=data.get('service_name'),
            plan_type=data.get('plan_type'),
            monthly_cost=data.get('monthly_cost', 0.0),
            currency=data.get('currency', 'USD'),
            renewal_date=data.get('renewal_date'),
            payment_method=data.get('payment_method'),
            notes=data.get('notes')
        )
        session.add(service)
        session.commit()
        return service.id
    finally:
        session.close()


def update_service(service_id, data):
    """서비스 수정"""
    session = get_session()
    try:
        service = session.query(Service).filter(Service.id == service_id).first()
        if service:
            for key, value in data.items():
                if hasattr(service, key):
                    setattr(service, key, value)
            service.updated_at = datetime.now()
            session.commit()
            return True
        return False
    finally:
        session.close()


def delete_service(service_id):
    """서비스 삭제"""
    session = get_session()
    try:
        service = session.query(Service).filter(Service.id == service_id).first()
        if service:
            session.delete(service)
            session.commit()
            return True
        return False
    finally:
        session.close()


# ============== 이력 관리 ==============

def get_system_history(system_id):
    """시스템 변경 이력 조회"""
    session = get_session()
    try:
        history = session.query(SystemHistory)\
            .filter(SystemHistory.system_id == system_id)\
            .order_by(SystemHistory.changed_at.desc())\
            .all()
        return [h.to_dict() for h in history]
    finally:
        session.close()


def record_history(system_id, field_name, old_value, new_value, changed_by='', comment=''):
    """변경 이력 기록"""
    session = get_session()
    try:
        history = SystemHistory(
            system_id=system_id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by,
            comment=comment
        )
        session.add(history)
        session.commit()
    finally:
        session.close()


# ============== 대시보드 통계 ==============

def get_dashboard_stats():
    """대시보드용 통계 데이터"""
    session = get_session()
    try:
        # 전체 시스템 수
        total = session.query(func.count(System.id))\
            .filter(System.is_deleted == False).scalar()

        # 상태별 시스템 수
        status_counts = {}
        for status in ['초기 개발', '개발 중', '테스트 필요', '운영 가능']:
            count = session.query(func.count(System.id))\
                .filter(System.is_deleted == False, System.status == status).scalar()
            status_counts[status] = count

        # 이번 달 신규 등록
        first_day = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_this_month = session.query(func.count(System.id))\
            .filter(System.is_deleted == False, System.created_at >= first_day).scalar()

        # 평균 진행률
        avg_progress = session.query(func.avg(System.progress))\
            .filter(System.is_deleted == False).scalar() or 0

        # 부서별 시스템 분포
        systems = session.query(System).filter(System.is_deleted == False).all()
        dept_distribution = {}
        for system in systems:
            if system.departments:
                for dept in system.departments:
                    dept_distribution[dept] = dept_distribution.get(dept, 0) + 1

        # 최근 수정된 시스템 (최근 5개)
        recent_systems = session.query(System)\
            .filter(System.is_deleted == False)\
            .order_by(System.updated_at.desc())\
            .limit(5)\
            .all()

        recent_updates = [{
            'system_name': s.system_name,
            'status': s.status,
            'progress': s.progress * 100,
            'updated_at': s.updated_at.strftime('%Y-%m-%d %H:%M') if s.updated_at else ''
        } for s in recent_systems]

        # 주의 필요 시스템 (진행률 30% 미만 또는 30일 이상 미업데이트)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        alert_systems = session.query(System)\
            .filter(
                System.is_deleted == False,
                ((System.progress < 0.3) | (System.updated_at < thirty_days_ago))
            )\
            .all()

        alerts = [{
            'system_name': s.system_name,
            'status': s.status,
            'progress': s.progress * 100,
            'updated_at': s.updated_at.strftime('%Y-%m-%d') if s.updated_at else '',
            'reason': '진행률 30% 미만' if s.progress < 0.3 else '30일 이상 미업데이트'
        } for s in alert_systems]

        # 완료 임박 시스템 (진행률 90% 이상)
        upcoming = session.query(System)\
            .filter(System.is_deleted == False, System.progress >= 0.9, System.status != '운영 가능')\
            .all()

        upcoming_systems = [{
            'system_name': s.system_name,
            'status': s.status,
            'progress': s.progress * 100,
            'target_date': s.target_date.strftime('%Y-%m-%d') if s.target_date else ''
        } for s in upcoming]

        # 서비스 총 비용
        services = session.query(Service).all()
        total_cost = sum(s.monthly_cost for s in services)

        return {
            'total': total,
            'status_counts': status_counts,
            'production': status_counts.get('운영 가능', 0),
            'developing': status_counts.get('개발 중', 0),
            'production_rate': status_counts.get('운영 가능', 0) / total if total > 0 else 0,
            'new_this_month': new_this_month,
            'avg_progress': avg_progress,
            'progress_change': 0,  # 이전 달 대비 변화량 (추후 구현)
            'dept_distribution': dept_distribution,
            'recent_updates': recent_updates,
            'alert_systems': alerts,
            'upcoming_systems': upcoming_systems,
            'total_cost': total_cost,
            'monthly_costs': []  # 월별 비용 추이 (추후 구현)
        }
    finally:
        session.close()


def get_all_departments():
    """모든 부서 목록 반환"""
    session = get_session()
    try:
        systems = session.query(System).filter(System.is_deleted == False).all()
        departments = set()
        for system in systems:
            if system.departments:
                departments.update(system.departments)
        return sorted(list(departments))
    finally:
        session.close()


def get_all_platforms(platform_type='frontend'):
    """모든 플랫폼 목록 반환"""
    session = get_session()
    try:
        systems = session.query(System).filter(System.is_deleted == False).all()
        platforms = set()
        for system in systems:
            if platform_type == 'frontend' and system.frontend_platform:
                platforms.add(system.frontend_platform)
            elif platform_type == 'backend' and system.backend_platform:
                platforms.add(system.backend_platform)
        return sorted(list(platforms))
    finally:
        session.close()


# 앱 시작 시 DB 초기화
init_db()
