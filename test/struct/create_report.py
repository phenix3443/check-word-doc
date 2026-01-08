#!/usr/bin/env python3
"""
创建符合科技报告标准的完整测试文档
包含：封面、目录、插图目录、附表目录、正文、参考文献
"""
import os
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime

def create_scientific_report():
    """创建科技报告测试文档"""
    
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
                <w:t>2025年度-23年项目-科技报告</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:pPr>
                <w:jc w:val="center"/>
            </w:pPr>
            <w:r>
                <w:t>项目名称：智能化数据处理系统研发</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:pPr>
                <w:jc w:val="center"/>
            </w:pPr>
            <w:r>
                <w:t>承担单位：某某研究院</w:t>
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
                <w:t>完成时间：2025年1月</w:t>
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
                <w:t>1 引言 ........................... 1</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>2 研究方法 ........................... 2</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>3 系统设计 ........................... 3</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>4 实验结果 ........................... 4</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>5 结论 ........................... 5</w:t>
            </w:r>
        </w:p>
        
        <!-- 插图目录部分 -->
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
                <w:jc w:val="center"/>
            </w:pPr>
            <w:r>
                <w:t>插图目录</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>图2-1 系统架构图 ........................... 2</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>图3-1 数据流程图 ........................... 3</w:t>
            </w:r>
        </w:p>
        
        <!-- 附表目录部分 -->
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
                <w:jc w:val="center"/>
            </w:pPr>
            <w:r>
                <w:t>附表目录</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>表3-1 系统性能对比 ........................... 3</w:t>
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
                <w:t>表4-1 实验数据统计 ........................... 4</w:t>
            </w:r>
        </w:p>
        
        <!-- 正文部分 -->
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
            </w:pPr>
            <w:r>
                <w:t>1 引言</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>随着信息技术的快速发展，智能化数据处理系统在各个领域中发挥着越来越重要的作用。本项目旨在开发一套高效、可靠的智能化数据处理系统。</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>本研究的主要目标是提高数据处理的效率和准确性，为相关应用提供技术支撑。</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
            </w:pPr>
            <w:r>
                <w:t>2 研究方法</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading2"/>
            </w:pPr>
            <w:r>
                <w:t>2.1 技术路线</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>本项目采用模块化设计思路，将系统分为数据采集、数据处理、结果输出三个主要模块。</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
            </w:pPr>
            <w:r>
                <w:t>3 系统设计</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>系统采用分层架构设计，包括数据层、业务逻辑层和表示层。</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
            </w:pPr>
            <w:r>
                <w:t>4 实验结果</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>通过大量实验验证，系统在处理效率和准确性方面都达到了预期目标。</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
            </w:pPr>
            <w:r>
                <w:t>5 结论</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>本项目成功开发了智能化数据处理系统，为相关领域的应用提供了有效的技术解决方案。</w:t>
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
                <w:t>[1] 张三, 李四. 智能数据处理技术研究[J]. 计算机科学, 2023, 50(1): 1-10.</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>[2] Wang L, Chen M. Advanced Data Processing Systems[J]. IEEE Transactions, 2023, 15(2): 20-35.</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>[3] 王五, 赵六. 数据处理系统架构设计[M]. 北京: 科学出版社, 2022.</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>[4] Johnson R, Smith K. Machine Learning in Data Processing[C]// Proceedings of ICML, 2023: 100-115.</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>[5] 刘七, 陈八. 智能化系统性能优化方法[J]. 软件学报, 2023, 34(3): 45-60.</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>[6] Brown A, Davis B. Data Analytics and Processing[J]. Nature Computing, 2023, 22(4): 78-92.</w:t>
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
    <dc:title>科技报告测试文档</dc:title>
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
    doc_path = os.path.join(os.path.dirname(__file__), "report.docx")
    
    with zipfile.ZipFile(doc_path, 'w', zipfile.ZIP_DEFLATED) as docx:
        docx.writestr('[Content_Types].xml', content_types_xml)
        docx.writestr('_rels/.rels', rels_xml)
        docx.writestr('word/document.xml', document_xml)
        docx.writestr('word/_rels/document.xml.rels', word_rels_xml)
        docx.writestr('docProps/core.xml', core_xml)
        docx.writestr('docProps/app.xml', app_xml)
    
    print(f"科技报告测试文档已创建: {os.path.basename(doc_path)}")
    print("文档结构:")
    print("  - 封面: 段落1-4（包含项目名称、承担单位、完成时间、科技报告）")
    print("  - 目录: 段落5-10")
    print("  - 插图目录: 段落11-13")
    print("  - 附表目录: 段落14-16")
    print("  - 正文: 段落17-28（包含5个一级标题，1个二级标题）")
    print("  - 参考文献: 段落29-35（6个参考文献）")
    print("符合科技报告要求:")
    print("  ✓ 包含所有必需部分（封面、目录、插图目录、附表目录、正文、参考文献）")
    print("  ✓ 正文包含5个编号标题")
    print("  ✓ 参考文献数量充足（6个）")
    print("  ✓ 文档部分顺序正确")
    
    return True

if __name__ == "__main__":
    if create_scientific_report():
        print("\n✓ 科技报告测试文档创建成功！")
        print("现在可以运行以下命令测试:")
        print("poetry run python script/check.py --check structure --config 2025/task/科技报告/科技报告-2025.yaml test/struct/report.docx")
    else:
        print("\n✗ 科技报告测试文档创建失败！")