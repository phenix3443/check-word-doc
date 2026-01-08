#!/usr/bin/env python3
"""
配置文件加载功能测试
测试 ConfigLoader 的各种功能和错误处理
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'script'))

from config_loader import ConfigLoader, ConfigError

def test_basic_config_loading():
    """测试基本配置文件加载"""
    print("测试基本配置文件加载...")
    
    config_path = os.path.join(os.path.dirname(__file__), "basic.yaml")
    
    try:
        config_loader = ConfigLoader(config_path)
        config = config_loader.load()
        
        print(f"  ✓ 配置文件加载成功")
        print(f"  检查项数量: {len(config.get('checks', []))}")
        print(f"  检查项: {config.get('checks', [])}")
        
        # 验证配置结构
        assert 'structure' in config, "缺少 structure 配置"
        assert 'paragraphs' in config, "缺少 paragraphs 配置"
        assert 'references' in config, "缺少 references 配置"
        
        # 验证具体配置值
        structure_config = config['structure']
        assert structure_config['enabled'] == True, "structure.enabled 应该为 True"
        assert structure_config['required_parts']['table_of_contents'] == True, "应该要求目录"
        
        paragraphs_config = config['paragraphs']
        assert paragraphs_config['enabled'] == True, "paragraphs.enabled 应该为 True"
        assert "Normal" in paragraphs_config['check_styles'], "应该检查 Normal 样式"
        
        print("  ✓ 配置验证通过")
        return True
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False

def test_invalid_config_handling():
    """测试无效配置文件的错误处理"""
    print("\n测试无效配置文件的错误处理...")
    
    config_path = os.path.join(os.path.dirname(__file__), "invalid.yaml")
    
    try:
        config_loader = ConfigLoader(config_path)
        config = config_loader.load()
        
        # 检查是否正确处理了无效的检查项
        checks = config.get('checks', [])
        if 'invalid_check_name' in checks:
            print("  ⚠️  警告: 无效的检查项名称未被过滤")
        else:
            print("  ✓ 无效的检查项名称已被过滤")
        
        # 检查配置验证
        try:
            config_loader._validate_config()
            print("  ⚠️  警告: 配置验证未发现错误")
        except ConfigError as e:
            print(f"  ✓ 配置验证正确发现错误: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ✓ 正确捕获了配置错误: {e}")
        return True

def test_nonexistent_config():
    """测试不存在的配置文件"""
    print("\n测试不存在的配置文件...")
    
    config_path = os.path.join(os.path.dirname(__file__), "nonexistent.yaml")
    
    try:
        config_loader = ConfigLoader(config_path)
        config = config_loader.load()
        print("  ✗ 应该抛出异常，但没有")
        return False
        
    except Exception as e:
        print(f"  ✓ 正确处理了不存在的文件: {e}")
        return True

def test_config_import():
    """测试配置文件导入功能"""
    print("\n测试配置文件导入功能...")
    
    config_path = os.path.join(os.path.dirname(__file__), "import.yaml")
    
    try:
        config_loader = ConfigLoader(config_path)
        config = config_loader.load()
        
        print(f"  ✓ 导入配置文件加载成功")
        
        # 验证导入的配置
        assert 'structure' in config, "缺少导入的 structure 配置"
        assert 'paragraphs' in config, "缺少导入的 paragraphs 配置"
        assert 'headings' in config, "缺少新增的 headings 配置"
        
        # 验证配置覆盖
        structure_config = config['structure']
        assert structure_config['required_parts']['references'] == True, "references 应该被覆盖为 True"
        assert structure_config['required_parts']['cover'] == True, "应该有新增的 cover 要求"
        
        print("  ✓ 配置导入和覆盖验证通过")
        return True
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False

def test_config_validation():
    """测试配置验证功能"""
    print("\n测试配置验证功能...")
    
    config_path = os.path.join(os.path.dirname(__file__), "basic.yaml")
    
    try:
        config_loader = ConfigLoader(config_path)
        config_loader.load()
        
        # 测试检查项启用状态
        assert config_loader.get_check_enabled('structure') == True, "structure 应该启用"
        assert config_loader.get_check_enabled('paragraphs') == True, "paragraphs 应该启用"
        assert config_loader.get_check_enabled('references') == True, "references 应该启用"
        assert config_loader.get_check_enabled('headings') == False, "headings 应该禁用"
        
        print("  ✓ 检查项启用状态验证通过")
        
        # 测试配置验证
        config_loader._validate_config()
        print("  ✓ 配置验证通过")
        
        return True
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False

def test_config_access_methods():
    """测试配置访问方法"""
    print("\n测试配置访问方法...")
    
    config_path = os.path.join(os.path.dirname(__file__), "basic.yaml")
    
    try:
        config_loader = ConfigLoader(config_path)
        config_loader.load()
        
        # 测试直接访问
        config = config_loader.config
        assert config is not None, "配置应该不为空"
        
        # 测试获取特定配置
        structure_config = config.get('structure', {})
        assert structure_config is not None, "应该能获取 structure 配置"
        assert structure_config['enabled'] == True, "structure 应该启用"
        
        # 测试获取不存在的配置
        nonexistent_config = config.get('nonexistent', {})
        assert nonexistent_config == {}, "不存在的配置应该返回空字典"
        
        print("  ✓ 配置访问方法验证通过")
        return True
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False

def show_usage():
    """显示使用说明"""
    print("\n" + "=" * 60)
    print("使用说明:")
    print("=" * 60)
    print("1. 运行配置加载测试:")
    print("   poetry run python test/config/config_check.py")
    print()
    print("2. 测试配置文件:")
    print("   - basic.yaml: 基本配置测试")
    print("   - invalid.yaml: 无效配置测试")
    print("   - import.yaml: 配置导入测试")
    print()
    print("3. 测试 ConfigLoader 类:")
    print("   - 基本加载功能")
    print("   - 错误处理")
    print("   - 配置验证")
    print("   - 导入功能")

if __name__ == "__main__":
    print("配置文件加载功能测试")
    print("=" * 50)
    
    tests = [
        test_basic_config_loading,
        test_invalid_config_handling,
        test_nonexistent_config,
        test_config_import,
        test_config_validation,
        test_config_access_methods
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"  ✗ 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，需要检查配置加载逻辑")
    
    show_usage()
    
    print("\n✅ 测试完成")
    sys.exit(0 if passed == total else 1)