from math import *
from random import *
from pyray import *
from time import *
from superEngine import *
from materials import *

width = 800
height = 600

world = World(300, 150)
camera = CAM(0, 0, 5) 
playing = True
mouse_on_clickable = False
brush_size = 3
brush_density = 100

materials = [Stone, Sand, Water, Sky_stone, Wood, Fire, Steam, Ash, Dirt, Lava, Tnt, Ice, Plastic, Super_Ice, Oil]
selected = 0

views = ['color', 'energy', 'velocity', 'moister', 'temperature']
view = 0

background_color = Color(130,130,130,140)
button_color = Color(70, 70, 70, 110)
button_down_color = Color(30, 30, 30, 130)
text_color = Color(25,25,25,255)
transparent = Color(0,0,0,0)

# ---- hud setup ----
hud = Widget(0, 0, 1, 1, "hud", Color(0, 0, 0, 0))
hud.add_child(Widget(10, 5, width-55, 30, "windometer", color=transparent, borders=WHITE))
hud.add_child(Widget(10, 40, width-55, 30, "fpsmeter", color=transparent, borders=WHITE))
hud.add_child(Widget(10, 5, 30, 30, "close", text="x", text_size=25, color=background_color, borders=WHITE, horizontal_align=END, text_x_offset=3, text_y_offset=0, clickable=True))
hud.add_child(Widget(10, 40, 30, 30, "fullscreen", text="[ ]", text_size=18, color=background_color, borders=WHITE, horizontal_align=END, text_x_offset=11, text_y_offset=1, clickable=True))
hud.add_child(Widget(10, 75, 30, 30, "pause", text="| |", text_size=16, color=background_color, borders=WHITE, horizontal_align=END, text_x_offset=11, text_y_offset=1, clickable=True))
hud.add_child(Widget(10, 5, 30, 30, "materials_btn", text="M", text_size=20, color=background_color, borders=WHITE, horizontal_align=END, vertical_align=END, clickable=True))
hud.add_child(Widget(10, 40, 30, 30, "tools_btn", text="T", text_size=20, color=background_color, borders=WHITE, horizontal_align=END, vertical_align=END, clickable=True))
hud.add_child(Widget(10, 75, 30, 30, "view_btn", text="V", text_size=20, color=background_color, borders=WHITE, horizontal_align=END, vertical_align=END, clickable=True))
hud.add_child(Widget(10, -20, 30, 30, "save_btn", text="S", text_size=20, color=background_color, borders=WHITE, horizontal_align=END, vertical_align=CENTER, clickable=True))
hud.add_child(Widget(10, 15, 30, 30, "load_btn", text="L", text_size=20, color=background_color, borders=WHITE, horizontal_align=END, vertical_align=CENTER, clickable=True))

hud.add_child(Widget(45, 5, 470, 20, "tools_head", text="T O O L S", text_size=20, text_color=text_color, text_x_offset=15, color=WHITE, horizontal_align=END, vertical_align=END, dragable=True, visible=True))
hud.get_child("tools_head").add_child(Widget(0, 20, 470, 135, "tools", color=background_color, borders=WHITE, horizontal_align=END, vertical_align=END))

hud.get_child("tools").add_child(Widget(5, 45, 460, 40, id='density',text='brush density:', text_size=25, color=button_color, borders=WHITE, horizontal_align=END, vertical_align=END, text_align=START, text_x_offset=5))
hud.get_child("density").add_child(Widget(25, 5, 80, 30, id='density-100', text='100%', text_size=26, text_x_offset=5, text_y_offset=1, color=button_down_color, borders=WHITE, horizontal_align=END, vertical_align=END, clickable=True))
hud.get_child("density").add_child(Widget(25+85*1, 5, 80, 30, id='density-60', text='60%', text_size=26, text_x_offset=5, text_y_offset=1, color=button_color, borders=WHITE, horizontal_align=END, vertical_align=END, clickable=True))
hud.get_child("density").add_child(Widget(25+85*2, 5, 80, 30, id='density-30', text='30%', text_size=26, text_x_offset=5, text_y_offset=1, color=button_color, borders=WHITE, horizontal_align=END, vertical_align=END, clickable=True))

hud.get_child("tools").add_child(Widget(5, 90, 460, 40, id='size',text='brush size:', text_size=25, color=button_color, borders=WHITE, horizontal_align=END, vertical_align=END, text_align=START, text_x_offset=5))
hud.get_child("size").add_child(Widget(42+55*0, 5, 50, 30, id='size-15', text='15', text_size=26, text_x_offset=5, text_y_offset=1, color=button_color, borders=WHITE, horizontal_align=END, vertical_align=END, clickable=True))
hud.get_child("size").add_child(Widget(42+55*1, 5, 50, 30, id='size-10', text='10', text_size=26, text_x_offset=5, text_y_offset=1, color=button_color, borders=WHITE, horizontal_align=END, vertical_align=END, clickable=True))
hud.get_child("size").add_child(Widget(42+55*2, 5, 50, 30, id='size-5', text='5', text_size=26, text_x_offset=5, text_y_offset=1, color=button_color, borders=WHITE, horizontal_align=END, vertical_align=END, clickable=True))
hud.get_child("size").add_child(Widget(42+55*3, 5, 50, 30, id='size-3', text='3', text_size=26, text_x_offset=5, text_y_offset=1, color=button_down_color, borders=WHITE, horizontal_align=END, vertical_align=END, clickable=True))
hud.get_child("size").add_child(Widget(42+55*4, 5, 50, 30, id='size-1', text='1', text_size=26, text_x_offset=5, text_y_offset=1, color=button_color, borders=WHITE, horizontal_align=END, vertical_align=END, clickable=True))


hud.add_child(Widget(45, 5, 470, 20, "materials_head", text="M A T E R I A L S", text_size=20, text_color=text_color, text_x_offset=15, color=WHITE, horizontal_align=END, vertical_align=END, dragable=True, visible=False))
hud.get_child("materials_head").add_child(Widget(0, 20, 470, 300, "materials", color=background_color, borders=WHITE, horizontal_align=END, vertical_align=END))

hud.add_child(Widget(5, 5, 150, 20, "view_mode", text="view mode: ", color=Color(0, 0, 0, 0), text_size=20, vertical_align=False, text_align=False))

hud.get_child("windometer").add_child(Widget(0, 0, 120, hud.get_child("windometer").h, id="wind", color=background_color, text="windometer", text_size=20, text_x_offset=13, clickable=True))
hud.get_child("fpsmeter").add_child(Widget(0, 0, 120, hud.get_child("fpsmeter").h, "wind", color=background_color, text="FPS-meter", text_size=20, text_x_offset=7))
def windometer_update():
    hud.get_child("windometer").w = width-55
    draw_rectangle(int(hud.get_child("windometer").x + hud.get_child("windometer").w/2), int(hud.get_child("windometer").y + 4), 1, hud.get_child("windometer").h-8, WHITE)
    if world.wind_toggle:
        if world.max_wind != 0:
            draw_rectangle(int(hud.get_child("windometer").x + hud.get_child("windometer").w/2 + world.wind/world.max_wind*hud.get_child("windometer").w/2), int(hud.get_child("windometer").y + 2), 2, hud.get_child("windometer").h-4, WHITE)
def fpsmeter_update():
    hud.get_child("fpsmeter").w = width-55
    if get_frame_time() != 0:
        draw_rectangle(int(hud.get_child("fpsmeter").x + 1/get_frame_time()/50*hud.get_child("fpsmeter").w-2), int(hud.get_child("fpsmeter").y + 2), 2, hud.get_child("fpsmeter").h-4, WHITE)
def pause():
    global playing
    playing = not playing
    if not playing:
        hud.get_child("pause").text_size = 21
        hud.get_child("pause").text = '>'
        hud.get_child("pause").text_x_offset = 4
    else:
        hud.get_child("pause").text_size = 16
        hud.get_child("pause").text = '| |'
        hud.get_child("pause").text_x_offset = 11
def fullscreen():
    set_window_size(get_monitor_width(get_current_monitor()), get_monitor_height(get_current_monitor()))
    toggle_fullscreen()
    if not is_window_fullscreen():
        set_window_size(800, 600)
def materials_btn():
    hud.get_child("materials_head").visible = not hud.get_child("materials_head").visible
def tools_btn():
    hud.get_child("tools_head").visible = not hud.get_child("tools_head").visible
def view_mode():
    global view
    view += 1
    if is_key_down(KEY_LEFT_SHIFT): view -= 2
    view %= 5
def select_material(m):
    global selected
    selected = m
    for index, button in enumerate(hud.get_child("materials").children):
        if index == m:
            button.color = button_down_color
        else:
            button.color = button_color
def wind_toggle():
    world.wind_toggle = not world.wind_toggle
def save():
    world_save = ''
    for y in range(world.height):
        for x in range(world.width):
            world_save += ' '
            if world.world[y][x] is not None:
                world_save += str(materials.index(world.world[y][x].__class__))
        world_save += '\n'
    f = open("save.sbx", "w")
    f.write(world_save)
    f.close()
def load():
    f = open("save.sbx", "r")
    world_save = f.read()
    world_save = [line.split(' ') for line in world_save.split('\n')]
    world.world = []
    for y in range(len(world_save)):
        world.world.append([])
        for x in range(len(world_save[y])):
            if world_save[y][x] != '':
                world.world[y].append(materials[int(world_save[y][x])]())
            else:
                world.world[y].append(None)
    f.close()
def view_mode_update():
    hud.get_child("view_mode").text = views[view]
def set_brush_size(s):
    global brush_size
    brush_size = s
    for button in hud.get_child('size').children:
        if button.id == 'size-'+str(s):
            button.color = button_down_color
        else:
            button.color = button_color
def set_brush_density(d):
    global brush_density
    for button in hud.get_child('density').children:
        if button.id == 'density-'+str(d):
            button.color = button_down_color
        else:
            button.color = button_color
    brush_density = d
hud.get_child("view_mode").custom_updates.append(view_mode_update)
hud.get_child("windometer").custom_updates.append(windometer_update)
hud.get_child("wind").execute = wind_toggle
hud.get_child("fpsmeter").custom_updates.append(fpsmeter_update)
hud.get_child("close").execute = close_window
hud.get_child("fullscreen").execute = fullscreen
hud.get_child("pause").execute = pause
hud.get_child("materials_btn").execute = materials_btn
hud.get_child("tools_btn").execute = tools_btn
hud.get_child("view_btn").execute = view_mode
hud.get_child("save_btn").execute = save
hud.get_child("load_btn").execute = load
for i in range(len(materials)):
    hud.get_child("materials").add_child(Widget((i%3)*155+5, int(i/3)*45+5, 150, 40, id="m-"+str(i), text=materials[i].__name__.replace('_', ' '), text_size=20, color=button_color, borders=WHITE, vertical_align=END, horizontal_align=END, clickable=True))
    hud.get_child("m-"+str(i)).execute = [select_material, i]
for i in [1, 3, 5, 10, 15]:
    hud.get_child("size-"+str(i)).execute = [set_brush_size, i]
for i in [30, 60, 100]:
    hud.get_child("density-"+str(i)).execute = [set_brush_density, i]

hud.get_child("materials").h = ceil(len(materials)/3)*45+5
select_material(0)
# ---- window setup ----
set_config_flags(FLAG_WINDOW_RESIZABLE)
init_window( width, height, "superbox 3.0")
render_texture = load_render_texture(world.width, world.height)
set_target_fps(50)
step = 0
while not window_should_close():
    width = get_screen_width()
    height = get_screen_height()
    # ---- input ----
    #   navigation
    if not mouse_on_clickable:
        if is_mouse_button_down(MOUSE_BUTTON_MIDDLE):
            camera.x += get_mouse_delta().x * .8
            camera.y += get_mouse_delta().y * .8
        if get_mouse_wheel_move() > 0: camera.vz += camera.scroll_speed
        if get_mouse_wheel_move() < 0: camera.vz -= camera.scroll_speed
        if (is_mouse_button_down(MOUSE_BUTTON_LEFT) or is_mouse_button_down(MOUSE_BUTTON_RIGHT)) and not (is_key_down(KEY_LEFT_SHIFT) or is_key_down(KEY_RIGHT_SHIFT)):
            x = int((get_mouse_x() - camera.x) / camera.z) % world.width
            y = int((- get_mouse_y() + camera.y) / camera.z) % world.height
            for y0 in range(int(-brush_size-1), int(brush_size+1)):
                for x0 in range(int(-brush_size-1), int(brush_size+1)):
                    if y0**2 + x0**2 <= brush_size**2:
                        x1 = (x0 + x) % world.width
                        y1 = (y0 + y) % world.height
                        if x1 < world.width and x1 >= 0 and y1 < world.height and y1 >= 0:
                                if random() < (brush_density/100)**2:
                                    world.world[y1][x1] = materials[selected]()
                                    if is_mouse_button_down(MOUSE_BUTTON_RIGHT):
                                        world.world[y1][x1] = None
    if is_key_pressed(KEY_F): fullscreen()
    if is_key_pressed(KEY_SPACE): pause()
    if is_key_pressed(KEY_TAB) or is_key_pressed(KEY_V): view_mode()
    if is_key_pressed(KEY_S): save()
    if is_key_pressed(KEY_L): load()
    if is_key_pressed(KEY_M): materials_btn()
    if is_key_pressed(KEY_T): tools_btn()
    # ---- simulation ----
    step += 1
    
    if camera.z * (1 + camera.vz) > 1.2:
        camera.z *= 1 + camera.vz
        camera.x *= 1 + camera.vz
        camera.y *= 1 + camera.vz
    else: camera.vx = 0
    camera.vz *= .8
    if abs(camera.vz) < .01: camera.vz = 0

    if playing:
        world.update()

    # ---- rendering ----
    begin_drawing()
    clear_background(WHITE)
    
    draw_rectangle_gradient_v(0, 0, width, height+100, Color(160, 220, 250, 255), Color(80, 185, 240, 255))
    render_texture = world.render_texture(render_texture, view)
    world.render(render_texture, camera, width, height)

    # ui
    set_mouse_cursor(0)
    mouse_on_clickable = hud.update()
    if mouse_on_clickable: set_mouse_cursor(4)
    elif is_cursor_on_screen(): set_mouse_cursor(3)

    end_drawing()

close_window()