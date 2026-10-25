"""Converte o GeoJSON dos estados em caminhos SVG simplificados (viewBox 0 0 1000 H).

Uso: python3 gerar_mapa.py <brazil-states.geojson> <saida.json>
Fonte usada: codeforgermany/click_that_hood (brazil-states.geojson).
"""
import json, math, sys

TOL = 1.6      # tolerância da simplificação, em unidades do viewBox
MIN_AREA = 12  # descarta ilhas menores que isso

def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy) or 1e-9
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        x, y = pts[i]
        d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / n
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return rdp(pts[: idx + 1], eps)[:-1] + rdp(pts[idx:], eps)
    return [pts[0], pts[-1]]

def area(r):
    return abs(sum(r[i][0] * r[i - 1][1] - r[i - 1][0] * r[i][1] for i in range(len(r)))) / 2

g = json.load(open(sys.argv[1]))
rings = []
for f in g["features"]:
    geom = f["geometry"]
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for p in polys:
        rings.append((f["properties"]["sigla"], p[0]))  # só o contorno externo
allpts = [pt for _, r in rings for pt in r]
lon0, lon1 = min(p[0] for p in allpts), max(p[0] for p in allpts)
lat0, lat1 = min(p[1] for p in allpts), max(p[1] for p in allpts)
k = math.cos(math.radians((lat0 + lat1) / 2))
W = 1000
s = W / ((lon1 - lon0) * k)
H = round((lat1 - lat0) * s)
proj = lambda p: ((p[0] - lon0) * k * s, (lat1 - p[1]) * s)

paths = {}
for uf, ring in rings:
    pts = [proj(p) for p in ring]
    if area(pts) < MIN_AREA:
        continue
    # anel fechado: divide no ponto mais distante do início antes de simplificar
    far = max(range(len(pts)), key=lambda i: math.dist(pts[0], pts[i]))
    pts = rdp(pts[: far + 1], TOL)[:-1] + rdp(pts[far:], TOL)
    if len(pts) < 4:
        continue
    d = "M" + "L".join(f"{x:.0f},{y:.0f}" for x, y in pts[:-1]) + "Z"
    paths[uf] = paths.get(uf, "") + d
rows = [{"uf": uf, "caminho": d, "largura": W, "altura": H} for uf, d in sorted(paths.items())]
json.dump(rows, open(sys.argv[2], "w"), ensure_ascii=False)
print(len(rows), "estados,", sum(len(r["caminho"]) for r in rows), "caracteres, viewBox", W, H)
