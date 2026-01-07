#!/usr/bin/env python3
"""
Script to check which references are not cited in the document and identify duplicate references.
"""

import zipfile
import xml.etree.ElementTree as ET
import re
from pathlib import Path
import sys
from datetime import datetime


def extract_text_from_docx(docx_path):
    """Extract all text content from Word document."""
    try:
        with zipfile.ZipFile(docx_path, "r") as docx:
            if "word/document.xml" not in docx.namelist():
                return None

            document_xml = docx.read("word/document.xml")
            root = ET.fromstring(document_xml)

            namespaces = {
                "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            }

            paragraphs = []
            for para in root.findall(".//w:p", namespaces):
                text_elements = para.findall(".//w:t", namespaces)
                para_text = "".join([t.text for t in text_elements if t.text])
                paragraphs.append(para_text)

            return paragraphs
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None


def extract_references_from_xml(docx_path):
    """Extract references from XML, handling Word auto-numbering."""
    try:
        with zipfile.ZipFile(docx_path, "r") as docx:
            document_xml = docx.read("word/document.xml")
            root = ET.fromstring(document_xml)

            namespaces = {
                "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            }

            paragraphs = root.findall(".//w:p", namespaces)

            # Find references section
            ref_start_idx = None
            for i, para in enumerate(paragraphs):
                text_elements = para.findall(".//w:t", namespaces)
                para_text = "".join([t.text for t in text_elements if t.text])
                if para_text.strip() == "参考文献":
                    ref_start_idx = i
                    break

            if ref_start_idx is None:
                return []

            # Find the numbering ID used for references
            # Check paragraphs after "参考文献" to find the numbering pattern
            ref_num_id = None
            for i in range(ref_start_idx + 1, min(ref_start_idx + 10, len(paragraphs))):
                para = paragraphs[i]
                num_pr = para.find(".//w:numPr", namespaces)
                if num_pr is not None:
                    num_id_elem = num_pr.find(".//w:numId", namespaces)
                    if num_id_elem is not None:
                        ref_num_id = num_id_elem.get(
                            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
                        )
                        break

            if ref_num_id is None:
                # Fallback to text-based extraction
                return []

            # Extract references with auto-numbering
            references = []
            ref_count = 0

            for i in range(ref_start_idx + 1, len(paragraphs)):
                para = paragraphs[i]

                # Check if this paragraph has the reference numbering
                num_pr = para.find(".//w:numPr", namespaces)
                if num_pr is not None:
                    num_id_elem = num_pr.find(".//w:numId", namespaces)
                    if num_id_elem is not None:
                        para_num_id = num_id_elem.get(
                            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
                        )
                        if para_num_id == ref_num_id:
                            ref_count += 1

                            # Extract text
                            text_elements = para.findall(".//w:t", namespaces)
                            para_text = "".join(
                                [t.text for t in text_elements if t.text]
                            ).strip()

                            if para_text:
                                references.append(
                                    {
                                        "number": ref_count,
                                        "text": para_text,
                                        "full_text": para_text,
                                    }
                                )

                # Check for end markers
                text_elements = para.findall(".//w:t", namespaces)
                para_text = "".join([t.text for t in text_elements if t.text]).strip()
                if para_text.startswith("附录") or para_text.startswith("后记"):
                    break

            return references

    except Exception as e:
        print(f"Error extracting references from XML: {e}")
        return []


def extract_references(paragraphs):
    """Extract reference list from document."""
    references = []
    in_references_section = False
    reference_start_pattern = re.compile(r"^参考文献$", re.IGNORECASE)
    reference_end_patterns = [
        re.compile(r"^附录", re.IGNORECASE),
        re.compile(r"^后记", re.IGNORECASE),
    ]

    ref_num = 1
    current_ref = None

    for i, para in enumerate(paragraphs):
        para_stripped = para.strip()

        if not in_references_section:
            if reference_start_pattern.match(para_stripped):
                next_para = paragraphs[i + 1].strip() if i + 1 < len(paragraphs) else ""
                if next_para and (
                    next_para[0].isupper()
                    or next_para.startswith("http")
                    or "[EB/OL]" in next_para
                    or re.match(r"^[A-Z]", next_para)
                ):
                    in_references_section = True
                    continue
        else:
            if any(pattern.match(para_stripped) for pattern in reference_end_patterns):
                if current_ref:
                    references.append(current_ref)
                    current_ref = None
                break

            if not para_stripped:
                continue

            ref_match = re.match(r"^\[?(\d+)\]?\s*(.+)", para_stripped)
            if ref_match:
                if current_ref:
                    references.append(current_ref)
                ref_num_from_text = int(ref_match.group(1))
                ref_text = ref_match.group(2).strip()
                current_ref = {
                    "number": ref_num_from_text,
                    "text": ref_text,
                    "full_text": para_stripped,
                }
                ref_num = ref_num_from_text + 1
            else:
                is_chinese_ref = (
                    len(para_stripped) > 0
                    and "\u4e00" <= para_stripped[0] <= "\u9fff"
                    and (
                        "." in para_stripped[:50]
                        or "，" in para_stripped[:50]
                        or "、" in para_stripped[:50]
                    )
                )
                looks_like_ref_start = (
                    re.match(r"^[A-Z][a-z]+", para_stripped)
                    or re.match(r"^[A-Z]\.", para_stripped)
                    or re.match(r"^[A-Z][a-z]+\s+[A-Z]", para_stripped)
                    or re.match(r"^[A-Z][a-z]+,\s+[A-Z]", para_stripped)
                    or para_stripped.startswith("http")
                    or "[EB/OL]" in para_stripped
                    or is_chinese_ref
                    or para_stripped.startswith('"')
                    or (
                        re.match(r"^[a-z]", para_stripped)
                        and (
                            "http" in para_stripped or "github" in para_stripped.lower()
                        )
                    )
                    or (
                        len(para_stripped) > 0
                        and para_stripped[0].isupper()
                        and not para_stripped.startswith("图")
                        and not para_stripped.startswith("表")
                    )
                )

                if looks_like_ref_start:
                    if current_ref:
                        references.append(current_ref)
                    current_ref = {
                        "number": ref_num,
                        "text": para_stripped,
                        "full_text": para_stripped,
                    }
                    ref_num += 1
                elif current_ref:
                    current_ref["text"] += " " + para_stripped
                    current_ref["full_text"] += " " + para_stripped

    if current_ref and in_references_section:
        references.append(current_ref)

    return references


def extract_citations(paragraphs):
    """Extract all citation numbers from document body."""
    citations = set()

    in_references_section = False
    reference_start_pattern = re.compile(r"^参考文献$", re.IGNORECASE)
    reference_end_patterns = [
        re.compile(r"^附录", re.IGNORECASE),
        re.compile(r"^后记", re.IGNORECASE),
    ]

    for i, para in enumerate(paragraphs):
        para_stripped = para.strip()

        if not in_references_section:
            if reference_start_pattern.match(para_stripped):
                next_para = paragraphs[i + 1].strip() if i + 1 < len(paragraphs) else ""
                if next_para and (
                    next_para[0].isupper()
                    or next_para.startswith("http")
                    or "[EB/OL]" in next_para
                    or re.match(r"^[A-Z]", next_para)
                ):
                    in_references_section = True
                    continue
        else:
            if any(pattern.match(para_stripped) for pattern in reference_end_patterns):
                in_references_section = False
            else:
                continue

        matches = re.findall(r"\[(\d+)\]", para)
        for match in matches:
            citations.add(int(match))

        matches = re.findall(r"\[(\d+)-(\d+)\]", para)
        for start, end in matches:
            start_num, end_num = int(start), int(end)
            citations.update(range(start_num, end_num + 1))

        matches = re.findall(r"\[(\d+),\s*(\d+)\]", para)
        for m1, m2 in matches:
            citations.add(int(m1))
            citations.add(int(m2))

        matches = re.findall(r"\[(\d+),\s*(\d+),\s*(\d+)\]", para)
        for m1, m2, m3 in matches:
            citations.add(int(m1))
            citations.add(int(m2))
            citations.add(int(m3))

        matches = re.findall(r"\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]", para)
        for m1, m2, m3, m4 in matches:
            citations.add(int(m1))
            citations.add(int(m2))
            citations.add(int(m3))
            citations.add(int(m4))

    return citations


def check_citation_superscript_format(docx_path):
    """Check if citation marks are in superscript format."""
    citation_issues = []

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
                "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            }

            body = root.find(".//w:body", namespaces)
            if body is None:
                return {
                    "found": False,
                    "message": "Document body not found",
                    "details": [],
                }

            paragraphs = body.findall(".//w:p", namespaces)

            in_references_section = False
            reference_start_pattern = re.compile(r"^参考文献$", re.IGNORECASE)
            reference_end_patterns = [
                re.compile(r"^附录", re.IGNORECASE),
                re.compile(r"^后记", re.IGNORECASE),
            ]

            def is_superscript(run):
                """Check if a text run is superscript."""
                rPr = run.find(".//w:rPr", namespaces)
                if rPr is not None:
                    vertAlign = rPr.find(".//w:vertAlign", namespaces)
                    if vertAlign is not None:
                        val = vertAlign.get(
                            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
                        )
                        if val == "superscript":
                            return True
                return False

            para_idx = 0
            for para in paragraphs:
                para_idx += 1
                para_text = "".join(
                    [t.text for t in para.findall(".//w:t", namespaces) if t.text]
                )
                para_stripped = para_text.strip()

                if not in_references_section:
                    if reference_start_pattern.match(para_stripped):
                        next_para_idx = para_idx
                        if next_para_idx < len(paragraphs):
                            next_para_text = "".join(
                                [
                                    t.text
                                    for t in paragraphs[next_para_idx].findall(
                                        ".//w:t", namespaces
                                    )
                                    if t.text
                                ]
                            )
                            next_para = next_para_text.strip()
                            if next_para and (
                                next_para[0].isupper()
                                or next_para.startswith("http")
                                or "[EB/OL]" in next_para
                                or re.match(r"^[A-Z]", next_para)
                            ):
                                in_references_section = True
                                continue
                else:
                    if any(
                        pattern.match(para_stripped)
                        for pattern in reference_end_patterns
                    ):
                        in_references_section = False
                    else:
                        continue

                citation_patterns = [
                    (r"\[(\d+)\]", "single"),
                    (r"\[(\d+)-(\d+)\]", "range"),
                    (r"\[(\d+),\s*(\d+)\]", "comma"),
                    (r"\[(\d+),\s*(\d+),\s*(\d+)\]", "comma3"),
                    (r"\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]", "comma4"),
                ]

                runs = para.findall(".//w:r", namespaces)
                run_positions = []
                current_pos = 0

                for run in runs:
                    text_elem = run.find(".//w:t", namespaces)
                    if text_elem is not None and text_elem.text:
                        run_text = text_elem.text
                        is_sup = is_superscript(run)
                        run_positions.append(
                            {
                                "start": current_pos,
                                "end": current_pos + len(run_text),
                                "text": run_text,
                                "is_superscript": is_sup,
                            }
                        )
                        current_pos += len(run_text)

                for pattern, pattern_type in citation_patterns:
                    matches = re.finditer(pattern, para_text)
                    for match in matches:
                        start_pos = match.start()
                        end_pos = match.end()
                        citation_text = match.group(0)

                        citation_is_superscript = False
                        citation_fully_covered = False

                        for run_info in run_positions:
                            run_start = run_info["start"]
                            run_end = run_info["end"]

                            if run_start <= start_pos and end_pos <= run_end:
                                citation_fully_covered = True
                                if run_info["is_superscript"]:
                                    citation_is_superscript = True
                                break
                            elif run_start < end_pos and start_pos < run_end:
                                if run_info["is_superscript"]:
                                    citation_is_superscript = True

                        if not citation_is_superscript or not citation_fully_covered:
                            estimated_page = max(1, int(para_idx / 25) + 1)

                            context_start = max(0, start_pos - 30)
                            context_end = min(len(para_text), end_pos + 30)
                            context = para_text[context_start:context_end]

                            citation_issues.append(
                                {
                                    "paragraph": para_idx,
                                    "estimated_page": estimated_page,
                                    "citation": citation_text,
                                    "position_in_para": start_pos,
                                    "context": context,
                                    "is_superscript": citation_is_superscript,
                                }
                            )

    except Exception as e:
        return {
            "found": False,
            "message": f"Error checking citation format: {e}",
            "details": [],
        }

    if citation_issues:
        return {
            "found": True,
            "message": f"Found {len(citation_issues)} citation(s) not in superscript format",
            "details": citation_issues,
        }
    else:
        return {
            "found": False,
            "message": "All citations are in superscript format",
            "details": [],
        }


def check_duplicate_references(references):
    """Check for duplicate references."""
    duplicates_found = []
    seen_texts = {}

    for ref in references:
        ref_text = ref["full_text"].strip()
        if ref_text in seen_texts:
            duplicates_found.append((seen_texts[ref_text], ref))
        else:
            seen_texts[ref_text] = ref

    return duplicates_found


def extract_keywords_from_reference(ref_text):
    """Extract keywords from reference text for searching."""
    keywords = []
    ref_lower = ref_text.lower()

    author_match = re.search(r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", ref_text)
    if author_match:
        author = author_match.group(1)
        author_parts = author.split()
        keywords.append(author_parts[0].lower())
        if len(author_parts) > 1:
            keywords.append(author_parts[1].lower())

    title_match = re.search(r'[""]([^""]+)[""]', ref_text)
    if title_match:
        title = title_match.group(1)
        title_words = re.findall(r"\b([A-Z][a-z]{4,})\b", title)
        keywords.extend([w.lower() for w in title_words[:4]])
    else:
        title_words = re.findall(r"\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", ref_text)
        if title_words:
            title = title_words[0]
            title_parts = title.split()
            keywords.extend([w.lower() for w in title_parts[:3]])

    important_terms = []
    if "smart contract" in ref_lower:
        important_terms.extend(["smart contract", "智能合约"])
    if "blockchain" in ref_lower:
        important_terms.extend(["blockchain", "区块链"])
    if "ethereum" in ref_lower:
        important_terms.append("ethereum")
    if "solidity" in ref_lower:
        important_terms.append("solidity")
    if "verification" in ref_lower:
        important_terms.append("verification")
    if "model checking" in ref_lower:
        important_terms.extend(["model checking", "模型检查"])
    if "operational semantics" in ref_lower:
        important_terms.append("operational semantics")
    if "fortran" in ref_lower:
        important_terms.extend(["fortran", "Fortran"])
    if "high performance" in ref_lower:
        important_terms.extend(
            ["high performance", "高性能", "parallel programming", "并行编程"]
        )
    if "parallel" in ref_lower:
        important_terms.extend(["parallel", "并行"])
    if "programming language" in ref_lower:
        important_terms.extend(["programming language", "编程语言"])
    if "algebra of connectors" in ref_lower or (
        "connector" in ref_lower and "algebra" in ref_lower
    ):
        important_terms.extend(
            [
                "connector",
                "连接器",
                "algebra",
                "代数",
                "组合",
                "composition",
                "component interaction",
                "组件交互",
                "组合规则",
                "composition rule",
            ]
        )
    if "bip" in ref_lower and ("bliudze" in ref_lower or "sifakis" in ref_lower):
        important_terms.extend(
            [
                "component",
                "组件",
                "interaction",
                "交互",
                "组合",
                "composition",
                "形式化",
                "formal",
                "组合语义",
                "compositional semantics",
            ]
        )
    if "prism" in ref_lower:
        important_terms.extend(
            [
                "prism",
                "probabilistic",
                "概率",
                "model checking",
                "模型检查",
                "verification",
                "验证",
            ]
        )
    if "smt" in ref_lower or "smt-comp" in ref_lower or "smt-lib" in ref_lower:
        important_terms.extend(
            [
                "smt",
                "solver",
                "求解器",
                "theorem proving",
                "定理证明",
                "satisfiability",
                "可满足性",
            ]
        )
    if "plotkin" in ref_lower and "operational semantics" in ref_lower:
        important_terms.extend(
            [
                "plotkin",
                "structural operational semantics",
                "结构化操作语义",
                "sos",
                "operational semantics",
                "操作语义",
            ]
        )
    if "crystality" in ref_lower or (
        "xu" in ref_lower and "wang" in ref_lower and "sun" in ref_lower
    ):
        important_terms.extend(
            [
                "crystality",
                "parallel evm",
                "并行evm",
                "operational semantics",
                "操作语义",
            ]
        )
    if "formal verification" in ref_lower and "solidity" in ref_lower:
        important_terms.extend(
            ["formal verification", "形式化验证", "solidity", "survey", "综述"]
        )
    if "security" in ref_lower and ("attack" in ref_lower or "challenge" in ref_lower):
        important_terms.extend(
            [
                "security",
                "安全",
                "attack",
                "攻击",
                "vulnerability",
                "漏洞",
                "threat",
                "威胁",
            ]
        )
    if "hoare logic" in ref_lower or "lamport" in ref_lower:
        important_terms.extend(
            [
                "hoare logic",
                "霍尔逻辑",
                "concurrent",
                "并发",
                "concurrency",
                "并发性",
                "correctness",
                "正确性",
            ]
        )
    if "defect" in ref_lower or "bug" in ref_lower:
        important_terms.extend(
            ["defect", "缺陷", "bug", "错误", "vulnerability", "漏洞", "issue", "问题"]
        )
    if "eclipse che" in ref_lower or "cloud-native" in ref_lower:
        important_terms.extend(
            [
                "eclipse",
                "che",
                "cloud",
                "云",
                "workspace",
                "工作空间",
                "development environment",
                "开发环境",
            ]
        )
    if "react" in ref_lower and "javascript" in ref_lower:
        important_terms.extend(
            [
                "react",
                "javascript",
                "ui",
                "interface",
                "界面",
                "frontend",
                "前端",
                "user interface",
                "用户界面",
            ]
        )
    if "version control" in ref_lower or "git" in ref_lower:
        important_terms.extend(
            [
                "version control",
                "版本控制",
                "git",
                "svn",
                "revision control",
                "修订控制",
            ]
        )
    if "bpmn" in ref_lower:
        important_terms.extend(
            [
                "bpmn",
                "business process",
                "业务流程",
                "workflow",
                "工作流",
                "modeling",
                "建模",
            ]
        )
    if "zeestar" in ref_lower or (
        "steffen" in ref_lower and "homomorphic" in ref_lower
    ):
        important_terms.extend(
            [
                "zeestar",
                "homomorphic encryption",
                "同态加密",
                "zero-knowledge",
                "零知识",
                "privacy",
                "隐私",
                "private",
                "私有",
            ]
        )

    keywords.extend(important_terms)

    keywords_match = re.findall(r"\b([A-Z][a-z]{4,})\b", ref_text[:200])
    keywords.extend([w.lower() for w in keywords_match[:3]])

    return list(set([k for k in keywords if len(k) > 2]))[:10]


def find_citation_suggestions(unreferenced_refs, references, paragraphs, ref_start_idx):
    """Find suggested citation locations for unreferenced references."""
    suggestions = {}

    for ref_num in unreferenced_refs:
        ref = next((r for r in references if r["number"] == ref_num), None)
        if not ref:
            continue

        ref_text = ref["full_text"]
        keywords = extract_keywords_from_reference(ref_text)

        if not keywords:
            continue

        matches = []
        for i, para in enumerate(paragraphs[:ref_start_idx]):
            para_lower = para.lower()
            para_stripped = para.strip()

            if not para_stripped or len(para_stripped) < 20:
                continue

            keyword_count = 0

            for kw in keywords:
                if kw in para_lower or kw in para:
                    if kw in [
                        "组合",
                        "composition",
                        "组合规则",
                        "composition rule",
                        "组合语义",
                        "compositional semantics",
                        "connector",
                        "连接器",
                        "algebra",
                        "代数",
                    ]:
                        keyword_count += 3
                    elif kw in [
                        "component interaction",
                        "组件交互",
                        "形式化",
                        "formal",
                        "component",
                        "组件",
                    ]:
                        keyword_count += 2
                    else:
                        keyword_count += 1

            if ref_num == 108:
                if "组合" in para and (
                    "语义" in para or "规则" in para or "机制" in para or "操作" in para
                ):
                    keyword_count += 5
                if "composition" in para_lower and (
                    "semantic" in para_lower
                    or "rule" in para_lower
                    or "mechanism" in para_lower
                    or "operational" in para_lower
                ):
                    keyword_count += 5
                if "形式化" in para and ("组合" in para or "合成" in para):
                    keyword_count += 4
                if (
                    "组合操作语义" in para
                    or "compositional operational semantics" in para_lower
                ):
                    keyword_count += 8
            elif ref_num == 109:
                if (
                    "prism" in para_lower
                    or "概率" in para
                    or "probabilistic" in para_lower
                ):
                    keyword_count += 3
                if "模型检测" in para or "model checking" in para_lower:
                    keyword_count += 2
            elif ref_num == 110:
                if "smt" in para_lower or "求解器" in para or "solver" in para_lower:
                    keyword_count += 3
                if "定理证明" in para or "theorem proving" in para_lower:
                    keyword_count += 2
            elif ref_num == 111:
                if "操作语义" in para or "operational semantics" in para_lower:
                    keyword_count += 3
                if "结构化" in para and "语义" in para:
                    keyword_count += 2
            elif ref_num == 112:
                if "crystality" in para_lower or (
                    "并行" in para and "evm" in para_lower
                ):
                    keyword_count += 4
                if "操作语义" in para and "并行" in para:
                    keyword_count += 3
            elif ref_num == 113:
                if "形式化验证" in para or "formal verification" in para_lower:
                    keyword_count += 3
                if "solidity" in para_lower and (
                    "验证" in para or "verification" in para_lower
                ):
                    keyword_count += 2
            elif ref_num == 114:
                if "安全" in para and (
                    "攻击" in para or "威胁" in para or "漏洞" in para
                ):
                    keyword_count += 3
                if "blockchain security" in para_lower or "区块链安全" in para:
                    keyword_count += 2
            elif ref_num == 115:
                if "正确性" in para or "correctness" in para_lower:
                    keyword_count += 2
                if "形式化验证" in para and "智能合约" in para:
                    keyword_count += 3
            elif ref_num == 116:
                if "安全研究" in para or "security research" in para_lower:
                    keyword_count += 2
                if "ethereum" in para_lower and (
                    "安全" in para or "security" in para_lower
                ):
                    keyword_count += 3
            elif ref_num == 119:
                if "hoare" in para_lower or "霍尔" in para:
                    keyword_count += 4
                if "并发" in para or "concurrent" in para_lower:
                    keyword_count += 2
            elif ref_num == 125:
                if "缺陷" in para or "defect" in para_lower or "bug" in para_lower:
                    keyword_count += 3
                if "ethereum" in para_lower and (
                    "缺陷" in para or "defect" in para_lower
                ):
                    keyword_count += 2
            elif ref_num == 149:
                if "eclipse" in para_lower or "che" in para_lower:
                    keyword_count += 3
                if "开发环境" in para or "development environment" in para_lower:
                    keyword_count += 2
            elif ref_num == 154:
                if "react" in para_lower:
                    keyword_count += 3
                if "前端" in para or "frontend" in para_lower or "ui" in para_lower:
                    keyword_count += 2
            elif ref_num == 160:
                if "版本控制" in para or "version control" in para_lower:
                    keyword_count += 3
                if "git" in para_lower or "svn" in para_lower:
                    keyword_count += 2
            elif ref_num == 163:
                if "bpmn" in para_lower:
                    keyword_count += 3
                if "业务流程" in para or "business process" in para_lower:
                    keyword_count += 2
            elif ref_num == 183:
                if "zeestar" in para_lower or (
                    "同态加密" in para or "homomorphic encryption" in para_lower
                ):
                    keyword_count += 4
                if "零知识" in para or "zero-knowledge" in para_lower:
                    keyword_count += 3
                if "隐私" in para or "privacy" in para_lower:
                    keyword_count += 2

            if keyword_count >= 1:
                para_text = para_stripped[:300]
                if para_text:
                    matches.append(
                        {
                            "paragraph": i + 1,
                            "text": para_text,
                            "keyword_matches": keyword_count,
                        }
                    )

        if matches:
            matches.sort(key=lambda x: x["keyword_matches"], reverse=True)
            suggestions[ref_num] = matches[:5]

    return suggestions


def is_level1_heading(para, namespaces):
    """Check if a paragraph is a level 1 heading."""
    pPr = para.find(".//w:pPr", namespaces)
    if pPr is None:
        return False, None, None

    # Method 1: Check outline level
    outline_lvl = pPr.find(".//w:outlineLvl", namespaces)
    if outline_lvl is not None:
        level_val = outline_lvl.get(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
        )
        if level_val == "0":  # Level 1 is 0 in Word
            style_name = None
            pStyle = pPr.find(".//w:pStyle", namespaces)
            if pStyle is not None:
                style_name = pStyle.get(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
                )
            return True, 1, style_name
        else:
            actual_level = int(level_val) + 1
            style_name = None
            pStyle = pPr.find(".//w:pStyle", namespaces)
            if pStyle is not None:
                style_name = pStyle.get(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
                )
            return False, actual_level, style_name

    # Method 2: Check paragraph style
    pStyle = pPr.find(".//w:pStyle", namespaces)
    if pStyle is not None:
        style_name = pStyle.get(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
        )
        # Check if it's a heading 1 style
        if style_name and (
            "Heading 1" in style_name
            or "标题 1" in style_name
            or "heading 1" in style_name.lower()
        ):
            return True, 1, style_name

    return False, None, None


def get_paragraph_alignment(para, namespaces):
    """Get paragraph alignment."""
    pPr = para.find(".//w:pPr", namespaces)
    if pPr is not None:
        jc = pPr.find(".//w:jc", namespaces)
        if jc is not None:
            val = jc.get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
            )
            if val:
                return val
    return "left"  # Default alignment


def check_references_heading_level(docx_path, heading_text="参考文献", heading_alignment=None):
    """
    Check if there exists a level 1 heading with the specified text and alignment.

    Args:
        docx_path: Path to the Word document
        heading_text: Text of the heading to check (default: "参考文献")
        heading_alignment: Expected alignment (default: None, no check)

    Returns:
        Dictionary with check results
    """
    try:
        with zipfile.ZipFile(docx_path, "r") as docx:
            document_xml = docx.read("word/document.xml")
            root = ET.fromstring(document_xml)

            namespaces = {
                "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            }

            paragraphs = root.findall(".//w:p", namespaces)

            # First, find all level 1 headings
            level1_headings = []
            for i, para in enumerate(paragraphs):
                is_level1, actual_level, style_name = is_level1_heading(
                    para, namespaces
                )
                if is_level1:
                    # Extract text from this heading
                    text_elements = para.findall(".//w:t", namespaces)
                    para_text = "".join(
                        [t.text for t in text_elements if t.text]
                    ).strip()
                    if para_text:
                        level1_headings.append(
                            {"index": i, "text": para_text, "style_name": style_name}
                        )

            # Check if any level 1 heading has the specified text
            ref_heading = None
            ref_heading_para = None
            for heading in level1_headings:
                if heading["text"] == heading_text:
                    ref_heading = heading
                    ref_heading_para = paragraphs[heading["index"]]
                    break

            if ref_heading is None:
                # Also check if the heading text exists anywhere (not as level 1 heading)
                ref_para_idx = None
                for i, para in enumerate(paragraphs):
                    text_elements = para.findall(".//w:t", namespaces)
                    para_text = "".join(
                        [t.text for t in text_elements if t.text]
                    ).strip()
                    if para_text == heading_text:
                        ref_para_idx = i
                        break

                if ref_para_idx is not None:
                    # Found the heading text but it's not a level 1 heading
                    ref_para = paragraphs[ref_para_idx]
                    is_level1, actual_level, style_name = is_level1_heading(
                        ref_para, namespaces
                    )
                    return {
                        "found": True,
                        "message": f"找到'{heading_text}'文本，但不是一级标题",
                        "is_level1": False,
                        "actual_level": actual_level if actual_level else "普通段落",
                        "style_name": style_name,
                        "paragraph_index": ref_para_idx + 1,
                    }
                else:
                    return {
                        "found": False,
                        "message": f"未找到'{heading_text}'标题",
                        "is_level1": False,
                        "actual_level": None,
                        "style_name": None,
                        "paragraph_index": None,
                    }

            # Found the heading text as a level 1 heading
            # Check alignment if required
            alignment_ok = True
            alignment_message = ""
            if heading_alignment and ref_heading_para:
                actual_alignment = get_paragraph_alignment(ref_heading_para, namespaces)
                if actual_alignment != heading_alignment:
                    alignment_ok = False
                    alignment_message = f"，但对齐方式应为'{heading_alignment}'，实际为'{actual_alignment}'"
                else:
                    alignment_message = f"，对齐方式为'{actual_alignment}'（正确）"

            return {
                "found": True,
                "message": f"找到'{heading_text}'一级标题{alignment_message}",
                "is_level1": True,
                "alignment_ok": alignment_ok,
                "actual_level": 1,
                "style_name": ref_heading["style_name"],
                "paragraph_index": ref_heading["index"] + 1,
            }

    except Exception as e:
        return {
            "found": False,
            "message": f"检查参考文献标题时出错: {e}",
            "is_level1": False,
            "actual_level": None,
            "style_name": None,
            "paragraph_index": None,
        }


def check_unreferenced_references(docx_path, config=None):
    """
    Check which references are not cited.
    
    Args:
        docx_path: Path to Word document
        config: Optional configuration dictionary. If not provided, will try to load from environment variable.
    """
    print("Extracting text from document...")
    paragraphs = extract_text_from_docx(docx_path)

    if not paragraphs:
        print("Error: Could not extract text from document")
        return None

    print(f"Found {len(paragraphs)} paragraphs")

    print("Extracting references...")
    # Try XML-based extraction first (handles Word auto-numbering)
    references = extract_references_from_xml(docx_path)
    if not references or len(references) < 10:
        # Fallback to text-based extraction
        references = extract_references(paragraphs)
    print(f"Found {len(references)} references")

    if not references:
        print("Warning: No references found in document")
        return {
            "references": [],
            "citations": set(),
            "unreferenced": [],
            "all_reference_numbers": set(),
            "duplicates": [],
        }

    print("Checking for duplicate references...")
    duplicates = check_duplicate_references(references)
    if duplicates:
        print(f"Found {len(duplicates)} duplicate reference groups")
    else:
        print("No duplicate references found")

    print("Extracting citations from document body...")
    citations = extract_citations(paragraphs)
    print(f"Found citations: {sorted(citations)}")

    all_ref_numbers = {ref["number"] for ref in references}
    unreferenced = sorted(all_ref_numbers - citations)

    ref_start_idx = -1
    for i, para in enumerate(paragraphs):
        if para.strip() == "参考文献":
            ref_start_idx = i
            break

    if ref_start_idx < 0:
        ref_start_idx = len(paragraphs)

    print("Finding citation suggestions for unreferenced references...")
    suggestions = find_citation_suggestions(
        unreferenced, references, paragraphs, ref_start_idx
    )
    print(f"Found suggestions for {len(suggestions)} unreferenced references")

    # Check if "参考文献" is under a level 1 heading
    heading_check = None
    try:
        # If config not provided, try to load from environment variable (for backward compatibility)
        if config is None:
            import os
            config_path = os.environ.get('CUSTOM_CONFIG_PATH')
            if config_path:
                from config_loader import ConfigLoader
                config_loader = ConfigLoader(config_path)
                config = config_loader.load()

        if config is None:
            print("⚠ Skipping heading check: configuration not available")
            heading_check = None
        else:
            refs_config = config.get("references", {})
            validation_config = refs_config.get("validation", {})

            check_heading_level = validation_config.get("check_heading_level")
            if check_heading_level is None:
                raise ValueError(
                    "check_heading_level not specified in config file (references.validation.check_heading_level)"
                )

            if check_heading_level:
                heading_text = validation_config.get("heading_text", "参考文献")
                heading_alignment = validation_config.get("heading_alignment")
                print(f"Checking if '{heading_text}' is under a level 1 heading...")
                if heading_alignment:
                    print(f"  Expected alignment: {heading_alignment}")
                heading_check = check_references_heading_level(
                    docx_path, heading_text=heading_text, heading_alignment=heading_alignment
                )
                if heading_check.get("is_level1"):
                    if heading_check.get("alignment_ok", True):
                        print(f"✓ '{heading_text}' is correctly under a level 1 heading")
                    else:
                        print(f"⚠ '{heading_text}' heading level check: {heading_check.get('message', 'N/A')}")
                else:
                    print(
                        f"⚠ '{heading_text}' heading level check: {heading_check.get('message', 'N/A')}"
                    )
                    if heading_check.get("actual_level"):
                        print(f"  Actual level: {heading_check.get('actual_level')}")
            else:
                print("References heading level check is disabled in config.")
                heading_check = None
    except Exception as e:
        raise ValueError(f"Error loading references validation config: {e}")

    return {
        "references": references,
        "citations": citations,
        "unreferenced": unreferenced,
        "all_reference_numbers": all_ref_numbers,
        "duplicates": duplicates,
        "suggestions": suggestions,
        "heading_check": heading_check,
    }


def generate_report(docx_path, result, superscript_check=None):
    """Generate markdown report."""
    docx_name = Path(docx_path).name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md_content = []
    md_content.append("# 参考文献引用检查报告\n")
    md_content.append(f"**文档名称**: {docx_name}\n")
    md_content.append(f"**检查时间**: {timestamp}\n")
    md_content.append("\n---\n")

    md_content.append("\n## 检查结果概览\n")
    md_content.append(f"- **参考文献总数**: {len(result['references'])}")
    md_content.append(f"- **被引用的参考文献数量**: {len(result['citations'])}")
    md_content.append(f"- **未被引用的参考文献数量**: {len(result['unreferenced'])}")
    md_content.append(f"- **重复的参考文献组数**: {len(result.get('duplicates', []))}")
    if result.get("duplicates"):
        unique_count = len(result["references"]) - len(result["duplicates"])
        md_content.append(f"- **实际唯一参考文献数**: {unique_count}")

    # Add heading level check result
    heading_check = result.get("heading_check", {})
    if heading_check:
        if heading_check.get("is_level1"):
            md_content.append("- **参考文献标题级别**: ✅ 正确（一级标题）")
        else:
            actual_level = heading_check.get("actual_level", "未知")
            md_content.append(
                f"- **参考文献标题级别**: ❌ 不符合要求（当前级别: {actual_level}，应为一级标题）"
            )

    if superscript_check:
        if superscript_check["found"]:
            md_content.append(
                f"- **非上标格式的引用数量**: {len(superscript_check['details'])}"
            )
        else:
            md_content.append("- **引用格式**: ✅ 所有引用均为上标格式")
    md_content.append("")

    if result["unreferenced"]:
        md_content.append("## 未被引用的参考文献\n")
        md_content.append(
            f"共发现 **{len(result['unreferenced'])}** 个未被引用的参考文献：\n"
        )
        md_content.append("| 序号 | 参考文献内容 |")
        md_content.append("|------|-------------|")

        for ref_num in result["unreferenced"]:
            ref = next(
                (r for r in result["references"] if r["number"] == ref_num), None
            )
            if ref:
                ref_text = (
                    ref["text"][:100] + "..." if len(ref["text"]) > 100 else ref["text"]
                )
                md_content.append(f"| [{ref_num}] | {ref_text} |")

        md_content.append("\n### 详细内容\n")
        suggestions = result.get("suggestions", {})
        for ref_num in result["unreferenced"]:
            ref = next(
                (r for r in result["references"] if r["number"] == ref_num), None
            )
            if ref:
                md_content.append(f"\n#### [{ref_num}]\n")
                md_content.append(f"{ref['full_text']}\n")

                if ref_num in suggestions:
                    md_content.append("\n**建议引用位置**:\n")
                    for idx, match in enumerate(suggestions[ref_num], 1):
                        md_content.append(
                            f"{idx}. 段落 {match['paragraph']}: {match['text']}...\n"
                        )
                    md_content.append("")
    else:
        md_content.append("\n## ✅ 检查结果\n")
        md_content.append("**所有参考文献均已被引用！**\n")

    md_content.append("\n---\n")
    md_content.append("\n## 引用统计\n")

    missing_citations = sorted(result["all_reference_numbers"] - result["citations"])
    if missing_citations:
        md_content.append(
            f"**未被引用的参考文献编号**: {', '.join(map(str, missing_citations))}\n"
        )

    extra_citations = sorted(result["citations"] - result["all_reference_numbers"])
    if extra_citations:
        md_content.append(
            f"**⚠️ 警告**: 文档中引用了不存在的参考文献编号: {', '.join(map(str, extra_citations))}\n"
        )

    md_content.append("\n---\n")
    md_content.append("\n## 重复参考文献检查\n")

    duplicates = result.get("duplicates", [])
    if duplicates:
        md_content.append(f"共发现 **{len(duplicates)}** 组完全相同的重复参考文献：\n")
        for idx, (ref1, ref2) in enumerate(duplicates, 1):
            md_content.append(f"### 重复组 {idx}\n")
            md_content.append(f"**参考文献 [{ref1['number']}]**:\n")
            md_content.append(f"{ref1['full_text']}\n")
            md_content.append(f"**参考文献 [{ref2['number']}]**:\n")
            md_content.append(f"{ref2['full_text']}\n")
            md_content.append("---\n")
    else:
        md_content.append("✅ **未发现重复的参考文献！**\n")

    if superscript_check:
        md_content.append("\n---\n")
        md_content.append("\n## 引用格式检查（上标）\n")
        if superscript_check["found"]:
            md_content.append("❌ **状态**: 发现问题\n")
            md_content.append(f"**结果**: {superscript_check['message']}\n")
            if superscript_check["details"]:
                md_content.append("\n**非上标格式的引用位置**:\n")
                md_content.append("| 序号 | 段落 | 页码 | 引用标记 | 上下文 |")
                md_content.append("|------|------|------|----------|--------|")

                for idx, detail in enumerate(superscript_check["details"], 1):
                    context = (
                        detail.get("context", "").replace("\n", " ").replace("|", "\\|")
                    )
                    if len(context) > 50:
                        context = context[:47] + "..."
                    md_content.append(
                        f"| {idx} | {detail['paragraph']} | 第 {detail['estimated_page']} 页 | {detail['citation']} | {context} |"
                    )
        else:
            md_content.append("✅ **状态**: 通过\n")
            md_content.append(f"**结果**: {superscript_check['message']}\n")

    md_content.append("\n---\n")

    # Add heading level check section
    heading_check = result.get("heading_check", {})
    if heading_check:
        md_content.append("\n## 参考文献标题级别检查\n")
        if heading_check.get("is_level1"):
            md_content.append("✅ **状态**: 通过\n")
            md_content.append("**结果**: '参考文献'标题正确位于一级标题下\n")
            if heading_check.get("paragraph_index"):
                md_content.append(
                    f"**位置**: 段落 {heading_check.get('paragraph_index')}\n"
                )
        else:
            md_content.append("❌ **状态**: 不符合要求\n")
            actual_level = heading_check.get("actual_level", "未知")
            style_name = heading_check.get("style_name", "无")
            md_content.append(f"**结果**: '参考文献'标题不是一级标题\n")
            md_content.append(f"**当前级别**: {actual_level}\n")
            if style_name:
                md_content.append(f"**段落样式**: {style_name}\n")
            if heading_check.get("paragraph_index"):
                md_content.append(
                    f"**位置**: 段落 {heading_check.get('paragraph_index')}\n"
                )
            md_content.append(
                "\n**要求**: '参考文献'应设置为一级标题（标题1/Heading 1）\n"
            )
        md_content.append("")

    md_content.append("\n---\n")
    md_content.append("\n*报告由参考文献检查脚本自动生成*\n")

    return "\n".join(md_content)


def main():
    if len(sys.argv) > 1:
        docx_path = Path(sys.argv[1])
    else:
        docx_path = Path(
            "/Users/lsl/nuts/我的坚果云/idea/yanshou/项目验收-22年项目-科技报告-20251229-v5.docx"
        )

    if not docx_path.exists():
        print(f"Error: File not found: {docx_path}")
        sys.exit(1)

    print("=" * 80)
    print(f"Checking references in document: {docx_path.name}")
    print("=" * 80)
    print()

    result = check_unreferenced_references(docx_path)

    if not result:
        print("Error: Could not check references")
        sys.exit(1)

    print()
    print("Checking citation superscript format...")
    superscript_check = check_citation_superscript_format(docx_path)
    print(f"Result: {superscript_check['message']}")
    if superscript_check["found"]:
        print(
            f"Found {len(superscript_check['details'])} citation(s) not in superscript format"
        )
    else:
        print("✅ All citations are in superscript format")

    print()
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total references: {len(result['references'])}")
    print(f"Cited references: {len(result['citations'])}")
    print(f"Unreferenced references: {len(result['unreferenced'])}")
    duplicates = result.get("duplicates", [])
    print(f"Duplicate reference groups: {len(duplicates)}")
    if duplicates:
        unique_count = len(result["references"]) - len(duplicates)
        print(f"Unique references (after removing duplicates): {unique_count}")

    if superscript_check["found"]:
        print(
            f"Citations not in superscript format: {len(superscript_check['details'])}"
        )
    else:
        print("Citation format: ✅ All citations are in superscript format")

    if result["unreferenced"]:
        print()
        print("Unreferenced references:")
        for ref_num in result["unreferenced"]:
            ref = next(
                (r for r in result["references"] if r["number"] == ref_num), None
            )
            if ref:
                print(f"  [{ref_num}] {ref['text'][:80]}...")
    else:
        print()
        print("✅ All references are cited!")

    duplicates = result.get("duplicates", [])
    if duplicates:
        print()
        print("Duplicate references:")
        for idx, (ref1, ref2) in enumerate(duplicates, 1):
            print(f"  Group {idx}:")
            print(f"    [{ref1['number']}] {ref1['full_text']}")
            print(f"    [{ref2['number']}] {ref2['full_text']}")

    extra_citations = result["citations"] - result["all_reference_numbers"]
    if extra_citations:
        print()
        print(
            f"⚠️  Warning: Document cites non-existent references: {sorted(extra_citations)}"
        )

    print("=" * 80)

    print()
    print("Generating markdown report...")
    md_report = generate_report(docx_path, result, superscript_check)

    script_dir = Path(__file__).parent
    report_dir = script_dir.parent / "report"
    report_dir.mkdir(exist_ok=True)

    report_path = report_dir / f"{docx_path.stem}_参考文献检查报告.md"
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(md_report)
        print(f"✓ Markdown report saved to: {report_path}")
    except Exception as e:
        print(f"✗ Error saving markdown report: {e}")


if __name__ == "__main__":
    main()
