"""
Generate an enhanced synthetic AWS CUR dataset with realistic cost patterns.
Covers 365 days, 7 regions, 5 accounts, 11 services, multiple instance types,
and all pricing terms. Includes injected anomalies for detection.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

# ── Configuration ──────────────────────────────────────────────────────────

START_DATE = datetime(2025, 6, 1)
END_DATE = datetime(2026, 5, 31)
N_DAYS = (END_DATE - START_DATE).days + 1  # 365

ACCOUNTS = [
    "111111111111", "222222222222", "333333333333",
    "444444444444", "555555555555",
]

SERVICES = {
    "AmazonEC2": {
        "family": "Compute Instance",
        "ops": ["RunInstances", "StartInstances", "StopInstances"],
        "usage_types": ["EU2-BoxUsage:t3.micro", "EU2-BoxUsage:t3.small",
                        "EU2-BoxUsage:t3.medium", "EU2-BoxUsage:t3.large",
                        "EU2-BoxUsage:m5.large", "EU2-BoxUsage:m5.xlarge",
                        "EU2-BoxUsage:c5.xlarge", "EU2-BoxUsage:r5.large"],
    },
    "AmazonS3": {
        "family": "Storage",
        "ops": ["PutObject", "GetObject", "ListBucket", "DeleteObject",
                "CopyObject", "HeadBucket"],
        "usage_types": ["TimedStorage-ByteHrs", "Requests-Tier1",
                        "Requests-Tier2", "DataTransfer-Out-Bytes"],
    },
    "AWSLambda": {
        "family": "API Request",
        "ops": ["Invoke", "GetFunction", "UpdateFunctionCode"],
        "usage_types": ["Lambda-GB-Second", "Lambda-Request"],
    },
    "AmazonRDS": {
        "family": "Compute Instance",
        "ops": ["CreateDBInstance", "ModifyDBInstance", "CreateDBSnapshot"],
        "usage_types": ["InstanceUsage:db.t3.micro", "InstanceUsage:db.t3.small",
                        "InstanceUsage:db.t3.medium"],
    },
    "AWSGlue": {
        "family": "AWS Glue",
        "ops": ["RunJob", "GetJob", "StartJobRun"],
        "usage_types": ["GlueCrawler-Hour", "GlueETL-Hour"],
    },
    "AmazonVPC": {
        "family": "Data Transfer",
        "ops": ["CreateVpc", "CreateSubnet", "CreateRouteTable"],
        "usage_types": ["VpcEndpoint-Hours", "VPN-Connection-Hours",
                        "NatGateway-Hours"],
    },
    "AWSSecretsManager": {
        "family": "API Request",
        "ops": ["GetSecretValue", "PutSecretValue", "CreateSecret"],
        "usage_types": ["SecretsManager-API-Tier1", "SecretsManager-Secrets"],
    },
    "AWSDataTransfer": {
        "family": "Data Transfer",
        "ops": ["PublicIP-Out", "PublicIP-In"],
        "usage_types": ["DataTransfer-Out-Bytes", "DataTransfer-In-Bytes"],
    },
    "AWSQueueService": {
        "family": "API Request",
        "ops": ["SendMessage", "ReceiveMessage", "DeleteMessage"],
        "usage_types": ["SQS-Request", "SQS-Queue-Hours"],
    },
    "AmazonSNS": {
        "family": "API Request",
        "ops": ["Publish", "Subscribe", "CreateTopic"],
        "usage_types": ["SNS-Request", "SNS-Delivery"],
    },
    "awskms": {
        "family": "API Request",
        "ops": ["Encrypt", "Decrypt", "GenerateDataKey"],
        "usage_types": ["KMS-Request", "KMS-Storage"],
    },
}

INSTANCE_TYPES = [
    "t3.micro", "t3.small", "t3.medium", "t3.large",
    "m5.large", "m5.xlarge",
    "c5.xlarge",
    "r5.large",
]

# Hourly base rates ($/hr) for each instance type
INSTANCE_RATES = {
    "t3.micro": 0.0104, "t3.small": 0.0208, "t3.medium": 0.0416,
    "t3.large": 0.0832, "m5.large": 0.096, "m5.xlarge": 0.192,
    "c5.xlarge": 0.170, "r5.large": 0.126,
}

REGIONS = ["us-east-1", "us-west-2", "eu-west-1", "eu-central-1",
           "ap-southeast-1", "ap-northeast-1", "eu-north-1"]

# Regional price multipliers (us-east-1 = 1.0 baseline)
REGION_MULTIPLIER = {
    "us-east-1": 1.0, "us-west-2": 1.08, "eu-west-1": 1.12,
    "eu-central-1": 1.16, "ap-southeast-1": 1.20,
    "ap-northeast-1": 1.25, "eu-north-1": 1.10,
}

PRICING_TERMS = ["OnDemand", "Reserved", "Spot", "SavingsPlan"]
PRICING_DISCOUNT = {"OnDemand": 1.0, "Reserved": 0.6,
                    "Spot": 0.3, "SavingsPlan": 0.8}
PRICING_WEIGHTS = {"OnDemand": 0.55, "Reserved": 0.20,
                   "Spot": 0.15, "SavingsPlan": 0.10}

LINE_ITEM_TYPES = ["Usage", "Credit", "Tax", "SavingsPlanCoveredUsage"]
LINE_ITEM_WEIGHTS = [0.90, 0.03, 0.02, 0.05]

# ── Anomaly definitions ─────────────────────────────────────────────────────

ANOMALIES = [
    # (service, description, date, magnitude_multiplier, duration_days)
    ("AmazonEC2", "Spike: EC2 spike mid-July", "2025-07-15", 8.0, 3),
    ("AmazonRDS", "Spike: RDS cost surge Sep", "2025-09-10", 6.0, 2),
    ("AWSLambda", "Gradual ramp-up Oct-Nov", "2025-10-01", 3.0, 45),
    ("AmazonS3", "Spike: S3 data transfer spike Dec", "2025-12-20", 10.0, 4),
    ("AmazonEC2", "Drop: EC2 costs drop sharply Feb", "2026-02-01", 0.1, 7),
    ("AmazonRDS", "Spike: RDS spike mid-Mar", "2026-03-15", 5.0, 3),
    ("AWSGlue", "Spike: Glue job spike Apr", "2026-04-05", 7.0, 2),
]


def generate_cur_rows() -> pd.DataFrame:
    rows = []

    for day_offset in range(N_DAYS):
        current_date = START_DATE + timedelta(days=day_offset)
        # Weekly pattern: higher on weekdays, lower on weekends
        weekday = current_date.weekday()
        weekly_factor = 1.3 if weekday < 5 else 0.7

        # Monthly pattern: month-end processing spike
        is_month_end = current_date.day >= 28
        monthly_factor = 1.4 if is_month_end else 1.0

        # Growth trend: ~15% over the year
        growth_trend = 1.0 + 0.15 * (day_offset / N_DAYS)

        # Random daily noise
        noise = np.random.lognormal(0, 0.15)

        daily_base_factor = weekly_factor * monthly_factor * growth_trend * noise

        for account in ACCOUNTS:
            # Each account gets 5-8 services
            account_services = random.sample(
                list(SERVICES.keys()),
                random.randint(5, len(SERVICES))
            )

            for service_name in account_services:
                svc = SERVICES[service_name]
                n_hours = random.randint(1, 24) if service_name in (
                    "AmazonEC2", "AmazonRDS") else random.randint(1, 8)
                region = random.choice(REGIONS)
                region_mult = REGION_MULTIPLIER[region]
                pricing_term = random.choices(PRICING_TERMS,
                                              weights=[PRICING_WEIGHTS[t] for t in PRICING_TERMS], k=1)[0]
                pricing_discount = PRICING_DISCOUNT[pricing_term]
                line_item_type = random.choices(LINE_ITEM_TYPES,
                                                weights=LINE_ITEM_WEIGHTS, k=1)[0]

                # Determine instance type for EC2/RDS
                instance_type = ""
                if service_name == "AmazonEC2":
                    instance_type = random.choice(INSTANCE_TYPES)
                elif service_name == "AmazonRDS":
                    instance_type = random.choice(
                        ["db.t3.micro", "db.t3.small", "db.t3.medium"]
                    )

                for hour in range(n_hours):
                    ts = current_date + timedelta(hours=hour)
                    op = random.choice(svc["ops"])
                    usage_type = random.choice(svc["usage_types"])

                    # Base cost calculation
                    if service_name == "AmazonEC2" and instance_type in INSTANCE_RATES:
                        base_hourly = INSTANCE_RATES[instance_type]
                        base_cost = base_hourly * daily_base_factor * region_mult * pricing_discount
                    elif service_name == "AmazonRDS":
                        base_cost = 0.05 * daily_base_factor * region_mult * pricing_discount
                    elif service_name == "AWSLambda":
                        base_cost = 0.00002 * daily_base_factor * region_mult * pricing_discount * random.uniform(1, 50)
                    elif service_name == "AmazonS3":
                        base_cost = 0.0001 * daily_base_factor * region_mult * pricing_discount * random.uniform(1, 20)
                    elif service_name == "AWSGlue":
                        base_cost = 0.44 * daily_base_factor * region_mult * pricing_discount * random.uniform(0.5, 3)
                    elif service_name == "AWSDataTransfer":
                        base_cost = 0.09 * daily_base_factor * region_mult * pricing_discount * random.uniform(0.1, 5)
                    else:
                        base_cost = 0.001 * daily_base_factor * region_mult * pricing_discount * random.uniform(0.5, 10)

                    # Add small random jitter
                    cost = max(0, np.random.normal(base_cost, base_cost * 0.1))

                    # Usage amount proportional to cost
                    usage_amount = cost * random.uniform(100, 10000) if cost > 0 else 0

                    # ── Inject anomalies ──
                    for anom_svc, _, anom_date_str, mult, duration in ANOMALIES:
                        if anom_svc != service_name:
                            continue
                        anom_start = pd.to_datetime(anom_date_str)
                        anom_end = anom_start + timedelta(days=duration)
                        if anom_start <= ts <= anom_end:
                            cost = cost * mult
                            if mult < 1.0:
                                cost = max(0.0001, cost)
                            break

                    # For negative costs (credits/refunds)
                    if line_item_type == "Credit" and cost > 0:
                        cost = -cost * random.uniform(0.5, 1.0)

                    # Resource IDs
                    if service_name == "AmazonS3":
                        resource_id = f"arn:aws:s3:::fincloud-data-{random.randint(1, 50)}"
                    elif service_name in ("AmazonEC2", "AmazonRDS"):
                        resource_id = f"i-{random.randint(0, 0xffffffffffffffff):016x}"
                    elif service_name == "AWSLambda":
                        resource_id = f"arn:aws:lambda:{region}:{account}:function:fincloud-func-{random.randint(1, 30)}"
                    else:
                        resource_id = f"arn:aws:{service_name.lower()}:{region}:{account}:resource/{random.randint(1, 100)}"

                    row = {
                        "identity/LineItemId": f"li-{random.randint(10**15, 10**16-1)}",
                        "identity/TimeInterval": f"{ts.isoformat()}/{(ts + timedelta(hours=1)).isoformat()}",
                        "bill/BillingEntity": "AWS",
                        "bill/BillType": "Anniversary",
                        "bill/PayerAccountId": "111111111111",
                        "bill/BillingPeriodStartDate": ts.replace(day=1).isoformat(),
                        "bill/BillingPeriodEndDate": (ts.replace(day=1) + timedelta(days=32)).replace(day=1).isoformat() if ts.month == 12 else ts.replace(month=ts.month+1, day=1).isoformat(),
                        "lineItem/UsageAccountId": account,
                        "lineItem/LineItemType": line_item_type,
                        "lineItem/UsageStartDate": ts.isoformat(),
                        "lineItem/UsageEndDate": (ts + timedelta(hours=1)).isoformat(),
                        "lineItem/ProductCode": service_name,
                        "lineItem/UsageType": usage_type,
                        "lineItem/Operation": op,
                        "lineItem/AvailabilityZone": f"{region}{random.choice(['a', 'b', 'c'])}",
                        "lineItem/ResourceId": resource_id,
                        "lineItem/UsageAmount": round(usage_amount, 6),
                        "lineItem/NormalizationFactor": "1.0",
                        "lineItem/NormalizedUsageAmount": round(usage_amount, 6),
                        "lineItem/CurrencyCode": "USD",
                        "lineItem/UnblendedRate": round(base_cost / max(usage_amount, 0.001), 10) if usage_amount > 0 else 0,
                        "lineItem/UnblendedCost": round(cost, 12),
                        "lineItem/BlendedRate": round(base_cost / max(usage_amount, 0.001), 10) if usage_amount > 0 else 0,
                        "lineItem/BlendedCost": round(cost, 12),
                        "lineItem/LineItemDescription": f"{service_name} usage in {region}",
                        "lineItem/TaxType": "",
                        "lineItem/LegalEntity": "Amazon Web Services",
                        "product/ProductName": service_name,
                        "product/availability": "",
                        "product/availabilityZone": "",
                        "product/capacitystatus": "",
                        "product/classicnetworkingsupport": "",
                        "product/clockSpeed": "",
                        "product/currentGeneration": "",
                        "product/dedicatedEbsThroughput": "",
                        "product/dedicatedEbsThroughputDescription": "",
                        "product/durability": "",
                        "product/ecu": "",
                        "product/enhancedNetworkingSupported": "",
                        "product/feeCode": "",
                        "product/feeDescription": "",
                        "product/fromLocation": "",
                        "product/fromLocationType": "",
                        "product/fromRegionCode": "",
                        "product/gpuMemory": "",
                        "product/group": "",
                        "product/groupDescription": "",
                        "product/instance": instance_type,
                        "product/instanceFamily": instance_type.split(".")[0] if instance_type else "",
                        "product/instanceFamilyCategory": "",
                        "product/instanceType": instance_type,
                        "product/instanceTypeFamily": instance_type.split(".")[0] if instance_type else "",
                        "product/intelAvx2Available": "",
                        "product/intelAvxAvailable": "",
                        "product/intelTurboAvailable": "",
                        "product/licenseModel": "",
                        "product/location": region,
                        "product/locationType": "AWS Region",
                        "product/marketoption": "",
                        "product/maxIopsvolume": "",
                        "product/maxThroughputvolume": "",
                        "product/maxVolumeSize": "",
                        "product/memory": "",
                        "product/messageDeliveryFrequency": "",
                        "product/messageDeliveryOrder": "",
                        "product/networkPerformance": "",
                        "product/normalizationSizeFactor": "",
                        "product/operatingSystem": "",
                        "product/operation": "",
                        "product/physicalProcessor": "",
                        "product/preInstalledSw": "",
                        "product/processorArchitecture": "",
                        "product/processorFeatures": "",
                        "product/productFamily": svc["family"],
                        "product/queueType": "",
                        "product/region": region,
                        "product/regionCode": region.replace("-", ""),
                        "product/servicecode": service_name.lower(),
                        "product/servicename": service_name,
                        "product/sku": f"{service_name}-{random.randint(1000,9999)}",
                        "product/storage": "",
                        "product/storageClass": "",
                        "product/storageMedia": "",
                        "product/tenancy": "",
                        "product/toLocation": "",
                        "product/toLocationType": "",
                        "product/toRegionCode": "",
                        "product/transferType": "",
                        "product/usagetype": usage_type,
                        "product/vcpu": "",
                        "product/volumeApiName": "",
                        "product/volumeType": "",
                        "product/vpcnetworkingsupport": "",
                        "pricing/RateCode": f"{service_name}.{random.randint(100000,999999)}",
                        "pricing/RateId": str(random.randint(10**14, 10**15-1)),
                        "pricing/currency": "USD",
                        "pricing/publicOnDemandCost": round(cost, 12) if pricing_term == "OnDemand" else 0,
                        "pricing/publicOnDemandRate": round(base_cost / max(usage_amount, 0.001), 10) if usage_amount > 0 else 0,
                        "pricing/term": pricing_term,
                        "pricing/unit": "Hrs" if "Instance" in svc["family"] else "Requests",
                        "reservation/AmortizedUpfrontCostForUsage": "",
                        "reservation/AmortizedUpfrontFeeForBillingPeriod": "",
                        "reservation/EffectiveCost": "",
                        "reservation/EndTime": "",
                        "reservation/ModificationStatus": "",
                        "reservation/NormalizedUnitsPerReservation": "",
                        "reservation/NumberOfReservations": "",
                        "reservation/RecurringFeeForUsage": "",
                        "reservation/StartTime": "",
                        "reservation/SubscriptionId": "",
                        "reservation/TotalReservedNormalizedUnits": "",
                        "reservation/TotalReservedUnits": "",
                        "reservation/UnitsPerReservation": "",
                        "reservation/UnusedAmortizedUpfrontFeeForBillingPeriod": "",
                        "reservation/UnusedNormalizedUnitQuantity": "",
                        "reservation/UnusedQuantity": "",
                        "reservation/UnusedRecurringFee": "",
                        "reservation/UpfrontValue": "",
                        "savingsPlan/TotalCommitmentToDate": "",
                        "savingsPlan/SavingsPlanARN": "",
                        "savingsPlan/SavingsPlanRate": "",
                        "savingsPlan/UsedCommitment": "",
                        "savingsPlan/SavingsPlanEffectiveCost": "",
                        "savingsPlan/AmortizedUpfrontCommitmentForBillingPeriod": "",
                        "savingsPlan/RecurringCommitmentForBillingPeriod": "",
                    }
                    rows.append(row)

    df = pd.DataFrame(rows)
    return df


def main():
    import os
    print("Generating enhanced synthetic CUR dataset...")
    print(f"  Date range: {START_DATE.date()} to {END_DATE.date()} ({N_DAYS} days)")
    print(f"  Accounts: {len(ACCOUNTS)}")
    print(f"  Services: {len(SERVICES)}")
    print(f"  Regions: {len(REGIONS)}")
    print(f"  Instance types: {len(INSTANCE_TYPES)}")
    print(f"  Anomalies: {len(ANOMALIES)}")

    df = generate_cur_rows()
    print(f"\nGenerated {len(df)} rows, {len(df.columns)} columns")
    print(f"Total cost: ${df['lineItem/UnblendedCost'].sum():.2f}")

    # Save
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "Fincloud-cur-enhanced-v2.csv"
    )
    df.to_csv(output_path, index=False)
    print(f"\nSaved to: {output_path}")

    # Print summary stats
    costs = df['lineItem/UnblendedCost']
    print(f"\n=== Summary ===")
    print(f"Total cost: ${costs.sum():.2f}")
    print(f"Mean cost: ${costs.mean():.6f}")
    print(f"Median: ${costs.median():.6f}")
    print(f"Max: ${costs.max():.2f}")
    print(f"Min: ${costs.min():.6f}")
    print(f"Positive rows: {(costs > 0).sum()}")
    print(f"Zero rows: {(costs == 0).sum()}")
    print(f"Negative rows: {(costs < 0).sum()}")

    print(f"\n=== Service breakdown ===")
    for svc in df['lineItem/ProductCode'].unique():
        mask = df['lineItem/ProductCode'] == svc
        c = costs[mask]
        print(f"  {svc:25s}  rows={len(c):6d}  total=${c.sum():>8.2f}  mean=${c.mean():>7.4f}")

    print(f"\n=== Instance types ===")
    val = df['product/instanceType'].value_counts()
    for k, v in val.items():
        if k:
            print(f"  {k:20s}  {v}")

    print(f"\n=== Pricing terms ===")
    print(df['pricing/term'].value_counts().to_string())

    print(f"\n=== Regions ===")
    print(df['product/region'].value_counts().to_string())

    print(f"\n=== Line item types ===")
    print(df['lineItem/LineItemType'].value_counts().to_string())

    print(f"\n=== Unique Resource IDs: {df['lineItem/ResourceId'].nunique()} ===")

    dates = pd.to_datetime(df['lineItem/UsageStartDate'], errors='coerce')
    print(f"\nDate range: {dates.min()} to {dates.max()}")
    print(f"Unique timestamps: {dates.nunique()}")


if __name__ == '__main__':
    main()
