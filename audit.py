"""Evidence-linked explanation audit. Official library mode or disclosed reference pilot.
Raw CSV is never redistributed. Counterfactual or notice legality is not inferred.
"""
from pathlib import Path
import argparse, hashlib, itertools, json, math, platform, time
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import Ridge
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.model_selection import train_test_split
from sklearn.calibration import calibration_curve

FEATURES=['MSinceOldestTradeOpen','AverageMInFile','NumSatisfactoryTrades','PercentTradesNeverDelq',
          'MSinceMostRecentDelq','NumInqLast6M','NetFractionRevolvingBurden','NetFractionInstallBurden']
GROUPS={'MSinceOldestTradeOpen':'Credit history','AverageMInFile':'Credit history',
        'NumSatisfactoryTrades':'Repayment history','PercentTradesNeverDelq':'Repayment history',
        'MSinceMostRecentDelq':'Repayment history','NumInqLast6M':'Recent inquiries',
        'NetFractionRevolvingBurden':'Revolving balances','NetFractionInstallBurden':'Installment balances',
        'ExternalRiskEstimate':'External risk score'}
LABELS={'MSinceOldestTradeOpen':'Oldest account age','AverageMInFile':'Average account age',
        'NumSatisfactoryTrades':'Satisfactory accounts','PercentTradesNeverDelq':'Never-delinquent share',
        'MSinceMostRecentDelq':'Time since delinquency','NumInqLast6M':'Recent inquiries',
        'NetFractionRevolvingBurden':'Revolving balance ratio','NetFractionInstallBurden':'Installment balance ratio',
        'ExternalRiskEstimate':'External risk estimate'}
SEED=2026

class Encoding:
    """Numeric value and separate -7/-8/-9 indicators. No ordinal interpretation of sentinels."""
    def fit(self, a):
        self.medians=np.array([np.median(c[c>=0]) for c in np.asarray(a).T]);return self
    def transform(self,a):
        a=np.asarray(a,dtype=float)
        numeric=np.where(a<0,self.medians,a)
        return np.column_stack([numeric,a==-7,a==-8,a==-9]).astype(float)

class Predictor:
    def __init__(self,model,enc):self.model,self.enc=model,enc
    def __call__(self,a):return self.model.predict_proba(self.enc.transform(a))[:,1]
    def probabilities(self,a):
        p=self(a);return np.column_stack([1-p,p])


def exact_shapley(x,background,predict):
    """Exact empirical interventional Shapley; coalition replacement may break dependence.
    Each term uses the identical fixed empirical background. No TreeSHAP approximation.
    """
    d=len(x);m=len(background);n=1<<d
    masks=((np.arange(n)[:,None]>>np.arange(d))&1).astype(bool)
    rows=np.where(masks[:,None,:],np.asarray(x)[None,None,:],background[None,:,:])
    values=predict(rows.reshape(-1,d)).reshape(n,m).mean(axis=1)
    phi=np.zeros(d)
    for j in range(d):
        for s in range(n):
            if not (s>>j)&1:
                k=s.bit_count();weight=1/(d*math.comb(d-1,k))
                phi[j]+=weight*(values[s|(1<<j)]-values[s])
    return phi,{'base':float(values[0]),'residual':float(values[-1]-values[0]-phi.sum())}


def local_surrogate(x,train,predict,seed,n=1200):
    """LIME-style pilot: empirical marginal perturbations and mismatch kernel.
    Not the LIME package; coefficients measure local sensitivity, not point attribution.
    """
    rng=np.random.default_rng(seed);d=len(x)
    z=np.column_stack([rng.choice(train[:,j],n) for j in range(d)])
    same=rng.random((n,d))<.55;z=np.where(same,x,z);z[0]=x
    scale=np.std(np.where(train<0,np.nan,train),axis=0) # replaced below with nan-aware
    scale=np.nanstd(np.where(train<0,np.nan,train),axis=0);scale=np.maximum(scale,1)
    delta=(z-x)/scale
    # Special states are categorical differences, not numerical distances.
    delta=np.where((z<0)|(x<0),np.where(z==x,0,1),delta)
    weights=np.exp(-np.mean(delta**2,axis=1)/(.75**2))
    # Interpretable representation: membership in the same empirical quartile/status as x.
    q=np.array([np.quantile(train[:,j][train[:,j]>=0],[.25,.5,.75]) for j in range(d)])
    def bins(a):
        return np.column_stack([np.where(a[:,j]<0,a[:,j],np.searchsorted(q[j],a[:,j])) for j in range(d)])
    reps=(bins(z)==bins(np.asarray(x)[None,:])).astype(float)
    y=predict(z);fit=Ridge(alpha=1).fit(reps,y,sample_weight=weights)
    return fit.coef_,{'local_fit_r2':float(fit.score(reps,y,sample_weight=weights)),
                     'local_prediction':float(fit.predict(np.ones((1,d)))[0])}


def reason_list(phi,features,grouped=False,k=4):
    # Signed sums before ranking prevent cherry-picking positive members within a group.
    scores={}
    for f,v in zip(features,phi):
        key=GROUPS[f] if grouped else f;scores[key]=scores.get(key,0)+float(v)
    return [{'id':f,'label':f if grouped else LABELS[f],'weight':v}
            for f,v in sorted(scores.items(),key=lambda x:(-x[1],x[0])) if v>1e-10][:k]


def compare(a,b):
    A=[x['id'] for x in a];B=[x['id'] for x in b];sa,sb=set(A),set(B)
    if not sa or not sb:return {'retention':None,'jaccard':None,'turnover':None,'first_changed':None,'empty':True}
    return {'retention':len(sa&sb)/len(sa),'jaccard':len(sa&sb)/len(sa|sb),
            'turnover':sa!=sb,'first_changed':A[0]!=B[0],'empty':False}


def summarize(comparisons):
    out=[];df=pd.DataFrame(comparisons)
    for key,g in df.groupby(['model','method','test','mapping'],sort=True):
        # First aggregate all comparisons within applicants, then across applicants.
        valid=g[g.retention.notna()].copy()
        if not len(valid):continue
        per=valid.groupby('case_id')[['retention','jaccard','turnover','first_changed']].mean()
        rng=np.random.default_rng(SEED);a=per.turnover.to_numpy(dtype=float)
        boots=np.mean(rng.choice(a,(1000,len(a)),replace=True),axis=1)
        out.append(dict(zip(['model','method','test','mapping'],key),applicants=len(per),
                        comparisons=len(valid),empty_comparisons=int(g.retention.isna().sum()),
                        retention=float(per.retention.mean()),jaccard=float(per.jaccard.mean()),
                        turnover=float(a.mean()),first_changed=float(per.first_changed.mean()),
                        turnover_ci=list(map(float,np.quantile(boots,[.025,.975])))))
    return out


def run(path,out,ncases=40,repeats=5,official=False):
    start=time.time();out.mkdir(parents=True,exist_ok=True)
    raw=pd.read_csv(path);Xraw=raw.drop(columns='RiskPerformance')
    assert set(raw.RiskPerformance)=={'Good','Bad'}
    quarantine=Xraw.eq(-9).all(axis=1)
    df=raw.loc[~quarantine].copy()
    # Predictor-identical records stay together even if labels differ.
    groups=pd.util.hash_pandas_object(df.drop(columns='RiskPerformance'),index=False)
    unique=groups.drop_duplicates().to_numpy()
    train_groups,temp=train_test_split(unique,test_size=.4,random_state=SEED)
    val_groups,test_groups=train_test_split(temp,test_size=.5,random_state=SEED)
    splits={name:df.index[groups.isin(g)].to_numpy() for name,g in [('train',train_groups),('validation',val_groups),('test',test_groups)]}
    assert not set(train_groups)&set(test_groups)
    report={'rows':len(raw),'quarantined_no_bureau':int(quarantine.sum()),'exact_duplicate_rows':int(raw.duplicated().sum()),
            'remaining_rows':len(df),'remaining_predictor_duplicates':int(df.drop(columns='RiskPerformance').duplicated().sum()),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'features_original':len(Xraw.columns),
            'split_rows':{k:len(v) for k,v in splits.items()},'label_counts':raw.RiskPerformance.value_counts().to_dict(),
            'codes':{c:{str(k):int(v) for k,v in Xraw[c][Xraw[c]<0].value_counts().items()} for c in Xraw}}
    cases=[];comparisons=[];models=[];attempts=[];baseline={}
    for variant in ['without_score','with_score']:
        feats=FEATURES+(['ExternalRiskEstimate'] if variant=='with_score' else [])
        frames={k:df.loc[v,feats].to_numpy(dtype=float) for k,v in splits.items()}
        labels={k:(df.loc[v,'RiskPerformance']=='Bad').astype(int).to_numpy() for k,v in splits.items()}
        enc=Encoding().fit(frames['train'])
        model=RandomForestClassifier(n_estimators=100,max_depth=7,min_samples_leaf=15,max_features=.8,random_state=SEED,n_jobs=2)
        model.fit(enc.transform(frames['train']),labels['train']);predict=Predictor(model,enc)
        metric={}
        for k in ['validation','test']:
            p=predict(frames[k]);frac,mean=calibration_curve(labels[k],p,n_bins=8)
            metric[k]={'auc':float(roc_auc_score(labels[k],p)),'average_precision':float(average_precision_score(labels[k],p)),
                       'brier':float(brier_score_loss(labels[k],p)),'calibration':{'observed':frac.tolist(),'predicted':mean.tolist()}}
        rng=np.random.default_rng(SEED);bg=frames['train'][rng.choice(len(frames['train']),24,replace=False)]
        scores=predict(frames['test']);eligible=np.flatnonzero(scores>=.5)
        ordered=eligible[np.argsort(scores[eligible])]
        if variant=='without_score':
            n=min(ncases//2,len(ordered)//2)
            positions=np.r_[ordered[:n],ordered[-n:]];ids=splits['test'][positions];primary_ids=set(map(int,ids))
        else:
            positions=np.array([j for j,i in enumerate(splits['test']) if int(i) in primary_ids and scores[j]>=.5])
        models.append({'id':variant,'features':feats,'metrics':metric,'audit_cases':len(positions),'model':'RandomForestClassifier',
                       'settings':{'n_estimators':100,'max_depth':7,'min_samples_leaf':15,'max_features':.8},
                       'background_rows':24})
        if official:
            import shap
            from lime.lime_tabular import LimeTabularExplainer
            # KernelSHAP on RAW feature blocks through the encoder: signed feature sum includes status effects.
            sh=shap.KernelExplainer(predict,bg)
            def explain_shap(x):
                np.random.seed(SEED)
                v=np.asarray(sh.shap_values(x,nsamples=1024,l1_reg=0))
                return v,{'base':float(sh.expected_value),'residual':float(predict(x[None,:])[0]-sh.expected_value-v.sum())}
            def explain_lime(x,seed):
                le=LimeTabularExplainer(frames['train'],feature_names=feats,class_names=['Good','Bad'],
                                       mode='classification',random_state=seed,discretize_continuous=True)
                ex=le.explain_instance(x,predict.probabilities,labels=(1,),num_features=len(feats),num_samples=2000)
                v=np.zeros(len(feats))
                for j,w in ex.local_exp[1]:v[j]=w
                return v,{'local_fit_r2':float(ex.score),'local_prediction':float(ex.local_pred[0]),
                          'condition_weights':[[str(label),float(weight)] for label,weight in ex.as_list(label=1)]}
            methods=['KernelSHAP','LIME']
        else:
            explain_shap=lambda x:exact_shapley(x,bg,predict)
            explain_lime=lambda x,seed:local_surrogate(x,frames['train'],predict,seed)
            methods=['Exact interventional Shapley','Custom LIME-style surrogate']
        for ii,pos in enumerate(positions):
            idx=int(splits['test'][pos]);x=frames['test'][pos];p=float(scores[pos]);stratum='near' if p<.6 else 'far'
            rec={'case_id':idx,'model':variant,'score':p,'stratum':stratum,'features':{f:float(v) for f,v in zip(feats,x)},'explanations':{},'perturbations':[]}
            for method in methods:
                runs=[]
                for seed in range(repeats if 'surrogate' in method or method=='LIME' else 1):
                    phi,meta=explain_lime(x,seed) if ('surrogate' in method or method=='LIME') else explain_shap(x)
                    entry={'seed':seed,'values':phi.tolist(),'individual':reason_list(phi,feats),
                           'grouped':reason_list(phi,feats,True),'diagnostics':meta}
                    runs.append(entry)
                rec['explanations'][method]=runs
                for a,b in itertools.combinations(runs,2):
                    for mapping in ['individual','grouped']:
                        comparisons.append({'case_id':idx,'model':variant,'method':method,'test':'repeatability','mapping':mapping,**compare(a[mapping],b[mapping])})
            # Fixed-model measurement sensitivity only; not actionable recourse or longitudinal transitions.
            for f in ['NetFractionRevolvingBurden','NetFractionInstallBurden']:
                j=feats.index(f)
                for delta in [-1,1]:
                    attempt={'case_id':idx,'model':variant,'feature':f,'delta':delta}
                    if x[j]<0:attempts.append(dict(attempt,status='special state frozen'));continue
                    z=x.copy();z[j]+=delta
                    if z[j]<0 or z[j]>np.max(frames['train'][:,j]):attempts.append(dict(attempt,status='outside observed training range'));continue
                    pp=float(predict(z[None,:])[0])
                    if pp<.5:attempts.append(dict(attempt,status='decision changed',score_after=pp));continue
                    if abs(pp-p)>.02:attempts.append(dict(attempt,status='score tolerance exceeded',score_after=pp));continue
                    attempts.append(dict(attempt,status='accepted',score_after=pp))
                    perturb={'feature':f,'delta':delta,'before':float(x[j]),'after':float(z[j]),'score_after':pp,'explanations':{}}
                    for method in methods:
                        phi,meta=explain_lime(z,0) if ('surrogate' in method or method=='LIME') else explain_shap(z)
                        ent={'values':phi.tolist(),'individual':reason_list(phi,feats),'grouped':reason_list(phi,feats,True),'diagnostics':meta}
                        perturb['explanations'][method]=ent
                        original=rec['explanations'][method][0]
                        for mapping in ['individual','grouped']:
                            comparisons.append({'case_id':idx,'model':variant,'method':method,'test':'measurement sensitivity','mapping':mapping,**compare(original[mapping],ent[mapping])})
                    rec['perturbations'].append(perturb)
            for mapping in ['individual','grouped']:
                comparisons.append({'case_id':idx,'model':variant,'method':'Between methods','test':'disagreement','mapping':mapping,
                                    **compare(rec['explanations'][methods[0]][0][mapping],rec['explanations'][methods[1]][0][mapping])})
            cases.append(rec)
            print(variant,ii+1,'/',len(positions),'case',idx,flush=True)
    summary=summarize(comparisons)
    result={'status':'official-library experiment' if official else 'REFERENCE PILOT: exact Shapley + custom LIME-style implementation',
            'date':'2026-10-14','data':report,'models':models,'cases':cases,'summary':summary,'attempts':attempts,
            'config':{'seed':SEED,'threshold':.5,'score_tolerance':.02,'repeats':repeats,'n_requested':ncases,'official':official},
            'limitations':['No legally validated notices. Group labels are illustrative audit categories, not sufficient principal reasons.',
                          'Grouped sums can mask opposite effects and lose specificity; compare raw and mapped evidence.',
                          'Coalition replacements and local perturbations may violate feature dependence.',
                          'Ratio +/-1 tests measurement sensitivity, not plausible borrower action; clinical/financial realism not established.',
                          'No protected-attribute or North Carolina representativeness claims.',
                          'With/without score models are separately trained; common-case comparison does not isolate a causal score effect.',
                          'Official FICO dictionary and redistribution terms remain unverified.'],
            'runtime_seconds':time.time()-start}
    (out/'audit_results.json').write_text(json.dumps(result,indent=2))
    pd.DataFrame(comparisons).to_csv(out/'comparisons.csv',index=False)
    pd.DataFrame(attempts).to_csv(out/'perturbation_log.csv',index=False)
    (out/'split.json').write_text(json.dumps({k:list(map(int,v)) for k,v in splits.items()},indent=2))
    (out/'run_manifest.json').write_text(json.dumps({'python':platform.python_version(),'dataset_sha256':report['sha256'],
                        'seed':SEED,'mode':result['status'],'elapsed_seconds':result['runtime_seconds']},indent=2))
    print('Complete',round(time.time()-start,1),'seconds',flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,default=Path('results'))
    p.add_argument('--cases',type=int,default=40);p.add_argument('--repeats',type=int,default=5);p.add_argument('--official',action='store_true')
    a=p.parse_args();run(a.data,a.out,a.cases,a.repeats,a.official)
