import sys,pathlib,math,collections,json,re
from kicad_sexpr import *
R=pathlib.Path(__file__).resolve().parents[1]
class DSU:
 def __init__(self):self.p={}
 def root(self,x):
  if x not in self.p:self.p[x]=x
  if self.p[x]!=x:self.p[x]=self.root(self.p[x])
  return self.p[x]
 def union(self,x,y):self.p[self.root(x)]=self.root(y)
d=DSU();pinloc={};labels=[];points=collections.defaultdict(set);paths={};comp={};no_connect=set()
def xy(n):return tuple(round(float(v),5) for v in n[1:3])
def pt(fn,x,y):
 k=(fn,round(x,5),round(y,5));points[fn].add(k);d.root(k);return k
def trans(c,x,y):
 mirror=child(c,'mirror')[1];ang=math.radians(float(child(c,'at')[3]));
 if mirror=='x':y=-y
 if mirror=='y':x=-x
 ox,oy=xy(child(c,'at'));return ox+x*math.cos(ang)-(-y)*math.sin(-ang),oy+x*math.sin(-ang)+(-y)*math.cos(ang)
sheets={f.name:parse(f.read_text()) for f in R.glob('*.kicad_sch')}
root=sheets['H743_Ardupilot.kicad_sch'];paths['H743_Ardupilot.kicad_sch']='/'
for sh in children(root,'sheet'):paths[props(sh)['Sheetfile']]='/'+props(sh)['Sheetname']+'/'
for fn,n in sheets.items():
 libs={s[1]:s for s in children(child(n,'lib_symbols'),'symbol')}
 for c in children(n,'symbol'):
  p=props(c);ref=p['Reference'];lib=get_lib(c,libs)
  assert lib is not None,(fn,ref)
  if not ref.startswith('#'):comp[ref]=(fn,c,lib)
  for pn in pin_nodes(lib):
   pos=pt(fn,*trans(c,*xy(child(pn,'at'))));num=child(pn,'number')[1]
   pinloc[ref,num]=pos
   if ref.startswith('#PWR'):labels.append((pos,'global',p['Value']))
 for typ in ['label','global_label','hierarchical_label']:
  for l in children(n,typ):labels.append((pt(fn,*xy(child(l,'at'))),'global' if typ=='global_label' else 'local',l[1]))
 for nc in children(n,'no_connect'):no_connect.add(pt(fn,*xy(child(nc,'at'))))
 for j in children(n,'junction'):pt(fn,*xy(child(j,'at')))
 for w in children(n,'wire'):
  for p in children(child(w,'pts'),'xy'):pt(fn,*xy(p))
 for sh in children(n,'sheet'):
  sf=props(sh)['Sheetfile']
  for p in children(sh,'pin'):
   pos=pt(fn,*xy(child(p,'at')));d.union(pos,('label',sf,p[1]))
for pos,typ,name in labels:d.union(pos,('global',name) if typ=='global' else ('label',pos[0],name))
for fn,n in sheets.items():
 for w in children(n,'wire'):
  (x1,y1),(x2,y2)=[xy(x) for x in children(child(w,'pts'),'xy')];p1=(fn,x1,y1)
  for p in points[fn]:
   _,x,y=p
   if abs((x-x1)*(y2-y1)-(y-y1)*(x2-x1))<1e-6 and min(x1,x2)-1e-6<=x<=max(x1,x2)+1e-6 and min(y1,y2)-1e-6<=y<=max(y1,y2)+1e-6:d.union(p1,p)
netpins=collections.defaultdict(list)
for (ref,num),pos in pinloc.items():
 if not ref.startswith('#'):netpins[d.root(pos)].append((ref,num))
pcb=parse((R/'H743_Ardupilot.kicad_pcb').read_text());pcbmap={}
for f in children(pcb,'footprint'):
 ref=props(f)['Reference']
 for p in children(f,'pad'):
  if p[1] and child(p,'net')[1]:pcbmap[ref,p[1]]=child(p,'net')[-1]
netnames=collections.defaultdict(set)
for pn,net in pcbmap.items():
 if pn in pinloc:netnames[d.root(pinloc[pn])].add(str(net))
conflicts={str(netpins[k]):sorted(v) for k,v in netnames.items() if len(v)>1}

res={}
for ref,(fn,c,lib) in comp.items():
 res[ref]={}
 for p in pin_nodes(lib):
  num=child(p,'number')[1];pos=pinloc[ref,num];rr=d.root(pos);known=netnames[rr]
  if len(known)==1:net=next(iter(known))
  else:
   nn=[(typ,name,pp[0]) for pp,typ,name in labels if d.root(pp)==rr]
   gl=[name for typ,name,_ in nn if typ=='global']
   if gl:net=gl[0]
   elif nn:net=paths[nn[0][2]]+nn[0][1]
   elif pos in no_connect:net='unconnected-('+ref+'-'+child(p,'name')[1].replace('/','{slash}')+'-Pad'+num+')'
   else:net='Net-('+ref+'-Pad'+num+')'
  res[ref][num]={'name':str(child(p,'name')[1]),'net':net,'position':pos,'nc':pos in no_connect}

# Read-only audit: a single PCB net must not merge separate schematic groups.
board_groups=collections.defaultdict(set)
for pn,net in pcbmap.items():
 if pn in pinloc: board_groups[net].add(d.root(pinloc[pn]))
merges={net:[netpins[g] for g in groups] for net,groups in board_groups.items() if len(groups)>1}
unsupported_bus_nets={k:merges.pop(k) for k in list(merges) if re.fullmatch(r'/MCU/MOTOR[1-4]',k)}
expected_motor_pairs={
 '/MCU/MOTOR1': {('U2','34'),('R47','1')},
 '/MCU/MOTOR2': {('U2','35'),('R48','1')},
 '/MCU/MOTOR3': {('U2','22'),('R49','1')},
 '/MCU/MOTOR4': {('U2','23'),('R50','1')},
}
unexpected_bus_membership={net:sorted(set(sum(groups,[]))) for net,groups in unsupported_bus_nets.items()
                           if set(sum(groups,[])) != expected_motor_pairs.get(net,set())}
unexpected_bus_membership.update({net:[] for net in expected_motor_pairs if net not in unsupported_bus_nets})
# Check named schematic nets independently of PCB net names. The four motor bus
# members are explicitly mapped to the MCU hierarchical bus, which the DSU
# parser does not expand into four wires.
mismatched_named_nets=[];named_pins_checked=0
for pn,board_net in pcbmap.items():
 if pn not in pinloc:continue
 rr=d.root(pinloc[pn]);associated=[(typ,str(name),pos[0]) for pos,typ,name in labels if d.root(pos)==rr]
 if not associated:continue
 globals_=sorted({name for typ,name,_ in associated if typ=='global'})
 locals_=sorted({paths[fn]+name for typ,name,fn in associated if typ=='local' and '[' not in name})
 expected=globals_[0] if globals_ else locals_[0] if locals_ else None
 if expected and re.fullmatch(r'/MOTORS\[1-4\]/MOTOR[1-4]',expected):
  expected='/MCU/'+expected.rsplit('/',1)[1]
 if expected:
  named_pins_checked+=1
  if str(board_net)!=expected:mismatched_named_nets.append([*pn,str(board_net),expected])
if __name__ == '__main__':
 print(json.dumps({'conflicting_groups':conflicts,'merged_groups':merges,
                   'mismatched_named_nets':mismatched_named_nets,
                   'unexpected_bus_membership':unexpected_bus_membership,
                   'named_pins_checked':named_pins_checked,'pins_compared':len(pcbmap),
                   'bus_nets_require_native_check':list(unsupported_bus_nets)},indent=2))
 sys.exit(bool(conflicts or merges or mismatched_named_nets or unexpected_bus_membership))
