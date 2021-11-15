import struct

class V3(object):
  def __init__(self, x, y, z=1):
    self.x = x
    self.y = y
    self.z = z

  def __matmul__(self, other):
    return V3(
        self.y * other.z -  self.z * other.y,
        self.z * other.x -  self.x * other.z,
        self.x * other.y -  self.y * other.x,
    )
  
  def __mul__(self, k):
    return V3(self.x * k, self.y * k, self.z * k)

  def __add__(self, v):
    return V3(self.x + v.x, self.y + v.y, self.z + v.z)

  def __sub__(self, v):
    return V3(self.x - v.x, self.y - v.y, self.z - v.z)
  
  def __mod__(self, v):
    return self.x * v.x + self.y * v.y + self.z * v.z

  def __str__(self):
    return '%.1f, %.1f, %.1f'%(self.x, self.y, self.z)
  
  def length(self):
    return (self.x**2 + self.y**2 + self.z**2)**0.5
  
  def norm(self):
    l = self.length()
    if l == 0:
      return V3(0, 0, 0)
    return V3(self.x/l, self.y/l, self.z/l)

class V2(object):
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def __mul__(self, k):
    return V2(self.x * k, self.y * k)

  def __add__(self, v):
    return V2(self.x + v.x, self.y + v.y)

  def __sub__(self, v):
    return V2(self.x - v.x, self.y - v.y)
  
  def __mod__(self, v):
    return self.x * v.x + self.y * v.y

  def __str__(self):
    return '%.1f, %.1f'%(self.x, self.y)
  
  def length(self):
    return (self.x**2 + self.y**2)**0.5
  
  def norm(self):
    l = self.length()
    if l == 0:
      return V2(0, 0)
    return V2(self.x/l, self.y/l)

class Matrix(object):
  def __init__(self, mat):
    self.mat = mat
    self.precheck()
    self.rows = len(mat)
    self.cols = len(mat[0])
    self.isSquare = self.rows == self.cols

  def precheck(self):
    if not self.mat or not self.mat[0]:
      raise AssertionError('Matrix has empty rows or columns.')
    sublen = len(self.mat[0])
    for row in self.mat:
      if len(row) != sublen:
        raise AssertionError('The rows in the matrix are not of the same lenght')
  
  def __matmul__(self, other):
    if type(other) == V3:
      other = Matrix([[other.x, other.y, other.z]]).transpose()
    elif type(other) == V2:
      other = Matrix([[other.x, other.y]]).transpose()

    if self.cols != other.rows:
      raise AssertionError("Matrixes can't be multiplied because middle values are not the same")
    middle = self.cols
    mat = [] 
    for nrow in range(self.rows):
      rmat = []
      for ncol in range(other.cols):
        x = 0
        for n in range(middle):
          x += self.mat[nrow][n] * other.mat[n][ncol]
        rmat.append(x)
      mat.append(rmat)
    return Matrix(mat)

  def __pow__(self, k):
    if not self.isSquare:
      raise AssertionError('Matrix is not square, it cannot be multiplied by itself')
    m = IdentityMatrix(self.rows)
    print(k)
    for _ in range(k):
      m @= self
    
    return m
  
  def __str__(self):
    string = '\n'
    for row in self.mat:
      string += '|'
      for item in row:
        string += ' ' + str(item) + ' '
      string += '|'
      string += '\n'
    return string
  
  def transpose(self):
    mat = []
    for nrow in range(self.cols):
      rMat = []
      for ncol in range(self.rows):
        rMat.append(self.mat[ncol][nrow])
      mat.append(rMat)
    return Matrix(mat)

class Vertex(Matrix):
  def __init__(self, ver):
    sub = Matrix([ver]).transpose()
    Matrix.__init__(self, sub.mat)

class IdentityMatrix(Matrix):
  def __init__(self, n):
    mat = []
    for i in range(n):
      rmat = []
      for j in range(n):
        if i - j == 0:
          rmat.append(1)
        else:
          rmat.append(0)
      mat.append(rmat)
    Matrix.__init__(self, mat)

def char(c):
  return struct.pack('=c', c.encode('ascii'))

def hword(w):
  return struct.pack('=h', w)

def word(d):
  return struct.pack('=l', d)

def ccolor(v):
  return max(0, min(255, int(v)))

def bbox(A, B, C):
  xmin = A.x
  xmax = A.x
  if B.x < xmin: xmin = B.x
  if C.x < xmin: xmin = C.x

  if B.x > xmax: xmax = B.x
  if C.x > xmax: xmax = C.x

  ymin = A.y
  ymax = A.y
  if B.y < ymin: ymin = B.y
  if C.y < ymin: ymin = C.y

  if B.y > ymax: ymax = B.y
  if C.y > ymax: ymax = C.y
  return int(xmin), int(xmax), int(ymin), int(ymax)

def barycentric(A, B, C, P):
  c = V3(C.x - A.x, B.x - A.x, A.x - P.x) @ V3(C.y - A.y, B.y - A.y, A.y - P.y)
  cx = c.x
  cy = c.y
  cz = c.z

  if abs(cz) < 1: return -1, -1, -1

  u = cx / cz
  v = cy / cz
  w = 1 - (u + v)

  return w, v, u

class color(object):
  def __init__(self, r, g, b):
    self.r = r
    self.g = g
    self.b = b

  def __add__(self, other_color):
    r = self.r + other_color.r
    g = self.g + other_color.g
    b = self.b + other_color.b

    return color(r, g, b)

  def __mul__(self, other):
    r = self.r * other
    g = self.g * other
    b = self.b * other
    return color(r, g, b)
  
  
  def toBytes(self):
    r = ccolor(self.r)
    g = ccolor(self.g)
    b = ccolor(self.b)
    return bytes([b, g, r])


def writebmp(filename, width, height, pixels):
  f = open(filename, 'bw')

  f.write(char('B'))
  f.write(char('M'))
  f.write(word(54 + width * height * 3))
  f.write(word(0))
  f.write(word(54))

  f.write(word(40))
  f.write(word(width))
  f.write(word(height))
  f.write(hword(1))
  f.write(hword(24))
  f.write(word(0))
  f.write(word(width * height * 3))
  f.write(word(0))
  f.write(word(0))
  f.write(word(0))
  f.write(word(0))
  for y in range(height):
    for x in range(width):
      f.write(pixels[y][x].toBytes())
    for _ in range(width % 4):
      f.write(struct.pack('=x'))
  f.close()

class Light(object):
  def __init__(self, pos, intensity):
    self.pos = pos.norm()
    self.intensity = intensity

class Texture(object):
  def __init__(self, path):
    self.path = path
    self.read()
  
  def read(self):
    image = open(self.path, 'rb')
    image.seek(10)
    header_size = struct.unpack('=l', image.read(4))[0]
    image.seek(18)

    self.width = struct.unpack('=l', image.read(4))[0]
    self.height = struct.unpack('=l', image.read(4))[0]
    self.pixels = []
    image.seek(28)
    pixel_size = struct.unpack('=h', image.read(2))[0]
    #print(pixel_size)
    image.seek(header_size)
    for y in range(self.height):
      self.pixels.append([])
      for _ in range(self.width):
        b = ord(image.read(1))
        g = ord(image.read(1))
        r = ord(image.read(1))
        if pixel_size == 32: image.read(1)
        self.pixels[y].append(color(r, g, b))
    image.close()

  def get_color(self, tx, ty, intensity):
    x = int(tx * self.width)
    y = int(ty * self.height)
    if x >= self.width: x = self.width - 1
    if y >= self.height: y = self.height - 1

    return self.pixels[y][x] * intensity