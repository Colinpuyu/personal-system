from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from config import config
from models import db, KnowledgeBase, Company, Project, Document, Analytics
import os

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册蓝图
    from routes.product_space import product_space_bp
    from routes.company_projects import company_projects_bp
    
    app.register_blueprint(product_space_bp, url_prefix='/product')
    app.register_blueprint(company_projects_bp, url_prefix='/company')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def index():
        """主页 - 显示概览"""
        # 统计数据
        stats = {
            'knowledge_count': KnowledgeBase.query.count(),
            'company_count': Company.query.count(),
            'project_count': Project.query.count(),
            'document_count': Document.query.count(),
        }

        # 最新知识库与项目
        recent_knowledge = KnowledgeBase.query.order_by(KnowledgeBase.created_at.desc()).limit(5).all()
        recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()

        # 最近活动（基于 Analytics 埋点）
        recent_activities_raw = Analytics.query.order_by(Analytics.timestamp.desc()).limit(5).all()
        recent_activities = []
        for evt in recent_activities_raw:
            item = {
                'title': '系统活动',
                'description': '',
                'icon': 'activity',
                'type': evt.event_type,
                'time': evt.timestamp.strftime('%Y-%m-%d %H:%M') if evt.timestamp else ''
            }
            if evt.event_type == 'search':
                item.update({
                    'title': f"搜索: {evt.search_query or ''}",
                    'description': '执行了一次搜索',
                    'icon': 'search',
                    'type': '搜索'
                })
            elif evt.event_type == 'file_open':
                item.update({
                    'title': f"查看文档 #{evt.entity_id}",
                    'description': '打开了文档',
                    'icon': 'file-text',
                    'type': '文档'
                })
            elif evt.event_type == 'note_view':
                item.update({
                    'title': f"查看知识库 #{evt.entity_id}",
                    'description': '查看了知识条目',
                    'icon': 'book',
                    'type': '知识库'
                })
            elif evt.event_type == 'note_create':
                item.update({
                    'title': f"创建知识库 #{evt.entity_id}",
                    'description': '创建了知识条目',
                    'icon': 'plus-circle',
                    'type': '知识库'
                })
            recent_activities.append(item)

        return render_template(
            'index.html',
            stats=stats,
            recent_knowledge=recent_knowledge,
            recent_projects=recent_projects,
            recent_activities=recent_activities,
        )
    
    @app.route('/search')
    def search():
        """全局搜索功能"""
        query = request.args.get('q', '')
        
        if query:
            # 记录搜索事件
            Analytics.track_event('search', search_query=query)
            
            # 搜索知识库
            knowledge_results = KnowledgeBase.query.filter(
                (KnowledgeBase.title.contains(query)) |
                (KnowledgeBase.content.contains(query))
            ).all()
            
            # 搜索项目
            project_results = Project.query.filter(
                (Project.name.contains(query)) |
                (Project.description.contains(query))
            ).all()
            
            # 搜索文档
            document_results = Document.query.filter(
                (Document.title.contains(query))
            ).all()
            
            return render_template('search_results.html',
                                 query=query,
                                 knowledge_results=knowledge_results,
                                 project_results=project_results,
                                 document_results=document_results)
        
        return render_template('search.html')
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5001)