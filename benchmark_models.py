"""Compare predeclared models on the existing split; select by validation AUC."""
from pathlib import Path
import json, sys
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, brier_score_loss
from audit import Encoding

R=Path(__file__).resolve().parents[1]
df=pd.read_csv(R/'data/heloc_dataset_v1.csv')
split=json.loads((R/'results/reference/split.json').read_text())
rows=[]
for scope in ['all_23','all_22_without_external_score']:
    features=[c for c in df if c!='RiskPerformance' and not (scope.endswith('without_external_score') and c=='ExternalRiskEstimate')]
    enc=Encoding().fit(df.loc[split['train'],features].to_numpy())
    X={s:enc.transform(df.loc[ids,features].to_numpy()) for s,ids in split.items()}
    y={s:(df.loc[ids,'RiskPerformance']=='Bad').astype(int) for s,ids in split.items()}
    candidates={
        'Logistic regression':make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,C=1)),
        'Random Forest':RandomForestClassifier(n_estimators=300,max_depth=8,min_samples_leaf=15,max_features=.8,random_state=2026,n_jobs=2),
        'Histogram gradient boosting':HistGradientBoostingClassifier(max_iter=150,max_leaf_nodes=15,min_samples_leaf=30,l2_regularization=10,random_state=2026),
    }
    for name,model in candidates.items():
        model.fit(X['train'],y['train'])
        p=model.predict_proba(X['validation'])[:,1]
        rows.append({'scope':scope,'model':name,'features':len(features),'validation_auc':float(roc_auc_score(y['validation'],p)),'validation_brier':float(brier_score_loss(y['validation'],p)),'estimator':model,'X':X,'y':y})
        print(scope,name,rows[-1]['validation_auc'],flush=True)
# Evaluate only the validation-selected candidate, leaving other test results uninspected.
best=max(rows,key=lambda r:r['validation_auc'])
p=best['estimator'].predict_proba(best['X']['test'])[:,1]
selected={k:v for k,v in best.items() if k not in ['estimator','X','y']}
selected.update(test_auc=float(roc_auc_score(best['y']['test'],p)),test_brier=float(brier_score_loss(best['y']['test'],p)))
report={'selection':'Highest validation AUC among six predeclared candidates. Only selected candidate evaluated on test. Existing split reused; original eight-feature test score was already known.','candidates':[{k:v for k,v in r.items() if k not in ['estimator','X','y']} for r in rows],'selected':selected,'audit_status':'Benchmark only. Existing explanation audit still describes the eight/nine-feature Random Forests; explanations have not been rerun for this candidate.'}
(R/'results/model_benchmark.json').write_text(json.dumps(report,indent=2))
print(json.dumps(selected,indent=2))
