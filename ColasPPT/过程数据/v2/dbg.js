(()=>{const S=[...document.querySelectorAll('section.slide')];const cur=S.find(s=>!s.hidden);const out={};
[4,5,11,12,20,27].forEach(n=>{const s=S[n-1];S.forEach(x=>x.hidden=true);s.hidden=false;const sb=s.getBoundingClientRect();
let best=[];s.querySelectorAll('*').forEach(e=>{const b=e.getBoundingClientRect();if(b.bottom>sb.bottom+1||b.right>sb.right+1)best.push([e.tagName+'.'+(e.className.baseVal??e.className),Math.round(b.bottom-sb.bottom),Math.round(b.right-sb.right)])});out[n]=best.slice(0,6);});
S.forEach(x=>x.hidden=true);cur.hidden=false;return JSON.stringify(out)})()
