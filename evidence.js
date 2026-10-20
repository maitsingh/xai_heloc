/* Numerical explanation-evidence utilities. No legal verdicts or wording dictionary. */
(function(root){
 const finite=n=>typeof n==='number'&&Number.isFinite(n);
 function validate(pack){
  if(!pack||pack.schema_version!=='credit-explanation-evidence/v1')throw Error('Use the credit-explanation-evidence/v1 JSON format. Download the example file to see the structure.');
  if(!pack.model||typeof pack.model.id!=='string'||!pack.model.id.trim()||typeof pack.model.output!=='string')throw Error('Provide a model identifier and name the repayment outcome being explained.');
  if(pack.model.score_scale!=='probability')throw Error('This version supports probability-scale scores only. Do not mix probability-scale predictions with log-odds or raw-margin contributions.');
  if(!Array.isArray(pack.features)||pack.features.length<1||pack.features.length>300)throw Error('Provide between 1 and 300 feature definitions.');
  const features=new Set();
  for(const f of pack.features){if(typeof f.id!=='string'||!f.id.trim()||typeof f.label!=='string'||!f.label.trim()||(f.group!==undefined&&(typeof f.group!=='string'||!f.group.trim()))||f.id.length>150||f.label.length>250||features.has(f.id))throw Error('Feature identifiers must be unique, with readable labels.');features.add(f.id)}
  if(!Array.isArray(pack.applications)||!pack.applications.length||pack.applications.length>500)throw Error('Provide between 1 and 500 application explanations.');
  const ids=new Set();
  for(const a of pack.applications){
   if(typeof a.id!=='string'||!a.id.trim()||ids.has(a.id)||!finite(a.score)||a.score<0||a.score>1)throw Error('Each application needs a unique string ID and a finite model score between 0 and 1.');ids.add(a.id);
   if(!Array.isArray(a.shapley)||a.shapley.length<2||a.shapley.length>20)throw Error('Each application needs 2–20 Shapley explanations of the same prediction.');
   const explanations=new Set();
   for(const ex of a.shapley){if(!ex||typeof ex.id!=='string'||!ex.id.trim()||explanations.has(ex.id)||typeof ex.reference!=='string'||!ex.reference.trim()||(!finite(ex.baseline)||ex.baseline<0||ex.baseline>1)||!ex.values)throw Error('Each explanation needs a unique ID, a comparison-group description, a baseline and all feature contributions.');explanations.add(ex.id);const keys=Object.keys(ex.values);if(keys.length!==features.size||keys.some(k=>!features.has(k)||!finite(ex.values[k])||Math.abs(ex.values[k])>1.000001))throw Error('Every Shapley explanation must supply one finite signed contribution for every declared feature.');}
   if(a.local_approximations!==undefined){if(!Array.isArray(a.local_approximations)||a.local_approximations.length>20)throw Error('Local approximation attempts must be an array with at most 20 entries.');for(const run of a.local_approximations){if(!run.coefficients||Object.entries(run.coefficients).some(([k,v])=>!features.has(k)||!finite(v)))throw Error('Local coefficients must use declared feature IDs and finite numbers.');if(run.fidelity&&( !finite(run.fidelity.r2)||run.fidelity.r2>1||!finite(run.fidelity.mae)||run.fidelity.mae<0||!['independent_generated','fitting_only','other'].includes(run.fidelity.evaluation)))throw Error('Fidelity must state a finite R² (at most 1), nonnegative score error and evaluation type: independent_generated, fitting_only, or other.');}}
  }
  return pack;
 }
 function contributions(ex,features,grouped=false){let rows;if(grouped){const sums=new Map();for(const f of features){const group=f.group||f.label;sums.set(group,(sums.get(group)||0)+ex.values[f.id]);}rows=[...sums].map(([id,value])=>({id,label:id,value}));}else rows=features.map(f=>({id:f.id,label:f.label,value:ex.values[f.id]}));return rows.sort((a,b)=>b.value-a.value||a.id.localeCompare(b.id));}
 function leading(ex,features,grouped=false){return contributions(ex,features,grouped).filter(r=>r.value>1e-10).slice(0,4)}
 function compare(a,b,features,grouped=false){const A=leading(a,features,grouped),B=leading(b,features,grouped),as=new Set(A.map(r=>r.id)),bs=new Set(B.map(r=>r.id));return {left:A,right:B,shared:A.filter(r=>bs.has(r.id)).map(r=>r.id),added:B.filter(r=>!as.has(r.id)).map(r=>r.id),removed:A.filter(r=>!bs.has(r.id)).map(r=>r.id),changed:A.length!==B.length||A.some(r=>!bs.has(r.id)),first_changed:(A[0]?.id||null)!==(B[0]?.id||null)};}
 function residual(a,ex){return a.score-ex.baseline-Object.values(ex.values).reduce((a,b)=>a+b,0)}
 const api={validate,contributions,leading,compare,residual};if(typeof module!=='undefined')module.exports=api;else root.ExplanationEvidence=api;
})(typeof globalThis!=='undefined'?globalThis:this);
