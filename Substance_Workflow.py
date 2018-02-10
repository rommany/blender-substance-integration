bl_info = {
    "name": "Substance Workflow",
    "author": "Rommany Allen",
    "version": (1, 0),
    "blender": (2, 70, 0),
    "location": "View3D > Object > ",
    "description": "Substance Designer worlkflows",
    "warning": "In Development",
    "wiki_url": "https://github.com/rommany/blender-substance-integration/wiki",
    "tracker_url": "",
    "category": "Import-Export"}

import os
from os.path import basename
import re
from collections import OrderedDict
from logging import log
import json



import bpy
from bpy.props import BoolProperty, BoolVectorProperty, FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, EnumProperty, StringProperty, PointerProperty
import bpy.utils.previews

from pysbs import context as sbsContext
from pysbs import sbsgenerator, sbsenum

icons_dict = bpy.utils.previews.new()

icons_dir = os.path.join(os.path.dirname(__file__), "icons")
#script_path = bpy.context.space_data.text.filepath

icons_dict.load("custom_icon", os.path.join(icons_dir, "icon.png"), 'IMAGE')
icon_value=icons_dict["custom_icon"].icon_id




class MaterialTrans(object):
    
    def __init__(self, *args, **kwargs):
        self.substance = args[0]
        self.material = args[1]
        self.name = self.material.name
        
        self.images = []
        
        for texslot in self.material.texture_slots:
            if texslot is not None and texslot.texture.type == 'IMAGE':
                if texslot.texture.image is not None:
                    self.images.append(texslot.texture.image)
                    
                    #texslot.texture.image.filepath

class Substance(object):
    
    def __init__(self, *args, **kwargs):
        
        
        # self.context = context.Context()
        # self.name = re.sub('blend','sbs', basename(bpy.data.filepath))
        # self.aDestFileAbsPath = bpy.path.abspath("//"+self.name)
        # self.sbsDoc = sbsgenerator.createSBSDocument(aContext,
        #                                              aFileAbsPath = aDestFileAbsPath,
        #                                              aGraphIdentifier = 'SimpleMaterial')
        # 
        # self.startPos = [48, 48, 0]
        # self.xOffset  = [192, 0, 0]
        # self.yOffset  = [0, 192, 0]
        
        self.materials = []
        for obj in bpy.data.objects:
            for matslot in obj.material_slots:
                newMat = MaterialTrans( self, matslot.material )
                #newMat.material = matslot.material
                #newMat.name = matslot.material.name
                self.materials.append(newMat)
                

def updateTextureNodes():
    
    textures = getSubstancePainterTextures()
    
    for material in bpy.data.materials:
        if material.name in textures:
            msg = material.name+ ' has substance paint'
            print('[SubstanceWorkflow]:', msg)
            # find node
            if material.node_tree != None:
                nodes = [n for n in material.node_tree.nodes if n.type == 'TEX_IMAGE']
                for node in nodes:
                    if node.name in textures[material.name]:
                        msg = node.name+ ' has substance paint'
                        print('[SubstanceWorkflow]:', msg)
                        
                        new_img = bpy.data.images.load(textures[material.name][node.name], check_existing=False)
                        material.node_tree  .nodes[node.name].image = new_img

   
'''Gets output textures from Substance Painter relative to the current blender file'''
def getSubstancePainterTextures():
    
    blendName = re.sub('\.blend','',basename(bpy.data.filepath) )
    sp_dir = bpy.data.filepath
    sp_dir = re.sub(basename(bpy.data.filepath),'Textures', sp_dir )
    
    rgx = blendName+'_(?P<material>\w+)_(?P<channel>\w+)\.(?P<filetype>\w+$)'
    
    regex = re.compile(rgx)
    
    results = {}
    
    materials = getMaterials()
    
    print(sp_dir)
    for _file in os.listdir(sp_dir):
        print (_file)
        match = regex.match(_file)
        if match:
            print (_file+'_MATCHED')
            matName = match.group('material')
            channel = match.group('channel')
            filetype = match.group('filetype')
            
            if matName not in results:
                results[matName] = {}
                
            relativePath = '//'+os.path.join('Textures', _file)
            results[matName][channel] = relativePath
                #if matName in materials:
                #    results[matName]['mat'] = materials[matName]
                
                #bpy.data.images.load(relativePath, check_existing=False)
            print ( results[matName][channel])  
                
                
    
    return results


def exportSelectedAsFbx():
    pass



def getMaterials():
    materials = {}
    for mat in bpy.data.materials:
        materials[mat.name] = mat
        
    return materials
        

def getObjects():
    mesh_objects = {}
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            mesh_objects.setdefault(ob.data, []).append(ob)
            
    print (mesh_objects)


def getTextures():
    for obj in bpy.data.objects:
        for matslot in obj.material_slots:
            for texslot in matslot.material.texture_slots:
                if texslot is not None and texslot.texture.type == 'IMAGE':
                    if texslot.texture.image is not None:
                        print('object', obj.name, 'has material',
                            matslot.material.name, 'that uses image',
                            texslot.texture.image.name)
                        print('It is saved at', texslot.texture.image.filepath)


def createBitmap(graph, texturePath, mapType):
    pass

def createSubstance():
    aContext = sbsContext.Context()
    
    
    
    
#aContext.getUrlAliasMgr().setAliasAbsPath(aAliasName = 'myAlias', aAbsPath = 'myAliasAbsolutePath')
 

    
    sbsName = re.sub('blend','sbs', basename(bpy.data.filepath))
 
    aDestFileAbsPath = bpy.path.abspath("//"+sbsName)
 
    startPos = [48, 48, 0]
    xOffset  = [192, 0, 0]
    yOffset  = [0, 192, 0]
     
    try:
        # Create a new SBSDocument from scratch, with a graph named 'SimpleMaterial'
        sbsDoc = sbsgenerator.createSBSDocument(aContext,
                                aFileAbsPath = aDestFileAbsPath,
                                aGraphIdentifier = 'SimpleMaterial')
     
        # Get the graph 'SimpleMaterial'
        aGraph = sbsDoc.getSBSGraph(aGraphIdentifier = 'SimpleMaterial')
        
     
        # Create three Uniform color nodes, for BaseColor, Roughness and Metallic
        baseColor = aGraph.createCompFilterNode(aFilter = sbsenum.FilterEnum.UNIFORM,
                            aParameters = {sbsenum.CompNodeParamEnum.OUTPUT_COLOR: [1, 0, 0, 1]},
                            aGUIPos     = startPos)
     
        roughness = aGraph.createCompFilterNode(aFilter = sbsenum.FilterEnum.UNIFORM,
                            aParameters = {sbsenum.CompNodeParamEnum.COLOR_MODE: sbsenum.ColorModeEnum.GRAYSCALE,
                                           sbsenum.CompNodeParamEnum.OUTPUT_COLOR: 0.3},
                            aGUIPos     = baseColor.getOffsetPosition(yOffset))
     
        metallic = aGraph.createCompFilterNode(aFilter = sbsenum.FilterEnum.UNIFORM,
                            aParameters = {sbsenum.CompNodeParamEnum.COLOR_MODE: sbsenum.ColorModeEnum.GRAYSCALE,
                                           sbsenum.CompNodeParamEnum.OUTPUT_COLOR: 0.6},
                            aGUIPos     = roughness.getOffsetPosition(yOffset))
     
        # Create three Output nodes, for BaseColor, Roughness and Metallic
        outBaseColor = aGraph.createOutputNode(aIdentifier = 'BaseColor',
                            aGUIPos = baseColor.getOffsetPosition(xOffset),
                            aUsages = {sbsenum.UsageEnum.BASECOLOR: sbsenum.ComponentsEnum.RGBA})
     
        outRoughness = aGraph.createOutputNode(aIdentifier = 'Roughness',
                            aGUIPos = roughness.getOffsetPosition(xOffset),
                            aUsages = {sbsenum.UsageEnum.ROUGHNESS: sbsenum.ComponentsEnum.RGBA})
     
        outMetallic = aGraph.createOutputNode(aIdentifier = 'Metallic',
                            aGUIPos = metallic.getOffsetPosition(xOffset),
                            aUsages = {sbsenum.UsageEnum.METALLIC: sbsenum.ComponentsEnum.RGBA})
     
        # Connect the Uniform color nodes to their respective Output node
        # (no need to precise aLeftNodeOutput and aRightNodeInput here as there is no ambiguity)
        aGraph.connectNodes(aLeftNode = baseColor, aRightNode = outBaseColor)
        aGraph.connectNodes(aLeftNode = roughness, aRightNode = outRoughness)
        aGraph.connectNodes(aLeftNode = metallic,  aRightNode = outMetallic)
     
        graphs = {}
     
     
        for obj in bpy.data.objects:
            for matslot in obj.material_slots:
                
                # create a new graph
                matGraph = sbsDoc.createGraph(aGraphIdentifier = matslot.material.name,
                aParameters = {sbsenum.CompNodeParamEnum.OUTPUT_FORMAT:sbsenum.OutputFormatEnum.FORMAT_16BITS},
                aInheritance= {sbsenum.CompNodeParamEnum.OUTPUT_FORMAT:sbsenum.ParamInheritanceEnum.ABSOLUTE})
                
                
                
                matBaseName = None
                
                
                for texslot in matslot.material.texture_slots:
                    if texslot is not None and texslot.texture.type == 'IMAGE':
                        if texslot.texture.image is not None:

                            
                            # get zbrush textures
                            regex = re.compile(r'(?P<name>\S+)_TXTR')
                            match = regex.match(texslot.texture.image.name)
                            if match:
                                
                                
                                #createBitmap(matGraph, texslot.texture.image.name, 'BASECOLOR' )
                                
                                
                                matBaseName = match.group('name')
                                
                                baseColor   = matGraph.createBitmapNode(aSBSDocument = sbsDoc,
                                aResourcePath  = texslot.texture.image.filepath,
                                #aGUIPos        = [y * x for y in yOffset],
                                aParameters    = {sbsenum.CompNodeParamEnum.COLOR_MODE:True},
                                aCookedFormat  = sbsenum.BitmapFormatEnum.JPG,
                                aCookedQuality = 1)
                                
                                
                                outBaseColor = matGraph.createOutputNode(aIdentifier = 'BaseColor',
                                aGUIPos = baseColor.getOffsetPosition(xOffset),
                                aUsages = {sbsenum.UsageEnum.BASECOLOR: sbsenum.ComponentsEnum.RGBA})
                                
                                matGraph.connectNodes(aLeftNode = baseColor, aRightNode = outBaseColor)
                                
                                
                            regex = re.compile(r'(?P<name>\S+)_NM')
                            match = regex.match(texslot.texture.image.name)
                            if match:
                                
                                matBaseName = match.group('name')
                                
                                normalMap   = matGraph.createBitmapNode(aSBSDocument = sbsDoc,
                                aResourcePath  = texslot.texture.image.filepath,
                                #aGUIPos        = [y * x for y in yOffset],
                                aParameters    = {sbsenum.CompNodeParamEnum.COLOR_MODE:True},
                                aCookedFormat  = sbsenum.BitmapFormatEnum.JPG,
                                aCookedQuality = 1)
                                
                                
                                outNormal = matGraph.createOutputNode(aIdentifier = 'Normal',
                                aGUIPos = baseColor.getOffsetPosition(xOffset),
                                aUsages = {sbsenum.UsageEnum.NORMAL: sbsenum.ComponentsEnum.RGB})
                                
                                matGraph.connectNodes(aLeftNode = normalMap, aRightNode = outNormal)
                                
                                
                            regex = re.compile(r'(?P<name>\S+)_DM')
                            match = regex.match(texslot.texture.image.name)
                            if match:
                                
                                matBaseName = match.group('name')
                                  
                                heightMap   = matGraph.createBitmapNode(aSBSDocument = sbsDoc,
                                aResourcePath  = texslot.texture.image.filepath,
                                #aGUIPos        = [y * x for y in yOffset],
                                aParameters    = {sbsenum.CompNodeParamEnum.COLOR_MODE:True},
                                aCookedFormat  = sbsenum.BitmapFormatEnum.JPG,
                                aCookedQuality = 1)
                                    
                                    
                                outHeight = matGraph.createOutputNode(aIdentifier = 'Height',
                                aGUIPos = baseColor.getOffsetPosition(xOffset),
                                aUsages = {sbsenum.UsageEnum.HEIGHT: sbsenum.ComponentsEnum.R})
                                    
                                matGraph.connectNodes(aLeftNode = heightMap, aRightNode = outHeight)
                                
                                
                            regex = re.compile(r'(?P<name>\S+)-AO')
                            match = regex.match(texslot.texture.image.name)
                            if match:
                            
                                
                                
                                matBaseName = match.group('name')
                                
                                
                                  
                                ambientOcclusion   = matGraph.createBitmapNode(aSBSDocument = sbsDoc,
                                aResourcePath  = bpy.path.abspath(texslot.texture.image.filepath),
                                #aGUIPos        = [y * x for y in yOffset],
                                aParameters    = {sbsenum.CompNodeParamEnum.COLOR_MODE:True},
                                aCookedFormat  = sbsenum.BitmapFormatEnum.JPG,
                                aCookedQuality = 1)
                                    
                                    
                                outAmbientOcclusion = matGraph.createOutputNode(aIdentifier = 'Ambient_Occlusion',
                                aGUIPos = baseColor.getOffsetPosition(xOffset),
                                aUsages = {sbsenum.UsageEnum.AMBIENT_OCCLUSION: sbsenum.ComponentsEnum.R})
                                    
                                matGraph.connectNodes(aLeftNode = ambientOcclusion, aRightNode = outAmbientOcclusion)
                                    
                            
                        print(texslot.texture.image.name)  
                            
                
                graphs[matslot.material.name] = matGraph
                
                            # get multimap exports 
                                
     
        # for k in getMaterials():
        #     secondGraph = sbsDoc.createGraph(aGraphIdentifier = k,
        #         aParameters = {sbsenum.CompNodeParamEnum.OUTPUT_FORMAT:sbsenum.OutputFormatEnum.FORMAT_16BITS},
        #         aInheritance= {sbsenum.CompNodeParamEnum.OUTPUT_FORMAT:sbsenum.ParamInheritanceEnum.ABSOLUTE})
        #     
        #     # Create three Uniform color nodes, for BaseColor, Roughness and Metallic
        #     baseColor = secondGraph.createCompFilterNode(aFilter = sbsenum.FilterEnum.UNIFORM,
        #                         aParameters = {sbsenum.CompNodeParamEnum.OUTPUT_COLOR: [1, 0, 0, 1]},
        #                         aGUIPos     = startPos)
        #  
        #     roughness = secondGraph.createCompFilterNode(aFilter = sbsenum.FilterEnum.UNIFORM,
        #                         aParameters = {sbsenum.CompNodeParamEnum.COLOR_MODE: sbsenum.ColorModeEnum.GRAYSCALE,
        #                                        sbsenum.CompNodeParamEnum.OUTPUT_COLOR: 0.3},
        #                         aGUIPos     = baseColor.getOffsetPosition(yOffset))
        #  
        #     metallic = secondGraph.createCompFilterNode(aFilter = sbsenum.FilterEnum.UNIFORM,
        #                         aParameters = {sbsenum.CompNodeParamEnum.COLOR_MODE: sbsenum.ColorModeEnum.GRAYSCALE,
        #                                        sbsenum.CompNodeParamEnum.OUTPUT_COLOR: 0.6},
        #                         aGUIPos     = roughness.getOffsetPosition(yOffset))
        #  
        #     # Create three Output nodes, for BaseColor, Roughness and Metallic
        #     outBaseColor = secondGraph.createOutputNode(aIdentifier = 'BaseColor',
        #                         aGUIPos = baseColor.getOffsetPosition(xOffset),
        #                         aUsages = {sbsenum.UsageEnum.BASECOLOR: sbsenum.ComponentsEnum.RGBA})
        #  
        #     outRoughness = secondGraph.createOutputNode(aIdentifier = 'Roughness',
        #                         aGUIPos = roughness.getOffsetPosition(xOffset),
        #                         aUsages = {sbsenum.UsageEnum.ROUGHNESS: sbsenum.ComponentsEnum.RGBA})
        #  
        #     outMetallic = secondGraph.createOutputNode(aIdentifier = 'Metallic',
        #                         aGUIPos = metallic.getOffsetPosition(xOffset),
        #                         aUsages = {sbsenum.UsageEnum.METALLIC: sbsenum.ComponentsEnum.RGBA})
        #  
        #     # Connect the Uniform color nodes to their respective Output node
        #     # (no need to precise aLeftNodeOutput and aRightNodeInput here as there is no ambiguity)
        #     secondGraph.connectNodes(aLeftNode = baseColor, aRightNode = outBaseColor)
        #     secondGraph.connectNodes(aLeftNode = roughness, aRightNode = outRoughness)
        #     secondGraph.connectNodes(aLeftNode = metallic,  aRightNode = outMetallic)
        # 
     
     
        # Write back the document structure into the destination .sbs file
        sbsDoc.writeDoc()
        #log.info("=> Resulting substance saved at %s", aDestFileAbsPath)
        return True
     
    except BaseException as error:
        #log.error("!!! [demoHelloWorld] Failed to create the new package")
        raise error


#bpy.ops.export_scene.fbx(filepath = yourpath, use_selection = True)

scn = None





### sbsbaker options
sbsbaker_global_options = OrderedDict()

sbsbaker_global_options['input-selection'] = bpy.props.StringProperty(
    name="input-selection",
    description='''Select a submesh/subgroup of a mesh.
Mesh subpart selection can be specified using this syntax for <arg>: <nodeName>@<materialId> where the additional
@<materialId> is optional. If no material id is specified, all the ids will be used for the process.
<nodeName> can either be the name of a mesh part or of a transform group. In this case, all the mesh parts parented
directly or inderectly to this node will be used for the process''',maxlen= 1024, default= "")


sbsbaker_global_options['inputs'] = bpy.props.StringProperty(
    name="inputs",
    description='''Mesh files to process.
This option is implicit, so you can just provide a list of files at the end of your arguments, they will be interpreted
as inputs.''', maxlen= 1024, default= "")


sbsbaker_global_options['name-suffix-high'] = bpy.props.StringProperty(name="name-suffix-high ", description="High Poly name suffix.", maxlen= 1024, default= "_high")
sbsbaker_global_options['name-suffix-low'] = bpy.props.StringProperty(name="name-suffix-low ", description="Low Poly name suffix.", maxlen= 1024, default= "_low")
sbsbaker_global_options['output-format'] = bpy.props.EnumProperty(items = [
        ('bmp', 'bmp', 'bmp'),
        ('dds', 'dds', 'dds'),
        ('bmp', 'bmp', 'bmp'),
        ('ico', 'ico', 'ico'),
        ('jpg', 'jpg', 'jpg'),
        ('jif', 'jif', 'jif'),
        ('jpeg', 'jpeg', 'jpeg'),
        ('jpe', 'jpe', 'jpe'),
        ('png', 'png', 'png'),
        ('tga', 'tga', 'tga'),
        ('targa', 'targa', 'targa'),
        ('tif', 'tif', 'tif'),
        ('tiff', 'tiff', 'tiff'),
        ('wap', 'wap', 'wap'),
        ('wbmp', 'wbmp', 'wbmp'),
        ('wbm', 'wbm', 'wbm'),
        ('hdr', 'hdr', 'hdr'),
        ('exr', 'exr', 'exr'),
        ('jp2', 'jp2', 'jp2'),
        ('webp', 'webp', 'webp'),
        ('jxr', 'jxr', 'jxr'),
        ('wdp', 'wdp', 'wdp'),
        ('hdp', 'hdp', 'hdp'),
        ('psd', 'psd', 'psd')],
                                 name="output-format",
                                 description="Format to use for output image file.",
                                 default="png")
    
sbsbaker_global_options['output-format-compression'] = bpy.props.EnumProperty(items = [
        ('raw', 'raw', 'raw'),
        ('dxt1', 'dxt1', 'dxt1'),
        ('dxt2', 'dxt2', 'dxt2'),
        ('dxt3', 'dxt3', 'dxt3'),
        ('dxt4', 'dxt4', 'dxt4'),
        ('dxt5', 'dxt5', 'dxt5'),
        ('ati1', 'ati1', 'ati1'),
        ('ati2', 'ati2', 'ati2')],
                                 name="output-format-compression",
                                 description="Dds compression to use for output image.",
                                 default="raw")

sbsbaker_global_options['output-name'] =  bpy.props.StringProperty(name="output-name", description='''Set the output name of the generated files, without the extension."The name is "{inputName}_{bakerName}" by default.
You can use the following patterns that will be replaced by the program when saving the result of the process:
- {inputName}. Replaced by the input name.
- {bakerName}. Replaced by the baker name.''', maxlen= 1024, default= "{inputName}_{bakerName}")


sbsbaker_global_options['per-fragment-binormal'] = bpy.props.BoolProperty(name="per-fragment-binormal", description=''' Controls whether the binormal of the tangent frame has to be computed in the fragment shader (true) or in the vertex shader (false).
- Set by default to 'false' for unitytspace tangent space plugin.
- Set by default to 'false' for mikktspace tangent space plugin.
- Set by default to 'true' otherwise.''', default=False)


sbsbaker_global_options['recompute-tangents'] = bpy.props.BoolProperty(
        name="recompute-tangents",
        description="Force to recompute tangents; do not load tangents from the mesh if available.",
        default=False)
    
sbsbaker_global_options['tangent-space-plugin'] = bpy.props.StringProperty(
        name="tangent-space-plugin",
        description='Set the plugin file used to compute the meshes tangent space frames.',
        maxlen= 1024,
        default= "/Applications/Substance Automation/plugins/tangentspace/libmikktspace.dylib")
    
sbsbaker_global_options['uv-set'] = EnumProperty(items = [
        ('0', 'UV 0', 'enum prop 1'),
        ('1', 'UV 1', 'enum prop 2'),
        ('2', 'UV 2', 'enum prop 2'),
        ('3', 'UV 3', 'enum prop 2'),
        ('4', 'UV 4', 'enum prop 2'),
        ('5', 'UV 5', 'enum prop 2'),
        ('6', 'UV 6', 'enum prop 2'),
        ('7', 'UV 7', 'enum prop 2')
        ], name="uv-set", description="Select UV set used to bake meshes information.", default="0")

sbsbaker_global_options['antialiasing'] = EnumProperty(items = [
        ('0', 'None', 'None'),
        ('1', 'Subsampling 2x2', 'Subsampling 2x2'),
        ('2', 'Subsampling 4x4', 'Subsampling 4x4'),
        ('3', 'Subsampling 8x8', 'Subsampling 8x8')],
                                name="antialiasing", description="Choosen antialiasing method", default="0")


sbsbaker_global_options['apply-diffusion'] = BoolProperty(name="apply-diffusion", description="Whether to use diffusion as a post-process after dilation, or not..", default=True)



sbsbaker_global_options['average-normals'] = BoolProperty(name="average-normals", description="Compute rays directions based on averaged normals.", default=True)
sbsbaker_global_options['details'] = FloatProperty(name="details", description="A lower value will be more precise but will easilly produce artefacts.", default=0.6)

sbsbaker_global_options['dilation-width'] = IntProperty(name="dilation-width", description="Width of the dilation post-process (in pixels) applied before diffusion.", default=1)

sbsbaker_global_options['normal'] = StringProperty(name="normal", description="External normal map from file", maxlen= 1024, default= "")

sbsbaker_global_options['normal-format'] =  EnumProperty(items = [('0', 'OpenGL', 'enum prop 1'), ('1', 'DirectX', 'enum prop 2') ],
                                name="normal-format",
                                description="Invert green component in normal map depending on selected format.",
                                default="1")

sbsbaker_global_options['normal-invert'] = BoolProperty(name="normal-invert", description="Invert the normals.", default=False)
sbsbaker_global_options['normal-world-space'] = BoolProperty(name="normal-world-space", description="Tell if the normal map is in world space.", default=False)

sbsbaker_global_options['output-size'] = EnumProperty(items = [
        ('0', '512 x 512', 'enum prop 1'),
        ('1', '1024 x 1024', 'enum prop 2'),
        ('2', '2048 x 2048', 'enum prop 2'),
        ('3', '4096 x 4096', 'enum prop 2')],
                                name="output-size", description="output size of the map", default="1")

sbsbaker_global_options['udim'] = StringProperty(name="udim", description="ID of the udim tile to bake. Only accepts MARI notation for now.", maxlen= 1024, default= "")


sbsbaker_global_options['cage-mesh'] = StringProperty(name="cage-mesh", description="Cage file.", maxlen= 1024, default= "")

sbsbaker_global_options['highdef-mesh'] = StringProperty(name="highdef-mesh", description="High definition meshes.", maxlen= 1024, default= "")


sbsbaker_global_options['ignore-backface']  = BoolProperty(name="ignore-backface", description="Ignore back-facing triangles when trying to match low and high resolution geometry.", default=True)


sbsbaker_global_options['invert-skew-correction']  = BoolProperty(name="invert-skew-correction", description="If enabled, bright areas correspond to averaged direction and dark areas correspond to straight directions.", default=False)
sbsbaker_global_options['match']  = EnumProperty(items = [('0', 'Always', 'Always'), ('1', 'By Mesh Name', 'By Mesh Name') ],
                                name="match",
                                description="Choose which method is used to match low and high resolution geometry.",
                                default="0")

sbsbaker_global_options['max-dist']  = FloatProperty(name="max-dist", description="Maximum Occluder Distance.", default=0.1)
sbsbaker_global_options['max-frontal'] = FloatProperty(name="max-frontal", description="Max frontal distance.", default=0.01)
sbsbaker_global_options['max-rear'] = FloatProperty(name="max-rear", description="Max rear distance.", default=0.01)
sbsbaker_global_options['min-dist'] = FloatProperty(name="min-dist", description="Minimum Occluder Distance (bias).", default=1e-5)

sbsbaker_global_options['normal'] = StringProperty(name="normal", description="External normal map from file", maxlen= 1024, default= "")
    
sbsbaker_global_options['normal-format'] =  EnumProperty(items = [('0', 'OpenGL', 'enum prop 1'), ('1', 'DirectX', 'enum prop 2') ],
                                name="normal-format",
                                description="Invert green component in normal map depending on selected format.",
                                default="1")

sbsbaker_global_options['relative-to-bbox'] = BoolProperty(name="relative-to-bbox", description="Interpret the max distances as a factor of the mesh bounding box.", default=True)


sbsbaker_global_options['skew-correction'] = BoolProperty(name="skew-correction", description="Straighten rays direction based on a grayscale texture to avoid projection deformation..", default=False)
sbsbaker_global_options['skew-map'] = StringProperty(name="skew-map", description="", maxlen= 1024, default= "")

sbsbaker_global_options['spread-angle'] = FloatProperty(name="spread-angle", description="Maximum spread angle of occlusion rays.", default=180.0)

sbsbaker_global_options['use-lowdef-as-highdef'] = BoolProperty(name="use-lowdef-as-highdef", description="Use the low poly mesh as the high poly mesh.", default=False)
sbsbaker_global_options['use-cage'] = BoolProperty(name="use-cage", description="Use cage to cast rays.", default=False)

sbsbaker_global_options['auto-normalize'] = BoolProperty(name="auto-normalize", description="Automatic normalization.", default=True)

sbsbaker_global_options['map-type'] =  EnumProperty(items = [('0', 'World Space', 'World Space'), ('1', 'Tangent Space', 'Tangent Space') ],
                                name="map-type",
                                description="Map type.",
                                default="1")

sbsbaker_global_options['normal-type']  =  EnumProperty(items = [
    ('0', 'Normal', 'Normal'),
    ('1', 'Tangent', 'Tangent'),
    ('2', 'Binormal', 'Binormal')],
                                name="normal-type",
                                description="Map type.",
                                default="0")

sbsbaker_global_options['axis']  =  EnumProperty(items = [
    ('0', 'X', 'X'),
    ('1', 'Y', 'Y'),
    ('2', 'Z', 'Z')],
                                name="axis",
                                description="Select which axis positions you want to bake.",
                                default="0")

sbsbaker_global_options['mode']  =  EnumProperty(items = [
    ('0', 'All Axis', 'All Axis'),
    ('1', 'One Axis', 'One Axis')],
                                name="mode",
                                description="Select the processing mode.",
                                default="0")

sbsbaker_global_options['normalization']  =  EnumProperty(items = [
    ('0', 'BBox', 'BBox'),
    ('1', 'BSphere', 'BSphere')],
                                name="normalization",
                                description="Select the processing mode.",
                                default="1")

sbsbaker_global_options['filtering-mode']  =  EnumProperty(items = [
    ('0', 'Nearest', 'Nearest'),
    ('1', 'Bilinear', 'Bilinear')],
                                name="filtering-mode",
                                description="Select the filtering mode used for texture pixel interpolation.",
                                default="1")

sbsbaker_global_options['high-poly-uv-set']  =  EnumProperty(items = [
    ('0', 'UV 0', 'UV 0'),
    ('1', 'UV 1', 'UV 1'),
    ('2', 'UV 2', 'UV 2')],
                                name="high-poly-uv-set",
                                description="Select UV set used to map the texture on the high resolution mesh.",
                                default="0")

sbsbaker_global_options['normal-map'] = BoolProperty(name="normal-map", description=" Makes the required computation to transfer tangent space normal map", default=False)

sbsbaker_global_options['texture-file'] = StringProperty(name="texture-file", description="Texture file to apply on the high resolution mesh.", maxlen= 1024, default= "")

sbsbaker_global_options['ignore-backface-secondary'] = BoolProperty(name="ignore-backface-secondary", description="Ignore back-facing triangles for occlusion rays.", default=True)

sbsbaker_global_options['max-dist-relative-scale'] = BoolProperty(
        name="max-dist-relative-scale",
        description="Interpret the Occluder Distance as a factor of the mesh bounding box",
        default=True)

sbsbaker_global_options['nb-second-rays'] = IntProperty(name="nb-second-rays", description="Number of secondary rays (in [1; 1000]).", default=64)

sbsbaker_global_options['ray-distrib'] = EnumProperty(items = [('0', 'Uniform', 'Uniform'), ('1', 'Cosine', 'Cosine') ],
                                name="ray-distrib",
                                description="Angular Distribution of Occlusion Rays.",
                                default="1")

sbsbaker_global_options['self-occlusion'] = EnumProperty(items = [('0', 'Always', 'Always'), ('1', 'Only Same Mesh Name', 'Only Same Mesh Name') ],
                                name="self-occlusion",
                                description="Choose what geometry will cause occlusion.",
                                default="0")

sbsbaker_global_options['uv-mode']  =  EnumProperty(items = [
    ('0', 'Random', 'Random'),
    ('1', 'Hue Shift', 'Hue Shift'),
    ('2', 'Grayscale', 'Grayscale'),
    ('3', 'Uniform', 'Uniform'),
    ('4', 'Material ID Color', 'Material ID Color')],
                                name="mode",
                                description="How svg shapes will be colored.",
                                default="1")

sbsbaker_global_options['padding'] = IntProperty(name="padding", description="Paddinto add to the svg shapes.", default= 0)


sbsbaker_global_options['direction']  =  EnumProperty(items = [
    ('0', 'From Texture', 'From Texture'),
    ('1', 'From uniform Vector', 'From uniform Vector')],
                                name="direction",
                                description="Input direction.",
                                default="1")

sbsbaker_global_options['direction-x'] = FloatProperty(name="direction-x", description="World space direction vector component.", default=0.0)
sbsbaker_global_options['direction-y'] = FloatProperty(name="direction-y", description="World space direction vector component.", default=-1.0)
sbsbaker_global_options['direction-z'] = FloatProperty(name="direction-z", description="World space direction vector component.", default=0.0)

sbsbaker_global_options['direction-file'] = StringProperty(
    name="direction-file",
    description="Input texture file giving a direction per pixel to be translated from world space coordinates to texture space coordinates..",
    maxlen= 1024, default= "")

## OLD
    
    #sbsbaker_global_options['relative-to-bbox'] = BoolProperty(name="relative-to-bbox", description="Interpret the max distances as a factor of the mesh bounding box.", default=True)

        

class ExportSelectAsFbxOperator(bpy.types.Operator):
    """ToolTip of UnityWorkflowOperator"""
    bl_idname = "addongen.exort_selected_as_fbx_operator"
    bl_label = "Export Selected"
    bl_options = {'REGISTER'}


    #@classmethod
    #def poll(cls, context):
    #    return context.object is not None
    
    def execute(self, context):
       
        fbxPath = re.sub('\.blend', '_'+bpy.context.selected_objects[0].name+'.fbx',bpy.data.filepath )
        bpy.ops.export_scene.fbx(filepath = fbxPath, axis_up='Z', use_selection = True)
        
        self.report({'INFO'}, "Exported Selected")
        return {'FINISHED'}
    
    #def invoke(self, context, event):
    #    wm.modal_handler_add(self)
    #    return {'RUNNING_MODAL'}  
    #    return wm.invoke_porps_dialog(self)
    #def modal(self, context, event):
    #def draw(self, context):

class UnityWorkflowOperator(bpy.types.Operator):
    """ToolTip of UnityWorkflowOperator"""
    bl_idname = "addongen.unity_workflow_operator"
    bl_label = "Unity Workflow Operator"
    bl_options = {'REGISTER'}


    #@classmethod
    #def poll(cls, context):
    #    return context.object is not None
    
    def execute(self, context):
        getObjects()
        
        substance = Substance()
        for mat in substance.materials:
            print (mat.name)
            for im in mat.images:
                print (im.filepath)
        
        self.report({'INFO'}, "Unity Workflow")
        return {'FINISHED'}
    
    #def invoke(self, context, event):
    #    wm.modal_handler_add(self)
    #    return {'RUNNING_MODAL'}  
    #    return wm.invoke_porps_dialog(self)
    #def modal(self, context, event):
    #def draw(self, context):

class ZBrushWorkflowOperator(bpy.types.Operator):
    """ToolTip of ZBrushWorkflowOperator"""
    bl_idname = "addongen.zbrush_workflow_operator"
    bl_label = "ZBrush Workflow Operator"
    bl_options = {'REGISTER'}


    #@classmethod
    #def poll(cls, context):
    #    return context.object is not None
    
    def execute(self, context):
        getTextures()
        #getMaterials()
        
        self.report({'INFO'}, "Zbrush Workflow")
        return {'FINISHED'}
    
    #def invoke(self, context, event):
    #    wm.modal_handler_add(self)
    #    return {'RUNNING_MODAL'}  
    #    return wm.invoke_porps_dialog(self)
    #def modal(self, context, event):
    #def draw(self, context):
    
class SubstanceWorkflowOperator(bpy.types.Operator):
    """ToolTip of SubstanceWorkflowOperator"""
    bl_idname = "addongen.substance_workflow_operator"
    bl_label = "Substance Workflow Operator"
    bl_options = {'REGISTER'}


    #@classmethod
    #def poll(cls, context):
    #    return context.object is not None
    
    def execute(self, context):
        #createSubstance()
        updateTextureNodes();
        #print ( json.dumps(getSubstancePainterTextures(), indent=2))
        self.report({'INFO'}, "Creating Substance")
        return {'FINISHED'}
    
    #def invoke(self, context, event):
    #    wm.modal_handler_add(self)
    #    return {'RUNNING_MODAL'}  
    #    return wm.invoke_porps_dialog(self)
    #def modal(self, context, event):
    #def draw(self, context):

class SubstanceWorkflowPanel(bpy.types.Panel):
    """Docstring of SubstanceWorkflowPanel"""
    bl_idname = "VIEW3D_PT_substance_workflow"
    bl_label = "Workflow"
    
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Tools'
    
    #Panels in ImageEditor are using .poll() instead of bl_context.
    #@classmethod
    #def poll(cls, context):
    #    return context.space_data.show_paint
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        # row = box.row()
        # row.operator(SubstanceWorkflowOperator.bl_idname, text = "Create SBS", icon_value=custom_icons["substance_designer"].icon_id)
        # 
        # row.operator(ZBrushWorkflowOperator.bl_idname, text = "ZBrush Workflow", icon_value=custom_icons["zbrush"].icon_id)
        # row.operator(UnityWorkflowOperator.bl_idname, text = "Unity Workflow", icon_value=custom_icons["unity"].icon_id)
        # row.operator(ExportSelectAsFbxOperator.bl_idname, text = "Export Selected", icon_value=custom_icons["unity"].icon_id)
        # 
        
        scene = context.scene
        mytool = scene.sbsbaker_InputAndOutput_options
        
        ao_opts = scene.sbsbaker_AmbientOcclusion_options
        
        
        
        #row = box.row()
        #box.prop(mytool, "workflow_context", text="Context")
        
        # box.prop(mytool, "ambient_occlusion", text="ambient_occlusion")
        # box.prop(mytool, "ambient_occlusion_from_mesh", text="ambient_occlusion_from_mesh")
        # box.prop(mytool, "bent_normal_from_mesh", text="bent_normal_from_mesh")
        # box.prop(mytool, "color_from_mesh", text="color_from_mesh")
        # box.prop(mytool, "curvature", text="curvature")
        # box.prop(mytool, "curvature_from_mesh", text="curvature_from_mesh")
        # box.prop(mytool, "height_from_mesh", text="height_from_mesh")
        # box.prop(mytool, "normal_from_mesh", text="normal_from_mesh")
        # box.prop(mytool, "normal_world_space", text="normal_world_space")
        # box.prop(mytool, "opacity_mask_from_mesh", text="opacity_mask_from_mesh")
        # box.prop(mytool, "position", text="position")
        # box.prop(mytool, "position_from_mesh", text="position_from_mesh")
        # box.prop(mytool, "texture_from_mesh", text="texture_from_mesh")
        # box.prop(mytool, "thickness_from_mesh", text="thickness_from_mesh")
        # box.prop(mytool, "uv_map", text="uv_map")
        # box.prop(mytool, "world_space_direction", text="world_space_direction")
        
        box.prop(mytool, "input_selection", text="input_selection")
        box.prop(mytool, "inputs", text="inputs")
        box.prop(mytool, "name_suffix_high", text="name_suffix_high")
        box.prop(mytool, "name_suffix_low", text="name_suffix_low")
        box.prop(mytool, "output_format", text="output_format")
        box.prop(mytool, "output_format_compression", text="output_format_compression")
        box.prop(mytool, "output_name", text="output_name")
        box.prop(mytool, "per_fragment_binormal", text="per_fragment_binormal")
        box.prop(mytool, "recompute_tangents", text="recompute_tangents")
        box.prop(mytool, "tangent_space_plugin", text="tangent_space_plugin")
        
        
        box.prop(ao_opts, "apply_diffusion", text="apply_diffusion")
        box.prop(ao_opts, "details", text="details")
        box.prop(ao_opts, "dilation_width", text="dilation_width")
        box.prop(ao_opts, "normal", text="normal")
        box.prop(ao_opts, "normal_format", text="normal_format")
        box.prop(ao_opts, "normal_invert", text="normal_invert")
        box.prop(ao_opts, "normal_world_space", text="normal_world_space")
        box.prop(ao_opts, "output_size", text="output_size")
        box.prop(ao_opts, "quality", text="quality")
        box.prop(ao_opts, "spread", text="spread")
        box.prop(ao_opts, "udim", text="udim")
        box.prop(ao_opts, "use_neighbors", text="use_neighbors")


    
    
    
    
    
    
    


class SubstanceWorkflowMenu(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_substance_workflow"
    bl_label = "Substance Workflow Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator(SubstanceWorkflowOperator.bl_idname)
        layout.separator()
        layout.menu("VIEW3D_MT_transform")
        layout.operator_menu_enum("object.select_by_type", "type", text="Select All by Type...")



############

class sbsbaker_InputAndOutputOptions(bpy.types.PropertyGroup):
    input_selection = StringProperty(name="input-selection", description='''Select a submesh/subgroup of a mesh.
Mesh subpart selection can be specified using this syntax for <arg>: <nodeName>@<materialId> where the additional
@<materialId> is optional. If no material id is specified, all the ids will be used for the process.
<nodeName> can either be the name of a mesh part or of a transform group. In this case, all the mesh parts parented
directly or inderectly to this node will be used for the process''', maxlen= 1024, default= "")
    
    inputs = StringProperty(name="inputs", description='''Mesh files to process.
This option is implicit, so you can just provide a list of files at the end of your arguments, they will be interpreted
as inputs.''', maxlen= 1024, default= "")
    
    name_suffix_high = StringProperty(name="name-suffix-high ", description="High Poly name suffix.", maxlen= 1024, default= "_high")
    name_suffix_low = StringProperty(name="name-suffix-low ", description="Low Poly name suffix.", maxlen= 1024, default= "_low")
    
    output_format = EnumProperty(items = [
        ('bmp', 'bmp', 'bmp'),
        ('dds', 'dds', 'dds'),
        ('bmp', 'bmp', 'bmp'),
        ('ico', 'ico', 'ico'),
        ('jpg', 'jpg', 'jpg'),
        ('jif', 'jif', 'jif'),
        ('jpeg', 'jpeg', 'jpeg'),
        ('jpe', 'jpe', 'jpe'),
        ('png', 'png', 'png'),
        ('tga', 'tga', 'tga'),
        ('targa', 'targa', 'targa'),
        ('tif', 'tif', 'tif'),
        ('tiff', 'tiff', 'tiff'),
        ('wap', 'wap', 'wap'),
        ('wbmp', 'wbmp', 'wbmp'),
        ('wbm', 'wbm', 'wbm'),
        ('hdr', 'hdr', 'hdr'),
        ('exr', 'exr', 'exr'),
        ('jp2', 'jp2', 'jp2'),
        ('webp', 'webp', 'webp'),
        ('jxr', 'jxr', 'jxr'),
        ('wdp', 'wdp', 'wdp'),
        ('hdp', 'hdp', 'hdp'),
        ('psd', 'psd', 'psd')],
                                 name="output-format",
                                 description="Format to use for output image file.",
                                 default="png")
    
    output_format_compression  = EnumProperty(items = [
        ('raw', 'raw', 'raw'),
        ('dxt1', 'dxt1', 'dxt1'),
        ('dxt2', 'dxt2', 'dxt2'),
        ('dxt3', 'dxt3', 'dxt3'),
        ('dxt4', 'dxt4', 'dxt4'),
        ('dxt5', 'dxt5', 'dxt5'),
        ('ati1', 'ati1', 'ati1'),
        ('ati2', 'ati2', 'ati2')],
                                 name="output-format-compression",
                                 description="Dds compression to use for output image.",
                                 default="raw")

    output_name = StringProperty(name="output-name ", description='''Set the output name of the generated files, without the extension."The name is "{inputName}_{bakerName}" by default.
You can use the following patterns that will be replaced by the program when saving the result of the process:
- {inputName}. Replaced by the input name.
- {bakerName}. Replaced by the baker name.''', maxlen= 1024, default= "{inputName}_{bakerName}")


    per_fragment_binormal = BoolProperty(name="per-fragment-binormal", description=''' Controls whether the binormal of the tangent frame has to be computed in the fragment shader (true) or in the vertex shader (false).
- Set by default to 'false' for unitytspace tangent space plugin.
- Set by default to 'false' for mikktspace tangent space plugin.
- Set by default to 'true' otherwise.''', default=False)
    
    recompute_tangents = BoolProperty(
        name="recompute-tangents",
        description="Force to recompute tangents; do not load tangents from the mesh if available.",
        default=False)
    
    tangent_space_plugin = StringProperty(
        name="tangent-space-plugin",
        description='Set the plugin file used to compute the meshes tangent space frames.',
        maxlen= 1024,
        default= "/Applications/Substance Automation/plugins/tangentspace/libmikktspace.dylib")

class sbsbaker_AmbientOcclusionOptions(bpy.types.PropertyGroup):
    apply_diffusion = BoolProperty(name="apply-diffusion", description="Whether to use diffusion as a post-process after dilation, or not..", default=True)
    details = FloatProperty(name="details", description="A lower value will be more precise but will easilly produce artefacts.", default=0.6)
    dilation_width = IntProperty(name="dilation-width", description="Width of the dilation post-process (in pixels) applied before diffusion.", default=1)
    normal = StringProperty(name="normal", description="External normal map from file", maxlen= 1024, default= "")
    
    normal_format =  EnumProperty(items = [('0', 'OpenGL', 'enum prop 1'), ('1', 'DirectX', 'enum prop 2') ],
                                name="normal-format",
                                description="Invert green component in normal map depending on selected format.",
                                default="1")
    
    normal_invert = BoolProperty(name="normal-invert", description="Invert the normals.", default=False)
    normal_world_space = BoolProperty(name="normal-world-space", description="Tell if the normal map is in world space.", default=False)

    output_size = EnumProperty(items = [
        ('0', '512 x 512', 'enum prop 1'),
        ('1', '1024 x 1024', 'enum prop 2'),
        ('2', '2048 x 2048', 'enum prop 2'),
        ('3', '4096 x 4096', 'enum prop 2')],
                                name="output-size", description="output size of the map", default="1")
    
    quality = EnumProperty(items = [
        ('0', 'Low', 'enum prop 1'),
        ('1', 'Medium', 'enum prop 2'),
        ('2', 'High', 'enum prop 2'),
        ('3', 'Very High', 'enum prop 2')],
                                name="quality", description="Quality of the ambient occlusion. A higher quality is slower.", default="1")
    

    spread = FloatProperty(name="spread", description="Spread of the ambient occlusion.", default=0.01)

    udim = StringProperty(name="udim", description="ID of the udim tile to bake. Only accepts MARI notation for now.", maxlen= 1024, default= "")
    
    use_neighbors = BoolProperty(name="use-neighbors", description="Use unselected mesh parts to compute the ambient occlusion.", default=False)


    uv_set = EnumProperty(items = [
        ('0', 'UV 0', 'enum prop 1'),
        ('1', 'UV 1', 'enum prop 2'),
        ('2', 'UV 2', 'enum prop 2'),
        ('3', 'UV 3', 'enum prop 2'),
        ('4', 'UV 4', 'enum prop 2'),
        ('5', 'UV 5', 'enum prop 2'),
        ('6', 'UV 6', 'enum prop 2'),
        ('7', 'UV 7', 'enum prop 2')
        ], name="uv-set", description="Select UV set used to bake meshes information.", default="1")




#########
class SubstanceWorkflowProps(bpy.types.PropertyGroup):
    my_bool =     BoolProperty(name="", description="", default=False)
    
    
    bakeNormalFromMesh =     BoolProperty(name="", description="", default=False)
    bakeAOFromMesh =     BoolProperty(name="", description="", default=False)
    
    
    ambient_occlusion = BoolProperty(name="", description="", default=False)
    ambient_occlusion_from_mesh = BoolProperty(name="", description="", default=False)
    bent_normal_from_mesh = BoolProperty(name="", description="", default=False)
    color_from_mesh = BoolProperty(name="", description="", default=False)
    curvature = BoolProperty(name="", description="", default=False)
    curvature_from_mesh = BoolProperty(name="", description="", default=False)
    height_from_mesh = BoolProperty(name="", description="", default=False)
    normal_from_mesh = BoolProperty(name="", description="", default=False)
    normal_world_space = BoolProperty(name="", description="", default=False)
    opacity_mask_from_mesh = BoolProperty(name="", description="", default=False)
    position = BoolProperty(name="", description="", default=False)
    position_from_mesh = BoolProperty(name="", description="", default=False)
    texture_from_mesh = BoolProperty(name="", description="", default=False)
    thickness_from_mesh = BoolProperty(name="", description="", default=False)
    uv_map = BoolProperty(name="", description="", default=False)
    world_space_direction = BoolProperty(name="", description="", default=False)
    
    
    my_boolVec =  BoolVectorProperty(name="", description="", default=(False, False, False))
    my_float =    FloatProperty(name="", description="", default=0.0)
    my_floatVec = FloatVectorProperty(name="", description="", default=(0.0, 0.0, 0.0)) 
    my_int =      IntProperty(name="", description="", default=0)  
    my_intVec =   IntVectorProperty(name="", description="", default=(0, 0, 0))
    my_string =   StringProperty(name="String Value", description="", default="", maxlen=0)
    workflow_context =  EnumProperty(items = [('ENUM1', 'Model', 'enum prop 1'),
        ('ENUM2', 'Surface', 'enum prop 2'),
        ('ENUM3', 'Animation', 'enum prop 2')
        ],
                                    name="Workflow Context",
                                    description="",
                                    default="ENUM1")


class SbsBakerIOOperator(bpy.types.Operator):
    bl_idname = "sbsbaker.io"  
    bl_label = "sbsbaker io"  
    bl_options = {"REGISTER", "UNDO"}
    
    input_selection = bpy.props.StringProperty(name="input-selection", description='''Select a submesh/subgroup of a mesh.
Mesh subpart selection can be specified using this syntax for <arg>: <nodeName>@<materialId> where the additional
@<materialId> is optional. If no material id is specified, all the ids will be used for the process.
<nodeName> can either be the name of a mesh part or of a transform group. In this case, all the mesh parts parented
directly or inderectly to this node will be used for the process''', maxlen= 1024, default= "")
    
    inputs = bpy.props.StringProperty(name="inputs", description='''Mesh files to process.
This option is implicit, so you can just provide a list of files at the end of your arguments, they will be interpreted
as inputs.''', maxlen= 1024, default= "")
    
    name_suffix_high = bpy.props.StringProperty(name="name-suffix-high ", description="High Poly name suffix.", maxlen= 1024, default= "_high")
    name_suffix_low = bpy.props.StringProperty(name="name-suffix-low ", description="Low Poly name suffix.", maxlen= 1024, default= "_low")
    
    output_format = bpy.props.EnumProperty(items = [
        ('bmp', 'bmp', 'bmp'),
        ('dds', 'dds', 'dds'),
        ('bmp', 'bmp', 'bmp'),
        ('ico', 'ico', 'ico'),
        ('jpg', 'jpg', 'jpg'),
        ('jif', 'jif', 'jif'),
        ('jpeg', 'jpeg', 'jpeg'),
        ('jpe', 'jpe', 'jpe'),
        ('png', 'png', 'png'),
        ('tga', 'tga', 'tga'),
        ('targa', 'targa', 'targa'),
        ('tif', 'tif', 'tif'),
        ('tiff', 'tiff', 'tiff'),
        ('wap', 'wap', 'wap'),
        ('wbmp', 'wbmp', 'wbmp'),
        ('wbm', 'wbm', 'wbm'),
        ('hdr', 'hdr', 'hdr'),
        ('exr', 'exr', 'exr'),
        ('jp2', 'jp2', 'jp2'),
        ('webp', 'webp', 'webp'),
        ('jxr', 'jxr', 'jxr'),
        ('wdp', 'wdp', 'wdp'),
        ('hdp', 'hdp', 'hdp'),
        ('psd', 'psd', 'psd')],
                                 name="output-format",
                                 description="Format to use for output image file.",
                                 default="png")
    
    output_format_compression  = bpy.props.EnumProperty(items = [
        ('raw', 'raw', 'raw'),
        ('dxt1', 'dxt1', 'dxt1'),
        ('dxt2', 'dxt2', 'dxt2'),
        ('dxt3', 'dxt3', 'dxt3'),
        ('dxt4', 'dxt4', 'dxt4'),
        ('dxt5', 'dxt5', 'dxt5'),
        ('ati1', 'ati1', 'ati1'),
        ('ati2', 'ati2', 'ati2')],
                                 name="output-format-compression",
                                 description="Dds compression to use for output image.",
                                 default="raw")

    output_name = bpy.props.StringProperty(name="output-name ", description='''Set the output name of the generated files, without the extension."The name is "{inputName}_{bakerName}" by default.
You can use the following patterns that will be replaced by the program when saving the result of the process:
- {inputName}. Replaced by the input name.
- {bakerName}. Replaced by the baker name.''', maxlen= 1024, default= "{inputName}_{bakerName}")


    per_fragment_binormal = bpy.props.BoolProperty(name="per-fragment-binormal", description=''' Controls whether the binormal of the tangent frame has to be computed in the fragment shader (true) or in the vertex shader (false).
- Set by default to 'false' for unitytspace tangent space plugin.
- Set by default to 'false' for mikktspace tangent space plugin.
- Set by default to 'true' otherwise.''', default=False)
    
    recompute_tangents = bpy.props.BoolProperty(
        name="recompute-tangents",
        description="Force to recompute tangents; do not load tangents from the mesh if available.",
        default=False)
    
    tangent_space_plugin = bpy.props.StringProperty(
        name="tangent-space-plugin",
        description='Set the plugin file used to compute the meshes tangent space frames.',
        maxlen= 1024,
        default= "/Applications/Substance Automation/plugins/tangentspace/libmikktspace.dylib")
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"} 

# <<OLD

######## sbsbaker option panels
class SbsBakerAmbientOcclutsonOperator(bpy.types.Operator): 
    bl_idname = "sbsbaker.ambientocclusion"  
    bl_label = "sbsbaker ambient-occlusion options"  
    bl_options = {"REGISTER", "UNDO"}

    global sbsbaker_global_options

    # input_selection = sbsbaker_global_options['input-selection']
    # inputs = sbsbaker_global_options['inputs']
    # name_suffix_high = sbsbaker_global_options['name-suffix-high']
    # name_suffix_low = sbsbaker_global_options['name-suffix-low']
    # output_format =sbsbaker_global_options['output-format']
    # output_format_compression =sbsbaker_global_options['output-format-compression']
    # output_name =sbsbaker_global_options['output-name']
    # per_fragment_binormal =sbsbaker_global_options['per-fragment-binormal']
    # recompute_tangents =sbsbaker_global_options['recompute-tangents']
    # tangent_space_plugin =sbsbaker_global_options['tangent-space-plugin']


    # ambient-occlusion 
    apply_diffusion = sbsbaker_global_options['apply-diffusion']
    details = sbsbaker_global_options['details']
    dilation_width = sbsbaker_global_options['dilation-width']
    normal = sbsbaker_global_options['normal']
    normal_format =  sbsbaker_global_options['normal-format']
    normal_invert = sbsbaker_global_options['normal-invert']
    normal_world_space = sbsbaker_global_options['normal-world-space']
    output_size = sbsbaker_global_options['output-size']
    
    quality = EnumProperty(items = [
        ('0', 'Low', 'enum prop 1'),
        ('1', 'Medium', 'enum prop 2'),
        ('2', 'High', 'enum prop 2'),
        ('3', 'Very High', 'enum prop 2')],
                                name="quality", description="Quality of the ambient occlusion. A higher quality is slower.", default="1")
    
    spread = FloatProperty(name="spread", description="Spread of the ambient occlusion.", default=0.01)
    udim = sbsbaker_global_options['udim']
    use_neighbors = BoolProperty(name="use-neighbors", description="Use unselected mesh parts to compute the ambient occlusion.", default=False)
    uv_set = sbsbaker_global_options['uv-set']
    
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"} 

class SbsBakerAmbientOcclutsonFromMeshOperator(bpy.types.Operator): 
    bl_idname = "sbsbaker.ambientocclusion_from_mesh"
    bl_label = "sbsbaker ambient-occlusion options"  
    bl_options = {"REGISTER", "UNDO"} 

    global sbsbaker_global_options

    # input_selection = sbsbaker_global_options['input-selection']
    # inputs = sbsbaker_global_options['inputs']
    # name_suffix_high = sbsbaker_global_options['name-suffix-high']
    # name_suffix_low = sbsbaker_global_options['name-suffix-low']
    # output_format =sbsbaker_global_options['output-format']
    # output_format_compression =sbsbaker_global_options['output-format-compression']
    # output_name =sbsbaker_global_options['output-name']
    # per_fragment_binormal =sbsbaker_global_options['per-fragment-binormal']
    # recompute_tangents =sbsbaker_global_options['recompute-tangents']
    # tangent_space_plugin =sbsbaker_global_options['tangent-space-plugin']

    # ambient-occlusion-from-mesh
    
    antialiasing = sbsbaker_global_options['antialiasing']
    apply_diffusion = sbsbaker_global_options['apply-diffusion']
    
    attenuation = EnumProperty(items = [
        ('0', 'None', 'None'),
        ('1', 'Smooth', 'Smooth'),
        ('2', 'Linear', 'Linear')],
                                name="attenuation", description="How occlusion is attenuated by occluder distance.", default="2")
    
    
    average_normals = sbsbaker_global_options['average-normals']
    
    

    dilation_width = sbsbaker_global_options['dilation-width']
    
    match = sbsbaker_global_options['match']
    use_lowdef_as_highdef =sbsbaker_global_options['use-lowdef-as-highdef']
    highdef_mesh = sbsbaker_global_options['highdef-mesh']
    use_cage = sbsbaker_global_options['use-cage']
    cage_mesh = sbsbaker_global_options['cage-mesh']
    relative_to_bbox = sbsbaker_global_options['relative-to-bbox']
    uv_set = sbsbaker_global_options['uv-set']
    
    ignore_backface = sbsbaker_global_options['ignore-backface']
    ignore_backface_secondary = sbsbaker_global_options['ignore-backface-secondary']
    
    invert_skew_correction = sbsbaker_global_options['invert-skew-correction']
    
    
    
    min_dist = sbsbaker_global_options['min-dist']
    max_dist = sbsbaker_global_options['max-dist']
    max_dist_relative_scale = sbsbaker_global_options['max-dist-relative-scale']
    
    max_frontal = sbsbaker_global_options['max-frontal']
    max_rear = sbsbaker_global_options['max-rear']
    
    
    
    nb_second_rays = sbsbaker_global_options['nb-second-rays']
    
    normal = sbsbaker_global_options['normal']
    normal_format =  sbsbaker_global_options['normal-format']
    normal_world_space = sbsbaker_global_options['normal-world-space']
    
    output_size = sbsbaker_global_options['output-size']
    
    
    ray_distrib =  sbsbaker_global_options['ray-distrib']
    
    
    self_occlusion =  sbsbaker_global_options['self-occlusion']
    spread_angle = sbsbaker_global_options['spread-angle']
    
    skew_correction = sbsbaker_global_options['skew-correction']
    skew_map = sbsbaker_global_options['skew-map']
   
    

    udim = sbsbaker_global_options['udim']
    
    
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"} 


class SbsBakerBentNormalFromMeshOperator(bpy.types.Operator): 
    bl_idname = "sbsbaker.bent_normal_from_mesh"
    bl_label = "sbsbaker bent-normal-from-mesh options"  
    bl_options = {"REGISTER", "UNDO"} 


    global sbsbaker_global_options

    # input_selection = sbsbaker_global_options['input-selection']
    # inputs = sbsbaker_global_options['inputs']
    # name_suffix_high = sbsbaker_global_options['name-suffix-high']
    # name_suffix_low = sbsbaker_global_options['name-suffix-low']
    # output_format =sbsbaker_global_options['output-format']
    # output_format_compression =sbsbaker_global_options['output-format-compression']
    # output_name =sbsbaker_global_options['output-name']
    # per_fragment_binormal =sbsbaker_global_options['per-fragment-binormal']
    # recompute_tangents =sbsbaker_global_options['recompute-tangents']
    # tangent_space_plugin =sbsbaker_global_options['tangent-space-plugin']
    # bent-normal-from-mesh options
    
    antialiasing = sbsbaker_global_options['antialiasing']
    apply_diffusion = sbsbaker_global_options['apply-diffusion']
    average_normals = BoolProperty(name="average-normals", description="Compute rays directions based on averaged normals.", default=True)
    cage_mesh = sbsbaker_global_options['cage-mesh']
    dilation_width = sbsbaker_global_options['dilation-width']
    highdef_mesh = sbsbaker_global_options['highdef-mesh']
    ignore_backface = sbsbaker_global_options['ignore-backface']
    ignore_backface_secondary = BoolProperty(name="ignore-backface-secondary", description="Ignore back-facing triangles for occlusion rays.", default=True)
    
    invert_skew_correction = sbsbaker_global_options['invert-skew-correction']
    
    map_type =  EnumProperty(items = [('0', 'World Space', 'World Space'), ('1', 'Tangent Space', 'Tangent Space') ],
                                name="map-type",
                                description="Map type.",
                                default="1")
    
    match = sbsbaker_global_options['match']
    max_dist = sbsbaker_global_options['max-dist']
    max_dist_relative_scale = BoolProperty(
        name="max-dist-relative-scale",
        description="Interpret the Occluder Distance as a factor of the mesh bounding box",
        default=True)
    
    max_frontal = sbsbaker_global_options['max-frontal']
    max_rear = sbsbaker_global_options['max-rear']
    min_dist = FloatProperty(name="min-dist", description="Minimum Occluder Distance (bias).", default=1e-5)
    nb_second_rays = IntProperty(name="nb-second-rays", description="Number of secondary rays (in [1; 1000]).", default=64)
    normal_invert = BoolProperty(name="normal-invert", description="Invert the normals.", default=False)
    output_size = sbsbaker_global_options['output-size']
    ray_distrib =  EnumProperty(items = [('0', 'Uniform', 'Uniform'), ('1', 'Cosine', 'Cosine') ],
                                name="ray-distrib",
                                description="Angular Distribution of Occlusion Rays.",
                                default="1")
    
    relative_to_bbox = sbsbaker_global_options['relative-to-bbox']
    
    self_occlusion =  EnumProperty(items = [('0', 'Always', 'Always'), ('1', 'Only Same Mesh Name', 'Only Same Mesh Name') ],
                                name="self-occlusion",
                                description="Choose what geometry will cause occlusion.",
                                default="0")
    
    skew_correction = sbsbaker_global_options['skew-correction']
    skew_map = sbsbaker_global_options['skew-map']
    spread_angle = sbsbaker_global_options['spread-angle']
    udim = sbsbaker_global_options['udim']
    use_cage = sbsbaker_global_options['use-cage']
    use_lowdef_as_highdef =sbsbaker_global_options['use-lowdef-as-highdef']
    uv_set = sbsbaker_global_options['uv-set']
    
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"}


class SbsBakerColorFromMeshOperator(bpy.types.Operator): 
    bl_idname = "sbsbaker.color_from_mesh"
    bl_label = "sbsbaker color-from-mesh options"  
    bl_options = {"REGISTER", "UNDO"} 


    global sbsbaker_global_options

    # input_selection = sbsbaker_global_options['input-selection']
    # inputs = sbsbaker_global_options['inputs']
    # name_suffix_high = sbsbaker_global_options['name-suffix-high']
    # name_suffix_low = sbsbaker_global_options['name-suffix-low']
    # output_format =sbsbaker_global_options['output-format']
    # output_format_compression =sbsbaker_global_options['output-format-compression']
    # output_name =sbsbaker_global_options['output-name']
    # per_fragment_binormal =sbsbaker_global_options['per-fragment-binormal']
    # recompute_tangents =sbsbaker_global_options['recompute-tangents']
    # tangent_space_plugin =sbsbaker_global_options['tangent-space-plugin']
    
    
    # bent-normal-from-mesh options
    
    antialiasing = sbsbaker_global_options['antialiasing']
    apply_diffusion = sbsbaker_global_options['apply-diffusion']
    
    average_normals = sbsbaker_global_options['average-normals']
    cage_mesh = sbsbaker_global_options['cage-mesh']

    color_generator =  EnumProperty(items = [
        ('0', 'Random', 'Random'),
        ('1', 'Hue Shift', 'Hue Shift'),
        ('2', 'Grayscale', 'Grayscale'),
        ],
                                name="color-generato",
                                description='''Choose the method for generating colors from IDs.
Vertex Color: reads the vertex color from the high definition meshes
Material Color: reads the material color from the high definition meshes (works only for FBX files)
Mesh ID: assigns a color per object from the high definition meshes Polygroup / Submesh ID: assigns a color per subobject (also
called element) from the high definition meshes.''',
                                default="1")
    
    
    color_source = EnumProperty(items = [
        ('0', 'Vertex Color', 'Vertex Color'),
        ('1', 'Material Color', 'Material Color'),
        ('2', 'Mesh ID', 'Mesh ID'),
        ('3', 'Polygroup/Submesh ID', 'Polygroup/Submesh ID')],
                                name="color-source",
                                description="Choose the source for color.", default="0")
    
    dilation_width = sbsbaker_global_options['dilation-width']
    highdef_mesh = sbsbaker_global_options['highdef-mesh']
    ignore_backface = sbsbaker_global_options['ignore-backface']
    
    invert_skew_correction = sbsbaker_global_options['invert-skew-correction']
    
    match = sbsbaker_global_options['match']
    
    max_frontal = sbsbaker_global_options['max-frontal']
    max_rear = sbsbaker_global_options['max-rear']

    output_size = sbsbaker_global_options['output-size']
    
    relative_to_bbox = sbsbaker_global_options['relative-to-bbox']
    
    
    skew_correction = sbsbaker_global_options['skew-correction']
    skew_map = sbsbaker_global_options['skew-map']
    
    udim = sbsbaker_global_options['udim']
    use_cage = sbsbaker_global_options['use-cage']
    use_lowdef_as_highdef =sbsbaker_global_options['use-lowdef-as-highdef']
    uv_set = sbsbaker_global_options['uv-set']
    
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"}


class SbsBakerCurvatureOperator(bpy.types.Operator): 
    bl_idname = "sbsbaker.curvature"  
    bl_label = "sbsbaker curvature options"  
    bl_options = {"REGISTER", "UNDO"} 

    global sbsbaker_global_options

    # input_selection = sbsbaker_global_options['input-selection']
    # inputs = sbsbaker_global_options['inputs']
    # name_suffix_high = sbsbaker_global_options['name-suffix-high']
    # name_suffix_low = sbsbaker_global_options['name-suffix-low']
    # output_format =sbsbaker_global_options['output-format']
    # output_format_compression =sbsbaker_global_options['output-format-compression']
    # output_name =sbsbaker_global_options['output-name']
    # per_fragment_binormal =sbsbaker_global_options['per-fragment-binormal']
    # recompute_tangents =sbsbaker_global_options['recompute-tangents']
    # tangent_space_plugin =sbsbaker_global_options['tangent-space-plugin']

    # curvature options
    algorithm =  EnumProperty(items = [
        ('0', 'Per Pixel', 'Per Pixel'),
        ('1', 'Per Vertex', 'Per Vertex') ],
                                name="algorithm",
                                description="Choose curvature computation algorithm (per vertex / per pixel)",
                                default="0")
    
    
    apply_diffusion = sbsbaker_global_options['apply-diffusion']
    
    
    details = FloatProperty(name="details", description="A lower value will be more precise but will easilly produce artefacts.", default=0.5)
    dilation_width = sbsbaker_global_options['dilation-width']
    
    normal = sbsbaker_global_options['normal']
    normal_format =  sbsbaker_global_options['normal-format']
    
    normal_world_space = sbsbaker_global_options['normal-world-space']

    output_size = sbsbaker_global_options['output-size']
    
    seams_power = FloatProperty(name="seams-power", description="Intensity of the seams on the map.", default=1.0)
    
    udim = sbsbaker_global_options['udim']
    uv_set = sbsbaker_global_options['uv-set']
    
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"} 


class SbsBakerCurvatureFromMeshOperator(bpy.types.Operator): 
    bl_idname = "sbsbaker.curvature_from_mesh"
    bl_label = "sbsbaker curvature-from-mesh options"  
    bl_options = {"REGISTER", "UNDO"} 


    global sbsbaker_global_options

    # input_selection = sbsbaker_global_options['input-selection']
    # inputs = sbsbaker_global_options['inputs']
    # name_suffix_high = sbsbaker_global_options['name-suffix-high']
    # name_suffix_low = sbsbaker_global_options['name-suffix-low']
    # output_format =sbsbaker_global_options['output-format']
    # output_format_compression =sbsbaker_global_options['output-format-compression']
    # output_name =sbsbaker_global_options['output-name']
    # per_fragment_binormal =sbsbaker_global_options['per-fragment-binormal']
    # recompute_tangents =sbsbaker_global_options['recompute-tangents']
    # tangent_space_plugin =sbsbaker_global_options['tangent-space-plugin']

    # bent-normal-from-mesh options
    
    antialiasing = sbsbaker_global_options['antialiasing']
    apply_diffusion = sbsbaker_global_options['apply-diffusion']
    
    average_normals = sbsbaker_global_options['average-normals']
    cage_mesh = sbsbaker_global_options['cage-mesh']
    
    dilation_width = sbsbaker_global_options['dilation-width']
    highdef_mesh = sbsbaker_global_options['highdef-mesh']
    
    intensity = FloatProperty(name="intensity", description="Multiply the computed curvature by this value.", default=1.0)

    
    max_dist = sbsbaker_global_options['max-dist']
    
    invert_skew_correction = sbsbaker_global_options['invert-skew-correction']
    
    match = sbsbaker_global_options['match']
    
    max_frontal = sbsbaker_global_options['max-frontal']
    max_rear = sbsbaker_global_options['max-rear']

    maximize_range = BoolProperty(name="maximize-range", description="Ensures the resulting map occupies the whole spectrum of values", default=False)

    output_size = sbsbaker_global_options['output-size']
    
    relative_to_bbox = sbsbaker_global_options['relative-to-bbox']
    
    skew_correction = sbsbaker_global_options['skew-correction']
    skew_map = sbsbaker_global_options['skew-map']
    
    soft_saturate = BoolProperty(name="soft-saturate", description="Softens the curvature values.", default=True)

    udim = sbsbaker_global_options['udim']
    use_cage = sbsbaker_global_options['use-cage']
    use_lowdef_as_highdef =sbsbaker_global_options['use-lowdef-as-highdef']
    uv_set = sbsbaker_global_options['uv-set']
    
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"}

class SbsBakerHeightFromMeshOperator(bpy.types.Operator): 
    bl_idname = "sbsbaker.height_from_mesh"
    bl_label = "sbsbaker height-from-mesh options"  
    bl_options = {"REGISTER", "UNDO"} 


    global sbsbaker_global_options

    # input_selection = sbsbaker_global_options['input-selection']
    # inputs = sbsbaker_global_options['inputs']
    # name_suffix_high = sbsbaker_global_options['name-suffix-high']
    # name_suffix_low = sbsbaker_global_options['name-suffix-low']
    # output_format =sbsbaker_global_options['output-format']
    # output_format_compression =sbsbaker_global_options['output-format-compression']
    # output_name =sbsbaker_global_options['output-name']
    # per_fragment_binormal =sbsbaker_global_options['per-fragment-binormal']
    # recompute_tangents =sbsbaker_global_options['recompute-tangents']
    # tangent_space_plugin =sbsbaker_global_options['tangent-space-plugin']

    # height-from-mesh options
    
    antialiasing = sbsbaker_global_options['antialiasing']
    apply_diffusion = sbsbaker_global_options['apply-diffusion']
    auto_normalize = sbsbaker_global_options['auto-normalize']
    average_normals = sbsbaker_global_options['average-normals']
    cage_mesh = sbsbaker_global_options['cage-mesh']
    dilation_width = sbsbaker_global_options['dilation-width']
    highdef_mesh = sbsbaker_global_options['highdef-mesh']
    ignore_backface = sbsbaker_global_options['ignore-backface']
    invert_skew_correction = sbsbaker_global_options['invert-skew-correction']
    match = sbsbaker_global_options['match']
    max_frontal = sbsbaker_global_options['max-frontal']
    max_rear = sbsbaker_global_options['max-rear']
    output_size = sbsbaker_global_options['output-size']
    relative_to_bbox = sbsbaker_global_options['relative-to-bbox']
    skew_correction = sbsbaker_global_options['skew-correction']
    skew_map = sbsbaker_global_options['skew-map']
    udim = sbsbaker_global_options['udim']
    use_cage = sbsbaker_global_options['use-cage']
    use_lowdef_as_highdef =sbsbaker_global_options['use-lowdef-as-highdef']
    uv_set = sbsbaker_global_options['uv-set']
    
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"}

class SbsBakerNormalFromMeshOperator(bpy.types.Operator): 
    bl_idname = "sbsbaker.normal_from_mesh"
    bl_label = "sbsbaker normal-from-mesh options"  
    bl_options = {"REGISTER", "UNDO"} 


    global sbsbaker_global_options
    
    antialiasing = sbsbaker_global_options['antialiasing']
    apply_diffusion = sbsbaker_global_options['apply-diffusion']
    average_normals = sbsbaker_global_options['average-normals']
    cage_mesh = sbsbaker_global_options['cage-mesh']
    dilation_width = sbsbaker_global_options['dilation-width']
    highdef_mesh = sbsbaker_global_options['highdef-mesh']
    ignore_backface = sbsbaker_global_options['ignore-backface']
    invert_skew_correction = sbsbaker_global_options['invert-skew-correction']
    map_type = sbsbaker_global_options['map-type']
    match = sbsbaker_global_options['match']
    max_frontal = sbsbaker_global_options['max-frontal']
    max_rear = sbsbaker_global_options['max-rear']
    normal_invert = sbsbaker_global_options['normal-invert']
    output_size = sbsbaker_global_options['output-size']
    relative_to_bbox = sbsbaker_global_options['relative-to-bbox']
    skew_correction = sbsbaker_global_options['skew-correction']
    skew_map = sbsbaker_global_options['skew-map']
    udim = sbsbaker_global_options['udim']
    use_cage = sbsbaker_global_options['use-cage']
    use_lowdef_as_highdef = sbsbaker_global_options['use-lowdef-as-highdef']
    uv_set = sbsbaker_global_options['uv-set']
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"}
    
class SbsBakerNormalWorldSpaceOperator(bpy.types.Operator): 
    bl_idname = "sbsbaker.normal_world_space"
    bl_label = "sbsbaker normal-world-space options"  
    bl_options = {"REGISTER", "UNDO"} 


    global sbsbaker_global_options
    
    apply_diffusion = sbsbaker_global_options['apply-diffusion']
    dilation_width = sbsbaker_global_options['dilation-width']
    normal = sbsbaker_global_options['normal']
    normal_format = sbsbaker_global_options['normal-format']
    normal_type = sbsbaker_global_options['normal-type']
    output_size = sbsbaker_global_options['output-size']
    udim = sbsbaker_global_options['udim']
    uv_set = sbsbaker_global_options['uv-set']
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"}
    
class SbsBakerOpacityMaskFromMesOperator(bpy.types.Operator): 
    bl_idname = "sbsbaker.opacity_mask_from_mesh"
    bl_label = "sbsbaker opacity-mask-from-mesh options"  
    bl_options = {"REGISTER", "UNDO"} 


    global sbsbaker_global_options
    
    antialiasing = sbsbaker_global_options['antialiasing']
    apply_diffusion = sbsbaker_global_options['apply-diffusion']
    average_normals = sbsbaker_global_options['average-normals']
    cage_mesh = sbsbaker_global_options['cage-mesh']
    dilation_width = sbsbaker_global_options['dilation-width']
    highdef_mesh = sbsbaker_global_options['highdef-mesh']
    ignore_backface = sbsbaker_global_options['ignore-backface']
    invert_skew_correction = sbsbaker_global_options['invert-skew-correction']
    match = sbsbaker_global_options['match']
    max_frontal = sbsbaker_global_options['max-frontal']
    max_rear = sbsbaker_global_options['max-rear']
    output_size = sbsbaker_global_options['output-size']
    relative_to_bbox = sbsbaker_global_options['relative-to-bbox']
    skew_correction = sbsbaker_global_options['skew-correction']
    skew_map = sbsbaker_global_options['skew-map']
    udim = sbsbaker_global_options['udim']
    use_cage = sbsbaker_global_options['use-cage']
    use_lowdef_as_highdef = sbsbaker_global_options['use-lowdef-as-highdef']
    uv_set = sbsbaker_global_options['uv-set']
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"}


class SbsBakerPositionOperator(bpy.types.Operator): 
    bl_idname = "sbsbaker.position"
    bl_label = "sbsbaker position options"  
    bl_options = {"REGISTER", "UNDO"} 


    global sbsbaker_global_options
    
    apply_diffusion = sbsbaker_global_options['apply-diffusion']
    axis = sbsbaker_global_options['axis']
    dilation_width = sbsbaker_global_options['dilation-width']
    mode = sbsbaker_global_options['mode']
    normalization = sbsbaker_global_options['normalization']
    output_size = sbsbaker_global_options['output-size']
    udim = sbsbaker_global_options['udim']
    uv_set = sbsbaker_global_options['uv-set']
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"}
    
class SbsBakerPositionFromMeshOperator(bpy.types.Operator): 
    bl_idname = "sbsbaker.position_from_mesh"
    bl_label = "sbsbaker position-from-mesh options"  
    bl_options = {"REGISTER", "UNDO"} 


    global sbsbaker_global_options
    
    antialiasing = sbsbaker_global_options['antialiasing']
    apply_diffusion = sbsbaker_global_options['apply-diffusion']
    average_normals = sbsbaker_global_options['average-normals']
    axis = sbsbaker_global_options['axis']
    cage_mesh = sbsbaker_global_options['cage-mesh']
    dilation_width = sbsbaker_global_options['dilation-width']
    highdef_mesh = sbsbaker_global_options['highdef-mesh']
    ignore_backface = sbsbaker_global_options['ignore-backface']
    invert_skew_correction = sbsbaker_global_options['invert-skew-correction']
    match = sbsbaker_global_options['match']
    max_frontal = sbsbaker_global_options['max-frontal']
    max_rear = sbsbaker_global_options['max-rear']
    mode = sbsbaker_global_options['mode']
    normalization = sbsbaker_global_options['normalization']
    output_size = sbsbaker_global_options['output-size']
    relative_to_bbox = sbsbaker_global_options['relative-to-bbox']
    skew_correction = sbsbaker_global_options['skew-correction']
    skew_map = sbsbaker_global_options['skew-map']
    udim = sbsbaker_global_options['udim']
    use_cage = sbsbaker_global_options['use-cage']
    use_lowdef_as_highdef = sbsbaker_global_options['use-lowdef-as-highdef']
    uv_set = sbsbaker_global_options['uv-set']
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"}

class SbsBakerTextureFromMeshOperator(bpy.types.Operator): 
    bl_idname = "sbsbaker.texture_from_mesh"
    bl_label = "sbsbaker texture-from-mesh options"  
    bl_options = {"REGISTER", "UNDO"} 


    global sbsbaker_global_options
    
    antialiasing = sbsbaker_global_options['antialiasing']
    apply_diffusion = sbsbaker_global_options['apply-diffusion']
    average_normals = sbsbaker_global_options['average-normals']
    cage_mesh = sbsbaker_global_options['cage-mesh']
    dilation_width = sbsbaker_global_options['dilation-width']
    filtering_mode = sbsbaker_global_options['filtering-mode']
    high_poly_uv_set = sbsbaker_global_options['high-poly-uv-set']
    highdef_mesh = sbsbaker_global_options['highdef-mesh']
    ignore_backface = sbsbaker_global_options['ignore-backface']
    invert_skew_correction = sbsbaker_global_options['invert-skew-correction']
    map_type = sbsbaker_global_options['map-type']
    match = sbsbaker_global_options['match']
    max_frontal = sbsbaker_global_options['max-frontal']
    max_rear = sbsbaker_global_options['max-rear']
    normal_invert = sbsbaker_global_options['normal-invert']
    normal_map = sbsbaker_global_options['normal-map']
    output_size = sbsbaker_global_options['output-size']
    relative_to_bbox = sbsbaker_global_options['relative-to-bbox']
    skew_correction = sbsbaker_global_options['skew-correction']
    skew_map = sbsbaker_global_options['skew-map']
    texture_file = sbsbaker_global_options['texture-file']
    udim = sbsbaker_global_options['udim']
    use_cage = sbsbaker_global_options['use-cage']
    use_lowdef_as_highdef = sbsbaker_global_options['use-lowdef-as-highdef']
    uv_set = sbsbaker_global_options['uv-set']
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"}
    
class SbsBakerThicknessFromMeshOperator(bpy.types.Operator): 
    bl_idname = "sbsbaker.thickness_from_mesh"
    bl_label = "sbsbaker thickness-from-mesh options"  
    bl_options = {"REGISTER", "UNDO"} 


    global sbsbaker_global_options
    
    antialiasing = sbsbaker_global_options['antialiasing']
    apply_diffusion = sbsbaker_global_options['apply-diffusion']
    auto_normalize = sbsbaker_global_options['auto-normalize']
    average_normals = sbsbaker_global_options['average-normals']
    cage_mesh = sbsbaker_global_options['cage-mesh']
    dilation_width = sbsbaker_global_options['dilation-width']
    highdef_mesh = sbsbaker_global_options['highdef-mesh']
    ignore_backface = sbsbaker_global_options['ignore-backface']
    ignore_backface_secondary = sbsbaker_global_options['ignore-backface-secondary']
    invert_skew_correction = sbsbaker_global_options['invert-skew-correction']
    match = sbsbaker_global_options['match']
    max_dist = sbsbaker_global_options['max-dist']
    max_dist_relative_scale = sbsbaker_global_options['max-dist-relative-scale']
    max_frontal = sbsbaker_global_options['max-frontal']
    max_rear = sbsbaker_global_options['max-rear']
    min_dist = sbsbaker_global_options['min-dist']
    nb_second_rays = sbsbaker_global_options['nb-second-rays']
    output_size = sbsbaker_global_options['output-size']
    ray_distrib = sbsbaker_global_options['ray-distrib']
    relative_to_bbox = sbsbaker_global_options['relative-to-bbox']
    self_occlusion = sbsbaker_global_options['self-occlusion']
    skew_correction = sbsbaker_global_options['skew-correction']
    skew_map = sbsbaker_global_options['skew-map']
    spread_angle = sbsbaker_global_options['spread-angle']
    udim = sbsbaker_global_options['udim']
    use_cage = sbsbaker_global_options['use-cage']
    use_lowdef_as_highdef = sbsbaker_global_options['use-lowdef-as-highdef']
    uv_set = sbsbaker_global_options['uv-set']
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"}

class SbsBakerUvMapOperator(bpy.types.Operator): 
    bl_idname = "sbsbaker.uvmap"
    bl_label = "sbsbaker uv-map options"  
    bl_options = {"REGISTER", "UNDO"} 


    global sbsbaker_global_options
    
    apply_diffusion = sbsbaker_global_options['apply-diffusion']
    dilation_width = sbsbaker_global_options['dilation-width']
    mode = sbsbaker_global_options['uv-mode']
    output_size = sbsbaker_global_options['output-size']
    padding = sbsbaker_global_options['padding']
    udim = sbsbaker_global_options['udim']
    uv_set = sbsbaker_global_options['uv-set']
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"}
    
class SbsBakerWorldSpaceDirectionOperator(bpy.types.Operator): 
    bl_idname = "sbsbaker.world_space_direction"
    bl_label = "world-space-direction options"  
    bl_options = {"REGISTER", "UNDO"} 


    global sbsbaker_global_options
    
    apply_diffusion = sbsbaker_global_options['apply-diffusion']
    dilation_width = sbsbaker_global_options['dilation-width']
    direction = sbsbaker_global_options['direction']
    direction_file = sbsbaker_global_options['direction-file']
    direction_x = sbsbaker_global_options['direction-x']
    direction_y = sbsbaker_global_options['direction-y']
    direction_z = sbsbaker_global_options['direction-z']
    normal_format = sbsbaker_global_options['normal-format']
    output_size = sbsbaker_global_options['output-size']
    udim = sbsbaker_global_options['udim']
    uv_set = sbsbaker_global_options['uv-set']
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"}


#######


class sbsbakerAmbientOcclusionPropertiesPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "sbsbaker"
    bl_idname = "OBJECT_sbsbaker"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    
    
    
    #bl_space_type = 'VIEW_3D'
    #bl_region_type = 'TOOLS'
    #bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        mytool = scene.addongen_substance_workflow_props
        
        box = layout.box()

        row = box.row()
        # row.prop(obj, "expanded",
        #     icon="TRIA_DOWN",
        #     icon_only=True, emboss=False
        # )
        row.label(text="Active object is: " + obj.name)

        #if obj.expanded:
        row = box.row()
        row.prop(obj, "name")
        
        row = box.row()
        row.operator(SbsBakerAmbientOcclutsonOperator.bl_idname, text = "ambient-occlusion", icon_value=custom_icons["substance_designer"].icon_id)
        
        row = box.row()
        row.operator(SbsBakerAmbientOcclutsonFromMeshOperator.bl_idname, text = "ambient-occlusion-from-mesh", icon_value=custom_icons["substance_designer"].icon_id)
        
        row = box.row()
        row.operator(SbsBakerBentNormalFromMeshOperator.bl_idname, text = "bent-normal-from-mesh", icon_value=custom_icons["substance_designer"].icon_id)
        
        row = box.row()
        row.operator(SbsBakerColorFromMeshOperator.bl_idname, text = "color-from-mesh", icon_value=custom_icons["substance_designer"].icon_id)
        
        row = box.row()
        row.operator(SbsBakerCurvatureOperator.bl_idname, text = "curvature", icon_value=custom_icons["substance_designer"].icon_id)
        
        row = box.row()
        row.operator(SbsBakerCurvatureFromMeshOperator.bl_idname, text = "curvature-from-mesh", icon_value=custom_icons["substance_designer"].icon_id)
        
        row = box.row()
        row.operator(SbsBakerHeightFromMeshOperator.bl_idname, text = "height-from-mesh", icon_value=custom_icons["substance_designer"].icon_id)
        
        row = box.row()
        row.operator(SbsBakerNormalFromMeshOperator.bl_idname, text = "normal-from-mesh", icon_value=custom_icons["substance_designer"].icon_id)
        
        row = box.row()
        row.operator(SbsBakerNormalWorldSpaceOperator.bl_idname, text = "normal-world-space", icon_value=custom_icons["substance_designer"].icon_id)
        
        row = box.row()
        row.operator(SbsBakerOpacityMaskFromMesOperator.bl_idname, text = "opacity-mask-from-mesh", icon_value=custom_icons["substance_designer"].icon_id)
        row = box.row()
        row.operator(SbsBakerPositionOperator.bl_idname, text = "position", icon_value=custom_icons["substance_designer"].icon_id)
        
        row = box.row()
        row.operator(SbsBakerPositionFromMeshOperator.bl_idname, text = "position-from-mesh", icon_value=custom_icons["substance_designer"].icon_id)
        
        row = box.row()
        row.operator(SbsBakerTextureFromMeshOperator.bl_idname, text = "texture-from-mesh", icon_value=custom_icons["substance_designer"].icon_id)
        
        row = box.row()
        row.operator(SbsBakerThicknessFromMeshOperator.bl_idname, text = "thickness-from-mesh", icon_value=custom_icons["substance_designer"].icon_id)
        
        row = box.row()
        row.operator(SbsBakerUvMapOperator.bl_idname, text = "uv-map", icon_value=custom_icons["substance_designer"].icon_id)
        
        row = box.row()
        row.operator(SbsBakerWorldSpaceDirectionOperator.bl_idname, text = "world-space-direction", icon_value=custom_icons["substance_designer"].icon_id)
        
        
class PBR_BuildeNodes_Operator(bpy.types.Operator): 
    bl_idname = "substance.build_pbr"
    bl_label = "build PBR nodes"  
    #bl_options = {"REGISTER", "UNDO"} 

    
    # global sbsbaker_global_options
    # 
    # apply_diffusion = sbsbaker_global_options['apply-diffusion']
    # dilation_width = sbsbaker_global_options['dilation-width']
    # direction = sbsbaker_global_options['direction']
    # direction_file = sbsbaker_global_options['direction-file']
    # direction_x = sbsbaker_global_options['direction-x']
    # direction_y = sbsbaker_global_options['direction-y']
    # direction_z = sbsbaker_global_options['direction-z']
    # normal_format = sbsbaker_global_options['normal-format']
    # output_size = sbsbaker_global_options['output-size']
    # udim = sbsbaker_global_options['udim']
    # uv_set = sbsbaker_global_options['uv-set']
    
    def execute(self, context) :
        #bpy.context.scene.render.engine = 'CYCLES'
        #bpy.context.space_data.context = 'MATERIAL'
        #bpy.context.area.type = 'NODE_EDITOR'
        
        material = bpy.data.materials['Material']
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
    
        return {"FINISHED Building PBR Nodes"}

class PBR_NodeBuilderPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "PBR node builder"
    bl_idname = "substance.nodebuilder" 
    #bl_space_type = 'NODE_EDITOR'
    # bl_region_type = 'WINDOW'
    # bl_context = "material"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Tools'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        mytool = scene.addongen_substance_workflow_props
        
        box = layout.box()

        row = box.row()
        # row.prop(obj, "expanded",
        #     icon="TRIA_DOWN",
        #     icon_only=True, emboss=False
        # )
        row.label(text="Active object is: " + obj.name)
        
        row = box.row()
        row.operator(PBR_BuildeNodes_Operator.bl_idname, text = "build nodes", icon_value=custom_icons["substance_designer"].icon_id)
        
    


##### >>>>>>>>
class SbsCookerOptions(bpy.types.Operator):
    
    #sbscooker [<global_option>...] [<option>...] <inputs>...
    
    bl_idname = "sbscooker.properties"
    bl_label = "sbscooker options"  
    bl_options = {"REGISTER", "UNDO"}
    
    ### I/O options
    alias = StringProperty(
        name="alias",
        description='''Add an alias definition.
            syntax of <arg>: '<alias>://<path>'
            Every occurence of <arg> in every url of every input file with be replaced
            with <path> before cooking.''',
        maxlen= 1024, default= "")
    
    enable_icons = BoolProperty(
        name='enable-icons',
        description = 'Include graph icons files in the SBSAR if they exist.',
        default = False)
    
    includes = StringProperty(
        name="includes",
        description='''Add a path to the list of folders of default packages. The Substance
            authoring tool default packages folder will be automatically appended to
            this list.''',
        maxlen= 1024, default= "")
    
    inputs = StringProperty(
        name="inputs",
        description='''Paths to the substance files to cook (in the .sbs file format).''',
        maxlen= 1024, default= "")


    merge = BoolProperty(
        name='merge',
        description = 'Merge all the results in one file',
        default = False)
    
    no_archive = BoolProperty(
        name='no-archive',
        description = 'Generate non packaged SBSASM and XML.',
        default = False )
    
    output_name = StringProperty(
        name="output-name",
        description='''Set the output name of the generated files, without the extension."The
            name is "{inputName}" by default.
            You can use the following patterns that will be replaced by the program
            when saving the result of the process:
              {inputName}  Replaced by the name of the first processed sbs file.
            [default: "{inputName}"]''',
        maxlen= 1024, default= "")

    output_path = StringProperty(
        name="output-path",
        description='''Set the output path for the generated files.
            By default the path is empty, i.e. the files will be saved in the current
            directory. You can use the following patterns that will be replaced by the
            program when saving the result of the process:
              {inputPath}  Replaced by the path of the first processed sbs file.''',
        maxlen= 1024, default= "")

    # Cooking options
    
    compression_mode = EnumProperty(items = [
        ('0', 'auto', 'auto'),
        ('1', 'best', 'best'),
        ('2', 'none', 'none')],
                                name="compression-mode",
                                description="Set the compression mode",
                                default="0")
    
    expose_output_size = BoolProperty(
                                name="expose-output-size",
                                description="Expose output size ?",
                                default=True)
    
    expose_pixel_size= BoolProperty(
                                name="expose-pixel-size",
                                description="Expose pixel size ?",
                                default=False)
    
    expose_random_seed = BoolProperty(
                                name="expose-random-seed",
                                description="Expose random seed ?",
                                default=True)
    
    no_optimization = BoolProperty(
                                name="no-optimization",
                                description='''Disable optimization.
            Check advanced parameters for finer tweaks with optimization.''',
                                default=False)
    
    size_imit = IntProperty(
                                name="size-limit",
                                description='''Maximum width and height of all compositing nodes,given as the exponent of
            a power in base 2.In other words, you must provide the logarithm in base 2
            of the actual width/height.
            For example '--size-limit 10' means nodes have a size limit of 1024x1024
            pixels.
            [Default value: Engine specific]''',
                                default=10)


    # Linking options
    
    link = StringProperty(
        name="link",
        description='''Call linker to generate .sbsbin file for an engine identified with the
            <engine_id> or <engine_short_name> parameter.''',
        maxlen= 1024, default= "")
   
    link_output_name = StringProperty(
        name="link-output-name",
        description='''Set the output name of the generated linked files, without the
            extension.The name is "{outputName}_{engineName}" by default.
            You can use the following patterns that will be replaced by the program
            when saving the result of the process:
            - {inputName}  Replaced by the name of the processed sbs.
            - {engineName}  Replaced by the name of the engine used to link the sbs.
            - {outputName}  Replaced by the output name specified by the --output-name
            command.''',
        maxlen= 1024, default= "{outputName}_{engineName}")
    
    link_output_path = StringProperty(
        name="link-output-path",
        description='''Set the output path of the generated linked files.The path is
            "{outputPath}" by default.
            program when saving the result of the process:
            - {inputPath}  Replaced by the path of the processed sbs.
            - {engineName}  Replaced by the name of the engine used to link the sbs.
            - {outputPath}  Replaced by the output path specified by the --output-path
            command''',
        maxlen= 1024, default= "{outputPath}")
    

    # Watermarking options
    post_filter = StringProperty(
        name="post-filter",
        description='''Post-filter substance file to apply (in the .sbs file format).''',
        maxlen= 1024, default= "")
   
    # Cooking optimization options
    crc = BoolProperty(
        name="crc",
        description='''Reduce cooking time.''',
        default=False)
    
    full = BoolProperty(
        name="full",
        description='''Full optimizations options. Best performance and memory footprint, slower
            cooking process.''',
        default=True)
    
    merge_data = BoolProperty(
        name="merge-data",
        description='''Reduce binary size.''',
        default=False)
    
    merge_graph = BoolProperty(
        name="merge-graph",
        description='''Best performance.''',
        default=False)
    
    reordering = BoolProperty(
        name="reorderingmerge-graph",
        description='''Reduce memory footprint.''',
        default=False)
    
    # Other options
    internal = BoolProperty(
        name="internal",
        description='''<uint>''',
        default=False)
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"}

    
    
class SbsCookerPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "sbscooker"
    bl_idname = "OBJECT_sbscooker"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    
    
    
    #bl_space_type = 'VIEW_3D'
    #bl_region_type = 'TOOLS'
    #bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        #mytool = scene.sbscooker.options
        
        box = layout.box()

        row = box.row()
        
        row.operator(SbsCookerOptions.bl_idname, text = "sbscooker options", icon_value=custom_icons["substance_designer"].icon_id)
     


'''Subcommand info
Return description of a substance archive file.
'''
class SbsRenderInfoOptions(bpy.types.Operator):
    
    
    #sbsrender [<global_options>...] info [<options>...]
    #sbsrender [<global_options>...] render [<options>...]

    
    bl_idname = "sbsrender.info_properties"
    bl_label = "sbsrender info options"  
    bl_options = {"REGISTER", "UNDO"}

    ### I/O options
    my_input = StringProperty(
        name="input",
        description='''Substance Archive File described. This option is implicit, so you can just provide a filepath at the end of your arguments, they will be interpreted as input.''',
        maxlen= 1024, default= "")


    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"}
    
'''Subcommand render
Render outputs of a substance archive file to image files.
'''
class SbsRenderRenderOptions(bpy.types.Operator):
    
    
    #sbsrender [<global_options>...] info [<options>...]
    #sbsrender [<global_options>...] render [<options>...]

    global sbsbaker_global_options
    
    bl_idname = "sbsrender.render_properties"
    bl_label = "sbsrender render options"  
    bl_options = {"REGISTER", "UNDO"}

    ### I/O options
    input_graph = StringProperty( #   --input-graph <graph_url> 
        name="input-graph",
        description='''Select specific graph to be rendered. If no graph are selected, all graphs are rendered.''',
        maxlen= 1024, default= "")


    input_graph_output = StringProperty( #   --input-graph-output <name> 
        name="input-graph-output",
        description = 'Select output to be rendered. If no output are selected, all outputs are rendered.',
        maxlen= 1024, default= "")
    
    inputs = StringProperty( #   --inputs <path> 
        name="inputs",
        description = 'List of substance archive file to render.',
        maxlen= 1024, default= "")
    
    output_bit_depth = StringProperty( #   --output-bit-depth <name> 
        name="output-bit-depth",
        description = '''Change the bit depth of the result image. The computation is still done in the bit depth the cooked graph uses. This option only affects the bit depth of the output image. <name> can be set to "8" (or "int8"), "16" (or "int16"),"16f" (or "float16") or "32f" (or "float32"). ''',
        maxlen= 1024, default= "")
    
    output_format = sbsbaker_global_options['output-format']
    output_format_compression = sbsbaker_global_options['output-format-compression']
    
    output_name = StringProperty( #  --output-name <name> [default: "{inputName}_{inputGraphUrl}_{outputNodeName}"] 
        name="output-name",
        description = '''You can use the following patterns that will be replaced by the program when saving the result of the process: - {inputName} replaced by the archive filename. - {inputGraphUrl} replaced by the graph url. - {outputNodeName} replaced by the output name. ''',
        maxlen= 1024, default= "{inputName}_{inputGraphUrl}_{outputNodeName}")
    
    output_path = StringProperty( #  --output-path <path>
        name="output-path",
        description = 'Output file path. Default path is empty. You can use the following patterns that will be replaced by the program when saving the result of the process: -{inputPath} replaced by the input filepath.',
        maxlen= 1024, default= "")
    
    png_format_compression =  EnumProperty(items = [ #  --png-format-compression <format> [default: "default"] 
    ('0', 'default', 'default'),
    ('1', 'best_speed', 'best_speed'),
    ('2', 'best_compression', 'best_compression'),
    ('2', 'none', 'none')],
                                        name="png-format-compression",
                                        description="PNG compression to use for output image",
                                        default="0")
    
    # Specific options
    set_entry = StringProperty( #   --set-entry <arg> 
        name="set-entry",
        description = 'Set image data to an image input. Format of <arg>: <input_identifier>@<filepath_of_image>.',
        maxlen= 1024, default= "")
    
    set_value = StringProperty( #   --set-value <arg> 
        name="set-value",
        description = 'Set value to a numerical input parameter. Format of <arg> : <input_identifier>@<value>. ',
        maxlen= 1024, default= "")
    
    use_preset = StringProperty( #   --use-preset <name> 
        name="use-preset",
        description = 'Use a specific preset to set values. <name> is the name of preset that must be included in the input sbsar file.',
        maxlen= 1024, default= "")
    
    
    # Runtime options
    engine = StringProperty( #   --engine <arg> 
        name="engine",
        description = 'Switch to specific engine implementation. format of <arg> : <dynamic_library_filepath> or <engine_version_basename_substring> e.g.: ogl3, d3d10pc, ... ',
        maxlen= 1024, default= "")
    
    engineMem = StringProperty( #  --engine <uint>
        name="engine-mem",
        description = 'Set the maximum amount of memory that the Substance Engine is allowed to use. In MB (default 1000 MB)',
        maxlen= 1024, default= "")
    
    
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"}


class SbsRenderPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "sbsrender"
    bl_idname = "OBJECT_sbsrender"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    
    
    
    #bl_space_type = 'VIEW_3D'
    #bl_region_type = 'TOOLS'
    #bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        #mytool = scene.sbscooker.options
        
        box = layout.box()

        row = box.row()
        row.operator(
            SbsRenderInfoOptions.bl_idname,
            text = "info",
            icon_value=custom_icons["substance_designer"].icon_id)
        
        
        row.operator(SbsRenderRenderOptions.bl_idname, text = "render", icon_value=custom_icons["substance_designer"].icon_id)
   
   
'''sbsmutator
Modifies and specializes .sbs files.

Typical examples of operations would be to connect images to inputs, instantiate a graph and expose inputs, etc.
Use the Pysbs - Python API in more advanced scenarios such as generating a graph from scratch.
'''
class SbsMutatorOptions(bpy.types.Operator):
    
    
    # Usage
    # sbsmutator [<global_options>...] edit [<options>...]
    # sbsmutator [<global_options>...] export [<options>...]
    # sbsmutator [<global_options>...] graph-parameters-editor [<options>...]
    # sbsmutator [<global_options>...] info [<options>...]
    # sbsmutator [<global_options>...] instantiate [<options>...]
    # sbsmutator [<global_options>...] specialization [<options>...]
    # sbsmutator [<global_options>...] update [<options>...]


    global sbsbaker_global_options
    
    bl_idname = "sbsmutator.properties"
    bl_label = "sbsmutator optiions"
    
    
    def execute(self, context) :  
        #print("fixed item", self.fixed_items)  
        return {"FINISHED"}


def add_to_menu(self, context) :
    self.layout.operator("mesh.dropdownexample", icon = "PLUGIN")

custom_icons = None


def register():
    
    global custom_icons
    custom_icons = bpy.utils.previews.new()
    
    #bpy.utils.register_module(__name__)
    
   #script_path = bpy.context.space_data.text.filepath
    icons_dir = '/users/rom/Library/Application Support/Blender/2.79/scripts/addons/icons'
    custom_icons.load("substance_designer", os.path.join(icons_dir, "substance_designer.png"), 'IMAGE')
    custom_icons.load("zbrush", os.path.join(icons_dir, "ZBrushLogo.png"), 'IMAGE')
    custom_icons.load("unity", os.path.join(icons_dir, "Unity.png"), 'IMAGE')
    
    bpy.utils.register_class(SubstanceWorkflowProps)
    bpy.types.Scene.addongen_substance_workflow_props = PointerProperty(type = SubstanceWorkflowProps)
    
    bpy.utils.register_class(sbsbaker_InputAndOutputOptions)
    bpy.types.Scene.sbsbaker_InputAndOutput_options = PointerProperty(type = sbsbaker_InputAndOutputOptions)
    
    bpy.utils.register_class(sbsbaker_AmbientOcclusionOptions)
    bpy.types.Scene.sbsbaker_AmbientOcclusion_options = PointerProperty(type = sbsbaker_AmbientOcclusionOptions)
    
    
    bpy.utils.register_class(SbsBakerIOOperator)
    bpy.utils.register_class(SbsBakerAmbientOcclutsonOperator)
    bpy.utils.register_class(SbsBakerAmbientOcclutsonFromMeshOperator)
    bpy.utils.register_class(SbsBakerBentNormalFromMeshOperator)
    bpy.utils.register_class(SbsBakerColorFromMeshOperator)
    bpy.utils.register_class(SbsBakerCurvatureOperator)
    bpy.utils.register_class(SbsBakerCurvatureFromMeshOperator)
    bpy.utils.register_class(SbsBakerHeightFromMeshOperator)
    
    bpy.utils.register_class(SbsBakerNormalFromMeshOperator)
    bpy.utils.register_class(SbsBakerNormalWorldSpaceOperator)
    bpy.utils.register_class(SbsBakerOpacityMaskFromMesOperator)
    bpy.utils.register_class(SbsBakerPositionOperator)
    bpy.utils.register_class(SbsBakerPositionFromMeshOperator)
    bpy.utils.register_class(SbsBakerTextureFromMeshOperator)
    bpy.utils.register_class(SbsBakerThicknessFromMeshOperator)
    bpy.utils.register_class(SbsBakerUvMapOperator)
    bpy.utils.register_class(SbsBakerWorldSpaceDirectionOperator)
    
    
    bpy.utils.register_class(SbsCookerOptions)
    bpy.utils.register_class(SbsCookerPanel)
    
    bpy.utils.register_class(SbsRenderInfoOptions)
    bpy.utils.register_class(SbsRenderRenderOptions)
    bpy.utils.register_class(SbsRenderPanel)
    
    


    

    
    #bpy.types.VIEW3D_MT_object.append(add_to_menu)

    
    #
    
    
    
    bpy.utils.register_class(ExportSelectAsFbxOperator)
    bpy.utils.register_class(ZBrushWorkflowOperator)
    bpy.utils.register_class(UnityWorkflowOperator)
    
    
    
    bpy.utils.register_class(SubstanceWorkflowOperator)
    bpy.utils.register_class(SubstanceWorkflowPanel)
    bpy.utils.register_class(SubstanceWorkflowMenu)
    
    bpy.utils.register_class(sbsbakerAmbientOcclusionPropertiesPanel)
    
    bpy.utils.register_class(PBR_BuildeNodes_Operator)
    bpy.utils.register_class(PBR_NodeBuilderPanel)
    
    

def unregister():
    
    global custom_icons
    bpy.utils.previews.remove(custom_icons)
    
    bpy.utils.unregister_class(SubstanceWorkflowProps)
    #del bpy.types.Scene.addongen_substance_workflow_props

    bpy.utils.unregister_class(SubstanceWorkflowOperator)
    bpy.utils.unregister_class(SubstanceWorkflowPanel)
    bpy.utils.unregister_class(SubstanceWorkflowMenu)
    
if __name__ == "__main__":
    register()
