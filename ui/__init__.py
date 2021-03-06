"""
Copyright (C) 2017 Bricks Brought to Life
http://bblanimation.com/
chris@bblanimation.com

Created by Christopher Gearhart

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# system imports
import bpy
from bpy.types import Panel
from bpy.props import *
from .aglist_actions import *
from .aglist_utils import *
from .aglist_attrs import *
from .app_handlers import *
from ..functions import *
props = bpy.props

# updater import
from .. import addon_updater_ops

class BasicMenu(bpy.types.Menu):
    bl_idname = "AssemblMe_specials_menu"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout

        layout.operator("aglist.copy_to_others", icon="COPY_ID", text="Copy Settings to Others")
        layout.operator("aglist.copy_settings", icon="COPYDOWN", text="Copy Settings")
        layout.operator("aglist.paste_settings", icon="PASTEDOWN", text="Paste Settings")

class AnimationsPanel(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label       = "Animations"
    bl_idname      = "VIEW3D_PT_tools_AssemblMe_animations"
    bl_context     = "objectmode"
    bl_category    = "AssemblMe"
    COMPAT_ENGINES = {"CYCLES", "BLENDER_RENDER"}

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        return True

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene

        if bversion() < '002.078.00':
            col = layout.column(align=True)
            col.label('ERROR: upgrade needed', icon='ERROR')
            col.label('AssemblMe requires Blender 2.78+')
            return

        # Call to check for update in background
        # Internally also checks to see if auto-check enabled
        # and if the time interval has passed
        addon_updater_ops.check_for_update_background()
        # draw auto-updater update box
        addon_updater_ops.update_notice_box_ui(self, context)

        # draw UI list and list actions
        if len(scn.aglist) < 2:
            rows = 2
        else:
            rows = 4
        row = layout.row()
        row.template_list("AssemblMe_UL_items", "", scn, "aglist", scn, "aglist_index", rows=rows)

        col = row.column(align=True)
        col.operator("aglist.list_action", icon='ZOOMIN', text="").action = 'ADD'
        col.operator("aglist.list_action", icon='ZOOMOUT', text="").action = 'REMOVE'
        col.menu("AssemblMe_specials_menu", icon='DOWNARROW_HLT', text="")
        if len(scn.aglist) > 1:
            col.separator()
            col.operator("aglist.list_action", icon='TRIA_UP', text="").action = 'UP'
            col.operator("aglist.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'

        col1 = layout.column(align=True)
        if scn.aglist_index == -1:
            row = col1.row(align=True)
            row.operator("aglist.list_action", icon='ZOOMIN', text="Create New Animation").action = 'ADD'
        else:
            ag = scn.aglist[scn.aglist_index]
            if ag.animated:
                n = ag.group_name
                col1.label("Group Name:")
                col1.label("%(n)s" % locals())
            else:
                col1.label("Group Name:")
                split = col1.split(align=True, percentage=0.85)
                col = split.column(align=True)
                col.prop_search(ag, "group_name", bpy.data, "groups", text="")
                col = split.column(align=True)
                col.operator("aglist.set_to_active", icon="EDIT", text="")
                if not bpy.data.groups.get(ag.group_name):
                    row = col1.row(align=True)
                    row.active = len(bpy.context.selected_objects) != 0
                    row.operator("scene.new_group_from_selection", icon='ZOOMIN', text="From Selection")

class ActionsPanel(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label       = "Actions"
    bl_idname      = "VIEW3D_PT_tools_AssemblMe_actions"
    bl_context     = "objectmode"
    bl_category    = "AssemblMe"
    COMPAT_ENGINES = {"CYCLES", "BLENDER_RENDER"}

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        if bversion() < '002.078.00':
            return False
        scn = bpy.context.scene
        if scn.aglist_index == -1:
            return False
        return True

    def draw(self, context):
        layout = self.layout
        scn, ag = getActiveContextInfo()

        col = layout.column(align=True)
        row = col.row(align=True)
        if not ag.animated:
            row.active = groupExists(ag.group_name)
            row.operator("scene.create_build_animation", text="Create Build Animation", icon="MOD_BUILD").action = "CREATE"
        else:
            row.operator("scene.create_build_animation", text="Update Build Animation", icon="MOD_BUILD").action = "UPDATE"
        row = col.row(align=True)
        row.operator("scene.start_over", text="Start Over", icon="RECOVER_LAST")
        if bpy.data.texts.find('AssemblMe_log') >= 0:
            split = layout.split(align=True, percentage = 0.9)
            col = split.column(align=True)
            row = col.row(align=True)
            row.operator("scene.report_error", text="Report Error", icon="URL")
            col = split.column(align=True)
            row = col.row(align=True)
            row.operator("scene.close_report_error", text="", icon="PANEL_CLOSE")

class SettingsPanel(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label       = "Settings"
    bl_idname      = "VIEW3D_PT_tools_AssemblMe_settings"
    bl_context     = "objectmode"
    bl_category    = "AssemblMe"
    COMPAT_ENGINES = {"CYCLES", "BLENDER_RENDER"}

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        if bversion() < '002.078.00':
            return False
        scn = bpy.context.scene
        if scn.aglist_index == -1:
            return False
        return True

    def draw(self, context):
        layout = self.layout
        scn, ag = getActiveContextInfo()

        if bversion() < '002.075.00':
            col = layout.column(align=True)
            col.label('ERROR: upgrade needed', icon='ERROR')
            col.label('AssemblMe requires Blender 2.75+')
            return

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(scn, "animPreset", text="Preset")

        box = layout.box()

        col = box.column(align=True)
        row = col.row(align=True)
        row.label("Animation:")
        row = col.row(align=True)
        if ag.orientRandom > 0.005:
            approx = "~"
        else:
            approx = ""
        row.operator("scene.refresh_build_animation_length", text="Duration: " + approx + str(ag.animLength) + " frames", icon="FILE_REFRESH")
        row = col.row(align=True)
        row.prop(ag, "firstFrame")
        row = col.row(align=True)
        row.prop(ag, "buildSpeed")
        row = col.row(align=True)
        row.prop(ag, "velocity")
        row = col.row(align=True)

        if scn.animPreset == "Follow Curve":
            col = layout.column(align=True)
            row = col.row(align=True)
            row.label("Path Object:")
            row = col.row(align=True)
            row.prop(ag, "pathObject")
        else:
            split = box.split(align=False, percentage = 0.5)
            col = split.column(align=True)
            row = col.row(align=True)
            row.label("Location Offset:")
            row = col.row(align=True)
            row.prop(ag, "xLocOffset")
            row = col.row(align=True)
            row.prop(ag, "yLocOffset")
            row = col.row(align=True)
            row.prop(ag, "zLocOffset")
            row = col.row(align=True)
            row.prop(ag, "locInterpolationMode", text="")
            row = col.row(align=True)
            row.prop(ag, "locationRandom")
            row = col.row(align=True)

            col = split.column(align=True)
            row = col.row(align=True)
            row.label("Rotation Offset:")
            row = col.row(align=True)
            row.prop(ag, "xRotOffset")
            row = col.row(align=True)
            row.prop(ag, "yRotOffset")
            row = col.row(align=True)
            row.prop(ag, "zRotOffset")
            row = col.row(align=True)
            row.prop(ag, "rotInterpolationMode", text="")
            row = col.row(align=True)
            row.prop(ag, "rotationRandom")

        col1 = box.column(align=True)
        row = col1.row(align=True)
        row.label("Layer Orientation:")
        row = col1.row(align=True)
        split = row.split(align=True, percentage=0.9)
        row = split.row(align=True)
        col = row.column(align=True)
        col.prop(ag, "xOrient")
        col = row.column(align=True)
        col.prop(ag, "yOrient")
        col = split.column(align=True)
        if ag.visualizerActive:
            col.operator("scene.visualize_layer_orientation", text="", icon="RESTRICT_VIEW_OFF")
        else:
            col.operator("scene.visualize_layer_orientation", text="", icon="RESTRICT_VIEW_ON")
        row = col1.row(align=True)
        row.prop(ag, "orientRandom")
        col1 = box.column(align=True)
        row = col1.row(align=True)
        row.prop(ag, "layerHeight")

        col = box.column(align=True)
        row = col.row(align=True)
        row.label("Build Type:")
        row = col.row(align=True)
        row.prop(ag, "buildType", text="")
        row = col.row(align=True)
        row.prop(ag, "invertBuild")

class AdvancedPanel(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label       = "Advanced"
    bl_idname      = "VIEW3D_PT_tools_AssemblMe_advanced"
    bl_context     = "objectmode"
    bl_category    = "AssemblMe"
    bl_options     = {"DEFAULT_CLOSED"}
    COMPAT_ENGINES = {"CYCLES", "BLENDER_RENDER"}

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        if bversion() < '002.078.00':
            return False
        scn = bpy.context.scene
        if scn.aglist_index == -1:
            return False
        return True

    def draw(self, context):
        layout = self.layout
        scn, ag = getActiveContextInfo()

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(scn, "skipEmptySelections")
        row = col.row(align=True)
        row.prop(ag, "useGlobal")

        row = col.row(align=True)
        row.label("Visualizer:")
        row = col.row(align=True)
        row.prop(scn, "visualizerScale")
        row.prop(scn, "visualizerRes")

class presetManager(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label       = "Preset Manager"
    bl_idname      = "VIEW3D_PT_tools_AssemblMe_preset_manager"
    bl_context     = "objectmode"
    bl_category    = "AssemblMe"
    bl_options     = {"DEFAULT_CLOSED"}
    COMPAT_ENGINES = {"CYCLES", "BLENDER_RENDER"}

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        if bversion() < '002.078.00':
            return False
        return True

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        if scn.aglist_index != -1:
            col = layout.column(align=True)
            row = col.row(align=True)
            row.label("Create New Preset:")
            row = col.row(align=True)
            split = row.split(align=True, percentage = 0.7)
            col = split.column(align=True)
            col.prop(scn, "newPresetName", text="")
            col = split.column(align=True)
            col.active = scn.newPresetName != ""
            col.operator("scene.animation_presets", text="Create", icon="ZOOMIN").action = "CREATE"
        col = layout.column(align=True)
        row = col.row(align=True)
        row.label("Remove Existing Preset:")
        row = col.row(align=True)
        split = row.split(align=True, percentage = 0.7)
        col = split.column(align=True)
        col.prop(scn, "animPresetToDelete", text="")
        col = split.column(align=True)
        col.active = scn.animPresetToDelete != "None"
        col.operator("scene.animation_presets", text="Remove", icon="X").action = "REMOVE"
        col = layout.column(align=True)
        row = col.row(align=True)
        col.operator("scene.info_restore_preset", text="Restore Presets", icon="INFO")
