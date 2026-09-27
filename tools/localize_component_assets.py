"""Local project assets; mechanical envelope models are explicitly labelled.
Run once on the review branch. No pad/net/placement geometry is changed.
"""
from pathlib import Path
import sys,json,shutil,copy
import cadquery as cq
from kicad_sexpr import *
R=Path(__file__).resolve().parents[1];M=R/'composants/3d'
if not (R/'composants/kicad').exists():shutil.copytree(R/'extralib',R/'composants/kicad')
for table in ['fp-lib-table','sym-lib-table']:
 p=R/table;p.write_text(p.read_text().replace('${KIPRJMOD}/extralib/','${KIPRJMOD}/composants/kicad/'))
# Keep the older snapshots for provenance; the tables now use composants/kicad.
maps={};records={}
def bind(fid,filename,kind='KiCad, geometrie generique du boitier',scale=(1,1,1),rot=(0,0,0),off=(0,0,0)):
 maps[fid]=parse(f'(model "${{KIPRJMOD}}/composants/3d/{filename}" (offset (xyz {off[0]} {off[1]} {off[2]})) (scale (xyz {scale[0]} {scale[1]} {scale[2]})) (rotate (xyz {rot[0]} {rot[1]} {rot[2]})))')
 records[fid]={'file':'composants/3d/'+filename,'type':kind,'scale':scale,'rotate':rot,'offset':off}
for lib,names in {
 'Capacitor_SMD':['C_0402_1005Metric','C_0603_1608Metric','C_0805_2012Metric'],
 'Resistor_SMD':['R_0402_1005Metric'],'Inductor_SMD':['L_0402_1005Metric'],
 'Diode_SMD':['D_SOD-123','Nexperia_CFP3_SOD-123W'],
 'Package_TO_SOT_SMD':['SOT-23'],'Package_QFP':['LQFP-100_14x14mm_P0.5mm'],
 'Package_LGA':['Bosch_LGA-16_4.5x3mm_P0.5mm_LayoutBorder7x1y_ClockwisePinNumbering']}.items():
 for name in names:bind(lib+':'+name,name+'.step')
bind('H743_Custom:Diodes_SMA_SMAJ30CA','D_SMA.step')
bind('H743_Custom:Diodes_U-DFN3030-8_TypeE','DFN-8-1EP_3x3mm_P0.65mm_EP1.5x2.25mm.step',kind='KiCad: EP nominal 1.5 x 2.25, pads PCB maximaux 1.6 x 2.35 (Diodes p.17/20)')
bind('Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y','LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y.step',scale=(1,1,.83/.78))
bind('H743_Custom:TDK_ICM45686_LGA14_3x2.5mm','LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y.step',scale=(1,1,.81/.78))
for n in ['JST_GH_SM04B-GHS-TB_1x04_P1.25mm_Horizontal','JST_SH_SM08B-SRSS-TB_1x08_P1.00mm_Horizontal']:
 bind('H743_Custom:'+n+'_GNDtabs',n.replace('1x04_','1x04-1MP_').replace('1x08_','1x08-1MP_')+'.step')
# Envelopes use manufacturer package dimensions, no invented lead geometry.
envelopes={
 'H743_Custom:TI_RPE0009B_VQFN-HR-9_2x2mm':(2,2,1.0,'LMR43620_RPE0009B_envelope'),
 'H743_Custom:TI_RAK0009A_WQFN-HR-9_2.5x2.0mm':(2,2.5,.8,'LMR60430_RAK0009A_envelope'),
 'Package_SON:HVSON-8-1EP_3x3mm_P0.65mm_EP1.6x2.4mm':(3,3,.85,'TJA1051_HVSON8_envelope'),
 'H743_Custom:Infineon_DPS368_PG-VLGA-8-2':(2.5,2,1.1,'DPS368_envelope'),
 'H743_Custom:QFN10_BMP581_BOS':(2,2,.8,'BMP581_envelope'),
 'H743_Custom:Everlight_19-337_1.6x1.6mm':(1.6,1.6,.35,'Everlight_19-337_envelope'),
 'H743_Custom:Murata_CSTNE_3.2x1.3_P1.2mm':(3.2,1.3,.9,'Murata_CSTNE_envelope'),
 'H743_Custom:L_Coilcraft_XGL4030':(4,4,3.1,'Coilcraft_XGL4030_envelope')}
for fid,(x,y,z,name) in envelopes.items():
 shape=cq.Workplane('XY').box(x,y,z,centered=(True,True,False))
 cq.exporters.export(shape,str(M/(name+'.step')))
 bind(fid,name+'.step','ENVELOPPE RECONSTRUITE: volume du boitier uniquement; contacts et tolerances non representes')
 records[fid]['body_mm']=[x,y,z]
bind('H743_Custom:Amphenol_10067099-200LF_RevH','Amphenol_10067099-200LF_supplier.step','STEP fournisseur fourni par utilisateur; orientation rapprochee du plan Rev.H',rot=(90,0,0),off=(0,-.9,1.45))
# The SnapMagic source archives prohibit redistribution of isolated models.
# Use the redistributable KiCad SOT-666 and an independently generated USB envelope.
bind('USBLC6_2P6:SOT50P160X60-6N','SOT-666.step','KiCad SOT-666, boitier nominal; modèle fournisseur privé utilisé pour comparaison')
shape=cq.Workplane('XY').box(8.94,6.9,4.36,centered=(True,True,False)).translate((0,0,-1.05))
cq.exporters.export(shape,str(M/'JAE_DX07S016JA1R1500_envelope.step'))
bind('H743_Custom:JAE_DX07S016JA1R1500_16P','JAE_DX07S016JA1R1500_envelope.step','ENVELOPPE RECONSTRUITE: limites mesurees du STEP fourni, 8.94 x 6.90 mm, z -1.05 a 3.31 mm; ni contacts ni interface de connexion; plan fabricant complet requis')
# Bake the Amphenol supplier transform into STEP.
fid='H743_Custom:Amphenol_10067099-200LF_RevH';rec=records[fid]
shape=cq.Compound.makeCompound(cq.importers.importStep(str(R/rec['file'])).vals())
shape=shape.rotate((0,0,0),(1,0,0),90).translate(rec['offset'])
cq.exporters.export(shape,str(M/'Amphenol_10067099-200LF_aligned.step'))
old=rec.copy();bind(fid,'Amphenol_10067099-200LF_aligned.step',rec['type']);records[fid]['source_transform']=old
dirs={str(child(l,'name')[1]):R/str(child(l,'uri')[1]).replace('${KIPRJMOD}/','') for l in children(parse((R/'fp-lib-table').read_text()),'lib')}
for fid,model in maps.items():
 lib,name=fid.split(':',1);p=dirs[lib]/(name+'.kicad_mod');s=p.read_text();n=parse(s)
 edits=[(m.start,m.end,'') for m in children(n,'model')];edits.append((n.end-1,n.end-1,'\n  '+dump(model)+'\n'));p.write_text(replace(s,edits))
for p in R.glob('*.kicad_pcb'):
 s=p.read_text();n=parse(s);edits=[]
 for fp in children(n,'footprint'):
  fid=str(fp[1]);edits.extend((m.start,m.end,'') for m in children(fp,'model'))
  if fid in maps:edits.append((fp.end-1,fp.end-1,'\n  '+dump(maps[fid])+'\n'))
 p.write_text(replace(s,edits))
(M/'BINDINGS.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')
print('Modeles lies:',len(maps),'dont enveloppes:',len(envelopes)+1)
