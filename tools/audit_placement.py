"""Conservative courtyard overlap and placement snapshot check for FC_01.

This supplements, but does not replace, KiCad DRC. Curved courtyards and
angled polygons are reduced to axis-aligned bounds and may yield false alarms.
"""
import json
import math
import pathlib
import sys

from kicad_sexpr import child, children, parse, props

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXED = set("J3 J13 J14 JP1 J8 J9 J11 J10 J7 J6 J4 J5 J1 J2 H1 H2 H3 H4 USB1 U8 U14 J12".split())


def outline(fp):
    at = child(fp, "at")
    ox, oy = map(float, at[1:3])
    angle = math.radians(float(at[3]) if len(at) > 3 else 0)
    points = []
    for item in fp:
        if not isinstance(item, list) or item[0] not in ("fp_rect", "fp_line", "fp_poly", "fp_circle"):
            continue
        if "CrtYd" not in str(child(item, "layer")[1]):
            continue
        if item[0] == "fp_poly":
            coords = [p[1:3] for p in children(child(item, "pts"), "xy")]
        elif item[0] == "fp_circle":
            coords = [child(item, key)[1:3] for key in ("center", "end")]
        else:
            coords = [child(item, key)[1:3] for key in ("start", "end")]
        for x, y in coords:
            x, y = float(x), float(y)
            points.append((ox + x * math.cos(angle) + y * math.sin(angle),
                           oy - x * math.sin(angle) + y * math.cos(angle)))
    if not points:
        return None
    return (min(p[0] for p in points), min(p[1] for p in points),
            max(p[0] for p in points), max(p[1] for p in points))


def main():
    board = parse((ROOT / "H743_Ardupilot.kicad_pcb").read_text())
    fps = {str(props(f)["Reference"]): f for f in children(board, "footprint")}
    boxes = {ref: outline(f) for ref, f in fps.items()}
    collisions = []
    for i, (a, fa) in enumerate(fps.items()):
        ba = boxes[a]
        if ba is None:
            continue
        for b, fb in list(fps.items())[i + 1:]:
            bb = boxes[b]
            if bb is None or child(fa, "layer")[1] != child(fb, "layer")[1]:
                continue
            dx = min(ba[2], bb[2]) - max(ba[0], bb[0])
            dy = min(ba[3], bb[3]) - max(ba[1], bb[1])
            if dx > 1e-6 and dy > 1e-6:
                collisions.append((a, b, round(dx, 3), round(dy, 3)))
    fixed = {r: list(child(fps[r], "at")[1:]) + [str(child(fps[r], "layer")[1])]
             for r in sorted(FIXED) if r in fps}
    baseline_changes = []
    if len(sys.argv) == 3 and sys.argv[1] == "--baseline":
        old = parse(pathlib.Path(sys.argv[2]).read_text())
        before = {str(props(f)["Reference"]): f for f in children(old, "footprint")}
        for ref in sorted(FIXED):
            a, b = before[ref], fps[ref]
            if child(a, "at")[1:] != child(b, "at")[1:] or child(a, "layer")[1] != child(b, "layer")[1]:
                baseline_changes.append(ref)
    oscillator_opposite_keepout = []
    osc = fps.get("Y1")
    if osc is not None:
        at = child(osc, "at")
        ox, oy = map(float, at[1:3])
        for zone in children(osc, "zone"):
            if str(child(zone, "layer")[1]) != "F.Cu":
                continue
            pts = [(ox + float(p[1]), oy + float(p[2]))
                   for p in children(child(child(zone, "polygon"), "pts"), "xy")]
            if not pts:
                continue
            zb = (min(x for x, y in pts), min(y for x, y in pts),
                  max(x for x, y in pts), max(y for x, y in pts))
            for ref, fp in fps.items():
                fb = boxes[ref]
                if ref == "Y1" or child(fp, "layer")[1] != "F.Cu" or fb is None:
                    continue
                if min(zb[2], fb[2]) > max(zb[0], fb[0]) and min(zb[3], fb[3]) > max(zb[1], fb[1]):
                    oscillator_opposite_keepout.append(ref)
    print(json.dumps({"fixed": fixed, "fixed_changed_from_baseline": baseline_changes,
                      "oscillator_opposite_keepout_overlaps": oscillator_opposite_keepout,
                      "courtyard_aabb_overlap": collisions,
                      "missing_courtyard": sorted(r for r, b in boxes.items() if b is None)}, indent=2))


if __name__ == "__main__":
    main()
