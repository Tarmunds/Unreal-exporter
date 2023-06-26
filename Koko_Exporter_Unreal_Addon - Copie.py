import bpy
import os
from bpy.types import Operator

bl_info = {
    "name": "Export Unreal",
    "author": "Tarmunds",
    "version": (1, 3),
    "blender": (2, 80, 0),
    "location": "File > Export",
    "description": "Exports each selected object into its own file, at the origin of the world (depend of objects origins)",
    "doc_url":     "https://docs.google.com/document/d/1j2DZWXR-klQArrlfSLQAV_ltop4BOsD6ZXgRYFnC0b0/edit?usp=sharing",
    "category": "Import-Export",
}

# try de pannel avec variable
class MeshRenamePanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_path_var"
    bl_label = "Path Var"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(context.scene, "mesh_rename_path", text="Path Var")
        col.operator("export.selected_object", text="export")

#fonction d'export type ue
class ExportSelectedObjectsOperator(Operator):
    bl_idname = "export.selected_object"
    bl_label = "Export Unreal"

    def execute(self, context):

        path = context.scene.mesh_rename_path

        # export to blend file location
        basedir = os.path.dirname(bpy.data.filepath)

        if not basedir:
            raise Exception("Blend file is not saved")

        exportDir = path
        view_layer = context.view_layer

        obj_active = view_layer.objects.active
        selection = context.selected_objects

        bpy.ops.object.select_all(action='DESELECT')

        for obj in selection:
            obj.select_set(True)

            # some exporters only use the active object
            context.view_layer.objects.active = obj

            # allow location static override
            # bpy.ops.object.make_override_static()
            bpy.ops.object.make_local()

            # store object location then zero it out
            location = obj.location.copy()
            bpy.ops.object.location_clear()

            name = bpy.path.clean_name(obj.name)
            fn = os.path.join(exportDir, name)

            bpy.ops.export_scene.fbx(filepath=fn + ".fbx", use_selection=True, apply_unit_scale=False,
                                     object_types={'MESH', 'ARMATURE'}, mesh_smooth_type='FACE',
                                     use_mesh_modifiers=True)

            # restore location
            obj.location = location

            obj.select_set(False)

            print("written:", fn)

        view_layer.objects.active = obj_active

        for obj in selection:
            obj.select_set(True)

        return {'FINISHED'}


def menu_func_export(self, context):
    self.layout.operator(ExportSelectedObjectsOperator.bl_idname, text="Export Selected Unreal Ready (fbx)")


def register():
    bpy.utils.register_class(ExportSelectedObjectsOperator)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export) #base export end
    bpy.utils.register_class(MeshRenamePanel)
    bpy.utils.register_class(MeshRenameOperator)
    bpy.types.Scene.mesh_rename_path = bpy.props.StringProperty(name="path", default="")



def unregister():
    bpy.utils.unregister_class(ExportSelectedObjectsOperator)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export) #base export end
    bpy.utils.unregister_class(MeshRenamePanel)
    bpy.utils.unregister_class(MeshRenameOperator)
    del bpy.types.Scene.mesh_rename_path
    del bpy.types.Scene.mesh_rename_increment


if __name__ == "__main__":
    register()