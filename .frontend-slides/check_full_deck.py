from pathlib import Path
import json,re,subprocess
root=Path(__file__).parent.parent
url=(root/'厦门工学院-AI浪潮下的学习与创造.html').as_uri()+'?export=1'
code=r'''async (page)=>{
const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.setViewportSize({width:1280,height:720});await page.emulateMedia({reducedMotion:'reduce'});
await page.goto(URL);await page.evaluate(()=>document.fonts.ready);await page.waitForTimeout(250);
const checks=[];
for(let i=0;i<50;i++){
 await page.evaluate(i=>window.presentation.show(i),i);await page.waitForTimeout(30);
 checks.push(await page.evaluate(()=>{
  const s=document.querySelector('.slide.active'),b=s.getBoundingClientRect();
  const edits=[...s.querySelectorAll('[data-edit],.j-footer')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&!e.closest('[hidden]')});
  const fields=edits.map(e=>{const range=document.createRange();range.selectNodeContents(e);const r=range.getBoundingClientRect();return {key:e.dataset.edit||'footer',text:e.innerText,x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom,outside:r.left<b.left-2||r.right>b.right+2||r.top<b.top-2||r.bottom>b.bottom-2}});
  const overlaps=[];for(let a=0;a<fields.length;a++)for(let c=a+1;c<fields.length;c++){const x=fields[a],y=fields[c],w=Math.min(x.right,y.right)-Math.max(x.x,y.x),h=Math.min(x.bottom,y.bottom)-Math.max(x.y,y.y);if(w>5&&h>5)overlaps.push([x.key,y.key,Math.round(w),Math.round(h)]);}
  return {id:s.dataset.id,title:s.dataset.title,active:document.querySelectorAll('.slide.active').length,outside:fields.filter(x=>x.outside),overlaps,images:[...s.querySelectorAll('img')].every(x=>x.complete&&x.naturalWidth>0),stage:{w:b.width,h:b.height}};
 }));
 await page.screenshot({path:DIR+'/'+String(i+1).padStart(2,'0')+'.png'});
}
return {checks,errors};
}'''.replace('URL',repr(url)).replace('DIR',repr(str(root/'output/playwright/full-deck')))
r=subprocess.run(['/Users/huangjiabao/.codex/skills/playwright/scripts/playwright_cli.sh','-s=xiamen-slides','run-code',code],capture_output=True,text=True)
(root/'.frontend-slides/full-browser-check.txt').write_text(r.stdout+r.stderr)
m=re.search(r'### Result\n(.*?)\n### Ran',r.stdout,re.S)
if m:
 d=json.loads(m.group(1));(root/'.frontend-slides/full-browser-check.json').write_text(json.dumps(d,ensure_ascii=False,indent=2))
 print(json.dumps({'slides':len(d['checks']),'errors':d['errors'],'issues':[s for s in d['checks'] if s['outside'] or s['overlaps'] or not s['images'] or s['stage']['w']!=1280]},ensure_ascii=False))
else:print(r.stdout+r.stderr)
raise SystemExit(r.returncode)
