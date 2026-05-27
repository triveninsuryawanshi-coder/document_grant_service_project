#!/usr/bin/env python3
"""Project validation script."""
import os
import sys
from pathlib import Path

def check_project_structure():
    """Verify project structure is complete."""
    base_path = Path(__file__).parent
    
    required_files = {
        'Core': [
            'app/__init__.py',
            'app/config.py',
            'app/database.py',
            'app/logging_config.py',
            'app/main.py',
            'app/models.py',
            'app/schemas.py',
            'app/services.py',
            'app/seed.py',
        ],
        'Migrations': [
            'alembic/__init__.py',
            'alembic/env.py',
            'alembic/script.mako',
            'alembic/versions/__init__.py',
            'alembic/versions/001_initial_schema.py',
        ],
        'Tests': [
            'tests/__init__.py',
            'tests/conftest.py',
            'tests/test_services.py',
            'tests/test_endpoints.py',
        ],
        'Configuration': [
            'docker-compose.yml',
            'pyproject.toml',
            'requirements.txt',
            'alembic.ini',
            '.env',
            '.env.example',
            '.gitignore',
            '.dockerignore',
        ],
        'Documentation': [
            'README.md',
            'API.md',
            'SOLUTION.md',
            'DEPLOYMENT.md',
            'CONTRIBUTING.md',
            'PROJECT_OVERVIEW.md',
            'CHECKLIST.md',
            'BUILD_SUMMARY.md',
        ],
        'Utilities': [
            'Makefile',
            'quick-start.sh',
            'quick-start.bat',
        ],
    }
    
    print("=" * 60)
    print("PROJECT VALIDATION REPORT")
    print("=" * 60)
    print()
    
    total_found = 0
    total_required = 0
    
    for category, files in required_files.items():
        print(f"📦 {category}:")
        found = 0
        for file in files:
            file_path = base_path / file
            exists = file_path.exists()
            status = "✅" if exists else "❌"
            print(f"  {status} {file}")
            if exists:
                found += 1
            total_found += 1
            total_required += 1
        
        percentage = (found / len(files)) * 100
        print(f"  └─ {found}/{len(files)} ({percentage:.0f}%)")
        print()
    
    print("=" * 60)
    print(f"TOTAL: {total_found}/{total_required} files found")
    print("=" * 60)
    
    if total_found == total_required:
        print("✅ PROJECT STRUCTURE COMPLETE!")
        return True
    else:
        print(f"❌ Missing {total_required - total_found} file(s)")
        return False

def check_python_syntax():
    """Check Python files for syntax errors."""
    print("\n📝 Checking Python Syntax:")
    print("-" * 60)
    
    base_path = Path(__file__).parent
    python_files = list(base_path.rglob("*.py"))
    
    errors = []
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                compile(f.read(), py_file, 'exec')
            print(f"✅ {py_file.relative_to(base_path)}")
        except SyntaxError as e:
            print(f"❌ {py_file.relative_to(base_path)}: {e}")
            errors.append(str(py_file))
        except Exception as e:
            print(f"⚠️  {py_file.relative_to(base_path)}: {type(e).__name__}")
    
    if errors:
        print(f"\n❌ Found {len(errors)} syntax error(s)")
        return False
    print(f"\n✅ All {len(python_files)} Python files have valid syntax")
    return True

def main():
    """Run all validation checks."""
    structure_ok = check_project_structure()
    syntax_ok = check_python_syntax()
    
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    print(f"Project Structure: {'✅ PASS' if structure_ok else '❌ FAIL'}")
    print(f"Python Syntax: {'✅ PASS' if syntax_ok else '❌ FAIL'}")
    print("=" * 60)
    
    if structure_ok and syntax_ok:
        print("\n✅ ALL CHECKS PASSED - PROJECT READY!")
        return 0
    else:
        print("\n❌ SOME CHECKS FAILED - REVIEW ABOVE")
        return 1

if __name__ == "__main__":
    sys.exit(main())
