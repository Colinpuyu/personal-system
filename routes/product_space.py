from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models import db, KnowledgeBase, Analytics
from datetime import datetime
import json

product_space_bp = Blueprint('product_space', __name__)

@product_space_bp.route('/knowledge')
def knowledge_list():
    """知识库列表页面"""
    # 获取筛选参数
    source = request.args.get('source')
    tag = request.args.get('tag')
    
    # 基础查询
    query = KnowledgeBase.query
    
    # 应用筛选
    if source:
        query = query.filter_by(source=source)
    
    if tag:
        # 标签筛选 - 使用 LIKE 来匹配数组中的标签
        query = query.filter(KnowledgeBase.tags.contains(f'"{tag}"'))
    
    # 获取所有知识条目
    knowledge_items = query.order_by(KnowledgeBase.created_at.desc()).all()
    
    # 获取所有可用的标签和来源用于筛选
    all_tags = set()
    all_sources = set()
    
    for item in KnowledgeBase.query.all():
        all_tags.update(item.get_tags_list())
        if item.source:
            all_sources.add(item.source)
    
    return render_template('product/knowledge_list.html',
                         knowledge_items=knowledge_items,
                         all_tags=sorted(all_tags),
                         all_sources=sorted(all_sources))

@product_space_bp.route('/knowledge/new', methods=['GET', 'POST'])
def knowledge_new():
    """创建新知识条目"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        tags = request.form.get('tags', '').split(',')
        source = request.form.get('source')
        confidence = int(request.form.get('confidence', 3))
        
        # 清理标签
        tags = [tag.strip() for tag in tags if tag.strip()]
        
        # 创建新条目
        knowledge = KnowledgeBase(
            title=title,
            content=content,
            source=source,
            confidence=confidence
        )
        knowledge.set_tags_list(tags)
        
        db.session.add(knowledge)
        db.session.commit()
        
        # 记录创建事件
        Analytics.track_event('note_create', entity_id=knowledge.id, entity_type='knowledge_base')
        
        flash('知识条目创建成功！', 'success')
        return redirect(url_for('product_space.knowledge_detail', id=knowledge.id))
    
    return render_template('product/knowledge_form.html')

@product_space_bp.route('/knowledge/<int:id>')
def knowledge_detail(id):
    """知识条目详情页面"""
    knowledge = KnowledgeBase.query.get_or_404(id)
    
    # 增加访问计数
    knowledge.access_count += 1
    db.session.commit()
    
    # 记录查看事件
    Analytics.track_event('note_view', entity_id=id, entity_type='knowledge_base')
    
    return render_template('product/knowledge_detail.html', knowledge=knowledge)

@product_space_bp.route('/knowledge/<int:id>/edit', methods=['GET', 'POST'])
def knowledge_edit(id):
    """编辑知识条目"""
    knowledge = KnowledgeBase.query.get_or_404(id)
    
    if request.method == 'POST':
        knowledge.title = request.form.get('title')
        knowledge.content = request.form.get('content')
        tags = request.form.get('tags', '').split(',')
        knowledge.source = request.form.get('source')
        knowledge.confidence = int(request.form.get('confidence', 3))
        
        # 清理标签
        tags = [tag.strip() for tag in tags if tag.strip()]
        knowledge.set_tags_list(tags)
        
        knowledge.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('知识条目更新成功！', 'success')
        return redirect(url_for('product_space.knowledge_detail', id=id))
    
    return render_template('product/knowledge_form.html', knowledge=knowledge)

@product_space_bp.route('/knowledge/<int:id>/delete', methods=['POST'])
def knowledge_delete(id):
    """删除知识条目"""
    knowledge = KnowledgeBase.query.get_or_404(id)
    
    db.session.delete(knowledge)
    db.session.commit()
    
    flash('知识条目已删除！', 'success')
    return redirect(url_for('product_space.knowledge_list'))

@product_space_bp.route('/api/knowledge/search')
def api_knowledge_search():
    """知识库搜索 API"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify([])
    
    # 搜索知识条目
    results = KnowledgeBase.query.filter(
        (KnowledgeBase.title.contains(query)) |
        (KnowledgeBase.content.contains(query))
    ).limit(10).all()
    
    # 转换为 JSON 格式
    data = [item.to_dict() for item in results]
    
    # 记录搜索事件
    Analytics.track_event('search', search_query=query)
    
    return jsonify(data)

@product_space_bp.route('/capability-map')
def capability_map():
    """能力地图页面"""
    # 获取所有知识条目，按标签分组
    knowledge_items = KnowledgeBase.query.all()
    
    # 按标签组织数据
    capability_data = {}
    
    for item in knowledge_items:
        tags = item.get_tags_list()
        for tag in tags:
            if tag not in capability_data:
                capability_data[tag] = []
            capability_data[tag].append({
                'id': item.id,
                'title': item.title,
                'confidence': item.confidence,
                'created_at': item.created_at.isoformat()
            })
    
    return render_template('product/capability_map.html', capability_data=capability_data)