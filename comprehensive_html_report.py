#!/usr/bin/env python3
"""
综合HTML文件验证报告
检查语法、路径引用、JavaScript语法等
"""

import re
import os
import requests
from pathlib import Path

def check_external_resources(content):
    """检查外部资源链接"""
    issues = []
    
    # 检查CSS和JS链接
    css_js_pattern = r'<(?:link|script)[^>]*(?:href|src)=["\']([^"\']+)["\'][^>]*>'
    resources = re.findall(css_js_pattern, content)
    
    for resource in resources:
        if resource.startswith(('http://', 'https://', '//')):
            # 外部资源，尝试检查可用性
            try:
                response = requests.head(resource, timeout=5)
                if response.status_code >= 400:
                    issues.append(f"外部资源可能不可用: {resource} (状态码: {response.status_code})")
            except Exception as e:
                issues.append(f"无法检查外部资源: {resource} (错误: {str(e)})")
        elif resource.startswith('/'):
            # 本地资源，检查是否存在
            local_path = Path('/Users/colin/Desktop/personal-system') / resource.lstrip('/')
            if not local_path.exists():
                issues.append(f"本地资源不存在: {resource}")
    
    return issues

def validate_html_comprehensive(file_path):
    """综合验证HTML文件"""
    errors = []
    warnings = []
    info = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        errors.append(f"无法读取文件: {str(e)}")
        return errors, warnings, info
    
    filename = Path(file_path).name
    
    # 1. 基本HTML结构检查
    lines = content.split('\n')
    has_doctype = any('<!DOCTYPE' in line.upper() for line in lines[:5])
    if not has_doctype:
        warnings.append("缺少DOCTYPE声明")
    
    has_html_tag = '<html' in content.lower()
    has_head_tag = '<head' in content.lower()
    has_body_tag = '<body' in content.lower()
    
    if not has_html_tag:
        errors.append("缺少<html>标签")
    if not has_head_tag:
        warnings.append("缺少<head>标签")
    if not has_body_tag:
        warnings.append("缺少<body>标签")
    
    # 2. Jinja2模板语法检查
    jinja_blocks = re.findall(r'\{\% (block|endblock|extends|if|endif|for|endfor) [^\%]*\%\}', content)
    jinja_variables = re.findall(r'\{\{[^}]*\}\}', content)
    
    info.append(f"Jinja2块: {len(jinja_blocks)} 个")
    info.append(f"Jinja2变量: {len(jinja_variables)} 个")
    
    # 3. JavaScript语法检查（重点）
    js_errors = check_javascript_syntax_detailed(content, info)
    errors.extend(js_errors)
    
    # 4. 外部资源检查
    resource_issues = check_external_resources(content)
    warnings.extend(resource_issues)
    
    # 5. 属性引号检查
    for line_num, line in enumerate(lines, 1):
        # 跳过Jinja2语法行
        if '{%' in line or '{{' in line:
            continue
            
        # 检查HTML属性引号
        if '"' in line and line.count('"') % 2 != 0:
            errors.append(f"第{line_num}行: 双引号不匹配")
    
    # 6. 特定模式检查
    # 检查是否正确使用了tojson过滤器
    if 'onclick=' in content and '{{' in content and 'tojson' not in content:
        warnings.append("onclick事件中使用了Jinja2变量但未使用tojson过滤器，可能导致JavaScript语法错误")
    
    # 7. 安全性检查
    if 'javascript:' in content.lower():
        warnings.append("发现javascript:协议，可能存在安全风险")
    
    # 8. 可访问性检查
    if '<img' in content and 'alt=' not in content:
        warnings.append("<img>标签缺少alt属性，影响可访问性")
    
    return errors, warnings, info

def check_javascript_syntax_detailed(content, info):
    """详细检查JavaScript语法"""
    errors = []

    # 检查onclick事件
    onclick_pattern = r'onclick=["\']([^"\']+)["\']'
    onclicks = re.findall(onclick_pattern, content, re.IGNORECASE)

    for onclick in onclicks:
        # 检查函数调用语法
        if 'editCompany(' in onclick or 'deleteCompany(' in onclick or 'deleteProject(' in onclick or 'deleteDocument(' in onclick:
            # 检查是否正确使用了tojson过滤器
            if '{{' in onclick and 'tojson' not in onclick:
                errors.append(f"JavaScript语法错误: onclick事件中的Jinja2变量未使用tojson过滤器")

            # 检查引号匹配
            if onclick.count('"') % 2 != 0 or onclick.count("'") % 2 != 0:
                errors.append(f"JavaScript语法错误: onclick事件中引号不匹配")

    # 检查内联JavaScript
    script_pattern = r'<script[^>]*>(.*?)</script>'
    scripts = re.findall(script_pattern, content, re.DOTALL | re.IGNORECASE)

    for i, script in enumerate(scripts):
        # 基本的JavaScript语法检查
        if 'function' in script:
            # 检查函数定义语法
            function_defs = re.findall(r'function\s+(\w+)\s*\([^)]*\)\s*\{', script)
            info.append(f"脚本块{i+1}中定义了函数: {', '.join(function_defs)}")

    return errors

def generate_comprehensive_report():
    """生成综合验证报告"""
    directory = '/Users/colin/Desktop/personal-system/templates/company'
    
    print("🔍 综合HTML验证报告")
    print("=" * 80)
    print(f"目录: {directory}")
    print("检查项目: HTML结构、Jinja2语法、JavaScript语法、外部资源、安全性、可访问性")
    print("=" * 80)
    
    total_files = 0
    total_errors = 0
    total_warnings = 0
    
    for html_file in sorted(Path(directory).glob('*.html')):
        total_files += 1
        filename = html_file.name
        
        print(f"\n📄 {filename}")
        print("-" * 60)
        
        errors, warnings, info = validate_html_comprehensive(html_file)
        
        # 显示信息
        if info:
            print("ℹ️  信息:")
            for item in info:
                print(f"   {item}")
        
        # 显示错误
        if errors:
            print("❌ 错误:")
            for error in errors:
                print(f"   • {error}")
            total_errors += len(errors)
        
        # 显示警告
        if warnings:
            print("⚠️  警告:")
            for warning in warnings:
                print(f"   • {warning}")
            total_warnings += len(warnings)
        
        # 状态总结
        if not errors and not warnings:
            print("✅ 状态: 完美！")
        elif not errors:
            print("✅ 状态: 通过（有警告）")
        else:
            print("❌ 状态: 需要修复")
    
    print("\n" + "=" * 80)
    print("📊 总结")
    print(f"总文件数: {total_files}")
    print(f"总错误数: {total_errors}")
    print(f"总警告数: {total_warnings}")
    
    if total_errors == 0:
        print("🎉 所有HTML文件语法正确！")
    else:
        print("⚠️  发现一些需要修复的问题")
    
    print("\n🔧 修复建议:")
    print("1. 为所有HTML文件添加DOCTYPE声明")
    print("2. 确保所有Jinja2变量在JavaScript中使用tojson过滤器")
    print("3. 检查外部资源链接的可用性")
    print("4. 为所有<img>标签添加alt属性")
    print("5. 避免使用javascript:协议")

if __name__ == "__main__":
    generate_comprehensive_report()