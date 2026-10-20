const fs=require('fs'),path=require('path');
const {reviewEvidence}=require('../src/notice_review_legacy.js');
const dir=path.join(__dirname,'../results/notice_audit');
const inputs=JSON.parse(fs.readFileSync(path.join(dir,'inputs.json')));
const expected=new Map(JSON.parse(fs.readFileSync(path.join(dir,'evaluation.json'))).findings.map(x=>[x.id,x]));
for(const row of inputs){const a=reviewEvidence(row.bundle),b=expected.get(row.id);if(JSON.stringify(a)!==JSON.stringify({disposition:b.disposition,findings:b.findings}))throw Error('Browser/Python mismatch: '+row.id)}
for(const row of JSON.parse(fs.readFileSync(path.join(dir,'challenges.json'))).cases){if(JSON.stringify(reviewEvidence(row.bundle))!==JSON.stringify(row.review))throw Error('Challenge review mismatch')}
console.log('PASS: browser and Python evidence reviewers agree on 360 primary scenarios and 40 challenge examples.');
