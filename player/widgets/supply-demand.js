/* Widget "supply-demand": a draggable supply-and-demand chart.
 * Model of the chart:  demand  P = 10 + demandShift − Q ;  supply  P = Q − supplyShift ;  equilibrium = where they cross.
 * params: show (parts to draw), demandShift, supplyShift (−3…3),
 *         interactive ("curves"|"none"), ask ("equilibrium"|null), answered, marker. */
(function(){
const X=q=>200+86*q, Y=p=>720-52*p, Qf=x=>(x-200)/86, Pf=y=>(720-y)/52, LIM=[0.3,9.7];
const eq=(s,t)=>({q:(10+s+t)/2,p:(10+s-t)/2});
const DL=s=>({c:10+s,m:-1}), SL=t=>({c:-t,m:1});
function clip(L){const a=(LIM[0]-L.c)/L.m,b=(LIM[1]-L.c)/L.m,lo=Math.max(LIM[0],Math.min(a,b)),hi=Math.min(LIM[1],Math.max(a,b));
  return lo<hi?[{q:lo,p:L.c+L.m*lo},{q:hi,p:L.c+L.m*hi}]:null;}
const T=(id,x,by,text,o={})=>{const size=o.size||34;return {op:'write',id,x,y:by-0.82*size,text,size,color:o.color,anchor:o.anchor};};
const LN=(id,x1,y1,x2,y2,o={})=>({op:'line',id,x1,y1,x2,y2,color:o.color,width:o.w||5,arrow:o.arrow||false,dash:o.dash});
const ALL=['axes','demand','supply','equilibrium','readout'];
const arrow=(d,t)=>d>0.15?'↑':d<-0.15?'↓':t.same;

const TXT={
 en:{price:'Price',qty:'Quantity',same:'no change',
  title_ask:'Where is the new equilibrium?',
  why:(s,t)=>{const a=Math.abs(s)>.15,b=Math.abs(t)>.15;
    const dn=s>0?'Demand rises (D shifts right)':'Demand falls (D shifts left)',sn=t>0?'Supply rises (S shifts right)':'Supply falls (S shifts left)';
    return a&&!b?dn+':\nthe point slides along S':b&&!a?sn+':\nthe point slides along D':'Both curves moved.\nThe bigger shift\ndecides the direction.';},
  EV:{D1:'a rise in demand (D shifts right)',D_1:'a fall in demand (D shifts left)',S1:'a rise in supply (S shifts right)',S_1:'a fall in supply (S shifts left)'},
  up:'up',down:'down',nameD:'demand',nameS:'supply',colD:'red',colS:'blue',
  correct:(ev,dp,dq)=>`Right. The new equilibrium E₂ is on both curves: with ${ev}, price goes ${dp} and quantity goes ${dq}.`,
  stay:()=>'The dot is still at the old equilibrium E₁. A curve has shifted, so E₁ is no longer on both curves; the equilibrium has to be found again.',
  vertical:(nm)=>`The dot is on the new ${nm} curve, but the quantity did not change. A price change also moves the quantity along the other curve, so the point has to lie on both curves.`,
  wrong:(wp,wq,wev,col,nm,other)=>`Price ${wp} and quantity ${wq} is what ${wev} looks like. In this question the ${col} ${nm} curve moved, not the ${other} curve.`,
  reversed:(ev,dp,dq)=>`The direction is reversed. With ${ev}, price should go ${dp} and quantity ${dq}, not the other way round.`,
  geo:(onD,onS)=>(onD&&!onS?'The dot is on the demand curve but not on the supply curve.':!onD&&onS?'The dot is on the supply curve but not on the demand curve.':!onD&&!onS?'The dot is on neither curve.':'')+' The equilibrium must be on both curves — where they cross.'},
};

function candidates(s,t){
  const e0=eq(0,0),out=[{id:'correct',...eq(s,t),ok:true},{id:'stay',q:e0.q,p:e0.p}];
  if(Math.abs(s)>=1.5&&Math.abs(t)<0.01)out.push({id:'vertical-only',q:5,p:5+s},{id:'wrong-curve',...eq(0,-s)},{id:'reversed',...eq(-s,0)});
  else if(Math.abs(t)>=1.5&&Math.abs(s)<0.01)out.push({id:'vertical-only',q:5,p:5-t},{id:'wrong-curve',...eq(-t,0)},{id:'reversed',...eq(0,-t)});
  return out;
}
const outcome=(kind,sg)=>kind==='D'?{dp:sg,dq:sg}:{dp:-sg,dq:sg};
function classify(p){
  const t=TXT.en,s=p.demandShift||0,u=p.supplyShift||0,m=p.marker;
  const cands=candidates(s,u);let best=null,bd=1e9;
  for(const c of cands){const d=Math.hypot(m.x-X(c.q),m.y-Y(c.p));if(d<bd){bd=d;best=c;}}
  const kind=Math.abs(s)>=Math.abs(u)?'D':'S',sg=Math.sign(kind==='D'?s:u),o=outcome(kind,sg);
  const w=v=>v>0?t.up:t.down,ev=t.EV[kind+(sg>0?'1':'_1')];
  const nm=kind==='D'?t.nameD:t.nameS,other=kind==='D'?t.nameS:t.nameD,col=kind==='D'?t.colD:t.colS;
  if(bd<=50){
    const id=best.id;let say;
    if(id==='correct')say=t.correct(ev,w(o.dp),w(o.dq));
    else if(id==='stay')say=t.stay();
    else if(id==='vertical-only')say=t.vertical(nm);
    else if(id==='wrong-curve'){const wk=kind==='D'?'S':'D',ws=-sg,wo=outcome(wk,ws);say=t.wrong(w(wo.dp),w(wo.dq),t.EV[wk+(ws>0?'1':'_1')],col,nm,other);}
    else say=t.reversed(ev,w(o.dp),w(o.dq));
    return {say,ok:!!best.ok,patch:{marker:{x:X(best.q),y:Y(best.p)},answered:!!best.ok},result:{matched:id,correct:!!best.ok}};
  }
  const q=Qf(m.x),pp=Pf(m.y);
  const dist=L=>Math.abs((L.c+L.m*q)-pp)/Math.sqrt(2)*52;
  return {say:t.geo(dist(DL(s))<28,dist(SL(u))<28),ok:false,result:{matched:null,correct:false}};
}

registerWidget('supply-demand',{
  defaults:{show:ALL,demandShift:0,supplyShift:0,interactive:'curves',ask:null,answered:false,marker:null},
  animate:['demandShift','supplyShift','marker'],
  normalize(to,given){if(given.ask){to.answered=false;to.marker=null;}return to;},
  summary(p){
    const s=p.demandShift||0,u=p.supplyShift||0,e=eq(s,u),e0=eq(0,0),r=v=>Math.round(v*100)/100;
    const o={demand_shift:r(s),supply_shift:r(u),equilibrium:{price:r(e.p),quantity:r(e.q)},change:{price:r(e.p-e0.p),quantity:r(e.q-e0.q)}};
    if(p.ask){o.ask=p.ask;o.answered=!!p.answered;if(p.marker)o.marker={price:r(Pf(p.marker.y)),quantity:r(Qf(p.marker.x))};}
    return o;
  },
  expand(p){
    const t=TXT.en,show=new Set(p.show||ALL),s=p.demandShift||0,u=p.supplyShift||0;
    const e=eq(s,u),e0=eq(0,0),dq=e.q-e0.q,dp=e.p-e0.p,moved=Math.abs(dq)>0.1||Math.abs(dp)>0.1;
    const ask=p.ask==='equilibrium',answered=!!p.answered,ops=[],handles=[];
    const mk=p.marker||{x:X(e0.q),y:Y(e0.p)};
    if(show.has('axes')){
      ops.push(LN('xaxis',200,720,1120,720,{w:4,arrow:true}),LN('yaxis',200,720,200,180,{w:4,arrow:true}),
        T('ylab',200,150,t.price,{anchor:'middle'}),T('xlab',1130,745,t.qty));
    }
    const lbl=(id,L,txt,color,dy)=>{const g=clip(L);if(g)ops.push(T(id,X(g[1].q)+16,Y(g[1].p)+dy,txt,{size:36,color}));};
    const seg=L=>{const g=clip(L);return g?[X(g[0].q),Y(g[0].p),X(g[1].q),Y(g[1].p)]:null;};
    const curvesLive=(p.interactive||'curves')==='curves'&&!ask;
    if(show.has('demand')){
      if(Math.abs(s)>0.1){const c=seg(DL(0));if(c){ops.push(LN('d0',...c,{color:'red',w:4,dash:true}));lbl('d0l',DL(0),'D₁','red',-6);}}
      const c=seg(DL(s));
      if(c){ops.push(LN('d',...c,{color:'red',w:6}));lbl('dl',DL(s),Math.abs(s)>0.1?'D₂':'D','red',-10);
        if(curvesLive)handles.push({param:'demandShift',hit:{type:'line',x1:c[0],y1:c[1],x2:c[2],y2:c[3],w:56},
          value:(pt)=>{let v=Qf(pt.x)+Pf(pt.y)-10;v=Math.max(-3,Math.min(3,v));return Math.abs(v)<0.15?0:v;}});}
      if(Math.abs(s)>0.15)ops.push(LN('sh_d',X(6.5),Y(3.5),X(6.5+s),Y(3.5),{color:'green',w:5,arrow:true}));
    }
    if(show.has('supply')){
      if(Math.abs(u)>0.1){const c=seg(SL(0));if(c){ops.push(LN('s0',...c,{color:'blue',w:4,dash:true}));lbl('s0l',SL(0),'S₁','blue',30);}}
      const c=seg(SL(u));
      if(c){ops.push(LN('s',...c,{color:'blue',w:6}));lbl('sl',SL(u),Math.abs(u)>0.1?'S₂':'S','blue',-14);
        if(curvesLive)handles.push({param:'supplyShift',hit:{type:'line',x1:c[0],y1:c[1],x2:c[2],y2:c[3],w:56},
          value:(pt)=>{let v=Qf(pt.x)-Pf(pt.y);v=Math.max(-3,Math.min(3,v));return Math.abs(v)<0.15?0:v;}});}
      if(Math.abs(u)>0.15)ops.push(LN('sh_s',X(6.5),Y(6.5),X(6.5+u),Y(6.5),{color:'green',w:5,arrow:true}));
    }
    const guides=(id,q,pp,color,lq,lp)=>{
      ops.push(LN(id+'v',X(q),Y(pp),X(q),720,{color,w:3,dash:true}),LN(id+'h',X(q),Y(pp),200,Y(pp),{color,w:3,dash:true}));
      if(lq)ops.push(T(id+'q',X(q),775,lq,{size:30,anchor:'middle',color:color==='gray'?undefined:color}));
      if(lp)ops.push(T(id+'p',140,Y(pp)+10,lp,{size:30,anchor:'middle',color:color==='gray'?undefined:color}));
    };
    const showE=show.has('equilibrium')&&(!ask||answered);
    if(ask||(showE&&moved)){ // the old equilibrium stays visible as a hollow ring
      if(!ask)guides('g0',e0.q,e0.p,'gray','Q₁','P₁');
      ops.push({op:'ellipse',id:'e0',cx:X(e0.q),cy:Y(e0.p),rx:14,ry:14,color:'gray',width:4,dash:true},T('e0l',X(e0.q)-64,Y(e0.p)+44,'E₁',{size:30,color:'gray'}));
    }
    if(showE){
      guides('g1',e.q,e.p,'green',moved?'Q₂':'Q*',moved?'P₂':'P*');
      ops.push({op:'ellipse',id:'e',cx:X(e.q),cy:Y(e.p),rx:15,ry:15,color:'green',fill:'green',width:4},T('el',X(e.q)+22,Y(e.p)+44,moved?'E₂':'E',{size:36,color:'green'}));
    }
    if(ask){
      if(!answered)guides('gm',Qf(mk.x),Pf(mk.y),'gray');
      ops.push({op:'ellipse',id:'mk',cx:mk.x,cy:mk.y,rx:20,ry:20,color:'green',fill:'green',width:6});
      if(!answered){
        ops.push(T('mkl',mk.x+30,mk.y-26,'E₂ ?',{size:38,color:'green'}));
        handles.push({param:'marker',hit:{type:'circle',cx:mk.x,cy:mk.y,r:46},
          value:(pt)=>({x:Math.max(X(LIM[0]),Math.min(X(LIM[1]),pt.x)),y:Math.max(Y(LIM[1]),Math.min(Y(LIM[0]),pt.y))}),
          onDrop:(pp)=>classify(pp)});
      }
    }
    if(show.has('readout')&&moved&&(!ask||answered)){
      ops.push(T('rdp',1180,330,`${t.price.split(' ')[0]}  ${arrow(dp,t)}`,{size:44,color:dp>0.15?'red':dp<-0.15?'blue':undefined}),
               T('rdq',1180,400,`${t.qty.split(' ')[0]}  ${arrow(dq,t)}`,{size:44,color:dq>0.15?'red':dq<-0.15?'blue':undefined}),
               T('rdd',1180,470,`ΔP = ${dp>0?'+':''}${dp.toFixed(1)}\nΔQ = ${dq>0?'+':''}${dq.toFixed(1)}`,{size:30,color:'gray'}),
               T('rdw',1180,590,t.why(s,u),{size:32}));
    }
    return {ops,handles};
  }
});
})();
