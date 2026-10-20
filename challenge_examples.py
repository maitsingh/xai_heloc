from pathlib import Path
from copy import deepcopy
import json
from evidence_review import review
R=Path(__file__).resolve().parents[1]
inputs=json.loads((R/'results/notice_audit/inputs.json').read_text())
truth={x['id']:x for x in json.loads((R/'results/notice_audit/truth.json').read_text())}
rows=[]
for s in inputs:
    t=truth[s['id']]
    if t['partition']!='evaluation' or t['scenario']!='correct':continue
    b=deepcopy(s['bundle']);b['notice']['reasons'][0]['text']='Credit-file factor considered: '+b['notice']['reasons'][0]['text'].lower()
    rows.append({'case_id':s['case_id'],'challenge':'accurate_unlisted_paraphrase','stipulated_truth':'correct','bundle':b,'review':review(b)})
    b=deepcopy(s['bundle']);r=b['notice']['reasons'][0];r['text']='Income insufficient for the requested amount';b['catalog'][r['code']]['approved_wording']=[r['text']]
    rows.append({'case_id':s['case_id'],'challenge':'corrupted_trusted_catalog','stipulated_truth':'wrong','bundle':b,'review':review(b)})
summary=[]
for kind in ['accurate_unlisted_paraphrase','corrupted_trusted_catalog']:
    subset=[r for r in rows if r['challenge']==kind]
    summary.append({'challenge':kind,'cases':len(subset),'flagged':sum(r['review']['disposition']=='Investigate' for r in subset),'interpretation':'False-alarm challenge: valid wording falls outside catalog.' if kind.startswith('accurate') else 'Missed-defect challenge: source catalog and notice share the error.'})
(R/'results/notice_audit/challenges.json').write_text(json.dumps({'status':'Post-primary illustrative challenge set; no checker changes','summary':summary,'cases':rows},indent=2))
print(json.dumps(summary,indent=2))
