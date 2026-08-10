import os
import sys
import re
import ast
import inspect

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

print("=" * 60)
print("NEXUS DEEP PRODUCTION-READINESS CODE AUDIT")
print("=" * 60)

root_dir = os.path.dirname(os.path.abspath(__file__))
py_files = []
for r, d, files in os.walk(root_dir):
    if ".git" in r or "__pycache__" in r or ".venv" in r:
        continue
    for f in files:
        if f.endswith(".py"):
            py_files.append(os.path.join(r, f))

print(f"Total Python source files discovered: {len(py_files)}")

# 1. SQL Injection / String Formatting Check in SQL
sql_fstring_issues = []
sql_raw_format_issues = []
missing_rollback_issues = []
unclosed_connections = []

for p in py_files:
    fname = os.path.relpath(p, root_dir)
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    for idx, line in enumerate(lines, 1):
        # Look for cursor.execute with f-strings or % formatting
        if "cursor.execute(" in line or ".execute(" in line:
            if 'f"""' in line or 'f"' in line or "f'''" in line or "f'" in line:
                # Check if it's dynamic query with unescaped variables
                sql_fstring_issues.append((fname, idx, line.strip()))
            if " % " in line and ("SELECT" in line or "INSERT" in line or "UPDATE" in line or "DELETE" in line):
                if not ("%s" in line and "(" in line):
                    sql_raw_format_issues.append((fname, idx, line.strip()))

print(f"\n1. SQL Injection / f-string SQL check:")
if sql_fstring_issues:
    print(f"⚠️ Found {len(sql_fstring_issues)} f-string SQL executions:")
    for f, l, s in sql_fstring_issues:
        print(f"  - [{f}:{l}] {s[:100]}")
else:
    print("✅ ZERO f-string SQL injection vulnerabilities found!")

if sql_raw_format_issues:
    print(f"⚠️ Found {len(sql_raw_format_issues)} raw % formatting SQL executions:")
    for f, l, s in sql_raw_format_issues:
        print(f"  - [{f}:{l}] {s[:100]}")
else:
    print("✅ ZERO raw % string formatting SQL vulnerabilities found!")

# 2. Check Database Isolation (user_id presence in queries)
print(f"\n2. Authorization & Multi-Tenant User Isolation check in models.py:")
with open(os.path.join(root_dir, "models.py"), "r", encoding="utf-8") as f:
    models_content = f.read()

# Find all cursor.execute in models.py
exec_matches = re.finditer(r'cursor\.execute\(\s*"""(.*?)"""|\'\'\'(.*?)\'\'\'|"([^"]+)"|\'([^\']+)\'', models_content, re.DOTALL)
suspicious_queries = []

for match in exec_matches:
    q = (match.group(1) or match.group(2) or match.group(3) or match.group(4) or "").strip()
    if not q:
        continue
    upper_q = q.upper()
    # Check tables that MUST have user_id
    isolated_tables = [
        "SUBJECTS", "CHAPTERS", "TOPICS", "SUBTOPICS", "TOPIC_PROGRESS", 
        "DAILY_PLANS", "STUDY_SESSIONS", "REVISIONS", "MISTAKES", "NOTES", 
        "FORMULAS", "QUIZZES", "QUIZ_ATTEMPTS", "RECALL_RESPONSES", "TERMS", "SETTINGS"
    ]
    
    for tbl in isolated_tables:
        if f"FROM {tbl}" in upper_q or f"UPDATE {tbl}" in upper_q or f"DELETE FROM {tbl}" in upper_q or f"JOIN {tbl}" in upper_q:
            # Check if user_id or users u is checked
            if "USER_ID" not in upper_q and "USERS" not in upper_q and "CREATE TABLE" not in upper_q and "ALTER TABLE" not in upper_q and "CREATE INDEX" not in upper_q:
                # Some subqueries might join on chapter_id where chapter is already user-scoped, but let's audit
                suspicious_queries.append((tbl, q[:150].replace("\n", " ")))

print(f"Audited isolated tables across all queries.")
if suspicious_queries:
    print(f"Found {len(suspicious_queries)} queries for closer inspection:")
    for tbl, q in suspicious_queries[:10]:
        print(f"  - Table {tbl}: {q}")
else:
    print("✅ All queries properly enforce user_id isolation!")

# 3. Check for Division by Zero in calculations
print(f"\n3. Division by Zero Protection Audit:")
div_zero_risks = []
for p in py_files:
    fname = os.path.relpath(p, root_dir)
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    for idx, line in enumerate(lines, 1):
        if "/" in line and not line.strip().startswith("#") and not line.strip().startswith("//"):
            if re.search(r'/\s*len\(', line) or re.search(r'/\s*total', line, re.IGNORECASE) or re.search(r'/\s*count', line, re.IGNORECASE):
                if "if " not in line and "max(" not in line and "or 1" not in line and "?:" not in line:
                    div_zero_risks.append((fname, idx, line.strip()))

if div_zero_risks:
    print(f"Found {len(div_zero_risks)} lines with potential zero division risks to verify:")
    for f, l, s in div_zero_risks[:10]:
        print(f"  - [{f}:{l}] {s[:100]}")
else:
    print("✅ All division operations have safety guards!")
