#!/usr/bin/env python3
"""
Paragraph format checking functions.
段落格式检查功能，包括：
- 段落标点符号检查
- 中文间距检查  
- 中文引号检查
- 连续空行检查

可以针对不同文档部分的段落进行检查（如：正文、参考文献等）
"""

from chinese_text import check_chinese_spacing, check_chinese_quotes
from empty_lines import check_consecutive_empty_lines
from config_loader import ConfigLoader
import zipfile
import xml.etree.ElementTree as ET


def _is_check_enabled(config_loader, check_name, item_config):
    """
    Check if a specific check is enabled.
    
    Args:
        config_loader: ConfigLoader instance
        check_name: Name of the check (e.g., "cover", "page_numbers")
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


def run_paragraphs_check(docx_path, config_loader=None, structure=None):
    """Run paragraphs check (includes spacing, quotes, empty lines) based on Word styles."""
    print("Checking paragraphs...")
    try:
        if config_loader is None:
            config_loader = ConfigLoader()
        # 确保配置已加载
        if hasattr(config_loader, 'config') and config_loader.config:
            config = config_loader.config
        else:
            config = config_loader.load()
        
        # 从 paragraphs 配置中获取设置
        paragraphs_config = config.get("paragraphs", {})
        
        # Check if check is enabled
        if not _is_check_enabled(config_loader, "paragraphs", paragraphs_config):
            result = {
                "found": False,
                "message": "Paragraphs check is disabled",
                "details": {
                    "spacing": [],
                    "quotes": {"english_quotes": [], "quote_matching": []},
                    "empty_lines": []
                },
            }
            print(f"   Result: {result['message']}")
            return result
        
        # 获取要检查的样式
        check_styles = paragraphs_config.get("check_styles", ["Normal", "正文"])
        
        # 根据Word样式确定要检查的段落
        target_paragraphs = _get_paragraphs_by_styles(docx_path, check_styles)
        
        if not target_paragraphs:
            result = {
                "found": False,
                "message": f"No paragraphs found with styles: {check_styles}",
                "details": {
                    "spacing": [],
                    "quotes": {"english_quotes": [], "quote_matching": []},
                    "empty_lines": []
                },
            }
            print(f"   Result: {result['message']}")
            return result
        
        all_issues = []
        all_details = {
            "spacing": [],
            "quotes": {"english_quotes": [], "quote_matching": []},
            "empty_lines": []
        }
        
        # 检查中文间距（针对指定部分的段落）
        spacing_config = paragraphs_config.get("spacing", {})
        if spacing_config.get("chinese_spacing", False):
            spacing_result = run_chinese_spacing_check(docx_path, config_loader, target_paragraphs)
            if spacing_result.get("found"):
                all_issues.extend(spacing_result.get("details", []))
                all_details["spacing"] = spacing_result.get("details", [])
        
        # 检查中文引号（针对指定部分的段落）
        quotes_config = paragraphs_config.get("quotes", {})
        if quotes_config.get("english_quotes", False) or quotes_config.get("quote_matching", False):
            quotes_result = run_chinese_quotes_check(docx_path, config_loader, target_paragraphs)
            if quotes_result.get("found"):
                quotes_details = quotes_result.get("details", {})
                all_details["quotes"] = quotes_details
                # 将引号问题添加到总问题列表
                if quotes_details.get("english_quotes"):
                    all_issues.extend(quotes_details["english_quotes"])
                if quotes_details.get("quote_matching"):
                    all_issues.extend(quotes_details["quote_matching"])
        
        # 检查空行（针对指定部分的段落）
        empty_lines_config = paragraphs_config.get("empty_lines", {})
        if empty_lines_config.get("consecutive", False):
            empty_lines_result = run_empty_lines_check(docx_path, config_loader, target_paragraphs)
            if empty_lines_result.get("found"):
                all_issues.extend(empty_lines_result.get("details", []))
                all_details["empty_lines"] = empty_lines_result.get("details", [])
        
        # 生成综合结果
        if all_issues:
            result = {
                "found": True,
                "message": f"发现 {len(all_issues)} 个段落格式问题（检查样式：{', '.join(check_styles)}）",
                "details": all_details
            }
        else:
            result = {
                "found": False,
                "message": f"未发现段落格式问题（检查样式：{', '.join(check_styles)}）",
                "details": all_details
            }
        
        print(f"   Result: {result['message']}")
        return result
        
    except Exception as e:
        print(f"   Error checking body paragraphs: {e}")
        return {
            "found": True,
            "message": f"Error: {e}",
            "details": {
                "spacing": [],
                "quotes": {"english_quotes": [], "quote_matching": []},
                "empty_lines": []
            },
            "error": True
        }


def run_chinese_spacing_check(docx_path, config_loader=None, target_paragraphs=None):
    """Run Chinese spacing check."""
    print("Checking Chinese spacing...")
    try:
        if config_loader is None:
            config_loader = ConfigLoader()
        # 确保配置已加载
        if hasattr(config_loader, 'config') and config_loader.config:
            config = config_loader.config
        else:
            config = config_loader.load()
        
        # 从 paragraphs.spacing 配置中获取中文间距检查设置
        paragraphs_config = config.get("paragraphs", {})
        spacing_config = paragraphs_config.get("spacing", {})
        
        # Check if check is enabled
        if not _is_check_enabled(config_loader, "paragraphs", paragraphs_config):
            spacing_check = {
                "found": False,
                "message": "Chinese spacing check is disabled",
                "details": [],
            }
            print(f"   Result: {spacing_check['message']}")
            return spacing_check
        
        # 检查是否启用了中文间距检查
        check_enabled = (
            paragraphs_config.get("enabled", True) and 
            spacing_config.get("chinese_spacing", False)
        )
        
        if check_enabled:
            # 使用指定的目标段落
            if target_paragraphs is None:
                target_paragraphs = []
            spacing_check = check_chinese_spacing(docx_path, target_paragraphs=target_paragraphs)
            print(f"   Result: {spacing_check['message']}")
            
            if spacing_check["found"]:
                print()
                print("   WARNING: Chinese spacing issues found!")
                print(f"   Found {len(spacing_check['details'])} issue(s)")
                if len(spacing_check["details"]) > 20:
                    print("   First 10 locations:")
                    for detail in spacing_check["details"][:10]:
                        print(
                            f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['text']}"
                        )
                    print("   ...")
                else:
                    print("   Locations:")
                    for detail in spacing_check["details"]:
                        print(
                            f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['text']}"
                        )
            else:
                print("   ✓ No Chinese spacing issues found")
        else:
            spacing_check = {
                "found": False,
                "message": "Chinese spacing check is disabled",
                "details": [],
            }
            print(f"   Result: {spacing_check['message']}")
    except Exception as e:
        print(f"   Error loading Chinese spacing config: {e}")
        spacing_check = {
            "found": False,
            "message": f"Error: {e}",
            "details": []
        }

    return spacing_check


def run_chinese_quotes_check(docx_path, config_loader=None, target_paragraphs=None):
    """Run Chinese quotes check."""
    print("Checking Chinese quotes...")
    try:
        if config_loader is None:
            config_loader = ConfigLoader()
        # 确保配置已加载
        if hasattr(config_loader, 'config') and config_loader.config:
            config = config_loader.config
        else:
            config = config_loader.load()
        
        # 从 body_paragraphs.quotes 配置中获取中文引号检查设置
        body_paragraphs_config = config.get("body_paragraphs", {})
        quotes_config = body_paragraphs_config.get("quotes", {})
        
        # Check if check is enabled
        if not _is_check_enabled(config_loader, "body_paragraphs", body_paragraphs_config):
            quotes_check = {
                "found": False,
                "message": "Chinese quotes check is disabled",
                "details": {
                    "english_quotes": [],
                    "quote_matching": []
                },
            }
            print(f"   Result: {quotes_check['message']}")
            return quotes_check
        
        # 检查是否启用了中文引号检查
        check_enabled = (
            body_paragraphs_config.get("enabled", True) and 
            (quotes_config.get("english_quotes", False) or quotes_config.get("quote_matching", False))
        )
        
        if check_enabled:
            check_english_quotes = quotes_config.get("english_quotes", True)
            check_quote_matching = quotes_config.get("quote_matching", True)
            
            # 只检查正文段落
            body_paragraphs = structure.get('document_parts', {}).get('body', {}).get('paragraphs', []) if structure else []
            quotes_check = check_chinese_quotes(
                docx_path,
                check_english_quotes=check_english_quotes,
                check_quote_matching=check_quote_matching,
                target_paragraphs=body_paragraphs
            )
            print(f"   Result: {quotes_check['message']}")
            
            if quotes_check["found"]:
                print()
                print("   WARNING: Chinese quotes issues found!")
                details = quotes_check.get("details", {})
                english_quotes = details.get("english_quotes", [])
                quote_matching = details.get("quote_matching", [])
                
                if english_quotes:
                    print(f"   Found {len(english_quotes)} English quote issue(s)")
                    if len(english_quotes) > 20:
                        print("   First 10 locations:")
                        for detail in english_quotes[:10]:
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['type']} - {detail['text']}"
                            )
                        print("   ...")
                    else:
                        print("   Locations:")
                        for detail in english_quotes:
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['type']} - {detail['text']}"
                            )
                
                if quote_matching:
                    print(f"   Found {len(quote_matching)} quote matching issue(s)")
                    if len(quote_matching) > 20:
                        print("   First 10 locations:")
                        for detail in quote_matching[:10]:
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['quote_type']} (左: {detail['left_count']}, 右: {detail['right_count']})"
                            )
                        print("   ...")
                    else:
                        print("   Locations:")
                        for detail in quote_matching:
                            print(
                                f"      - Paragraph {detail['paragraph']} (Page ~{detail['page']}): {detail['quote_type']} (左: {detail['left_count']}, 右: {detail['right_count']})"
                            )
            else:
                print("   ✓ No Chinese quotes issues found")
        else:
            quotes_check = {
                "found": False,
                "message": "Chinese quotes check is disabled",
                "details": {
                    "english_quotes": [],
                    "quote_matching": []
                },
            }
            print(f"   Result: {quotes_check['message']}")
    except Exception as e:
        print(f"   Error loading Chinese quotes config: {e}")
        quotes_check = {
            "found": False,
            "message": f"Error: {e}",
            "details": {
                "english_quotes": [],
                "quote_matching": []
            }
        }

    return quotes_check


def run_empty_lines_check(docx_path, config_loader=None, target_paragraphs=None):
    """Run empty lines check."""
    print("Checking for consecutive empty lines...")
    try:
        if config_loader is None:
            import os
            config_path = os.environ.get('CUSTOM_CONFIG_PATH')
            if not config_path:
                raise ValueError("Configuration file path is required. Please specify a config file using --config option.")
            config_loader = ConfigLoader(config_path)
        config = config_loader.load()
        
        # 从 body_paragraphs.empty_lines 配置中获取空行检查设置
        body_paragraphs_config = config.get("body_paragraphs", {})
        empty_lines_config = body_paragraphs_config.get("empty_lines", {})
        
        # Check if check is enabled
        if not _is_check_enabled(config_loader, "body_paragraphs", body_paragraphs_config):
            empty_lines_check = {
                "found": False,
                "message": "Empty lines check is disabled",
                "details": [],
            }
            print(f"   Result: {empty_lines_check['message']}")
            return empty_lines_check
        
        # 检查是否启用了空行检查
        check_enabled = (
            body_paragraphs_config.get("enabled", True) and 
            empty_lines_config.get("consecutive", False)
        )
        
        if check_enabled:
            max_consecutive = empty_lines_config.get("max_consecutive")
            if max_consecutive is None:
                raise ValueError("max_consecutive not specified in config file (body_paragraphs.empty_lines.max_consecutive)")
            
            # 只检查正文段落
            body_paragraphs = structure.get('document_parts', {}).get('body', {}).get('paragraphs', []) if structure else []
            empty_lines_check = check_consecutive_empty_lines(
                docx_path, max_consecutive=max_consecutive, target_paragraphs=body_paragraphs
            )
            print(f"   Result: {empty_lines_check['message']}")
            
            if empty_lines_check["found"]:
                print()
                print("   警告：发现连续空行！")
                print(f"   发现 {len(empty_lines_check['details'])} 组连续空行")
                print("   位置：")
                for detail in empty_lines_check["details"]:
                    start_para = detail.get("start", detail.get("start_paragraph", "N/A"))
                    end_para = detail.get("end", detail.get("end_paragraph", "N/A"))
                    count = detail.get("count", detail.get("consecutive_count", "N/A"))
                    page = detail.get("estimated_start_page", "N/A")
                    print(f"      - 段落 {start_para} 到 {end_para}：{count} 个连续空行 (第 ~{page} 页)")
            else:
                print("   ✓ 未发现连续空行")
                
            print(f"   Total paragraphs in document: {empty_lines_check.get('total_paragraphs', 'N/A')}")
        else:
            empty_lines_check = {
                "found": False,
                "message": "Empty lines check is disabled",
                "details": [],
            }
            print(f"   Result: {empty_lines_check['message']}")
    except Exception as e:
        print(f"   Error loading empty lines config: {e}")
        empty_lines_check = {
            "found": False,
            "message": f"Error: {e}",
            "details": []
        }

    return empty_lines_check


def _get_paragraphs_by_styles(docx_path, target_styles):
    """根据Word样式获取段落索引列表"""
    target_paragraphs = []
    
    try:
        with zipfile.ZipFile(docx_path, 'r') as docx:
            document_xml = docx.read('word/document.xml')
            root = ET.fromstring(document_xml)
            
            namespaces = {
                'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
            }
            
            paragraphs = root.findall('.//w:p', namespaces)
            
            for i, para in enumerate(paragraphs):
                # 获取段落样式
                pPr = para.find('w:pPr', namespaces)
                style_val = None
                
                if pPr is not None:
                    pStyle = pPr.find('w:pStyle', namespaces)
                    if pStyle is not None:
                        style_val = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                
                # 检查样式是否匹配
                if _is_target_style(style_val, target_styles):
                    target_paragraphs.append(i)
    
    except Exception as e:
        print(f"Error getting paragraphs by styles: {e}")
    
    return target_paragraphs


def _is_target_style(style_val, target_styles):
    """判断样式是否为目标样式"""
    if not target_styles:
        return False
    
    # 如果没有样式，检查是否包含 None 或 Normal
    if not style_val:
        return any(style.lower() in ['none', 'normal', '正文'] for style in target_styles)
    
    # 直接匹配
    if style_val in target_styles:
        return True
    
    # 忽略大小写匹配
    style_lower = style_val.lower()
    for target_style in target_styles:
        if style_lower == target_style.lower():
            return True
    
    # 特殊处理：Normal 样式可能对应无样式的段落
    if style_val.lower() == 'normal' and any(style.lower() in ['none', '正文'] for style in target_styles):
        return True
    
    return False