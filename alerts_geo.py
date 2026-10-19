"""alerts_geo.py: one-time builder of the region outlines for the live alert map (/alerts/).
Natural Earth 1:10m admin-1 (public domain) -> Russian federal subjects plus Crimea and Sevastopol, Lambert conformal
conic (lon0 100, standard parallels 50/70), simplified, written as SVG paths to data/alerts_regions.json.
Run with a venv that has pyshp + shapely:  python alerts_geo.py /path/to/ne_10m_admin_1_states_provinces"""
import sys, json, math, os
import shapefile
from shapely.geometry import shape, mapping
from shapely.ops import transform
R = 6371.0
def lcc(lon0, p1, p2, ph0):
    L0, P1, P2, PH0 = map(math.radians, (lon0, p1, p2, ph0))
    n = math.log(math.cos(P1) / math.cos(P2)) / math.log(math.tan(math.pi / 4 + P2 / 2) / math.tan(math.pi / 4 + P1 / 2))
    F = math.cos(P1) * math.tan(math.pi / 4 + P1 / 2) ** n / n; rho0 = R * F / math.tan(math.pi / 4 + PH0 / 2) ** n
    def proj(lon, lat):
        if lon < 0: lon += 360
        rho = R * F / math.tan(math.pi / 4 + math.radians(lat) / 2) ** n; th = n * (math.radians(lon) - L0)
        return rho * math.sin(th), -(rho0 - rho * math.cos(th))   # y down for SVG
    return proj
FULL = lcc(100, 50, 70, 60); WEST = lcc(45, 47, 62, 55)   # whole country; European Russia with the Urals, drawn upright
def paths(geom, proj, tol, keep):
    g = transform(lambda x, y, z=None: tuple(zip(*[proj(a, b) for a, b in zip(x, y)])), geom).buffer(0).simplify(tol, preserve_topology=True)
    polys = [g] if g.geom_type == 'Polygon' else list(g.geoms)
    polys = [p for p in polys if p.area > 60 or len(polys) == 1 or keep]
    c = g.representative_point()
    return ''.join('M' + 'L'.join(f'{x:.0f},{y:.0f}' for x, y in p.exterior.coords[:-1]) + 'Z' for p in polys), [round(c.x), round(c.y)]
def bbox(ds):
    xs = [float(v) for d in ds for v in d.replace('M', ' ').replace('L', ' ').replace('Z', ' ').replace(',', ' ').split()]
    return [min(xs[0::2]), min(xs[1::2]), max(xs[0::2]), max(xs[1::2])]
EN = {'RU-MOW': 'Moscow Oblast', 'RU-MOS': 'Moscow', 'RU-SPE': 'Saint Petersburg', 'UA-43': 'Crimea (occupied)', 'UA-40': 'Sevastopol (occupied)'}
def main(src):
    r = shapefile.Reader(src, encoding='utf-8'); out = {}
    for sr in r.iterShapeRecords():
        d = sr.record.as_dict(); iso = d['iso_3166_2']
        if not (iso.startswith('RU-') or iso in ('UA-43', 'UA-40')) or not d['name']: continue
        geom = shape(sr.shape.__geo_interface__); small = iso in ('RU-MOS', 'RU-SPE', 'UA-40')
        path, c = paths(geom, FULL, 4 if small else 9, small)
        out[iso] = {'ru': d['name_ru'], 'en': EN.get(iso, d['name_en'] or d['name']), 'd': path, 'c': c}
        if geom.representative_point().x < 62: out[iso]['dw'], out[iso]['cw'] = paths(geom, WEST, 2 if small else 4, small)
    bb = bbox([o['d'] for o in out.values()]); bw = bbox([o['dw'] for o in out.values() if 'dw' in o])
    json.dump({'source': 'Natural Earth 1:10m admin-1 (public domain), Lambert conformal conic', 'bbox': bb, 'bbox_west': bw, 'regions': out},
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'alerts_regions.json'), 'w'), ensure_ascii=False)
    print(len(out), 'regions', bb, bw, sum('dw' in o for o in out.values()), 'in the west view')
if __name__ == '__main__': main(sys.argv[1])
