from pathlib import Path
import re
import subprocess


required = [
    "README.md",
    ".env.example",
    "docs/architecture.md",
    "docs/model_card.md",
    "docs/fairness_audit_summary.csv",
    "docs/fairness_auc_by_group.csv",
    "docs/images/fairness_audit.png",
    "docs/run_locally.md",
    "docs/demo_script.md",
    "docs/interview_prep.md",
    "docs/final_checklist.md",
    "notebooks/05_fairness_audit.ipynb",
    "scripts/day4_governance.py",
]

recommended_images = [
    "docs/images/copilot_narrative.png",
    "docs/images/copilot_qa.png",
    "docs/images/copilot_risk.png",
]

powerbi_images = [
    "docs/images/page1_executive.png",
    "docs/images/page2_attrition.png",
    "docs/images/page3_engagement.png",
    "docs/images/page4_diversity.png",
    "docs/images/page5_workforce.png",
]

missing_required = [p for p in required if not Path(p).exists()]
missing_recommended = [p for p in recommended_images if not Path(p).exists()]
missing_powerbi = [p for p in powerbi_images if not Path(p).exists()]

if missing_required:
    print("DAY 4 VERIFY FAILED — missing required files:")
    for p in missing_required:
        print(" -", p)
    raise SystemExit(1)

readme = Path("README.md").read_text(encoding="utf-8", errors="ignore")
image_refs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme)
broken_refs = [ref for ref in image_refs if not Path(ref).exists()]

if broken_refs:
    print("DAY 4 VERIFY FAILED — README has broken image refs:")
    for ref in broken_refs:
        print(" -", ref)
    raise SystemExit(1)

tracked_env = subprocess.run(
    ["git", "ls-files", ".env"],
    capture_output=True,
    text=True,
    check=False,
).stdout.strip()

tracked_audit = subprocess.run(
    ["git", "ls-files", "apps/api/audit.log"],
    capture_output=True,
    text=True,
    check=False,
).stdout.strip()

tracked_raw = subprocess.run(
    ["git", "ls-files", "data/raw"],
    capture_output=True,
    text=True,
    check=False,
).stdout.splitlines()
tracked_raw_bad = [p for p in tracked_raw if not p.endswith(".gitkeep")]

tracked_lakehouse = subprocess.run(
    ["git", "ls-files", "lakehouse"],
    capture_output=True,
    text=True,
    check=False,
).stdout.splitlines()
tracked_lakehouse_bad = [
    p for p in tracked_lakehouse
    if p.endswith(".parquet") or p.endswith(".duckdb")
]

if tracked_env:
    print("DAY 4 VERIFY FAILED — .env is tracked:")
    print(tracked_env)
    raise SystemExit(1)

if tracked_audit:
    print("DAY 4 VERIFY FAILED — audit log is tracked:")
    print(tracked_audit)
    raise SystemExit(1)

if tracked_raw_bad:
    print("DAY 4 VERIFY FAILED — raw data files are tracked:")
    for p in tracked_raw_bad:
        print(" -", p)
    raise SystemExit(1)

if tracked_lakehouse_bad:
    print("DAY 4 VERIFY FAILED — generated lakehouse files are tracked:")
    for p in tracked_lakehouse_bad:
        print(" -", p)
    raise SystemExit(1)

print("DAY 4 VERIFY PASSED — governance/docs are ready.")
print("\nRecommended Copilot screenshots:")
if missing_recommended:
    for p in missing_recommended:
        print(" - missing:", p)
else:
    print(" - all present")

print("\nPower BI screenshots:")
if missing_powerbi:
    for p in missing_powerbi:
        print(" - missing:", p)
else:
    print(" - all present")
