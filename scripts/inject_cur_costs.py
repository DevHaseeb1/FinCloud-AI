"""
Inject realistic AWS on-demand costs into the real CUR CSV file.
Preserves ALL 127 columns - only cost/rate columns are modified.

Extends data to ~30 days and injects anomaly scenarios for the ML pipeline.

Usage: python scripts/inject_cur_costs.py
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

# Force UTF-8 for stdout (handles Windows cp1252 issues)
import sys, io
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

INPUT  = Path(__file__).resolve().parent.parent / "Fincloud-cur-00001.csv"
OUTPUT = Path(__file__).resolve().parent.parent / "Fincloud-cur-enhanced.csv"

# Column indices (0-based)
I_LINE_ITEM_TYPE    = 10
I_USAGE_START       = 11
I_USAGE_END         = 12
I_PRODUCT_CODE      = 13
I_USAGE_TYPE        = 14
I_OPERATION         = 15
I_AZ                = 16
I_RESOURCE_ID       = 17
I_USAGE_AMOUNT      = 18
I_NORM_FACTOR       = 19
I_NORM_USAGE        = 20
I_CURRENCY          = 21
I_UNBLENDED_RATE    = 22
I_UNBLENDED_COST    = 23
I_BLENDED_RATE      = 24
I_BLENDED_COST      = 25
I_PRODUCT_NAME      = 29    # product/ProductName
I_USAGE_ACCOUNT_ID  = 9     # lineItem/UsageAccountId
I_SERVICE_CODE      = 79    # product/servicecode
I_SERVICE_NAME      = 80    # product/servicename

# -- Rate lookup -----------------------------------------------------------
# Returns (rate_per_unit, is_zero) where rate_per_unit is already in
# the correct unit for UsageAmount (no conversion needed).
def get_rate(pc, ut):
    ut = ut or ""

    # EC2 compute (UsageAmount is in hours)
    if pc == "AmazonEC2":
        if "BoxUsage:t3.micro" in ut:     return 0.0104
        if "BoxUsage:t3.small" in ut:     return 0.0208
        if "BoxUsage:t3.medium" in ut:    return 0.0416
        if "CPUCredits" in ut:            return 0.0
        if "EBSOptimized" in ut:          return 0.0
        if "EBS:VolumeUsage.gp3" in ut:   return 0.08    # per GB-month
        # Data transfer (bytes -> GB conversion)
        if "DataTransfer-Out" in ut:      return 0.09 / (1024**3)
        if "DataTransfer-In" in ut:       return 0.0
        if "DataTransfer-Regional" in ut: return 0.01 / (1024**3)
        if "AWS-Out-Bytes" in ut:         return 0.02 / (1024**3)
        if "AWS-In-Bytes" in ut:          return 0.02 / (1024**3)
        if "CloudFront-Out" in ut:        return 0.085 / (1024**3)
        if "CloudFront-In" in ut:         return 0.0

    # VPC (UsageAmount is in hours)
    if pc == "AmazonVPC" and "PublicIPv4" in ut:
        return 0.005

    # S3
    if pc == "AmazonS3":
        # TimedStorage: UsageAmount is in byte-hours, convert to $/GB-month
        if "TimedStorage" in ut:
            return 0.023 / (1024**3 * 730.5)
        if "Requests-Tier1" in ut:        return 5e-6     # per request
        if "Requests-Tier2" in ut:        return 4e-7     # per request
        if "Requests-Tier3" in ut:        return 0.0
        if "DataTransfer-Out" in ut:      return 0.09 / (1024**3)
        if "DataTransfer-In" in ut:       return 0.0
        if "DataTransfer-Regional" in ut: return 0.01 / (1024**3)
        if "AWS-Out-Bytes" in ut:         return 0.02 / (1024**3)
        if "AWS-In-Bytes" in ut:          return 0.02 / (1024**3)
        if "Global-Bucket-Hrs-FreeTier" in ut: return 0.0

    # Glue
    if pc == "AWSGlue" and "Catalog-Request" in ut:
        return 1e-6  # $0.001/1k

    # KMS
    if pc == "awskms" and "KMS-Requests" in ut:
        return 3e-9  # $0.000003/10k

    # Secrets Manager
    if pc == "AWSSecretsManager" and "SecretsManager" in ut:
        return 3e-8  # $0.00003/10k

    # SQS / SNS (free tier)
    if pc in ("AWSQueueService", "AmazonSNS"):
        return 0.0

    # DataTransfer
    if pc == "AWSDataTransfer":
        return 0.02 / (1024**3)

    return None


# ── Service metadata for generated rows ───────────────────────────────────
# Maps product_code -> (product_name, service_name, service_code)
SERVICE_META = {
    "AmazonEC2": ("Amazon Elastic Compute Cloud", "Amazon Elastic Compute Cloud", "AmazonEC2"),
    "AmazonS3":  ("Amazon Simple Storage Service", "Amazon Simple Storage Service", "AmazonS3"),
    "AmazonRDS": ("Amazon Relational Database Service", "Amazon Relational Database Service", "AmazonRDS"),
    "AmazonVPC": ("Amazon Virtual Private Cloud", "Amazon Virtual Private Cloud", "AmazonVPC"),
    "AWSLambda": ("AWS Lambda", "AWS Lambda", "AWSLambda"),
    "AWSGlue":   ("AWS Glue", "AWS Glue", "AWSGlue"),
    "awskms":    ("AWS Key Management Service", "AWS Key Management Service", "awskms"),
    "AWSSecretsManager": ("AWS Secrets Manager", "AWS Secrets Manager", "AWSSecretsManager"),
    "AWSQueueService":   ("AWS Queue Service", "AWS Queue Service", "AWSQueueService"),
    "AmazonSNS": ("Amazon Simple Notification Service", "Amazon Simple Notification Service", "AmazonSNS"),
    "AWSDataTransfer":   ("AWS Data Transfer", "AWS Data Transfer", "AWSDataTransfer"),
}

def fill_metadata(row, pc):
    """Set service name/service code columns for a generated row."""
    meta = SERVICE_META.get(pc, (pc, pc, pc))
    row[I_PRODUCT_NAME]     = meta[0]
    row[I_SERVICE_CODE]     = meta[2]
    row[I_SERVICE_NAME]     = meta[1]
    row[I_USAGE_ACCOUNT_ID] = "430155298731"


def compute_cost(pc, ut, usage_amount_str):
    rate = get_rate(pc, ut)
    if rate is None or rate == 0:
        return 0.0, 0.0
    try:
        ua = float(usage_amount_str) if usage_amount_str else 0.0
    except (ValueError, TypeError):
        ua = 0.0
    return rate, rate * ua


# -- Timestamp helpers ----------------------------------------------------
def parse_ts(val):
    return datetime.strptime(val.rstrip("Z"), "%Y-%m-%dT%H:%M:%S")

def fmt_ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# -- Instance type upgrader ------------------------------------------------
def upgrade_usage_type(ut):
    """30% chance to promote t3.micro -> t3.small (to go beyond free tier)."""
    if not ut:
        return ut, False
    if "t3.micro" in ut and random.random() < 0.50:
        return ut.replace("t3.micro", "t3.small"), True
    return ut, False


# -- Assign realistic placeholder usage for free-tier/Credit rows ----------
def placeholder_usage(pc, ut, sd, ed):
    """Return a realistic usage amount string for free-tier rows that have $0 usage."""
    if pc == "AmazonS3":
        if "TimedStorage" in ut:
            # ~30 GB stored for the full period (byte-hours)
            hours = max(1, (ed - sd).total_seconds() / 3600)
            return str(30.0 * (1024**3) * hours * random.uniform(0.9, 1.1))
        if "Requests-Tier1" in ut:
            return str(int(random.uniform(1000, 10000)))
        if "Requests-Tier2" in ut:
            return str(int(random.uniform(5000, 50000)))
        if "DataTransfer-Out" in ut:
            return str(int(random.uniform(1e8, 5e8)))  # 100-500 MB
        if "DataTransfer-In" in ut:
            return str(int(random.uniform(5e8, 2e9)))  # 0.5-2 GB
        if "AWS-Out-Bytes" in ut:
            return str(int(random.uniform(1e8, 1e9)))
        if "Global-Bucket-Hrs-FreeTier" in ut:
            return "0.0"

    if pc == "AmazonEC2":
        if "EBS:VolumeUsage.gp3" in ut:
            # 30 GB for the period (GB-months proportional to hours)
            hours = max(1, (ed - sd).total_seconds() / 3600)
            return str(30.0 * hours / 730 * random.uniform(0.9, 1.1))
        if "DataTransfer-Out" in ut:
            return str(int(random.uniform(5e7, 2e8)))  # 50-200 MB
        if "DataTransfer-In" in ut:
            return str(int(random.uniform(1e8, 5e8)))
        if "DataTransfer-Regional" in ut:
            return str(int(random.uniform(1e8, 5e8)))
        if "CloudFront-Out" in ut:
            return str(int(random.uniform(5e8, 2e9)))
        if "CloudFront-In" in ut:
            return str(int(random.uniform(1e9, 5e9)))

    if pc == "AmazonVPC" and "PublicIPv4" in ut:
        # hours - 1.0 per row (each row is 1 hour)
        return "1.0"

    if pc == "AWSGlue" and "Catalog-Request" in ut:
        return str(int(random.uniform(10, 100)))

    if pc == "awskms" and "KMS-Requests" in ut:
        return str(int(random.uniform(100, 1000)))

    if pc == "AWSSecretsManager" and "SecretsManager" in ut:
        return str(int(random.uniform(50, 500)))

    return None


# ══════════════════════════════════════════════════════════════════════════
def main():
    # -- 1. Read CSV ------------------------------------------------------
    with open(INPUT, newline="", encoding="utf-8-sig") as f:
        reader = list(csv.reader(f))
    header = reader[0]
    rows   = reader[1:]
    print(f"Read {len(rows)} data rows ({len(header)} columns)")

    # -- 2. Determine date range ------------------------------------------
    all_dates = []
    for r in rows:
        if r[I_USAGE_START]:
            try:
                all_dates.append(parse_ts(r[I_USAGE_START]))
            except Exception:
                pass
    if not all_dates:
        print("ERROR: no valid timestamps found")
        return
    all_dates.sort()
    min_dt, max_dt = all_dates[0], all_dates[-1]
    span_days = (max_dt - min_dt).days
    print(f"Date range: {min_dt.date()} -> {max_dt.date()} ({span_days} days)")

    # -- 3. Process rows: compute cost, upgrade instances -----------------
    processed = []
    svc_costs = {}

    for r in rows:
        nr = list(r)
        pc  = nr[I_PRODUCT_CODE]
        ut  = nr[I_USAGE_TYPE]
        lit = nr[I_LINE_ITEM_TYPE]
        ua  = nr[I_USAGE_AMOUNT]

        # Parse timestamps
        try:
            sd = parse_ts(nr[I_USAGE_START])
            ed = parse_ts(nr[I_USAGE_END])
        except Exception:
            sd = ed = min_dt

        # Upgrade some t3.micro to t3.small
        if pc == "AmazonEC2" and "BoxUsage" in (ut or ""):
            new_ut, upgraded = upgrade_usage_type(ut)
            if upgraded:
                nr[I_USAGE_TYPE] = new_ut
                ut = new_ut

        # For free-tier Credit rows where UsageAmount is 0, assign a realistic value
        ua_str = ua
        if (lit == "Credit" or (ua and ua.strip() in ("", "0.0000000000"))):
            pl = placeholder_usage(pc, ut, sd, ed)
            if pl is not None:
                nr[I_USAGE_AMOUNT] = pl
                ua_str = pl

        # Compute cost
        rate, cost = compute_cost(pc, ut, ua_str)

        # Write cost columns
        nr[I_UNBLENDED_RATE] = f"{rate:.10f}" if rate else "0.0000000000"
        nr[I_UNBLENDED_COST] = f"{cost:.10f}"
        nr[I_BLENDED_RATE]   = f"{rate:.10f}" if rate else "0.0000000000"
        nr[I_BLENDED_COST]   = f"{cost:.10f}"
        nr[I_CURRENCY]       = "USD"

        svc_costs[pc] = svc_costs.get(pc, 0.0) + cost
        processed.append(nr)

    total = sum(svc_costs.values())
    # Fill missing service metadata for Tax rows from the original CSV
    for r in processed:
        if not r[I_SERVICE_NAME].strip() and r[I_PRODUCT_CODE]:
            fill_metadata(r, r[I_PRODUCT_CODE])

    print(f"\nBase costs ({len(processed)} rows):")
    for s, c in sorted(svc_costs.items(), key=lambda x: -x[1]):
        print(f"  {s:<20s} ${c:>8.2f}")
    print(f"  {'TOTAL':<20s} ${total:>8.2f}")

    # -- 4. Extend to ~30 days --------------------------------------------
    target_days = 33
    extra_cycles = max(1, (target_days - span_days + span_days - 1) // span_days)

    print(f"\nExtending {span_days}d -> ~{span_days * (extra_cycles + 1)}d ({extra_cycles} extra cycles)...")
    extended = list(processed)

    for cycle in range(1, extra_cycles + 1):
        shift = timedelta(days=span_days * cycle)
        for r in processed:
            nr = list(r)

            try:
                sd = parse_ts(nr[I_USAGE_START]) + shift
                ed = parse_ts(nr[I_USAGE_END])   + shift
            except Exception:
                continue

            nr[I_USAGE_START] = fmt_ts(sd)
            nr[I_USAGE_END]   = fmt_ts(ed)

            # Vary usage amount by +/- 25%
            ua = nr[I_USAGE_AMOUNT]
            if ua and ua.strip() not in ("", "0.0000000000"):
                try:
                    v = float(ua) * random.uniform(0.75, 1.25)
                    nr[I_USAGE_AMOUNT] = f"{v:.10f}"
                except (ValueError, TypeError):
                    pass

            # Recompute cost
            pc = nr[I_PRODUCT_CODE]
            ut = nr[I_USAGE_TYPE]
            rate, cost = compute_cost(pc, ut, nr[I_USAGE_AMOUNT])
            nr[I_UNBLENDED_RATE] = f"{rate:.10f}" if rate else "0.0000000000"
            nr[I_UNBLENDED_COST] = f"{cost:.10f}"
            nr[I_BLENDED_RATE]   = f"{rate:.10f}" if rate else "0.0000000000"
            nr[I_BLENDED_COST]   = f"{cost:.10f}"

            svc_costs[pc] = svc_costs.get(pc, 0.0) + cost
            extended.append(nr)

    total = sum(svc_costs.values())
    print(f"After extension ({len(extended)} rows): total ${total:.2f}")

    # -- 5. Baseline: Continuous t3.small EC2 instance ------------------
    # Simulate a small dev server running 24/7 for the entire dataset
    print("\nBaseline: t3.small dev server (24/7)...")
    base_start = all_dates[0]
    base_end   = max_dt + timedelta(days=span_days * extra_cycles)

    current = base_start
    ec2_base_hours = 0
    while current < base_end:
        for hour in range(24):
            ts = current + timedelta(hours=hour)
            if ts > base_end:
                break
            row = [""] * len(header)
            row[I_LINE_ITEM_TYPE] = "Usage"
            row[I_USAGE_START]    = fmt_ts(ts)
            row[I_USAGE_END]      = fmt_ts(ts + timedelta(hours=1))
            row[I_PRODUCT_CODE]   = "AmazonEC2"
            row[I_USAGE_TYPE]     = "BoxUsage:t3.small"
            row[I_OPERATION]      = "RunInstances"
            row[I_AZ]             = "us-east-1a"
            row[I_RESOURCE_ID]    = "i-0f9a8b7c6d5e4f3a2"
            row[I_USAGE_AMOUNT]   = "1.0"
            row[I_CURRENCY]       = "USD"
            fill_metadata(row, "AmazonEC2")
            rate = 0.0208
            cost = 0.0208
            row[I_UNBLENDED_RATE] = f"{rate:.10f}"
            row[I_UNBLENDED_COST] = f"{cost:.10f}"
            row[I_BLENDED_RATE]   = f"{rate:.10f}"
            row[I_BLENDED_COST]   = f"{cost:.10f}"
            svc_costs["AmazonEC2"] = svc_costs.get("AmazonEC2", 0.0) + cost
            ec2_base_hours += 1
            extended.append(row)
        current += timedelta(days=1)
    total = sum(svc_costs.values())
    print(f"  +{ec2_base_hours} hours, running total: ${total:.2f}")

    # -- 6. Anomaly A1: Extra EC2 t3.medium (3 days) ---------------------
    print("Anomaly A1: 2x t3.medium instances for 3 days...")
    mid_idx = len(all_dates) // 2
    anchor = all_dates[mid_idx] + timedelta(days=random.randint(0, 2))
    a1_start = anchor

    for day_off in range(3):
        for inst in range(2):
            for hour in range(24):
                ts = a1_start + timedelta(days=day_off, hours=hour)
                row = [""] * len(header)
                row[I_LINE_ITEM_TYPE] = "Usage"
                row[I_USAGE_START]    = fmt_ts(ts)
                row[I_USAGE_END]      = fmt_ts(ts + timedelta(hours=1))
                row[I_PRODUCT_CODE]   = "AmazonEC2"
                row[I_USAGE_TYPE]     = "BoxUsage:t3.medium"
                row[I_OPERATION]      = "RunInstances"
                row[I_AZ]             = random.choice(["us-east-1a", "us-east-1b"])
                rid = f"i-a1-{inst:04d}"
                row[I_RESOURCE_ID]    = rid
                row[I_USAGE_AMOUNT]   = "1.0"
                row[I_CURRENCY]       = "USD"
                fill_metadata(row, "AmazonEC2")
                rate = 0.0416
                cost = 0.0416
                row[I_UNBLENDED_RATE] = f"{rate:.10f}"
                row[I_UNBLENDED_COST] = f"{cost:.10f}"
                row[I_BLENDED_RATE]   = f"{rate:.10f}"
                row[I_BLENDED_COST]   = f"{cost:.10f}"
                svc_costs["AmazonEC2"] = svc_costs.get("AmazonEC2", 0.0) + cost
                extended.append(row)
    total = sum(svc_costs.values())
    print(f"  +144 rows, running total: ${total:.2f}")

    # -- 7. Anomaly A2: S3 data transfer spike (1 day) -------------------
    print("Anomaly A2: S3 data transfer spike...")
    a2_start = a1_start + timedelta(days=random.randint(4, 7))
    for hour in range(24):
        ts = a2_start + timedelta(hours=hour)
        row = [""] * len(header)
        row[I_LINE_ITEM_TYPE] = "Usage"
        row[I_USAGE_START]    = fmt_ts(ts)
        row[I_USAGE_END]      = fmt_ts(ts + timedelta(hours=1))
        row[I_PRODUCT_CODE]   = "AmazonS3"
        row[I_USAGE_TYPE]     = "DataTransfer-Out-Bytes"
        row[I_OPERATION]      = "GetObject"
        row[I_AZ]             = "-"
        row[I_RESOURCE_ID]    = "arn:aws:s3:::fyp-shared-assets"
        row[I_USAGE_AMOUNT]   = str(int(8e9 * random.uniform(0.8, 1.2)))
        row[I_CURRENCY]       = "USD"
        fill_metadata(row, "AmazonS3")
        rate, cost = compute_cost("AmazonS3", "DataTransfer-Out-Bytes", row[I_USAGE_AMOUNT])
        row[I_UNBLENDED_RATE] = f"{rate:.10f}"
        row[I_UNBLENDED_COST] = f"{cost:.10f}"
        row[I_BLENDED_RATE]   = f"{rate:.10f}"
        row[I_BLENDED_COST]   = f"{cost:.10f}"
        svc_costs["AmazonS3"] = svc_costs.get("AmazonS3", 0.0) + cost
        extended.append(row)
    total = sum(svc_costs.values())
    print(f"  +24 rows, running total: ${total:.2f}")

    # -- 8. Anomaly A3: RDS db.t3.micro appears --------------------------
    print("Anomaly A3: RDS db.t3.micro (mid-dataset)...")
    rds_start = all_dates[len(all_dates) // 3]
    rds_end   = all_dates[-1] + timedelta(days=span_days * extra_cycles)
    rds_rate  = 0.017

    current = rds_start
    while current < rds_end:
        for hour in range(24):
            ts = current + timedelta(hours=hour)
            if ts > rds_end:
                break
            row = [""] * len(header)
            row[I_LINE_ITEM_TYPE] = "Usage"
            row[I_USAGE_START]    = fmt_ts(ts)
            row[I_USAGE_END]      = fmt_ts(ts + timedelta(hours=1))
            row[I_PRODUCT_CODE]   = "AmazonRDS"
            row[I_USAGE_TYPE]     = "BoxUsage:db.t3.micro"
            row[I_OPERATION]      = "CreateDBInstance"
            row[I_AZ]             = random.choice(["us-east-1a", "us-east-1b"])
            row[I_RESOURCE_ID]    = "arn:aws:rds:us-east-1:430155298731:db/fyp-staging-db"
            row[I_USAGE_AMOUNT]   = "1.0"
            row[I_CURRENCY]       = "USD"
            fill_metadata(row, "AmazonRDS")
            row[I_UNBLENDED_RATE] = f"{rds_rate:.10f}"
            row[I_UNBLENDED_COST] = f"{rds_rate:.10f}"
            row[I_BLENDED_RATE]   = f"{rds_rate:.10f}"
            row[I_BLENDED_COST]   = f"{rds_rate:.10f}"
            svc_costs["AmazonRDS"] = svc_costs.get("AmazonRDS", 0.0) + rds_rate
            extended.append(row)
        current += timedelta(days=1)
    rds_hours = len([x for x in extended if x[I_PRODUCT_CODE] == "AmazonRDS"])
    total = sum(svc_costs.values())
    print(f"  +{rds_hours} RDS hours, running total: ${total:.2f}")

    # -- 9. Anomaly A4: Lambda burst (4 days) ----------------------------
    print("Anomaly A4: Lambda function invocations...")
    lambda_start = max_dt + timedelta(days=span_days * max(0, extra_cycles - 1))
    lambda_rate  = 1.66667e-5

    for day_off in range(4):
        for _ in range(random.randint(150, 400)):
            ts = lambda_start + timedelta(
                days=day_off,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            gb_sec = random.uniform(128, 3008) / 1024 * random.uniform(0.2, 8.0)
            row = [""] * len(header)
            row[I_LINE_ITEM_TYPE] = "Usage"
            row[I_USAGE_START]    = fmt_ts(ts)
            row[I_USAGE_END]      = fmt_ts(ts + timedelta(seconds=int(gb_sec * 1024 / 128)))
            row[I_PRODUCT_CODE]   = "AWSLambda"
            row[I_USAGE_TYPE]     = "Lambda-GB-Second"
            row[I_OPERATION]      = "Invoke"
            row[I_AZ]             = "-"
            func_id = random.randint(1, 3)
            row[I_RESOURCE_ID]    = f"arn:aws:lambda:us-east-1:430155298731:function:fyp-processor-{func_id}"
            row[I_USAGE_AMOUNT]   = f"{gb_sec:.10f}"
            row[I_CURRENCY]       = "USD"
            fill_metadata(row, "AWSLambda")
            cost = gb_sec * lambda_rate
            row[I_UNBLENDED_RATE] = f"{lambda_rate:.10f}"
            row[I_UNBLENDED_COST] = f"{cost:.10f}"
            row[I_BLENDED_RATE]   = f"{lambda_rate:.10f}"
            row[I_BLENDED_COST]   = f"{cost:.10f}"
            svc_costs["AWSLambda"] = svc_costs.get("AWSLambda", 0.0) + cost
            extended.append(row)
    lambda_rows = len([x for x in extended if x[I_PRODUCT_CODE] == "AWSLambda"])
    total = sum(svc_costs.values())
    print(f"  +{lambda_rows} Lambda rows, running total: ${total:.2f}")

    # -- 9. Cap at $70 ---------------------------------------------------
    total = sum(svc_costs.values())
    print(f"\nFinal total before cap: ${total:.2f}")
    if total > 70.0:
        scale = 65.0 / total
        print(f"  Scaling by {scale:.4f} to target $65")
        for r in extended:
            c = r[I_UNBLENDED_COST]
            if c and c.strip() not in ("", "0.0000000000"):
                try:
                    cv = float(c) * scale
                    r[I_UNBLENDED_COST] = f"{cv:.10f}"
                    r[I_BLENDED_COST]   = f"{cv:.10f}"
                except (ValueError, TypeError):
                    pass
        for s in svc_costs:
            svc_costs[s] *= scale
        total = sum(svc_costs.values())

    # -- 10. Write output ------------------------------------------------
    print(f"\nWriting {len(extended)} rows to {OUTPUT}...")
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(extended)

    # -- 11. Final summary ------------------------------------------------
    print(f"\n{'='*60}")
    print(f"  FINAL COST BREAKDOWN")
    print(f"{'='*60}")
    for s, c in sorted(svc_costs.items(), key=lambda x: -x[1]):
        pct = c / total * 100
        print(f"  {s:<22s} ${c:>7.2f}  ({pct:>5.1f}%)")
    print(f"  {'-'*40}")
    print(f"  {'TOTAL':<22s} ${total:>7.2f}  (100.0%)")
    print(f"  Rows: {len(extended)}")

    # Date range
    out_dates = []
    for r in extended:
        try:
            out_dates.append(parse_ts(r[I_USAGE_START]))
        except Exception:
            pass
    if out_dates:
        out_dates.sort()
        print(f"  Date range: {out_dates[0].date()} -> {out_dates[-1].date()} ({len(out_dates)} timestamps)")


if __name__ == "__main__":
    main()
