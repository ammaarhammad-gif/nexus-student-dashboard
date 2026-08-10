import os
import sys
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

root = os.path.dirname(os.path.abspath(__file__))
pages_dir = os.path.join(root, "pages_modules")

print("=" * 60)
print("PAGES MODULES PRODUCTION READINESS AUDIT")
print("=" * 60)

for f in sorted(os.listdir(pages_dir)):
    if not f.endswith(".py"):
        continue
    fpath = os.path.join(pages_dir, f)
    with open(fpath, "r", encoding="utf-8") as file:
        content = file.read()
        lines = content.splitlines()

    print(f"\n📄 Auditing {f} ({len(lines)} lines)...")

    # Check plotly charts responsiveness
    plotly_figs = [i+1 for i, l in enumerate(lines) if "st.plotly_chart(" in l]
    for p_line in plotly_figs:
        line_txt = lines[p_line-1]
        has_container_width = "use_container_width=True" in line_txt or "use_container_width" in lines[min(p_line, len(lines)-1)]
        if not has_container_width:
            print(f"  ⚠️ Line {p_line}: st.plotly_chart might be missing `use_container_width=True`")

    # Check unhandled st.rerun or session_state access
    for idx, l in enumerate(lines, 1):
        if "st.session_state[" in l:
            # Check if key is set or get
            pass

    # Check empty state handling
    has_empty_check = any("len(" in l and "== 0" in l for l in lines) or any("if not " in l for l in lines)
    if not has_empty_check:
        print(f"  ℹ️ Notice: Check if {f} has sufficient empty-state handling.")

print("\nAudit of pages_modules complete!")
