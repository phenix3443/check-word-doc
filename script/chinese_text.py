#!/usr/bin/env python3
"""
Chinese text format checking functions.
检查中文间距和中文引号格式。
"""

import zipfile
import xml.etree.ElementTree as ET
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import estimate_page_from_paragraph
from cover import find_first_page_end


def is_chinese_char(char):
    """判断字符是否为中文字符。"""
    return '\u4e00' <= char <= '\u9fff'


def _check_paragraph_spacing(para_info):
    """
    检查单个段落的中文间距问题（用于并行处理）。
    
    Args:
        para_info: 包含段落信息的元组 (para_idx, para, para_text, text_elements, text_positions, namespaces, total_paragraphs)
        
    Returns:
        该段落发现的问题列表
    """
    para_idx, para, para_text, text_elements, text_positions, namespaces, total_paragraphs = para_info
    issues = []

    if not para_text.strip():
        return issues

    # 检查两个中文之间是否只有空格
    pattern = r'([\u4e00-\u9fff])(\s+)([\u4e00-\u9fff])'
    matches = list(re.finditer(pattern, para_text))

    if matches:
        for match in matches:
            start_pos = match.start()
            end_pos = match.end()
            full_match = match.group(0)
            between_text = match.group(2)

            # 验证：两个中文之间必须只有空白字符
            if between_text.strip() == '' and len(between_text) > 0:
                # 验证匹配的文本确实是"中文+只有空白字符+中文"
                matched_text = para_text[start_pos:end_pos]
                verify_pattern = r'^[\u4e00-\u9fff]\s+[\u4e00-\u9fff]$'
                if re.match(verify_pattern, matched_text):
                    # 关键检查：找到包含这两个中文字符的文本元素
                    text_elem1 = None
                    text_elem2 = None
                    chinese1_pos = start_pos
                    chinese2_pos = end_pos - 1

                    for tp in text_positions:
                        if tp['start'] <= chinese1_pos < tp['end']:
                            text_elem1 = tp['element']
                        if tp['start'] <= chinese2_pos < tp['end']:
                            text_elem2 = tp['element']

                    # 如果两个中文字符在同一个文本元素中，直接报告为问题（如"通 过"）
                    if text_elem1 is not None and text_elem2 is not None and text_elem1 == text_elem2:
                        # 两个中文字符在同一个文本元素中，中间只有空格，这是问题
                        issues.append({
                            "paragraph": para_idx,
                            "page": estimate_page_from_paragraph(para_idx, total_paragraphs),
                            "text": full_match,
                            "position": start_pos,
                            "context": para_text[max(0, start_pos - 20):end_pos + 20]
                        })
                        continue

                    # 如果找不到文本元素，或者两个中文字符在不同的文本元素中，需要进一步检查
                    # 如果两个中文字符在不同的文本元素中，检查它们之间是否有其他XML元素
                    if text_elem1 is not None and text_elem2 is not None and text_elem1 != text_elem2:
                        # 第一步：检查文本内容 - 在文本位置 start_pos+1 到 end_pos-1 之间是否有非空白字符
                        actual_between_text = para_text[start_pos + 1:end_pos - 1]
                        non_whitespace = ''.join(actual_between_text.split())
                        if non_whitespace:
                            # 如果中间有非空白字符，说明不是纯空格问题，跳过
                            continue

                        # 第二步：检查XML结构 - 判断两个中文字符之间的元素类型
                        # 获取两个文本元素所在的run
                        all_runs = para.findall(".//w:r", namespaces)
                        elem1_run = None
                        elem2_run = None

                        for run in all_runs:
                            if text_elem1 in list(run.iter()):
                                elem1_run = run
                            if text_elem2 in list(run.iter()):
                                elem2_run = run

                        # 判断两个run之间的内容类型
                        content_type = None  # None=未知, 'formula'=公式, 'text'=正常文本, 'whitespace_only'=只有空格

                        if elem1_run is not None and elem2_run is not None:
                            found_elem1 = False
                            for run in all_runs:
                                if run == elem1_run:
                                    found_elem1 = True
                                    continue
                                if found_elem1:
                                    # 检查这个run是否包含公式对象（m:oMath 或 m:oMathPara）
                                    if run.find(".//m:oMath", namespaces) is not None:
                                        content_type = 'formula'
                                        break
                                    if run.find(".//m:oMathPara", namespaces) is not None:
                                        content_type = 'formula'
                                        break
                                    math_ns = "http://schemas.openxmlformats.org/officeDocument/2006/math"
                                    for elem in run.iter():
                                        if math_ns in elem.tag:
                                            content_type = 'formula'
                                            break
                                    if content_type == 'formula':
                                        break

                                    # 检查这个run是否包含非空白文本
                                    run_text_elements = run.findall(".//w:t", namespaces)
                                    for text_elem in run_text_elements:
                                        if text_elem.text and text_elem.text.strip():
                                            content_type = 'text'
                                            break
                                    if content_type == 'text':
                                        break
                                if run == elem2_run:
                                    break

                        # 第三步：检查 text_positions 中位于两个中文字符之间的文本元素
                        if content_type is None:
                            for tp in text_positions:
                                # 检查这个文本元素是否与匹配的文本范围有重叠
                                if tp['start'] < end_pos - 1 and tp['end'] > start_pos + 1:
                                    # 计算重叠部分的文本
                                    overlap_start = max(tp['start'], start_pos + 1)
                                    overlap_end = min(tp['end'], end_pos - 1)
                                    if overlap_start < overlap_end:
                                        # 提取重叠部分的文本内容
                                        text_in_overlap = tp['text']
                                        if text_in_overlap:
                                            # 计算重叠部分在文本元素中的相对位置
                                            relative_start = overlap_start - tp['start']
                                            relative_end = overlap_end - tp['start']
                                            overlap_text = text_in_overlap[relative_start:relative_end]

                                            # 检查重叠部分的文本是否包含非空白字符
                                            if overlap_text.strip():
                                                content_type = 'text'
                                                break

                                        # 检查这个文本元素所在的run是否包含公式
                                        text_elem = tp['element']
                                        parent_run = None
                                        for run in para.findall(".//w:r", namespaces):
                                            if text_elem in list(run.iter()):
                                                parent_run = run
                                                break
                                        if parent_run is not None:
                                            if parent_run.find(".//m:oMath", namespaces) is not None:
                                                content_type = 'formula'
                                                break
                                            if parent_run.find(".//m:oMathPara", namespaces) is not None:
                                                content_type = 'formula'
                                                break
                                            math_ns = "http://schemas.openxmlformats.org/officeDocument/2006/math"
                                            for elem in parent_run.iter():
                                                if math_ns in elem.tag:
                                                    content_type = 'formula'
                                                    break
                                            if content_type == 'formula':
                                                break
                                elif tp['start'] >= end_pos:
                                    # 已经超过匹配文本的结束位置，停止检查
                                    break

                        # 根据内容类型决定是否跳过
                        # 如果是公式或正常文本，跳过（不是问题）
                        # 如果只有空格（content_type 为 None 或 'whitespace_only'），继续检查
                        if content_type == 'formula' or content_type == 'text':
                            continue
                    elif text_elem1 is None or text_elem2 is None:
                        # 如果找不到文本元素，说明可能是特殊情况，但中间只有空格，应该报告为问题
                        # 这种情况可能是文本元素提取有问题，但正则表达式已经匹配到了，应该报告
                        issues.append({
                            "paragraph": para_idx,
                            "page": estimate_page_from_paragraph(para_idx, total_paragraphs),
                            "text": full_match,
                            "position": start_pos,
                            "context": para_text[max(0, start_pos - 20):end_pos + 20]
                        })
                        continue

                    # 如果 text_elem1 或 text_elem2 为 None，或者两个中文字符在不同的文本元素中且中间只有空格
                    # 这种情况应该报告为问题
                    issues.append({
                        "paragraph": para_idx,
                        "page": estimate_page_from_paragraph(para_idx, total_paragraphs),
                        "text": full_match,
                        "position": start_pos,
                        "context": para_text[max(0, start_pos - 20):end_pos + 20]
                    })

    return issues


def check_chinese_spacing(docx_path, target_paragraphs=None):
    """
    检查两个中文之间是否有空格。
    
    Args:
        docx_path: Word文档路径
        
    Returns:
        包含检查结果的字典
    """
    issues = []

    try:
        with zipfile.ZipFile(docx_path, "r") as docx:
            if "word/document.xml" not in docx.namelist():
                return {
                    "found": False,
                    "message": "Document body not found",
                    "details": [],
                }

            document_xml = docx.read("word/document.xml")
            root = ET.fromstring(document_xml)

            namespaces = {
                "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
                "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
            }

            body = root.find(".//w:body", namespaces)
            if body is None:
                return {
                    "found": False,
                    "message": "Document body not found",
                    "details": [],
                }

            paragraphs = body.findall(".//w:p", namespaces)
            first_page_end = find_first_page_end(paragraphs, namespaces, body)
            total_paragraphs = len(paragraphs)

            # 准备需要检查的段落信息
            para_info_list = []
            for para_idx, para in enumerate(paragraphs, 1):
                # 跳过封面页的标题部分（前几个段落），但不跳过表格中的内容
                # 只跳过前3个段落（通常是标题）
                if para_idx <= 3:
                    continue
                
                # 获取段落文本
                text_elements = para.findall(".//w:t", namespaces)
                para_text = "".join([t.text for t in text_elements if t.text])
                
                # 如果是空段落且在前30个段落内，可能是封面的分隔符，检查是否跳过
                if not para_text.strip() and para_idx <= 30:
                    # 检查是否有节属性，如果有，说明是页面分隔符，跳过
                    pPr = para.find(".//w:pPr", namespaces)
                    if pPr is not None and pPr.find(".//w:sectPr", namespaces) is not None:
                        continue
                
                if not para_text.strip():
                    continue
                
                # 获取段落中所有的文本元素及其在文本中的位置
                text_positions = []
                current_pos = 0
                for text_elem in text_elements:
                    if text_elem.text:
                        text_positions.append({
                            'element': text_elem,
                            'start': current_pos,
                            'end': current_pos + len(text_elem.text),
                            'text': text_elem.text
                        })
                        current_pos += len(text_elem.text)
                
                para_info_list.append((para_idx, para, para_text, text_elements, text_positions, namespaces, total_paragraphs))
            
            # 使用并行处理加速检查（对于大文档）
            if len(para_info_list) > 50:
                with ThreadPoolExecutor(max_workers=8) as executor:
                    future_to_para = {
                        executor.submit(_check_paragraph_spacing, para_info): para_info[0]
                        for para_info in para_info_list
                    }
                    for future in as_completed(future_to_para):
                        try:
                            para_issues = future.result()
                            issues.extend(para_issues)
                        except Exception as e:
                            print(f"   Warning: Error processing paragraph {future_to_para[future]}: {e}")
            else:
                # 对于小文档，串行处理更快（避免线程开销）
                for para_info in para_info_list:
                    para_issues = _check_paragraph_spacing(para_info)
                    issues.extend(para_issues)
    
    except Exception as e:
        return {
            "found": False,
            "message": f"Error checking Chinese spacing: {e}",
            "details": [],
        }

    if issues:
        return {
            "found": True,
            "message": f"发现 {len(issues)} 处中文之间包含空格的问题",
            "details": issues,
        }
    else:
        return {
            "found": False,
            "message": "未发现中文之间包含空格的问题",
            "details": [],
        }


def is_text_in_formula_context(text_elem, para, namespaces):
    """
    检查文本元素是否在公式对象的上下文中。
    包括：
    1. 文本元素是否在公式对象（m:oMath）中
    2. 文本元素是否在公式对象的父元素中
    3. 文本元素是否紧邻公式对象（前后有公式对象）
    """
    math_ns = "http://schemas.openxmlformats.org/officeDocument/2006/math"
    
    # 查找包含这个文本元素的run
    for run in para.findall(".//w:r", namespaces):
        if text_elem in list(run.iter()):
            # 1. 检查run是否直接包含公式对象
            if run.find(".//m:oMath", namespaces) is not None:
                return True
            if run.find(".//m:oMathPara", namespaces) is not None:
                return True
            
            # 2. 检查run是否在公式对象的父元素中
            # 查找所有公式对象
            for omath in para.findall(".//m:oMath", namespaces):
                # 检查omath的父元素是否包含这个run
                for parent in para.iter():
                    if omath in list(parent.iter()):
                        if run in list(parent.iter()):
                            return True
            
            for omathPara in para.findall(".//m:oMathPara", namespaces):
                for parent in para.iter():
                    if omathPara in list(parent.iter()):
                        if run in list(parent.iter()):
                            return True
            
            # 3. 检查run的父元素链中是否有公式命名空间
            for elem in run.iter():
                if math_ns in str(elem.tag):
                    return True
            
            # 4. 检查run是否紧邻公式对象（在段落级别）
            # 获取段落的所有直接子元素
            para_children = list(para)
            
            # 找到包含这个run的元素在段落中的位置
            run_container_index = -1
            for i, child in enumerate(para_children):
                if run in list(child.iter()):
                    run_container_index = i
                    break
            
            if run_container_index >= 0:
                # 检查前后是否有公式对象
                if run_container_index > 0:
                    prev_elem = para_children[run_container_index - 1]
                    if prev_elem.find(".//m:oMath", namespaces) is not None or "oMath" in str(prev_elem.tag):
                        return True
                
                if run_container_index < len(para_children) - 1:
                    next_elem = para_children[run_container_index + 1]
                    if next_elem.find(".//m:oMath", namespaces) is not None or "oMath" in str(next_elem.tag):
                        return True
    
    return False


def check_chinese_quotes(docx_path, check_english_quotes=True, check_quote_matching=True, target_paragraphs=None):
    """
    检查中文引号格式问题。
    
    Args:
        docx_path: Word文档路径
        check_english_quotes: 是否检查英文引号包围中文
        check_quote_matching: 是否检查中文引号匹配
        
    Returns:
        包含检查结果的字典
    """
    english_quote_issues = []
    quote_matching_issues = []
    
    # 定义引号对
    quote_pairs = {
        '\u201c': '\u201d',  # 中文双引号："（左）和 "（右）
        '\u2018': '\u2019',  # 中文单引号：'（左）和 '（右）
        '《': '》',  # 书名号
        '「': '」',  # 方括号
        '『': '』',  # 方括号
    }
    
    try:
        with zipfile.ZipFile(docx_path, "r") as docx:
            if "word/document.xml" not in docx.namelist():
                return {
                    "found": False,
                    "message": "Document body not found",
                    "details": {
                        "english_quotes": [],
                        "quote_matching": []
                    },
                }

            document_xml = docx.read("word/document.xml")
            root = ET.fromstring(document_xml)

            namespaces = {
                "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
                "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
            }

            body = root.find(".//w:body", namespaces)
            if body is None:
                return {
                    "found": False,
                    "message": "Document body not found",
                    "details": {
                        "english_quotes": [],
                        "quote_matching": []
                    },
                }

            paragraphs = body.findall(".//w:p", namespaces)
            first_page_end = find_first_page_end(paragraphs, namespaces, body)
            
            for para_idx, para in enumerate(paragraphs, 1):
                # 跳过封面页
                if para_idx - 1 <= first_page_end:
                    continue
                
                # 跳过表格单元格中的段落
                if para.find(".//w:tc", namespaces) is not None:
                    continue
                
                # 获取段落文本
                text_elements = para.findall(".//w:t", namespaces)
                para_text = "".join([t.text for t in text_elements if t.text])
                
                if not para_text.strip():
                    continue
                
                # 建立文本位置到文本元素的映射
                text_positions = []
                current_pos = 0
                for text_elem in text_elements:
                    if text_elem.text:
                        text_positions.append({
                            'element': text_elem,
                            'start': current_pos,
                            'end': current_pos + len(text_elem.text),
                            'text': text_elem.text
                        })
                        current_pos += len(text_elem.text)
                
                # 检查英文引号包围中文
                if check_english_quotes:
                    # 检查英文双引号 "中文"
                    pattern_double = r'"([^"]*[\u4e00-\u9fff]+[^"]*)"'
                    matches_double = list(re.finditer(pattern_double, para_text))
                    for match in matches_double:
                        # 检查匹配范围内的文本元素是否在公式上下文中
                        in_formula = False
                        for tp in text_positions:
                            if match.start() < tp['end'] and match.end() > tp['start']:
                                if is_text_in_formula_context(tp['element'], para, namespaces):
                                    in_formula = True
                                    break
                        
                        # 如果不在公式上下文中，才标记为错误
                        if not in_formula:
                            english_quote_issues.append({
                                "paragraph": para_idx,
                                "page": estimate_page_from_paragraph(para_idx, len(paragraphs)),
                                "text": match.group(0),
                                "position": match.start(),
                                "context": para_text[max(0, match.start() - 20):match.end() + 20],
                                "type": "英文双引号"
                            })
                    
                    # 检查英文单引号 '中文'
                    pattern_single = r"'([^']*[\u4e00-\u9fff]+[^']*)'"
                    matches_single = list(re.finditer(pattern_single, para_text))
                    for match in matches_single:
                        # 检查匹配范围内的文本元素是否在公式上下文中
                        in_formula = False
                        for tp in text_positions:
                            if match.start() < tp['end'] and match.end() > tp['start']:
                                if is_text_in_formula_context(tp['element'], para, namespaces):
                                    in_formula = True
                                    break
                        
                        # 如果不在公式上下文中，才标记为错误
                        if not in_formula:
                            english_quote_issues.append({
                                "paragraph": para_idx,
                                "page": estimate_page_from_paragraph(para_idx, len(paragraphs)),
                                "text": match.group(0),
                                "position": match.start(),
                                "context": para_text[max(0, match.start() - 20):match.end() + 20],
                                "type": "英文单引号"
                            })
                
                # 检查中文引号匹配
                if check_quote_matching:
                    for left_quote, right_quote in quote_pairs.items():
                        # 使用栈来检查引号匹配（类似括号匹配算法）
                        stack = []  # 栈，存储左引号的位置
                        unmatched_right = []  # 未匹配的右引号位置
                        two_left_with_chinese = []  # 两个左引号中间有中文的情况
                        
                        # 遍历文本，检查引号匹配
                        for i, char in enumerate(para_text):
                            if char == left_quote:
                                # 遇到左引号
                                if stack:
                                    # 栈不为空，说明前面有未匹配的左引号
                                    # 检查两个左引号之间是否有中文
                                    prev_left_pos = stack[-1]
                                    text_between = para_text[prev_left_pos + 1:i]
                                    # 检查中间是否有中文
                                    if any('\u4e00' <= c <= '\u9fff' for c in text_between):
                                        two_left_with_chinese.append((prev_left_pos, i))
                                # 将当前左引号位置入栈
                                stack.append(i)
                            elif char == right_quote:
                                # 遇到右引号
                                if stack:
                                    # 栈不为空，有对应的左引号，出栈
                                    stack.pop()
                                else:
                                    # 栈为空，说明这个右引号没有对应的左引号
                                    unmatched_right.append(i)
                        
                        # 栈中剩余的左引号都是未匹配的
                        unmatched_left = stack
                        
                        # 统计引号数量（用于报告）
                        left_count = para_text.count(left_quote)
                        right_count = para_text.count(right_quote)
                        
                        # 报告"两个左引号中间有中文"的问题
                        for left_pos1, left_pos2 in two_left_with_chinese:
                            context_start = max(0, left_pos1 - 30)
                            context_end = min(len(para_text), left_pos2 + 50)
                            context = para_text[context_start:context_end]
                            
                            quote_matching_issues.append({
                                "paragraph": para_idx,
                                "page": estimate_page_from_paragraph(para_idx, len(paragraphs)),
                                "quote_type": f"{left_quote}{right_quote}",
                                "left_count": left_count,
                                "right_count": right_count,
                                "text": para_text[:100] if len(para_text) > 100 else para_text,
                                "context": context
                            })
                        
                        # 报告未匹配的引号问题
                        if unmatched_left or unmatched_right:
                            # 优先使用未匹配的右引号位置（因为通常是缺少左引号）
                            if unmatched_right:
                                quote_pos = unmatched_right[0]
                            elif unmatched_left:
                                quote_pos = unmatched_left[0]
                            else:
                                quote_pos = 0
                            
                            context_start = max(0, quote_pos - 30)
                            context_end = min(len(para_text), quote_pos + 50)
                            context = para_text[context_start:context_end]
                            
                            quote_matching_issues.append({
                                "paragraph": para_idx,
                                "page": estimate_page_from_paragraph(para_idx, len(paragraphs)),
                                "quote_type": f"{left_quote}{right_quote}",
                                "left_count": left_count,
                                "right_count": right_count,
                                "text": para_text[:100] if len(para_text) > 100 else para_text,
                                "context": context
                            })
    
    except Exception as e:
        return {
            "found": False,
            "message": f"Error checking Chinese quotes: {e}",
            "details": {
                "english_quotes": [],
                "quote_matching": []
            },
        }

    total_issues = len(english_quote_issues) + len(quote_matching_issues)
    
    if total_issues > 0:
        message_parts = []
        if english_quote_issues:
            message_parts.append(f"{len(english_quote_issues)} 处英文引号问题")
        if quote_matching_issues:
            message_parts.append(f"{len(quote_matching_issues)} 处引号匹配问题")
        message = f"发现 {' 和 '.join(message_parts)}"
        
        return {
            "found": True,
            "message": message,
            "details": {
                "english_quotes": english_quote_issues,
                "quote_matching": quote_matching_issues
            },
        }
    else:
        return {
            "found": False,
            "message": "未发现中文引号格式问题",
            "details": {
                "english_quotes": [],
                "quote_matching": []
            },
        }

