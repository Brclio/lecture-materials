from pathlib import Path
import re, base64, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT=Path(__file__).parent
OUT=ROOT/'slide-previews'
BASE=Path('/Users/huangjiabao/.codex/skills/frontend-slides/viewport-base.css').read_text()
FONTLIST=[('Noto Sans SC',400),('Noto Sans SC',800),('Noto Serif SC',700),('Manrope',800),('Barlow',900),('Space Grotesk',700),('JetBrains Mono',400),('Big Shoulders Display',900),('Albert Sans',400),('Archivo',800)]

# Shared setup deliberately leaves each composition free to define its own grid.
COMMON='''
/* === SHARED CANVAS AND MOTION === */
*{box-sizing:border-box;margin:0;padding:0}
:root{--stage-bg:#202125;--slide-bg:#fff}
body{font-family:'Noto Sans SC',sans-serif}
.slide{isolation:isolate}
.reveal{animation:arrive .9s cubic-bezier(.16,1,.3,1) both}
.delay-1{animation-delay:.12s}.delay-2{animation-delay:.24s}.delay-3{animation-delay:.36s}
@keyframes arrive{from{opacity:0;transform:translateY(25px)}to{opacity:1;transform:translateY(0)}}
'''
JS='''
/* === FIXED 16:9 STAGE SCALING === */
const stage=document.querySelector('.deck-stage');
function fit(){const s=Math.min(innerWidth/1920,innerHeight/1080);stage.style.transform=`translate(${(innerWidth-1920*s)/2}px,${(innerHeight-1080*s)/2}px) scale(${s})`;}
addEventListener('resize',fit);fit();
'''

def own_previews():
    p=ROOT/'round2-hi';p.mkdir(exist_ok=True)
    (p/'style-h.css').write_text('''
/* === IMMERSIVE KEYNOTE: A LUMINOUS HORIZON === */
:root{--slide-bg:#030c1b;--stage-bg:#02060f}
.slide{color:#effbff;background:radial-gradient(ellipse at 50% 124%,#065e7e 0%,#071c37 35%,#030c1b 65%)}
.h-grid{position:absolute;inset:0;opacity:.16;background-image:radial-gradient(#8be9e6 1px,transparent 1px);background-size:38px 38px;mask-image:linear-gradient(to bottom,black,transparent 70%)}
.h-orbit{position:absolute;width:2050px;height:640px;left:-65px;top:820px;border:2px solid #6df5f0;border-radius:50%;box-shadow:0 -4px 26px #2bdff799,0 -25px 120px #028ef355,inset 0 8px 45px #13f9ef44;transform:rotate(-9deg)}
.h-orbit.two{width:2400px;left:-240px;top:850px;height:670px;opacity:.3;box-shadow:none}
.h-top{position:absolute;top:68px;left:85px;right:85px;display:flex;justify-content:space-between;font:400 25px 'Noto Sans SC';color:#9eb6c9}
.h-word{position:absolute;top:150px;left:0;width:100%;text-align:center;font:800 29px 'Noto Sans SC';letter-spacing:5px;color:#74e4db}
.h-title{position:absolute;top:275px;left:150px;right:150px;text-align:center;font:800 132px/1.35 'Noto Sans SC';letter-spacing:0;text-shadow:0 3px 40px #0c355b}
.h-title span{color:#b7f6ed}
.h-sub{position:absolute;top:690px;left:0;width:100%;text-align:center;font:400 35px 'Noto Sans SC';color:#b8cad9}
.h-bottom{position:absolute;bottom:65px;left:85px;right:85px;display:flex;justify-content:space-between;align-items:center;font:400 24px 'Noto Sans SC';color:#9bbac8}
.h-pulse{display:inline-block;width:11px;height:11px;border-radius:50%;background:#73e8db;margin-right:15px;box-shadow:0 0 20px #74e8db}
''')
    (p/'style-h.body.html').write_text('''
<div class="h-grid" aria-hidden="true"></div><div class="h-orbit" aria-hidden="true"></div><div class="h-orbit two" aria-hidden="true"></div>
<header class="h-top reveal"><span>大学讲座</span><span>AI悦创 / Bornforthis</span></header>
<p class="h-word reveal delay-1">AI 浪潮下</p>
<h1 class="h-title reveal delay-2">我们应该如何<br><span>应对与学习？</span></h1>
<p class="h-sub reveal delay-3">不止提出问题，更是解决问题。</p>
<footer class="h-bottom reveal delay-3"><span><i class="h-pulse"></i>从想法，到作品。</span><span>LEARN / BUILD / SHARE</span></footer>
''')
    (p/'style-i.css').write_text('''
/* === SILVER STUDIO: A SCULPTURAL, HIGH-KEY COMPOSITION === */
:root{--slide-bg:#f5f5f3;--stage-bg:#dedfdf}
.slide{color:#191a20;background:radial-gradient(ellipse at 80% 100%,#dee1ea 0%,#f5f5f3 55%)}
.i-top{position:absolute;top:70px;left:90px;right:90px;display:flex;justify-content:space-between;font:400 24px 'Noto Sans SC';color:#525862}
.i-mark{display:inline-flex;gap:8px;align-items:center;font-family:'Manrope';font-weight:800;letter-spacing:-.8px}
.i-dot{width:13px;height:13px;background:#637693;border-radius:50%}
.i-hero{position:absolute;left:115px;top:270px;z-index:2}
.i-kicker{font:400 35px 'Noto Sans SC';color:#637693;margin-bottom:35px}
.i-title{font:700 103px/1.5 'Noto Serif SC';letter-spacing:0}
.i-sub{font:400 32px 'Noto Sans SC';margin-top:45px;color:#61646b}
.i-object{position:absolute;left:1190px;top:180px;width:600px;height:740px;transform:rotate(27deg);border-radius:50%;background:conic-gradient(from 60deg,#fdfdfd 0deg,#a4acb8 38deg,#eaedf1 64deg,#fff 105deg,#a5afc0 152deg,#e6eaf1 179deg,#fff 217deg,#a2aebe 252deg,#f6f7f9 300deg,#fdfdfd 360deg);box-shadow:inset 20px 12px 30px #fff9,inset -15px -10px 35px #838b9b55,40px 60px 70px #8993a72b}
.i-object:before{content:'';position:absolute;inset:95px 125px;border-radius:50%;background:linear-gradient(120deg,#d3d8e0,#f5f5f3 45%,#ebedf1);box-shadow:inset 20px 10px 25px #8f9bad55,0 0 0 8px #fff4}
.i-object:after{content:'';position:absolute;inset:25px;border-radius:50%;border:2px solid #ffffff99}
.i-line{position:absolute;bottom:145px;left:90px;right:90px;height:1px;background:#b4b9c2}
.i-bottom{position:absolute;bottom:85px;left:90px;right:90px;display:flex;justify-content:space-between;font:400 25px 'Noto Sans SC';color:#656a73}
''')
    (p/'style-i.body.html').write_text('''
<header class="i-top reveal"><span class="i-mark"><i class="i-dot"></i>Bornforthis</span><span>AI悦创 · 大学讲座</span></header>
<div class="i-object reveal delay-1" aria-hidden="true"></div>
<div class="i-hero"><p class="i-kicker reveal delay-1">AI 浪潮下</p><h1 class="i-title reveal delay-2">我们应该如何<br>应对与学习？</h1><p class="i-sub reveal delay-3">不止提出问题，更是解决问题。</p></div>
<div class="i-line"></div><footer class="i-bottom reveal delay-3"><span>原则 · 方法 · 实践</span><span>从想法，到作品。</span></footer>
''')

def getfont(args):
    family,weight,text=args
    q=urllib.parse.urlencode({'family':f'{family}:wght@{weight}','text':text,'display':'swap'})
    css=urllib.request.urlopen('https://fonts.googleapis.com/css2?'+q,timeout=40).read().decode()
    def embed(m):
        data=urllib.request.urlopen(m.group(1),timeout=40).read()
        return 'url(data:font/woff2;base64,'+base64.b64encode(data).decode()+')'
    return re.sub(r'url\((https://[^)]+)\)',embed,css)

def build():
    files={}
    for c,folder in [('d','de'),('e','de'),('f','fg'),('g','fg'),('h','hi'),('i','hi')]:
        p=ROOT/f'round2-{folder}'
        if (p/f'style-{c}.body.html').exists():files[c]=((p/f'style-{c}.css').read_text(),(p/f'style-{c}.body.html').read_text())
    alltext=''.join(re.sub('<[^>]+>','',body) for css,body in files.values())
    chars=''.join(sorted(set(alltext+'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz大学讲座AI悦创')))
    cache=ROOT/'round2-fonts.css'
    if not cache.exists():
        with ThreadPoolExecutor(max_workers=5) as ex:
            fontcss='\n'.join(ex.map(getfont,[(f,w,chars) for f,w in FONTLIST]))
        cache.write_text(fontcss)
    fonts=cache.read_text()
    for c,(css,body) in files.items():
        h='<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>AI 浪潮下，我们应该如何应对与学习｜AI悦创</title><style>'+fonts+'\n'+BASE+'\n'+COMMON+'\n'+css+'</style></head><body><div class="deck-viewport"><main class="deck-stage"><section class="slide active visible">'+body+'</section></main></div><script>'+JS+'</script></body></html>'
        (OUT/f'style-{c}.html').write_text(h)
    print('Built previews:',','.join(files))

if __name__=='__main__':
    import sys
    own_previews()
    if '--own-only' not in sys.argv:build()
