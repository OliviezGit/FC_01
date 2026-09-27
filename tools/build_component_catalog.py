"""Build the traceable component inventory and refresh instance purchasing fields."""
from pathlib import Path
import json,csv,re,hashlib,collections
from kicad_sexpr import *
import check_connectivity as graph
from component_fields import fields, feature_fields
R=Path(__file__).resolve().parents[1];D=R/'composants'
evidence=json.loads((R/'verification/EVIDENCE.json').read_text());buy=json.loads((D/'achats.json').read_text())
bindings=json.loads((D/'3d/BINDINGS.json').read_text())
pdfs={
'0402WGF5101TCE':'Royalohm.pdf','C1005X5R1C225M050BC':'TDK_C.pdf','GRM21BR61H106KE43L':'GRM21.pdf','GCM155R71H104KE02D':'GCM155.pdf',
'SMAJ30CA-13-F':'SMAJ30CA.pdf','PMEG4030ER,115':'PMEG4030ER.pdf','1N5819HW-7-F':'1N5819HW.pdf','PESD2CANFD24V-TR':'PESD2CANFD24V.pdf',
'AP7361C-33FGE-7':'AP7361C.pdf','BLM15AG601SN1D':'BLM15.pdf','XGL4030-332MEC':'XGL4030_mirror.pdf','10067099-200LF':'10067099.pdf','CSTNE8M00GH5C000R0':'CSTNE8M.pdf'}
for ref in ['U1','U2','U3','U4','U7','U8','U9','U10','U11','U12','U13','U14','Q1','D1','USB1']:
 pdfs[str(props(graph.comp[ref][1])['MPN'])]=ref+'_datasheet.pdf'
for m in buy:
 if m.startswith('RC0402'):pdfs[m]='Yageo_RC.pdf'
 if m.startswith('CL'):pdfs[m]=m[:-1]+'.pdf'
sources={}
for name in ['DOWNLOADS.json','MIRRORS.json','MORE_DOWNLOADS.json','LAST_DOWNLOADS.json']:
 for k,v in json.loads((D/'pdf'/name).read_text()).items():
  if isinstance(v,str):sources[k+'.pdf']=v
  elif 'file' in v:sources[v['file']]=v['url']
sources['PMEG4030ER.pdf']='https://www.mouser.com/datasheet/2/916/PMEG4030ER-2938673.pdf'
sources['U11_datasheet.pdf']='https://www.mouser.com/catalog/specsheets/TDK_DS_000577_ICM_45686.pdf'
for m,file in pdfs.items():
 if file.startswith('CL'):sources[file]='https://product.samsungsem.com/part/download.do?masterKey='+m[:-1]+'&type=specsheet'
 sources.setdefault(file,evidence[m]['source'])
groups=collections.defaultdict(list);features=[]
for ref,(fn,c,lib) in graph.comp.items():
 p=props(c);mpn=str(p.get('MPN',''))
 if mpn:groups[mpn].append(ref)
 else:features.append(ref)
def sortref(v):return re.sub(r'\d+',lambda m:m[0].zfill(5),v)
dirs={str(child(l,'name')[1]):R/str(child(l,'uri')[1]).replace('${KIPRJMOD}/','') for l in children(parse((R/'fp-lib-table').read_text()),'lib')}
catalog=[];byref={}
for m,refs in sorted(groups.items(),key=lambda x:sortref(sorted(x[1],key=sortref)[0])):
 refs=sorted(refs,key=sortref);fn,c,lib=graph.comp[refs[0]];p=props(c);fid=str(p['Footprint']);ln,fpn=fid.split(':',1)
 ev=evidence[m].copy()
 if m=='XGL4030-332MEC':ev.update(status='MANUFACTURER_LAND_REVIEWED',review='Coilcraft document 1575-4 du 19/12/2022: pads 0.98 x 3.40 mm, entraxe 2.37 mm; concordent avec empreinte. Enveloppe 4 x 4 x 3.1 mm. Tol. corps +/-0.3 mm non representee.')
 if m=='10067099-200LF':ev.update(status='MANUFACTURER_DRAWING_REVIEWED',review='Plan Amphenol 10067099 Rev.H p.2: version 200LF hauteur 2.65 mm, 8 contacts pas 1.10 mm + 2 detecteurs. Plan local et STEP fournisseur rapproches de l empreinte; validation assemblage reste a faire.')
 native=str((dirs[ln]/(fpn+'.kicad_mod')).relative_to(R))
 rec={'mpn':m,'references':refs,'quantity':len(refs),'manufacturer':str(p.get('Manufacturer','')),'value':str(p.get('Value','')),'package':str(p.get('Package','')),
 'symbol_ids':sorted({str(child(graph.comp[r][1],'lib_id')[1]) for r in refs}),'symbol_file':'composants/kicad/FC01_Project.kicad_sym','footprint_id':fid,'footprint_file':native,
 'datasheet_file':'composants/pdf/'+pdfs[m],'datasheet_download_url':sources[pdfs[m]],'manufacturer_source_url':evidence[m]['source'],
 'model':bindings[fid],'electrical_review':ev,'purchasing':buy[m],'control_pdf':'composants/controle/'+re.sub(r'[^A-Za-z0-9_.-]','_',m)+'.pdf'}
 catalog.append(rec)
 for ref in refs:byref[ref]=rec
(D/'catalogue.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
manifest=[]
for file,url in sorted(sources.items()):
 p=D/'pdf'/file
 if p.exists():manifest.append({'file':'composants/pdf/'+file,'url':url,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'retrieved':'2026-09-27'})
(D/'pdf/SOURCES.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
rows=[]
for r in catalog:
 p=r['purchasing'];rows.append({'MPN':r['mpn'],'Repères':', '.join(r['references']),'Quantité PCB':r['quantity'],'Valeur':r['value'],'Fabricant':r['manufacturer'],'Symbole':'; '.join(r['symbol_ids']),'Fichier symbole':r['symbol_file'],'Empreinte':r['footprint_file'],'3D':r['model']['file'],'Type 3D':r['model']['type'],'PDF technique':r['datasheet_file'],'Source PDF':r['datasheet_download_url'],'Fournisseur France':p['supplier'],'Référence commande':p['order_code'],'Prix unitaire EUR HT':p['unit_eur_ht'],'Quantité tarif / minimum':p['price_quantity'],'Stock relevé':p['stock'],'Date consultation':p['checked'],'Lien achat':p['url'],'Remarques achat':p['notes'],'Contrôle PDF':r['control_pdf']})
with (D/'BOM_FR.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=';');w.writeheader();w.writerows(rows)
frows=[]
for ref in sorted(features,key=sortref):
 fn,c,lib=graph.comp[ref];p=props(c)
 frows.append({'Reference':ref,'Value':str(p.get('Value','')),'Symbol':str(child(c,'lib_id')[1]),'Footprint':str(p['Footprint']),'3D / achat':'Non applicable: pastille, point test, cavalier cuivre ou trou du PCB; pas de composant achete.'})
with (D/'ELEMENTS_PCB.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(frows[0]));w.writeheader();w.writerows(frows)
# Existing EDA instance fields now point at the locally archived specification.
for path in list(R.glob('*.kicad_sch'))+list(R.glob('*.kicad_pcb')):
 s=path.read_text();n=parse(s);edits=[]
 for c in children(n,'symbol' if path.suffix=='.kicad_sch' else 'footprint'):
  ref=str(props(c).get('Reference',''))
  if ref not in graph.comp:continue
  sid=str(child(graph.comp[ref][1],'lib_id')[1])
  if ref in byref:
   rec=byref[ref];vals=fields(rec,sid)
  else:
   fid=str(props(graph.comp[ref][1])['Footprint']);ln,fpn=fid.split(':',1)
   vals=feature_fields(sid,str((dirs[ln]/(fpn+'.kicad_mod')).relative_to(R)))
  existing={str(x[1]):x for x in children(c,'property')}
  if ref in byref:
   # Remove stale alternate commercial quotes from the instance's legacy fields.
   for key in ('RS Part Number','RS URL','Mouser Part Number','Mouser URL'):
    if key in existing:vals[key]=''
   for key in ('Supplier Note','Supplier Specs'):
    if key in existing:vals[key]=rec['purchasing']['notes']
   if 'Supplier PDF' in existing:vals['Supplier PDF']=rec['datasheet_download_url']
  for k,v in vals.items():
   if k in existing:
    old=existing[k][2];edits.append((old.start,old.end,json.dumps(v,ensure_ascii=False)))
   elif path.suffix=='.kicad_sch':
    edits.append((c.end-1,c.end-1,'\n'+f'(property {json.dumps(k)} {json.dumps(v,ensure_ascii=False)} (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))'+'\n'))
 path.write_text(replace(s,edits))
print(json.dumps({'mpns':len(catalog),'purchased_references':sum(len(x) for x in groups.values()),'pcb_features':len(features),'pdfs':len(manifest),'pricing_unconfirmed':[m for m,p in buy.items() if p['unit_eur_ht'] is None]},indent=2))
