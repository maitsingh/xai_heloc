"""Descriptive extension: changes hidden when detailed factors become broad categories.
Computed from existing fixed-model reference experiments; not a new preregistered test.
"""
from pathlib import Path
import json
from audit import compare
from notice_benchmark import cluster_interval
R=Path(__file__).resolve().parents[1]

def run():
    ref=json.loads((R/'results/reference_sensitivity/experiment.json').read_text())
    rows=[]
    for cid in sorted({r['case_id'] for r in ref['records']}):
        for seed in [101,202,303]:
            a=next(r for r in ref['records'] if r['case_id']==cid and r['reference']=='population' and r['seed']==seed)
            b=next(r for r in ref['records'] if r['case_id']==cid and r['reference']=='near_cutoff' and r['seed']==seed)
            detailed=compare(a['individual'],b['individual']);grouped=compare(a['grouped'],b['grouped'])
            rows.append({'case_id':cid,'seed':seed,'detailed':detailed,'grouped':grouped,
                         'hidden_change':bool(detailed['turnover'] and grouped['turnover'] is False)})
    valid=[r for r in rows if not r['detailed']['empty'] and not r['grouped']['empty']]
    summary={field:cluster_interval([r['case_id'] for r in valid],[float(r[field]['turnover']) for r in valid]) for field in ['detailed','grouped']}
    summary['hidden_change']=cluster_interval([r['case_id'] for r in valid],[float(r['hidden_change']) for r in valid])
    result={'design':'Exploratory descriptive summary of existing fixed-model reference results. Grouping is a research mapping, not a lender-approved taxonomy.',
            'applications':len({r['case_id'] for r in valid}),'paired_comparisons':len(valid),'excluded_empty_comparisons':len(rows)-len(valid),
            'hidden_change_comparisons':sum(r['hidden_change'] for r in valid),
            'applications_with_hidden_change':len({r['case_id'] for r in valid if r['hidden_change']}),
            'summary':summary,'records':rows}
    (R/'results/reference_sensitivity/grouping_analysis.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':run()
