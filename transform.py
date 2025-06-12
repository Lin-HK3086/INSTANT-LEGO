import bpy
import mathutils
from statistics import mean


VERTEX_COLOR_LAYER_NAME = "xuewang"


def run_vertex_color_to_materials():

    obj = bpy.context.active_object
    if not obj or obj.type != 'MESH':
        return

    mesh = obj.data

    if VERTEX_COLOR_LAYER_NAME not in mesh.vertex_colors:
        print(f"错误：模型上找不到名为 '{VERTEX_COLOR_LAYER_NAME}' 的顶点颜色层。")
        return

    vertex_colors = mesh.vertex_colors[VERTEX_COLOR_LAYER_NAME]

    mesh.materials.clear()
    print("已清空现有材质。")

    for face in mesh.polygons:
        
        face_colors = []
        for loop_index in face.loop_indices:
            color = vertex_colors.data[loop_index].color
            face_colors.append(color)

        if not face_colors:
            continue

        avg_r = mean(c[0] for c in face_colors)
        avg_g = mean(c[1] for c in face_colors)
        avg_b = mean(c[2] for c in face_colors)
        avg_a = mean(c[3] for c in face_colors)
        

        avg_color = mathutils.Vector((avg_r, avg_g, avg_b, avg_a))


        mat_name = f"Material_Face_{face.index}"
        new_mat = bpy.data.materials.new(name=mat_name)
        new_mat.use_nodes = True 
        
        principled_bsdf = new_mat.node_tree.nodes.get('Principled BSDF')
        if principled_bsdf:
            principled_bsdf.inputs['Base Color'].default_value = avg_color


        mesh.materials.append(new_mat)
        
        face.material_index = len(mesh.materials) - 1

    print(f"处理完成！共为 {len(mesh.polygons)} 个面创建了独立的材质。")


run_vertex_color_to_materials()
