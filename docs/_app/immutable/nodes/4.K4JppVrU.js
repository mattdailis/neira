import{n as _e,e as wt,u as Be,i as ot,s as it,v as Le,w as He,x as Ve,y as Ae,r as rt,z as kt,b as at,A as bt,B as Ce,d as ft}from"../chunks/scheduler.BlEyUcvO.js";import{C as yt,D as Et,E as Ct,F as Mt,S as ct,i as ut,e as I,s as F,j as T,c as O,k as q,a as G,l as S,f as b,g as pe,b as U,q as de,d as $,m as i,B as ue,G as Dt,H as Tt,n as te,t as me,h as we,I as St,v as It,w as Ot,x as Bt,p as qe,A as Me,y as Lt,J as dt,K as ht,L as Re,r as Ue}from"../chunks/index.CaHyJZoe.js";import{e as fe,u as Ne,f as Pe}from"../chunks/each.BDePSiCe.js";function _t(l,e,t,n){if(!e)return _e;const c=l.getBoundingClientRect();if(e.left===c.left&&e.right===c.right&&e.top===c.top&&e.bottom===c.bottom)return _e;const{delay:_=0,duration:d=300,easing:v=wt,start:a=yt()+_,end:p=a+d,tick:k=_e,css:m}=t(l,{from:e,to:c},n);let C=!0,g=!1,h;function o(){m&&(h=Ct(l,0,1,d,_,v,m)),_||(g=!0)}function f(){m&&Mt(l,h),C=!1}return Et(H=>{if(!g&&H>=a&&(g=!0),g&&H>=p&&(k(1,0),f()),!C)return!1;if(g){const u=H-a,r=0+1*v(u/d);k(r,1-r)}return!0}),o(),k(0,1),f}function pt(l){const e=getComputedStyle(l);if(e.position!=="absolute"&&e.position!=="fixed"){const{width:t,height:n}=e,c=l.getBoundingClientRect();l.style.position="absolute",l.style.width=t,l.style.height=n,De(l,c)}}function De(l,e){const t=l.getBoundingClientRect();if(e.left!==t.left||e.top!==t.top){const n=getComputedStyle(l),c=n.transform==="none"?"":n.transform;l.style.transform=`${c} translate(${e.left-t.left}px, ${e.top-t.top}px)`}}function vt(l){const e=l-1;return e*e*e+1}function Ht(l){return--l*l*l*l*l+1}function Vt({fallback:l,...e}){const t=new Map,n=new Map;function c(d,v,a){const{delay:p=0,duration:k=R=>Math.sqrt(R)*30,easing:m=vt}=Be(Be({},e),a),C=d.getBoundingClientRect(),g=v.getBoundingClientRect(),h=C.left-g.left,o=C.top-g.top,f=C.width/g.width,H=C.height/g.height,u=Math.sqrt(h*h+o*o),r=getComputedStyle(v),M=r.transform==="none"?"":r.transform,B=+r.opacity;return{delay:p,duration:ot(k)?k(u):k,easing:m,css:(R,x)=>`
				opacity: ${R*B};
				transform-origin: top left;
				transform: ${M} translate(${x*h}px,${x*o}px) scale(${R+(1-R)*f}, ${R+(1-R)*H});
			`}}function _(d,v,a){return(p,k)=>(d.set(k.key,p),()=>{if(v.has(k.key)){const m=v.get(k.key);return v.delete(k.key),c(m,p,k)}return d.delete(k.key),l&&l(p,k,a)})}return[_(n,t,!1),_(t,n,!0)]}function gt(l,{from:e,to:t},n={}){const c=getComputedStyle(l),_=c.transform==="none"?"":c.transform,[d,v]=c.transformOrigin.split(" ").map(parseFloat),a=e.left+e.width*d/t.width-(t.left+d),p=e.top+e.height*v/t.height-(t.top+v),{delay:k=0,duration:m=g=>Math.sqrt(g)*120,easing:C=vt}=n;return{delay:k,duration:ot(m)?m(Math.sqrt(a*a+p*p)):m,easing:C,css:(g,h)=>{const o=h*a,f=h*p,H=g+h*e.width/t.width,u=g+h*e.height/t.height;return`transform: ${_} translate(${o}px, ${f}px) scale(${H}, ${u});`}}}const At=l=>({}),je=l=>({});function qt(l){let e,t,n,c,_,d,v,a,p,k,m,C,g,h,o,f="close modal",H,u,r="apply changes",M,B,R;const x=l[5].header,A=Le(x,l,l[4],je),J=l[5].default,Y=Le(J,l,l[4],null);return{c(){e=I("dialog"),t=I("div"),A&&A.c(),n=F(),c=I("hr"),_=F(),d=I("p"),v=I("b"),a=T(l[3]),k=F(),Y&&Y.c(),m=F(),C=I("hr"),g=F(),h=I("div"),o=I("button"),o.textContent=f,H=F(),u=I("button"),u.textContent=r,this.h()},l(L){e=O(L,"DIALOG",{class:!0});var W=q(e);t=O(W,"DIV",{class:!0});var K=q(t);A&&A.l(K),n=G(K),c=O(K,"HR",{}),_=G(K),d=O(K,"P",{});var ne=q(d);v=O(ne,"B",{});var ie=q(v);a=S(ie,l[3]),ie.forEach(b),ne.forEach(b),k=G(K),Y&&Y.l(K),m=G(K),C=O(K,"HR",{}),g=G(K),h=O(K,"DIV",{style:!0});var le=q(h);o=O(le,"BUTTON",{class:!0,"data-svelte-h":!0}),pe(o)!=="svelte-15i90tf"&&(o.textContent=f),H=G(le),u=O(le,"BUTTON",{class:!0,"data-svelte-h":!0}),pe(u)!=="svelte-l6i33e"&&(u.textContent=r),le.forEach(b),K.forEach(b),W.forEach(b),this.h()},h(){d.hidden=p=l[3]==="",o.autofocus=!0,U(o,"class","svelte-19dligb"),u.autofocus=!0,U(u,"class","svelte-19dligb"),de(h,"display","flex"),de(h,"justify-content","space-between"),U(t,"class","svelte-19dligb"),U(e,"class","svelte-19dligb")},m(L,W){$(L,e,W),i(e,t),A&&A.m(t,null),i(t,n),i(t,c),i(t,_),i(t,d),i(d,v),i(v,a),i(t,k),Y&&Y.m(t,null),i(t,m),i(t,C),i(t,g),i(t,h),i(h,o),i(h,H),i(h,u),l[9](e),M=!0,u.focus(),B||(R=[ue(o,"click",l[7]),ue(u,"click",l[8]),ue(t,"click",Dt(l[6])),ue(e,"close",l[10]),ue(e,"click",Tt(l[11]))],B=!0)},p(L,[W]){A&&A.p&&(!M||W&16)&&He(A,x,L,L[4],M?Ae(x,L[4],W,At):Ve(L[4]),je),(!M||W&8)&&te(a,L[3]),(!M||W&8&&p!==(p=L[3]===""))&&(d.hidden=p),Y&&Y.p&&(!M||W&16)&&He(Y,J,L,L[4],M?Ae(J,L[4],W,null):Ve(L[4]),null)},i(L){M||(me(A,L),me(Y,L),M=!0)},o(L){we(A,L),we(Y,L),M=!1},d(L){L&&b(e),A&&A.d(L),Y&&Y.d(L),l[9](null),B=!1,rt(R)}}}function Rt(l,e,t){let{$$slots:n={},$$scope:c}=e,{showModal:_}=e,{apply:d}=e,v="",a;function p(o){kt.call(this,l,o)}const k=()=>a.close(),m=()=>{const[o,f]=d();o?a.close():t(3,v=f)};function C(o){at[o?"unshift":"push"](()=>{a=o,t(2,a)})}const g=()=>t(0,_=!1),h=()=>a.close();return l.$$set=o=>{"showModal"in o&&t(0,_=o.showModal),"apply"in o&&t(1,d=o.apply),"$$scope"in o&&t(4,c=o.$$scope)},l.$$.update=()=>{l.$$.dirty&5&&a&&_&&(t(3,v=""),a.showModal())},[_,d,a,v,c,n,p,k,m,C,g,h]}class Ut extends ct{constructor(e){super(),ut(this,e,Rt,qt,it,{showModal:0,apply:1})}}function ze(l,e,t,n){let c=[[t,[]]];for(let d=0;d<l;d++){let v=[];for(let[a,p]of c){let k=new Set;for(let m of p)k.add(m[0]),k.add(m[1]);for(let m of Nt(e,a)){let C=m[1];k.has(C)||v.push([C,[...p,m]])}}c=v}let _=[];for(let[d,v]of c)d===n&&new Set(v.map(a=>a[3])).size>1&&_.push(v);return console.log({paths:_}),_}function Nt(l,e){let t=[];for(const n of l)n[0]===e?t.push(n):n[1]===e&&t.push([n[1],n[0],-n[2],n[3],n[4]]);return t}function Fe(l,e,t){const n=l.slice();return n[36]=e[t],n}function Ge(l,e,t){const n=l.slice();return n[39]=e[t],n}function Ke(l,e,t){const n=l.slice();return n[36]=e[t],n}function Je(l,e,t){const n=l.slice();return n[36]=e[t],n}function We(l,e,t){const n=l.slice();return n[46]=e[t],n}function Xe(l,e,t){const n=l.slice();return n[46]=e[t],n}function Ye(l,e){let t,n=e[46].description+"",c,_,d,v,a,p,k=_e,m,C,g;function h(...o){return e[11](e[46],...o)}return{key:l,first:null,c(){t=I("div"),c=T(n),_=F(),this.h()},l(o){t=O(o,"DIV",{class:!0});var f=q(t);c=S(f,n),_=G(f),f.forEach(b),this.h()},h(){U(t,"class",d=Ce("item"+(e[4]&&e[4][0].id==e[46].id?" selected":"")+(e[4].length>1&&e[4][1].id==e[46].id?" secondaryselect":""))+" svelte-1w90mea"),this.first=t},m(o,f){$(o,t,f),i(t,c),i(t,_),m=!0,C||(g=ue(t,"click",h),C=!0)},p(o,f){e=o,(!m||f[0]&4)&&n!==(n=e[46].description+"")&&te(c,n),(!m||f[0]&20&&d!==(d=Ce("item"+(e[4]&&e[4][0].id==e[46].id?" selected":"")+(e[4].length>1&&e[4][1].id==e[46].id?" secondaryselect":""))+" svelte-1w90mea"))&&U(t,"class",d)},r(){p=t.getBoundingClientRect()},f(){pt(t),k(),De(t,p)},a(){k(),k=_t(t,p,gt,{})},i(o){m||(o&&ft(()=>{m&&(a&&a.end(1),v=dt(t,e[7],{key:e[46].id}),v.start())}),m=!0)},o(o){v&&v.invalidate(),o&&(a=ht(t,e[6],{key:e[46].id})),m=!1},d(o){o&&b(t),o&&a&&a.end(),C=!1,g()}}}function Qe(l,e){let t,n=e[3].indexOf(e[46])+1+"",c,_,d=e[46].description+"",v,a,p,k,m,C,g=_e,h,o,f;function H(...u){return e[13](e[46],...u)}return{key:l,first:null,c(){t=I("div"),c=T(n),_=T(`.
						`),v=T(d),a=F(),this.h()},l(u){t=O(u,"DIV",{class:!0});var r=q(t);c=S(r,n),_=S(r,`.
						`),v=S(r,d),a=G(r),r.forEach(b),this.h()},h(){U(t,"class",p=Ce("item"+(e[4]&&e[4][0].id==e[46].id?" selected":"")+(e[4].length>1&&e[4][1].id==e[46].id?" secondaryselect":""))+" svelte-1w90mea"),this.first=t},m(u,r){$(u,t,r),i(t,c),i(t,_),i(t,v),i(t,a),h=!0,o||(f=ue(t,"click",H),o=!0)},p(u,r){e=u,(!h||r[0]&8)&&n!==(n=e[3].indexOf(e[46])+1+"")&&te(c,n),(!h||r[0]&8)&&d!==(d=e[46].description+"")&&te(v,d),(!h||r[0]&24&&p!==(p=Ce("item"+(e[4]&&e[4][0].id==e[46].id?" selected":"")+(e[4].length>1&&e[4][1].id==e[46].id?" secondaryselect":""))+" svelte-1w90mea"))&&U(t,"class",p)},r(){C=t.getBoundingClientRect()},f(){pt(t),g(),De(t,C)},a(){g(),g=_t(t,C,gt,{})},i(u){h||(u&&ft(()=>{h&&(m&&m.end(1),k=dt(t,e[7],{key:e[46].id}),k.start())}),h=!0)},o(u){k&&k.invalidate(),u&&(m=ht(t,e[6],{key:e[46].id})),h=!1},d(u){u&&b(t),u&&m&&m.end(),o=!1,f()}}}function Ze(l){let e,t="<i>No schools have been selected</i>";return{c(){e=I("p"),e.innerHTML=t,this.h()},l(n){e=O(n,"P",{style:!0,"data-svelte-h":!0}),pe(e)!=="svelte-4pzh4c"&&(e.innerHTML=t),this.h()},h(){de(e,"color","gray")},m(n,c){$(n,e,c)},d(n){n&&b(e)}}}function $e(l){let e,t=l[4][0].description+"",n,c,_,d=l[4][0].description+"",v,a,p=l[5].filter(l[14]).length+"",k,m,C=new Set(l[5].filter(l[15]).flatMap(nt)).size-1+"",g,h,o,f,H=fe(l[5].filter(l[16])),u=[];for(let r=0;r<H.length;r+=1)u[r]=xe(Je(l,H,r));return{c(){e=I("h2"),n=T(t),c=F(),_=I("p"),v=T(d),a=T(" has raced "),k=T(p),m=T(" times this season against "),g=T(C),h=T(" unique opponents."),o=F(),f=I("ul");for(let r=0;r<u.length;r+=1)u[r].c();this.h()},l(r){e=O(r,"H2",{class:!0});var M=q(e);n=S(M,t),M.forEach(b),c=G(r),_=O(r,"P",{});var B=q(_);v=S(B,d),a=S(B," has raced "),k=S(B,p),m=S(B," times this season against "),g=S(B,C),h=S(B," unique opponents."),B.forEach(b),o=G(r),f=O(r,"UL",{});var R=q(f);for(let x=0;x<u.length;x+=1)u[x].l(R);R.forEach(b),this.h()},h(){U(e,"class","svelte-1w90mea")},m(r,M){$(r,e,M),i(e,n),$(r,c,M),$(r,_,M),i(_,v),i(_,a),i(_,k),i(_,m),i(_,g),i(_,h),$(r,o,M),$(r,f,M);for(let B=0;B<u.length;B+=1)u[B]&&u[B].m(f,null)},p(r,M){if(M[0]&16&&t!==(t=r[4][0].description+"")&&te(n,t),M[0]&16&&d!==(d=r[4][0].description+"")&&te(v,d),M[0]&16&&p!==(p=r[5].filter(r[14]).length+"")&&te(k,p),M[0]&16&&C!==(C=new Set(r[5].filter(r[15]).flatMap(nt)).size-1+"")&&te(g,C),M[0]&48){H=fe(r[5].filter(r[16]));let B;for(B=0;B<H.length;B+=1){const R=Je(r,H,B);u[B]?u[B].p(R,M):(u[B]=xe(R),u[B].c(),u[B].m(f,null))}for(;B<u.length;B+=1)u[B].d(1);u.length=H.length}},d(r){r&&(b(e),b(c),b(_),b(o),b(f)),Me(u,r)}}}function xe(l){let e,t=l[36][0]+"",n,c,_=l[36][1]+"",d,v,a=l[36][2]+"",p,k,m=l[36][3]+"",C,g,h,o,f,H;return{c(){e=I("li"),n=T(t),c=T(","),d=T(_),v=T(","),p=T(a),k=T(","),C=T(m),g=T(" ("),h=I("a"),o=T("link"),H=T(")"),this.h()},l(u){e=O(u,"LI",{});var r=q(e);n=S(r,t),c=S(r,","),d=S(r,_),v=S(r,","),p=S(r,a),k=S(r,","),C=S(r,m),g=S(r," ("),h=O(r,"A",{href:!0});var M=q(h);o=S(M,"link"),M.forEach(b),H=S(r,")"),r.forEach(b),this.h()},h(){U(h,"href",f=l[36][4])},m(u,r){$(u,e,r),i(e,n),i(e,c),i(e,d),i(e,v),i(e,p),i(e,k),i(e,C),i(e,g),i(e,h),i(h,o),i(e,H)},p(u,r){r[0]&16&&t!==(t=u[36][0]+"")&&te(n,t),r[0]&16&&_!==(_=u[36][1]+"")&&te(d,_),r[0]&16&&a!==(a=u[36][2]+"")&&te(p,a),r[0]&16&&m!==(m=u[36][3]+"")&&te(C,m),r[0]&16&&f!==(f=u[36][4])&&U(h,"href",f)},d(u){u&&b(e)}}}function et(l){let e,t=l[4][0].description+"",n,c,_=l[4][1].description+"",d,v,a,p=l[4][0].description+"",k,m,C=l[4][1].description+"",g,h,o=l[5].filter(l[17]).filter(l[18]).length+"",f,H,u=l[5].filter(l[19]).filter(l[20]).length===1?"":"s",r,M,B,R,x,A,J,Y=l[4][0].description+"",L,W,K=l[4][1].description+"",ne,ie,le,re=fe(l[5].filter(l[21]).filter(l[22])),X=[];for(let w=0;w<re.length;w+=1)X[w]=tt(Ke(l,re,w));let ae=fe(ze(2,l[5],l[4][0].description,l[4][1].description)),ee=[];for(let w=0;w<ae.length;w+=1)ee[w]=lt(Ge(l,ae,w));return{c(){e=I("h2"),n=T(t),c=T(" vs "),d=T(_),v=F(),a=I("p"),k=T(p),m=T(" has raced "),g=T(C),h=F(),f=T(o),H=T(" time"),r=T(u),M=T(" this season."),B=F(),R=I("ul");for(let w=0;w<X.length;w+=1)X[w].c();x=F(),A=I("p"),J=T("Here are the paths of length 2 from "),L=T(Y),W=T(" to "),ne=T(K),ie=F(),le=I("ul");for(let w=0;w<ee.length;w+=1)ee[w].c();this.h()},l(w){e=O(w,"H2",{class:!0});var z=q(e);n=S(z,t),c=S(z," vs "),d=S(z,_),z.forEach(b),v=G(w),a=O(w,"P",{});var s=q(a);k=S(s,p),m=S(s," has raced "),g=S(s,C),h=G(s),f=S(s,o),H=S(s," time"),r=S(s,u),M=S(s," this season."),s.forEach(b),B=G(w),R=O(w,"UL",{});var y=q(R);for(let N=0;N<X.length;N+=1)X[N].l(y);y.forEach(b),x=G(w),A=O(w,"P",{});var V=q(A);J=S(V,"Here are the paths of length 2 from "),L=S(V,Y),W=S(V," to "),ne=S(V,K),V.forEach(b),ie=G(w),le=O(w,"UL",{});var Z=q(le);for(let N=0;N<ee.length;N+=1)ee[N].l(Z);Z.forEach(b),this.h()},h(){U(e,"class","svelte-1w90mea")},m(w,z){$(w,e,z),i(e,n),i(e,c),i(e,d),$(w,v,z),$(w,a,z),i(a,k),i(a,m),i(a,g),i(a,h),i(a,f),i(a,H),i(a,r),i(a,M),$(w,B,z),$(w,R,z);for(let s=0;s<X.length;s+=1)X[s]&&X[s].m(R,null);$(w,x,z),$(w,A,z),i(A,J),i(A,L),i(A,W),i(A,ne),$(w,ie,z),$(w,le,z);for(let s=0;s<ee.length;s+=1)ee[s]&&ee[s].m(le,null)},p(w,z){if(z[0]&16&&t!==(t=w[4][0].description+"")&&te(n,t),z[0]&16&&_!==(_=w[4][1].description+"")&&te(d,_),z[0]&16&&p!==(p=w[4][0].description+"")&&te(k,p),z[0]&16&&C!==(C=w[4][1].description+"")&&te(g,C),z[0]&16&&o!==(o=w[5].filter(w[17]).filter(w[18]).length+"")&&te(f,o),z[0]&16&&u!==(u=w[5].filter(w[19]).filter(w[20]).length===1?"":"s")&&te(r,u),z[0]&48){re=fe(w[5].filter(w[21]).filter(w[22]));let s;for(s=0;s<re.length;s+=1){const y=Ke(w,re,s);X[s]?X[s].p(y,z):(X[s]=tt(y),X[s].c(),X[s].m(R,null))}for(;s<X.length;s+=1)X[s].d(1);X.length=re.length}if(z[0]&16&&Y!==(Y=w[4][0].description+"")&&te(L,Y),z[0]&16&&K!==(K=w[4][1].description+"")&&te(ne,K),z[0]&48){ae=fe(ze(2,w[5],w[4][0].description,w[4][1].description));let s;for(s=0;s<ae.length;s+=1){const y=Ge(w,ae,s);ee[s]?ee[s].p(y,z):(ee[s]=lt(y),ee[s].c(),ee[s].m(le,null))}for(;s<ee.length;s+=1)ee[s].d(1);ee.length=ae.length}},d(w){w&&(b(e),b(v),b(a),b(B),b(R),b(x),b(A),b(ie),b(le)),Me(X,w),Me(ee,w)}}}function tt(l){let e,t=l[36][0]+"",n,c,_=l[36][2]+"",d,v,a=l[36][3]+"",p,k,m,C,g,h;return{c(){e=I("li"),n=T(t),c=T(" won by "),d=T(_),v=T(" seconds on "),p=T(a),k=T(" ("),m=I("a"),C=T("link"),h=T(`)
						`),this.h()},l(o){e=O(o,"LI",{});var f=q(e);n=S(f,t),c=S(f," won by "),d=S(f,_),v=S(f," seconds on "),p=S(f,a),k=S(f," ("),m=O(f,"A",{href:!0});var H=q(m);C=S(H,"link"),H.forEach(b),h=S(f,`)
						`),f.forEach(b),this.h()},h(){U(m,"href",g=l[36][4])},m(o,f){$(o,e,f),i(e,n),i(e,c),i(e,d),i(e,v),i(e,p),i(e,k),i(e,m),i(m,C),i(e,h)},p(o,f){f[0]&16&&t!==(t=o[36][0]+"")&&te(n,t),f[0]&16&&_!==(_=o[36][2]+"")&&te(d,_),f[0]&16&&a!==(a=o[36][3]+"")&&te(p,a),f[0]&16&&g!==(g=o[36][4])&&U(m,"href",g)},d(o){o&&b(e)}}}function lt(l){let e,t=_()+"",n,c;function _(){return l[23](l[39])}return{c(){e=I("li"),n=T(t),c=F()},l(d){e=O(d,"LI",{});var v=q(e);n=S(v,t),c=G(v),v.forEach(b)},m(d,v){$(d,e,v),i(e,n),i(e,c)},p(d,v){l=d,v[0]&16&&t!==(t=_()+"")&&te(n,t)},d(d){d&&b(e)}}}function st(l){let e,t,n=l[36][0]+"",c,_,d,v=l[36][1]+"",a,p,k,m=l[36][2]+"",C,g,h,o=l[36][3]+"",f,H,u,r,M,B,R,x;return{c(){e=I("tr"),t=I("td"),c=T(n),_=F(),d=I("td"),a=T(v),p=F(),k=I("td"),C=T(m),g=F(),h=I("td"),f=T(o),H=F(),u=I("td"),r=T("("),M=I("a"),B=T("link"),R=T(")"),x=F(),this.h()},l(A){e=O(A,"TR",{});var J=q(e);t=O(J,"TD",{class:!0});var Y=q(t);c=S(Y,n),Y.forEach(b),_=G(J),d=O(J,"TD",{class:!0});var L=q(d);a=S(L,v),L.forEach(b),p=G(J),k=O(J,"TD",{class:!0});var W=q(k);C=S(W,m),W.forEach(b),g=G(J),h=O(J,"TD",{class:!0});var K=q(h);f=S(K,o),K.forEach(b),H=G(J),u=O(J,"TD",{class:!0});var ne=q(u);r=S(ne,"("),M=O(ne,"A",{href:!0});var ie=q(M);B=S(ie,"link"),ie.forEach(b),R=S(ne,")"),ne.forEach(b),x=G(J),J.forEach(b),this.h()},h(){U(t,"class","svelte-1w90mea"),U(d,"class","svelte-1w90mea"),U(k,"class","svelte-1w90mea"),U(h,"class","svelte-1w90mea"),U(M,"href",l[36][4]),U(u,"class","svelte-1w90mea")},m(A,J){$(A,e,J),i(e,t),i(t,c),i(e,_),i(e,d),i(d,a),i(e,p),i(e,k),i(k,C),i(e,g),i(e,h),i(h,f),i(e,H),i(e,u),i(u,r),i(u,M),i(M,B),i(u,R),i(e,x)},p:_e,d(A){A&&b(e)}}}function Pt(l){let e,t,n;return{c(){e=I("textarea"),this.h()},l(c){e=O(c,"TEXTAREA",{class:!0}),q(e).forEach(b),this.h()},h(){U(e,"class","modaltextarea svelte-1w90mea")},m(c,_){$(c,e,_),Re(e,l[1]),t||(n=ue(e,"input",l[25]),t=!0)},p(c,_){_[0]&2&&Re(e,c[1])},d(c){c&&b(e),t=!1,n()}}}function jt(l){let e,t="Copy/paste seeding";return{c(){e=I("h2"),e.textContent=t,this.h()},l(n){e=O(n,"H2",{slot:!0,class:!0,"data-svelte-h":!0}),pe(e)!=="svelte-j4u52k"&&(e.textContent=t),this.h()},h(){U(e,"slot","header"),U(e,"class","svelte-1w90mea")},m(n,c){$(n,e,c)},p:_e,d(n){n&&b(e)}}}function zt(l){let e,t,n,c,_,d="Unseeded",v,a,p=[],k=new Map,m,C,g,h="Seeding",o,f=[],H=new Map,u,r,M,B,R,x,A,J,Y,L,W,K,ne='<tr class="headerrow svelte-1w90mea"><td class="svelte-1w90mea">Faster School</td> <td class="svelte-1w90mea">Slower School</td> <td class="svelte-1w90mea">Margin</td> <td class="svelte-1w90mea">Date</td> <td class="svelte-1w90mea">Link</td></tr>',ie,le,re,X,ae,ee,w,z,s=fe(l[2]);const y=E=>E[46].id;for(let E=0;E<s.length;E+=1){let D=Xe(l,s,E),Q=y(D);k.set(Q,p[E]=Ye(Q,D))}let V=fe(l[3]);const Z=E=>E[46].id;for(let E=0;E<V.length;E+=1){let D=We(l,V,E),Q=Z(D);H.set(Q,f[E]=Qe(Q,D))}let N=l[4].length==0&&Ze(),P=l[4].length===1&&$e(l),se=l[4].length===2&&et(l),ve=fe(l[5]),oe=[];for(let E=0;E<ve.length;E+=1)oe[E]=st(Fe(l,ve,E));function mt(E){l[27](E)}let Te={apply:l[26],$$slots:{header:[jt],default:[Pt]},$$scope:{ctx:l}};return l[0]!==void 0&&(Te.showModal=l[0]),X=new Ut({props:Te}),at.push(()=>St(X,"showModal",mt)),{c(){e=I("div"),t=I("div"),n=I("div"),c=I("div"),_=I("h2"),_.textContent=d,v=F(),a=I("div");for(let E=0;E<p.length;E+=1)p[E].c();m=F(),C=I("div"),g=I("h2"),g.textContent=h,o=F();for(let E=0;E<f.length;E+=1)f[E].c();u=F(),r=I("div"),M=I("div"),N&&N.c(),B=F(),P&&P.c(),R=F(),se&&se.c(),x=F(),A=I("div"),J=I("input"),Y=F(),L=I("div"),W=I("table"),K=I("thead"),K.innerHTML=ne,ie=F(),le=I("tbody");for(let E=0;E<oe.length;E+=1)oe[E].c();re=F(),It(X.$$.fragment),this.h()},l(E){e=O(E,"DIV",{class:!0,style:!0});var D=q(e);t=O(D,"DIV",{class:!0,style:!0});var Q=q(t);n=O(Q,"DIV",{class:!0});var j=q(n);c=O(j,"DIV",{class:!0});var he=q(c);_=O(he,"H2",{class:!0,"data-svelte-h":!0}),pe(_)!=="svelte-1rh5f2t"&&(_.textContent=d),v=G(he),a=O(he,"DIV",{style:!0});var Se=q(a);for(let ce=0;ce<p.length;ce+=1)p[ce].l(Se);Se.forEach(b),he.forEach(b),m=G(j),C=O(j,"DIV",{class:!0});var ke=q(C);g=O(ke,"H2",{class:!0,"data-svelte-h":!0}),pe(g)!=="svelte-qa7qnb"&&(g.textContent=h),o=G(ke);for(let ce=0;ce<f.length;ce+=1)f[ce].l(ke);ke.forEach(b),j.forEach(b),Q.forEach(b),u=G(D),r=O(D,"DIV",{class:!0});var be=q(r);M=O(be,"DIV",{class:!0});var ge=q(M);N&&N.l(ge),B=G(ge),P&&P.l(ge),R=G(ge),se&&se.l(ge),ge.forEach(b),x=G(be),A=O(be,"DIV",{class:!0});var ye=q(A);J=O(ye,"INPUT",{placeholder:!0}),Y=G(ye),L=O(ye,"DIV",{class:!0,style:!0});var Ie=q(L);W=O(Ie,"TABLE",{style:!0});var Ee=q(W);K=O(Ee,"THEAD",{"data-svelte-h":!0}),pe(K)!=="svelte-t5fbth"&&(K.innerHTML=ne),ie=G(Ee),le=O(Ee,"TBODY",{});var Oe=q(le);for(let ce=0;ce<oe.length;ce+=1)oe[ce].l(Oe);Oe.forEach(b),Ee.forEach(b),Ie.forEach(b),ye.forEach(b),be.forEach(b),D.forEach(b),re=G(E),Ot(X.$$.fragment,E),this.h()},h(){U(_,"class","svelte-1w90mea"),de(a,"height","100%"),de(a,"overflow-y","scroll"),U(c,"class","left"),U(g,"class","svelte-1w90mea"),U(C,"class","right"),U(n,"class","board svelte-1w90mea"),U(t,"class","w3-col s4"),de(t,"justify-content","left"),U(M,"class","selectionpane svelte-1w90mea"),U(J,"placeholder","this box does nothing yet..."),de(W,"border-collapse","collapse"),U(L,"class","researchtable svelte-1w90mea"),de(L,"height","calc(100vh - 43px)"),U(A,"class","researchpane svelte-1w90mea"),U(r,"class","w3-col s8"),U(e,"class","w3-row-padding w3-margin-bottom toplevel svelte-1w90mea"),de(e,"height","calc(100vh - 43px)"),de(e,"overflow","hidden")},m(E,D){$(E,e,D),i(e,t),i(t,n),i(n,c),i(c,_),i(c,v),i(c,a);for(let Q=0;Q<p.length;Q+=1)p[Q]&&p[Q].m(a,null);i(n,m),i(n,C),i(C,g),i(C,o);for(let Q=0;Q<f.length;Q+=1)f[Q]&&f[Q].m(C,null);i(e,u),i(e,r),i(r,M),N&&N.m(M,null),i(M,B),P&&P.m(M,null),i(M,R),se&&se.m(M,null),i(r,x),i(r,A),i(A,J),i(A,Y),i(A,L),i(L,W),i(W,K),i(W,ie),i(W,le);for(let Q=0;Q<oe.length;Q+=1)oe[Q]&&oe[Q].m(le,null);$(E,re,D),Bt(X,E,D),ee=!0,w||(z=[ue(window,"keydown",l[9]),ue(g,"click",l[12]),ue(J,"keydown",l[24])],w=!0)},p(E,D){if(D[0]&20){s=fe(E[2]),Ue();for(let j=0;j<p.length;j+=1)p[j].r();p=Ne(p,D,y,1,E,s,k,a,Pe,Ye,null,Xe);for(let j=0;j<p.length;j+=1)p[j].a();qe()}if(D[0]&24){V=fe(E[3]),Ue();for(let j=0;j<f.length;j+=1)f[j].r();f=Ne(f,D,Z,1,E,V,H,C,Pe,Qe,null,We);for(let j=0;j<f.length;j+=1)f[j].a();qe()}if(E[4].length==0?N||(N=Ze(),N.c(),N.m(M,B)):N&&(N.d(1),N=null),E[4].length===1?P?P.p(E,D):(P=$e(E),P.c(),P.m(M,R)):P&&(P.d(1),P=null),E[4].length===2?se?se.p(E,D):(se=et(E),se.c(),se.m(M,null)):se&&(se.d(1),se=null),D[0]&32){ve=fe(E[5]);let j;for(j=0;j<ve.length;j+=1){const he=Fe(E,ve,j);oe[j]?oe[j].p(he,D):(oe[j]=st(he),oe[j].c(),oe[j].m(le,null))}for(;j<oe.length;j+=1)oe[j].d(1);oe.length=ve.length}const Q={};D[0]&14&&(Q.apply=E[26]),D[0]&2|D[1]&1048576&&(Q.$$scope={dirty:D,ctx:E}),!ae&&D[0]&1&&(ae=!0,Q.showModal=E[0],bt(()=>ae=!1)),X.$set(Q)},i(E){if(!ee){for(let D=0;D<s.length;D+=1)me(p[D]);for(let D=0;D<V.length;D+=1)me(f[D]);me(X.$$.fragment,E),ee=!0}},o(E){for(let D=0;D<p.length;D+=1)we(p[D]);for(let D=0;D<f.length;D+=1)we(f[D]);we(X.$$.fragment,E),ee=!1},d(E){E&&(b(e),b(re));for(let D=0;D<p.length;D+=1)p[D].d();for(let D=0;D<f.length;D+=1)f[D].d();N&&N.d(),P&&P.d(),se&&se.d(),Me(oe,E),Lt(X,E),w=!1,rt(z)}}}const nt=l=>[l[0],l[1]];function Ft(l,e,t){let{data:n}=e,c=n.races,d=[...n.foundersDay],v=!1,a="";for(const[s,y]of Object.entries(c)){if(y.heats===void 0){console.log({race:y});continue}for(const V of y.heats)if(V.class==="fours"&&V.gender==="girls"&&V.varsity_index==="1")for(let Z=0;Z<V.results.length-1;Z++)for(let N=Z+1;N<V.results.length;N++)d.push([V.results[Z].school,V.results[N].school,Math.round(100*(V.results[N].margin_from_winner-V.results[Z].margin_from_winner))/100,y.day,y.url])}d.sort((s,y)=>(s=s[3],y=y[3],-(s<y?-1:s>y?1:0)));const[p,k]=Vt({duration:s=>Math.sqrt(s*200),fallback(s,y){const V=getComputedStyle(s),Z=V.transform==="none"?"":V.transform;return{duration:600,easing:Ht,css:N=>`
					transform: ${Z} scale(${N});
					opacity: ${N}
				`}}});let m=1,g=["Nobles","Groton","Brooks","BB&N","Middlesex","Taft","Cambridge RLS","Choate","Hopkins","Winsor","Frederick Gunn","Miss Porter's","Brewster Academy","Canterbury","Greenwich Academy","Lyme/Old Lyme","St. Mark's","NMH","Berkshire Academy","Newton Country Day","Pomfret"].map(s=>({id:m++,description:s})),h=[],o=[g[0]];function f(s){const y={id:m++,done:!1,seeded:!1,description:s.value};todos=[y,...todos],s.value=""}function H(s,y){return y<=0?s:(s===void 0&&console.error("wat"),[...s.slice(0,y-1),o[0],s[y-1],...s.slice(y+1)])}function u(s,y){return y>=s.length-1?s:[...s.slice(0,y),s[y+1],o[0],...s.slice(y+2)]}function r(s){console.log("moveToSeeding("+JSON.stringify(s)+")");let y={...o[0],seeded:!0},V=g.map(Z=>Z.id).indexOf(y.id);t(3,h=[...h.slice(0,V),y,...h.slice(V)]),t(2,g=g.filter(Z=>Z.id!=y.id)),t(4,o=[y])}function M(s){console.log("moveToUnseeded("+JSON.stringify(s)+")");let y={...o[0],seeded:!1},V=h.map(Z=>Z.id).indexOf(y.id);t(2,g=[...g.slice(0,V),y,...g.slice(V)]),t(3,h=h.filter(Z=>Z.id!=y.id)),t(4,o=[y])}function B(s){if(v)return;if(![38,40,37,39].includes(s.keyCode)){console.log(s.keyCode);return}if(s.preventDefault(),s.repeat||o.length!=1)return;let y=g.map(V=>V.id).indexOf(o[0].id);if(y<0)switch(y=h.map(V=>V.id).indexOf(o[0].id),s.keyCode){case 38:t(3,h=H(h,y));break;case 40:t(3,h=u(h,y));break;case 37:M(o[0]);break}else switch(s.keyCode){case 38:t(2,g=H(g,y));break;case 40:t(2,g=u(g,y));break;case 37:break;case 39:r(o[0]);break}}const R=(s,y)=>{y.shiftKey?t(4,o=[o[0],s]):t(4,o=[s])},x=()=>{t(1,a=h.map(s=>s.description).join(`
`)),t(0,v=!0)},A=(s,y)=>{y.shiftKey?t(4,o=[o[0],s]):t(4,o=[s])},J=s=>s.includes(o[0].description),Y=s=>s.includes(o[0].description),L=s=>s.includes(o[0].description),W=s=>s.includes(o[0].description),K=s=>s.includes(o[1].description),ne=s=>s.includes(o[0].description),ie=s=>s.includes(o[1].description),le=s=>s.includes(o[0].description),re=s=>s.includes(o[1].description),X=function(s){let y=o[0].description;for(const V of s)y+="-("+V[2]+")->"+V[1];return y},ae=s=>s.key==="Enter"&&f(s.target);function ee(){a=this.value,t(1,a)}const w=()=>{let s=g.map(P=>P.description)+h.map(P=>P.description),y=[];for(let P of a.split(`
`))if(P=P.trim(),P!==""){if(!s.includes(P))return[!1,`"${P}" was not recognized`];y.push(P)}let V=[],Z=[],N=g.concat(h);for(const P of N)y.includes(P.description)?Z.push(P):V.push(P);return Z.sort((P,se)=>y.indexOf(P.description)-y.indexOf(se.description)),console.log({result:y,all:N,newUnseeded:V,newSeeding:Z}),t(3,h=Z),t(2,g=V),[!0,"whoopee"]};function z(s){v=s,t(0,v)}return l.$$set=s=>{"data"in s&&t(10,n=s.data)},[v,a,g,h,o,d,p,k,f,B,n,R,x,A,J,Y,L,W,K,ne,ie,le,re,X,ae,ee,w,z]}class Wt extends ct{constructor(e){super(),ut(this,e,Ft,zt,it,{data:10},null,[-1,-1])}}export{Wt as component};
