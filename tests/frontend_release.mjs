import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const elements=new Map();
function element(){return {textContent:'',innerHTML:'',style:{},open:false,disabled:false,classList:{toggle(){},contains(){return false;}},showModal(){this.open=true;},close(){this.open=false;},addEventListener(){},querySelector(){return null;}};}
const get=s=>{if(!elements.has(s))elements.set(s,element());return elements.get(s);};
const factory={name:'Release factory',repository:'owner/repository',budget:20,model:'External harness',approval_stages:['spec','review']};
let response={ok:true,status:200,json:async()=>({runs:[],factory,stages:['triage','spec','build','review','verify'],auth_enabled:true,worker_enabled:false})};
const context=vm.createContext({document:{querySelector:get,querySelectorAll:()=>[],addEventListener(){},hidden:false},window:{addEventListener(){}},location:{hash:''},fetch:async()=>response,Intl,Date,setTimeout:()=>1,clearTimeout(){},setInterval(){},URL,Blob,console});
vm.runInContext(fs.readFileSync('web/app.js','utf8'),context);
await new Promise(resolve=>setImmediate(resolve));
for(const view of ['overview','runs','approvals','factory','stack','insights']){
  vm.runInContext(`navigate('${view}')`,context);
  assert.ok(get('#main').innerHTML.length>100,`${view} renders`);
  assert.equal(get('#breadcrumb').textContent,vm.runInContext(`names['${view}']`,context));
}
assert.match(vm.runInContext(`esc('<img src=x onerror="boom">')`,context),/&lt;img/);
response={ok:false,status:403,json:async()=>({detail:'Authentication required'})};
await assert.rejects(vm.runInContext("api('/overview')",context),/Authentication required/);
assert.equal(get('#auth-dialog').open,true,'tenant-gateway 403 opens login when no token is set');
get('#auth-dialog').open=false;
vm.runInContext("token='valid-but-readonly'",context);
await assert.rejects(vm.runInContext("api('/overview')",context));
assert.equal(get('#auth-dialog').open,false,'role-denial does not reopen login for an existing credential');
response={ok:false,status:502,json:async()=>{throw Error('bad json');}};
await assert.rejects(vm.runInContext("api('/overview')",context),/unexpected response/);
const html=fs.readFileSync('web/index.html','utf8');
assert.match(html,/id="api-reference"/);
assert.doesNotMatch(html,/href="\/openapi.json"/,'protected OpenAPI uses authenticated fetch instead of unauthenticated navigation');
console.log('Frontend release checks passed: six views, escaped output, auth boundary, invalid responses, authenticated API-reference control.');
