import csv
with open('Fincloud-cur-enhanced.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    credit_rows = []
    for row in reader:
        li_type = row.get('lineItem/LineItemType', '')
        if li_type == 'Credit':
            uc = row.get('lineItem/UnblendedCost', '')
            bc = row.get('lineItem/BlendedCost', '')
            svc = row.get('product/servicename', '')
            region = row.get('product/region', '')
            usage_start = row.get('lineItem/UsageStartDate', '')
            prod_code = row.get('lineItem/ProductCode', '')
            credit_rows.append({
                'uc': uc,
                'bc': bc,
                'svc': svc,
                'region': region,
                'start': usage_start,
                'prod': prod_code
            })
    
    print('Credit rows (showing unique combinations):')
    seen = set()
    for r in credit_rows:
        key = (r['uc'], r['bc'], r['svc'], r['region'])
        if key not in seen:
            seen.add(key)
            print(f'  Unblended={r[\"uc\"]}, Blended={r[\"bc\"]}, Svc={r[\"svc\"]}, Region=[{r[\"region\"]}], Prod={r[\"prod\"]}')
    
    print()
    # Sum credits by unblended and blended
    total_uc = sum(float(r['uc']) if r['uc'] else 0.0 for r in credit_rows)
    total_bc = sum(float(r['bc']) if r['bc'] else 0.0 for r in credit_rows)
    print(f'Total credit rows: {len(credit_rows)}')
    print(f'Total credit unblended: {total_uc:.4f}')
    print(f'Total credit blended: {total_bc:.4f}')
