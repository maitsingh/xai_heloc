"""Exploratory external-score approximations; no original upstream ground truth."""
from pathlib import Path
from datetime import datetime,timezone
import json, hashlib, warnings
import numpy as np,pandas as pd,joblib
from sklearn.ensemble import HistGradientBoostingRegressor,RandomForestClassifier
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error,r2_score
from audit import FEATURES,Encoding,Predictor,SEED,exact_shapley,reason_list,compare
R=Path(__file__).resolve().parents[1]
warnings.filterwarnings('ignore',message='.*sklearn.utils.parallel.delayed.*')

class Combined:
    def __init__(self,approx,encoding,downstream,bounds):self.approx,self.encoding,self.downstream,self.bounds=approx,encoding,downstream,bounds
    def score(self,x):return np.clip(self.approx.predict(self.encoding.transform(x)),*self.bounds)
    def __call__(self,x):return self.downstream(np.column_stack([x,self.score(x)]))

def run():
    out=R/'results/score_reconstruction';out.mkdir(exist_ok=True)
    raw=pd.read_csv(R/'data/heloc_dataset_v1.csv');split=json.loads((R/'results/reference/split.json').read_text())
    previous=json.loads((R/'results/external_score/experiment.json').read_text())
    eligible={k:[i for i in split[k] if raw.loc[i,'ExternalRiskEstimate']>=0] for k in ['train','validation','test']}
    tr=raw.loc[eligible['train']];train=tr[FEATURES].to_numpy(float)
    enc=Encoding().fit(train);bounds=[float(tr.ExternalRiskEstimate.min()),float(tr.ExternalRiskEstimate.max())]
    alltrain=raw.loc[split['train'],FEATURES+['ExternalRiskEstimate']].to_numpy(float)
    downenc=Encoding().fit(alltrain)
    rf=RandomForestClassifier(n_estimators=100,max_depth=7,min_samples_leaf=15,max_features=.8,random_state=SEED,n_jobs=2)
    rf.fit(downenc.transform(alltrain),(raw.loc[split['train'],'RiskPerformance']=='Bad').astype(int))
    original=Predictor(rf,downenc)
    approximations={'additive':make_pipeline(StandardScaler(),Ridge(alpha=10)),
                    'nonlinear':HistGradientBoostingRegressor(max_iter=150,max_leaf_nodes=15,l2_regularization=5,random_state=SEED)}
    labels={'additive':'Additive score approximation','nonlinear':'Nonlinear score approximation'}
    combined={};metrics={};test=raw.loc[eligible['test']];x_test=test[FEATURES].to_numpy(float)
    true_prob=original(test[FEATURES+['ExternalRiskEstimate']].to_numpy(float));test_predictions={}
    for key,m in approximations.items():
        m.fit(enc.transform(train),tr.ExternalRiskEstimate)
        fn=Combined(m,enc,original,bounds);combined[key]=fn;sp=fn.score(x_test);pr=fn(x_test);test_predictions[key]=pr
        metrics[key]={'label':labels[key],'test_records':len(test),'external_score_mae':float(mean_absolute_error(test.ExternalRiskEstimate,sp)),
                      'external_score_r2':float(r2_score(test.ExternalRiskEstimate,sp)),
                      'probability_mae':float(np.mean(abs(pr-true_prob))),
                      'probability_error_quantiles':list(map(float,np.quantile(abs(pr-true_prob),[.5,.9,.95,.99]))),
                      'unclipped_out_of_training_range':int(np.sum((m.predict(enc.transform(x_test))<bounds[0])|(m.predict(enc.transform(x_test))>bounds[1])))}
        print(key,json.dumps(metrics[key]),flush=True)
    ref_positions=np.random.default_rng(SEED).choice(len(train),24,replace=False);background=train[ref_positions]
    original_background=raw.loc[[eligible['train'][i] for i in ref_positions],FEATURES+['ExternalRiskEstimate']].to_numpy(float)
    audit_ids=[r['case_id'] for r in previous['records'] if r['model']=='with_score' and r['features']['ExternalRiskEstimate']>=0]
    cases=[]
    for idx,cid in enumerate(audit_ids):
        x=raw.loc[cid,FEATURES].to_numpy(float);orig=next(r for r in previous['records'] if r['model']=='with_score' and r['case_id']==cid)
        actual=float(original(raw.loc[cid,FEATURES+['ExternalRiskEstimate']].to_numpy(float)[None,:])[0])
        assert abs(actual-orig['score'])<1e-10
        original_values,original_diagnostics=exact_shapley(raw.loc[cid,FEATURES+['ExternalRiskEstimate']].to_numpy(float),original_background,original)
        original_explanation={'values':original_values.tolist(),'diagnostics':original_diagnostics,'individual':reason_list(original_values,FEATURES+['ExternalRiskEstimate']),'grouped':reason_list(original_values,FEATURES+['ExternalRiskEstimate'],True)}
        item={'case_id':cid,'inputs':dict(zip(FEATURES,map(float,x))),'observed_external_score':float(raw.loc[cid,'ExternalRiskEstimate']),
              'original_probability':actual,'original_shapley':original_explanation,'approximations':{}}
        for key,fn in combined.items():
            v,d=exact_shapley(x,background,fn);p=float(fn(x[None,:])[0])
            item['approximations'][key]={'estimated_external_score':float(fn.score(x[None,:])[0]),'probability':p,'probability_error':abs(p-actual),
                                         'values':list(map(float,v)),'diagnostics':d,'individual':reason_list(v,FEATURES),'grouped':reason_list(v,FEATURES,True)}
        a,b=[item['approximations'][k] for k in ['additive','nonlinear']]
        ca=compare(a['individual'],b['individual']);cg=compare(a['grouped'],b['grouped'])
        item['comparison']={'probability_difference':abs(a['probability']-b['probability']),
                            'maximum_original_probability_error':max(a['probability_error'],b['probability_error']),
                            'individual':ca,'grouped':cg,'same_order':[r['id'] for r in a['individual']]==[r['id'] for r in b['individual']]}
        cases.append(item)
        if (idx+1)%10==0:print('Explained',idx+1,'/',len(audit_ids),flush=True)
    bands=[]
    for t in [.005,.01,.02,.05]:
        close=[c for c in cases if c['comparison']['probability_difference']<=t]
        both=[c for c in close if c['comparison']['maximum_original_probability_error']<=t]
        bands.append({'probability_band':t,'approximate_outputs_close':len(close),
                      'both_close_to_original':len(both),
                      'different_factor_sets_when_outputs_close':sum(bool(c['comparison']['individual']['turnover']) for c in close),
                      'different_factor_sets_when_both_close_to_original':sum(bool(c['comparison']['individual']['turnover']) for c in both),
                      'different_concept_sets_when_both_close_to_original':sum(bool(c['comparison']['grouped']['turnover']) for c in both)})
    ranked=sorted(cases,key=lambda c:(not bool(c['comparison']['individual']['turnover']),c['comparison']['maximum_original_probability_error'],c['case_id']))
    # Pick smallest maximum original-prediction error among changed factor sets; disclose selection.
    featured=8193 if any(c['case_id']==8193 for c in cases) else ranked[0]['case_id']
    payload={'generated_at':datetime.now(timezone.utc).isoformat(),'design':'Exploratory; same-test feasibility metrics were already known.',
             'protocol_sha256':hashlib.sha256((R/'docs/EXTERNAL_SCORE_RECONSTRUCTION.md').read_bytes()).hexdigest(),
             'features':FEATURES,'counts':{k:len(v) for k,v in eligible.items()},'score_clipping_bounds':bounds,'metrics':metrics,'cases':cases,'bands':bands,
             'summary':{'audit_records':len(cases),'different_factor_sets':sum(bool(c['comparison']['individual']['turnover']) for c in cases),
                        'different_concept_sets':sum(bool(c['comparison']['grouped']['turnover']) for c in cases),
                        'test_probability_difference_mean':float(np.mean(abs(test_predictions['additive']-test_predictions['nonlinear'])))},
             'featured_case':featured,'featured_selection':'Record 8193 selected after inspection to illustrate detailed-factor changes with close original-prediction agreement and unchanged broader topics. See all forty records; the example is not representative.',
             'background_record_ids':[eligible['train'][i] for i in ref_positions],
             'limitations':['Original external-score mechanism is unavailable.','Both explanations describe reconstructed systems, not authenticated original upstream factors.','References and feature dependence affect attributions.','Earlier test results and feasibility results were known; evaluation is exploratory.','Forty audited records are deliberately selected, not representative of lender decisions.']}
    (out/'experiment.json').write_text(json.dumps(payload,indent=2))
    joblib.dump({'approximations':approximations,'encoding':enc,'original_model':rf,'original_encoding':downenc,'score_clipping_bounds':bounds,'features':FEATURES},out/'models.joblib')
    testrows=pd.DataFrame({'case_id':eligible['test'],'observed_external_score':test.ExternalRiskEstimate.to_numpy(),'original_probability':true_prob,
                          'additive_probability':test_predictions['additive'],'nonlinear_probability':test_predictions['nonlinear']})
    testrows.to_csv(out/'test_predictions.csv',index=False)
    print(json.dumps({'summary':payload['summary'],'bands':bands,'featured_case':featured},indent=2))
if __name__=='__main__':run()
