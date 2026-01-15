from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class System(Base):
    """개발 시스템 모델"""
    __tablename__ = 'systems'

    id = Column(Integer, primary_key=True, autoincrement=True)
    system_name = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    url = Column(String(500))
    departments = Column(JSON)  # ["생산기획팀", "개발팀"]
    progress = Column(Float, default=0.0)
    status = Column(String(50), nullable=False, index=True)

    frontend_platform = Column(String(100))
    frontend_plan = Column(String(100))
    backend_platform = Column(String(100))
    backend_plan = Column(String(100))
    api_info = Column(String(200))

    owner = Column(String(100))
    start_date = Column(Date)
    target_date = Column(Date)
    notes = Column(Text)

    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'system_name': self.system_name,
            'description': self.description,
            'url': self.url,
            'departments': self.departments or [],
            'progress': self.progress,
            'status': self.status,
            'frontend_platform': self.frontend_platform,
            'frontend_plan': self.frontend_plan,
            'backend_platform': self.backend_platform,
            'backend_plan': self.backend_plan,
            'api_info': self.api_info,
            'owner': self.owner,
            'start_date': self.start_date,
            'target_date': self.target_date,
            'notes': self.notes,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by
        }


class SystemHistory(Base):
    """시스템 변경 이력 모델"""
    __tablename__ = 'system_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    system_id = Column(Integer, nullable=False, index=True)
    field_name = Column(String(100))
    old_value = Column(Text)
    new_value = Column(Text)
    changed_by = Column(String(100))
    changed_at = Column(DateTime, default=datetime.now, index=True)
    comment = Column(Text)

    def to_dict(self):
        return {
            'id': self.id,
            'system_id': self.system_id,
            'field_name': self.field_name,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'changed_by': self.changed_by,
            'changed_at': self.changed_at,
            'comment': self.comment
        }


class Service(Base):
    """서비스 비용 모델"""
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(String(100), unique=True, nullable=False)
    plan_type = Column(String(100))
    monthly_cost = Column(Float, default=0.0)
    currency = Column(String(10), default='USD')
    renewal_date = Column(Date)
    payment_method = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'service_name': self.service_name,
            'plan_type': self.plan_type,
            'monthly_cost': self.monthly_cost,
            'currency': self.currency,
            'renewal_date': self.renewal_date,
            'payment_method': self.payment_method,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class Attachment(Base):
    """첨부 파일 모델"""
    __tablename__ = 'attachments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    system_id = Column(Integer, nullable=False, index=True)
    file_name = Column(String(500))
    file_path = Column(String(1000))
    file_size = Column(Integer)
    uploaded_by = Column(String(100))
    uploaded_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'system_id': self.system_id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'uploaded_by': self.uploaded_by,
            'uploaded_at': self.uploaded_at
        }


class Comment(Base):
    """댓글 모델"""
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    system_id = Column(Integer, nullable=False, index=True)
    content = Column(Text, nullable=False)
    author = Column(String(100))
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'system_id': self.system_id,
            'content': self.content,
            'author': self.author,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
