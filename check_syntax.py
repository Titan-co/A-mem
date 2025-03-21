import py_compile
import os
import sys

def check_file_syntax(filepath):
    print(f"Checking syntax of {filepath}")
    try:
        py_compile.compile(filepath, doraise=True)
        print(f"✓ Syntax OK for {filepath}")
        return True
    except Exception as e:
        print(f"✗ Syntax error in {filepath}: {e}")
        return False

def check_file_imports(filepath):
    print(f"Checking imports in {filepath}")
    with open(filepath, 'r') as f:
        content = f.read()
    
    import_lines = [line.strip() for line in content.split('\n') if line.strip().startswith('import ') or line.strip().startswith('from ')]
    
    all_imports_ok = True
    for import_line in import_lines:
        try:
            print(f"Testing: {import_line}")
            exec(import_line)
            print(f"✓ Import OK: {import_line}")
        except Exception as e:
            print(f"✗ Import error: {import_line} - {e}")
            all_imports_ok = False
    
    return all_imports_ok

if __name__ == "__main__":
    python_files = [f for f in os.listdir('.') if f.endswith('.py')]
    
    print(f"Found {len(python_files)} Python files")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    
    for pyfile in python_files:
        print("="*50)
        print(f"Checking {pyfile}")
        syntax_ok = check_file_syntax(pyfile)
        if syntax_ok:
            import_ok = check_file_imports(pyfile)
        print()
    
    print("\nFocusing on server.py:")
    if 'server.py' in python_files:
        print("="*50)
        print("CONTENT OF server.py:")
        with open('server.py', 'r') as f:
            print(f.read())
    else:
        print("server.py not found!")
