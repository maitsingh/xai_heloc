"""Frozen-model reference sensitivity and independent-neighborhood surrogate evaluation."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,itertools,json,warnings
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score,mean_absolute_error
if __package__:
    from .audit import FEATURES,Encoding,Predictor,exact_shapley,reason_list,compare,SEED
    from .notice_benchmark import cluster_interval
else:
    from audit import FEATURES,Encoding,Predictor,exact_shapley,reason_list,compare,SEED
    from notice_benchmark import cluster_interval
R=Path(__file__).resolve().parents[1]
warnings.filterwarnings('ignore',message='.*sklearn.utils.parallel.delayed.*',category=UserWarning)

def neighborhood(x,train,seed,n=1200,include_anchor=True):
    rng=np.random.default_rng(seed);d=len(x)
    z=np.column_stack([rng.choice(train[:,j],n) for j in range(d)])
    z=np.where(rng.random((n,d))<.55,x,z)
    if include_anchor:z[0]=x
    scale=np.maximum(np.nanstd(np.where(train<0,np.nan,train),axis=0),1)
    delta=(z-x)/scale;delta=np.where((z<0)|(x<0),np.where(z==x,0,1),delta)
    weights=np.exp(-np.mean(delta**2,axis=1)/(.75**2))
    q=np.array([np.quantile(train[:,j][train[:,j]>=0],[.25,.5,.75]) for j in range(d)])
    def bins(a):return np.column_stack([np.where(a[:,j]<0,a[:,j],np.searchsorted(q[j],a[:,j])) for j in range(d)])
    reps=(bins(z)==bins(np.asarray(x)[None,:])).astype(float)
    return z,reps,weights

def run():
    lock=json.loads((R/'results/protocol_v2_lock.json').read_text());assert hashlib.sha256((R/'docs/PROTOCOL_v2.md').read_bytes()).hexdigest()==lock['protocol_sha256']
    df=pd.read_csv(R/'data/heloc_dataset_v1.csv');split=json.loads((R/'results/reference/split.json').read_text())
    old=json.loads((R/'results/reference/audit_results.json').read_text());cases=[c for c in old['cases'] if c['model']=='without_score']
    train=df.loc[split['train'],FEATURES].to_numpy(float);y=(df.loc[split['train'],'RiskPerformance']=='Bad').astype(int)
    enc=Encoding().fit(train);model=RandomForestClassifier(n_estimators=100,max_depth=7,min_samples_leaf=15,max_features=.8,random_state=SEED,n_jobs=2)
    model.fit(enc.transform(train),y);predict=Predictor(model,enc)
    for c in cases:assert abs(predict(np.array(list(c['features'].values()))[None,:])[0]-c['score'])<1e-10
    scores=predict(train);near=train[(scores>=.45)&(scores<.50)];assert len(near)>=24
    refs={}
    for scope,pool in [('population',train),('near_cutoff',near)]:
        for seed in [101,202,303]:refs[(scope,seed)]=pool[np.random.default_rng(seed).choice(len(pool),24,replace=False)]
    out=R/'results/reference_sensitivity';out.mkdir(exist_ok=True)
    artifact=out/'rf8_model.joblib';joblib.dump({'model':model,'encoding':enc,'features':FEATURES,'split':split},artifact)
    manifests=[{'reference':scope,'seed':seed,'values':bg.tolist(),'sha256':hashlib.sha256(bg.tobytes()).hexdigest()} for (scope,seed),bg in refs.items()]
    records=[];comparisons=[];fidelity=[]
    for i,c in enumerate(cases):
        cid=c['case_id'];x=df.loc[cid,FEATURES].to_numpy(float);by={}
        for (scope,seed),bg in refs.items():
            v,diagnostics=exact_shapley(x,bg,predict);reason=reason_list(v,FEATURES)
            entry={'case_id':cid,'reference':scope,'seed':seed,'score':c['score'],'values':v.tolist(),'individual':reason,'grouped':reason_list(v,FEATURES,True),'diagnostics':diagnostics};records.append(entry);by[(scope,seed)]=entry
        for seed in [101,202,303]:
            comparisons.append({'case_id':cid,'test':'reference_definition','reference':'population_vs_near_cutoff','seed':seed,**compare(by[('population',seed)]['individual'],by[('near_cutoff',seed)]['individual'])})
        for scope in ['population','near_cutoff']:
            for a,b in itertools.combinations([101,202,303],2):comparisons.append({'case_id':cid,'test':'background_resampling','reference':scope,'seed':f'{a}:{b}',**compare(by[(scope,a)]['individual'],by[(scope,b)]['individual'])})
        for seed in range(5):
            z,reps,w=neighborhood(x,train,seed);f=Ridge(alpha=1).fit(reps,predict(z),sample_weight=w)
            z2,reps2,w2=neighborhood(x,train,seed+10000,include_anchor=False);actual=predict(z2);estimated=f.predict(reps2)
            # Exact agreement with earlier local-surrogate weights validates the reconstruction.
            np.testing.assert_allclose(f.coef_,c['explanations']['Custom LIME-style surrogate'][seed]['values'],rtol=1e-10,atol=1e-10)
            point_prediction=float(f.predict(np.ones((1,len(x))))[0])
            fidelity.append({'case_id':cid,'seed':seed,'fit_r2':float(f.score(reps,predict(z),sample_weight=w)),'heldout_r2':float(r2_score(actual,estimated,sample_weight=w2)),'heldout_mae':float(mean_absolute_error(actual,estimated,sample_weight=w2)),'point_error':abs(point_prediction-c['score'])})
        if (i+1)%10==0:print(f'Explained {i+1}/{len(cases)} records',flush=True)
    summary=[]
    for test,scope in [('reference_definition','population_vs_near_cutoff'),('background_resampling','population'),('background_resampling','near_cutoff')]:
        rows=[r for r in comparisons if r['test']==test and r['reference']==scope and r['retention'] is not None]
        metrics={}
        for field in ['turnover','retention','first_changed']:metrics[field]=cluster_interval([r['case_id'] for r in rows],[float(r[field]) for r in rows])
        summary.append({'test':test,'reference':scope,**metrics})
    result={'generated_at':datetime.now(timezone.utc).isoformat(),'protocol_sha256':lock['protocol_sha256'],'model_sha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),'method':'Exact empirical interventional Shapley; custom LIME-style surrogate','reference_pool_counts':{'population':len(train),'near_cutoff':len(near)},'model_test_auc':old['models'][0]['metrics']['test']['auc'],'summary':summary,'fidelity_summary':{k:{'median':float(np.median([r[k] for r in fidelity])),'min':float(min(r[k] for r in fidelity)),'max':float(max(r[k] for r in fidelity))} for k in ['fit_r2','heldout_r2','heldout_mae','point_error']},'records':records,'fidelity':fidelity,'comparisons':comparisons,'reference_manifests':manifests}
    (out/'experiment.json').write_text(json.dumps(result,indent=2));pd.DataFrame(comparisons).to_csv(out/'comparisons.csv',index=False);pd.DataFrame(fidelity).to_csv(out/'fidelity.csv',index=False)
    print(json.dumps({k:result[k] for k in ['reference_pool_counts','summary','fidelity_summary']},indent=2))

if __name__=='__main__':run()
