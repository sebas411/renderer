from gl import Renderer
from lib import *
from math import pi
from shaders import *


burro = Texture('./models/burro.bmp')
gato1 = Texture('./models/gato1.bmp')
gato2 = Texture('./models/gato2.bmp')
shrek1 = Texture('./models/shrek1.bmp')
shrek2 = Texture('./models/shrek2.bmp')
galleta = Texture('./models/galleta.bmp')
fiona = Texture('./models/Fiona.bmp')

l = Light(V3(0, 0, 1), 1)

r = Renderer(1920, 1080, l)
r.loadBackground('./backgrounds/swamp.bmp')
a = pi / 4

r.lookAt(V3(0, 1.3, 5), V3(0, 1.3, 0), V3(0, 1, 0))
r.active_shader = gouraud

r.current_texture = burro
r.load("./models/burro.obj", (-2, 0, -3), (0.08, 0.08, 0.08), (0, a/2, 0))
r.draw_arrays('TRIANGLE')

r.current_texture = shrek1
r.second_texture = shrek2
r.load("./models/Shrek.obj", (-.7, 0, -5), (0.013, 0.013, 0.013), (0, a/4, 0))
r.draw_arrays('TRIANGLE')

r.current_texture = gato1
r.second_texture = gato2
r.load("./models/Puss.obj", (0, 0, -1), (0.06, 0.06, 0.06), (0, 0, 0))
r.draw_arrays('TRIANGLE')

r.active_shader = flat
r.current_texture = galleta
r.load("./models/galleta.obj", (2, -0.5, -5), (7, 7, 7), (0, -3*a/2, 0))
r.draw_arrays('TRIANGLE')

r.current_texture = fiona
r.load("./models/Fiona.obj", (0, -0.2, -5), (0.9, 0.9, 0.9), (0, -a/4, 0))
r.draw_arrays('TRIANGLE')



r.render()