#!/usr/bin/env python3
"""
Utility functions for document format checking.
"""

import xml.etree.ElementTree as ET


def extract_text_from_xml(xml_content):
    """Extract text content from Word XML, handling namespaces."""
    try:
        root = ET.fromstring(xml_content)

        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }

        text_elements = []

        for t in root.findall('.//w:t', namespaces):
            if t.text:
                text_elements.append(t.text)

        if not text_elements:
            for elem in root.iter():
                if elem.text and elem.text.strip():
                    text_elements.append(elem.text.strip())

        return ' '.join(text_elements)
    except Exception:
        return None


def estimate_page_from_paragraph(para_num, total_paras):
    """Roughly estimate page number from paragraph number."""
    avg_paras_per_page = 25
    estimated_page = max(1, int(para_num / avg_paras_per_page) + 1)
    return estimated_page

