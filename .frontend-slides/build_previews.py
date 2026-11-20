from pathlib import Path
import base64
import re
import urllib.parse
import urllib.request

ROOT = Path(__file__).parent
OUT = ROOT / 'slide-previews'
OUT.mkdir(exist_ok=True)
BASE = Path('/Users/huangjiabao/.codex/skills/frontend-slides/viewport-base.css').read_text()

# Subset and embed official Google Fonts so local previews work offline.
TEXT = 'AI浪潮下我们应该如何应对与学习不止提出问题更是解决问题厦门工学院悦创从想法到作品理念交付原则方法实践BornforthisLEARNBUILDSHARE0123456789 /·→，？。'
def font(family, weight, chars=TEXT):
    url = 'https://fonts.googleapis.com/css2?' + urllib.parse.urlencode({'family': f'{family}:wght@{weight}', 'text': chars, 'display': 'swap'})
    css = urllib.request.urlopen(url, timeout=30).read().decode()
    def embed(match):
        data = urllib.request.urlopen(match.group(1), timeout=30).read()
        return 'url(data:font/woff2;base64,' + base64.b64encode(data).decode() + ')'
    return re.sub(r'url\((https://[^)]+)\)', embed, css)

cache = ROOT / 'preview-fonts.css'
if not cache.exists():
    cache.write_text('\n'.join(font(*f) for f in [('Noto Sans SC',400),('Noto Sans SC',800),('Noto Serif SC',700),('Manrope',800),('Barlow',900)]))
FONTS = cache.read_text()
COMMON = '''
/* === BASE TYPOGRAPHY AND SHARED SLIDE CHROME === */
*{box-sizing:border-box;margin:0;padding:0}
:root{--stage-bg:#191b1d;--slide-bg:#fff}
body{font-family:'Noto Sans SC',sans-serif}
.slide{padding:90px 110px}
.top{display:flex;justify-content:space-between;align-items:center;font-size:26px;font-weight:400;letter-spacing:1px}
.rule{height:1px;background:currentColor;opacity:.25;margin-top:32px}
.footer{position:absolute;bottom:75px;left:110px;right:110px;display:flex;align-items:center;justify-content:space-between;font-size:25px}
.reveal{animation:rise .85s cubic-bezier(.16,1,.3,1) both}
.delay-1{animation-delay:.12s}.delay-2{animation-delay:.23s}.delay-3{animation-delay:.34s}
@keyframes rise{from{opacity:0;transform:translateY(28px)}to{opacity:1;transform:translateY(0)}}
h1{font-weight:800;letter-spacing:0;line-height:1.3}
'''
SCRIPT = '''
/* === SCALE THE COMPLETE 1920 × 1080 STAGE, INCLUDING ON PHONES === */
const stage=document.querySelector('.deck-stage');
function fit(){const s=Math.min(innerWidth/1920,innerHeight/1080);stage.style.transform=`translate(${(innerWidth-1920*s)/2}px,${(innerHeight-1080*s)/2}px) scale(${s})`;}
addEventListener('resize',fit);fit();
'''
def save(letter, css, body):
    html='<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI 浪潮下，我们应该如何应对与学习｜AI悦创</title><style>'+FONTS+'\n'+BASE+'\n'+COMMON+'\n'+css+'</style></head><body><div class="deck-viewport"><main class="deck-stage"><section class="slide active visible" aria-label="AI 浪潮下，我们应该如何应对与学习">'+body+'</section></main></div><script>'+SCRIPT+'</script></body></html>'
    (OUT / f'style-{letter}.html').write_text(html)

save('a','''
/* === ELECTRIC STUDIO: A PRECISE WHITE / COBALT SPLIT === */
:root{--slide-bg:#fff}.slide{color:#111318}
.lower{position:absolute;left:0;right:0;bottom:0;height:320px;background:#4361ee;color:white;padding:60px 110px}
.lower p{font-size:44px;font-weight:800}.lower .footer{bottom:52px}
.hero{position:absolute;left:110px;top:245px;width:1260px}
.hero .eyebrow{font-size:37px;color:#4361ee;margin-bottom:22px}
h1{font-size:113px;line-height:1.26}
.ai{position:absolute;right:105px;top:267px;font:800 244px/1 'Manrope';color:#4361ee;letter-spacing:-15px}
.sideline{position:absolute;right:110px;top:570px;width:268px;border-top:3px solid #4361ee;padding-top:22px;font:800 24px 'Manrope';color:#4361ee}
''','''
<header class="top reveal"><span>厦门工学院</span><span>AI悦创 / Bornforthis</span></header><div class="rule"></div>
<div class="hero reveal delay-1"><p class="eyebrow">AI 浪潮下</p><h1>我们应该如何<br>应对与学习？</h1></div>
<div class="ai reveal delay-2" aria-hidden="true">AI</div><div class="sideline reveal delay-2">LEARN. BUILD. SHARE.</div>
<div class="lower"><p class="reveal delay-2">不止提出问题，更是解决问题。</p><footer class="footer reveal delay-3"><span>原则 · 方法 · 实践</span><span>01</span></footer></div>
''')

save('b','''
/* === BROADSIDE: TYPE AS THE MAIN GRAPHIC ELEMENT === */
:root{--slide-bg:#111111}.slide{color:#f0ece5}
.top{font-size:25px}.rule{background:#505048;opacity:1}
.hero{position:absolute;left:110px;top:210px}
.wordmark{font:900 280px/.95 'Barlow',sans-serif;letter-spacing:-8px;color:#e85d26}
.wordmark span{font:800 115px 'Noto Sans SC',sans-serif;letter-spacing:0;margin-left:33px;vertical-align:38px}
h1{font-size:107px;line-height:1.35;margin-top:25px}
.callout{position:absolute;right:110px;bottom:230px;width:510px;border-top:2px solid #e85d26;padding-top:28px;color:#e85d26;font-size:42px;font-weight:800;line-height:1.6}
.footer{border-top:1px solid #505048;padding-top:30px;color:#a5a59d}
''','''
<header class="top reveal"><span>厦门工学院</span><span>AI悦创 / Bornforthis</span></header><div class="rule"></div>
<div class="hero"><div class="wordmark reveal delay-1">AI<span>浪潮下</span></div><h1 class="reveal delay-2">我们应该如何<br>应对与学习？</h1></div>
<p class="callout reveal delay-3">不止提出问题，<br>更是解决问题。</p>
<footer class="footer reveal delay-3"><span>原则 · 方法 · 实践</span><span>01</span></footer>
''')

save('c','''
/* === CUSTOM: A LEARNING JOURNEY, DRAWN AS A TIDAL HORIZON === */
:root{--slide-bg:#f2eedf}.slide{color:#173c35}
.top{font-size:25px}.rule{opacity:.3}
.art{position:absolute;left:110px;top:245px;width:520px;height:570px;border-radius:260px 260px 0 0;overflow:hidden;background:#ddd5ba}
.sun{position:absolute;width:290px;height:290px;border-radius:50%;background:#d47a42;left:115px;top:90px}
.water{position:absolute;left:-140px;bottom:-155px;width:800px;height:500px;border-radius:50%;background:#1f5145;transform:rotate(-15deg)}
.water.two{left:-270px;bottom:-255px;background:#729681;transform:rotate(14deg)}
.arc{position:absolute;width:700px;height:700px;left:-90px;top:220px;border:1px solid #b4c1a3;border-radius:50%}
.arc.a2{top:255px}.arc.a3{top:290px}.arc.a4{top:325px}
.hero{position:absolute;left:750px;top:280px;right:95px}
.eyebrow{font-size:30px;margin-bottom:42px;color:#8b5b3d}
h1{font-family:'Noto Serif SC',serif;font-size:90px;line-height:1.48;font-weight:700}
.subtitle{font-size:34px;margin-top:45px;line-height:1.7}
.footer{border-top:1px solid #bdc2ad;padding-top:26px}
''','''
<header class="top reveal"><span>厦门工学院</span><span>AI悦创 / Bornforthis</span></header><div class="rule"></div>
<div class="art reveal delay-1" aria-hidden="true"><div class="sun"></div><div class="water"></div><div class="water two"></div><div class="arc"></div><div class="arc a2"></div><div class="arc a3"></div><div class="arc a4"></div></div>
<div class="hero"><p class="eyebrow reveal delay-1">AI 浪潮下</p><h1 class="reveal delay-2">我们应该如何<br>应对与学习？</h1><p class="subtitle reveal delay-3">不止提出问题，更是解决问题。</p></div>
<footer class="footer reveal delay-3"><span>从想法，到作品。</span><span>01</span></footer>
''')
print('Created three self-contained title slides:', OUT)
