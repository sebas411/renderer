from obj import Obj
from lib import *
from math import cos, sin

BLACK = color(0, 0, 0)
WHITE = color(255, 255, 255)

class Renderer(object):
  def __init__(self, width, height, light=Light(V3(0,0,1), 1)):
    self.light = light
    self.width = width
    self.height = height
    self.current_color = WHITE
    self.current_texture = None
    self.second_texture = None
    self.clear()

  def setCurrentColor(self, color):
    self.current_color = color

  def clear(self):
    self.framebuffer = [[BLACK for x in range(self.width)] for y in range(self.height)]
    self.zbuffer = [[float('-inf') for x in range(self.width)] for y in range(self.height)]
  
  def render(self, filename='render.bmp'):
    writebmp(filename, self.width, self.height, self.framebuffer)

  def loadBackground(self, path):
    t = Texture(path)
    self.framebuffer = t.pixels

  def point(self, x, y, color = None):
    x, y = int(x), int(y)
    self.framebuffer[y][x] = color or self.current_color

  def triangle(self):
    A = next(self.active_vertex_array)
    B = next(self.active_vertex_array)
    C = next(self.active_vertex_array)

    if self.current_texture:
      tA, itA = next(self.active_vertex_array)
      tB, itB = next(self.active_vertex_array)
      tC, itC = next(self.active_vertex_array)

    if self.current_normals:
      nA = next(self.active_vertex_array)
      nB = next(self.active_vertex_array)
      nC = next(self.active_vertex_array)

    xmin, xmax, ymin, ymax = bbox(A, B, C)
    if xmin < 0: xmin = 0
    if ymin < 0: ymin = 0
    if xmax >= self.width: xmax = self.width - 1
    if ymax >= self.height: ymax = self.height - 1

    for x in range(xmin, xmax + 1):
      for y in range(ymin, ymax + 1):
        P = V2(x, y)
        w, v, u = barycentric(A, B, C, P)
        if w < 0 or v < 0 or u < 0:
          continue

        if self.current_normals:
          varying_normals=(nA, nB, nC)
        else:
          varying_normals=None
        
        if self.current_texture:
          tx = tA.x * w + tB.x * v + tC.x * u
          ty = tA.y * w + tB.y * v + tC.y * u
          col = self.active_shader(
            self,
            triangle=(A, B, C),
            bar=(w, v, u),
            tex_coords=(tx, ty),
            varying_normals=varying_normals,
            isSecond=itA and itB and itC
          )

        else:
          col = self.active_shader(
            self,
            triangle=(A, B, C),
            bar=(w, v, u),
            varying_normals=varying_normals
          )
        z = A.z * w + B.z * v + C.z * u
        if z > self.zbuffer[y][x]:
          self.point(x, y, color=col)
          self.zbuffer[y][x] = z

  def transform(self, v):
    augmented_vertex = Vertex([v.x, v.y, v.z, 1])
    transformed_vertex = (self.Viewport @ self.Projection @ self.View @ self.Model @ augmented_vertex).transpose().mat[0]
    transformed_vertex = V3(
      transformed_vertex[0] / transformed_vertex[3],
      transformed_vertex[1] / transformed_vertex[3],
      transformed_vertex[2] / transformed_vertex[3],
    )
    return transformed_vertex

  def normalTransform(self, v):
    augmented_vertex = Vertex([v.x, v.y, v.z, 1])
    transformed_vertex = (self.Rotation @ augmented_vertex).transpose().mat[0]
    transformed_vertex = V3(
      transformed_vertex[0] / transformed_vertex[3],
      transformed_vertex[1] / transformed_vertex[3],
      transformed_vertex[2] / transformed_vertex[3],
    )
    return transformed_vertex

  def load(self, filename, translate=(0, 0, 0), scale=(1, 1, 1), rotate=(0, 0, 0)):
    self.loadModelMatrix(translate, scale, rotate)
    model = Obj(filename)

    vertex_buffer_object = []

    vv = 0
    vt = 0
    vn = 0

    for face in model.faces:
      for v in range(len(face)):
        vertex = self.transform(V3(*model.vertices[face[v][0]-1]))
        vertex_buffer_object.append(vertex)
        vv += 1

      if self.current_texture:
        for v in range(len(face)):
          tvertex = [V3(*model.tvertices[face[v][1]-1][0]), model.tvertices[face[v][1]-1][1]]
          vertex_buffer_object.append(tvertex)
          vt += 1

      if len(face[v]) > 2:
        self.current_normals = True
        for v in range(len(face)):
          normal = self.normalTransform(V3(*model.normals[face[v][2]-1])).norm()
          vertex_buffer_object.append(normal)
          vn += 1
      else:
        self.current_normals = False
    self.active_vertex_array = iter(vertex_buffer_object)
  
  def loadModelMatrix(self, translate=(0, 0, 0), scale=(1, 1, 1), rotate=(0, 0, 0)):
    translate = V3(*translate)
    scale = V3(*scale)
    rotate = V3(*rotate)

    translation_matrix = Matrix([
      [1, 0, 0, translate.x],
      [0, 1, 0, translate.y],
      [0, 0, 1, translate.z],
      [0, 0, 0, 1],
    ])

    a = rotate.x
    rotation_matrix_x = Matrix([
      [1, 0, 0, 0],
      [0, cos(a), -sin(a), 0],
      [0, sin(a), cos(a), 0],
      [0, 0, 0, 1],
    ])

    a = rotate.y
    rotation_matrix_y = Matrix([
      [cos(a), 0, sin(a), 0],
      [0, 1, 0, 0],
      [-sin(a), 0, cos(a), 0],
      [0, 0, 0, 1],
    ])
    a = rotate.z
    rotation_matrix_z = Matrix([
      [cos(a), -sin(a), 0, 0],
      [sin(a), cos(a), 0, 0],
      [0, 0, 1, 0],
      [0, 0, 0, 1],
    ])

    rotation_matrix = rotation_matrix_x @ rotation_matrix_y @ rotation_matrix_z
    self.Rotation = rotation_matrix

    scale_matrix = Matrix([
      [scale.x, 0, 0, 0],
      [0, scale.y, 0, 0],
      [0, 0, scale.z, 0],
      [0, 0, 0, 1],
    ])

    self.Model = translation_matrix @ rotation_matrix @ scale_matrix

  def loadViewMatrix(self, x, y, z, center):
    M = Matrix([
      [x.x, x.y, x.z, 0],
      [y.x, y.y, y.z, 0],
      [z.x, z.y, z.z, 0],
      [0, 0, 0, 1],
    ])

    O = Matrix([
      [1, 0, 0, -center.x],
      [0, 1, 0, -center.y],
      [0, 0, 1, -center.z],
      [0, 0, 0, 1],
    ])

    self.View = M @ O

  def loadProjectionMatrix(self, coeff):
    self.Projection = Matrix([
      [1, 0, 0, 0],
      [0, 1, 0, 0],
      [0, 0, 1, 0],
      [0, 0, coeff, 1],
    ])

  def loadViewportMatrix(self, x=0, y=0):
    lower = self.height if self.height < self.width else self.width
    self.Viewport = Matrix([
      [lower/2, 0, 0, x + self.width/2],
      [0, lower/2, 0, y + self.height/2],
      [0, 0, lower/2, 0],
      [0, 0, 0, 1],
    ])

  def lookAt(self, eye, center, up):
    z = (eye - center).norm()
    x = (up @ z).norm()
    y = (z @ x).norm()
    

    self.loadViewMatrix(x, y, z, center)
    self.loadProjectionMatrix(-1/(eye - center).length())
    self.loadViewportMatrix()

  def draw_arrays(self, polygon):
    if polygon == 'TRIANGLE':
      try:
        while True:
          self.triangle()
      except StopIteration:
        print('Done')
      
