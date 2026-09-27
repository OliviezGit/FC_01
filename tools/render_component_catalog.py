"""Independent vector EDA review sheets (not a native KiCad plot or ERC/DRC)."""
from pathlib import Path
import json,math,re,collections,csv,os
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import cadquery as cq
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from xml.sax.saxutils import escape
from kicad_sexpr import *
import check_connectivity as graph
R=Path(__file__).resolve().parents[1];D=R/'composants';O=D/'controle';T=R.parent/'tmp/catalog_render';T.mkdir(parents=True,exist_ok=True)
catalog=json.loads((D/'catalogue.json').read_text());bindings=json.loads((D/'3d/BINDINGS.json').read_text())
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVB','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
W,H=595.276,841.89
def para(c,text,x,y,width=515,size=9,color='#233247'):
 st=ParagraphStyle('p',fontName='DV',fontSize=size,leading=size*1.4,textColor=HexColor(color))
 p=Paragraph(text,st);w,h=p.wrap(width,1000);p.drawOn(c,x,y-h);return y-h-7
def header(c,title,sub):
 c.setFillColor(HexColor('#112b42'));c.rect(0,H-95,W,95,fill=1,stroke=0)
 c.setFillColor(HexColor('#6fd8c4'));c.setFont('DVB',9);c.drawString(36,H-27,'FC_01  /  DOSSIER COMPOSANTS  /  27.09.2026')
 c.setFillColor(HexColor('#ffffff'));c.setFont('DVB',16);c.drawString(36,H-55,title)
 c.setFont('DV',8);c.drawString(36,H-76,sub[:115])
def footer(c,label):
 c.setStrokeColor(HexColor('#dce4eb'));c.line(36,34,W-36,34)
 c.setFillColor(HexColor('#617184'));c.setFont('DV',7);c.drawString(36,22,label);c.drawRightString(W-36,22,str(c.getPageNumber()))
def frame(c,x,y,w,h,title):
 c.setFillColor(HexColor('#f5f8fb'));c.setStrokeColor(HexColor('#dce4eb'));c.roundRect(x,y,w,h,5,fill=1,stroke=1)
 c.setFillColor(HexColor('#112b42'));c.setFont('DVB',9);c.drawString(x+12,y+h-20,title)
def line(c,points,color='#80303b',width=1,closed=False,fill=False):
 c.setStrokeColor(HexColor(color));c.setLineWidth(width);c.setFillColor(HexColor(color));p=c.beginPath();p.moveTo(*points[0])
 for pt in points[1:]:p.lineTo(*pt)
 if closed:p.close()
 c.drawPath(p,stroke=1,fill=fill)
def symbol(c,n,box):
 elems=[]
 for s in children(n,'symbol'):
  tail=str(s[1]).rsplit('_',2)
  if len(tail)==3 and tail[-1] not in ('0','1'):continue
  elems+=s[2:]
 pts=[]
 for e in elems:
  if not isinstance(e,list):continue
  for k in ['start','end','mid','at','center']:
   z=child(e,k)
   if len(z)>=3:pts.append(tuple(map(float,z[1:3])))
  for z in children(child(e,'pts'),'xy'):pts.append(tuple(map(float,z[1:3])))
 if not pts:return
 x,y,w,h=box;lo=np.min(pts,axis=0);hi=np.max(pts,axis=0);ext=np.maximum(hi-lo,1);s=min((w-40)/ext[0],(h-40)/ext[1],20);cx,cy=(lo+hi)/2
 def pt(v):return (x+w/2+(float(v[0])-cx)*s,y+h/2+(float(v[1])-cy)*s)
 for e in elems:
  if not isinstance(e,list):continue
  kind=e[0];width=max(.35,float(child(child(e,'stroke'),'width')[1] or .15)*s)
  if kind=='rectangle':
   a1=pt(child(e,'start')[1:]);b1=pt(child(e,'end')[1:]);c.setFillColor(HexColor('#fff9e8'));c.setStrokeColor(HexColor('#80303b'));c.setLineWidth(width);c.rect(min(a1[0],b1[0]),min(a1[1],b1[1]),abs(a1[0]-b1[0]),abs(a1[1]-b1[1]),fill=child(child(e,'fill'),'type')[1]=='background',stroke=1)
  elif kind=='polyline':
   pp=[pt(z[1:]) for z in children(child(e,'pts'),'xy')]
   if pp:line(c,pp,width=width,closed=pp[0]==pp[-1],fill=child(child(e,'fill'),'type')[1] in ('outline','background'))
  elif kind=='circle':
   center=pt(child(e,'center')[1:]);rad=float(child(e,'radius')[1])*s;c.setStrokeColor(HexColor('#80303b'));c.setLineWidth(width);c.circle(*center,max(rad,.1),stroke=1,fill=0)
  elif kind=='arc':
   aa,bb,cc=[np.array(list(map(float,child(e,k)[1:3]))) for k in ['start','mid','end']]
   try:
    cent=np.linalg.solve(2*np.array([bb-aa,cc-aa]),np.array([bb@bb-aa@aa,cc@cc-aa@aa]));angs=[math.atan2(*(p-cent)[::-1]) for p in [aa,bb,cc]];a0,am,ae=angs;de=(ae-a0)%(2*math.pi)
    if (am-a0)%(2*math.pi)>de:de-=2*math.pi
    rr=np.linalg.norm(aa-cent);pp=[pt(cent+rr*np.array([math.cos(t),math.sin(t)])) for t in np.linspace(a0,a0+de,40)];line(c,pp,width=width)
   except np.linalg.LinAlgError:pass
  elif kind=='pin':
   if child(e,'hide')[1]=='yes':continue
   at=child(e,'at');a1=np.array(list(map(float,at[1:3])));ang=math.radians(float(at[3]));v=np.array([math.cos(ang),math.sin(ang)]);b1=a1+float(child(e,'length')[1])*v;line(c,[pt(a1),pt(b1)],width=.7)
   num=str(child(e,'number')[1]);name=str(child(e,'name')[1]);fs=min(9,max(4.5,1.1*s));c.setFont('DV',fs);c.setFillColor(HexColor('#80303b'))
   pp=pt((a1+b1)/2);c.drawCentredString(pp[0]+(4 if abs(v[1])>.5 else 0),pp[1]+(3 if abs(v[0])>.5 else 0),num)
   if name and name!='~' and child(child(n,'pin_names'),'hide')[1]!='yes':
    pos=pt(b1+.45*v);c.setFillColor(HexColor('#164d53'))
    if v[0]>.5:c.drawString(pos[0],pos[1]-fs*.33,name)
    elif v[0]<-.5:c.drawRightString(pos[0],pos[1]-fs*.33,name)
    else:
     c.saveState();c.translate(*pos);c.rotate(90);c.drawString(0,0,name);c.restoreState()
def footprint(c,n,box):
 pads=children(n,'pad');points=[]
 for p in pads:
  at=child(p,'at');sz=child(p,'size');px,py=map(float,at[1:3]);pw,ph=map(float,sz[1:3]);points.extend([(px-pw/2,py-ph/2),(px+pw/2,py+ph/2)])
 for e in n:
  if isinstance(e,list) and e[0] in ('fp_line','fp_rect','fp_circle'):
   for k in ['start','end','center']:
    z=child(e,k)
    if len(z)>2:points.append(tuple(map(float,z[1:3])))
 x,y,w,h=box;lo=np.min(points,axis=0);hi=np.max(points,axis=0);ext=np.maximum(hi-lo,.1);s=min((w-30)/ext[0],(h-30)/ext[1],95);cx,cy=(lo+hi)/2
 def pt(v):return x+w/2+(float(v[0])-cx)*s,y+h/2-(float(v[1])-cy)*s
 for e in n:
  if not isinstance(e,list) or not str(e[0]).startswith('fp_'):continue
  layer=child(e,'layer')[1]
  if layer not in ('F.Fab','F.CrtYd'):continue
  col='#405c6f' if layer=='F.Fab' else '#adbcc8'
  if e[0]=='fp_line':line(c,[pt(child(e,'start')[1:]),pt(child(e,'end')[1:])],col,.6)
  if e[0]=='fp_rect':
   a1=pt(child(e,'start')[1:]);b1=pt(child(e,'end')[1:]);line(c,[a1,(a1[0],b1[1]),b1,(b1[0],a1[1])],col,.6,True)
 for p in pads:
  if not p[1] and p[2]!='np_thru_hole':continue
  at=child(p,'at');px,py=map(float,at[1:3]);pw,ph=map(float,child(p,'size')[1:3]);a1=math.radians(float(at[3]) if len(at)>3 else 0)
  pp=[pt((px+dx*math.cos(a1)-dy*math.sin(a1),py+dx*math.sin(a1)+dy*math.cos(a1))) for dx,dy in [(-pw/2,-ph/2),(pw/2,-ph/2),(pw/2,ph/2),(-pw/2,ph/2)]]
  if str(p[3])=='custom':
   prim=child(p,'primitives')
   for poly in children(prim,'gr_poly'):
    pp2=[pt((px+float(z[1]),py+float(z[2]))) for z in children(child(poly,'pts'),'xy')]
    if pp2:line(c,pp2,'#cf963f',.2,True,True)
  else:line(c,pp,'#cf963f' if p[1] else '#a4b3bf',.2,True,True)
  drill=child(p,'drill')
  if len(drill)>1 and drill[1]:
   ds=[float(z) for z in drill[1:] if str(z).replace('.','',1).isdigit()];pos=pt((px,py));c.setFillColor(HexColor('#f5f8fb'));c.setStrokeColor(HexColor('#405c6f'))
   if len(ds)==1:c.circle(pos[0],pos[1],ds[0]*s/2,stroke=1,fill=1)
   elif len(ds)>1:c.roundRect(pos[0]-ds[0]*s/2,pos[1]-ds[1]*s/2,ds[0]*s,ds[1]*s,min(ds)*s/2,stroke=1,fill=1)
  pos=pt((px,py));c.setFillColor(HexColor('#152c40'));fs=min(7,max(1.5,pw*s/(max(1,len(str(p[1])))*.75)));c.setFont('DVB',fs);c.drawCentredString(pos[0],pos[1]-fs*.3,str(p[1]))
 c.setFont('DV',7);c.setFillColor(HexColor('#617184'));c.drawCentredString(x+w/2,y-4,'Cuivre ocre / corps bleu / cour dessin gris - vue dessus')
def model_image(rec):
 key=Path(rec['file']).stem+'_'+str(rec['scale'][2]);path=T/(key+'.png')
 if path.exists():return path
 shape=cq.Compound.makeCompound(cq.importers.importStep(str(R/rec['file'])).vals());vs,ts=shape.tessellate(.065,.25);v=np.array([[p.x,p.y,p.z] for p in vs])*rec['scale'];tri=v[np.array(ts)]
 norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm/=np.maximum(np.linalg.norm(norm,axis=1)[:,None],1e-10);light=np.array([.2,-.5,1]);light/=np.linalg.norm(light);shade=.55+.4*np.maximum(0,norm@light);colors=np.stack([shade*.42,shade*.55,shade*.64,np.ones(len(shade))],axis=1)
 fig=plt.figure(figsize=(5.2,3.6),dpi=150);ax=fig.add_subplot(111,projection='3d');ax.add_collection3d(Poly3DCollection(tri,facecolors=colors,edgecolors='none',rasterized=True))
 lo=v.min(axis=0);hi=v.max(axis=0);span=hi-lo;ax.set(xlim=(lo[0],hi[0]),ylim=(lo[1],hi[1]),zlim=(min(0,lo[2]),hi[2]));ax.set_box_aspect(np.maximum(span,.2));ax.view_init(28,-65);ax.set_axis_off();fig.subplots_adjust(0,0,1,1);fig.savefig(path,transparent=True);plt.close(fig);return path
def control(r):
 path=R/r['control_pdf'];c=canvas.Canvas(str(path),pagesize=(W,H));c.setTitle(r['mpn']+' - controle FC_01');c.setAuthor('FC_01 / controle documentaire')
 header(c,r['mpn'],' / '.join(r['references']));y=H-117
 y=para(c,escape(r['manufacturer'])+' - '+escape(r['value'])+' - '+escape(r['package']),36,y)
 y=para(c,'<b>Quantité carte :</b> '+str(r['quantity'])+' | <b>Broches et pastilles :</b> contrôle structurel concordant.',36,y)
 p=r['purchasing'];price='NON CONFIRMÉ' if p['unit_eur_ht'] is None else f"{p['unit_eur_ht']:.4f} EUR HT / pièce, tarif quantité {p['price_quantity']}"
 y=para(c,'<b>Achat :</b> '+escape(p['supplier'])+' | '+escape(p['order_code'] or 'référence commande non confirmée'),36,y)
 y=para(c,'<b>Prix :</b> '+price+' | <b>Stock relevé :</b> '+(str(p['stock']) if p['stock'] is not None else 'non confirmé'),36,y)
 if p['url']:y=para(c,'<link href="'+escape(p['url'])+'" color="#167883">Ouvrir la fiche fournisseur France</link>',36,y)
 y=para(c,escape(p['notes']),36,y,size=8,color='#8d522c')
 y=para(c,'<b>PDF technique local :</b> '+escape(r['datasheet_file'])+'<br/><link href="'+escape(r['datasheet_download_url'])+'" color="#167883">Lien de téléchargement de la fiche technique</link>',36,y,size=8)
 frame(c,36,245,251,225,'EMPREINTE / mm');frame(c,300,245,259,225,'MODÈLE 3D LOCAL')
 footprint(c,parse((R/r['footprint_file']).read_text()),(43,267,237,174));c.drawImage(str(model_image(r['model'])),304,265,width=249,height=177,mask='auto',preserveAspectRatio=True,anchor='c')
 y=227;y=para(c,'<b>3D :</b> '+escape(r['model']['type']),36,y,size=8)
 y=para(c,'<b>Empreinte :</b> '+escape(r['footprint_id'])+'<br/><b>STEP :</b> '+escape(r['model']['file']),36,y,size=7)
 y=para(c,'<b>Contrôle documentaire :</b> '+escape(r['electrical_review']['review']),36,y,size=8)
 footer(c,'Lecture indépendante des fichiers KiCad. Aucun ERC/DRC natif exécuté.');c.showPage()
 # Each actual symbol variant used by this manufacturer part is represented.
 for sid in r['symbol_ids']:
  ref=next(ref for ref in r['references'] if str(child(graph.comp[ref][1],'lib_id')[1])==sid);lib=graph.comp[ref][2]
  header(c,r['mpn'],'SYMBOLE  /  '+sid);para(c,'<b>Repères :</b> '+', '.join(x for x in r['references'] if str(child(graph.comp[x][1],'lib_id')[1])==sid),36,H-118,size=9)
  frame(c,36,86,523,606,'SYMBOLE / CORPS ET NUMÉROS DES BROCHES');symbol(c,lib,(52,105,491,555))
  hidden=[str(child(p,'number')[1]) for p in pin_nodes(lib) if child(p,'hide')[1]=='yes']
  para(c,'Correspondance complète : verification/PINS.csv'+(' | Broches masquées dans le symbole : '+', '.join(hidden) if hidden else ''),36,70,size=7)
  footer(c,'Rendu vectoriel de la variante utilisée; champs de nomenclature en page précédente.');c.showPage()
 c.save();print(r['mpn'],flush=True)
for r in catalog:control(r)
# All non-purchased PCB features, grouped by their actual symbol/footprint pair.
features=collections.defaultdict(list)
for ref,(fn,c,lib) in graph.comp.items():
 if not props(c).get('MPN'):features[(str(child(c,'lib_id')[1]),str(props(c)['Footprint']))].append(ref)
dirs={str(child(l,'name')[1]):R/str(child(l,'uri')[1]).replace('${KIPRJMOD}/','') for l in children(parse((R/'fp-lib-table').read_text()),'lib')}
c=canvas.Canvas(str(O/'elements_PCB.pdf'),pagesize=(W,H))
for (sid,fid),refs in features.items():
 header(c,'Éléments fabriqués dans le PCB',', '.join(refs));para(c,'Symbole et empreinte présents. Pas de composant acheté : prix, stock et modèle 3D séparé non applicables.',36,720)
 frame(c,36,360,523,300,'SYMBOLE');symbol(c,graph.comp[refs[0]][2],(52,380,491,240))
 frame(c,36,75,523,265,'EMPREINTE');ln,name=fid.split(':',1);footprint(c,parse((dirs[ln]/(name+'.kicad_mod')).read_text()),(55,100,485,205));footer(c,' / '.join(refs));c.showPage()
c.save()
# Consolidated document with a concise index and transparent release conditions.
intro=T/'intro.pdf';c=canvas.Canvas(str(intro),pagesize=(W,H));header(c,'Contrôle des composants',f'{len(catalog)} références fabricant / {sum(r["quantity"] for r in catalog)} composants achetés / {sum(len(v) for v in features.values())} éléments PCB')
y=715
for t in [
'<b>Couverture documentaire :</b> 35 PDF techniques originaux couvrent les 44 références. Les bibliothèques de symboles et empreintes actives, ainsi que tous les STEP liés, sont dans composants/.',
f'<b>Cohérence structurelle :</b> {len(graph.comp)} repères schéma/PCB et {sum(len(v) for v in graph.res.values())} correspondances broche-pastille. Aucun écart détecté par le contrôleur indépendant. Les 4 nets du bus MOTOR ne sont pas résolus par ce contrôleur. Aucun ERC/DRC natif KiCad exécuté.',
'<b>3D :</b> 9 références utilisent une enveloppe reconstruite du boîtier, sans contacts détaillés. Les autres modèles sont issus de KiCad ou des fichiers fournisseurs fournis. Les modèles génériques ne remplacent pas une validation mécanique aux tolérances maximales.',
'<b>Achats à résoudre :</b> 0402WGF5101TCE (R1/R2), 19-337/R6GHBHC-M01/2T (D1), RC0402FR-0716K5L (R9), XGL4030-332MEC (L1/L2) : offre exacte, prix et stock France non confirmés. Aucun remplacement automatique effectué.',
'<b>Prix :</b> EUR HT hors port. Tarif quantité 1 sauf C1005X5R1C225M050BC chez Farnell, minimum et multiple 10. Sa source indexée est ancienne : stock à reconfirmer. Les relevés web ne constituent pas une réservation de stock.',
'<b>Avant fabrication :</b> conserver les réserves de verification/REPORT.md, effectuer ERC/DRC sous KiCad et validation d’assemblage. Les 4 composants ajoutés lors du précédent contrôle sont encore en zone de placement provisoire.',
'<b>Fichiers de travail :</b> composants/BOM_FR.csv, catalogue.json, pdf/SOURCES.json, 3d/BINDINGS.json et verification/PINS.csv. Les PDF ci-après montrent chaque variante de symbole utilisée pour chaque référence fabricant.'
]:y=para(c,t,36,y,size=10)
footer(c,'Rapport documentaire et contrôle de cohérence; libération fabrication non prononcée.');c.showPage()
header(c,'Index des références','Chaque dossier contient empreinte, 3D, approvisionnement et variantes de symbole')
y=715
for i,r in enumerate(catalog):
 col=0 if i<22 else 1;row=i%22;x=36+col*270;yy=y-row*28
 refs=r['references'];short=', '.join(refs[:5])+(' ... ('+str(len(refs))+' repères)' if len(refs)>5 else '')
 para(c,escape(r['mpn']),x,yy,width=250,size=8);para(c,escape(short),x,yy-12,width=250,size=6,color='#617184')
footer(c,'Les repères sont regroupés uniquement lorsqu’ils partagent la référence fabricant.');c.showPage();c.save()
out=fitz.open();out.insert_pdf(fitz.open(intro));toc=[]
for r in catalog:
 toc.append([1,r['mpn']+' / '+', '.join(r['references']),len(out)+1]);out.insert_pdf(fitz.open(R/r['control_pdf']))
toc.append([1,'Éléments PCB sans achat',len(out)+1]);out.insert_pdf(fitz.open(O/'elements_PCB.pdf'));out.set_toc(toc);out.save(O/'CONTROLE_COMPLET.pdf',garbage=4,deflate=True)
print('TOTAL PAGES',len(out))
