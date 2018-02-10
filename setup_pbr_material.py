bpy.context.scene.render.engine = 'CYCLES'
bpy.context.space_data.context = 'MATERIAL'
bpy.context.area.type = 'NODE_EDITOR'

material = bpy.data.materials['Torus']
nodes = material.node_tree.nodes
links = material.node_tree.links

# clear default nodes
for node in nodes:
    nodes.remove(node)

# setup shader
shader = nodes.new(type="ShaderNodeBsdfPrincipled")
output = nodes.new(type="ShaderNodeOutputMaterial")
output.location = 400,0
link = links.new(shader.outputs[0], output.inputs[0])   

# setup baseColor
baseColor = nodes.new(type="ShaderNodeTexImage")
baseColor.name = 'BaseColor'
baseColor.location = -800,100
link = links.new(baseColor.outputs[0], shader.inputs[0])

# setup metalic
metalic = nodes.new(type="ShaderNodeTexImage")
metalic.name = 'Metalic'
metalic.location = -600,-100
link = links.new(metalic.outputs[0], shader.inputs[4])

# setup roughness
roughness = nodes.new(type="ShaderNodeTexImage")
roughness.name = 'Roughness'
roughness.location = -800,-100
link = links.new(roughness.outputs[0], shader.inputs[7])

# setup normal map
normalTexture = nodes.new(type="ShaderNodeTexImage")
normalTexture.name = 'Normal'
normalTexture.location = -800,-400
normalMap = nodes.new(type="ShaderNodeNormalMap")
normalMap.location = -400,-400

link = links.new(normalTexture.outputs[0], normalMap.inputs[1])
link = links.new(normalMap.outputs[0], shader.inputs[17])


#displacement = nodes.new(type="ShaderNodeTexImage")







