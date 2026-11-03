const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1200,height:900}});
const errs=[];p.on('pageerror',e=>errs.push(e.message));
for (const h of ['opt2','opt3','action']){
 await p.goto('file://'+process.cwd()+'/preview.html#'+h);await p.waitForTimeout(500);
 await p.screenshot({path:'s_'+h+'.png',fullPage:true});}
await p.setViewportSize({width:400,height:800});await p.goto('file://'+process.cwd()+'/preview.html#top');await p.waitForTimeout(400);
console.log('errs',errs,'scrollW',await p.evaluate(()=>document.documentElement.scrollWidth));
await p.screenshot({path:'s_mobile.png'});await b.close();})();
