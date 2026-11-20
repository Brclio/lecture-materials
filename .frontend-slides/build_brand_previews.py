"""Adapt the copied Brclio landing template to the Frontend Slides fixed stage.
Visual tokens and typography come from Brclio; stage behavior comes from frontend-slides.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import base64, re, urllib.parse, urllib.request

ROOT=Path(__file__).parent
OUT=ROOT/'brand-previews'
OUT.mkdir(exist_ok=True)
SKILL=Path('/Users/huangjiabao/.codex/skills/brclio-design-system')
TEMPLATE=(ROOT/'brand-template-base.html').read_text()
TOKENS=re.search(r':root\s*\{.*?\n\s*\}',TEMPLATE,re.S).group()
BASE=Path('/Users/huangjiabao/.codex/skills/frontend-slides/viewport-base.css').read_text()
ASSETS={name:'data:image/png;base64,'+base64.b64encode((SKILL/'assets'/file).read_bytes()).decode() for name,file in [('AVATAR','avatar.png'),('CHARACTER','character.png')]}
FONTS=['Noto Serif SC:wght@900','Noto Sans SC:wght@400','Noto Sans SC:wght@700','Fraunces:ital,wght@1,400','Caveat:wght@700']

def getfont(family,text):
    q=urllib.parse.urlencode({'family':family,'text':text,'display':'swap'})
    css=urllib.request.urlopen('https://fonts.googleapis.com/css2?'+q,timeout=40).read().decode()
    def embed(m):
        data=urllib.request.urlopen(m.group(1),timeout=40).read()
        return 'url(data:font/woff2;base64,'+base64.b64encode(data).decode()+')'
    return re.sub(r'url\((https://[^)]+)\)',embed,css)

COMMON='''
/* === BRCLIO TEMPLATE BASE ADAPTED TO A FIXED SLIDE CANVAS === */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--stage-bg:#ede9df;--slide-bg:var(--cream)}
body{font-family:'Noto Sans SC',sans-serif;color:var(--ink)}
h1,h2,h3{font-family:'Noto Serif SC',serif;font-weight:900;letter-spacing:0}
::selection{background:var(--yellow);color:var(--ink)}
.slide{isolation:isolate}
.slide.active>*{animation:brand-enter .7s cubic-bezier(.16,1,.3,1) both}
@keyframes brand-enter{from{opacity:0;translate:0 20px}to{opacity:1;translate:0 0}}
/* === PRESENTATION CONTROLS: OUTSIDE THE DESIGN CANVAS === */
.deck-controls{display:flex;gap:6px;align-items:center;padding:6px;background:#fefcf6f5;border:1px solid #d8d4c9;border-radius:12px;box-shadow:0 3px 14px #1a1a2e10;bottom:10px}
.deck-controls button{font:700 15px 'Noto Sans SC',sans-serif;border:0;background:transparent;border-radius:7px;color:var(--ink);padding:8px 15px;cursor:pointer}
.deck-controls button:hover{background:var(--yellow-soft)}
.deck-controls button:disabled{opacity:.3;cursor:default}
.deck-controls output{font-size:13px;min-width:52px;text-align:center;color:var(--ink-light)}
.embed .deck-controls{display:none}
@media(max-width:900px){.deck-controls{bottom:10px;font-size:clamp(12px,2vw,15px)}.deck-controls button{padding:7px 11px}}
@media(prefers-reduced-motion:reduce){.slide.active>*{animation:none!important}}
@media print{.deck-controls{display:none!important}}
'''

JS='''
/* === FRONTEND SLIDES: NAVIGATION AND UNIFORM 16:9 SCALING === */
class SlidePresentation {
 constructor(){
  this.slides=[...document.querySelectorAll('.slide')];this.stage=document.querySelector('.deck-stage');this.index=0;this.wheelTime=0;
  if(new URLSearchParams(location.search).has('embed'))document.body.classList.add('embed');
  this.fit();addEventListener('resize',()=>this.fit());
  document.getElementById('prev').onclick=()=>this.show(this.index-1);
  document.getElementById('next').onclick=()=>this.show(this.index+1);
  document.addEventListener('keydown',e=>{if(e.altKey||e.metaKey||e.ctrlKey)return;if(['ArrowRight','ArrowDown',' ','PageDown'].includes(e.key)){e.preventDefault();this.show(this.index+1)}if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){e.preventDefault();this.show(this.index-1)}if(e.key==='Home')this.show(0);if(e.key==='End')this.show(this.slides.length-1)});
  addEventListener('wheel',e=>{if(document.body.classList.contains('embed'))return;const now=Date.now();if(now-this.wheelTime>650&&Math.abs(e.deltaY)>24){this.show(this.index+(e.deltaY>0?1:-1));this.wheelTime=now}},{passive:true});
  let start=null;this.stage.addEventListener('touchstart',e=>{start=[e.changedTouches[0].clientX,e.changedTouches[0].clientY]},{passive:true});
  this.stage.addEventListener('touchend',e=>{if(!start)return;const dx=e.changedTouches[0].clientX-start[0],dy=e.changedTouches[0].clientY-start[1];if(Math.abs(dx)>40&&Math.abs(dx)>Math.abs(dy))this.show(this.index+(dx<0?1:-1));start=null},{passive:true});
  addEventListener('hashchange',()=>this.show((parseInt(location.hash.slice(1))||1)-1,false));
  this.show((parseInt(location.hash.slice(1))||1)-1,false);
 }
 fit(){const s=Math.min(innerWidth/1920,innerHeight/1080);this.stage.style.transform=`translate(${(innerWidth-1920*s)/2}px,${(innerHeight-1080*s)/2}px) scale(${s})`}
 show(i,update=true){this.index=Math.max(0,Math.min(this.slides.length-1,i));this.slides.forEach((el,n)=>{el.classList.toggle('active',n===this.index);el.classList.toggle('visible',n===this.index);el.setAttribute('aria-hidden',n===this.index?'false':'true');el.inert=n!==this.index});document.getElementById('counter').textContent=`${this.index+1} / ${this.slides.length}`;document.getElementById('prev').disabled=this.index===0;document.getElementById('next').disabled=this.index===this.slides.length-1;if(update)history.replaceState(null,'','#'+(this.index+1));}
}
window.presentation=new SlidePresentation();
'''

def main():
    data={}
    for c in 'jkl':
        p=ROOT/f'brand-{c}'
        if not (p/'slide-3.html').exists():raise RuntimeError('Missing design '+c)
        data[c]=((p/'style.css').read_text(),[(p/f'slide-{i}.html').read_text() for i in range(1,4)])
    text=''.join(re.sub(r'<[^>]+>','',b) for css,slides in data.values() for b in slides)
    chars=''.join(sorted(set(text+'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz上一页下一页')))
    cache=ROOT/'brand-fonts.css'
    if not cache.exists():
        with ThreadPoolExecutor(max_workers=5) as ex:fonts='\n'.join(ex.map(lambda f:getfont(f,chars),FONTS))
        cache.write_text(fonts)
    fonts=cache.read_text()
    for c,(css,slides) in data.items():
        for key,value in ASSETS.items():slides=[s.replace('{{'+key+'}}',value) for s in slides]
        content=''.join('<section class="slide'+(' active visible' if i==0 else '')+'" aria-label="'+['讲座封面','Builder 三步流程','判断 AI 的答案'][i]+'">'+s+'</section>' for i,s in enumerate(slides))
        body='<div class="deck-viewport"><main class="deck-stage">'+content+'</main></div><nav class="deck-controls" aria-label="幻灯片导航"><button id="prev" aria-label="上一页">←</button><output id="counter" aria-live="polite">1 / 3</output><button id="next" aria-label="下一页">→</button></nav><script>'+JS+'</script><!-- Design adapted from Brclio Design System; © 2026 Brclio | CC BY-NC-SA 4.0 -->'
        # Transform the copied template, retaining its base tokens and licensing.
        html=re.sub(r'<link[^>]*>','',TEMPLATE)
        html=re.sub(r'<title>.*?</title>','<title>AI 浪潮下，我们应该如何应对与学习｜Brclio</title><meta name="license" content="CC BY-NC-SA 4.0"><link rel="icon" href="data:,">',html,flags=re.S)
        html=re.sub(r'<style>.*?</style>',lambda m:'<style>'+fonts+'\n'+TOKENS+'\n'+BASE+'\n'+COMMON+'\n'+css+'</style>',html,flags=re.S)
        html=re.sub(r'<body>.*?</body>',lambda m:'<body>'+body+'</body>',html,flags=re.S)
        (OUT/f'brclio-{c}.html').write_text(html)
    print('Built J/K/L, each with 3 slides:',OUT)

if __name__=='__main__':main()
