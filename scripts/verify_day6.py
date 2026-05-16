from pathlib import Path

required_files = [
    Path("docs/fabric/setup.md"),
    Path("fabric/README.md"),
]

required_dirs = [
    Path("docs/fabric/screenshots"),
    Path("fabric/notebooks"),
]

missing = []

for path in required_files:
    if not path.exists():
        missing.append(str(path))

for path in required_dirs:
    if not path.exists():
        missing.append(str(path))

if missing:
    print("DAY 6 VERIFY FAILED")
    print("Missing required files/folders:")
    for item in missing:
        print(f" - {item}")
    raise SystemExit(1)

setup = Path("docs/fabric/setup.md").read_text(encoding="utf-8")

required_phrases = [
    "Agile HR Copilot Dev",
    "agile_hr_lakehouse",
    "Local-to-Fabric Mapping",
    "Blocker Log",
    "Day 6 Done Condition",
    "lakehouse/gold",
    "fact_attrition_risk",
]

missing_phrases = [phrase for phrase in required_phrases if phrase not in setup]

if missing_phrases:
    print("DAY 6 VERIFY FAILED")
    print("Missing required setup.md phrases:")
    for phrase in missing_phrases:
        print(f" - {phrase}")
    raise SystemExit(1)

screenshots = sorted(Path("docs/fabric/screenshots").glob("*.png"))

print("DAY 6 VERIFY PASSED")
print(f"setup doc: docs/fabric/setup.md")
print(f"fabric readme: fabric/README.md")
print(f"screenshot count: {len(screenshots)}")
if screenshots:
    print("screenshots:")
    for shot in screenshots:
        print(f" - {shot}")
else:
    print("screenshots: none yet — acceptable only if Fabric access is documented as blocked")
