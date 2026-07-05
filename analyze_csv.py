import csv
with open('Fincloud-cur-enhanced.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    row_count = 0
    neg_cost_rows = 0
    neg_cost_sum = 0.0
    zero_cost_rows = 0
    missing_cost_rows = 0
    type_stats = {}
    svc_stats = {}
    region_stats = {}
    prod_code_stats = {}
    for row in reader:
        row_count += 1
        li_type = row.get('lineItem/LineItemType', 'UNKNOWN')
        svc = row.get('product/servicename', 'UNKNOWN')
        region = row.get('product/region', 'UNKNOWN')
        prod_code = row.get('lineItem/ProductCode', 'UNKNOWN')
        uc_str = row.get('lineItem/UnblendedCost', '')
        uc = 0.0
        if uc_str == '' or uc_str is None:
            missing_cost_rows += 1
        else:
            try:
                uc = float(uc_str)
                if uc < 0:
                    neg_cost_rows += 1
                    neg_cost_sum += uc
                elif uc == 0:
                    zero_cost_rows += 1
            except ValueError:
                missing_cost_rows += 1
        if li_type not in type_stats:
            type_stats[li_type] = {'count': 0, 'sum': 0.0}
        type_stats[li_type]['count'] += 1
        type_stats[li_type]['sum'] += uc
        if svc not in svc_stats:
            svc_stats[svc] = {'count': 0, 'sum': 0.0}
        svc_stats[svc]['count'] += 1
        svc_stats[svc]['sum'] += uc
        if region not in region_stats:
            region_stats[region] = {'count': 0, 'sum': 0.0}
        region_stats[region]['count'] += 1
        region_stats[region]['sum'] += uc
        if prod_code not in prod_code_stats:
            prod_code_stats[prod_code] = {'count': 0, 'sum': 0.0}
        prod_code_stats[prod_code]['count'] += 1
        prod_code_stats[prod_code]['sum'] += uc
    print('Total rows:', row_count)
    print('Negative cost rows:', neg_cost_rows, 'sum:', round(neg_cost_sum, 4))
    print('Zero cost rows:', zero_cost_rows)
    print('Missing/empty cost rows:', missing_cost_rows)
    print()
    print('By lineItem/LineItemType:')
    for t, s in sorted(type_stats.items(), key=lambda x: -x[1]['sum']):
        print(' ', t, 'rows=' + str(s['count']), 'sum=' + str(round(s['sum'], 4)))
    print()
    print('By product/servicename (top 15):')
    for s, st in sorted(svc_stats.items(), key=lambda x: -x[1]['sum'])[:15]:
        print(' ', s, 'rows=' + str(st['count']), 'sum=' + str(round(st['sum'], 4)))
    print()
    print('By product/region (top 10):')
    for r, st in sorted(region_stats.items(), key=lambda x: -x[1]['sum'])[:10]:
        print(' ', r, 'rows=' + str(st['count']), 'sum=' + str(round(st['sum'], 4)))
    print()
    print('By lineItem/ProductCode:')
    for p, st in sorted(prod_code_stats.items(), key=lambda x: -x[1]['sum']):
        print(' ', p, 'rows=' + str(st['count']), 'sum=' + str(round(st['sum'], 4)))
