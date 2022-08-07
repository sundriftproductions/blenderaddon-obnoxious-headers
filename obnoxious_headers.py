#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================

import bpy
import blf
from bpy.app.handlers import persistent

# Version History
# 1.0.1 - 2020-03-21: Made it so we do NOT change the color of view_3d.space.header; Bone Keyboard needs to change that
#                     header color if Shift Lock is engaged.
# 1.0.2 - 2020-03-22: Renamed this to "Obnoxious Headers" since this handles both autokeyframe and X-Axis Mirror (and
#                     possibly others in the future).
# 1.0.3 - 2020-03-23: Made it so X-Axis Mirror message appears whether you're in pose or edit mode.
# 1.0.4 - 2020-07-02: Made it so X-Axis Mirror message appears if you're in Weight Paint mode.
# 1.0.5 - 2020-11-10: Made it so X-Axis Mirror message appears if you're in Particle Edit mode.
# 1.0.6 - 2020-11-11: Made it so X-Axis Mirror message appears if you're in Texture Paint mode.
# 1.0.7 - 2020-12-20: Fixed this to work with Blender 2.91, where instead of using use_symmetry_x on the weight and
#                     paint tool, you have to use use_mirror_x on the object itself.
# 1.0.8 - 2022-01-25: Added messages for Strand Lengths and Root Positions (when in Particle Edit mode).
# 1.0.9 - 2022-01-25: Altered colors of new messages.
# 1.0.10 - 2022-04-05: Fixed a bug where there were constant error messages that said "AttributeError: 'Lattice' object has no attribute 'use_mirror_x'" when trying to edit a lattice. (Maybe it was possible to do a mirror on lattices in previous Blender versions, but it's not possible now.)
# 1.0.11 - 2022-08-07: Misc formatting cleanup before uploading to GitHub.

bl_info = {
    "name" : "Obnoxious Headers",
    "author" : "Jeff Boller, Bookyakuno",
    "version" : (1, 0, 11),
    "blender" : (2, 93, 0),
    "location" : "UI",
    "description" : "This add-on makes it _extremely_ obvious if certain important, project-altering features are turned on or off. If the automatic keyframe feature is enabled, the header colors in Blender are turned an obnoxious color of red. If X-Axis Mirror is on, Preserve Strands Length (when in Particle Edit mode) is off, or Preserve Root Position (when in Particle Edit mode) is off, an obnoxious text message will appear in the lower left hand corner of every 3D Viewport window. This code is a fork of the header_color_change script by Bookyakuno: https://github.com/bookyakuno/-Blender-/blob/master/header_color_change.py",
    "category" : "UI",
    "wiki_url": "https://github.com/sundriftproductions/blenderaddon-obnoxious-headers/wiki",
    "tracker_url": "https://github.com/sundriftproductions/blenderaddon-obnoxious-headers",
}

font_info = {
    "font_id": 0,
    "handler": None,
}

def draw_callback_px_x_axis_mirror(self, context):
    font_id = font_info["font_id"]
    blf.position(font_id, 20, 20, 0)
    blf.size(font_id, 40, 72)
    blf.color(font_id, 1.0, 1.0, 0.5, 1.0)
    blf.enable(font_id, blf.SHADOW)
    blf.shadow(font_id, 5, 1.0, 0.0, 0.0, 1.0)
    blf.shadow_offset(font_id, 2, -2)
    blf.draw(font_id, "X-Axis Mirror On!")
    blf.disable(font_id, blf.SHADOW)

def draw_callback_px_preserve_strand_lengths(self, context):
    font_id = font_info["font_id"]
    blf.position(font_id, 20, 100, 0)
    blf.size(font_id, 30, 54)
    blf.color(font_id, 0.192, 1.0, 0.00392, 1.0) # Lime green
    blf.enable(font_id, blf.SHADOW)
    blf.shadow(font_id, 5, 0.0, 0.0, 0.0, 1.0)
    blf.shadow_offset(font_id, 2, -2)
    blf.draw(font_id, "Warning: Preserve Strand Lengths OFF!")
    blf.disable(font_id, blf.SHADOW)

def draw_callback_px_preserve_root_positions(self, context):
    font_id = font_info["font_id"]
    blf.position(font_id, 20, 67, 0)
    blf.size(font_id, 30, 54)
    blf.color(font_id, 1.0, 0.3961, 0.9922, 1.0) # Light purple
    blf.enable(font_id, blf.SHADOW)
    blf.shadow(font_id, 5, 0.0, 0.0, 0.0, 1.0)
    blf.shadow_offset(font_id, 2, -2)
    blf.draw(font_id, "Warning: Preserve Root Positions OFF!")
    blf.disable(font_id, blf.SHADOW)

def redraw_regions():
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    region.tag_redraw()

def create_x_axis_message():
    import os
    font_path = bpy.path.abspath('//Zeyada.ttf')
    if os.path.exists(font_path):
        font_info["font_id"] = blf.load(font_path)
    else:
        font_info["font_id"] = 0

    # Set the font drawing routine to run every frame.
    handler = bpy.app.driver_namespace.get('draw_x_axis_message')
    if not handler:
        handler = bpy.types.SpaceView3D.draw_handler_add(
            draw_callback_px_x_axis_mirror, (None, None), 'WINDOW', 'POST_PIXEL')
        dns = bpy.app.driver_namespace
        dns['draw_x_axis_message'] = handler
        redraw_regions()

def remove_x_axis_message():
    handler = bpy.app.driver_namespace.get('draw_x_axis_message')
    if handler:
        bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
        del bpy.app.driver_namespace['draw_x_axis_message']
        redraw_regions()

def create_preserve_strand_lengths_message():
    import os
    font_path = bpy.path.abspath('//Zeyada.ttf')
    if os.path.exists(font_path):
        font_info["font_id"] = blf.load(font_path)
    else:
        font_info["font_id"] = 0

    # Set the font drawing routine to run every frame.
    handler = bpy.app.driver_namespace.get('draw_preserve_strand_lengths_message')
    if not handler:
        handler = bpy.types.SpaceView3D.draw_handler_add(
            draw_callback_px_preserve_strand_lengths, (None, None), 'WINDOW', 'POST_PIXEL')
        dns = bpy.app.driver_namespace
        dns['draw_preserve_strand_lengths_message'] = handler
        redraw_regions()

def remove_preserve_strand_lengths_message():
    handler = bpy.app.driver_namespace.get('draw_preserve_strand_lengths_message')
    if handler:
        bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
        del bpy.app.driver_namespace['draw_preserve_strand_lengths_message']
        redraw_regions()

def create_preserve_root_positions_message():
    import os
    font_path = bpy.path.abspath('//Zeyada.ttf')
    if os.path.exists(font_path):
        font_info["font_id"] = blf.load(font_path)
    else:
        font_info["font_id"] = 0

    # Set the font drawing routine to run every frame.
    handler = bpy.app.driver_namespace.get('draw_preserve_root_positions_message')
    if not handler:
        handler = bpy.types.SpaceView3D.draw_handler_add(
            draw_callback_px_preserve_root_positions, (None, None), 'WINDOW', 'POST_PIXEL')
        dns = bpy.app.driver_namespace
        dns['draw_preserve_root_positions_message'] = handler
        redraw_regions()

def remove_preserve_root_positions_message():
    handler = bpy.app.driver_namespace.get('draw_preserve_root_positions_message')
    if handler:
        bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
        del bpy.app.driver_namespace['draw_preserve_root_positions_message']
        redraw_regions()

@persistent
def LoadPost_header_col(scn):
    handle_handlers_draw_header_col()

def handle_handlers_draw_header_col():
    if OBNOXIOUS_HEADERS_prefset not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(OBNOXIOUS_HEADERS_prefset)

def OBNOXIOUS_HEADERS_prefset(scene):
    if bpy.context.scene.tool_settings.use_keyframe_insert_auto:
        bpy.context.preferences.themes[0].dopesheet_editor.space.header = (1, 0.000000, 0.000000, 1.000000)
        bpy.context.preferences.themes[0].graph_editor.space.header = (1, 0.000000, 0.000000, 1.000000)
        bpy.context.preferences.themes[0].nla_editor.space.header = (1, 0.000000, 0.000000, 1.000000)
        bpy.context.preferences.themes[0].image_editor.space.header = (1, 0.000000, 0.000000, 1.000000)
        bpy.context.preferences.themes[0].sequence_editor.space.header = (1, 0.000000, 0.000000, 1.000000)
        bpy.context.preferences.themes[0].text_editor.space.header = (1, 0.000000, 0.000000, 1.000000)
        bpy.context.preferences.themes[0].node_editor.space.header = (1, 0.000000, 0.000000, 1.000000)
        bpy.context.preferences.themes[0].properties.space.header = (1, 0.000000, 0.000000, 1.000000)
        bpy.context.preferences.themes[0].outliner.space.header = (1, 0.000000, 0.000000, 1.000000)
        bpy.context.preferences.themes[0].info.space.header = (1, 0.000000, 0.000000, 1.000000)
        bpy.context.preferences.themes[0].console.space.header = (1, 0.000000, 0.000000, 1.000000)
        bpy.context.preferences.themes[0].clip_editor.space.header = (1, 0.000000, 0.000000, 1.000000)
        bpy.context.preferences.themes[0].topbar.space.header = (1, 0.000000, 0.000000, 1.000000)
    else:
        bpy.context.preferences.themes[0].dopesheet_editor.space.header = (0.137255, 0.137255, 0.137255, 1.000000)
        bpy.context.preferences.themes[0].graph_editor.space.header = (0.137255, 0.137255, 0.137255, 1.000000)
        bpy.context.preferences.themes[0].nla_editor.space.header = (0.137255, 0.137255, 0.137255, 1.000000)
        bpy.context.preferences.themes[0].image_editor.space.header = (0.137255, 0.137255, 0.137255, 1.000000)
        bpy.context.preferences.themes[0].sequence_editor.space.header = (0.137255, 0.137255, 0.137255, 1.000000)
        bpy.context.preferences.themes[0].text_editor.space.header = (0.137255, 0.137255, 0.137255, 1.000000)
        bpy.context.preferences.themes[0].node_editor.space.header = (0.137255, 0.137255, 0.137255, 1.000000)
        bpy.context.preferences.themes[0].properties.space.header = (0.137255, 0.137255, 0.137255, 1.000000)
        bpy.context.preferences.themes[0].outliner.space.header = (0.137255, 0.137255, 0.137255, 1.000000)
        bpy.context.preferences.themes[0].info.space.header = (0.137255, 0.137255, 0.137255, 1.000000)
        bpy.context.preferences.themes[0].console.space.header = (0.137255, 0.137255, 0.137255, 1.000000)
        bpy.context.preferences.themes[0].clip_editor.space.header = (0.137255, 0.137255, 0.137255, 1.000000)
        bpy.context.preferences.themes[0].topbar.space.header = (0.137255, 0.137255, 0.137255, 1.000000)
    if (bpy.context.mode == 'POSE' and bpy.context.object.pose.use_mirror_x) or \
            ((bpy.context.mode == 'EDIT_ARMATURE' or
              bpy.context.mode == 'EDIT_MESH' or
              bpy.context.mode == 'PARTICLE' or
              bpy.context.mode == 'PAINT_WEIGHT' or
              bpy.context.mode == 'PAINT_TEXTURE') and bpy.context.object.data.use_mirror_x):
        create_x_axis_message()
    else:
        remove_x_axis_message()

    if bpy.context.mode == 'PARTICLE':
        if bpy.context.scene.tool_settings.particle_edit.use_preserve_length == False:
            create_preserve_strand_lengths_message()
        else:
            remove_preserve_strand_lengths_message()

        if bpy.context.scene.tool_settings.particle_edit.use_preserve_root == False:
            create_preserve_root_positions_message()
        else:
            remove_preserve_root_positions_message()
    else:
        remove_preserve_strand_lengths_message()
        remove_preserve_root_positions_message()

def register():
    bpy.app.handlers.load_post.append(LoadPost_header_col)

def unregister():
    bpy.app.handlers.load_post.remove(LoadPost_header_col)

if __name__ == "__main__":
    register()
