"""Generate controlled notice cases, with truth kept separate from review inputs."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,itertools
from datetime import datetime,timezone
import numpy as np
import pandas as pd
if __package__:
    from .audit import LABELS, SEED
    from .evidence_review import review
else:
    from audit import LABELS, SEED
    from evidence_review import review
R=Path(__file__).resolve().parents[1]

def cluster_interval(records,values):
    per=pd.DataFrame({'case':records,'v':values}).groupby('case').v.mean().to_numpy()
    rng=np.random.default_rng(SEED)
    boot=rng.choice(per,(1000,len(per)),replace=True).mean(axis=1)
    return {'rate':float(per.mean()),'ci':list(map(float,np.quantile(boot,[.025,.975]))),'records':len(per),'scenarios':len(values)}

def run():
    data=json.loads((R/'results/reference/audit_results.json').read_text())
    cases=[c for c in data['cases'] if c['model']=='without_score']
    rng=np.random.default_rng(20261016);ids=rng.permutation(sorted(c['case_id'] for c in cases))
    split={str(int(i)):'development' if j<20 else 'evaluation' for j,i in enumerate(ids)}
    out=R/'results/notice_audit';out.mkdir(exist_ok=True)
    (out/'partition.json').write_text(json.dumps(split,indent=2))
    catalog={f:{'source_features':[f],'approved_wording':[LABELS[f], 'Recorded '+LABELS[f].lower()]} for f in LABELS}
    catalog['POLICY_ELIGIBILITY']={'source_features':['research_eligibility_flag'],'approved_wording':['Application does not meet the research eligibility rule']}
    scenarios=[];truth=[];outputs=[]
    for c in cases:
        cid=c['case_id'];part=split[str(cid)];features=list(c['features']);shap=c['explanations']['Exact interventional Shapley'][0]
        atoms=shap['individual'];assert atoms
        artifacts={'model':'rf8-seed2026','preprocessing':'special-status-v1','explainer':'exact-interventional-v1','reference':'training-24-seed2026','mapping':'feature-reasons-v1'}
        dec={'id':f'HELOC-{cid}-research','case_id':cid,'basis':'model','outcome':'research_reject','score':c['score'],'cutoff':.5,'artifacts':artifacts,'required_reasons':[], 'attribution':dict(zip(features,shap['values'])),'rule_trace':['Research eligibility gate: pass','Risk model evaluated',f'Bad-class score {c["score"]:.6f} >= research cutoff 0.50']}
        reasons=[{'code':r['id'],'text':LABELS[r['id']],'source_features':[r['id']]} for r in atoms]
        clean={'decision':dec,'catalog':catalog,'notice':{'decision_id':dec['id'],'artifacts':deepcopy(artifacts),'reasons':reasons}}
        entries=[]
        entries.append(('correct','correct','Correct model-driven notice',deepcopy(clean)))
        p=deepcopy(clean)
        for r in p['notice']['reasons']:r['text']='Recorded '+r['text'].lower()
        entries.append(('paraphrase','correct','Catalog-approved wording variation',p))
        p=deepcopy(clean);p['decision']['artifacts']['mapping']='feature-reasons-v0';p['notice']['artifacts']['mapping']='feature-reasons-v0';p['newest_available_mapping']='feature-reasons-v1'
        entries.append(('historical','correct','Historical notice with matching historical mapping',p))
        gate=deepcopy(clean);gate['decision'].update(basis='eligibility_gate',required_reasons=['POLICY_ELIGIBILITY'],rule_trace=['Constructed research eligibility flag: fail','Decision stopped at eligibility gate','Risk score retained for diagnostics only; not used in this decision'])
        gate['notice']['reasons']=[{'code':'POLICY_ELIGIBILITY','text':catalog['POLICY_ELIGIBILITY']['approved_wording'][0],'source_features':['research_eligibility_flag']}]
        entries.append(('policy_correct','correct','Notice identifies the terminating research policy rule',deepcopy(gate)))
        wrong=deepcopy(clean)
        # Different replacement concepts in development/evaluation; preserve otherwise identical evidence.
        wrong['notice']['reasons'][0]['code']='NumInqLast6M' if atoms[0]['id']!='NumInqLast6M' else 'AverageMInFile'
        if part=='evaluation':wrong['notice']['reasons'][0]['code']='NetFractionInstallBurden' if atoms[0]['id']!='NetFractionInstallBurden' else 'MSinceMostRecentDelq'
        wrong['notice']['reasons'][0]['text']=LABELS[wrong['notice']['reasons'][0]['code']]
        entries.append(('wrong_mapping','mapping','A reason cites evidence for a different concept',wrong))
        wrong=deepcopy(clean);wrong['notice']['reasons'][0]['text']=('Excessively high ' if part=='development' else 'Unacceptably low ')+LABELS[atoms[0]['id']].lower()
        entries.append(('unsupported_wording','mapping','Directional wording lacks supporting catalog evidence',wrong))
        wrong=deepcopy(gate);wrong['notice']['reasons']=deepcopy(reasons)
        entries.append(('omitted_policy','coverage','Notice substitutes diagnostic score reasons for the terminating rule',wrong))
        wrong=deepcopy(clean);wrong['notice']['artifacts']['model' if part=='development' else 'reference']='different-retained-artifact'
        entries.append(('stale','provenance','Explanation artifact differs from the decision-time artifact',wrong))
        wrong=deepcopy(clean);wrong['decision']=None
        entries.append(('missing','insufficient','Decision trace withheld: correctness cannot be established',wrong))
        runs=c['explanations']['Custom LIME-style surrogate'];sets=[{r['id'] for r in e['individual']} for e in runs]
        instability=float(np.mean([a!=b for a,b in itertools.combinations(sets,2)]))
        for kind,label,description,bundle in entries:
            sid=f'{cid}-{kind}';scenarios.append({'id':sid,'case_id':cid,'bundle':bundle,'seed_turnover':instability})
            truth.append({'id':sid,'partition':part,'family':label,'scenario':kind,'description':description})
            # Review function sees only the supplied bundle, never label/partition/scenario metadata.
            finding=review(bundle)
            outputs.append({'id':sid,'case_id':cid,'partition':part,'family':label,'scenario':kind,'stability_flag':instability>.20,'stability_turnover':instability,'evidence_flag':finding['disposition']=='Investigate',**finding})
    evals=[x for x in outputs if x['partition']=='evaluation'];summary=[]
    for method,field in [('Repeatability screen','stability_flag'),('Structured evidence review','evidence_flag')]:
        for family in ['mapping','coverage','provenance','all_defects','correct']:
            selected=[x for x in evals if (x['family'] in ['mapping','coverage','provenance'] if family=='all_defects' else x['family']==family)]
            summary.append({'method':method,'family':family,**cluster_interval([x['case_id'] for x in selected],[x[field] for x in selected]),'flagged':sum(x[field] for x in selected)})
    missing=[x for x in evals if x['family']=='insufficient']
    sweep=[]
    for threshold in np.arange(0,1.001,.05):
        sweep.append({'threshold':round(float(threshold),2),'defect_detection':float(np.mean([x['stability_turnover']>threshold for x in evals if x['family'] in ['mapping','coverage','provenance']])),'false_alarm':float(np.mean([x['stability_turnover']>threshold for x in evals if x['family']=='correct']))})
    lock=json.loads((R/'results/protocol_v2_lock.json').read_text());actual=hashlib.sha256((R/'docs/PROTOCOL_v2.md').read_bytes()).hexdigest();assert actual==lock['protocol_sha256']
    result={'title':'From Risk Scores to Reasons','generated_at':datetime.now(timezone.utc).isoformat(),'protocol_sha256':actual,'scope':'Controlled contract-consistency benchmark; all policies, notices and defects are constructed.','counts':{'development_records':20,'evaluation_records':20,'total_scenarios':len(outputs),'evaluation_scenarios':len(evals),'evaluation_defects':80,'evaluation_correct':80,'evaluation_missing_evidence':20},'summary':summary,'missing_evidence':{'cases':len(missing),'correct_abstentions':sum(x['disposition']=='Insufficient evidence' for x in missing)},'threshold_sweep':sweep,'findings':outputs}
    for name,obj in [('inputs.json',scenarios),('truth.json',truth),('evaluation.json',result)]: (out/name).write_text(json.dumps(obj,indent=2))
    print(json.dumps({'counts':result['counts'],'summary':summary,'missing':result['missing_evidence']},indent=2))

if __name__=='__main__':run()
