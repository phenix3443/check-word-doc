#!/usr/bin/env python3
"""
创建包含各种格式问题的测试文档
使用系统自带的 zipfile 和 xml 库，不需要额外依赖
"""
import os
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime

def create_test_document():
    """创建测试文档"""
    
    # Word 文档的基本 XML 结构
    document_xml = '''<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <!-- 标题部分（前3个段落会被跳过） -->
        <w:p>
            <w:r>
                <w:t>测试文档标题</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>副标题</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>作者信息</w:t>
            </w:r>
            <!-- 添加分页符来分隔封面页和正文 -->
            <w:pPr>
                <w:sectPr>
                    <w:type w:val="nextPage"/>
                </w:sectPr>
            </w:pPr>
        </w:p>
        
        <!-- 正文段落（第4个段落开始） -->
        <w:p>
            <w:r>
                <w:t>这是正常的段落。</w:t>
            </w:r>
        </w:p>
        
        <!-- 中文间距问题 -->
        <w:p>
            <w:r>
                <w:t>这里有 中文 间距 问题。</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>另一个中文 间距问题的 例子。</w:t>
            </w:r>
        </w:p>
        
        <!-- 英文引号问题 -->
        <w:p>
            <w:r>
                <w:t>这里使用了"英文双引号"包围中文。</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>还有'英文单引号'的问题。</w:t>
            </w:r>
        </w:p>
        
        <!-- 正常的中文引号 -->
        <w:p>
            <w:r>
                <w:t>这里使用了"正确的中文引号"。</w:t>
            </w:r>
        </w:p>
        
        <!-- 引号匹配问题 -->
        <w:p>
            <w:r>
                <w:t>这里有\u201c不匹配的引号。</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>还有\u201c另一个不匹配的引号问题。</w:t>
            </w:r>
        </w:p>
        
        <!-- 空段落（连续空行） -->
        <w:p></w:p>
        <w:p></w:p>
        
        <w:p>
            <w:r>
                <w:t>空行后的正常段落。</w:t>
            </w:r>
        </w:p>
        
        <!-- 更多正文段落 -->
        <w:p>
            <w:r>
                <w:t>这是另一个正常段落。</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>包含公式符号的段落：s', s'', seg'等数学符号。</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>最后一个测试段落。</w:t>
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
    <dc:title>测试文档</dc:title>
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
    doc_path = os.path.join(os.path.dirname(__file__), "test.docx")
    
    with zipfile.ZipFile(doc_path, 'w', zipfile.ZIP_DEFLATED) as docx:
        docx.writestr('[Content_Types].xml', content_types_xml)
        docx.writestr('_rels/.rels', rels_xml)
        docx.writestr('word/document.xml', document_xml)
        docx.writestr('word/_rels/document.xml.rels', word_rels_xml)
        docx.writestr('docProps/core.xml', core_xml)
        docx.writestr('docProps/app.xml', app_xml)
    
    print(f"测试文档已创建: {os.path.basename(doc_path)}")
    print("包含的格式问题:")
    print("  - 中文间距问题: 2个（段落5、6）")
    print("  - 英文引号问题: 2个（段落7、8）")
    print("  - 引号匹配问题: 2个（段落10、11）")
    print("  - 连续空行问题: 1组（段落12、13）")
    print("  - 公式符号: 1个段落（段落15）")
    print("  - 总段落数: 16个（前3个为标题，后13个为正文）")
    
    return True

if __name__ == "__main__":
    if create_test_document():
        print("\n✓ 测试文档创建成功！")
        print("现在可以运行以下命令测试:")
        print("poetry run python script/check.py --check paragraphs --config config/basic.yaml test/paragraphs/test.docx")
    else:
        print("\n✗ 测试文档创建失败！")