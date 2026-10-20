"""Replay actual model outputs under controlled, explicitly constructed policies.

Never load a model supplied by a site visitor: the joblib artifact here is the
trusted project artifact only. The browser displays these precomputed executions.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy
import hashlib
import json
import joblib
import numpy as np
from audit import Predictor

R = Path(__file__).resolve().parents[1]
MODES = {
    'chart_only': 'Explanation report only',
    'original': 'Original records recovered',
    'missing_policy': 'Original lending policy missing',
    'new_policy': 'Newer lending policy substituted',
    'wrong_model': 'Model identity mismatch',
    'changed_input': 'Input snapshot altered',
    'changed_explanation': 'Explanation report altered',
}

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def decide(score, policy):
    return 'Declined' if score >= policy['decline_at_or_above'] else 'Not declined by this rule'

def assess(package, predict, artifact_digest, feature_names):
    event = package['event']
    checks = {}
    for key, expected in [('inputs', 'inputs_sha256'), ('policy', 'policy_sha256')]:
        obj = package.get(key)
        checks[key] = 'missing' if obj is None else ('verified' if digest(obj) == event[expected] else 'mismatch')
    supplied_model = package.get('model_sha256')
    checks['model'] = 'missing' if supplied_model is None else ('verified' if supplied_model == event['model_sha256'] == artifact_digest else 'mismatch')
    explanation = package.get('explanation')
    residual = None if explanation is None else float(explanation['base'] + sum(explanation['values']) - event['prediction'])
    explanation_matches = residual is not None and abs(residual) < 1e-8
    can_replay = checks['model'] == checks['inputs'] == 'verified'
    replayed = None
    if can_replay:
        row = np.array([[package['inputs'][f] for f in feature_names]], dtype=float)
        replayed = float(predict(row)[0])
    score_matches = replayed is not None and abs(replayed - event['prediction']) < 1e-8
    decision = decide(replayed, package['policy']) if score_matches and checks['policy'] == 'verified' else None
    return {
        'record_checks': checks,
        'explanation_sum_matches': explanation_matches,
        'explanation_residual': residual,
        'prediction_reproduced': score_matches,
        'replayed_prediction': replayed,
        'original_decision_reconstructed': decision is not None and decision == event['decision'],
        'replayed_decision': decision,
        'inconsistencies': [k for k, v in checks.items() if v == 'mismatch'] + ([] if explanation_matches else ['explanation']),
        'missing_records': [k for k, v in checks.items() if v == 'missing'],
        'upstream_score_explained': False,
    }

def run():
    out = R / 'results/decision_reconstruction'
    out.mkdir(exist_ok=True)
    model_path = R / 'results/reference_sensitivity/rf8_model.joblib'
    model_sha = hashlib.sha256(model_path.read_bytes()).hexdigest()
    artifact = joblib.load(model_path)
    predict = Predictor(artifact['model'], artifact['encoding'])
    names = artifact['features']
    reference = json.loads((R / 'results/reference/audit_results.json').read_text())
    cases = [c for c in reference['cases'] if c['model'] == 'without_score']
    original_policy = {'id': 'illustrative-policy-v1', 'decline_at_or_above': .50, 'role': 'constructed research rule, not observed lender policy'}
    later_policy = {**original_policy, 'id': 'illustrative-policy-v2', 'decline_at_or_above': .65}
    records, evaluations = [], []
    for case in cases:
        phi = case['explanations']['Exact interventional Shapley'][0]
        event = {'case_id': case['case_id'], 'timestamp': '2026-09-01T12:00:00Z',
                 'prediction': case['score'], 'decision': decide(case['score'], original_policy),
                 'inputs_sha256': digest(case['features']), 'policy_sha256': digest(original_policy), 'model_sha256': model_sha}
        full = {'event': event, 'inputs': case['features'], 'model_sha256': model_sha,
                'policy': original_policy, 'explanation': {'base': phi['diagnostics']['base'], 'values': phi['values']}}
        packages = {}
        for mode in MODES:
            p = copy.deepcopy(full)
            if mode == 'chart_only':
                for key in ['inputs', 'model_sha256', 'policy']: p.pop(key)
            elif mode == 'missing_policy': p.pop('policy')
            elif mode == 'new_policy': p['policy'] = copy.deepcopy(later_policy)
            elif mode == 'wrong_model': p['model_sha256'] = hashlib.sha256(b'constructed substitute artifact').hexdigest()
            elif mode == 'changed_input': p['inputs'][names[0]] += 24
            elif mode == 'changed_explanation': p['explanation']['values'][0] += .10
            result = assess(p, predict, model_sha, names)
            evaluations.append({'case_id': case['case_id'], 'package': mode, **result})
            packages[mode] = {'records': p, 'assessment': result}
        records.append({'case_id': case['case_id'], 'score': case['score'], 'packages': packages,
                        'later_policy_decision': decide(case['score'], later_policy)})
    summary = []
    for mode, label in MODES.items():
        rows = [e for e in evaluations if e['package'] == mode]
        summary.append({'package': mode, 'label': label, 'records': len(rows),
                        'explanations_add_up': sum(e['explanation_sum_matches'] for e in rows),
                        'predictions_reproduced': sum(e['prediction_reproduced'] for e in rows),
                        'decisions_reconstructed': sum(e['original_decision_reconstructed'] for e in rows),
                        'inconsistent_packages': sum(bool(e['inconsistencies']) for e in rows)})
    payload = {'generated_at': datetime.now(timezone.utc).isoformat(), 'design': 'Controlled evidence-removal and inconsistency demonstration; constructed lending policies around measured predictions.',
               'protocol_sha256': hashlib.sha256((R / 'docs/DECISION_RECONSTRUCTION_PROTOCOL.md').read_bytes()).hexdigest(),
               'model_sha256': model_sha, 'features': names, 'policies': [original_policy, later_policy],
               'case_count': len(cases), 'package_count': len(evaluations), 'summary': summary, 'cases': records,
               'changed_outcomes_under_later_policy': sum(c['later_policy_decision'] != c['packages']['original']['records']['event']['decision'] for c in records),
               'trust_assumption': 'Logged identities are retained independently and trusted. Matching hashes do not authenticate real-world data or establish regulatory adequacy.'}
    (out / 'experiment.json').write_text(json.dumps(payload, indent=2))
    print(json.dumps({'summary': summary, 'changed_outcomes_under_later_policy': payload['changed_outcomes_under_later_policy']}, indent=2))

if __name__ == '__main__':
    run()
