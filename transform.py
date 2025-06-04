import bpy


def setup_vertex_color_material():


    obj = bpy.context.active_object
    if not obj:
        print("错误: 没有选中的活动物体。")
        # 可以通过 self.report 通知用户，但在简单脚本中 print 也可以
        # self.report({'ERROR'}, "没有选中的活动物体。")
        return


    if obj.type != 'MESH':
        print(f"错误: 物体 '{obj.name}' 不是网格类型。")
        return

    mesh = obj.data
    if not mesh:
        print(f"错误: 物体 '{obj.name}' 没有网格数据。")
        return


    if not mesh.color_attributes:
        print(f"错误: 网格 '{mesh.name}' 没有任何顶点颜色层 (颜色属性)。")
        print("请先在顶点绘制模式下为模型添加顶点颜色。")
        return


    vertex_color_layer = mesh.color_attributes[0]
    if not vertex_color_layer:
        print(f"错误: 无法获取网格 '{mesh.name}' 的有效顶点颜色层。")
        return

    vertex_color_layer_name = vertex_color_layer.name
    print(f"将使用顶点颜色层: '{vertex_color_layer_name}'")


    if not obj.material_slots:
        bpy.ops.object.material_slot_add()
        print(f"为物体 '{obj.name}' 添加了新的材质槽。")

    if obj.material_slots[0].material:
        mat = obj.material_slots[0].material
        print(f"使用物体 '{obj.name}' 的现有材质: '{mat.name}'")
    else:
        mat = bpy.data.materials.new(name=f"{obj.name}_VColorMat")
        obj.material_slots[0].material = mat
        print(f"为物体 '{obj.name}' 创建并分配了新材质: '{mat.name}'")


    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links





    color_attr_node = nodes.new(type='ShaderNodeAttribute')
    color_attr_node.attribute_type = 'GEOMETRY'
    color_attr_node.attribute_name = vertex_color_layer_name
    color_attr_node.location = (-300, 300)
    print(f"创建了 '颜色属性 (Color Attribute)' 节点，并设置为读取 '{vertex_color_layer_name}'。")

    principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled_node.location = (0, 300)
    print("创建了 '原理化BSDF (Principled BSDF)' 节点。")

    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (300, 300)
    print("创建了 '材质输出 (Material Output)' 节点。")

    links.new(color_attr_node.outputs['Color'], principled_node.inputs['Base Color'])
    print("连接: 颜色属性 (Color) -> 原理化BSDF (Base Color)")

    links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    print("连接: 原理化BSDF (BSDF) -> 材质输出 (Surface)")

    print(f"成功为物体 '{obj.name}' 设置了使用顶点颜色的材质 '{mat.name}'。")
    print("请切换到材质预览或渲染模式查看效果。")





