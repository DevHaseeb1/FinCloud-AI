"""
Quick validation: simulate what the upload pipeline does to the enhanced CSV.
"""

import pandas as pd
import sys
from pathlib import Path

CSV = Path(__file__).resolve().parent.parent / "Fincloud-cur-enhanced.csv"

df = pd.read_csv(CSV, dtype=str)
print(f"Original rows: {len(df)}")

# ── Normalize column names ──────────────────────────────────────────────
def normalize(col):
    col = col.replace("/", "_").replace("-", "_")
    result = []
    for i, c in enumerate(col):
        if c.isupper() and i > 0 and (col[i-1].islower() or col[i-1].isdigit()):
            result.append("_")
        result.append(c)
    col = "".join(result).lower()
    while "__" in col:
        col = col.replace("__", "_")
    return col.strip("_")

df.columns = [normalize(c) for c in df.columns]

# ── Map columns ──────────────────────────────────────────────────────────
mapping = {
    "timestamp": ["line_item_usage_start_date", "identity_time_interval"],
    "service":   ["product_servicename", "product_servicecode", "product_product_name"],
    "total_cost":["line_item_unblended_cost", "line_item_blended_cost"],
}
for target, candidates in mapping.items():
    if target not in df.columns:
        for c in candidates:
            if c in df.columns:
                df = df.rename(columns={c: target})
                print(f"  Mapped {c} -> {target}")
                break
        else:
            print(f"  MISSING: {target}")

# ── Validate required ───────────────────────────────────────────────────
required = ["timestamp", "service", "total_cost"]
missing_cols = [c for c in required if c not in df.columns]
if missing_cols:
    print(f"\nERROR: Missing columns: {missing_cols}")
    sys.exit(1)

print("\nAll required columns present")

# ── Parse types ─────────────────────────────────────────────────────────
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df["total_cost"] = pd.to_numeric(df["total_cost"], errors="coerce")
df["service"] = df["service"].astype(str).str.lower().str.strip()

invalid_ts = df["timestamp"].isna().sum()
invalid_svc = (df["service"].isna() | (df["service"].str.strip() == "")).sum()
invalid_cost = df["total_cost"].isna().sum()

print(f"\nInvalid timestamps: {invalid_ts}")
print(f"Invalid services:   {invalid_svc}")
print(f"Invalid costs:      {invalid_cost}")

# ── Clean ────────────────────────────────────────────────────────────────
initial = len(df)
df = df.dropna(subset=["timestamp", "service", "total_cost"])
df = df[df["service"].str.strip() != ""]
df = df[df["total_cost"].notna()]
dropped = initial - len(df)
print(f"Dropped rows: {dropped}")
print(f"Rows after cleaning: {len(df)}")

# ── Summary ──────────────────────────────────────────────────────────────
total = df["total_cost"].sum()
print(f"\nTotal cost: ${total:.2f}")

print("\nService breakdown:")
for svc, cost in df.groupby("service")["total_cost"].sum().sort_values(ascending=False).items():
    print(f"  {svc:<30s} ${cost:>7.2f}")

print(f"\nDate range: {df['timestamp'].min()} -> {df['timestamp'].max()}")
print(f"Days: {(df['timestamp'].max() - df['timestamp'].min()).days}")
print(f"\nAll checks PASSED")
