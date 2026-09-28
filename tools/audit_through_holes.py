"""Find opposite-face parts and copper pads intersecting through-hole lands.

This is a conservative 2D check; KiCad DRC and a mechanical review are still required.
"""
import json
import math
import sys
from pathlib import Path

from kicad_sexpr import child, children, parse, props
from audit_placement import outline

board_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'H743_Ardupilot.kicad_pcb'
board = parse(board_path.read_text())
parts = {str(props(f)['Reference']): f for f in children(board, 'footprint')}


def pad_box(fp, pad, extra=0):
    at = child(fp, 'at')
    theta = math.radians(float(at[3]) if len(at) > 3 else 0)
    pt = child(pad, 'at')
    x, y = map(float, pt[1:3])
    cx = float(at[1]) + x * math.cos(theta) + y * math.sin(theta)
    cy = float(at[2]) - x * math.sin(theta) + y * math.cos(theta)
    w, h = map(float, child(pad, 'size')[1:3])
    angle = math.radians(float(pt[3]) if len(pt) > 3 else 0)
    half_x = (abs(w * math.cos(angle)) + abs(h * math.sin(angle))) / 2 + extra
    half_y = (abs(w * math.sin(angle)) + abs(h * math.cos(angle))) / 2 + extra
    return cx - half_x, cy - half_y, cx + half_x, cy + half_y


def overlap(a, b):
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


issues = []
for source, fp in parts.items():
    side = str(child(fp, 'layer')[1])
    for hole in children(fp, 'pad'):
        if hole[2] not in ('thru_hole', 'np_thru_hole'):
            continue
        land = pad_box(fp, hole)
        for target, other in parts.items():
            if target == source or str(child(other, 'layer')[1]) == side:
                continue
            if not overlap(land, outline(other)):
                continue
            contacts = []
            for pad in children(other, 'pad'):
                if pad[2] == 'smd' and overlap(land, pad_box(other, pad)):
                    contacts.append({'pad': str(pad[1]), 'net': str(child(pad, 'net')[1])})
            issues.append({'hole_part': source, 'hole_pad': str(hole[1]),
                           'hole_type': str(hole[2]), 'hole_net': str(child(hole, 'net')[1]),
                           'opposite_part': target, 'opposite_pad_contacts': contacts})

print(json.dumps({'opposite_face_through_hole_issues': issues}, indent=2))
