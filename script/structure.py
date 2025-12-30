#!/usr/bin/env python3
"""
Document structure analysis functions.
"""

import zipfile


def analyze_document_structure(docx_path):
    """Analyze the overall structure of the document."""
    structure = {
        'headers': [],
        'footers': [],
        'sections': []
    }

    try:
        with zipfile.ZipFile(docx_path, 'r') as docx:
            file_list = docx.namelist()

            structure['headers'] = [f for f in file_list if 'header' in f.lower() and f.endswith('.xml')]
            structure['footers'] = [f for f in file_list if 'footer' in f.lower() and f.endswith('.xml')]
            structure['sections'] = [f for f in file_list if 'word/section' in f.lower() or 'document.xml' in f]

    except Exception as e:
        print(f"Error analyzing document structure: {e}")

    return structure

