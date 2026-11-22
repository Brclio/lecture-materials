import json,re,base64,os,sys
d=os.path.dirname(os.path.abspath(__file__))
t=open(os.path.join(d,'template.html'),encoding='utf-8').read()
assets=json.load(open(os.path.join(d,'assets.json')))
# new assets from files: {{F:name.ext}}
def f(m):
    p=os.path.join(d,'new',m.group(1))
    ext=p.rsplit('.',1)[1].lower()
    mime={'png':'image/png','jpg':'image/jpeg','jpeg':'image/jpeg','webp':'image/webp','svg':'image/svg+xml','woff2':'font/woff2'}[ext]
    return f"data:{mime};base64,"+base64.b64encode(open(p,'rb').read()).decode()
t=re.sub(r'\{\{F:([^}]+)\}\}',f,t)
t=re.sub(r'\{\{(A[0-9a-f]{8})\}\}',lambda m:assets[m.group(1)],t)
out=os.path.join(os.path.dirname(d),'厦门工学院·AI浪潮下，如何学习与创造.html')
open(out,'w',encoding='utf-8').write(t)
print('built',len(t))
