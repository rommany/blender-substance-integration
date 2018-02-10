bl_info = {
    "name": "Substance Workflow",
    "author": "Your Name Here",
    "version": (1, 0),
    "blender": (2, 70, 0),
    "location": "View3D > Object > ",
    "description": "Adds a new Mesh Object",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"}

import bpy
from bpy.props import BoolProperty, BoolVectorProperty, FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, EnumProperty, StringProperty, PointerProperty

class SubstanceWorkflowOperator(bpy.types.Operator):
    """ToolTip of SubstanceWorkflowOperator"""
    bl_idname = "addongen.substance_workflow_operator"
    bl_label = "Substance Workflow Operator"
    bl_options = {'REGISTER'}


    #@classmethod
    #def poll(cls, context):
    #    return context.object is not None
    
    def execute(self, context):
        self.report({'INFO'}, "Hello World!")
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
    bl_label = "Substance Workflow Panel"
    
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Tools'
    
    #Panels in ImageEditor are using .poll() instead of bl_context.
    #@classmethod
    #def poll(cls, context):
    #    return context.space_data.show_paint
    
    def draw(self, context):
        layout = self.layout
        layout.operator(SubstanceWorkflowOperator.bl_idname, text = "My Substance Workflow", icon = 'BLENDER')

class SubstanceWorkflowMenu(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_substance_workflow"
    bl_label = "Substance Workflow Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator(SubstanceWorkflowOperator.bl_idname)
        layout.separator()
        layout.menu("VIEW3D_MT_transform")
        layout.operator_menu_enum("object.select_by_type", "type", text="Select All by Type...")

class SubstanceWorkflowProps(bpy.types.PropertyGroup):
    my_bool =     BoolProperty(name="", description="", default=False)
    my_boolVec =  BoolVectorProperty(name="", description="", default=(False, False, False))
    my_float =    FloatProperty(name="", description="", default=0.0)
    my_floatVec = FloatVectorProperty(name="", description="", default=(0.0, 0.0, 0.0)) 
    my_int =      IntProperty(name="", description="", default=0)  
    my_intVec =   IntVectorProperty(name="", description="", default=(0, 0, 0))
    my_string =   StringProperty(name="String Value", description="", default="", maxlen=0)
    my_enum =     EnumProperty(items = [('ENUM1', 'Enum1', 'enum prop 1'), 
                                        ('ENUM2', 'Enum2', 'enum prop 2')],
                               name="",
                               description="",
                               default="ENUM1")

def register():
    bpy.utils.register_class(SubstanceWorkflowProps)
    bpy.types.Scene.addongen_substance_workflow_props = PointerProperty(type = SubstanceWorkflowProps)

    bpy.utils.register_class(SubstanceWorkflowOperator)
    bpy.utils.register_class(SubstanceWorkflowPanel)
    bpy.utils.register_class(SubstanceWorkflowMenu)

def unregister():
    bpy.utils.unregister_class(SubstanceWorkflowProps)
    #del bpy.types.Scene.addongen_substance_workflow_props

    bpy.utils.unregister_class(SubstanceWorkflowOperator)
    bpy.utils.unregister_class(SubstanceWorkflowPanel)
    bpy.utils.unregister_class(SubstanceWorkflowMenu)
    
if __name__ == "__main__":
    register()
