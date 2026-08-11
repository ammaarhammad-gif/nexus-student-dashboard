import re
import ast

with open('models.py', 'r', encoding='utf-8') as f:
    code = f.read()

tree = ast.parse(code)
functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
print(f"Total function definitions in models.py: {len(functions)}")

missing_user_id = []
dynamic_sql_calls = []

# Excluded utility functions that legitimately don't take user_id
ALLOWED_NO_USER_ID = {
    'create_user', 'verify_user', 'get_user_by_id', '_calculate_streak',
    '_get_cached_syllabi', 'list_preloaded_syllabi', '_build_node_tree',
    '_format_duration', '_parse_latex', '_sanitize_html'
}

for fn in functions:
    fn_name = fn.name
    arg_names = [a.arg for a in fn.args.args]
    fn_code = ast.get_source_segment(code, fn)
    
    if 'cursor.execute' in fn_code:
        if 'user_id' not in arg_names and fn_name not in ALLOWED_NO_USER_ID:
            missing_user_id.append((fn_name, arg_names))
            
        # Check for non-parameterized calls or formatted strings
        for node in ast.walk(fn):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'execute':
                    first_arg = node.args[0] if node.args else None
                    if isinstance(first_arg, (ast.JoinedStr, ast.BinOp)):
                        dynamic_sql_calls.append((fn_name, ast.unparse(first_arg)[:100]))

print("\n--- 1. DATABASE FUNCTIONS MISSING user_id PARAMETER ---")
if not missing_user_id:
    print("None! All DB operations enforce user_id parameter.")
else:
    for fn, args in missing_user_id:
        print(f"  ❌ {fn}({', '.join(args)})")

print("\n--- 2. POTENTIAL DYNAMIC SQL INTERPOLATIONS ---")
if not dynamic_sql_calls:
    print("None! All queries use parameterized statements (%s).")
else:
    for fn, sql_sample in dynamic_sql_calls:
        print(f"  ⚠️ {fn}: {sql_sample}")

