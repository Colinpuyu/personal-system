personal-system/
├── docs/
│   ├── PROJECT_PROPOSAL.md   # 立项文档
│   └── PRD.md                # 产品需求文档
├── app.py                    # 应用入口（MySQL配置）
├── config.py                 # 环境配置
├── models.py                 # MySQL数据模型
├── routes/
│   ├── __init__.py
│   ├── product_space.py      # 产品经理模块路由
│   └── company_projects.py   # 公司项目模块路由
├── templates/                # HTMX前端模板
├── .env.example              # 环境变量模板
└── requirements.txt