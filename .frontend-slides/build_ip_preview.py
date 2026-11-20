"""Extend the reviewed Brclio J sample with two unmodified scene illustrations.

The existing J HTML supplies the self-contained cover, brand typography,
16:9 stage CSS, navigation, and license. New images are embedded byte-for-byte;
object-fit: contain preserves the entire illustration at its original ratio.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import base64
import hashlib
import re
import sys
import urllib.parse
import urllib.request

ROOT = Path(__file__).parent
WORKSPACE = ROOT.parent
OUT = ROOT / 'ip-previews'
SOURCE = ROOT / 'brand-previews' / 'brclio-j.html'
IMAGES = WORKSPACE / 'assets' / 'xiamen-ai-lecture-illustrations'
TARGET = OUT / 'brclio-ip.html'
SCENES = ['01-learning-to-work.png', '02-judge-ai-answers.png']

CSS = '''
/* === IP SCENES: WARM BRAND FRAME, ORIGINAL WHITE ILLUSTRATIONS === */
.ip-canvas{position:absolute;inset:0;overflow:hidden;background:var(--cream);color:var(--ink);font-family:'Noto Sans SC',sans-serif}
.ip-canvas *{box-sizing:border-box}
.ip-scene{position:absolute;margin:0;background:#fff}
.ip-scene img{display:block;width:100%;height:100%;max-width:100%;max-height:100%;object-fit:contain;object-position:center;filter:none;opacity:1}
.ip-scene-kicker{font:400 27px/1.5 'Noto Sans SC',sans-serif;color:var(--blue)}
.ip-learning .ip-copy{position:absolute;left:110px;top:275px;width:460px}
.ip-learning h2{font:900 84px/1.45 'Noto Serif SC',serif;letter-spacing:0;color:var(--blue);margin:27px 0 0}
.ip-learning h2 span,.ip-learning h2 strong{display:block;font-weight:900}
.ip-learning h2 strong{display:inline-block;position:relative;isolation:isolate}
.ip-learning h2 strong::after{content:'';position:absolute;left:0;right:0;height:40px;bottom:5px;background:var(--yellow);z-index:-1}
.ip-learning .ip-support{font:400 30px/1.7 'Noto Sans SC',sans-serif;margin-top:39px;color:var(--ink-light)}
.ip-learning .ip-scene{left:610px;top:225px;width:1210px;height:681px}
.ip-judgment .ip-scene{left:100px;top:215px;width:1210px;height:705px}
.ip-judgment .ip-copy{position:absolute;left:1360px;top:265px;width:455px}
.ip-judgment .ip-lead{font:900 58px/1.5 'Noto Serif SC',serif;letter-spacing:0;color:var(--blue);margin-top:33px;white-space:nowrap}
.ip-judgment .ip-conclusion{font:900 106px/1.36 'Noto Serif SC',serif;color:var(--ink);letter-spacing:0;margin-top:16px}
.ip-judgment .ip-conclusion span{display:inline-block;position:relative;isolation:isolate}
.ip-judgment .ip-conclusion span::after{content:'';position:absolute;left:0;right:0;bottom:11px;height:40px;background:var(--yellow);z-index:-1}
.ip-judgment .ip-support{font:400 28px/1.8 'Noto Sans SC',sans-serif;color:var(--ink-light);margin-top:42px}
/* The source artwork stays white, as required by bornforthis-illustrations.
   This is an intentional artwork surface, not a replacement brand background. */
'''

SLIDE2 = '''
<section class="slide" aria-label="把学到的，变成做出来的">
 <div class="ip-canvas ip-learning">
  <header class="j-header"><span class="j-brand">Brclio</span><span class="j-context">公开学习与作品</span></header>
  <div class="ip-copy">
   <p class="ip-scene-kicker"><span class="j-red-mark" aria-hidden="true"></span>从学习，到作品</p>
   <h2><span>把学到的，</span><span>变成</span><strong>做出来的。</strong></h2>
   <p class="ip-support">输出，才让能力被看见。</p>
  </div>
  <figure class="ip-scene"><img src="{{SCENE1}}" alt="Bornforthis 把学习笔记折成可下水的纸船，用亲手做出的作品检验学习。"></figure>
  <footer class="j-footer"><span>Learn. Build. Teach. Share.</span><span class="j-page">02</span></footer>
  <div class="j-baseband" aria-hidden="true"></div>
 </div>
 <!-- Speaker note: 原稿581—587行强调公开记录、分享和输出，以作品展示能力。 -->
</section>'''

SLIDE3 = '''
<section class="slide" aria-label="AI 给出答案，你负责判断">
 <div class="ip-canvas ip-judgment">
  <header class="j-header"><span class="j-brand">Brclio</span><span class="j-context">批判性思维</span></header>
  <figure class="ip-scene"><img src="{{SCENE2}}" alt="Bornforthis 将 AI 提供的钥匙放到真实锁芯前逐一测试，用实际结果验证答案。"></figure>
  <div class="ip-copy">
   <p class="ip-scene-kicker"><span class="j-red-mark" aria-hidden="true"></span>判断与验证</p>
   <h2 class="ip-lead">AI 给出答案，</h2>
   <p class="ip-conclusion">你负责<br><span>判断。</span></p>
   <p class="ip-support">做什么、为什么做、<br>做得对不对。</p>
  </div>
  <footer class="j-footer"><span>Brclio · AI悦创</span><span class="j-page">03</span></footer>
  <div class="j-baseband" aria-hidden="true"></div>
 </div>
 <!-- Speaker note: 原稿595—615行要求追问、说明操作与结果，并在修改后实际验证。 -->
</section>'''

class TextCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)

def extra_font(family, text):
    """Add only the new text's unicode ranges; retain all existing embedded faces."""
    query = urllib.parse.urlencode({'family':family,'text':text,'display':'swap'})
    css = urllib.request.urlopen('https://fonts.googleapis.com/css2?' + query,timeout=40).read().decode()
    def embed(m):
        data = urllib.request.urlopen(m.group(1),timeout=40).read()
        return 'url(data:font/woff2;base64,' + base64.b64encode(data).decode() + ')'
    css = re.sub(r'url\((https://[^)]+)\)',embed,css)
    ranges = ','.join(f'U+{ord(c):X}' for c in text if not c.isspace())
    css = re.sub(r'(@font-face\s*\{)(.*?)(\})',lambda m:m.group(1)+m.group(2)+'\n unicode-range:'+ranges+';\n'+m.group(3),css,flags=re.S)
    return css

def fonts():
    collector=TextCollector()
    collector.feed(SLIDE2 + SLIDE3)
    chars=''.join(sorted(set(''.join(collector.parts))))
    digest=hashlib.sha256(chars.encode()).hexdigest()[:12]
    cache=OUT / ('extra-fonts-'+digest+'.css')
    if not cache.exists():
        families=['Noto Serif SC:wght@900','Noto Sans SC:wght@400','Noto Sans SC:wght@700']
        with ThreadPoolExecutor(max_workers=3) as pool:
            css='\n'.join(pool.map(lambda family:extra_font(family,chars),families))
        cache.write_text(css)
    return cache.read_text()

def data_uri(path):
    return 'data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode()

def main():
    OUT.mkdir(exist_ok=True)
    extra=fonts()
    if '--prepare-fonts' in sys.argv:
        print('Supplemental fonts ready; existing J font faces are retained.')
        return
    missing=[str(IMAGES/name) for name in SCENES if not (IMAGES/name).is_file()]
    if missing:
        raise SystemExit('Awaiting scene illustrations:\n'+'\n'.join(missing))
    source=SOURCE.read_text()
    cover=re.search(r'<section class="slide\b.*?</section>',source,re.S).group()
    pages=cover+SLIDE2.replace('{{SCENE1}}',data_uri(IMAGES/SCENES[0]))+SLIDE3.replace('{{SCENE2}}',data_uri(IMAGES/SCENES[1]))
    html=re.sub(r'(<main class="deck-stage">).*?(</main>)',lambda m:m.group(1)+pages+m.group(2),source,flags=re.S)
    html=html.replace('</style>','\n'+extra+'\n'+CSS+'\n</style>',1)
    html=re.sub(r'<title>.*?</title>','<title>AI 浪潮下｜Brclio 场景讲座样稿</title>',html,count=1,flags=re.S)
    html=html.replace('</body>','<!-- Scene illustrations: bornforthis-illustrations; original PNGs embedded without cropping or recoloring. -->\n</body>',1)
    # Fail clearly instead of producing a silently broken local artifact.
    assert '{{SCENE' not in html and len(re.findall(r'<section class="slide\b',html))==3
    assert 'object-fit:contain' in html and 'window.presentation=new SlidePresentation();' in html
    TARGET.write_text(html)
    print('Built:',TARGET)
    print('Slides: 3; images embedded intact; original J cover, fonts and navigation retained.')

if __name__=='__main__':
    main()
