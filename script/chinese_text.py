#!/usr/bin/env python3
"""
Chinese text format checking functions.
检查中文间距和中文引号格式。
"""

import zipfile
import xml.etree.ElementTree as ET
import re
from utils import estimate_page_from_paragraph
from cover import find_first_page_end


def is_chinese_char(char):
    """判断字符是否为中文字符。"""
    return '\u4e00' <= char <= '\u9fff'


def check_chinese_spacing(docx_path):
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
            
            # 检查段落中的中文间距问题
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
                
                # 检查两个中文之间是否只有空格（不能有其他符号）
                # 方法：遍历所有文本元素，检查相邻文本元素之间是否有公式、数学符号等
                # 如果两个中文字符之间只有空格，但XML结构中有其他元素（如公式），不应该标记为问题
                
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
                                
                                # 如果两个中文字符在不同的文本元素中，检查它们之间是否有其他XML元素
                                if text_elem1 is not None and text_elem2 is not None and text_elem1 != text_elem2:
                                    # 检查两个文本元素之间是否有公式、数学符号等元素
                                    # 方法：检查从text_elem1到text_elem2之间的所有元素
                                    has_other_elements = False
                                    
                                    # 获取两个元素的父元素（通常是w:r）
                                    # 检查它们之间是否有其他w:r元素包含公式等
                                    all_runs = para.findall(".//w:r", namespaces)
                                    elem1_run = None
                                    elem2_run = None
                                    
                                    for run in all_runs:
                                        if text_elem1 in list(run.iter()):
                                            elem1_run = run
                                        if text_elem2 in list(run.iter()):
                                            elem2_run = run
                                    
                                    # 如果找到了两个run元素，检查它们之间是否有包含公式的run
                                    if elem1_run is not None and elem2_run is not None:
                                        found_elem1 = False
                                        for run in all_runs:
                                            if run == elem1_run:
                                                found_elem1 = True
                                                continue
                                            if found_elem1:
                                                # 检查这个run是否包含公式、数学符号等
                                                if run.find(".//m:oMath", namespaces) is not None:
                                                    has_other_elements = True
                                                    break
                                                if run.find(".//m:oMathPara", namespaces) is not None:
                                                    has_other_elements = True
                                                    break
                                                # 检查是否有其他非文本内容
                                                math_ns = "http://schemas.openxmlformats.org/officeDocument/2006/math"
                                                for elem in run.iter():
                                                    if math_ns in elem.tag:
                                                        has_other_elements = True
                                                        break
                                                if has_other_elements:
                                                    break
                                            if run == elem2_run:
                                                break
                                    
                                    # 如果有其他元素（如公式、数学符号），跳过这个匹配
                                    if has_other_elements:
                                        continue
                                
                                issues.append({
                                    "paragraph": para_idx,
                                    "page": estimate_page_from_paragraph(para_idx, len(paragraphs)),
                                    "text": full_match,
                                    "position": start_pos,
                                    "context": para_text[max(0, start_pos - 20):end_pos + 20]
                                })
    
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


def check_chinese_quotes(docx_path, check_english_quotes=True, check_quote_matching=True):
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
        '"': '"',  # 双引号
        '\u2018': '\u2019',  # 单引号
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
                
                # 检查英文引号包围中文
                if check_english_quotes:
                    # 检查英文双引号 "中文"
                    pattern_double = r'"([^"]*[\u4e00-\u9fff]+[^"]*)"'
                    matches_double = list(re.finditer(pattern_double, para_text))
                    for match in matches_double:
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
                        # 统计左引号和右引号的数量
                        left_count = para_text.count(left_quote)
                        right_count = para_text.count(right_quote)
                        
                        if left_count != right_count:
                            # 找到不匹配的位置
                            quote_matching_issues.append({
                                "paragraph": para_idx,
                                "page": estimate_page_from_paragraph(para_idx, len(paragraphs)),
                                "quote_type": f"{left_quote}{right_quote}",
                                "left_count": left_count,
                                "right_count": right_count,
                                "text": para_text[:100] if len(para_text) > 100 else para_text,
                                "context": para_text[max(0, para_text.find(left_quote) - 20):min(len(para_text), para_text.find(left_quote) + 50)] if left_quote in para_text else para_text[:50]
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

