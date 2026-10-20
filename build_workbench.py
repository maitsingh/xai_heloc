"""Build the measured external-score investigation and offline preview."""
from pathlib import Path
import json,re
from audit import LABELS,GROUPS
R=Path(__file__).resolve().parents[1]
external=json.loads((R/'results/external_score/experiment.json').read_text())
study=json.loads((R/'results/score_reconstruction/experiment.json').read_text())
labels={**LABELS,'MSinceOldestTradeOpen':'Oldest account age','AverageMInFile':'Average account age','NumSatisfactoryTrades':'Accounts with on-time payments','PercentTradesNeverDelq':'Accounts never delinquent','MSinceMostRecentDelq':'Time since most recent delinquency','NumInqLast6M':'Recent credit inquiries','NetFractionRevolvingBurden':'Revolving balance / credit limit','NetFractionInstallBurden':'Installment balance / original amount','ExternalRiskEstimate':'Externally supplied score'}
local={str(c['case_id']):[{k:r[k] for k in ['seed','heldout_r2','heldout_mae','point_error']} for r in c['surrogate']] for c in external['records'] if c['model']=='with_score'}
data={'study':study,'labels':labels,'groups':GROUPS,'local':local,'external_summary':external['summary']}
js='const PROJECT='+json.dumps(data,separators=(',',':'))+';'
(R/'site/data.js').write_text(js)
html=(R/'src/workbench.html').read_text().replace('<!-- LEGAL_APPENDIX -->',(R/'src/requirements-appendix.html').read_text()).replace('<!-- EVIDENCE_APPENDIX -->',(R/'src/evidence-appendix.html').read_text());(R/'site/index.html').write_text(html)
preview=html.replace('<script src="data.js"></script>','<script>'+js+'</script>').replace('<script src="app.js"></script>','<script>'+(R/'site/app.js').read_text()+'</script>')
(R.parent/'heloc_workbench_preview.html').write_text(preview)
# The inline rendering uses the same application and measured data, root-scoped.
css=re.search(r'<style>(.*?)</style>',preview,re.S).group(1)
body=re.search(r'<body>(.*?)</body>',preview,re.S).group(1)
css=css.replace('body{','#score-investigation-render{').replace('header{','#score-investigation-render header{').replace('main{','#score-investigation-render main{').replace('footer{','#score-investigation-render footer{')
css="@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,400;9..144,500&family=IBM+Plex+Mono:wght@400;500&display=swap');\n"+css
fragment='<style>'+css+'</style><div id="score-investigation-render">'+body+'</div>'
fragment=fragment.replace("window.scrollTo({top:0,behavior:'instant'});",'').replace('</script><script>','\n')
if Path('/workspace').is_dir():
    Path('/workspace/credit-score-investigation.html').write_text(fragment)
assert len(fragment.encode())<1024*1024
print('Built site, offline preview and inline render:',len(fragment.encode()),'bytes')
