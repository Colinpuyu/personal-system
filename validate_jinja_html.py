#!/usr/bin/env python3
"""
专门处理Jinja2模板的HTML验证器
"""

import re
import os
from pathlib import Path

def validate_jinja_html_file(file_path):
    """验证包含Jinja2语法的HTML文件"""
    errors = []
    warnings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        errors.append(f"无法读取文件: {str(e)}")
        return errors, warnings
    
    # 检查基本的HTML结构
    lines = content.split('\n')
    has_doctype = any('<!DOCTYPE' in line.upper() for line in lines[:5])
    if not has_doctype:
        warnings.append("缺少DOCTYPE声明")
    
    # 检查引号匹配（考虑Jinja2变量）
    for line_num, line in enumerate(lines, 1):
        # 跳过Jinja2语法行
        if '{%' in line or '{{' in line:
            continue
            
        # 检查HTML属性引号
        if '"' in line and line.count('"') % 2 != 0:
            errors.append(f"第{line_num}行: 双引号不匹配")
        if "'" in line and line.count("'") % 2 != 0:
            warnings.append(f"第{line_num}行: 单引号不匹配")
    
    # 检查标签结构（更智能的方法）
    # 移除Jinja2语法进行结构检查
    clean_html = re.sub(r'\{\{.*?\}\}', 'PLACEHOLDER', content, flags=re.DOTALL)
    clean_html = re.sub(r'\{\%.*?\%\}', '', clean_html, flags=re.DOTALL)
    
    # 检查自闭合标签
    self_closing_tags = ['br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr']
    
    # 查找潜在的标签问题
    tag_pattern = r'<(/?)([a-zA-Z][a-zA-Z0-9]*)[^>]*>'
    tags = re.findall(tag_pattern, clean_html)
    
    # 简单的标签计数检查
    tag_counts = {}
    for is_closing, tag_name in tags:
        tag_name = tag_name.lower()
        if tag_name in self_closing_tags:
            continue
            
        key = f"{is_closing}{tag_name}"
        tag_counts[key] = tag_counts.get(key, 0) + 1
    
    # 检查常见的不匹配
    for tag_name in ['div', 'form', 'p', 'label', 'input', 'textarea', 'select', 'button']:
        opening = tag_counts.get('', {}).get(tag_name, 0) if isinstance(tag_counts.get('', {}), dict) else 0
        closing = tag_counts.get('/', {}).get(tag_name, 0) if isinstance(tag_counts.get('/', {}), dict) else 0
        
        if opening != closing:
            warnings.append(f"<{tag_name}> 标签数量不匹配: 开始标签 {opening} 个，结束标签 {closing} 个")
    
    # 检查JavaScript语法（特别是我们修复的部分）
    js_errors = check_javascript_syntax(content)
    errors.extend(js_errors)
    
    return errors, warnings

def check_javascript_syntax(content):
    """检查JavaScript语法错误"""
    errors = []
    
    # 检查onclick事件中的JavaScript
    onclick_pattern = r'onclick="([^"]*)"'
    onclicks = re.findall(onclick_pattern, content)
    
    for onclick in onclicks:
        # 检查函数调用语法
        if 'editCompany(' in onclick or 'deleteCompany(' in onclick or 'deleteProject(' in onclick or 'deleteDocument(' in onclick:
            # 检查是否正确使用了tojson过滤器
            if '{{' in onclick and 'tojson' not in onclick:
                errors.append(f"JavaScript语法错误: onclick事件中的变量未使用tojson过滤器: {onclick}")
            
            # 检查引号匹配
            if onclick.count('"') % 2 != 0:
                errors.append(f"JavaScript语法错误: onclick事件中引号不匹配: {onclick}")
    
    return errors

def validate_all_jinja_html_files(directory):
    """验证目录下所有HTML文件"""
    results = {}
    
    for html_file in Path(directory).glob('*.html'):
        errors, warnings = validate_jinja_html_file(html_file)
        results[html_file.name] = {
            'errors': errors,
            'warnings': warnings,
            'status': '✅ 通过' if not errors else '❌ 错误'
        }
    
    return results

def main():
    directory = '/Users/colin/Desktop/personal-system/templates/company'
    print(f"正在验证目录: {directory}")
    print("=" * 60)
    
    results = validate_all_jinja_html_files(directory)
    
    total_files = len(results)
    error_files = sum(1 for r in results.values() if r['errors'])
    
    for filename, result in results.items():
        print(f"\n📄 {filename}")
        print(f"状态: {result['status']}")
        
        if result['errors']:
            print("错误:")
            for error in result['errors']:
                print(f"  ❌ {error}")
        
        if result['warnings']:
            print("警告:")
            for warning in result['warnings']:
                print(f"  ⚠️  {warning}")
    
    print("\n" + "=" * 60)
    print(f"总计: {total_files} 个文件")
    print(f"通过: {total_files - error_files} 个文件")
    print(f"错误: {error_files} 个文件")

if __name__ == "__main__":
    main()