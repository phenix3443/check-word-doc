#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重复和未引用文献对照分析报告生成器

该脚本用于分析总报告中的重复文献和未引用文献在各课题报告中的分布情况，
并生成详细的对照分析报告。

使用方法:
    python generate_reference_analysis.py --main-report <主报告路径> --subject-reports <课题报告目录> [--output <输出文件>]

示例:
    python generate_reference_analysis.py \
        --main-report "/path/to/main-report.docx" \
        --subject-reports "/path/to/subject-reports/" \
        --output "reference_analysis.md"
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Tuple, Optional, Set
import re

# 添加脚本目录到路径，以便导入其他模块
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

try:
    from references import check_unreferenced_references
    from config_loader import ConfigLoader
except ImportError as e:
    print(f"错误: 无法导入必要模块: {e}")
    print("请确保 references.py 和 config_loader.py 在同一目录下")
    sys.exit(1)


class ReferenceAnalyzer:
    """参考文献分析器"""

    def __init__(self):
        self.main_report_data = {}
        self.subject_reports_data = {}
        self.analysis_result = {}

    def analyze_main_report(self, main_report_path: str) -> Dict:
        """分析主报告的参考文献"""
        print(f"正在分析主报告: {main_report_path}")

        try:
            result = check_unreferenced_references(main_report_path)

            # 提取基本信息
            main_data = {
                'path': main_report_path,
                'filename': Path(main_report_path).name,
                'total_references': len(result.get('references', [])),
                'cited_references': len(result.get('references', [])) - len(result.get('unreferenced', [])),
                'unreferenced_references': result.get('unreferenced', []),
                'duplicate_groups': result.get('duplicates', []),
                'references': result.get('references', []),
                'non_existent_citations': result.get('non_existent_citations', []),
                'citations_not_superscript': result.get('citations_not_superscript', [])
            }

            self.main_report_data = main_data
            print(f"✓ 主报告分析完成: {main_data['total_references']} 条参考文献")
            return main_data

        except Exception as e:
            print(f"✗ 分析主报告时出错: {e}")
            return {}

    def analyze_subject_reports(self, subject_reports_dir: str) -> Dict:
        """分析课题报告的参考文献"""
        print(f"正在分析课题报告目录: {subject_reports_dir}")

        subject_data = {}
        subject_dir = Path(subject_reports_dir)

        if not subject_dir.exists():
            print(f"✗ 课题报告目录不存在: {subject_reports_dir}")
            return {}

        # 查找所有课题子目录
        for subject_folder in sorted(subject_dir.iterdir()):
            if not subject_folder.is_dir():
                continue

            subject_name = subject_folder.name
            print(f"  分析 {subject_name}...")

            # 查找该课题的科技报告文档
            docx_files = list(subject_folder.glob("*科技报告*.docx"))

            if not docx_files:
                print(f"    ⚠️ 未找到科技报告文档")
                subject_data[subject_name] = {
                    'status': 'no_report',
                    'message': '未找到科技报告文档'
                }
                continue

            # 使用第一个找到的文档
            report_file = docx_files[0]

            try:
                result = check_unreferenced_references(str(report_file))

                subject_data[subject_name] = {
                    'status': 'success',
                    'path': str(report_file),
                    'filename': report_file.name,
                    'total_references': len(result.get('references', [])),
                    'cited_references': len(result.get('references', [])) - len(result.get('unreferenced', [])),
                    'unreferenced_references': result.get('unreferenced', []),
                    'duplicate_groups': result.get('duplicates', []),
                    'references': result.get('references', []),
                    'format': 'standard'
                }

                print(f"    ✓ {subject_data[subject_name]['total_references']} 条参考文献")

            except Exception as e:
                # 尝试检查是否是尾注格式
                if self._check_endnotes_format(str(report_file)):
                    try:
                        endnotes_data = self._analyze_endnotes(str(report_file))
                        subject_data[subject_name] = {
                            'status': 'success',
                            'path': str(report_file),
                            'filename': report_file.name,
                            'total_references': endnotes_data['total'],
                            'cited_references': endnotes_data['cited'],
                            'unreferenced_references': endnotes_data['unreferenced'],
                            'duplicate_groups': [],
                            'references': endnotes_data['references'],
                            'format': 'endnotes'
                        }
                        print(f"    ✓ {endnotes_data['total']} 条参考文献 (尾注格式)")
                    except Exception as e2:
                        print(f"    ✗ 尾注分析失败: {e2}")
                        # 如果尾注分析也失败，但检测到0个参考文献，可能是正常情况
                        if "Found 0 references" in str(e):
                            subject_data[subject_name] = {
                                'status': 'success',
                                'path': str(report_file),
                                'filename': report_file.name,
                                'total_references': 0,
                                'cited_references': 0,
                                'unreferenced_references': [],
                                'duplicate_groups': [],
                                'references': [],
                                'format': 'standard'
                            }
                            print(f"    ⚠️ 未发现参考文献")
                        else:
                            subject_data[subject_name] = {
                                'status': 'error',
                                'message': str(e2)
                            }
                else:
                    print(f"    ✗ 分析失败: {e}")
                    # 如果是因为找不到参考文献而失败，标记为成功但无参考文献
                    if "Found 0 references" in str(e) or "No references found" in str(e):
                        subject_data[subject_name] = {
                            'status': 'success',
                            'path': str(report_file),
                            'filename': report_file.name,
                            'total_references': 0,
                            'cited_references': 0,
                            'unreferenced_references': [],
                            'duplicate_groups': [],
                            'references': [],
                            'format': 'standard'
                        }
                        print(f"    ⚠️ 未发现参考文献")
                    else:
                        subject_data[subject_name] = {
                            'status': 'error',
                            'message': str(e)
                        }

        self.subject_reports_data = subject_data
        print(f"✓ 课题报告分析完成: {len(subject_data)} 个课题")
        return subject_data

    def _check_endnotes_format(self, docx_path: str) -> bool:
        """检查文档是否使用尾注格式"""
        try:
            import zipfile
            from xml.etree import ElementTree as ET

            with zipfile.ZipFile(docx_path, 'r') as docx:
                try:
                    endnotes_xml = docx.read('word/endnotes.xml')
                    return True
                except KeyError:
                    return False
        except:
            return False

    def _analyze_endnotes(self, docx_path: str) -> Dict:
        """分析尾注格式的参考文献"""
        import zipfile
        from xml.etree import ElementTree as ET

        with zipfile.ZipFile(docx_path, 'r') as docx:
            # 提取尾注
            endnotes_xml = docx.read('word/endnotes.xml')
            endnotes_root = ET.fromstring(endnotes_xml)

            endnotes = endnotes_root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}endnote')
            references = []

            for endnote in endnotes:
                endnote_id = endnote.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id', '')
                if endnote_id and endnote_id != '-1':
                    endnote_text = ''
                    for text_elem in endnote.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                        if text_elem.text:
                            endnote_text += text_elem.text

                    if endnote_text.strip():
                        references.append({
                            'number': int(endnote_id) if endnote_id.isdigit() else len(references) + 1,
                            'content': endnote_text.strip()
                        })

            # 检查主文档中的尾注引用
            document_xml = docx.read('word/document.xml')
            doc_root = ET.fromstring(document_xml)

            endnote_refs = doc_root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}endnoteReference')
            cited_ids = set()
            for ref in endnote_refs:
                ref_id = ref.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
                if ref_id:
                    cited_ids.add(int(ref_id) if ref_id.isdigit() else 0)

            # 计算未引用的
            all_ids = set(ref['number'] for ref in references)
            unreferenced_ids = list(all_ids - cited_ids)

            return {
                'total': len(references),
                'cited': len(cited_ids),
                'unreferenced': unreferenced_ids,
                'references': references
            }

    def find_matching_references(self) -> Dict:
        """查找主报告和课题报告中的匹配参考文献"""
        print("正在匹配参考文献...")

        if not self.main_report_data or not self.subject_reports_data:
            print("✗ 缺少主报告或课题报告数据")
            return {}

        # 处理主报告参考文献数据结构
        main_refs = {}
        for ref in self.main_report_data.get('references', []):
            if isinstance(ref, dict):
                number = ref.get('number', 0)
                # 尝试不同的内容字段名
                content = ref.get('content', '') or ref.get('text', '') or ref.get('full_text', '')
            else:
                # 如果是其他格式，尝试适配
                number = getattr(ref, 'number', 0) if hasattr(ref, 'number') else 0
                content = getattr(ref, 'content', '') or getattr(ref, 'text', '') or str(ref)
            main_refs[number] = content

        matches = {}

        for subject_name, subject_data in self.subject_reports_data.items():
            if subject_data.get('status') != 'success':
                continue

            # 处理课题报告参考文献数据结构
            subject_refs = {}
            for ref in subject_data.get('references', []):
                if isinstance(ref, dict):
                    number = ref.get('number', 0)
                    # 尝试不同的内容字段名
                    content = ref.get('content', '') or ref.get('text', '') or ref.get('full_text', '')
                else:
                    number = getattr(ref, 'number', 0) if hasattr(ref, 'number') else 0
                    content = getattr(ref, 'content', '') or getattr(ref, 'text', '') or str(ref)
                subject_refs[number] = content
            subject_matches = []

            # 简单的文本匹配
            for main_num, main_content in main_refs.items():
                for subject_num, subject_content in subject_refs.items():
                    if self._is_similar_reference(main_content, subject_content):
                        subject_matches.append({
                            'main_number': main_num,
                            'subject_number': subject_num,
                            'content': main_content[:100] + "..." if len(main_content) > 100 else main_content,
                            'similarity': self._calculate_similarity(main_content, subject_content)
                        })

            matches[subject_name] = subject_matches

        return matches

    def _is_similar_reference(self, ref1: str, ref2: str, threshold: float = 0.8) -> bool:
        """判断两个参考文献是否相似"""
        # 简化的相似度判断
        ref1_clean = re.sub(r'[^\w\s]', '', ref1.lower())
        ref2_clean = re.sub(r'[^\w\s]', '', ref2.lower())

        # 检查关键词匹配
        words1 = set(ref1_clean.split())
        words2 = set(ref2_clean.split())

        if not words1 or not words2:
            return False

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        similarity = len(intersection) / len(union) if union else 0
        return similarity >= threshold

    def _calculate_similarity(self, ref1: str, ref2: str) -> float:
        """计算两个参考文献的相似度"""
        ref1_clean = re.sub(r'[^\w\s]', '', ref1.lower())
        ref2_clean = re.sub(r'[^\w\s]', '', ref2.lower())

        words1 = set(ref1_clean.split())
        words2 = set(ref2_clean.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def generate_analysis_report(self, output_path: str = None) -> str:
        """生成分析报告"""
        print("正在生成分析报告...")

        if not output_path:
            output_path = f"reference_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        # 查找匹配的参考文献
        matches = self.find_matching_references()

        # 生成报告内容
        report_content = self._generate_report_content(matches)

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"✓ 分析报告已生成: {output_path}")
        return output_path

    def _generate_report_content(self, matches: Dict) -> str:
        """生成报告内容"""
        content = []

        # 标题和基本信息
        content.append("# 总报告重复文献和未引用文献在各课题中的对应分析\n")

        # 总报告信息
        content.append("## 总报告参考文献检查结果")
        content.append(f"**文档**: {self.main_report_data.get('filename', 'N/A')}")
        content.append(f"**总参考文献**: {self.main_report_data.get('total_references', 0)} 条")
        content.append(f"**未引用文献**: {len(self.main_report_data.get('unreferenced_references', []))} 条")
        content.append(f"**重复文献**: {len(self.main_report_data.get('duplicate_groups', []))} 组")
        content.append("")
        content.append("---\n")

        # 重复文献分析
        content.append("## 一、重复文献在各课题中的分布\n")
        duplicate_groups = self.main_report_data.get('duplicate_groups', [])

        if duplicate_groups:
            for i, group in enumerate(duplicate_groups, 1):
                content.append(f"### 重复组 {i}")

                # 创建表格
                content.append("| 总报告编号 | 文献内容 | " + " | ".join([f"课题 {j}" for j in range(1, 6)]) + " | 状态 |")
                content.append("|" + "|".join(["----------"] * (7 + 5)) + "|")

                for ref in group:
                    ref_num = ref.get('number', 'N/A')
                    ref_text = ref.get('content', '') or ref.get('text', '') or ref.get('full_text', '')
                    ref_content = ref_text[:50] + "..." if len(ref_text) > 50 else ref_text

                    # 检查在各课题中的分布
                    subject_columns = []
                    for j in range(1, 6):
                        subject_name = f"课题{j}"
                        if subject_name in matches:
                            matching_refs = [m for m in matches[subject_name] if m['main_number'] == ref_num]
                            if matching_refs:
                                subject_columns.append(f"[{matching_refs[0]['subject_number']}]")
                            else:
                                subject_columns.append("❌")
                        else:
                            subject_columns.append("❌")

                    # 判断状态
                    status = "被引用" if ref_num not in self.main_report_data.get('unreferenced_references', []) else "未引用"

                    content.append(f"| **[{ref_num}]** | {ref_content} | " + " | ".join(subject_columns) + f" | {status} |")

                content.append("")

                # 分析
                analysis = self._analyze_duplicate_group(group, matches)
                content.append(f"**分析**: {analysis}\n")
        else:
            content.append("未发现重复文献。\n")

        content.append("---\n")

        # 未引用文献分析
        content.append("## 二、未引用文献在各课题中的分布\n")

        unreferenced_refs = self.main_report_data.get('unreferenced_references', [])
        main_refs = {ref['number']: ref.get('content', '') or ref.get('text', '') or ref.get('full_text', '') for ref in self.main_report_data.get('references', [])}

        # 按课题分组显示
        for subject_name in sorted(self.subject_reports_data.keys()):
            if subject_name not in matches:
                continue

            subject_matches = matches[subject_name]
            unreferenced_matches = [m for m in subject_matches if m['main_number'] in unreferenced_refs]

            if unreferenced_matches:
                content.append(f"### 在{subject_name}中找到的未引用文献")
                content.append(f"| 总报告编号 | {subject_name}编号 | 文献内容 | {subject_name}状态 | 总报告状态 |")
                content.append("|------------|-----------|----------|----------|------------|")

                for match in unreferenced_matches:
                    main_num = match['main_number']
                    subject_num = match['subject_number']
                    content_text = match['content']

                    # 检查在课题中的引用状态
                    subject_data = self.subject_reports_data[subject_name]
                    subject_unreferenced = subject_data.get('unreferenced_references', [])
                    subject_status = "❌ 未引用" if subject_num in subject_unreferenced else "✅ 被引用"

                    content.append(f"| [{main_num}] | [{subject_num}] | {content_text} | {subject_status} | ❌ 未引用 |")

                # 统计
                cited_in_subject = len([m for m in unreferenced_matches if m['subject_number'] not in self.subject_reports_data[subject_name].get('unreferenced_references', [])])
                content.append(f"\n**小结**: {subject_name}中有 {len(unreferenced_matches)} 条文献与总报告编号匹配，其中 {cited_in_subject} 条在{subject_name}中被引用但在总报告中未引用，{len(unreferenced_matches) - cited_in_subject} 条在两边都未引用\n")

        # 完全未找到的文献
        all_matched_refs = set()
        for subject_matches in matches.values():
            all_matched_refs.update(m['main_number'] for m in subject_matches)

        unmatched_unreferenced = [ref_num for ref_num in unreferenced_refs if ref_num not in all_matched_refs]

        if unmatched_unreferenced:
            content.append("### 完全未在任何课题中找到的文献")
            content.append("以下文献在总报告中未被引用，且在任何课题报告中都未找到：\n")
            content.append("| 总报告编号 | 文献内容 | 状态 |")
            content.append("|------------|----------|------|")

            for ref_num in unmatched_unreferenced:
                ref_content = main_refs.get(ref_num, 'N/A')[:80] + "..." if len(main_refs.get(ref_num, '')) > 80 else main_refs.get(ref_num, 'N/A')
                content.append(f"| [{ref_num}] | {ref_content} | 总报告特有 |")

            content.append("")

        content.append("---\n")

        # 总结和建议
        content.append("## 三、总结和建议\n")

        content.append("### 重复文献处理建议")
        if duplicate_groups:
            duplicate_refs = []
            for group in duplicate_groups:
                if len(group) > 1:
                    # 建议删除除第一个外的其他重复项
                    to_delete = [ref['number'] for ref in group[1:]]
                    duplicate_refs.extend(to_delete)

            if duplicate_refs:
                content.append(f"1. **删除重复**: 建议删除 {', '.join(f'[{num}]' for num in duplicate_refs)}，保留对应的第一个引用")
                content.append("2. **更新引用**: 删除后需要重新编号并更新文中引用")
                content.append("3. **课题协调**: 通知相关课题组更新其引用编号")
        else:
            content.append("1. **无重复文献**: 未发现重复文献")

        content.append("")

        content.append("### 未引用文献处理建议")

        # 统计各类文献数量
        cited_in_subjects = 0
        completely_unused = 0
        subject_specific = len(unmatched_unreferenced) if 'unmatched_unreferenced' in locals() else 0

        for subject_matches in matches.values():
            for match in subject_matches:
                if match['main_number'] in unreferenced_refs:
                    subject_data = self.subject_reports_data.get(list(matches.keys())[0], {})  # 简化处理
                    if match['subject_number'] not in subject_data.get('unreferenced_references', []):
                        cited_in_subjects += 1
                    else:
                        completely_unused += 1

        content.append(f"1. **课题特有文献**: 约 {cited_in_subjects} 条在课题中被引用但总报告未引用，建议在总报告中添加引用")
        content.append(f"2. **完全未引用**: 约 {completely_unused} 条文献在课题中也未被引用，可考虑删除")
        content.append(f"3. **总报告特有**: {subject_specific} 条文献需要确认是否必要，如不必要可删除")

        content.append("")

        content.append("### 统计汇总")
        content.append(f"- **重复文献**: {len(duplicate_groups)} 组，涉及 {sum(len(group) for group in duplicate_groups)} 条文献")
        content.append(f"- **未引用但在课题中有用**: 约 {cited_in_subjects} 条")
        content.append(f"- **完全未引用**: 约 {completely_unused} 条")
        content.append(f"- **总报告特有未引用**: {subject_specific} 条")

        content.append(f"\n*检查时间：{datetime.now().strftime('%Y-%m-%d')}*")

        return "\n".join(content)

    def _analyze_duplicate_group(self, group: List[Dict], matches: Dict) -> str:
        """分析重复组的分布情况"""
        if len(group) < 2:
            return "无重复"

        # 简化的分析
        ref_nums = [ref['number'] for ref in group]

        # 查找在哪些课题中出现
        appearing_subjects = []
        for subject_name, subject_matches in matches.items():
            subject_refs = [m['main_number'] for m in subject_matches]
            if any(num in subject_refs for num in ref_nums):
                appearing_subjects.append(subject_name)

        if appearing_subjects:
            return f"{', '.join(appearing_subjects)} 中有相关引用"
        else:
            return "未在课题中找到相关引用"


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="生成重复和未引用文献对照分析报告",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s --main-report "总报告.docx" --subject-reports "课题报告目录/"
  %(prog)s --main-report "总报告.docx" --subject-reports "课题报告目录/" --output "分析报告.md"
        """
    )

    parser.add_argument(
        "--main-report", "-m",
        required=True,
        help="主报告文档路径 (.docx)"
    )

    parser.add_argument(
        "--subject-reports", "-s",
        required=True,
        help="课题报告目录路径"
    )

    parser.add_argument(
        "--output", "-o",
        help="输出报告文件路径 (默认: reference_analysis_YYYYMMDD_HHMMSS.md)"
    )

    parser.add_argument(
        "--config", "-c",
        help="自定义配置文件路径"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出"
    )

    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()

    # 设置配置文件
    if args.config:
        os.environ["CHECK_WORD_DOC_CONFIG_PATH"] = args.config

    # 检查输入文件和目录
    if not os.path.exists(args.main_report):
        print(f"错误: 主报告文件不存在: {args.main_report}")
        sys.exit(1)

    if not os.path.exists(args.subject_reports):
        print(f"错误: 课题报告目录不存在: {args.subject_reports}")
        sys.exit(1)

    # 创建分析器
    analyzer = ReferenceAnalyzer()

    try:
        # 分析主报告
        main_data = analyzer.analyze_main_report(args.main_report)
        if not main_data:
            print("错误: 主报告分析失败")
            sys.exit(1)

        # 分析课题报告
        subject_data = analyzer.analyze_subject_reports(args.subject_reports)
        if not subject_data:
            print("错误: 课题报告分析失败")
            sys.exit(1)

        # 生成分析报告
        output_path = analyzer.generate_analysis_report(args.output)

        print(f"\n{'='*60}")
        print("分析完成!")
        print(f"主报告: {main_data['total_references']} 条参考文献")
        print(f"课题报告: {len([s for s in subject_data.values() if s.get('status') == 'success'])} 个成功分析")
        print(f"输出报告: {output_path}")
        print(f"{'='*60}")

    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
