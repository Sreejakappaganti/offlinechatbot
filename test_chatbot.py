#!/usr/bin/env python3
"""
Tests for the offline chatbot (without requiring model download).

These tests validate the code structure and basic functionality.
"""

import sys
import ast


def test_config():
    """Test configuration module."""
    print("Testing config.py...")
    import config
    
    # Check required attributes exist
    required_attrs = [
        'MODEL_NAME', 'MODEL_CACHE_DIR', 'MAX_NEW_TOKENS',
        'TEMPERATURE', 'TOP_P', 'TOP_K', 'DO_SAMPLE', 'MAX_HISTORY'
    ]
    
    for attr in required_attrs:
        assert hasattr(config, attr), f"Missing required config: {attr}"
    
    # Validate types and ranges
    assert isinstance(config.MODEL_NAME, str), "MODEL_NAME must be string"
    assert isinstance(config.MAX_NEW_TOKENS, int), "MAX_NEW_TOKENS must be int"
    assert 0.0 <= config.TEMPERATURE <= 2.0, "TEMPERATURE must be between 0 and 2"
    assert 0.0 <= config.TOP_P <= 1.0, "TOP_P must be between 0 and 1"
    assert config.MAX_HISTORY > 0, "MAX_HISTORY must be positive"
    
    print("✓ config.py tests passed\n")


def test_chatbot_structure():
    """Test chatbot.py structure without importing (to avoid dependencies)."""
    print("Testing chatbot.py structure...")
    
    with open('chatbot.py', 'r') as f:
        tree = ast.parse(f.read())
    
    # Find classes and methods
    classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            classes[node.name] = methods
    
    # Check OfflineChatbot class exists with required methods
    assert 'OfflineChatbot' in classes, "OfflineChatbot class not found"
    
    required_methods = ['__init__', 'generate_response', 'chat']
    for method in required_methods:
        assert method in classes['OfflineChatbot'], f"Missing method: {method}"
    
    # Check for main function
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    assert 'main' in functions, "main function not found"
    
    print("✓ chatbot.py structure tests passed\n")


def test_requirements():
    """Test requirements.txt."""
    print("Testing requirements.txt...")
    
    with open('requirements.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    # Check for essential packages
    essential = ['transformers', 'torch', 'sentencepiece']
    for package in essential:
        assert any(package in line for line in lines), f"Missing package: {package}"
    
    print("✓ requirements.txt tests passed\n")


def test_gitignore():
    """Test .gitignore."""
    print("Testing .gitignore...")
    
    with open('.gitignore', 'r') as f:
        content = f.read()
    
    # Check for important exclusions
    important_patterns = ['__pycache__', 'models/', 'venv/', '.env']
    for pattern in important_patterns:
        assert pattern in content, f"Missing .gitignore pattern: {pattern}"
    
    # Check for Python bytecode exclusion (either *.pyc or *.py[cod])
    assert '*.pyc' in content or '*.py[cod]' in content, "Missing Python bytecode pattern"
    
    print("✓ .gitignore tests passed\n")


def test_readme():
    """Test README.md."""
    print("Testing README.md...")
    
    with open('README.md', 'r') as f:
        content = f.read()
    
    # Check for important sections
    important_sections = [
        'Installation', 'Usage', 'Requirements',
        'Offline', 'Gemma'
    ]
    for section in important_sections:
        assert section in content, f"README missing section: {section}"
    
    # Check for code blocks
    assert '```' in content, "README should have code examples"
    
    print("✓ README.md tests passed\n")


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("Running Offline Chatbot Tests")
    print("=" * 70 + "\n")
    
    tests = [
        test_config,
        test_chatbot_structure,
        test_requirements,
        test_gitignore,
        test_readme
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}\n")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}\n")
            failed += 1
    
    print("=" * 70)
    if failed == 0:
        print("All tests passed! ✓")
        print("=" * 70 + "\n")
        return 0
    else:
        print(f"{failed} test(s) failed ✗")
        print("=" * 70 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
