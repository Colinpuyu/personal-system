from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Enum
import json

db = SQLAlchemy()

class KnowledgeBase(db.Model):
    __tablename__ = 'knowledge_base'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(500))  # JSON array stored as string
    source = db.Column(db.Enum('会议', '课程', '竞品', '灵感', name='source_types'))
    confidence = db.Column(db.Integer, default=3)  # 1-5 scale
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    access_count = db.Column(db.Integer, default=0)  # 用于数据埋点和缓存
    
    def get_tags_list(self):
        """将标签字符串转换为列表"""
        if self.tags:
            return json.loads(self.tags)
        return []
    
    def set_tags_list(self, tags_list):
        """将标签列表转换为字符串"""
        self.tags = json.dumps(tags_list, ensure_ascii=False)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'tags': self.get_tags_list(),
            'source': self.source,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'access_count': self.access_count
        }

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    projects = db.relationship('Project', backref='company', lazy=True)

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum('进行中', '已完成', '暂停', '计划中', name='project_status'))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    documents = db.relationship('Document', backref='project', lazy=True)

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500))
    document_type = db.Column(db.Enum('文档', '设计稿', '会议纪要', name='document_types'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'file_path': self.file_path,
            'document_type': self.document_type,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# 数据埋点模型
class Analytics(db.Model):
    __tablename__ = 'analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)  # 'note_view', 'search', 'file_open'
    entity_id = db.Column(db.Integer)  # 关联的实体ID
    entity_type = db.Column(db.String(50))  # 'knowledge_base', 'document'
    search_query = db.Column(db.String(200))  # 搜索关键词
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def track_event(event_type, entity_id=None, entity_type=None, search_query=None):
        """记录事件"""
        analytics = Analytics(
            event_type=event_type,
            entity_id=entity_id,
            entity_type=entity_type,
            search_query=search_query
        )
        db.session.add(analytics)
        db.session.commit()