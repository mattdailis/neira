import{t as q,h as z}from"./index.tVoUV_k3.js";import{r as B}from"./scheduler.B7PGr4mf.js";function G(n){return(n==null?void 0:n.length)!==void 0?n:Array.from(n)}function C(n,d){z(n,1,1,()=>{d.delete(n.key)})}function H(n,d){n.f(),C(n,d)}function I(n,d,x,D,S,g,h,A,p,j,u,k){let i=n.length,f=g.length,c=i;const w={};for(;c--;)w[n[c].key]=c;const o=[],a=new Map,m=new Map,_=[];for(c=f;c--;){const e=k(S,g,c),s=x(e);let t=h.get(s);t?_.push(()=>t.p(e,d)):(t=j(s,e),t.c()),a.set(s,o[c]=t),s in w&&m.set(s,Math.abs(c-w[s]))}const M=new Set,v=new Set;function y(e){q(e,1),e.m(A,u),h.set(e.key,e),u=e.first,f--}for(;i&&f;){const e=o[f-1],s=n[i-1],t=e.key,l=s.key;e===s?(u=e.first,i--,f--):a.has(l)?!h.has(t)||M.has(t)?y(e):v.has(l)?i--:m.get(t)>m.get(l)?(v.add(t),y(e)):(M.add(l),i--):(p(s,h),i--)}for(;i--;){const e=n[i];a.has(e.key)||p(e,h)}for(;f;)y(o[f-1]);return B(_),o}export{G as e,H as f,I as u};
