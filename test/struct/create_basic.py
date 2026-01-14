#!/usr/bin/env python3
"""
创建包含完整结构的测试文档（封面、目录、正文）
用于测试结构检查功能
"""
import os
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime

def create_complete_document():
    """创建包含完整结构的测试文档"""
    
    # Word 文档的基本 XML 结构
    document_xml = '''<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <!-- 封面部分 -->
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Title"/>
                <w:jc w:val="center"/>
            </w:pPr>
            <w:r>
                <w:t>测试文档标题</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:pPr>
                <w:jc w:val="center"/>
            </w:pPr>
            <w:r>
                <w:t>副标题</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:pPr>
                <w:jc w:val="center"/>
                <!-- 添加分页符来分隔封面页和目录 -->
                <w:sectPr>
                    <w:type w:val="nextPage"/>
                </w:sectPr>
            </w:pPr>
            <w:r>
                <w:t>作者信息</w:t>
            </w:r>
        </w:p>
        
        <!-- 目录部分 -->
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
                <w:jc w:val="center"/>
            </w:pPr>
            <w:r>
                <w:t>目录</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>1. 引言 ........................... 1</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>2. 方法 ........................... 2</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>3. 结果 ........................... 3</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>4. 结论 ........................... 4</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:pPr>
                <!-- 添加分页符来分隔目录和正文 -->
                <w:sectPr>
                    <w:type w:val="nextPage"/>
                </w:sectPr>
            </w:pPr>
            <w:r>
                <w:t>参考文献 ........................... 5</w:t>
            </w:r>
        </w:p>
        
        <!-- 正文部分 -->
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
            </w:pPr>
            <w:r>
                <w:t>1. 引言</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>这是引言部分的内容。</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
            </w:pPr>
            <w:r>
                <w:t>2. 方法</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>这是方法部分的内容。</w:t>
            </w:r>
        </w:p>
        
        <!-- 包含一些格式问题用于测试 -->
        <w:p>
            <w:r>
                <w:t>这里有 中文 间距 问题。</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>这里使用了"英文双引号"包围中文。</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
            </w:pPr>
            <w:r>
                <w:t>3. 结果</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>这是结果部分的内容。</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
            </w:pPr>
            <w:r>
                <w:t>4. 结论</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>这是结论部分的内容。</w:t>
            </w:r>
        </w:p>
        
        <!-- 参考文献部分 -->
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
                <w:jc w:val="center"/>
            </w:pPr>
            <w:r>
                <w:t>参考文献</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>[1] 张三. 测试文献标题. 测试期刊, 2023, 1(1): 1-10.</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>[2] 李四. 另一个测试文献. 另一个期刊, 2023, 2(2): 11-20.</w:t>
            </w:r>
        </w:p>
    </w:body>
</w:document>'''

    # 其他必需的 Word 文档文件
    app_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
    <Application>Python Script</Application>
    <DocSecurity>0</DocSecurity>
    <ScaleCrop>false</ScaleCrop>
    <SharedDoc>false</SharedDoc>
    <HyperlinksChanged>false</HyperlinksChanged>
    <AppVersion>1.0</AppVersion>
</Properties>'''

    core_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <dc:title>完整结构测试文档</dc:title>
    <dc:creator>Python Script</dc:creator>
    <dcterms:created xsi:type="dcterms:W3CDTF">{datetime.now().isoformat()}</dcterms:created>
    <dcterms:modified xsi:type="dcterms:W3CDTF">{datetime.now().isoformat()}</dcterms:modified>
</cp:coreProperties>'''

    content_types_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
    <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
    <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''

    rels_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
    <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
    <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''

    word_rels_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>'''

    # 创建 Word 文档
    doc_path = os.path.join(os.path.dirname(__file__), "basic.docx")
    
    with zipfile.ZipFile(doc_path, 'w', zipfile.ZIP_DEFLATED) as docx:
        docx.writestr('[Content_Types].xml', content_types_xml)
        docx.writestr('_rels/.rels', rels_xml)
        docx.writestr('word/document.xml', document_xml)
        docx.writestr('word/_rels/document.xml.rels', word_rels_xml)
        docx.writestr('docProps/core.xml', core_xml)
        docx.writestr('docProps/app.xml', app_xml)
    
    print(f"完整结构测试文档已创建: {os.path.basename(doc_path)}")
    print("文档结构:")
    print("  - 封面: 段落1-3")
    print("  - 目录: 段落4-9")
    print("  - 正文: 段落10-19")
    print("  - 参考文献: 段落20-22")
    print("包含的格式问题:")
    print("  - 中文间距问题: 1个（段落14）")
    print("  - 英文引号问题: 1个（段落15）")
    
    return True

if __name__ == "__main__":
    if create_complete_document():
        print("\n✓ 完整结构测试文档创建成功！")
        print("现在可以运行以下命令测试:")
        print("poetry run python script/check.py --check structure --config config/base.yaml test/struct/basic.docx")
    else:
        print("\n✗ 完整结构测试文档创建失败！")