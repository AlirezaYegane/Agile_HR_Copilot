from pathlib import Path
import pandas as pd

GOLD = Path("lakehouse/gold")

pulse_path = GOLD / "fact_engagement_pulse.parquet"
out_path = GOLD / "fact_pulse_themes.parquet"

if not pulse_path.exists():
    raise FileNotFoundError(f"Missing {pulse_path}")

pulse = pd.read_parquet(pulse_path)

required_cols = {"EmployeeID", "QuarterKey", "Quarter", "ThemesFlagged"}
missing = required_cols - set(pulse.columns)
if missing:
    raise ValueError(f"Missing columns in fact_engagement_pulse: {missing}")

themes = (
    pulse
    .dropna(subset=["ThemesFlagged"])
    .copy()
)

themes["Theme"] = themes["ThemesFlagged"].astype(str).str.split(",")
themes = themes.explode("Theme")
themes["Theme"] = themes["Theme"].astype(str).str.strip()

themes = themes[
    themes["Theme"].notna()
    & (themes["Theme"] != "")
    & (themes["Theme"].str.lower() != "none")
]

fact_pulse_themes = themes[
    ["EmployeeID", "QuarterKey", "Quarter", "Theme"]
].copy()

fact_pulse_themes["ThemeCount"] = 1

fact_pulse_themes.to_parquet(out_path, index=False)

print("Created:", out_path)
print("Rows:", len(fact_pulse_themes))
print()
print(fact_pulse_themes["Theme"].value_counts())
