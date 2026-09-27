"""Read-only structural audit. --write refreshes the CSV/JSON review artifacts.
This does not replace KiCad ERC/DRC or manufacturer/assembly review.
"""
import collections, copy, csv, json, pathlib, re, sys
from kicad_sexpr import *
import check_connectivity as graph
from component_fields import fields, feature_fields
R=pathlib.Path(__file__).resolve().parents[1]
errors=[]
def require(ok,msg):
    if not ok:errors.append(msg)
def sortref(v):return re.sub(r'\d+',lambda m:m[0].zfill(5),str(v))
def norm(n):
    if isinstance(n,list):return tuple(norm(x) for x in n)
    try:return round(float(n),7)
    except ValueError:return str(n)
def pad_signature(p,theta=0,back=False):
    p=copy.deepcopy(p)
    p[:]=[x for x in p if not(isinstance(x,list) and x[0] in ('net','pinfunction','pintype','uuid','tstamp'))]
    at=child(p,'at'); angle=float(at[3]) if len(at)>3 else 0
    if back:at[2]=a(-float(at[2]))
    angle=((theta-angle) if back else (angle-theta))%360
    at[:]=at[:3]+[a(angle)]
    layers=child(p,'layers')
    if back:
        for i in range(1,len(layers)):
            v=layers[i]
            if v.startswith(('F.','B.')):layers[i]=q(('B.' if v.startswith('F.') else 'F.')+v[2:])
    layers[1:]=sorted(layers[1:])
    # KiCad serializes polygon fill/thermal defaults on save; they do not alter copper here.
    p[:]=[x for x in p if not(isinstance(x,list) and x[0]=='thermal_bridge_angle')]
    for primitive in child(p,'primitives')[1:]:
        if not isinstance(primitive,list):continue
        primitive[:]=[x for x in primitive if not(isinstance(x,list) and x[0]=='fill')]
        if back:
            for point in children(child(primitive,'pts'),'xy'):point[2]=a(-float(point[2]))
    return norm(p)
fpdirs={str(child(l,'name')[1]):R/str(child(l,'uri')[1]).replace('${KIPRJMOD}/','') for l in children(parse((R/'fp-lib-table').read_text()),'lib')}
symlib=parse((R/'composants/kicad/FC01_Project.kicad_sym').read_text());symbols={str(s[1]):s for s in children(symlib,'symbol')}
catalog=json.loads((R/'composants/catalogue.json').read_text())
byref={ref:record for record in catalog for ref in record['references']}
symbol_instances=[]
for fn, sheet in graph.sheets.items():
    cached_symbols={str(item[1]):item for item in children(child(sheet,'lib_symbols'),'symbol')}
    for instance in children(sheet,'symbol'):
        reference=str(props(instance)['Reference']);sid=str(child(instance,'lib_id')[1]);key=sid.split(':',1)[-1]
        require(sid.startswith('FC01_Project:') and key in symbols,f'{fn}/{reference}: symbol is not resolved in the project library')
        if key in symbols:
            expected=copy.deepcopy(symbols[key]);expected[1]=q(sid)
            require(cached_symbols.get(sid)==expected,f'{fn}/{reference}: embedded symbol differs from the local library')
        symbol_instances.append({'Sheet':fn,'Reference':reference,'Symbol':sid,'Role':'Network/power symbol; footprint, 3D and purchase not applicable' if reference.startswith('#') else 'Physical PCB reference'})
board=graph.pcb; fps={str(props(f)['Reference']):f for f in children(board,'footprint')}
require(len(fps)==len(children(board,'footprint')),'Duplicate PCB reference')
require(set(fps)==set(graph.comp),'Schematic/PCB reference set mismatch')
components=[];pins=[];schema_fields=[]
evidence=json.loads((R/'verification/EVIDENCE.json').read_text()) if (R/'verification/EVIDENCE.json').exists() else {}
for ref,(fn,c,lib) in sorted(graph.comp.items(),key=lambda kv:sortref(kv[0])):
    p=props(c);fid=str(p['Footprint']);sid=str(child(c,'lib_id')[1]);libname,name=fid.split(':',1)
    src=fpdirs[libname]/(name+'.kicad_mod');require(src.is_file(),f'{ref}: missing footprint {fid}')
    values=fields(byref[ref],sid) if ref in byref else feature_fields(sid,str(src.relative_to(R)))
    for key,expected in values.items():
        require(str(p.get(key,''))==expected,f'{ref}: inconsistent schematic field {key}')
    for key in ('Symbol_Library_File','Footprint_File','Model_3D','Component_PDF','Datasheet'):
        file=str(p.get(key,''))
        if file:require(file.startswith('${KIPRJMOD}/') and (R/file.removeprefix('${KIPRJMOD}/')).is_file(),f'{ref}: missing/non-local asset in {key}')
    require(str(p['Footprint'])==byref[ref]['footprint_id'] if ref in byref else True,f'{ref}: catalogue/instance footprint mismatch')
    schema_fields.append({'Sheet':fn,'Reference':ref,'MPN':str(p.get('MPN','')),'Footprint':fid,**{key:str(p.get(key,'')) for key in values if not key.startswith('DigiKey') and key not in ('Price Checked','Footprint Audit','Library Audit')}})
    symkey=sid.split(':',1)[1];require(symkey in symbols,f'{ref}: missing symbol {sid}')
    if symkey in symbols:
        expected=copy.deepcopy(symbols[symkey]);expected[1]=q(sid)
        require(expected==lib,f'{ref}: cache/library symbol differs')
    if not src.exists() or ref not in fps:continue
    fp=parse(src.read_text());bf=fps[ref]
    sn={str(child(x,'number')[1]) for x in pin_nodes(lib)}
    ln={str(x[1]) for x in children(fp,'pad') if x[1]}
    bn={str(x[1]) for x in children(bf,'pad') if x[1]}
    require(sn==ln==bn,f'{ref}: pad sets differ: symbol={sn}, library={ln}, PCB={bn}')
    require(str(bf[1])==fid,f'{ref}: wrong PCB footprint id')
    if p.get('MPN'):
        lm=children(fp,'model');bm=children(bf,'model')
        require(len(lm)==len(bm)==1,f'{ref}: expected one local 3D model')
        require(lm==bm,f'{ref}: PCB/library 3D binding differs')
        for model in lm:
            require(str(model[1]).startswith('${KIPRJMOD}/composants/3d/'),f'{ref}: non-local 3D model')
            require((R/str(model[1]).replace('${KIPRJMOD}/','')).is_file(),f'{ref}: missing STEP')
    require(str(child(bf,'path')[1]).endswith('/'+str(child(c,'uuid')[1])),f'{ref}: wrong schematic UUID')
    at=child(bf,'at');theta=float(at[3]) if len(at)>3 else 0;back=child(bf,'layer')[1]=='B.Cu'
    # Compare geometry in footprint coordinates, independent of placement/side.
    ls=collections.Counter(pad_signature(x) for x in children(fp,'pad'))
    bs=collections.Counter(pad_signature(x,theta,back) for x in children(bf,'pad'))
    require(ls==bs,f'{ref}: PCB/library pad geometry differs')
    ev=evidence.get(str(p.get('MPN','')),evidence.get('_pcb_feature',{}))
    components.append({'Reference':ref,'Sheet':fn,'Value':str(p.get('Value','')),'Manufacturer':str(p.get('Manufacturer','')),'MPN':str(p.get('MPN','')),'Package':str(p.get('Package','')),'Symbol':sid,'Footprint':fid,'Symbol_pin_numbers':' '.join(sorted(sn,key=sortref)),'Footprint_pad_numbers':' '.join(sorted(ln,key=sortref)),'Status':ev.get('status','PENDING'),'Evidence':ev.get('source',''),'Review':ev.get('review','')})
    for pin in pin_nodes(lib):
        num=str(child(pin,'number')[1]);pads=[x for x in children(fp,'pad') if x[1]==num]
        pins.append({'Reference':ref,'Pin':num,'Symbol_pin_name':str(child(pin,'name')[1]),'PCB_net':graph.pcbmap.get((ref,num),''),'No_connect':graph.res[ref][num]['nc'],'Library_pad_geometry_mm':json.dumps([{'at':list(child(x,'at')[1:]),'size':list(child(x,'size')[1:]),'shape':str(x[3]),'mask_margin':str(child(x,'solder_mask_margin')[1])} for x in pads],ensure_ascii=False)})
require(not graph.conflicts,'Conflicting schematic/PCB nets')
require(not graph.merges,'PCB joins separate schematic nets')
report={'schematic_references':len(graph.comp),'pcb_footprints':len(fps),'unique_manufacturer_part_numbers':len({x['MPN'] for x in components if x['MPN']}),'symbol_pin_pad_pairs':len(pins),'schematic_symbol_instances':len(symbol_instances),'network_power_symbols':sum(x['Reference'].startswith('#') for x in symbol_instances),'purchased_references_with_local_assets':len(byref),'schematic_instance_fields_checked':len(schema_fields),'unconfirmed_purchasing_mpns':[x['mpn'] for x in catalog if x['purchasing']['unit_eur_ht'] is None],'errors':errors,'unsupported_bus_nets':sorted(graph.unsupported_bus_nets),'native_ERC_DRC_run':False}
if '--write' in sys.argv:
    out=R/'verification';out.mkdir(exist_ok=True)
    for name,rows in [('COMPONENTS.csv',components),('PINS.csv',pins)]:
        with (out/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
    for name,rows in [('SCHEMA_FIELDS.csv',schema_fields),('SCHEMA_SYMBOLS.csv',symbol_instances)]:
        with (out/name).open('w',newline='',encoding='utf-8-sig') as f:
            columns=list(dict.fromkeys(key for row in rows for key in row))
            w=csv.DictWriter(f,fieldnames=columns,delimiter=';',lineterminator='\n');w.writeheader();w.writerows(rows)
    (out/'CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2));sys.exit(bool(errors))
