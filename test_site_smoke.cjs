/* Simulated DOM and Blob tests. Not a replacement for browser/visual QA. */
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const root=path.resolve(process.argv[2]||'.'),html=fs.readFileSync(path.join(root,'site/index.html'),'utf8');
let els=[],ids={},blobs=new Map(),serial=0;
class El{
 constructor(tag,attrs){this.tag=tag;this.attrs=attrs;this.id=attrs.id;this.dataset={};for(const[k,v]of Object.entries(attrs))if(k.startsWith('data-'))this.dataset[k.slice(5)]=v;this.hidden='hidden'in attrs;this.value=attrs.value||'';this.listeners={};this._html='';}
 set innerHTML(s){this._html=s;parse(s);if(this.tag==='select')this.value=(s.match(/<option value="([^"]*)"/)||[])[1]||'';}
 get innerHTML(){return this._html}
 setAttribute(k,v){this.attrs[k]=v}
 removeAttribute(k){delete this.attrs[k]}
 addEventListener(k,cb){this.listeners[k]=cb}
 fire(k){return this.listeners[k]?.({target:this})}
}
function parse(h){for(const m of h.matchAll(/<(\w+)([^>]*)>/g)){const a={};for(const x of m[2].matchAll(/([\w-]+)(?:="([^"]*)")?/g))a[x[1]]=x[2]||'';if(a.id||a.class||Object.keys(a).some(k=>k.startsWith('data-'))){const e=new El(m[1],a);els.push(e);if(a.id)ids[a.id]=e;}}}
parse(html);
const doc={getElementById:id=>{if(id==='score-investigation-render')return null;assert(ids[id],'Missing '+id);return ids[id]},querySelector:sel=>{assert(sel.startsWith('#'));assert(ids[sel.slice(1)],'Missing '+sel);return ids[sel.slice(1)]},querySelectorAll:sel=>{
 if(sel==='.page')return els.filter(e=>e.attrs.class==='page'||e.attrs.class?.split(' ').includes('page'));
 if(sel==='nav [data-page]')return els.filter(e=>e.tag==='button'&&e.dataset.page&&['The project',''].includes('')).filter(e=>e.dataset.page&& !e.attrs.class);
 if(sel.startsWith('[data-'))return els.filter(e=>e.dataset[sel.slice(6,-1)]!==undefined);
 throw new Error('Unexpected selector '+sel);
}};
const ctx={document:doc,window:{scrollTo:()=>{},print:()=>{}},console,Blob,URL:{createObjectURL:b=>{const u='blob:mock-'+(++serial);blobs.set(u,b);return u},revokeObjectURL:u=>blobs.delete(u)}};
vm.createContext(ctx);for(const f of ['data.js','evidence.js','app.js'])vm.runInContext(fs.readFileSync(path.join(root,'site',f),'utf8'),ctx);
(async()=>{
 assert(!ids.about.hidden);vm.runInContext("page('investigate')",ctx);assert(!ids.investigate.hidden);assert(ids.about.hidden);
 const all=vm.runInContext('S.cases.map(c=>c.case_id)',ctx);
 for(const id of all){
  ids['case-select'].value=String(id);ids['case-select'].fire('change');
  assert.equal(vm.runInContext('caseId',ctx),id);
  assert(ids['case-content'].innerHTML.includes('Shapley contributions to the repayment prediction'));
  vm.runInContext("page('investigate')",ctx);assert(!ids['case-toolbar'].hidden);
  vm.runInContext("page('compare')",ctx);assert(!ids.compare.hidden);assert(ids.investigate.hidden);
  ids['topics-view'].fire('click');assert.equal(vm.runInContext('detail',ctx),'topics');
  assert(ids['approximation-charts'].innerHTML.includes('Revolving balances'));
  assert.equal(ids['topics-view'].attrs['aria-pressed'],'true');
  ids['factors-view'].fire('click');assert.equal(vm.runInContext('detail',ctx),'factors');
  assert(ids['approximation-charts'].innerHTML.includes('Average account age'));
  assert(ids['local-fit'].innerHTML.includes('median weighted R²'));
 }
 ids['case-select'].value='8193';ids['case-select'].fire('change');
 ids['prepare-report'].fire('click');assert(!ids['report-output'].hidden);
 const note=await blobs.get(ids['download-report'].href).text();assert(note.includes('WHAT REMAINS UNESTABLISHED'));assert(note.includes('Historical record: 8193'));assert(note.startsWith('<!doctype html>'));
 const data=JSON.parse(await blobs.get(ids['download-json'].href).text());assert.equal(data.case_id,8193);assert.equal(data.measurements.case_id,8193);assert(data.findings.unestablished_claim.includes('original external credit-risk score'));
 fs.mkdirSync(path.join(root,'site/examples'),{recursive:true});fs.writeFileSync(path.join(root,'site/examples/external-score-review-8193.html'),note);fs.writeFileSync(path.join(root,'site/examples/external-score-review-8193.json'),JSON.stringify(data,null,2));
 ids['topics-view'].fire('click');assert(ids['report-output'].hidden);assert.equal(blobs.size,0);
 vm.runInContext("page('research')",ctx);assert(!ids.research.hidden);assert(!ids['case-toolbar'].hidden);assert(ids['protocol-tests'].innerHTML.includes('Decision fidelity'));assert(ids['protocol-case-matrix'].innerHTML.includes('record 8193'));vm.runInContext("page('methods')",ctx);assert(!ids.methods.hidden);vm.runInContext("page('legal')",ctx);assert(!ids.legal.hidden);vm.runInContext("page('evidence')",ctx);assert(!ids.evidence.hidden);assert(ids.legal.hidden);assert(ids['findings-summary'].innerHTML.includes('4 of 12'));assert(ids['agreement-table'].innerHTML.includes('12'));
 for(let index=0;index<4;index++){
  ids['agreement-band'].value=String(index);ids['agreement-band'].fire('input');
  const band=vm.runInContext('S.bands['+index+']',ctx);
  assert(ids['findings-summary'].innerHTML.includes(band.different_factor_sets_when_both_close_to_original+' of '+band.both_close_to_original));
  assert.equal(ids['agreement-band'].attrs['aria-valuetext'],(band.probability_band*100).toFixed(1)+' percentage points');
 }
 ids['other-methods-view'].fire('click');assert(ids['requirements-panel'].hidden);assert(!ids['other-methods-panel'].hidden);assert.equal(ids['evidence-switch'].dataset.mode,'methods');
 ids['requirements-view'].fire('click');assert(!ids['requirements-panel'].hidden);assert(ids['other-methods-panel'].hidden);
 assert(!html.includes('Newer policy supplied'));assert(!html.includes('Review findings'));
 console.log('PASS: all forty records, both factor/topic views, all seven navigation pages, local-fidelity evidence, all four measured slider positions, evidence/method selector, readable/JSON note contents and stale-export invalidation. Browser visual and download behavior remain outside this simulation.');
})().catch(e=>{console.error(e);process.exitCode=1});
