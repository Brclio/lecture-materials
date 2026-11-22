import re,os
d=os.path.dirname(os.path.abspath(__file__))
R=lambda n:open(os.path.join(d,n),encoding='utf-8').read()
head,orig,tail,src,css,icons=R('head.html'),R('slides.orig.html'),R('tail.html'),R('slides.src.html'),R('extra.css'),R('icons.html')
secs=re.findall(r'<section (?:id="first-cover" )?class="slide.*?</aside></section>',orig,re.S)
cover=secs[0]; comic=secs[22]; b3=secs[26]
b3=b3.replace('<span class="builder-stage-label">第一步</span>','<span class="builder-stage-label">第一步<span class="lv">AI 时代 · 更难</span></span>')
b3=b3.replace('<span class="builder-stage-label">第二步</span>','<span class="builder-stage-label">第二步<span class="lv easy">AI 时代 · 变简单</span></span>')
b3=b3.replace('<span class="builder-stage-label">第三步</span>','<span class="builder-stage-label">第三步<span class="lv">AI 时代 · 更难</span></span>')
b3=b3.replace('<strong class="builder-stage-title">让人来用</strong>','<strong class="builder-stage-title">把它推广出去</strong>').replace('把成品带回给那个人，看他愿不愿意再用一次。','让人去 Care，让人去用它。')
b3=b3.replace('data-chapter="Q7 · Builder 的三种能力"','data-chapter="Q7 · Builder 的三种能力"')
comic=comic.replace('data-chapter="Q5 · 长期积累的回报"','data-chapter="Q5 · 长期主义"')
src=src.replace('<!--COVER-->',cover).replace('<!--COMIC-->',comic).replace('<!--BUILDER3-->',b3)
parts=re.findall(r'<section .*?</section>',src,re.S)
n=len(parts); out=[]
for i,p in enumerate(parts):
    p=re.sub(r'^<section (id="first-cover" )?class="slide[^"]*"[^>]*>','',p,count=0) if False else p
    m=re.match(r'<section ([^>]*)>',p); attrs=m.group(1)
    title=re.search(r'data-title="([^"]*)"',attrs).group(1)
    attrs=re.sub(r'\s*(hidden|aria-label="[^"]*"|data-print="[^"]*")','',attrs)
    attrs=re.sub(r'class="slide([^"]*)"',lambda m:'class="slide'+m.group(1).replace(' is-active','')+(' is-active' if i==0 else '')+'"',attrs)
    extra=('' if i==0 else ' hidden')+f' aria-label="第 {i+1} 页，{title}" data-print="Brclio · 厦门工学院　　{i+1:02d} / {n}"'
    attrs=re.sub(r'(class="[^"]*")',r'\1'+extra,attrs,count=1)
    out.append('<section '+attrs+'>'+p[m.end():])
head=head.replace('{{A851d3630}}','{{F:lecture-song.woff2}}')
head=head.replace('</style></head>','\n'+css+'\n</style></head>',1)
head=head.replace('<main id="stage"',icons+'<main id="stage"',1)
open(os.path.join(d,'template.html'),'w',encoding='utf-8').write(head+'\n'.join(out)+'\n'+tail)
print('slides',n)
