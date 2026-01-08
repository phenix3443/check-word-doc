#!/usr/bin/env python3
"""
Document structure analysis functions.
"""

import zipfile
import xml.etree.ElementTree as ET
import re


def analyze_document_structure(docx_path):
    """Analyze the overall structure of the document."""
    structure = {
        'headers': [],
        'footers': [],
        'sections': [],
        'document_parts': {
            'cover': {'start': None, 'end': None, 'paragraphs': []},
            'toc': {'start': None, 'end': None, 'paragraphs': []},
            'figure_list': {'start': None, 'end': None, 'paragraphs': []},
            'table_list': {'start': None, 'end': None, 'paragraphs': []},
            'body': {'start': None, 'end': None, 'paragraphs': []},
            'references': {'start': None, 'end': None, 'paragraphs': []},
            'attachments': {'start': None, 'end': None, 'paragraphs': []}
        },
        'total_paragraphs': 0
    }

    try:
        with zipfile.ZipFile(docx_path, 'r') as docx:
            file_list = docx.namelist()

            # 分析文件结构
            structure['headers'] = [f for f in file_list if 'header' in f.lower() and f.endswith('.xml')]
            structure['footers'] = [f for f in file_list if 'footer' in f.lower() and f.endswith('.xml')]
            structure['sections'] = [f for f in file_list if 'word/section' in f.lower() or 'document.xml' in f]

            # 分析文档内容结构
            if 'word/document.xml' in file_list:
                document_xml = docx.read('word/document.xml')
                structure = _analyze_document_content(document_xml, structure)

    except Exception as e:
        print(f"Error analyzing document structure: {e}")

    return structure


def _analyze_document_content(document_xml, structure):
    """分析文档内容，识别各个部分"""
    try:
        root = ET.fromstring(document_xml)

        # 定义命名空间
        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }

        # 获取所有段落
        paragraphs = root.findall('.//w:p', namespaces)
        structure['total_paragraphs'] = len(paragraphs)

        # 分析每个段落的内容和样式
        paragraph_info = []
        for i, para in enumerate(paragraphs):
            para_info = _analyze_paragraph(para, i, namespaces)
            paragraph_info.append(para_info)

        # 识别文档各部分
        structure['document_parts'] = _identify_document_parts(paragraph_info)

    except Exception as e:
        print(f"Error analyzing document content: {e}")

    return structure


def _analyze_paragraph(para, index, namespaces):
    """分析单个段落"""
    para_info = {
        'index': index,
        'text': '',
        'style': None,
        'is_heading': False,
        'heading_level': None,
        'is_body_paragraph': False,
        'is_empty': True,
        'has_page_break': False,
        'has_section_break': False
    }
    
    try:
        # 获取段落文本
        text_elements = para.findall('.//w:t', namespaces)
        para_text = ''.join([t.text or '' for t in text_elements])
        para_info['text'] = para_text.strip()
        para_info['is_empty'] = len(para_info['text']) == 0
        
        # 获取段落样式
        pPr = para.find('w:pPr', namespaces)
        style_val = None
        if pPr is not None:
            # 检查样式
            pStyle = pPr.find('w:pStyle', namespaces)
            if pStyle is not None:
                style_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
        
        para_info['style'] = style_val
        
        # 根据样式和内容判断段落类型
        if style_val and _is_heading_style(style_val):
            # 明确的标题样式
            para_info['is_heading'] = True
            para_info['heading_level'] = _extract_heading_level(style_val)
        elif style_val and _is_body_paragraph_style(style_val):
            # 明确的正文样式
            para_info['is_body_paragraph'] = True
        else:
            # 没有明确样式或Normal样式，根据内容判断
            if para_info['text'] and not para_info['is_empty']:
                # 优先检查是否是正文段落（长文本或包含句号）
                if len(para_info['text']) > 30 or '。' in para_info['text']:
                    para_info['is_body_paragraph'] = True
                # 然后检查是否看起来像标题
                elif _looks_like_heading(para_info['text']):
                    para_info['is_heading'] = True
                    para_info['heading_level'] = _guess_heading_level(para_info['text'])
                else:
                    # 默认认为是正文段落
                    para_info['is_body_paragraph'] = True
            
        # 检查分页符和分节符
        if pPr is not None:
            sectPr = pPr.find('w:sectPr', namespaces)
            if sectPr is not None:
                para_info['has_section_break'] = True
            
            # 检查分页符
            pageBreakBefore = pPr.find('w:pageBreakBefore', namespaces)
            if pageBreakBefore is not None:
                para_info['has_page_break'] = True
    
    except Exception as e:
        print(f"Error analyzing paragraph {index}: {e}")
    
    return para_info


def _is_heading_style(style_val):
    """判断样式是否为标题样式"""
    if not style_val:
        return False
    
    style_lower = style_val.lower()
    heading_patterns = [
        'heading', 'title', 'subtitle', 
        '标题', '题目', '章节', '节标题'
    ]
    
    return any(pattern in style_lower for pattern in heading_patterns)


def _is_body_paragraph_style(style_val):
    """判断样式是否为正文段落样式"""
    # None 或 Normal 样式通常是正文段落
    if not style_val or style_val.lower() in ['normal', 'none']:
        return True
    
    style_lower = style_val.lower()
    body_patterns = [
        'normal', 'body', 'paragraph', 'text',
        '正文', '段落', '内容', '文本'
    ]
    
    return any(pattern in style_lower for pattern in body_patterns)


def _extract_heading_level(style_val):
    """从样式名称中提取标题级别"""
    if not style_val:
        return 1
    
    # 尝试从样式名中提取数字
    import re
    level_match = re.search(r'(\d+)', style_val)
    if level_match:
        level = int(level_match.group(1))
        return min(max(level, 1), 6)  # 限制在1-6级之间
    
    return 1  # 默认为1级标题


def _looks_like_heading(text):
    """根据文本内容判断是否像标题"""
    if not text or len(text.strip()) == 0:
        return False
    
    text = text.strip()
    
    # 检查是否包含标题特征
    import re
    
    # 包含编号的可能是标题
    if re.match(r'^\d+[\.\s]', text):  # 如：1. 引言, 1 引言
        return True
    
    if re.match(r'^\d+\.\d+[\.\s]', text):  # 如：1.1 方法
        return True
    
    if re.match(r'^[一二三四五六七八九十]+[\.\s、]', text):  # 如：一、引言
        return True
    
    # 包含常见标题关键词且较短
    heading_keywords = [
        '引言', '概述', '摘要', '总结', '结论', '方法', '结果', '讨论',
        '目录', '参考文献', '附录', '致谢', '声明', '插图目录', '附表目录',
        'introduction', 'conclusion', 'method', 'result', 'discussion',
        'abstract', 'summary', 'references', 'appendix'
    ]
    
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in heading_keywords) and len(text) < 50:
        return True
    
    # 包含冒号的短文本可能是封面信息（如：项目名称：xxx）
    if ':' in text or '：' in text:
        if len(text) < 100:
            return True
    
    # 全部是大写字母可能是标题
    if text.isupper() and len(text) < 50:
        return True
    
    # 很短的文本且不以句号结尾可能是标题
    if len(text) < 20 and not text.endswith('。') and not text.endswith('.'):
        return True
    
    return False


def _guess_heading_level(text):
    """根据文本内容猜测标题级别"""
    if not text:
        return 1
    
    import re
    
    # 检查数字编号
    match = re.match(r'^(\d+)[\.\s]', text.strip())
    if match:
        num = int(match.group(1))
        if num <= 6:
            return 1  # 一级标题
    
    # 检查多级编号
    match = re.match(r'^(\d+)\.(\d+)[\.\s]', text.strip())
    if match:
        return 2  # 二级标题
    
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)[\.\s]', text.strip())
    if match:
        return 3  # 三级标题
    
    # 检查中文编号
    if re.match(r'^[一二三四五六七八九十]+[\.\s、]', text.strip()):
        return 1  # 一级标题
    
    # 默认为1级标题
    return 1


def _identify_document_parts(paragraph_info):
    """识别文档的各个部分"""
    parts = {
        'cover': {'start': None, 'end': None, 'paragraphs': []},
        'toc': {'start': None, 'end': None, 'paragraphs': []},
        'figure_list': {'start': None, 'end': None, 'paragraphs': []},
        'table_list': {'start': None, 'end': None, 'paragraphs': []},
        'body': {'start': None, 'end': None, 'paragraphs': []},
        'references': {'start': None, 'end': None, 'paragraphs': []},
        'attachments': {'start': None, 'end': None, 'paragraphs': []}
    }
    
    try:
        current_part = 'cover'  # 默认从封面开始
        total_paras = len(paragraph_info)
        
        for i, para in enumerate(paragraph_info):
            text = para['text'].lower()
            
            # 识别各部分的开始（基于内容和样式）
            if _is_toc_start(text, para):
                if current_part != 'toc':
                    if current_part == 'cover':
                        parts['cover']['end'] = i - 1
                    current_part = 'toc'
                    parts['toc']['start'] = i
            elif _is_figure_list_start(text, para):
                if current_part != 'figure_list':
                    if current_part in ['cover', 'toc']:
                        parts[current_part]['end'] = i - 1
                    current_part = 'figure_list'
                    parts['figure_list']['start'] = i
            elif _is_table_list_start(text, para):
                if current_part != 'table_list':
                    if current_part in ['cover', 'toc', 'figure_list']:
                        parts[current_part]['end'] = i - 1
                    current_part = 'table_list'
                    parts['table_list']['start'] = i
            elif _is_references_start(text, para):
                if current_part != 'references':
                    if current_part == 'body':
                        parts['body']['end'] = i - 1
                    current_part = 'references'
                    parts['references']['start'] = i
            elif _is_attachments_start(text, para):
                if current_part != 'attachments':
                    if current_part == 'references':
                        parts['references']['end'] = i - 1
                    current_part = 'attachments'
                    parts['attachments']['start'] = i
            elif _is_body_content(text, para, current_part):
                # 检查是否应该切换到正文部分
                if current_part in ['cover', 'toc', 'figure_list', 'table_list'] and current_part != 'body':
                    # 如果当前不在正文部分，且这个段落看起来像正文内容，则切换到正文
                    if current_part != 'cover':  # 不是封面的话，结束当前部分
                        parts[current_part]['end'] = i - 1
                    current_part = 'body'
                    parts['body']['start'] = i
            
            # 将段落添加到当前部分
            parts[current_part]['paragraphs'].append(i)

        # 设置默认的结束位置和正文开始位置
        section_break_indices = [i for i, p in enumerate(paragraph_info) if p['has_section_break']]
        
        if parts['cover']['start'] is None and parts['cover']['paragraphs']:
            parts['cover']['start'] = 0
        
        # 如果有分节符，封面结束于第一个分节符，正文从分节符后开始
        if section_break_indices:
            first_section_break = section_break_indices[0]
            if parts['cover']['end'] is None:
                parts['cover']['end'] = first_section_break
            # 重新分配段落：封面段落只包含分节符之前的段落
            parts['cover']['paragraphs'] = list(range(0, first_section_break + 1))
            # 正文从分节符后开始
            if parts['body']['start'] is None:
                parts['body']['start'] = first_section_break + 1
                parts['body']['paragraphs'] = list(range(first_section_break + 1, total_paras))
        else:
            # 没有分节符的情况，默认前3个段落为封面，其余为正文
            if parts['cover']['end'] is None:
                parts['cover']['end'] = min(2, total_paras - 1)
            parts['cover']['paragraphs'] = list(range(0, min(3, total_paras)))
            if total_paras > 3:
                if parts['body']['start'] is None:
                    parts['body']['start'] = 3
                    parts['body']['paragraphs'] = list(range(3, total_paras))

        # 为没有明确结束的部分设置结束位置
        for part_name, part_info in parts.items():
            if part_info['paragraphs'] and part_info['end'] is None:
                part_info['end'] = total_paras - 1

    except Exception as e:
        print(f"Error identifying document parts: {e}")

    return parts


def _is_toc_start(text, para):
    """判断是否为目录开始"""
    toc_keywords = ['目录', 'contents', 'table of contents']
    # 排除插图目录和附表目录
    exclude_keywords = ['插图目录', '图目录', '附表目录', '表目录']
    
    # 检查是否包含目录关键词但不包含排除关键词
    has_toc_keyword = any(keyword in text for keyword in toc_keywords)
    has_exclude_keyword = any(keyword in text for keyword in exclude_keywords)
    
    return has_toc_keyword and not has_exclude_keyword


def _is_figure_list_start(text, para):
    """判断是否为插图目录开始"""
    fig_keywords = ['插图目录', '图目录', 'list of figures', 'figure list']
    return any(keyword in text for keyword in fig_keywords)


def _is_table_list_start(text, para):
    """判断是否为附表目录开始"""
    table_keywords = ['附表目录', '表目录', 'list of tables', 'table list']
    return any(keyword in text for keyword in table_keywords)


def _is_body_start(text, para):
    """判断是否为正文开始"""
    # 通常正文以一级标题开始，且不是目录类标题
    if para['is_heading'] and para['heading_level'] == 1:
        exclude_keywords = ['目录', '插图', '附表', '参考文献', '附录', 'contents', 'figures', 'tables', 'references', 'appendix']
        return not any(keyword in text for keyword in exclude_keywords)
    return False


def _is_body_content(text, para, current_part):
    """判断是否为正文内容"""
    # 如果已经在正文部分，继续归类为正文
    if current_part == 'body':
        return True
    
    # 如果是正文段落样式
    if para.get('is_body_paragraph', False):
        return True
    
    # 如果是正文标题（编号标题，但不是特殊部分标题）
    if para.get('is_heading', False):
        exclude_keywords = ['目录', '插图', '附表', '参考文献', '附录', 'contents', 'figures', 'tables', 'references', 'appendix']
        if not any(keyword in text for keyword in exclude_keywords):
            # 检查是否是编号标题（如：1 引言、2.1 方法等）
            import re
            if re.match(r'^\d+[\.\s]', text.strip()) or re.match(r'^\d+\.\d+[\.\s]', text.strip()):
                return True
    
    # 如果当前在目录相关部分，但这个段落看起来像正文内容
    if current_part in ['toc', 'figure_list', 'table_list']:
        # 长段落通常是正文
        if len(text.strip()) > 50 and para.get('is_body_paragraph', False):
            return True
        
        # 包含正文特征的段落
        body_indicators = ['研究', '方法', '实验', '结果', '分析', '讨论', '本文', '本研究', '系统', '算法']
        if any(indicator in text for indicator in body_indicators) and len(text.strip()) > 20:
            return True
    
    return False


def _is_references_start(text, para):
    """判断是否为参考文献开始"""
    ref_keywords = ['参考文献', 'references', '参考资料']
    return any(keyword in text for keyword in ref_keywords) and para['is_heading']


def _is_attachments_start(text, para):
    """判断是否为附录开始"""
    att_keywords = ['附录', 'appendix', '附件']
    return any(keyword in text for keyword in att_keywords) and para['is_heading']


def get_paragraphs_for_part(structure, part_name):
    """获取指定部分的段落索引列表"""
    if part_name in structure.get('document_parts', {}):
        return structure['document_parts'][part_name]['paragraphs']
    return []


def is_paragraph_in_part(structure, paragraph_index, part_name):
    """判断段落是否属于指定部分"""
    part_paragraphs = get_paragraphs_for_part(structure, part_name)
    return paragraph_index in part_paragraphs


# ============================================================================
# 文档结构验证功能（从 structure_check.py 合并）
# ============================================================================

def _is_check_enabled(config_loader, check_name, item_config):
    """
    Check if a specific check is enabled.
    
    Args:
        config_loader: ConfigLoader instance
        check_name: Name of the check (e.g., "structure")
        item_config: Configuration dictionary for the check item
        
    Returns:
        True if check is enabled, False otherwise
    """
    # First check top-level checks section
    if not config_loader.get_check_enabled(check_name):
        return False
    
    # Then check item-level enabled flag
    if not item_config.get("enabled", True):
        return False
    
    return True


def run_structure_check(docx_path, config_loader=None, structure=None):
    """Run document structure validation check."""
    print("Checking document structure...")
    try:
        if config_loader is None:
            from config_loader import ConfigLoader
            config_loader = ConfigLoader()
        # 确保配置已加载
        if hasattr(config_loader, 'config') and config_loader.config:
            config = config_loader.config
        else:
            config = config_loader.load()
        
        # 获取结构检查配置
        structure_config = config.get("structure", {})
        
        # Check if check is enabled
        if not _is_check_enabled(config_loader, "structure", structure_config):
            result = {
                "found": False,
                "message": "Document structure check is disabled",
                "details": [],
            }
            print(f"   Result: {result['message']}")
            return result
        
        if structure is None:
            result = {
                "found": True,
                "message": "Document structure not provided for validation",
                "details": [],
                "error": True
            }
            print(f"   Result: {result['message']}")
            return result
        
        # 获取必需部分配置
        required_parts = structure_config.get("required_parts", {})
        validation_config = structure_config.get("validation", {})
        scientific_report_rules = structure_config.get("scientific_report_rules", {})
        
        issues = []
        document_parts = structure.get('document_parts', {})
        
        # 检查必需的文档部分
        for part_name, is_required in required_parts.items():
            if is_required:
                # 处理部分名称映射（table_of_contents -> toc）
                actual_part_name = _map_config_to_structure_name(part_name)
                part_info = document_parts.get(actual_part_name, {})
                part_paragraphs = part_info.get('paragraphs', [])
                
                if not part_paragraphs:
                    issues.append({
                        'type': 'missing_required_part',
                        'part': part_name,
                        'message': f"缺少必需的文档部分：{_get_part_chinese_name(part_name)}"
                    })
        
        # 检查正文段落数量
        min_body_paragraphs = validation_config.get("min_body_paragraphs", 1)
        body_info = document_parts.get('body', {})
        body_paragraphs = body_info.get('paragraphs', [])
        
        if len(body_paragraphs) < min_body_paragraphs:
            issues.append({
                'type': 'insufficient_body_paragraphs',
                'current_count': len(body_paragraphs),
                'required_count': min_body_paragraphs,
                'message': f"正文段落数量不足：当前{len(body_paragraphs)}个，至少需要{min_body_paragraphs}个"
            })
        
        # 检查文档部分顺序
        if validation_config.get("check_part_order", False):
            expected_order = validation_config.get("expected_order")
            order_issues = _check_part_order(document_parts, expected_order)
            issues.extend(order_issues)
        
        # 检查正文内容要求
        body_content_requirements = validation_config.get("body_content_requirements", {})
        if body_content_requirements:
            body_issues = _check_body_content_requirements(document_parts, body_content_requirements, docx_path)
            issues.extend(body_issues)
        
        # 检查科技报告特有规则
        if scientific_report_rules:
            scientific_issues = _check_scientific_report_rules(document_parts, scientific_report_rules, docx_path)
            issues.extend(scientific_issues)
        
        # 生成结果
        if issues:
            result = {
                "found": True,
                "message": f"发现 {len(issues)} 个文档结构问题",
                "details": issues
            }
        else:
            result = {
                "found": False,
                "message": "文档结构符合要求",
                "details": []
            }
        
        print(f"   Result: {result['message']}")
        
        # 显示详细信息
        if issues:
            print()
            print("   WARNING: Document structure issues found!")
            print(f"   Found {len(issues)} issue(s)")
            print("   Issues:")
            for issue in issues:
                print(f"      - {issue['message']}")
        else:
            print("   ✓ Document structure is valid")
        
        return result
        
    except Exception as e:
        print(f"   Error checking document structure: {e}")
        return {
            "found": True,
            "message": f"Error: {e}",
            "details": [],
            "error": True
        }


def _get_part_chinese_name(part_name):
    """获取文档部分的中文名称"""
    name_mapping = {
        'cover': '封面',
        'table_of_contents': '目录',
        'toc': '目录',
        'figure_list': '插图目录',
        'table_list': '附表目录',
        'body': '正文',
        'references': '参考文献',
        'attachments': '附录'
    }
    return name_mapping.get(part_name, part_name)


def _map_config_to_structure_name(config_name):
    """将配置中的部分名称映射到结构分析中的名称"""
    mapping = {
        'table_of_contents': 'toc',
        'figure_list': 'figure_list',
        'table_list': 'table_list',
        'body': 'body',
        'references': 'references',
        'attachments': 'attachments',
        'cover': 'cover'
    }
    return mapping.get(config_name, config_name)


def _check_part_order(document_parts, expected_order=None):
    """检查文档部分的顺序"""
    issues = []
    
    # 使用提供的顺序或默认顺序
    if expected_order is None:
        expected_order = ['cover', 'table_of_contents', 'figure_list', 'table_list', 'body', 'references', 'attachments']
    
    # 获取实际存在的部分及其起始位置
    existing_parts = []
    for part_name in expected_order:
        part_info = document_parts.get(part_name, {})
        if part_info.get('paragraphs'):
            start_paragraph = min(part_info['paragraphs'])
            existing_parts.append((part_name, start_paragraph))
    
    # 按起始段落排序
    existing_parts.sort(key=lambda x: x[1])
    
    # 检查顺序是否正确
    expected_existing_order = [part for part in expected_order if any(p[0] == part for p in existing_parts)]
    actual_order = [part[0] for part in existing_parts]
    
    if actual_order != expected_existing_order:
        issues.append({
            'type': 'incorrect_part_order',
            'expected_order': expected_existing_order,
            'actual_order': actual_order,
            'message': f"文档部分顺序不正确。期望顺序：{' -> '.join([_get_part_chinese_name(p) for p in expected_existing_order])}，实际顺序：{' -> '.join([_get_part_chinese_name(p) for p in actual_order])}"
        })
    
    return issues


def get_structure_summary(structure):
    """获取文档结构摘要"""
    if not structure:
        return "无法分析文档结构"
    
    document_parts = structure.get('document_parts', {})
    total_paragraphs = structure.get('total_paragraphs', 0)
    
    summary = [f"总段落数：{total_paragraphs}"]
    
    for part_name, part_info in document_parts.items():
        if part_info.get('paragraphs'):
            start = min(part_info['paragraphs'])
            end = max(part_info['paragraphs'])
            count = len(part_info['paragraphs'])
            chinese_name = _get_part_chinese_name(part_name)
            summary.append(f"{chinese_name}：段落{start}-{end}（{count}个段落）")
    
    return "；".join(summary)


def _check_body_content_requirements(document_parts, body_requirements, docx_path):
    """检查正文内容要求"""
    issues = []
    
    try:
        # 获取正文段落
        body_info = document_parts.get('body', {})
        body_paragraphs = body_info.get('paragraphs', [])
        
        if not body_paragraphs:
            return issues
        
        # 分析正文中的标题
        with zipfile.ZipFile(docx_path, 'r') as docx:
            document_xml = docx.read('word/document.xml')
            root = ET.fromstring(document_xml)
            
            namespaces = {
                'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
            }
            
            paragraphs = root.findall('.//w:p', namespaces)
            headings_in_body = []
            
            # 重新分析正文段落，获取详细的样式信息
            for para_idx in body_paragraphs:
                if para_idx < len(paragraphs):
                    para = paragraphs[para_idx]
                    # 使用改进的段落分析函数
                    para_info = _analyze_paragraph(para, para_idx, namespaces)
                    
                    # 如果是标题
                    if para_info['is_heading']:
                        headings_in_body.append({
                            'index': para_idx,
                            'text': para_info['text'],
                            'style': para_info['style'],
                            'level': para_info['heading_level']
                        })
        
        # 检查最少标题数量
        min_headings = body_requirements.get("min_headings", 0)
        if len(headings_in_body) < min_headings:
            issues.append({
                'type': 'insufficient_headings',
                'current_count': len(headings_in_body),
                'required_count': min_headings,
                'message': f"正文标题数量不足：当前{len(headings_in_body)}个，至少需要{min_headings}个"
            })
        
        # 检查编号标题要求
        if body_requirements.get("require_numbered_headings", False):
            unnumbered_headings = []
            for heading in headings_in_body:
                text = heading['text']
                # 简单检查是否包含数字编号
                if not re.match(r'^\d+', text.strip()):
                    unnumbered_headings.append(heading)
            
            if unnumbered_headings:
                issues.append({
                    'type': 'unnumbered_headings',
                    'count': len(unnumbered_headings),
                    'headings': [h['text'] for h in unnumbered_headings[:3]],  # 只显示前3个
                    'message': f"发现{len(unnumbered_headings)}个未编号的标题"
                })
    
    except Exception as e:
        issues.append({
            'type': 'body_analysis_error',
            'message': f"正文内容分析出错：{e}"
        })
    
    return issues


def _check_scientific_report_rules(document_parts, scientific_rules, docx_path):
    """检查科技报告特有规则"""
    issues = []
    
    try:
        # 检查目录要求
        toc_requirements = scientific_rules.get("toc_requirements", {})
        if toc_requirements:
            toc_info = document_parts.get('toc', {})
            toc_paragraphs = toc_info.get('paragraphs', [])
            
            min_entries = toc_requirements.get("min_entries", 0)
            if len(toc_paragraphs) < min_entries:
                issues.append({
                    'type': 'insufficient_toc_entries',
                    'current_count': len(toc_paragraphs),
                    'required_count': min_entries,
                    'message': f"目录条目数量不足：当前{len(toc_paragraphs)}个，至少需要{min_entries}个"
                })
        
        # 检查参考文献要求
        references_requirements = scientific_rules.get("references_requirements", {})
        if references_requirements:
            references_info = document_parts.get('references', {})
            references_paragraphs = references_info.get('paragraphs', [])
            
            min_references = references_requirements.get("min_references", 0)
            if len(references_paragraphs) < min_references:
                issues.append({
                    'type': 'insufficient_references',
                    'current_count': len(references_paragraphs),
                    'required_count': min_references,
                    'message': f"参考文献数量不足：当前{len(references_paragraphs)}个段落，至少需要{min_references}个参考文献"
                })
    
    except Exception as e:
        issues.append({
            'type': 'scientific_rules_error',
            'message': f"科技报告规则检查出错：{e}"
        })
    
    return issues

