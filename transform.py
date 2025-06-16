import bpy
import bmesh
from mathutils import Color

def quantize_color(c, precision=2):
    return tuple(round(v, precision) for v in c)

def color_to_material(color, material_cache, obj):
    if color in material_cache:
        return material_cache[color]

    hex_name = f"mat_{int(color[0]*255):02x}{int(color[1]*255):02x}{int(color[2]*255):02x}"
    mat = bpy.data.materials.new(name=hex_name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)

    obj.data.materials.append(mat)
    material_cache[color] = len(obj.data.materials) - 1  # Save index
    return material_cache[color]

def assign_materials_per_face_fast(obj):
    bpy.ops.object.mode_set(mode='OBJECT')
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()

    color_layer = bm.loops.layers.color.active
    if color_layer is None:
        print("❌ 没有找到顶点颜色层")
        return

    material_cache = {}

    # 遍历面
    for face in bm.faces:
        # 提取第一个顶点的颜色并量化
        color_raw = face.loops[0][color_layer]
        color = quantize_color((color_raw[0], color_raw[1], color_raw[2]), precision=2)

        mat_index = color_to_material(color, material_cache, obj)
        face.material_index = mat_index

    bm.to_mesh(mesh)
    bm.free()
    print(f"✅ 完成，每种颜色生成一个材质，共 {len(material_cache)} 个材质")

# 执行
obj = bpy.context.active_object
if obj and obj.type == 'MESH':
    assign_materials_per_face_fast(obj)
else:
    print("❌ 请先选择一个网格对象")
