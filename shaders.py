def gouraud(render, **kwargs):
  w, v, u = kwargs['bar']
  nA, nB, nC = kwargs['varying_normals']

  iA, iB, iC = [n % render.light.pos for n in (nA, nB, nC)]

  intensity = w * iA + v * iB + u * iC
  if render.current_texture:
    tx, ty = kwargs['tex_coords']
    isSecond = kwargs['isSecond']
    tcolor = render.current_texture.get_color(tx, ty, intensity) if not isSecond else render.second_texture.get_color(tx, ty, intensity)
  else:
    tcolor = render.current_color * intensity

  return tcolor

def flat(render, **kwargs):
  A, B, C = kwargs['triangle']
  normal = ((B - A) @ (C - A)).norm()
  intensity = normal % render.light.pos

  if render.current_texture:
    tx, ty = kwargs['tex_coords']
    isSecond = kwargs['isSecond']
    tcolor = render.current_texture.get_color(tx, ty, intensity) if not isSecond else render.second_texture.get_color(tx, ty, intensity)
  else:
    tcolor = render.current_color * intensity

  return tcolor