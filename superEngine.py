from math import *
from random import *
from pyray import *
import inspect
from time import *
from materials import *


Fail = 0
Success = 1
Neighbor = 2

END = 0
START = 1
CENTER = 2

def exchange_temperature(pixel1, pixel2):
    exchange = (pixel1.temperature_exchange + pixel2.temperature_exchange) / 2
    old_temp = pixel1.temperature
    pixel1.temperature = (1+exchange)/2 * pixel1.temperature + (1-exchange)/2 * pixel2.temperature
    pixel2.temperature = (1+exchange)/2 * pixel2.temperature + (1-exchange)/2 * old_temp

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.max_v = 5
        self.wind_toggle = False
        self.wind = 0
        self.max_wind = .04
        self.wind_variable = .001
        self.wind_normalizer = .998
        self.gravity = 0.15
        self.world = []
        for y in range(height):
            self.world.append([])
            for x in range(width):
                self.world[y].append(None)

    def render_texture(self, render_texture, color_mode):
        begin_texture_mode(render_texture)
        clear_background(Color(0, 0, 0, 0))  
        for y in range(self.height):
            if self.world[y].count(None) == self.width: continue
            for x in range(self.width):
                if self.world[y][x] is None: continue
                pixel = self.world[y][x]

                c = WHITE
                if color_mode == 0:  # light mode
                    c = pixel.color
                if color_mode == 1:  # energy mode
                    h = int((180 - sqrt(pixel.vx**2 + pixel.vy**2) * pixel.mass * 100) % 360)  
                    c = color_from_hsv(h, 95, 85)
                if color_mode == 2:  # velocity mode
                    r = min(int(abs(pixel.vx) ** .4 / self.max_v * 250), 250)
                    g = min(int(abs(pixel.vy) ** .4 / self.max_v * 250), 250)
                    b = min(r, g, 70)
                    c = Color(r, g, b, 255)
                if color_mode == 3: # moister mode
                    if hasattr(pixel, 'moister'):
                        m = int(max(min(pixel.moister / 5 * 255, 255), 0))
                        c = Color(m, m, m, 255)
                    else: c = BLACK
                if color_mode == 4: # temperature mode
                    v = pixel.temperature
                    r = 120 # range of temperatures displayed
                    v = min(v, r)
                    v = max(v, -r)
                    v = (v + r) / (r * 2) * 360
                    c = color_from_hsv(int(v), 0.8, 0.8)

                draw_pixel(x, y, c)
        end_texture_mode()
        return render_texture
    
    def render(self, render_texture, camera, width, height):
        x_scale = int(self.width * camera.z)
        y_scale = int(self.height * camera.z)
        for y in range(-2, int(height/y_scale+1)):
            for x in range(-2, int(width/x_scale+1)):
                draw_texture_ex(render_texture.texture,
                Vector2(
                    x*x_scale + camera.x%x_scale,
                    y*y_scale + camera.y%y_scale
                ), 0, camera.z, WHITE)
    
    def attempt_swap(self, x, y, dx, dy):
        if x == dx and y == dy: return Fail
        if self.world[dy][dx] is not None: return Neighbor

        self.world[dy][dx] = self.world[y][x]
        self.world[y][x] = None
        return Success

    def update(self):
        #   world updates 🌍
        
        self.wind += (random()-.5)*self.wind_variable
        if self.wind > self.max_wind: self.wind = self.max_wind
        if self.wind < -self.max_wind: self.wind = -self.max_wind
        self.wind *= self.wind_normalizer
        wind_side = -1
        if self.wind < 0: wind_side = 1

        total_energy = 0
        for y in range(self.height):
            if self.world[y].count(None) == self.width: continue
            for x, pixel in enumerate(self.world[y]):
                if pixel is None: continue

                if abs(pixel.vy) < .5:
                    pixel.vy -= self.gravity * pixel.gravity_effect 
                if self.wind_toggle:
                    if self.world[y][(x+wind_side)%(self.width-1)] is None:
                        pixel.vx += self.wind / pixel.mass

                #   physics ⛓️
                
                dx, dy = 0, 0 # velocity in this simulation is just the odds of praticle moving, one step at a time.
                if abs(pixel.vx) > random(): dx = 1
                if pixel.vx < 0: dx *= -1
                if abs(pixel.vy) > random(): dy = 1
                if pixel.vy < 0: dy *= -1
                dx += x
                dy += y

                if dy == 0 and dx == 0:
                    if pixel.liquidity > random():
                        dx = [-1,1][randint(0,1)]

                dx %= self.width
                dy %= self.height

                # moving pixels and physical reactions
                result = self.attempt_swap(x, y, dx, dy)

                if result == Neighbor:
                    neighbor = self.world[dy][dx]
                    # the ratio enery is redestibuted upon
                    ratio = neighbor.mass / (pixel.mass + neighbor.mass)
                    # force = velocity * mass
                    force_x = pixel.vx * pixel.mass
                    force_y = pixel.vy * pixel.mass
                    # particles in the real world do not colide perfectly aligned
                    # i simulate this by transfering a little x energy to y, and some y to x
                    # it also acts as a viscosity parameter since increasing it makes the particle more slippery
                    if  random() < .5:
                        lost_x = force_x * (random()*2-1)*pixel.liquidity
                        lost_y = force_y * (random()*2-1)*pixel.liquidity
                        force_x -= lost_x + lost_y
                        force_y -= lost_y + lost_x

                    # bounce is how much energy is wasted
                    pixel.vx = - force_x * ratio / pixel.mass * pixel.bounce * neighbor.bounce
                    pixel.vy = - force_y * ratio / pixel.mass * pixel.bounce * neighbor.bounce
                    neighbor.vx += force_x * (1 - ratio) / neighbor.mass
                    neighbor.vy += force_y * (1 - ratio) / neighbor.mass
                    if neighbor.vx > self.max_v: neighbor.vx = self.max_v
                    if neighbor.vy > self.max_v: neighbor.vy = self.max_v
                if pixel.vx > self.max_v: pixel.vx = self.max_v
                if pixel.vy > self.max_v: pixel.vy = self.max_v
                total_energy += (pixel.vx + pixel.vy) * pixel.mass
            
                #   chimestry 🧪
                # decay
                for i in range(len(pixel.current_decay_chance)):
                    pixel.current_decay_chance[i] += pixel.decay_chance_growth[i]
                for i in range(len(pixel.current_decay_chance)):
                    if pixel.current_decay_chance[i] > random() * 100:
                        if pixel.decay_to[i] is not None:
                            self.world[y][x] = pixel.decay_to[i]()
                            self.world[y][x].vx = (pixel.vx * pixel.mass) / self.world[y][x].mass
                            self.world[y][x].vy = (pixel.vy * pixel.mass) / self.world[y][x].mass
                        else: self.world[y][x] = None
                # chimical reactions
                if result == Neighbor:
                    neighbor = self.world[dy][dx]
                    for reaction in pixel.reacts_as:
                        if reaction in neighbor.reacts_to:
                            reaction_index = neighbor.reacts_to.index(reaction)
                            for i in range(len(neighbor.reaction_results[reaction_index])):
                                if neighbor.reaction_odds[reaction_index][i] > random():
                                    pixel.reaction_feedback(reaction)
                                    if neighbor.reaction_results[reaction_index][i] is None:
                                        self.world[dy][dx] = None
                                    elif inspect.isclass(neighbor.reaction_results[reaction_index][i]): 
                                        self.world[dy][dx] = neighbor.reaction_results[reaction_index][i]()
                                        self.world[dy][dx].vx = (neighbor.vx * neighbor.mass) / self.world[dy][dx].mass
                                        self.world[dy][dx].vy = (neighbor.vy * neighbor.mass) / self.world[dy][dx].mass
                                    else:
                                        getattr(neighbor, neighbor.reaction_results[reaction_index][i])()
                # temperature exchange 🔥
                if result == Neighbor:
                    neighbor = self.world[dy][dx]
                    exchange_temperature(pixel, neighbor)

                if abs(pixel.temperature) > 1: # temperature lost
                    if pixel.temperature > 0:
                        pixel.temperature -= 0.01
                    else:
                        pixel.temperature += 0.01

                # freezing and melting 🥶🥵
                if result == Neighbor:
                    dx = x
                    dy = y
                if pixel.freeze_at is not None:
                    if pixel.temperature < pixel.freeze_at:
                        if pixel.freeze_to is not None:
                            self.world[dy][dx] = pixel.freeze_to()
                        else:
                            self.world[dy][dx] = None
                if pixel.melt_at is not None:
                    if pixel.temperature > pixel.melt_at:
                        if pixel.melt_to is not None:
                            self.world[dy][dx] = pixel.melt_to()
                        else:
                            self.world[dy][dx] = None

                # explosions 💥
                if self.world[y][x] is not None: # i need to rework this <--------------------------------
                    if self.world[y][x].explosion_chance > random():
                        if random() < 0.01:
                            r = self.world[y][x].explosion_radius
                            self.world[y][x] = None
                            for ey in range(y-r, y+r):
                                ey %= self.height
                                for ex in range(x-r, x+r):
                                    ex %= self.width
                                    if self.world[ey][ex] is not None:
                                        if ey <= y:
                                            self.world[ey][ex].vy -= pixel.explosive_power / self.world[ey][ex].mass
                                        else:
                                            self.world[ey][ex].vy += pixel.explosive_power / self.world[ey][ex].mass
                                        if ex <= x:
                                            self.world[ey][ex].vx -= pixel.explosive_power / self.world[ey][ex].mass
                                        else:
                                            self.world[ey][ex].vx += pixel.explosive_power / self.world[ey][ex].mass
        return total_energy

class CAM:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.scroll_speed = .08
        self.vz = 0

class Widget:
    def __init__(self, x, y, w, h, id=None, color=WHITE, text="", text_size=30, text_color=WHITE, clickable=False, dragable=False, horizontal_align=START, vertical_align=START, text_align=CENTER, text_x_offset=0, text_y_offset=0, borders=Color(0,0,0,0), visible=True):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        if id is None: id = int(random()*10**8)
        self.id = id
        self.color = color
        self.text = text
        self.text_size = text_size
        self.text_color = text_color
        self.clickable = clickable
        self.dragable = dragable
        self.visible = visible
        self.horizontal_align = horizontal_align
        self.vertical_align = vertical_align
        self.text_align = text_align
        self.text_x_offset = text_x_offset
        self.text_y_offset = text_y_offset
        self.borders = borders
        self.children = []
        self.custom_updates = []

    def mouse_over(self):
        x = False
        y = False
        if self.horizontal_align == START:
            if get_mouse_position().x - get_mouse_delta().x > self.x and get_mouse_position().x - get_mouse_delta().x < self.x + self.w: x = True
        elif self.horizontal_align == END:
            if get_mouse_position().x - get_mouse_delta().x > get_screen_width() - self.x - self.w and get_mouse_position().x - get_mouse_delta().x < get_screen_width() - self.x: x = True
        elif self.horizontal_align == CENTER:
            if get_mouse_position().x - get_mouse_delta().x > get_screen_width()/2 + self.x and get_mouse_position().x - get_mouse_delta().x < get_screen_width()/2 + self.x + self.w: x = True
        if self.vertical_align == START:
            if get_mouse_position().y - get_mouse_delta().y > self.y and get_mouse_position().y - get_mouse_delta().y < self.y + self.h: y = True
        elif self.vertical_align == END:
            if get_mouse_position().y - get_mouse_delta().y > get_screen_height() - self.y - self.h and get_mouse_position().y - get_mouse_delta().y < get_screen_height() - self.y: y = True
        elif self.vertical_align == CENTER:
            if get_mouse_position().y - get_mouse_delta().y > get_screen_height()/2 + self.y and get_mouse_position().y - get_mouse_delta().y < get_screen_height()/2 + self.y + self.h: y = True
        return x and y

    def update(self):
        for up in self.custom_updates:
            up()
        on = False
        if self.visible:
            if self.mouse_over():
                if self.clickable:
                    on = True
                    if is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
                        if isinstance(self.execute, list):
                            self.execute[0](self.execute[1])
                        else:
                            self.execute()
                if self.dragable:
                    on = True
                    if is_mouse_button_down(MOUSE_BUTTON_LEFT):
                            self.move_by(get_mouse_delta().x, get_mouse_delta().y)
            if self.horizontal_align == START:
                x = int(self.x)
            elif self.horizontal_align == END:
                x = int(get_screen_width()-self.x-self.w)
            elif self.horizontal_align == CENTER:
                x = int(get_screen_width()/2+self.x)
            if self.vertical_align == START:
                y = int(self.y)
            elif self.vertical_align == END:
                y = int(get_screen_height()-self.y-self.h)
            elif self.vertical_align == CENTER:
                y = int(get_screen_height()/2 + self.y)
            draw_rectangle_lines(x, y, int(self.w), int(self.h), self.borders)
            draw_rectangle(x, y, int(self.w), int(self.h), self.color)
            draw_text(self.text, int( x + (self.w/2-len(self.text)*self.text_size/3 if self.text_align == CENTER else 0) + self.text_x_offset), int(y + self.h/2 - self.text_size/2 + self.text_y_offset), int(self.text_size), self.text_color)
            for child in self.children:
                if child.update(): on = True
        return on

    def execute(self):
        print('executing #'+str(self.id))

    def add_child(self, child):
        child.x += self.x
        child.y += self.y
        self.children.append(child)

    def get_child(self, id, i=0):
        if self.id == id: return self
        for child in self.children:
            r = child.get_child(id, i+1)
            if r is not None: return r
        return None

    def move_by(self, dx, dy):
        if self.horizontal_align == END:
            self.x -= dx
        else:
            self.x += dx
        if self.vertical_align == END:
            self.y -= dy
        else:
            self.y += dy
        for child in self.children:
            child.move_by(dx, dy)

    def print(self, i=0):
        if i == 0: print('\n')
        print("    "*i, end="> #")
        print(self.id)
        for child in self.children:
            child.print(i+1)
    
