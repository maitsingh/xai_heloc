/* Browser implementation of the evidence contract checker. Inputs contain no truth labels. */
function reviewEvidence(bundle){
 const d=bundle.decision,c=bundle.catalog,n=bundle.notice||{},findings=[];
 if(!d||!c)return {disposition:'Insufficient evidence',findings:[{code:'missing_evidence',title:'Decision trace or mapping catalog is unavailable',evidence:'decision / catalog',request:'Obtain the versioned trace and reason catalog before assessing the notice.'}]};
 function add(code,title,evidence,request){findings.push({code,title,evidence,request})}
 if(n.decision_id!==d.id)add('identity','Notice refers to a different decision','notice.decision_id / decision.id','Recover the notice for the same decision identifier.');
 for(const [field,expected] of Object.entries(d.artifacts))if((n.artifacts||{})[field]!==expected)add('version',field+' does not match the decision record','notice.artifacts.'+field+' / decision.artifacts.'+field,'Regenerate from the retained decision-time artifacts; preserve the original notice.');
 (n.reasons||[]).forEach((r,i)=>{const spec=c[r.code];if(!spec){add('mapping','Reason code is absent from the supplied catalog',`notice.reasons[${i}].code`,'Provide the applicable catalog version and validate the description.');return}
 if(!spec.approved_wording.includes(r.text))add('wording','Reason wording has no support in the supplied mapping catalog',`notice.reasons[${i}].text / catalog.${r.code}`,'Review the description and direction against feature evidence; an unlisted paraphrase needs human review.');
 if(JSON.stringify([...(r.source_features||[])].sort())!==JSON.stringify([...spec.source_features].sort()))add('mapping','Stated reason and cited source features do not match',`notice.reasons[${i}].source_features / catalog.${r.code}`,'Correct the source-to-reason mapping and examine affected notices.');
 if(d.basis==='model'&&!(r.source_features||[]).every(f=>(d.attribution[f]||0)>0))add('support','Model reason cites a feature without a positive risk attribution',`notice.reasons[${i}] / decision.attribution`,'Verify sign, output class and reference before selecting this feature as an adverse contributor.');
 });
 if(d.basis==='eligibility_gate'){let observed=new Set((n.reasons||[]).map(r=>r.code)),required=new Set(d.required_reasons);
 if(![...required].every(r=>observed.has(r)))add('decision_coverage','The terminating eligibility rule is missing from the reasons','decision.rule_trace / notice.reasons','Explain the recorded rule that stopped the application; do not substitute an unused risk-score explanation.');
 if([...observed].some(r=>!required.has(r)))add('unused_score','Notice cites model factors after the policy gate stopped evaluation','decision.basis / notice.reasons','Separate diagnostic model outputs from the factors actually used in this decision.');}
 return {disposition:findings.length?'Investigate':'No discrepancy detected',findings};
}
function replayForest(forest,features){
 const raw=forest.features.map(f=>Number(features[f]));
 const x=raw.map((v,i)=>v<0?forest.medians[i]:v).concat(raw.map(v=>v===-7?1:0),raw.map(v=>v===-8?1:0),raw.map(v=>v===-9?1:0));
 let total=0;
 for(const t of forest.trees){let n=0;while(t.left[n]!==-1)n=x[t.feature[n]]<=t.threshold[n]?t.left[n]:t.right[n];let v=t.value[n];total+=v[1]/(v[0]+v[1]);}
 return total/forest.trees.length;
}
if(typeof module!=='undefined')module.exports={reviewEvidence,replayForest};
