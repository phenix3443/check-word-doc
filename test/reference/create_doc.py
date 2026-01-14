#!/usr/bin/env python3
"""
生成参考文献检查测试文档
创建包含各种参考文献问题的测试文档
"""

import zipfile
import xml.etree.ElementTree as ET
import os

def create_references_test_document():
    """创建参考文献测试文档"""
    
    # Word文档的基本XML结构
    document_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <!-- 标题 -->
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
                <w:jc w:val="center"/>
            </w:pPr>
            <w:r>
                <w:t>参考文献检查测试文档</w:t>
            </w:r>
        </w:p>
        
        <!-- 正文段落1 - 包含正确的参考文献引用 -->
        <w:p>
            <w:r>
                <w:t>这是第一个段落，包含正确的参考文献引用</w:t>
            </w:r>
            <w:r>
                <w:rPr>
                    <w:vertAlign w:val="superscript"/>
                </w:rPr>
                <w:t>[1]</w:t>
            </w:r>
            <w:r>
                <w:t>。这里还有另一个引用</w:t>
            </w:r>
            <w:r>
                <w:rPr>
                    <w:vertAlign w:val="superscript"/>
                </w:rPr>
                <w:t>[2]</w:t>
            </w:r>
            <w:r>
                <w:t>。</w:t>
            </w:r>
        </w:p>
        
        <!-- 正文段落2 - 包含多个连续引用 -->
        <w:p>
            <w:r>
                <w:t>这个段落包含多个连续引用</w:t>
            </w:r>
            <w:r>
                <w:rPr>
                    <w:vertAlign w:val="superscript"/>
                </w:rPr>
                <w:t>[3-5]</w:t>
            </w:r>
            <w:r>
                <w:t>和分散的引用</w:t>
            </w:r>
            <w:r>
                <w:rPr>
                    <w:vertAlign w:val="superscript"/>
                </w:rPr>
                <w:t>[6, 8]</w:t>
            </w:r>
            <w:r>
                <w:t>。</w:t>
            </w:r>
        </w:p>
        
        <!-- 正文段落3 - 包含错误的引用格式 -->
        <w:p>
            <w:r>
                <w:t>这个段落包含错误的引用格式：(1)和</w:t>
            </w:r>
            <w:r>
                <w:t>[7</w:t>
            </w:r>
            <w:r>
                <w:t>]和</w:t>
            </w:r>
            <w:r>
                <w:rPr>
                    <w:vertAlign w:val="superscript"/>
                </w:rPr>
                <w:t>9</w:t>
            </w:r>
            <w:r>
                <w:t>。</w:t>
            </w:r>
        </w:p>
        
        <!-- 正文段落4 - 包含不存在的引用 -->
        <w:p>
            <w:r>
                <w:t>这个段落引用了不存在的文献</w:t>
            </w:r>
            <w:r>
                <w:rPr>
                    <w:vertAlign w:val="superscript"/>
                </w:rPr>
                <w:t>[99]</w:t>
            </w:r>
            <w:r>
                <w:t>和</w:t>
            </w:r>
            <w:r>
                <w:rPr>
                    <w:vertAlign w:val="superscript"/>
                </w:rPr>
                <w:t>[100]</w:t>
            </w:r>
            <w:r>
                <w:t>。</w:t>
            </w:r>
        </w:p>
        
        <!-- 空段落 -->
        <w:p/>
        
        <!-- 参考文献标题 -->
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
                <w:jc w:val="center"/>
            </w:pPr>
            <w:r>
                <w:t>参考文献</w:t>
            </w:r>
        </w:p>
        
        <!-- 参考文献列表 -->
        <w:p>
            <w:r>
                <w:t>[1] 张三, 李四. 文档格式检查方法研究[J]. 计算机应用, 2023, 43(1): 1-8.</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>[2] Wang L, Smith J. Automated document validation techniques[C]// Proceedings of International Conference on Document Processing. New York: ACM Press, 2023: 123-130.</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>[3] 赵六. 中文文档规范化处理[M]. 北京: 清华大学出版社, 2022.</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>[4] Johnson M. Document structure analysis using machine learning[J]. IEEE Transactions on Document Analysis, 2023, 15(2): 45-62.</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>[5] 孙七, 周八. 参考文献自动检查系统设计[J]. 软件学报, 2023, 34(3): 234-245.</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>[6] Brown A, Davis C. Citation format validation in academic documents[J]. Journal of Information Science, 2023, 49(2): 178-192.</w:t>
            </w:r>
        </w:p>
        
        <!-- 缺少引用[7] -->
        
        <w:p>
            <w:r>
                <w:t>[8] 钱九. 文档质量评估方法[D]. 北京: 北京大学, 2023.</w:t>
            </w:r>
        </w:p>
        
        <!-- 未被引用的参考文献 -->
        <w:p>
            <w:r>
                <w:t>[9] Miller R. Unused reference example[J]. Example Journal, 2023, 1(1): 1-10.</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>[10] 李十. 另一个未被引用的文献[J]. 示例期刊, 2023, 2(1): 11-20.</w:t>
            </w:r>
        </w:p>
        
    </w:body>
</w:document>'''
    
    # 创建其他必需的XML文件
    app_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
    <Application>Microsoft Office Word</Application>
    <DocSecurity>0</DocSecurity>
    <ScaleCrop>false</ScaleCrop>
    <SharedDoc>false</SharedDoc>
    <HyperlinksChanged>false</HyperlinksChanged>
    <AppVersion>16.0000</AppVersion>
</Properties>'''
    
    core_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties">
    <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">参考文献检查测试文档</dc:title>
    <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">Test Generator</dc:creator>
    <cp:lastModifiedBy>Test Generator</cp:lastModifiedBy>
    <cp:revision>1</cp:revision>
    <dcterms:created xmlns:dcterms="http://purl.org/dc/terms/" xsi:type="dcterms:W3CDTF" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">2024-01-01T00:00:00Z</dcterms:created>
    <dcterms:modified xmlns:dcterms="http://purl.org/dc/terms/" xsi:type="dcterms:W3CDTF" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">2024-01-01T00:00:00Z</dcterms:modified>
</cp:coreProperties>'''
    
    content_types_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
    <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
    <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''
    
    main_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
    <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
    <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''
    
    # 创建docx文件
    docx_path = os.path.join(os.path.dirname(__file__), "test.docx")
    
    with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as docx:
        docx.writestr('[Content_Types].xml', content_types_xml)
        docx.writestr('_rels/.rels', main_rels)
        docx.writestr('word/document.xml', document_xml)
        docx.writestr('docProps/core.xml', core_xml)
        docx.writestr('docProps/app.xml', app_xml)
    
    return docx_path

if __name__ == "__main__":
    print("生成参考文献检查测试文档...")
    
    try:
        docx_path = create_references_test_document()
        print(f"参考文献测试文档已创建: {os.path.basename(docx_path)}")
        
        print("\n文档内容:")
        print("  - 正文段落: 4个（包含各种引用格式）")
        print("  - 参考文献: 10个（[1]-[10]）")
        
        print("\n包含的测试问题:")
        print("  - 正确的上标引用: [1], [2]")
        print("  - 连续引用: [3-5]")
        print("  - 多个引用: [6, 8]")
        print("  - 错误的引用格式: (1), [7], 9")
        print("  - 不存在的引用: [99], [100]")
        print("  - 缺失的参考文献: [7]")
        print("  - 未被引用的文献: [9], [10]")
        
        print("\n✓ 参考文献测试文档创建成功！")
        print("现在可以运行以下命令测试:")
        print("poetry run python script/check.py --check references --config config/base.yaml test/reference/test.docx")
        
    except Exception as e:
        print(f"✗ 创建测试文档失败: {e}")
        import traceback
        traceback.print_exc()