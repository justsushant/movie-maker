#!/usr/bin/env python3
"""
Verification script for Phase 4 - Test all example scripts.

This script tests that existing user code examples still work correctly
with Phase 4 additions.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Examples to test
EXAMPLES = [
    "examples/demo_phase2_showcase.py",
    "examples/demo_phase3_audio_reactive.py",
    "examples/dragon/create_dragon_video_phase4.py",
    "examples/mahabharata/create_mahabharata_video_phase4.py",
]

def test_example(script_path: str) -> Tuple[bool, str]:
    """
    Test a single example script.
    
    Returns:
        (success, output): Success status and output message
    """
    print(f"\n{'='*70}")
    print(f"Testing: {script_path}")
    print('='*70)
    
    if not Path(script_path).exists():
        return False, f"Script not found: {script_path}"
    
    try:
        # Run the script with a timeout
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print(f"✓ SUCCESS: {script_path}")
            return True, "Script executed successfully"
        else:
            print(f"✗ FAILED: {script_path}")
            print(f"Exit code: {result.returncode}")
            print(f"STDERR:\n{result.stderr[:500]}")
            return False, f"Exit code {result.returncode}: {result.stderr[:200]}"
            
    except subprocess.TimeoutExpired:
        print(f"✗ TIMEOUT: {script_path}")
        return False, "Script timed out after 5 minutes"
    except Exception as e:
        print(f"✗ ERROR: {script_path}")
        print(f"Exception: {e}")
        return False, str(e)

def main():
    """Run all example tests and report results."""
    print("="*70)
    print("PHASE 4 EXAMPLE VERIFICATION")
    print("="*70)
    
    results = []
    
    for example in EXAMPLES:
        success, message = test_example(example)
        results.append((example, success, message))
    
    # Print summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for example, success, message in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {example}")
        if not success:
            print(f"  Reason: {message}")
    
    print(f"\nResults: {passed}/{total} examples passed")
    
    if passed == total:
        print("\n✓ All examples work correctly with Phase 4!")
        return 0
    else:
        print(f"\n✗ {total - passed} example(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
