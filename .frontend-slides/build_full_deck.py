"""Build the complete lecture from audited manuscript data and the approved IP sample.

Layout source: Brclio template-landing -> approved brand J -> IP scene preview.
The deck is a self-contained 1920x1080 presentation; originals are not modified.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from html import escape
import base64, hashlib, io, json, re, urllib.parse, urllib.request
import qrcode, qrcode.image.svg

ROOT=Path(__file__).parent
WORK=ROOT.parent
OUT=WORK/'厦门工学院-AI浪潮下的学习与创造.html'
SOURCE=Path('/Users/huangjiabao/bornforthis.cn/docs/Books/06-publishing-and-speaking/01-xiamen-institute-of-technology-guide.assets')
BRAND=Path('/Users/huangjiabao/.codex/skills/brclio-design-system/assets')
IP=WORK/'assets/xiamen-ai-lecture-illustrations'
DATA=json.loads((ROOT/'slides-final.json').read_text())
FONTDIR=ROOT/'full-fonts'
FONTDIR.mkdir(exist_ok=True)
def esc(x):return escape(str(x),quote=True)
def txt(x):return esc(x).replace('\n','<br>')
def edit(tag,text,key,cls=''):return f'<{tag} data-edit="{key}" class="{cls}">{txt(text)}</{tag}>'
def uri(p):
 mime='image/jpeg' if p.suffix.lower() in ['.jpg','.jpeg'] else 'image/png'
 return 'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
def image(p,alt,cls=''):return f'<img class="{cls}" src="{uri(p)}" alt="{esc(alt)}">'
def qr(url):
 obj=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,border=4)
 obj.add_data(url);obj.make(fit=True)
 f=io.BytesIO();obj.make_image(image_factory=qrcode.image.svg.SvgPathImage).save(f)
 return re.sub(r'<\?xml[^>]*>','',f.getvalue().decode())
def links(s):
 return ''.join(f'<a href="{esc(l["url"])}" target="_blank" rel="noopener noreferrer">{esc(l["label"])} ↗</a>' for l in s.get('links',[])[:2])
def chrome(s,resource=False):
 footer=links(s) if not resource and s.get('links') else 'Learn. Build. Teach. Share.'
 return f'<header class="j-header"><span class="j-brand">Brclio</span><span class="j-context">{esc(s["section"])}</span></header><footer class="j-footer"><div class="footer-links">{footer}</div><span class="j-page">{s["id"]:02d} / {len(DATA):02d}</span></footer><div class="j-baseband" aria-hidden="true"></div>'
def heading(s,title=None,kicker=None):
 breaks={8:'经营“自己”\n这家公司',15:'学 Python，\n先练逻辑',22:'我看重的是：\n更容易开始',24:'让工具，\n服务你的任务',42:'先学会：\n记录、版本与表达',46:'进阶：\n把模型带到本地'}
 title=title or breaks.get(s['id'],s['title']);cl='tight' if len(title.replace('\n',''))>27 else 'long' if len(title.replace('\n',''))>22 else ''
 k=kicker if kicker is not None else s.get('kicker','')
 title_html=edit('h2',title,'title',cl)
 if s['id'] in [16,32,41]:
  parts=txt(title).rsplit('<br>',1)
  highlighted=(parts[0]+'<br>' if len(parts)>1 else '')+'<span class="headline">'+parts[-1]+'</span>'
  title_html=f'<h2 data-edit="title" class="{cl}">{highlighted}</h2>'
 return '<div class="slide-heading enter">'+(edit('p',k,'kicker','eyebrow') if k else '')+title_html+'</div>'
def point(p,i,kind='point',step=None):
 a=f' data-step="{step}"' if step else ''
 return f'<article class="{kind}"{a}><span class="point-num" aria-hidden="true">{i+1:02d}</span><div>'+edit('h3',re.sub(r'^\d+\s+','',p['label']),f'label-{i}')+edit('p',p['body'],f'body-{i}')+'</div></article>'
def section(s,content,classes=''):
 cls='slide '+classes+(' has-kicker' if s.get('kicker') else '')+(' multiline' if '\n' in s['title'] else '')
 notes=s['notes']+'\n\n'+('资料：\n'+'\n'.join(l['label']+' '+l['url'] for l in s.get('links',[])) if s.get('links') else '')
 return f'<!-- === SLIDE {s["id"]:02d}: {esc(s["title"].replace(chr(10)," "))} | Source {esc(s["source_lines"])} === --><section class="{cls}" data-id="{s["id"]:02d}" data-section="{esc(s["section"])}" data-title="{esc(s["title"].replace(chr(10)," "))}" aria-label="第{s["id"]}页 {esc(s["title"].replace(chr(10)," "))}">{content}<aside class="speaker-notes" hidden>{esc(notes)}</aside></section>'

def render(s):
 i=s['id'];typ=s['type'];p=s['points'];base=chrome(s,typ=='resources')
 if i==1:
  c=(ROOT/'brand-j/slide-1.html').read_text().replace('{{CHARACTER}}',uri(BRAND/'character.png'))
  c=c.replace('<h1>','<h1 data-edit="title">').replace('<p class="j-subtitle">','<p data-edit="subtitle" class="j-subtitle">').replace('<span class="j-page">01</span>','<span class="j-page">01 / 50</span>')
  return section(s,c,'cover')
 if i in [16,32,33,41]:
  art={16:('01-learning-to-work.png','把学到的，\n变成\n做出来的。','STEP 04 · Vibe Coding','从自己的需要出发，\n做一个真正想用的小项目。'),32:('03-public-learning.png','别再偷偷学。','Learn in Public','记录 → 分享 → 作品\n用输出，倒逼输入。'),33:('02-judge-ai-answers.png','AI 给出答案，\n你负责判断。','判断与验证','做什么、为什么做、\n做得对不对。'),41:('04-feedback-improvement.png','做内容，\n也做作品。','Creator × Builder','接触真实需要，\n让反馈推动下一次改进。')}
  name,title,kicker,caption=art[i]
  h=heading(s,title,kicker).replace('</div>',edit('p',caption,'caption','ip-caption')+'</div>')
  if i==16:h+='<div class="ip-idea-strip">'+''.join(edit('p',q['label'],f'idea-{n}') for n,q in enumerate(p))+'</div>'
  if i==33:h='<div class="slide-heading enter">'+edit('p','判断与验证','kicker','eyebrow')+edit('p','AI 给出答案，','lead','ip-lead')+'<h2 data-edit="title">你负责<br><span class="headline">判断。</span></h2>'+edit('p',caption,'caption','ip-caption')+'</div>'
  return section(s,base+h+'<figure class="ip-art enter">'+image(IP/name,caption)+'</figure>','ip'+(' reverse' if i==33 else ''))
 if typ=='resources':
  cards=[]
  for n,l in enumerate(s['links']):
   q=p[n] if n<len(p) else {'label':l['label'],'body':''}
   domain=urllib.parse.urlparse(l['url']).netloc
   cards.append('<article class="resource-item"><a class="qr" href="'+esc(l['url'])+'" target="_blank" rel="noopener noreferrer" aria-label="打开'+esc(l['label'])+'">'+qr(l['url'])+'</a><div>'+edit('h3',q['label'],f'label-{n}')+edit('p',q['body'],f'body-{n}')+f'<a class="site-label" href="{esc(l["url"])}" target="_blank" rel="noopener noreferrer">{esc(domain)} ↗</a></div></article>')
  return section(s,base+heading(s)+'<div class="stage-body resource-grid enter '+('two' if len(cards)==2 else '')+'">'+''.join(cards)+'</div>','resources')
 if i==5:
  c=base+heading(s)+image(BRAND/'avatar.png','Brclio 的手绘头像','profile-art enter')+'<div class="profile-copy enter">'
  c+=''.join('<article>'+edit('h3',q['label'],f'label-{n}')+edit('p',q['body'],f'body-{n}')+'</article>' for n,q in enumerate(p))+'</div><p class="profile-signature">Stay curious.<br>Keep building.</p>'
  return section(s,c,'profile')
 if i==6:
  c=base+heading(s)+'<div class="stage-body route-grid enter">'
  for n,q in enumerate(p):
   c+=point(q,n,'route-item',n//2 if n//2 else None)
  return section(s,c+'</div>','route')
 if i==11:
  c=base+heading(s)+'''<div class="resume-demo" data-toggle-group="resume"><div class="resume-tabs" role="group" aria-label="比较两种简历呈现方式"><button data-toggle-target="resume-before" aria-pressed="true">只有描述</button><button data-toggle-target="resume-after" aria-pressed="false">展示作品</button></div><div id="resume-before" class="resume-panel"><div class="resume-sheet"><h3>经历写了很多</h3><div class="resume-line"></div><div class="resume-line"></div><div class="resume-line"></div><div class="resume-line"></div><div class="resume-line"></div></div><div class="resume-view"><h3 data-edit="before-title">具体的成品，在哪里？</h3><p data-edit="before-body">只有文字描述，<br>仍然很难判断实际能力。</p></div></div><div id="resume-after" class="resume-panel" hidden><div class="resume-sheet"><h3>精选项目与直接入口</h3><div class="resume-project"><div class="project-tile">作品<br>预览</div><div class="project-labels">项目背景<br>我的贡献<br>可打开的作品链接</div></div></div><div class="resume-view"><h3 data-edit="after-title">让成品替你说话。</h3><p data-edit="after-body">说清背景，展示成果。<br>有作品，也要精简呈现。</p></div></div></div>'''
  return section(s,c,'resume')
 if i==18:
  c=base+heading(s)+image(SOURCE/s['image'],'讲者的 B 站视频作品墙，展示专业设计与 AI 结合的案例','works-image enter')+'<div class="works-copy">'
  c+=''.join('<article>'+edit('h3',q['label'],f'label-{n}')+edit('p',q['body'],f'body-{n}')+'</article>' for n,q in enumerate(p))+'</div>'
  return section(s,c,'works')
 if i==50:
  c=base+heading(s,'从你的第一个\n问题开始。','谢谢大家')+'<div class="closing-copy">'+edit('p','同学交流：学习计划 · 技术 · AI · 简历','students')+edit('p','学校合作：AI · 编程 · Vibe Coding','school')+'</div><div class="closing-codes"><figure>'+image(SOURCE/'微信二维码.JPG','讲者微信好友二维码','wechat-card')+'<figcaption>微信 · 交流与咨询</figcaption></figure><figure>'+image(SOURCE/'公众号：AI 悦创，二维码.jpg','AI 悦创公众号二维码','public-card')+'<figcaption>公众号 · AI 悦创</figcaption></figure></div><p class="closing-hint">Stay curious. Keep building.</p>'
  return section(s,c,'closing')
 if typ=='statement':
  quote='真正聪明的人，\n都坚信长期主义。' if i==31 else s.get('quote',s['title']);plain=quote.replace('\n','');cl='small' if len(plain)>26 else 'medium' if len(plain)>20 else ''
  support=''
  if i==10:support='让人直接看到，你能解决什么问题。'
  elif i==26:support='试着讲给一个不熟悉它的人听。'
  elif i==28:support='第一次接触的人能进入问题，已有经验的人也能获得新的理解。'
  elif i==31:support='一次次兑现价值，才会积累持续的信任。'
  c=base+heading(s)+'<span class="quote-symbol" aria-hidden="true">“</span><div class="statement-body enter">'+edit('p',quote,'quote','big-quote '+cl)+(edit('p',support,'support','quote-support') if support else '')+'</div>'
  return section(s,c,'statement'+(' blue-pause' if i==31 else ''))
 if typ=='comparison':
  c=base+heading(s)+'<div class="stage-body comparison-grid enter">'
  for n,q in enumerate(p):
   c+='<article class="compare-panel"'+(' data-step="1"' if i==21 and n==1 else '')+'><span class="compare-tag">'+('01' if n==0 else '02')+'</span>'+edit('h3',q['label'],f'label-{n}')
   if i==21:c+='<div class="memory-pools">'+('<span class="memory-block">32 GB 内存</span><span class="memory-block small">8 GB 显存</span>' if n==0 else '<span class="memory-block">CPU ＋ GPU 共用</span>')+'</div>'
   c+=edit('p',q['body'],f'body-{n}')+'</article>'
  c+='</div>'
  if s.get('quote'):c+=edit('p',s['quote'],'quote','aside-note')
  return section(s,c,'comparison'+(' has-quote' if s.get('quote') else '')+(' memory-page' if i==21 else ''))
 if typ=='quartet':
  return section(s,base+heading(s)+'<div class="stage-body four-grid enter">'+''.join(point(q,n) for n,q in enumerate(p))+'</div>','quartet paper-dark')
 # Alternate wide columns with offset editorial rows, preserving the sample grammar.
 isrows=i in [8,13,15,20,22,24,35,42,44,46]
 process=typ=='process'
 progressive=i in [4,19,38,48]
 c=base+heading(s)+'<div class="stage-body '+('' if isrows else 'triplet')+(' with-flow' if process else '')+' enter">'
 for n,q in enumerate(p):
  if i==40 and n==1:q={**q,'body':'判断与品味：知道取舍'}
  if i==39:
   h=point(q,n).replace('</article>','<span class="shift-label" data-step="1">'+['更难：理解用户','更容易：借助 AI','更难：争取注意力'][n]+'</span></article>')
  else:h=point(q,n,'row-point' if isrows else 'point',n if progressive and n else None)
  c+=h
 c+='</div>'
 if i==34:c+='<div class="prompt-example" data-step="1" data-edit="example">例如：点击“保存” → 页面没有变化 → 我希望内容保存成功。<br><strong>再追问：</strong>问题在哪？改哪里？怎样验证？</div>'
 if i==19:c+='<p class="aside-note" data-edit="skill-boundary">固定流程适合沉淀为 Skills；发散探索时，保留试错空间。</p>'
 return section(s,c,('rows' if isrows else 'process' if process else 'triad')+(' question' if i==34 else '')+(' builder-shift' if i==39 else '')+(' paper-dark' if i in [4,17,38,48] else ''))

def get_font(task):
 family,chars=task
 digest=hashlib.sha256((family+chars).encode()).hexdigest()[:20]
 cache=FONTDIR/(digest+'.css')
 if cache.exists():return cache.read_text()
 query=urllib.parse.urlencode({'family':family,'text':chars,'display':'swap'})
 css=urllib.request.urlopen('https://fonts.googleapis.com/css2?'+query,timeout=60).read().decode()
 def rep(m):
  data=urllib.request.urlopen(m.group(1),timeout=60).read()
  return 'url(data:font/woff2;base64,'+base64.b64encode(data).decode()+')'
 css=re.sub(r'url\((https://[^)]+)\)',rep,css)
 ranges=','.join('U+%X'%ord(c) for c in chars)
 css=css.replace('}',f' unicode-range:{ranges};\n}}')
 cache.write_text(css)
 return css

def main():
 pages='\n'.join(render(s) for s in DATA)
 visible=re.sub(r'<[^>]+>','',pages)
 ui='上一页下一页目录备注全屏编辑保存讲者关闭搜索页面计时暂停重新开始已自动保存到本机全部显示步骤浏览点击返回退出文本已保存下载讲座当前下一张章节导航请输入关键词演讲者视图快捷键重置取消完成'
 chars=''.join(sorted(set(visible+ui+'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ←→·—，。？！：；（）/')))
 chunks=[chars[i:i+260] for i in range(0,len(chars),260)]
 tasks=[(fam,c) for fam in ['Noto Serif SC:wght@900','Noto Sans SC:wght@400','Noto Sans SC:wght@700'] for c in chunks]
 with ThreadPoolExecutor(max_workers=8) as pool:fonts='\n'.join(pool.map(get_font,tasks))
 latin=(ROOT/'brand-fonts.css').read_text()
 fonts+='\n'+'\n'.join(b for b in re.findall(r'@font-face\s*\{.*?\}',latin,re.S) if 'Fraunces' in b or 'Caveat' in b)
 template=(ROOT/'brand-template-base.html').read_text()
 css=Path('/Users/huangjiabao/.codex/skills/frontend-slides/viewport-base.css').read_text()+'\n'+(ROOT/'brand-j/style.css').read_text()+'\n'+(ROOT/'full-layout.css').read_text()+'\n'+(ROOT/'full-controls.css').read_text()
 js=(ROOT/'full-runtime.js').read_text()
 html=re.sub(r'<link[^>]*>','',template)
 html=re.sub(r'<title>.*?</title>','<title>AI 浪潮下，我们应该如何应对与学习｜Brclio · AI悦创</title><meta name="license" content="CC BY-NC-SA 4.0"><link rel="icon" href="data:,">',html,flags=re.S)
 html=re.sub(r'<style>.*?</style>',lambda m:'<style>\n'+fonts+'\n'+css+'\n</style>',html,flags=re.S)
 body='<body data-deck-id="brclio-xiamen-ai-lecture-v1"><div class="deck-viewport"><main class="deck-stage">'+pages+'</main></div><script>\n'+js+'\n</script><!-- © 2026 Brclio | CC BY-NC-SA 4.0. Artwork: Bornforthis. Built from the approved J/IP sample. --></body>'
 html=re.sub(r'<body[^>]*>.*?</body>',lambda m:body,html,flags=re.S)
 assert len(re.findall(r'<section class="slide\b',html))==len(DATA)
 assert '{{' not in html
 OUT.write_text(html)
 (ROOT/'full-deck-manifest.json').write_text(json.dumps({'slides':len(DATA),'file':str(OUT),'characters':len(chars),'step_pages':[4,6,19,21,34,38,39,48],'interactive_comparison':[11],'ip_pages':[16,32,33,41]},ensure_ascii=False,indent=2))
 print(f'Built {len(DATA)} slides: {OUT} ({OUT.stat().st_size/1024/1024:.2f} MiB)')
if __name__=='__main__':main()
