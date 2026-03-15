import ast
import os
import sys

def check_file_documentation(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
        lines = source.splitlines()

    tree = ast.parse(source)
    missing = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            has_comment = False
            
            # 1. Check ABOVE the function
            start_line = node.lineno - 1
            search_line = start_line - 1
            while search_line >= 0:
                current_line = lines[search_line].strip()
                if current_line.startswith("#"):
                    has_comment = True
                    break
                elif not current_line:
                    search_line -= 1
                    continue
                else:
                    break
            
            # 2. Check INSIDE the function (first non-empty line)
            if not has_comment and hasattr(node, 'body') and node.body:
                first_node = node.body[0]
                # Check lines between def and first statement
                for i in range(node.lineno, first_node.lineno):
                    if lines[i].strip().startswith("#"):
                        has_comment = True
                        break
                # Also check if it's a docstring (though we're avoiding them)
                if not has_comment and isinstance(first_node, ast.Expr) and \
                   isinstance(first_node.value, ast.Constant) and \
                   isinstance(first_node.value.value, str):
                    has_comment = True
            
            if not has_comment:
                missing.append(f"Line {node.lineno}: {node.name}")

    return missing

def main():
    backend_dir = "backend"
    files_to_check = [
        os.path.join(backend_dir, "validate.py"),
        os.path.join(backend_dir, "generate.py"),
        os.path.join(backend_dir, "protocols.py")
    ]
    
    all_missing = {}
    for f in files_to_check:
        if os.path.exists(f):
            m = check_file_documentation(f)
            if m:
                all_missing[f] = m
                
    if all_missing:
        print("[FAIL] Documentation Quality Check FAILED")
        for f, m in all_missing.items():
            print(f"\nMissing documentation in {f}:")
            for item in m:
                print(f"  - {item}")
        sys.exit(1)
    else:
        print("[SUCCESS] Documentation Quality Check PASSED")
        sys.exit(0)

if __name__ == "__main__":
    main()
