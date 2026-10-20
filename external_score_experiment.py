"""Paired upstream-score dependence experiment; see docs/EXTERNAL_SCORE_ADDENDUM.md."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,warnings
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score,r2_score,mean_absolute_error
from sklearn.linear_model import Ridge
from audit import FEATURES,Encoding,Predictor,exact_shapley,reason_list,SEED
from reference_experiment import neighborhood
R=Path(__file__).resolve().parents[1]
warnings.filterwarnings('ignore',message='.*sklearn.utils.parallel.delayed.*',category=UserWarning)

def run():
    out=R/'results/external_score';out.mkdir(parents=True,exist_ok=True)
    df=pd.read_csv(R/'data/heloc_dataset_v1.csv')
    split=json.loads((R/'results/reference/split.json').read_text())
    old=json.loads((R/'results/reference/audit_results.json').read_text())
    primary=[c for c in old['cases'] if c['model']=='without_score']
    prev=json.loads((R/'results/reference_sensitivity/experiment.json').read_text())
    y=(df.loc[split['test'],'RiskPerformance']=='Bad').astype(int).to_numpy()
    bgpos=np.random.default_rng(SEED).choice(len(split['train']),24,replace=False)
    models={};predicts={};rows=[];importance=[]
    for variant in ['without_score','with_score']:
        features=FEATURES+(['ExternalRiskEstimate'] if variant=='with_score' else [])
        train=df.loc[split['train'],features].to_numpy(float);test=df.loc[split['test'],features].to_numpy(float)
        enc=Encoding().fit(train)
        model=RandomForestClassifier(n_estimators=100,max_depth=7,min_samples_leaf=15,max_features=.8,random_state=SEED,n_jobs=2)
        model.fit(enc.transform(train),(df.loc[split['train'],'RiskPerformance']=='Bad').astype(int))
        predict=Predictor(model,enc);pred=predict(test);predicts[variant]=pred
        auc=float(roc_auc_score(y,pred));models[variant]={'features':features,'test_auc':auc,'test_cases':len(y)}
        # Raw input block moves with its special-state representation through Encoding.
        for j,feature in enumerate(features):
            drops=[]
            for seed in range(10):
                perm=test.copy();perm[:,j]=np.random.default_rng(20261016+seed).permutation(test[:,j]);drops.append(auc-float(roc_auc_score(y,predict(perm))))
            importance.append({'model':variant,'feature':feature,'auc_drop_mean':float(np.mean(drops)),'auc_drop_sd':float(np.std(drops,ddof=1)),'drops':drops})
        for i,c in enumerate(primary):
            x=df.loc[c['case_id'],features].to_numpy(float);score=float(predict(x[None,:])[0])
            phi,diagnostics=exact_shapley(x,train[bgpos],predict)
            if variant=='without_score':
                assert abs(score-c['score'])<1e-10
                np.testing.assert_allclose(phi,c['explanations']['Exact interventional Shapley'][0]['values'],atol=1e-10)
            fits=[]
            for seed in range(5):
                if variant=='without_score':
                    fit=dict(next(f for f in prev['fidelity'] if f['case_id']==c['case_id'] and f['seed']==seed))
                    fit['values']=c['explanations']['Custom LIME-style surrogate'][seed]['values'];fit['individual']=c['explanations']['Custom LIME-style surrogate'][seed]['individual']
                else:
                    z,reps,w=neighborhood(x,train,seed)
                    f=Ridge(alpha=1).fit(reps,predict(z),sample_weight=w)
                    z2,reps2,w2=neighborhood(x,train,seed+10000,include_anchor=False)
                    actual=predict(z2);estimated=f.predict(reps2)
                    fit={'case_id':c['case_id'],'seed':seed,'values':f.coef_.tolist(),'individual':reason_list(f.coef_,features),'fit_r2':float(f.score(reps,predict(z),sample_weight=w)),'heldout_r2':float(r2_score(actual,estimated,sample_weight=w2)),'heldout_mae':float(mean_absolute_error(actual,estimated,sample_weight=w2)),'point_error':abs(float(f.predict(np.ones((1,len(x))))[0])-score)}
                fits.append(fit)
            rows.append({'case_id':c['case_id'],'model':variant,'score':score,'research_outcome':'deny' if score>=.5 else 'accept','features':{f:float(v) for f,v in zip(features,x)},'shapley':{'values':phi.tolist(),'individual':reason_list(phi,features),'grouped':reason_list(phi,features,True),'diagnostics':diagnostics},'surrogate':fits})
            if (i+1)%10==0:print(variant,i+1,'/',len(primary),flush=True)
    pairs=[]
    for c in primary:
        a=next(r for r in rows if r['case_id']==c['case_id'] and r['model']=='without_score');b=next(r for r in rows if r['case_id']==c['case_id'] and r['model']=='with_score')
        v=b['shapley']['values'][-1]
        pairs.append({'case_id':c['case_id'],'score_without':a['score'],'score_with':b['score'],'score_change':b['score']-a['score'],'outcome_changed':a['research_outcome']!=b['research_outcome'],'external_score_value':b['features']['ExternalRiskEstimate'],'external_shapley':v,'external_in_top_adverse':any(r['id']=='ExternalRiskEstimate' for r in b['shapley']['individual']),'external_largest_absolute':int(np.argmax(np.abs(b['shapley']['values'])))==len(FEATURES)})
    rng=np.random.default_rng(20261016);diffs=[]
    for _ in range(1000):
        ix=rng.choice(len(y),len(y),replace=True)
        if len(np.unique(y[ix]))<2:continue
        diffs.append(roc_auc_score(y[ix],predicts['with_score'][ix])-roc_auc_score(y[ix],predicts['without_score'][ix]))
    summary={'paired_applications':len(pairs),'outcomes_changed':sum(r['outcome_changed'] for r in pairs),'external_in_top_adverse':sum(r['external_in_top_adverse'] for r in pairs),'external_largest_absolute':sum(r['external_largest_absolute'] for r in pairs),'external_positive':sum(r['external_shapley']>0 for r in pairs),'test_outcomes_disagree':int(np.sum((predicts['with_score']>=.5)!=(predicts['without_score']>=.5))),'test_applications':len(y),'test_auc_difference':models['with_score']['test_auc']-models['without_score']['test_auc'],'test_auc_difference_ci':list(map(float,np.quantile(diffs,[.025,.975]))),'median_absolute_external_contribution':float(np.median([abs(r['external_shapley']) for r in pairs]))}
    result={'generated_at':datetime.now(timezone.utc).isoformat(),'design':'Exploratory paired external-score extension; earlier overlapping results were known.','addendum_sha256':hashlib.sha256((R/'docs/EXTERNAL_SCORE_ADDENDUM.md').read_bytes()).hexdigest(),'data_sha256':hashlib.sha256((R/'data/heloc_dataset_v1.csv').read_bytes()).hexdigest(),'models':models,'summary':summary,'pairs':pairs,'records':rows,'permutation_importance':importance,'background_record_ids':[int(split['train'][i]) for i in bgpos],'upstream_evidence':{'score_values':'Available in the supplied dataset','score_calculation':'Not provided','upstream_model':'Not provided','upstream_reasons':'Not provided','inference_warning':'Correlated credit-history inputs do not authenticate the upstream calculation.'}}
    (out/'experiment.json').write_text(json.dumps(result,indent=2));pd.DataFrame(pairs).to_csv(out/'paired_results.csv',index=False)
    pd.DataFrame([{k:v for k,v in r.items() if k!='drops'} for r in importance]).to_csv(out/'permutation_importance.csv',index=False)
    print(json.dumps(summary,indent=2))
if __name__=='__main__':run()
