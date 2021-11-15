
class Obj(object):
  def __init__(self, filename):
    with open(filename) as f:
      self.lines = f.read().splitlines()
    self.vertices = []
    self.tvertices = []
    self.normals = []
    self.faces = []
    self.read()
  
  def read(self):
    isSecond = False
    for line in self.lines:
      if line:
        prefix, value = line.split(' ', 1)
        if prefix == 'tex_change': isSecond = not isSecond

        if prefix == 'v':
          self.vertices.append(list(map(float, value.split(' '))))
        elif prefix == 'vt':
          self.tvertices.append([list(map(float, value.split(' '))), isSecond])
        elif prefix == 'vn':
          self.normals.append(list(map(float, value.split(' '))))
        elif prefix == 'f':
          retList = []
          for face in value.split(' '):
            inList = []
            for f in face.split('/'):
              inList.append(int(f))
            retList.append(inList)
          self.faces.append(retList)
