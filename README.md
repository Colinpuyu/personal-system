# Personal System

一个基于 Flask + SQLAlchemy 的个人产品管理系统，用于整理知识库、公司与项目管理、文档归档以及基础的分析埋点。

## 功能概览

- 知识库管理：创建、编辑、搜索、筛选（来源、标签、关键词）
- 公司与项目管理：公司列表与详情、项目增删改查、文档关联
- 文档管理：上传路径记录与文档类型标注
- 全局搜索：跨知识库、项目、文档的统一查询
- 数据埋点：搜索、浏览等行为记录

## 技术栈

- `Flask` Web 框架
- `Flask-SQLAlchemy` ORM
- 数据库：默认 SQLite（`instance/personal_system.db`）
- `python-dotenv` 配置加载
- 前端：Bootstrap 5 + Jinja2 模板

## 目录结构

```
personal-system/
├── app.py                 # 应用入口、蓝图注册、错误页处理
├── config.py              # 配置（通过 .env 读取）
├── models.py              # 数据模型定义（KnowledgeBase、Company、Project、Document、Analytics）
├── routes/                # 业务路由蓝图
│   ├── product_space.py   # 产品空间（知识库、能力图等）
│   └── company_projects.py# 公司与项目相关路由
├── templates/             # 页面模板
│   ├── base.html
│   ├── index.html
│   ├── product/
│   │   ├── knowledge_list.html
│   │   ├── knowledge_form.html
│   │   └── capability_map.html
│   └── company/
│       ├── company_list.html
│       ├── company_detail.html
│       ├── project_form.html
│       └── project_detail.html
├── instance/personal_system.db # 默认 SQLite 数据库
├── requirements.txt       # 依赖清单
├── init_db.py             # 数据库初始化脚本（可选）
├── validate_html.py       # HTML 语法校验辅助脚本
├── validate_jinja_html.py # Jinja 模板校验辅助脚本
└── comprehensive_html_report.py # 模板全面报告生成脚本
```

## 安装与运行

1) 环境准备（推荐 Python 3.10+）：

```
python3 -m venv venv
source venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
```

2) 配置 `.env`（可选）：

在 `personal-system/.env` 中设置数据库和调试参数，例如：

```
FLASK_ENV=development
SQLALCHEMY_DATABASE_URI=sqlite:///instance/personal_system.db
SQLALCHEMY_TRACK_MODIFICATIONS=False
SECRET_KEY=your_secret_key_here
```

如未设置，`config.py` 会使用默认开发配置。

3) 初始化数据库（如未自动创建或需要清空重建）：

```
python init_db.py
```

4) 启动服务：

```
python app.py
```

- 默认监听：`http://0.0.0.0:5002/`
- 主页：`/` 显示统计与最近内容

## 主要路由

- 产品空间（前缀 `/_product` 在代码中为 `/product`）
  - `GET /product/knowledge` 知识库列表（支持 `search`、`source`、`tag` 筛选）
  - `GET /product/knowledge/new` 新建知识库
  - `POST /product/knowledge/new` 提交新建
  - `GET /product/knowledge/<id>/edit` 编辑知识库
  - `POST /product/knowledge/<id>/edit` 提交编辑
  - `GET /product/capability-map` 能力图/能力地图页面

- 公司与项目（前缀 `/company`）
  - `GET /company/` 公司列表
  - `GET /company/<company_id>` 公司详情（含项目列表与筛选）
  - `GET /company/<company_id>/projects/new` 新建项目
  - `POST /company/<company_id>/projects/new` 提交新建
  - `GET /company/projects/<project_id>` 项目详情
  - `GET /company/projects/<project_id>/edit` 编辑项目
  - `POST /company/projects/<project_id>/edit` 提交编辑
  - 文档相关：`/company/projects/<project_id>/documents/...`

- 全局搜索
  - `GET /search?q=关键词` 返回知识库、项目、文档综合结果

## 数据模型

- `KnowledgeBase`
  - 主要字段：`title`、`content`、`tags(JSON string)`、`source(Enum: 会议/课程/竞品/灵感)`、`confidence(1-5)`、`access_count`
  - 方法：`get_tags_list()`、`set_tags_list()`、`to_dict()`

- `Company`
  - 字段：`name`、`description`
  - 关系：`projects`（一对多）

- `Project`
  - 字段：`name`、`description`、`status(Enum)`、`company_id`
  - 关系：`documents`（一对多）

- `Document`
  - 字段：`title`、`file_path`、`document_type(Enum)`、`project_id`

- `Analytics`
  - 记录事件：`event_type`、`entity_id`、`entity_type`、`search_query`、`timestamp`
  - 静态方法：`track_event(...)` 直接写库

## 前端与模板说明

- 使用 Bootstrap 5 配合 Jinja2 模板渲染
- 表单与筛选：知识库列表的 `search/source/tag` 采用 GET 提交，互相保留条件
- 编辑与新建表单：根据是否传入 `knowledge` 切换标题与 `action`
- 能力图页面：`product/capability_map.html`

## 常用脚本

- HTML/Jinja 校验：
  - `python validate_html.py`
  - `python validate_jinja_html.py`
- 模板报告：
  - `python comprehensive_html_report.py`

## 开发建议与注意事项

- 变更模型后请重新初始化或迁移数据库
- 提交表单前端有草稿自动保存逻辑（本地存储），编辑模式建议避免覆盖已有内容
- 枚举值（如 `source`、`project_status`、`document_types`）需与模板和表单保持一致

## 未来改进方向（建议）

- 知识库标签改用关联表；支持高亮搜索命中
- 公司/项目页增加分页、排序与更丰富的筛选
- 文档上传集成文件存储与预览
- 埋点分析可视化看板

## 许可证

未指定许可证。若需开源分发，请根据需求添加。