"""Contract-based review of supplied decision/notice evidence. No scenario labels accepted.

This checks consistency against retained records, not authenticity, legal sufficiency,
or semantic equivalence of arbitrary natural-language paraphrases.
"""
def review(bundle):
    decision=bundle.get('decision');catalog=bundle.get('catalog');notice=bundle.get('notice',{})
    if not decision or not catalog:
        return {'disposition':'Insufficient evidence','findings':[{'code':'missing_evidence','title':'Decision trace or mapping catalog is unavailable','evidence':'decision / catalog','request':'Obtain the versioned trace and reason catalog before assessing the notice.'}]}
    findings=[]
    def add(code,title,path,request):
        findings.append(dict(code=code,title=title,evidence=path,request=request))
    if notice.get('decision_id')!=decision.get('id'):
        add('identity','Notice refers to a different decision','notice.decision_id / decision.id','Recover the notice for the same decision identifier.')
    for field,expected in decision['artifacts'].items():
        if notice.get('artifacts',{}).get(field)!=expected:
            add('version',f'{field} does not match the decision record',f'notice.artifacts.{field} / decision.artifacts.{field}','Regenerate from the retained decision-time artifacts; preserve the original notice.')
    reasons=notice.get('reasons',[])
    for i,r in enumerate(reasons):
        spec=catalog.get(r.get('code'))
        if not spec:
            add('mapping','Reason code is absent from the supplied catalog',f'notice.reasons[{i}].code','Provide the applicable catalog version and validate the description.');continue
        if r.get('text') not in spec['approved_wording']:
            add('wording','Reason wording has no support in the supplied mapping catalog',f'notice.reasons[{i}].text / catalog.{r["code"]}','Review the description and direction against feature evidence; an unlisted paraphrase needs human review.')
        if sorted(r.get('source_features',[]))!=sorted(spec['source_features']):
            add('mapping','Stated reason and cited source features do not match',f'notice.reasons[{i}].source_features / catalog.{r["code"]}','Correct the source-to-reason mapping and examine affected notices.')
        if decision['basis']=='model':
            if not all(decision['attribution'].get(f,0)>0 for f in r.get('source_features',[])):
                add('support','Model reason cites a feature without a positive risk attribution',f'notice.reasons[{i}] / decision.attribution','Verify sign, output class and reference before selecting this feature as an adverse contributor.')
    observed={r.get('code') for r in reasons}
    if decision['basis']=='eligibility_gate':
        required=set(decision['required_reasons'])
        if not required.issubset(observed):
            add('decision_coverage','The terminating eligibility rule is missing from the reasons','decision.rule_trace / notice.reasons','Explain the recorded rule that stopped the application; do not substitute an unused risk-score explanation.')
        if observed-required:
            add('unused_score','Notice cites model factors after the policy gate stopped evaluation','decision.basis / notice.reasons','Separate diagnostic model outputs from the factors actually used in this decision.')
    return {'disposition':'Investigate' if findings else 'No discrepancy detected','findings':findings}
