#!/usr/bin/env python3
"""
通讯作者交叉验证测试

测试通讯作者在作者列表中是否有星号标记
"""

import re

def extract_corresponding_author_name(corresponding_author_text):
    """从通讯作者信息中提取作者名"""
    # 格式：* 论文通信作者：作者名（邮箱）
    match = re.match(r'^\*\s*论文通信作者[：:](.+)（[^）]+）$', corresponding_author_text)
    if match:
        return match.group(1).strip()
    return None


def check_author_has_asterisk(author_list_text, author_name):
    """检查作者列表中的作者是否有星号标记"""
    # 单作者情况：作者名[数字]*
    # 多作者情况：作者名数字*
    
    # 构建正则表达式来查找作者名
    # 需要考虑：
    # 1. 作者名后可能直接跟星号（单作者）：王嘉平*
    # 2. 作者名后跟数字再跟星号（多作者）：王嘉平1*
    
    # 转义作者名中的特殊字符
    escaped_name = re.escape(author_name)
    
    # 匹配模式：作者名 + [可选数字] + 星号
    pattern = f"{escaped_name}\\d*\\*"
    
    match = re.search(pattern, author_list_text)
    return match is not None


def test_cross_validation():
    """测试交叉验证"""
    
    print("=" * 80)
    print("通讯作者交叉验证测试")
    print("=" * 80)
    print()
    
    test_cases = [
        {
            "name": "场景1：单作者，有星号（正确）",
            "author_list": "王嘉平*",
            "corresponding_author": "* 论文通信作者：王嘉平（wangjiaping@pku.edu.cn）",
            "expected": True
        },
        {
            "name": "场景2：多作者，第一作者是通讯作者，有星号（正确）",
            "author_list": "王嘉平1*，汪浩2",
            "corresponding_author": "* 论文通信作者：王嘉平（wangjiaping@pku.edu.cn）",
            "expected": True
        },
        {
            "name": "场景3：多作者，第二作者是通讯作者，有星号（正确）",
            "author_list": "张三1，王嘉平2*",
            "corresponding_author": "* 论文通信作者：王嘉平（wangjiaping@pku.edu.cn）",
            "expected": True
        },
        {
            "name": "场景4：多作者，通讯作者没有星号（错误）",
            "author_list": "王嘉平1，汪浩2",
            "corresponding_author": "* 论文通信作者：王嘉平（wangjiaping@pku.edu.cn）",
            "expected": False
        },
        {
            "name": "场景5：单作者，没有星号（错误）",
            "author_list": "王嘉平",
            "corresponding_author": "* 论文通信作者：王嘉平（wangjiaping@pku.edu.cn）",
            "expected": False
        },
        {
            "name": "场景6：通讯作者不在作者列表中（错误）",
            "author_list": "张三1*，李四2",
            "corresponding_author": "* 论文通信作者：王嘉平（wangjiaping@pku.edu.cn）",
            "expected": False
        },
    ]
    
    print("📋 测试用例：")
    print()
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"📝 {test_case['name']}")
        print(f"   作者列表: {test_case['author_list']}")
        print(f"   通讯作者: {test_case['corresponding_author']}")
        
        # 提取通讯作者名
        author_name = extract_corresponding_author_name(test_case['corresponding_author'])
        print(f"   提取的作者名: {author_name}")
        
        # 检查是否有星号
        has_asterisk = check_author_has_asterisk(test_case['author_list'], author_name) if author_name else False
        
        # 判断结果
        is_correct = has_asterisk == test_case['expected']
        result = "✅" if is_correct else "❌"
        
        if is_correct:
            passed += 1
        else:
            failed += 1
        
        print(f"   检查结果: {'有星号' if has_asterisk else '无星号'}")
        print(f"   {result} {'通过' if is_correct else '失败'}")
        print()
    
    print("=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)
    
    return failed == 0


def propose_rule_config():
    """提出规则配置方案"""
    
    print()
    print("=" * 80)
    print("推荐的规则配置方案")
    print("=" * 80)
    print()
    
    print("方案：使用自定义验证函数（需要扩展 RuleChecker）")
    print()
    print("由于这个规则需要：")
    print("1. 从通讯作者信息中提取作者名")
    print("2. 在作者列表中查找该作者名")
    print("3. 验证该作者名后面是否有星号")
    print()
    print("这种跨元素的内容提取和比较，建议通过以下方式实现：")
    print()
    
    print("方案 A：扩展 RuleChecker 支持内容提取和比较")
    print()
    print("```yaml")
    print("# r-004: 通讯作者星号标记检查")
    print("- id: r-004")
    print("  name: 通讯作者星号标记检查")
    print("  description: 通讯作者在作者列表中必须有星号标记")
    print("  check:")
    print("    cross_validate:")
    print("      source:")
    print("        selector: \".corresponding-author\"")
    print("        extract: \"论文通信作者[：:](.+)（\"  # 提取作者名")
    print("      target:")
    print("        selector: \".author-list\"")
    print("        pattern: \"{extracted}\\\\d*\\\\*\"  # 检查作者名+数字+星号")
    print("  severity: error")
    print("  message: \"通讯作者在作者列表中必须有星号标记\"")
    print("```")
    print()
    
    print("方案 B：使用条件规则（简化版本）")
    print()
    print("虽然不能完全实现提取和比较，但可以检查基本格式：")
    print()
    print("```yaml")
    print("# r-004: 作者列表必须包含星号（如果有通讯作者）")
    print("- id: r-004")
    print("  name: 作者列表星号检查")
    print("  description: 如果有通讯作者，作者列表中必须有星号")
    print("  selector: \".author-list\"")
    print("  condition:")
    print("    selector: \".corresponding-author\"")
    print("    exists: true")
    print("  check:")
    print("    pattern: \"\\\\d*\\\\*\"  # 必须包含星号")
    print("  severity: error")
    print("  message: \"作者列表中必须有星号标记通讯作者\"")
    print("```")
    print()
    
    print("方案 C：在 RuleChecker 中实现专门的验证方法")
    print()
    print("在 RuleChecker 类中添加 _check_cross_reference 方法：")
    print()
    print("```python")
    print("def _check_cross_reference(self, config, rule_id, severity, message):")
    print("    # 1. 从通讯作者中提取作者名")
    print("    corresponding_blocks = self.selector.select(config['source']['selector'])")
    print("    if not corresponding_blocks:")
    print("        return")
    print("    ")
    print("    # 2. 提取作者名")
    print("    extract_pattern = config['source']['extract']")
    print("    author_name = None")
    print("    for block in corresponding_blocks:")
    print("        text = self._get_block_text(block)")
    print("        match = re.search(extract_pattern, text)")
    print("        if match:")
    print("            author_name = match.group(1).strip()")
    print("            break")
    print("    ")
    print("    if not author_name:")
    print("        return")
    print("    ")
    print("    # 3. 在作者列表中查找")
    print("    author_list_blocks = self.selector.select(config['target']['selector'])")
    print("    for block in author_list_blocks:")
    print("        text = self._get_block_text(block)")
    print("        # 构建查找模式")
    print("        search_pattern = config['target']['pattern'].format(extracted=re.escape(author_name))")
    print("        if not re.search(search_pattern, text):")
    print("            # 创建 Issue")
    print("            ...")
    print("```")
    print()
    
    print("=" * 80)
    print("推荐：方案 B（立即可用）+ 方案 C（未来增强）")
    print("=" * 80)
    print()
    print("理由：")
    print("1. ✅ 方案 B 可以立即实现，提供基本保护")
    print("2. ✅ 方案 C 提供完整的验证，但需要扩展 RuleChecker")
    print("3. ✅ 两者可以并存，逐步增强")
    print()


def main():
    """主函数"""
    success = test_cross_validation()
    propose_rule_config()
    
    if success:
        print()
        print("🎉 所有测试通过！")
        print()
    else:
        print()
        print("❌ 部分测试失败")
        print()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
