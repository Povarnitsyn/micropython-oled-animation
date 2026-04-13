import bpy

def create_oled_brain_material():
    # Принудительно ставим Cycles
    bpy.context.scene.render.engine = 'CYCLES'
    
    # 0. Делаем фон мира абсолютно черным (чтобы не было ореола)
    if bpy.context.scene.world:
        bpy.context.scene.world.use_nodes = True
        nodes_world = bpy.context.scene.world.node_tree.nodes
        nodes_world.clear()
        node_world_out = nodes_world.new(type='ShaderNodeOutputWorld')
        node_background = nodes_world.new(type='ShaderNodeBackground')
        node_background.inputs['Color'].default_value = (0, 0, 0, 1)
        node_background.inputs['Strength'].default_value = 0
        bpy.context.scene.world.node_tree.links.new(node_background.outputs['Background'], node_world_out.inputs['Surface'])

    mat_name = "OLED_Brain_Material"
    if mat_name in bpy.data.materials:
        bpy.data.materials.remove(bpy.data.materials[mat_name])
    
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # 1. Создаем ноды
    node_geo = nodes.new(type='ShaderNodeNewGeometry')
    node_math = nodes.new(type='ShaderNodeMath')
    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_emit = nodes.new(type='ShaderNodeEmission')
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    
    # 2. Настройка Math (Множитель чувствительности)
    node_math.operation = 'MULTIPLY'
    # ПОДБЕРИТЕ ЭТО ЗНАЧЕНИЕ: 
    # Если всё белое — уменьшайте (0.5), если всё черное — увеличивайте (2.0-5.0)
    node_math.inputs[1].default_value = 1.0 
    
    # 3. Настройка ColorRamp (Контраст извилин)
    ramp = node_ramp.color_ramp
    ramp.elements[0].position = 0.48  # Черный (глубина извилин)
    ramp.elements[1].position = 0.52  # Белый (выпуклости)
    
    # 4. Соединяем цепочку
    links.new(node_geo.outputs['Pointiness'], node_math.inputs[0])
    links.new(node_math.outputs['Value'], node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_emit.inputs['Color'])
    links.new(node_emit.outputs['Emission'], node_out.inputs['Surface'])
    
    # Назначаем материал
    obj = bpy.context.active_object
    if obj and obj.type == 'MESH':
        # Безопасная замена материала
        if not obj.data.materials:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat
        
        # Делаем объект активным для редактора шейдеров
        bpy.context.view_layer.objects.active = obj
        print(f"✅ Готово. Регулируй значение в ноде Math (Multiply) для контраста.")
    else:
        print("⚠️ Ошибка: Выделите 3D объект!")

create_oled_brain_material()
