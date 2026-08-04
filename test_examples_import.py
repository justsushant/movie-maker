#!/usr/bin/env python3
"""
Quick test to verify examples can be imported and have valid syntax.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_import(module_path):
    """Test if a module can be imported."""
    try:
        # Read and compile the file
        with open(module_path, 'r') as f:
            code = f.read()
        compile(code, module_path, 'exec')
        print(f"✓ {module_path}: Syntax valid")
        return True
    except SyntaxError as e:
        print(f"✗ {module_path}: Syntax error - {e}")
        return False
    except Exception as e:
        print(f"✗ {module_path}: Error - {e}")
        return False

def main():
    """Test all example files."""
    examples = [
        "examples/demo_phase2_showcase.py",
        "examples/demo_phase3_audio_reactive.py",
        "examples/dragon/create_dragon_video_phase4.py",
        "examples/mahabharata/create_mahabharata_video_phase4.py",
    ]
    
    print("="*70)
    print("TESTING EXAMPLE SYNTAX")
    print("="*70)
    
    results = []
    for example in examples:
        if Path(example).exists():
            success = test_import(example)
            results.append((example, success))
        else:
            print(f"✗ {example}: File not found")
            results.append((example, False))
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for example, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {example}")
    
    print(f"\nResults: {passed}/{total} examples have valid syntax")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
