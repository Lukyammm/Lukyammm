"""Photoreal render of the book on velvet (Blender/Cycles via the bpy module).

usage: python book_scene.py --variant A|B [--w 540 --h 675 --samples 48 --out file.png]
  A: velvet backdrop behind the book, wet dark floor under it
  B: velvet sweep, the book stands on the velvet too
Writes <out> and <out>.json with the book outline in screen space (for the post pass).
"""
import argparse
import json
import math
import os

import bpy
import bmesh
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('--variant', default='A')
ap.add_argument('--w', type=int, default=540)
ap.add_argument('--h', type=int, default=675)
ap.add_argument('--samples', type=int, default=48)
ap.add_argument('--out', default=os.path.join(HERE, 'test.png'))
ap.add_argument('--book', default='en')
ap.add_argument('--key', type=float, default=1.0, help='key light multiplier')
ap.add_argument('--exposure', type=float, default=0.0)
ap.add_argument('--look', default='AgX - Punchy')
ap.add_argument('--view', default='AgX')
ap.add_argument('--spec', type=float, default=0.3)
args = ap.parse_args()

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
coll = scene.collection

IN = 0.0254
W, H, D = 6 * IN, 9 * IN, 1.3 * IN
TC = 0.00035      # cover board thickness
R = 0.0022        # rounded hinge where the cover folds around the spine


def setin(node, name, val):
    if name in node.inputs:
        node.inputs[name].default_value = val
    else:
        print('missing input', name)


def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for nd in list(nt.nodes):
        nt.nodes.remove(nd)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    return m, nt, b


def noise(nt, vec, scale, detail=2.0, rough=0.5):
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value = scale
    n.inputs['Detail'].default_value = detail
    n.inputs['Roughness'].default_value = rough
    nt.links.new(vec, n.inputs['Vector'])
    return n


def bump(nt, height, strength, distance, normal=None):
    bp = nt.nodes.new('ShaderNodeBump')
    bp.inputs['Strength'].default_value = strength
    bp.inputs['Distance'].default_value = distance
    nt.links.new(height, bp.inputs['Height'])
    if normal is not None:
        nt.links.new(normal, bp.inputs['Normal'])
    return bp


def maprange(nt, val, a, b, c, d, interp='LINEAR'):
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.interpolation_type = interp
    mr.inputs['From Min'].default_value = a
    mr.inputs['From Max'].default_value = b
    mr.inputs['To Min'].default_value = c
    mr.inputs['To Max'].default_value = d
    nt.links.new(val, mr.inputs['Value'])
    return mr


# ---------------------------------------------------------------- materials
def cover_material(img_path, crease_u):
    m, nt, b = new_mat('cover')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(img_path)
    tex.interpolation = 'Cubic'
    nt.links.new(tc.outputs['UV'], tex.inputs['Vector'])
    nt.links.new(tex.outputs['Color'], b.inputs['Base Color'])
    # laminated card: soft sheen, roughness that wanders a little
    rn = noise(nt, tc.outputs['Object'], 35, 6, 0.55)
    nt.links.new(maprange(nt, rn.outputs['Fac'], 0.3, 0.7, 0.46, 0.6).outputs['Result'], b.inputs['Roughness'])
    setin(b, 'Specular IOR Level', args.spec)
    setin(b, 'Coat Weight', 0.04 if args.spec > 0.2 else 0.0)
    setin(b, 'Coat Roughness', 0.35)
    # paper grain
    g = noise(nt, tc.outputs['Object'], 2600, 2, 0.6)
    b1 = bump(nt, g.outputs['Fac'], 0.05, 0.00015)
    # the score line of a paperback, a few mm from the spine on the front cover
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['UV'], sep.inputs['Vector'])
    sub = nt.nodes.new('ShaderNodeMath'); sub.operation = 'SUBTRACT'
    nt.links.new(sep.outputs['X'], sub.inputs[0]); sub.inputs[1].default_value = crease_u
    ab = nt.nodes.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'
    nt.links.new(sub.outputs['Value'], ab.inputs[0])
    groove = maprange(nt, ab.outputs['Value'], 0.0, 0.0006, 0.0, 1.0, 'SMOOTHSTEP')
    b2 = bump(nt, groove.outputs['Result'], 0.55, 0.0004, b1.outputs['Normal'])
    nt.links.new(b2.outputs['Normal'], b.inputs['Normal'])
    return m


def plain_material(name, color, rough):
    m, nt, b = new_mat(name)
    setin(b, 'Base Color', (*color, 1))
    setin(b, 'Roughness', rough)
    return m


def pages_material():
    m, nt, b = new_mat('pages')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (25, 5200, 25)     # many thin lines across the thickness
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    n = noise(nt, mp.outputs['Vector'], 1.0, 4, 0.6)
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = (0.5, 0.45, 0.36, 1)
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = (0.74, 0.68, 0.56, 1)
    nt.links.new(n.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    setin(b, 'Roughness', 0.82)
    bp = bump(nt, n.outputs['Fac'], 0.3, 0.00008)
    nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m


def velvet_material():
    m, nt, b = new_mat('velvet')
    setin(b, 'Base Color', (0.0025, 0.0035, 0.0100, 1))
    setin(b, 'Roughness', 1.0)
    setin(b, 'Specular IOR Level', 0.12)
    setin(b, 'Sheen Weight', 1.0)
    setin(b, 'Sheen Roughness', 0.3)
    setin(b, 'Sheen Tint', (0.12, 0.17, 0.42, 1))
    tc = nt.nodes.new('ShaderNodeTexCoord')
    # crushed pile: wide soft patches where the nap points another way
    n1 = noise(nt, tc.outputs['Object'], 7, 8, 0.62)
    b1 = bump(nt, n1.outputs['Fac'], 0.32, 0.004)
    # the pile itself
    n2 = noise(nt, tc.outputs['Object'], 2200, 2, 0.5)
    b2 = bump(nt, n2.outputs['Fac'], 0.22, 0.00025, b1.outputs['Normal'])
    nt.links.new(b2.outputs['Normal'], b.inputs['Normal'])
    return m


def wet_floor_material():
    m, nt, b = new_mat('wet_floor')
    setin(b, 'Base Color', (0.004, 0.005, 0.008, 1))
    setin(b, 'Specular IOR Level', 0.5)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    patches = noise(nt, tc.outputs['Object'], 2.2, 6, 0.6)
    nt.links.new(maprange(nt, patches.outputs['Fac'], 0.35, 0.65, 0.04, 0.32, 'SMOOTHSTEP').outputs['Result'], b.inputs['Roughness'])
    ripple = noise(nt, tc.outputs['Object'], 55, 3, 0.5)
    bp = bump(nt, ripple.outputs['Fac'], 0.06, 0.0006)
    nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m


# ---------------------------------------------------------------- book
def profile(off, seg=12):
    """Cross-section of the cover, from the back fore-edge, round the spine, to the front fore-edge.
    off = 0 gives the outer surface, off = TC the inner one."""
    r = R - off
    pts = [(W / 2, D / 2 - off), (-W / 2 + R, D / 2 - off)]
    c1 = (-W / 2 + R, D / 2 - R)
    for i in range(1, seg + 1):
        a = math.pi / 2 + (math.pi / 2) * i / seg
        pts.append((c1[0] + r * math.cos(a), c1[1] + r * math.sin(a)))
    c2 = (-W / 2 + R, -D / 2 + R)
    for i in range(1, seg + 1):
        a = math.pi + (math.pi / 2) * i / seg
        pts.append((c2[0] + r * math.cos(a), c2[1] + r * math.sin(a)))
    pts.append((W / 2, -D / 2 + off))
    return pts


def arclen(pts):
    s = [0.0]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        s.append(s[-1] + math.hypot(x1 - x0, y1 - y0))
    return s


def build_cover(mat_cover, mat_inner, mat_edge):
    me = bpy.data.meshes.new('cover')
    bm = bmesh.new()
    outer, inner = profile(0.0), profile(TC)
    s = arclen(outer)
    L = s[-1]
    zb, zt = -H / 2, H / 2
    ob = [bm.verts.new((x, y, zb)) for x, y in outer]
    ot = [bm.verts.new((x, y, zt)) for x, y in outer]
    ib = [bm.verts.new((x, y, zb)) for x, y in inner]
    it = [bm.verts.new((x, y, zt)) for x, y in inner]
    uv = bm.loops.layers.uv.new('UVMap')
    n = len(outer)
    arc_idx = set(range(1, n - 2))
    for i in range(n - 1):
        f = bm.faces.new((ob[i], ob[i + 1], ot[i + 1], ot[i]))
        f.material_index = 0
        f.smooth = i in arc_idx
        u0, u1 = s[i] / L, s[i + 1] / L
        for lp, (u, v) in zip(f.loops, ((u0, 0), (u1, 0), (u1, 1), (u0, 1))):
            lp[uv].uv = (u, v)
        f2 = bm.faces.new((ib[i + 1], ib[i], it[i], it[i + 1]))
        f2.material_index = 1
        f2.smooth = i in arc_idx
        for ring_a, ring_b, z in ((ot, it, zt), (ob, ib, zb)):
            if z > 0:
                f3 = bm.faces.new((ring_a[i], ring_a[i + 1], ring_b[i + 1], ring_b[i]))
            else:
                f3 = bm.faces.new((ring_b[i], ring_b[i + 1], ring_a[i + 1], ring_a[i]))
            f3.material_index = 2
    for j in (0, n - 1):
        f4 = bm.faces.new((ob[j], ot[j], it[j], ib[j]))
        f4.material_index = 2
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    for mt in (mat_cover, mat_inner, mat_edge):
        me.materials.append(mt)
    obj = bpy.data.objects.new('cover', me)
    coll.objects.link(obj)
    bv = obj.modifiers.new('bevel', 'BEVEL')
    bv.width = 0.00012
    bv.segments = 2
    bv.limit_method = 'ANGLE'
    # front score line position in the wrap texture
    front_start = s[-2] / L
    crease = front_start + 0.0065 / L
    return obj, crease


def build_pages(mat_pages):
    inner = profile(TC + 0.00005)
    gap = 0.0003
    poly = inner[1:-1]
    poly = [(W / 2 - gap, inner[0][1])] + poly + [(W / 2 - gap, inner[-1][1])]
    me = bpy.data.meshes.new('pages')
    bm = bmesh.new()
    zb, zt = -H / 2 + gap, H / 2 - gap
    bot = [bm.verts.new((x, y, zb)) for x, y in poly]
    top = [bm.verts.new((x, y, zt)) for x, y in poly]
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bm.faces.new(top)
    bm.faces.new(list(reversed(bot)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat_pages)
    obj = bpy.data.objects.new('pages', me)
    coll.objects.link(obj)
    bv = obj.modifiers.new('bevel', 'BEVEL')
    bv.width = 0.0005
    bv.segments = 3
    bv.limit_method = 'ANGLE'
    return obj


wrap = os.path.join(HERE, f'wrap_{args.book}.png')
cover_obj, crease_u = build_cover(bpy.data.materials.new('tmp'), plain_material('inner', (0.78, 0.78, 0.75), 0.8),
                                  plain_material('cut_edge', (0.55, 0.55, 0.52), 0.7))
cover_obj.data.materials[0] = cover_material(wrap, crease_u)
pages_obj = build_pages(pages_material())

book = bpy.data.objects.new('book', None)
coll.objects.link(book)
for o in (cover_obj, pages_obj):
    o.parent = book
ROT = 0.62
book.rotation_euler = (0, 0, ROT)
book.location = (0, 0, H / 2 + (0.0002 if args.variant == 'B' else 0.0))

# ---------------------------------------------------------------- set
YB = 0.42   # the velvet hangs this far behind the book


def grid_mesh(name, nu, nv, fn):
    """fn(u, v) -> (x, y, z) for u, v in [0, 1]."""
    verts = [fn(i / (nu - 1), j / (nv - 1)) for j in range(nv) for i in range(nu)]
    faces = [(j * nu + i, j * nu + i + 1, (j + 1) * nu + i + 1, (j + 1) * nu + i)
             for j in range(nv - 1) for i in range(nu - 1)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    for p in me.polygons:
        p.use_smooth = True
    obj = bpy.data.objects.new(name, me)
    coll.objects.link(obj)
    return obj


def folds(x, z):
    """Soft vertical folds of hanging fabric, a little looser near the floor."""
    a = (0.026 * math.sin(2 * math.pi * x / 0.33 + 0.7 + 0.6 * z)
         + 0.015 * math.sin(2 * math.pi * x / 0.19 + 2.1 - 0.9 * z)
         + 0.007 * math.sin(2 * math.pi * x / 0.097 + 4.0 + 1.5 * z))
    return a * (0.75 + 0.35 * max(0.0, 0.5 - z))


velvet = velvet_material()
if args.variant == 'A':
    back = grid_mesh('backdrop', 260, 120, lambda u, v: (-0.8 + 1.6 * u, YB + folds(-0.8 + 1.6 * u, -0.05 + 1.15 * v), -0.05 + 1.15 * v))
    back.data.materials.append(velvet)
    floor = grid_mesh('floor', 2, 2, lambda u, v: (-1.5 + 3.0 * u, -1.5 + (YB + 1.6) * v, 0.0))
    floor.data.materials.append(wet_floor_material())
else:
    RC = 0.2
    Y0 = YB - RC

    def sweep(u, v):
        x = -0.9 + 1.8 * u
        L1 = Y0 + 1.2            # flat part, from y = -1.2 to Y0
        L2 = math.pi * RC / 2    # the curve
        L3 = 1.1                 # hanging part
        s = v * (L1 + L2 + L3)
        if s < L1:
            y, z, ny, nz = -1.2 + s, 0.0, 0.0, 1.0
            k = min(1.0, max(0.0, (s - (L1 - 0.1)) / 0.1))
        elif s < L1 + L2:
            a = (s - L1) / RC
            y, z = Y0 + RC * math.sin(a), RC - RC * math.cos(a)
            ny, nz = -math.sin(a), math.cos(a)
            k = 1.0
        else:
            y, z, ny, nz = YB, RC + (s - L1 - L2), -1.0, 0.0
            k = 1.0
        # folds grow from the floor into the curve and up the backdrop, small ripples on the floor
        f = folds(x, z) * k + (0.0009 * math.sin(2 * math.pi * x / 0.21 + 5 * y) + 0.0006 * math.sin(2 * math.pi * x / 0.083 - 7 * y)) * (1 - k)
        return (x, y + ny * f, z + nz * f)
    back = grid_mesh('sweep', 300, 260, sweep)
    back.data.materials.append(velvet)

# ---------------------------------------------------------------- lights
target = Vector((0.0, 0.0, 0.11))


def area(name, size, size_y, energy, loc, color, aim=None, spread=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.shape = 'RECTANGLE'
    ld.size, ld.size_y = size, size_y
    ld.energy = energy
    ld.color = color
    if spread is not None:
        ld.spread = spread
    ob = bpy.data.objects.new(name, ld)
    coll.objects.link(ob)
    ob.location = loc
    d = (aim or target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob


k = args.key
# key from the front right: the cover takes the light, the spine falls into soft shade
area('key', 0.6, 0.8, 8 * k, (0.72, -0.42, 0.74), (1.0, 0.95, 0.88), spread=math.radians(50))
area('fill', 1.0, 1.0, 2.4 * k, (-0.9, -0.55, 0.25), (0.86, 0.9, 1.0))
# thin rims behind the book: one outlines the spine, the other the page edge
area('rim_l', 0.12, 0.7, 12 * k, (-0.38, 0.28, 0.45), (0.85, 0.9, 1.0), aim=Vector((-0.05, 0.0, 0.15)))
area('rim_r', 0.12, 0.7, 10 * k, (0.42, 0.3, 0.4), (1.0, 0.94, 0.86), aim=Vector((0.05, 0.0, 0.12)))
area('top', 0.4, 0.4, 1.1 * k, (0.0, 0.05, 0.75), (1.0, 0.97, 0.92))
# a narrow beam running along the velvet, which is what shows its folds and sheen
area('graze', 0.25, 1.0, 9 * k, (-0.95, YB - 0.04, 0.55), (0.8, 0.86, 1.0), aim=Vector((0.6, YB + 0.03, 0.3)), spread=math.radians(25))
area('pool', 0.6, 0.6, 3.5 * k, (0.08, -0.15, 0.95), (0.9, 0.93, 1.0), aim=Vector((0.05, YB, 0.28)), spread=math.radians(40))

world = bpy.data.worlds.new('world')
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.0015, 0.002, 0.004, 1)
bg.inputs['Strength'].default_value = 1.0

# ---------------------------------------------------------------- camera
cam_d = bpy.data.cameras.new('cam')
cam_d.lens = 85
cam_d.sensor_fit = 'VERTICAL'
cam_d.sensor_height = 36
cam = bpy.data.objects.new('cam', cam_d)
coll.objects.link(cam)
elev = math.radians(16)
dist = 0.80
look = Vector((0.0, 0.0, 0.112))
cam.location = look + dist * Vector((0, -math.cos(elev), math.sin(elev)))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam
front_center = Vector((D / 2 * math.sin(ROT), -D / 2 * math.cos(ROT), H / 2))
cam_d.dof.use_dof = True
cam_d.dof.focus_distance = (front_center - cam.location).length
cam_d.dof.aperture_fstop = 11

# ---------------------------------------------------------------- render
r = scene.render
r.engine = 'CYCLES'
r.resolution_x, r.resolution_y = args.w, args.h
r.resolution_percentage = 100
r.film_transparent = False
r.image_settings.file_format = 'PNG'
r.image_settings.color_depth = '8'
scene.cycles.device = 'CPU'
scene.cycles.samples = args.samples
scene.cycles.use_adaptive_sampling = True
scene.cycles.use_denoising = True
try:
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception as e:  # noqa: BLE001
    print('denoiser', e)
scene.cycles.max_bounces = 8
scene.cycles.caustics_reflective = False
scene.cycles.caustics_refractive = False
scene.cycles.blur_glossy = 0.6
try:
    scene.view_settings.view_transform = args.view
    for look_name in (args.look, 'AgX - Medium High Contrast', 'Medium High Contrast'):
        try:
            scene.view_settings.look = look_name
            break
        except TypeError:
            pass
except TypeError as e:
    print('view', e)
scene.view_settings.exposure = args.exposure
print('VIEW', scene.view_settings.view_transform, '|', scene.view_settings.look)
r.filepath = args.out
bpy.ops.render.render(write_still=True)

# book outline in screen space, so the glints stay off the book
depsgraph = bpy.context.evaluated_depsgraph_get()
pts = []
for o in (cover_obj, pages_obj):
    ev = o.evaluated_get(depsgraph)
    mw = o.matrix_world
    for v in ev.data.vertices:
        p = world_to_camera_view(scene, cam, mw @ v.co)
        pts.append((p.x * args.w, (1 - p.y) * args.h))
with open(args.out + '.json', 'w') as fh:
    json.dump({'book_pts': pts, 'w': args.w, 'h': args.h}, fh)
print('done', args.out)
