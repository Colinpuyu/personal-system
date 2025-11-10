#!/usr/bin/env python3
"""
HTML语法验证器
检查HTML文件的基本语法错误
"""

import re
import os
from pathlib import Path

def validate_html_file(file_path):
    """验证单个HTML文件的语法"""
    errors = []
    warnings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        errors.append(f"无法读取文件: {str(e)}")
        return errors, warnings
    
    # 移除Jinja2模板语法，专注于HTML结构
    html_content = re.sub(r'\{\{.*?\}\}', '', content, flags=re.DOTALL)
    html_content = re.sub(r'\{\%.*?\%\}', '', html_content, flags=re.DOTALL)
    # 同时移除Jinja2的if条件内容，避免干扰标签匹配
    html_content = re.sub(r'\{\% if .*?\%\}.*?\{\% endif \%\}', '', html_content, flags=re.DOTALL)
    
    lines = html_content.split('\n')
    
    # 检查基本的HTML结构
    has_doctype = any('<!DOCTYPE' in line.upper() for line in lines[:5])
    if not has_doctype:
        warnings.append("缺少DOCTYPE声明")
    
    # 检查标签匹配
    tag_stack = []
    line_num = 0
    
    for line in lines:
        line_num += 1
        # 找到所有标签
        tags = re.findall(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)[^>]*>', line)
        
        for is_closing, tag_name in tags:
            tag_name = tag_name.lower()
            
            # 跳过自闭合标签
            if tag_name in ['br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr']:
                continue
                
            if not is_closing:
                # 开始标签
                tag_stack.append((tag_name, line_num))
            else:
                # 结束标签
                if not tag_stack:
                    errors.append(f"第{line_num}行: 意外的结束标签 </{tag_name}>")
                else:
                    last_tag, last_line = tag_stack[-1]
                    if last_tag == tag_name:
                        tag_stack.pop()
                    else:
                        errors.append(f"第{line_num}行: 标签不匹配，期望 </{last_tag}> 但找到 </{tag_name}>")
    
    # 检查未闭合的标签
    for tag_name, line_num in tag_stack:
        errors.append(f"第{line_num}行开始的 <{tag_name}> 标签未闭合")
    
    # 检查属性引号匹配
    for line_num, line in enumerate(lines, 1):
        # 简单的属性引号检查
        if line.count('"') % 2 != 0:
            errors.append(f"第{line_num}行: 双引号不匹配")
        if line.count("'") % 2 != 0:
            warnings.append(f"第{line_num}行: 单引号不匹配")
    
    return errors, warnings

def validate_all_html_files(directory):
    """验证目录下所有HTML文件"""
    results = {}
    
    for html_file in Path(directory).glob('*.html'):
        errors, warnings = validate_html_file(html_file)
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
    
    results = validate_all_html_files(directory)
    
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