/* Widget "seasons": the Earth on its orbit, plus a zoomed view of how sunlight hits it.
 * Geometry: the orbit is drawn in perspective; the Earth's axis is tilted 23.5° and always points the same way.
 * Seasons are split into four quarter-turns centred on the solstices and equinoxes (≈ June–August = summer).
 * params: show (orbit, labels, zoom, readout, note), angle (radians), interactive ("earth"|"none"),
 *         ask ("north-summer"|"south-summer"|null), answered. */
(function(){
const EPS=23.5*Math.PI/180,TWO=2*Math.PI,CITY=40*Math.PI/180,OC={x:560,y:480,rx:360,ry:122};
const SPECIAL=[{th:0,k:'winter'},{th:1.5*Math.PI,k:'spring'},{th:Math.PI,k:'summer'},{th:0.5*Math.PI,k:'autumn'}];
const SEASON_AT={0:'winter',[1.5*Math.PI]:'spring',[Math.PI]:'summer',[0.5*Math.PI]:'autumn'};
const OPP={winter:'summer',summer:'winter',spring:'autumn',autumn:'spring'};
const norm=a=>{a=((a%TWO)+TWO)%TWO;return a<1e-9?TWO:a;};
const adiff=(a,b)=>{const d=Math.abs(norm(a)-norm(b))%TWO;return d>Math.PI?TWO-d:d;};
const decl=th=>Math.asin(-Math.sin(EPS)*Math.cos(th));
function nearest(th){let b=SPECIAL[0],bd=9;for(const sp of SPECIAL){const d=adiff(th,sp.th);if(d<bd){bd=d;b=sp;}}return b;}
const seasonN=th=>SEASON_AT[nearest(th).th];
const dg=r=>r*180/Math.PI;
const ep=th=>({x:OC.x+OC.rx*Math.cos(th),y:OC.y+OC.ry*Math.sin(th)});
function dayLen(phi,d){const x=Math.max(-1,Math.min(1,-Math.tan(phi)*Math.tan(d)));return 24/Math.PI*Math.acos(x);}
const T=(id,x,by,text,o={})=>{const size=o.size||34;return {op:'write',id,x,y:by-0.82*size,text,size,color:o.color,anchor:o.anchor};};
const LN=(id,x1,y1,x2,y2,o={})=>({op:'line',id,x1,y1,x2,y2,color:o.color,width:o.w||5,arrow:o.arrow||false,dash:o.dash});
const ALL=['orbit','labels','zoom','readout','note'];
const latName=(d,t)=>Math.abs(dg(d))<0.5?t.equator:(d>0?t.north:t.south)+' '+Math.abs(dg(d)).toFixed(1)+'°';

const TXT={
 en:{season:{winter:'winter',spring:'spring',summer:'summer',autumn:'autumn'},special:{winter:'Winter\nsolstice',spring:'Spring\nequinox',summer:'Summer\nsolstice',autumn:'Autumn\nequinox'},
  orbit:'orbit',sun:'Sun',sunlight:'Sunlight',zoom:'Zoom: sunlight on the Earth',city:'40°N',equator:'the equator',north:'N',south:'S',
  note1:'Earth–Sun distance barely changes (≈ 3%); the axis tilt makes the seasons.',
  note2:'Seasons: four quarter-turns centred on the solstices and equinoxes.',
  overhead:l=>'Sun overhead: '+l,hemi:(n,s)=>`North: ${n}\nSouth: ${s}`,
  cityInfo:(e,h)=>`A city at 40°N\nNoon Sun angle ${e.toFixed(0)}°\nDay length ${h.toFixed(1)} h`,
  at:n=>'(exactly at the '+n+')',spName:{winter:'winter solstice',spring:'spring equinox',summer:'summer solstice',autumn:'autumn equinox'},
  okN:'Right. Here the north pole tilts toward the Sun, so it is summer in the north (and winter in the south). In the zoom, the 40°N city gets the highest noon Sun and the longest day.',
  okS:'Right. Here the south pole tilts toward the Sun, so it is summer in the south (and winter in the north): the two hemispheres have opposite seasons.',
  eqn:(l,isEq)=>`Here the Sun is overhead at ${l}${isEq?'':', not far from the equator'}: the axis tilts neither clearly toward nor away from the Sun. This is spring or autumn, not summer. Summer needs the position where a pole tilts most toward the Sun.`,
  oppN:'The opposite: the north pole tilts away from the Sun, so it is winter in the north and summer in the south. Seasons are not set by distance from the Sun (it is almost constant on this orbit) but by the axis tilt.',
  oppS:'That is summer in the north and winter in the south. For summer in the south, put the Earth where the south pole tilts toward the Sun — on the other side of the orbit.'},
};
const ASK={'north-summer':{cor:Math.PI,fork:'N'},'south-summer':{cor:0,fork:'S'}};

function classify(p){
  const t=TXT.en,a=ASK[p.ask],th=p.angle,z=nearest(th),d=decl(th);
  const ok=z.th===a.cor,eqn=z.th===0.5*Math.PI||z.th===1.5*Math.PI;
  let say;
  if(ok)say=a.fork==='N'?t.okN:t.okS;
  else if(eqn)say=t.eqn(latName(d,t),Math.abs(dg(d))<0.5);
  else say=a.fork==='N'?t.oppN:t.oppS;
  return {say,ok,patch:{answered:ok},result:{matched:z.k,correct:ok}};
}

registerWidget('seasons',{
  defaults:{show:ALL,angle:0,interactive:'earth',ask:null,answered:false},
  animate:['angle'],
  publicParams(p){const q={...p},names={0:'winter-solstice',[1.5*Math.PI]:'spring-equinox',[Math.PI]:'summer-solstice',[0.5*Math.PI]:'autumn-equinox'};
    for(const a in names)if(Math.abs(norm(p.angle)-norm(+a))<0.01){q.position=names[a];delete q.angle;}return q;},
  normalize(to,given){
    if(given.position!==undefined){const a={'winter-solstice':0,'spring-equinox':1.5*Math.PI,'summer-solstice':Math.PI,'autumn-equinox':0.5*Math.PI}[given.position];if(a!==undefined)to.angle=a;}
    delete to.position;
    if(given.ask){to.answered=false;}
    return to;},
  lerp(key,a,b,k){if(key==='angle'){const d=((b-a+Math.PI)%TWO+TWO)%TWO-Math.PI;return a+d*k;}},
  summary(p){
    const th=p.angle,d=decl(th),r=v=>Math.round(v*10)/10,sN=seasonN(th);
    const o={angle_deg:Math.round(dg(norm(th))%360),sun_overhead_latitude_deg:r(dg(d)),season_north:sN,season_south:OPP[sN],
      noon_sun_angle_40N_deg:Math.round(90-Math.abs(dg(CITY)-dg(d))),day_length_40N_h:r(dayLen(CITY,d))};
    if(p.ask){o.ask=p.ask;o.answered=!!p.answered;}
    return o;
  },
  expand(p){
    const t=TXT.en,show=new Set(p.show||ALL),th=p.angle,ask=!!p.ask,answered=!!p.answered,ops=[],handles=[];
    const e=ep(th);
    if(show.has('orbit')){
      ops.push({op:'ellipse',id:'orbit',cx:OC.x,cy:OC.y,rx:OC.rx,ry:OC.ry,color:'gray',width:4,dash:true});
      const a1=ep(1.5*Math.PI+0.14),a2=ep(1.5*Math.PI-0.14),lw=70;
      ops.push(LN('dir',a1.x,a1.y-24,a2.x,a2.y-24,{color:'gray',w:4,arrow:true}),T('dirl',a2.x-14-lw,a2.y-26,t.orbit,{size:28,color:'gray'}));
      ops.push({op:'ellipse',id:'sun',cx:OC.x,cy:OC.y,rx:50,ry:50,color:'sun',fill:'sun',width:5},T('sunl',OC.x,OC.y+10,t.sun,{size:28,anchor:'middle'}));
      ops.push(LN('sr',OC.x,OC.y,e.x,e.y,{color:'gray',w:3,dash:true}));
    }
    if(show.has('labels')&&!ask){
      const w=116;
      for(const sp of SPECIAL){const q=ep(sp.th);ops.push({op:'ellipse',id:'sp_'+sp.k,cx:q.x,cy:q.y,rx:7,ry:7,color:'gray',fill:'gray',width:3});}
      ops.push(T('spw',OC.x+OC.rx+50,OC.y+8,t.special.winter,{size:28,color:'gray'}),T('spu',OC.x-OC.rx-50-w,OC.y+8,t.special.summer,{size:28,color:'gray'}),
               T('spa',OC.x,OC.y+OC.ry+84,t.special.autumn.replace('\n',' '),{size:28,color:'gray',anchor:'middle'}),T('spr',OC.x,OC.y-OC.ry-60,t.special.spring.replace('\n',' '),{size:28,color:'gray',anchor:'middle'}));
    }
    if(show.has('orbit')){
      // the Earth: night side, axis with the north end marked
      const dx=-Math.cos(th),dy=-Math.sin(th)*0.34,m=Math.hypot(dx,dy),nx=-dx/m,ny=-dy/m,px=-ny,py=nx;
      let d='';for(let i=0;i<=16;i++){const f=-Math.PI/2+Math.PI*i/16,x=e.x+40*(Math.cos(f)*nx+Math.sin(f)*px),y=e.y+40*(Math.cos(f)*ny+Math.sin(f)*py);d+=(i?' L ':'M ')+x.toFixed(1)+' '+y.toFixed(1);}
      ops.push({op:'ellipse',id:'earth',cx:e.x,cy:e.y,rx:40,ry:40,color:'blue',fill:'blue',width:5},{op:'path',id:'night',d:d+' Z',color:'gray',width:3,fill:'ink'});
      const ax={x:Math.sin(EPS),y:-Math.cos(EPS)*0.94},L=74;
      ops.push(LN('axis',e.x-ax.x*L,e.y-ax.y*L,e.x+ax.x*L,e.y+ax.y*L,{w:5}),
        {op:'ellipse',id:'axn',cx:e.x+ax.x*L,cy:e.y+ax.y*L,rx:8,ry:8,color:'red',fill:'red',width:3},
        T('axl',e.x+ax.x*(L+26),e.y+ax.y*(L+26)+10,'N',{size:32,color:'red',anchor:'middle'}));
      if((p.interactive||'earth')==='earth'&&!(ask&&answered)){
        handles.push({param:'angle',hit:{type:'circle',cx:e.x,cy:e.y,r:64},
          value:(pt)=>{let a=Math.atan2((pt.y-OC.y)/OC.ry,(pt.x-OC.x)/OC.rx);
            if(!ask)for(const sp of SPECIAL)if(adiff(a,sp.th)<0.09)a=sp.th;return a;},
          onDrop:ask&&!answered?(pp)=>classify(pp):undefined});
      }
    }
    const dcl=decl(th);
    if(show.has('zoom')&&(!ask||answered)){
      const cx=1350,cy=290,R=105,u={x:-Math.sin(dcl),y:-Math.cos(dcl)},ev={x:-Math.cos(dcl),y:Math.sin(dcl)};
      const n={x:Math.cos(CITY)*ev.x+Math.sin(CITY)*u.x,y:Math.cos(CITY)*ev.y+Math.sin(CITY)*u.y},pc={x:cx+R*n.x,y:cy+R*n.y};
      ops.push(T('zt',cx,cy-R-100,t.zoom,{size:28,color:'gray',anchor:'middle'}));
      [-80,-40,0,40,80].forEach((dy,i)=>{if(Math.abs(cy+dy-pc.y)<18)return;ops.push(LN('ray'+i,1135,cy+dy,cx-Math.sqrt(R*R-dy*dy)-8,cy+dy,{color:'sun',w:4,arrow:true}));});
      ops.push(T('zl',1135,cy+R+30,t.sunlight,{size:28,color:'sun'}),
        {op:'ellipse',id:'zc',cx,cy,rx:R,ry:R,color:'ink',fill:'sun',width:5},
        {op:'path',id:'zn',d:`M ${cx} ${cy-R} A ${R} ${R} 0 0 1 ${cx} ${cy+R} Z`,color:'gray',width:3,fill:'ink'},
        LN('zeq',cx-ev.x*R,cy-ev.y*R,cx+ev.x*R,cy+ev.y*R,{color:'gray',w:3,dash:true}),
        LN('zax',cx-u.x*(R+26),cy-u.y*(R+26),cx+u.x*(R+34),cy+u.y*(R+34),{w:5}),
        T('zn_',cx+u.x*(R+66),cy+u.y*(R+66)+10,'N',{size:32,color:'red',anchor:'middle'}),
        {op:'ellipse',id:'zs',cx:cx-R,cy,rx:11,ry:11,color:'sun',fill:'sun',width:4},
        LN('cr',1135,pc.y,pc.x-6,pc.y,{color:'red',w:5,arrow:true}),
        LN('cg',pc.x+n.y*38,pc.y-n.x*38,pc.x-n.y*38,pc.y+n.x*38,{w:5}),
        {op:'ellipse',id:'cd',cx:pc.x,cy:pc.y,rx:10,ry:10,color:'red',fill:'red',width:3},
        T('cl',pc.x-90,pc.y-22,t.city,{size:26,color:'red'}));
    }
    if(show.has('readout')&&(!ask||answered)){
      const sN=seasonN(th),elev=90-Math.abs(dg(CITY)-dg(dcl)),hrs=dayLen(CITY,dcl),near=adiff(th,nearest(th).th)<0.09;
      ops.push(T('r1',1130,520,t.overhead(latName(dcl,t)),{size:34}),
        T('r2',1130,572,t.hemi(t.season[sN],t.season[OPP[sN]]),{size:34,color:'blue'}),
        T('r3',1130,672,t.cityInfo(elev,hrs),{size:30}));
      if(near)ops.push(T('r4',1130,800,t.at(t.spName[nearest(th).k]),{size:26,color:'gray'}));
    }
    if(show.has('note'))ops.push(T('n1',60,840,t.note1,{size:26,color:'gray'}),T('n2',60,872,t.note2,{size:26,color:'gray'}));
    return {ops,handles};
  }
});
})();
