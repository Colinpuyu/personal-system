#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表和初始化数据
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, KnowledgeBase, Company, Project, Document, Analytics

def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    app = create_app('development')
    
    with app.app_context():
        try:
            # 创建所有表
            print("创建数据库表...")
            db.create_all()
            print("数据库表创建成功！")
            
            # 检查是否已有数据
            if KnowledgeBase.query.first() or Company.query.first():
                print("检测到已有数据，跳过初始化数据步骤")
                return
            
            # 初始化示例数据
            print("初始化示例数据...")
            
            # 创建示例知识库条目
            sample_knowledge = [
                KnowledgeBase(
                    title="产品规划最佳实践",
                    content="""产品规划是产品开发过程中的关键环节，需要综合考虑市场需求、技术可行性、资源配置等多个因素。

关键步骤：
1. 市场调研：深入了解目标用户需求
2. 竞品分析：分析竞争对手的产品特点
3. 功能规划：制定产品功能清单
4. 时间规划：制定开发时间表
5. 资源评估：评估所需资源

注意事项：
- 保持规划的灵活性
- 定期回顾和调整
- 与团队成员充分沟通""",
                    source="会议",
                    confidence=4
                ),
                KnowledgeBase(
                    title="用户体验设计原则",
                    content="""用户体验设计是现代产品设计的核心，直接影响产品的用户接受度和市场表现。

设计原则：
1. 以用户为中心：始终考虑用户需求
2. 简洁明了：界面设计要简洁
3. 一致性：保持界面元素的一致性
4. 反馈及时：及时响应用户操作
5. 容错性：允许用户犯错并容易恢复

评估方法：
- 用户测试
- A/B测试
- 数据分析""",
                    source="课程",
                    confidence=5
                ),
                KnowledgeBase(
                    title="敏捷开发方法论",
                    content="""敏捷开发是一种以人为核心、迭代、循序渐进的方法。

价值观：
- 个体和互动高于流程和工具
- 工作的软件高于详尽的文档
- 客户合作高于合同谈判
- 响应变化高于遵循计划

常用实践：
1. 每日站会
2. 迭代开发
3. 持续集成
4. 测试驱动开发
5. 代码审查""",
                    source="灵感",
                    confidence=3
                )
            ]
            
            # 添加知识库条目并设置标签
            sample_knowledge[0].set_tags_list(['产品规划', '最佳实践', '方法论'])
            sample_knowledge[1].set_tags_list(['UX', '用户体验', '设计原则'])
            sample_knowledge[2].set_tags_list(['敏捷开发', '方法论', 'Scrum'])
            
            for knowledge in sample_knowledge:
                db.session.add(knowledge)
            
            # 创建示例公司
            sample_companies = [
                Company(
                    name="科技创新有限公司",
                    description="专注于人工智能和大数据技术的创新公司",
                    created_at=datetime.utcnow()
                ),
                Company(
                    name="互联网科技集团",
                    description="提供互联网服务和解决方案的大型企业",
                    created_at=datetime.utcnow()
                )
            ]
            
            for company in sample_companies:
                db.session.add(company)
            
            db.session.flush()  # 确保公司ID生成
            
            # 创建示例项目
            sample_projects = [
                Project(
                    name="智能客服系统",
                    description="基于人工智能的智能客服系统开发项目",
                    status="进行中",
                    company_id=sample_companies[0].id
                ),
                Project(
                    name="移动应用开发",
                    description="公司移动端应用开发项目",
                    status="计划中",
                    company_id=sample_companies[1].id
                ),
                Project(
                    name="数据分析平台",
                    description="企业级数据分析平台建设项目",
                    status="已完成",
                    company_id=sample_companies[0].id
                )
            ]
            
            for project in sample_projects:
                db.session.add(project)
            
            db.session.flush()  # 确保项目ID生成
            
            # 创建示例文档
            sample_documents = [
                Document(
                    title="项目需求文档",
                    document_type="文档",
                    project_id=sample_projects[0].id
                ),
                Document(
                    title="技术方案设计",
                    document_type="文档",
                    project_id=sample_projects[0].id
                ),
                Document(
                    title="用户界面设计",
                    document_type="设计稿",
                    project_id=sample_projects[1].id
                )
            ]
            
            for document in sample_documents:
                db.session.add(document)
            
            # 提交所有更改
            db.session.commit()
            print("示例数据初始化完成！")
            
            # 打印统计信息
            print("\n数据库初始化完成！")
            print(f"知识库条目数: {KnowledgeBase.query.count()}")
            print(f"公司数: {Company.query.count()}")
            print(f"项目数: {Project.query.count()}")
            print(f"文档数: {Document.query.count()}")
            
        except Exception as e:
            print(f"初始化过程中出现错误: {e}")
            db.session.rollback()
            raise

def reset_database():
    """重置数据库（谨慎使用）"""
    print("警告：这将删除所有数据！")
    confirm = input("确定要继续吗？输入 'yes' 确认: ")
    
    if confirm.lower() == 'yes':
        app = create_app('development')
        with app.app_context():
            try:
                print("正在删除所有表...")
                db.drop_all()
                print("正在重新创建表...")
                db.create_all()
                print("数据库重置完成！")
            except Exception as e:
                print(f"重置过程中出现错误: {e}")
                db.session.rollback()
                raise
    else:
        print("操作已取消")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库初始化工具')
    parser.add_argument('--reset', action='store_true', help='重置数据库（删除所有数据）')
    
    args = parser.parse_args()
    
    if args.reset:
        reset_database()
    else:
        init_database()