from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models import db, Company, Project, Document, Analytics
from werkzeug.utils import secure_filename
import os
from datetime import datetime

company_projects_bp = Blueprint('company_projects', __name__)

@company_projects_bp.route('/')
def company_list():
    """公司列表页面"""
    companies = Company.query.order_by(Company.name).all()
    return render_template('company/company_list.html', companies=companies)

@company_projects_bp.route('/<int:company_id>')
def company_detail(company_id):
    """公司详情页面"""
    company = Company.query.get_or_404(company_id)
    
    # 获取项目状态筛选
    status = request.args.get('status')
    
    # 基础查询
    projects_query = Project.query.filter_by(company_id=company_id)
    
    # 应用状态筛选
    if status:
        projects_query = projects_query.filter_by(status=status)
    
    projects = projects_query.order_by(Project.created_at.desc()).all()
    
    return render_template('company/company_detail.html', 
                         company=company, 
                         projects=projects)

@company_projects_bp.route('/<int:company_id>/projects/new', methods=['GET', 'POST'])
def project_new(company_id):
    """创建新项目"""
    company = Company.query.get_or_404(company_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        status = request.form.get('status', '计划中')
        
        project = Project(
            name=name,
            description=description,
            status=status,
            company_id=company_id
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash('项目创建成功！', 'success')
        return redirect(url_for('company_projects.project_detail', 
                              company_id=company_id, 
                              project_id=project.id))
    
    return render_template('company/project_form.html', company=company)

@company_projects_bp.route('/<int:company_id>/projects/<int:project_id>')
def project_detail(company_id, project_id):
    """项目详情页面"""
    company = Company.query.get_or_404(company_id)
    project = Project.query.get_or_404(project_id)
    
    # 确保项目属于该公司
    if project.company_id != company_id:
        flash('项目不存在', 'error')
        return redirect(url_for('company_projects.company_list'))
    
    # 获取项目文档
    documents = Document.query.filter_by(project_id=project_id).order_by(Document.created_at.desc()).all()
    
    return render_template('company/project_detail.html',
                         company=company,
                         project=project,
                         documents=documents)

@company_projects_bp.route('/<int:company_id>/projects/<int:project_id>/edit', methods=['GET', 'POST'])
def project_edit(company_id, project_id):
    """编辑项目"""
    company = Company.query.get_or_404(company_id)
    project = Project.query.get_or_404(project_id)
    
    # 确保项目属于该公司
    if project.company_id != company_id:
        flash('项目不存在', 'error')
        return redirect(url_for('company_projects.company_list'))
    
    if request.method == 'POST':
        project.name = request.form.get('name')
        project.description = request.form.get('description')
        project.status = request.form.get('status')
        project.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('项目更新成功！', 'success')
        return redirect(url_for('company_projects.project_detail',
                              company_id=company_id,
                              project_id=project_id))
    
    return render_template('company/project_form.html', company=company, project=project)

@company_projects_bp.route('/<int:company_id>/projects/<int:project_id>/documents/new', methods=['GET', 'POST'])
def document_new(company_id, project_id):
    """上传新文档"""
    company = Company.query.get_or_404(company_id)
    project = Project.query.get_or_404(project_id)
    
    # 确保项目属于该公司
    if project.company_id != company_id:
        flash('项目不存在', 'error')
        return redirect(url_for('company_projects.company_list'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        document_type = request.form.get('document_type', '文档')
        
        # 处理文件上传
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                filename = secure_filename(file.filename)
                upload_folder = os.path.join('uploads', str(project_id))
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                
                document = Document(
                    title=title,
                    file_path=file_path,
                    document_type=document_type,
                    project_id=project_id
                )
                
                db.session.add(document)
                db.session.commit()
                
                # 记录文档上传事件
                Analytics.track_event('file_upload', entity_id=document.id, entity_type='document')
                
                flash('文档上传成功！', 'success')
                return redirect(url_for('company_projects.project_detail',
                                      company_id=company_id,
                                      project_id=project_id))
        
        # 如果没有文件，创建纯文本文档
        document = Document(
            title=title,
            document_type=document_type,
            project_id=project_id
        )
        
        db.session.add(document)
        db.session.commit()
        
        flash('文档创建成功！', 'success')
        return redirect(url_for('company_projects.project_detail',
                              company_id=company_id,
                              project_id=project_id))
    
    return render_template('company/document_form.html', company=company, project=project)

@company_projects_bp.route('/<int:company_id>/projects/<int:project_id>/documents/<int:document_id>')
def document_detail(company_id, project_id, document_id):
    """文档详情页面"""
    company = Company.query.get_or_404(company_id)
    project = Project.query.get_or_404(project_id)
    document = Document.query.get_or_404(document_id)
    
    # 确保文档属于该项目和该公司
    if document.project_id != project_id or project.company_id != company_id:
        flash('文档不存在', 'error')
        return redirect(url_for('company_projects.company_list'))
    
    # 记录文档查看事件
    Analytics.track_event('file_open', entity_id=document_id, entity_type='document')
    
    return render_template('company/document_detail.html',
                         company=company,
                         project=project,
                         document=document)

@company_projects_bp.route('/api/companies/search')
def api_companies_search():
    """公司搜索 API"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify([])
    
    # 搜索公司
    results = Company.query.filter(
        Company.name.contains(query)
    ).limit(10).all()
    
    # 转换为 JSON 格式
    data = [{
        'id': company.id,
        'name': company.name,
        'description': company.description
    } for company in results]
    
    return jsonify(data)

@company_projects_bp.route('/api/projects/search')
def api_projects_search():
    """项目搜索 API"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify([])
    
    # 搜索项目
    results = Project.query.filter(
        (Project.name.contains(query)) |
        (Project.description.contains(query))
    ).limit(10).all()
    
    # 转换为 JSON 格式
    data = [{
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'status': project.status,
        'company_name': project.company.name
    } for project in results]
    
    return jsonify(data)

@company_projects_bp.route('/api/companies', methods=['POST'])
def api_company_create():
    """创建新公司 API"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'success': False, 'error': '公司名称不能为空'}), 400
        
        # 检查公司名称是否已存在
        existing_company = Company.query.filter_by(name=data['name']).first()
        if existing_company:
            return jsonify({'success': False, 'error': '该公司名称已存在'}), 400
        
        company = Company(
            name=data['name'],
            description=data.get('description', '')
        )
        
        db.session.add(company)
        db.session.commit()
        
        return jsonify({'success': True, 'id': company.id})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@company_projects_bp.route('/api/companies/<int:company_id>')
def api_company_detail(company_id):
    """获取公司详情 API"""
    company = Company.query.get_or_404(company_id)
    
    return jsonify({
        'id': company.id,
        'name': company.name,
        'description': company.description,
        'created_at': company.created_at.isoformat() if company.created_at else None
    })

@company_projects_bp.route('/api/companies/<int:company_id>', methods=['PUT'])
def api_company_update(company_id):
    """更新公司信息 API"""
    try:
        company = Company.query.get_or_404(company_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': '请求数据不能为空'}), 400
        
        # 如果名称被修改，检查新名称是否已存在
        if data.get('name') and data['name'] != company.name:
            existing_company = Company.query.filter_by(name=data['name']).first()
            if existing_company:
                return jsonify({'success': False, 'error': '该公司名称已存在'}), 400
        
        company.name = data.get('name', company.name)
        company.description = data.get('description', company.description)
        
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@company_projects_bp.route('/api/companies/<int:company_id>', methods=['DELETE'])
def api_company_delete(company_id):
    """删除公司 API"""
    try:
        company = Company.query.get_or_404(company_id)
        
        # 删除公司时，级联删除所有相关项目和文档
        for project in company.projects:
            # 删除项目的所有文档
            for document in project.documents:
                db.session.delete(document)
            db.session.delete(project)
        
        db.session.delete(company)
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@company_projects_bp.route('/api/projects/<int:project_id>', methods=['DELETE'])
def api_project_delete(project_id):
    """删除项目 API"""
    try:
        project = Project.query.get_or_404(project_id)
        company_id = project.company_id
        
        # 删除项目时，级联删除所有相关文档
        for document in project.documents:
            # 如果文档有文件路径，删除物理文件
            if document.file_path and os.path.exists(document.file_path):
                try:
                    os.remove(document.file_path)
                except Exception as e:
                    print(f"删除文件失败: {e}")
            db.session.delete(document)
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@company_projects_bp.route('/api/documents/<int:document_id>', methods=['DELETE'])
def api_document_delete(document_id):
    """删除文档 API"""
    try:
        document = Document.query.get_or_404(document_id)
        
        # 如果文档有文件路径，删除物理文件
        if document.file_path and os.path.exists(document.file_path):
            try:
                os.remove(document.file_path)
            except Exception as e:
                print(f"删除文件失败: {e}")
        
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500