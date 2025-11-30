import math
from PIL import Image

# ---------------------------------------------
# Vetores 3D
# ---------------------------------------------
class Vec3:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, k):
        return Vec3(self.x * k, self.y * k, self.z * k)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def norm(self):
        mag = math.sqrt(self.dot(self))
        return self * (1.0 / mag)

# ---------------------------------------------
# Raio
# ---------------------------------------------
class Ray:
    def __init__(self, orig, dir):
        self.orig = orig
        self.dir = dir.norm()

# ---------------------------------------------
# Esfera (objeto)
# ---------------------------------------------
class Sphere:
    def __init__(self, center, radius, color, specular=50, reflective=0.0):
        self.center = center
        self.radius = radius
        self.color = color
        self.specular = specular
        self.reflective = reflective

    def intersect(self, ray):
        oc = ray.orig - self.center
        a = ray.dir.dot(ray.dir)
        b = 2 * oc.dot(ray.dir)
        c = oc.dot(oc) - self.radius * self.radius
        disc = b*b - 4*a*c

        if disc < 0:
            return None

        t1 = (-b - math.sqrt(disc)) / (2*a)
        t2 = (-b + math.sqrt(disc)) / (2*a)
        t = min(t1, t2)

        if t < 0:
            t = max(t1, t2)
            if t < 0:
                return None

        return t

# ---------------------------------------------
# Luz
# ---------------------------------------------
class Light:
    def __init__(self, position, intensity):
        self.position = position
        self.intensity = intensity

# ---------------------------------------------
# Cena
# ---------------------------------------------
class Scene:
    def __init__(self, objects, light):
        self.objects = objects
        self.light = light

# ---------------------------------------------
# Ray Tracing
# ---------------------------------------------
def phong(color, normal, view_dir, light_dir, intensity, specular):
    # componente difusa
    diff = max(0, normal.dot(light_dir))  

    # componente especular
    reflect_dir = (normal * (2 * normal.dot(light_dir)) - light_dir)
    spec = max(0, reflect_dir.dot(view_dir)) ** (specular)

    r = min(255, int(color[0] * (0.1 + diff * intensity + 0.5 * spec)))
    g = min(255, int(color[1] * (0.1 + diff * intensity + 0.5 * spec)))
    b = min(255, int(color[2] * (0.1 + diff * intensity + 0.5 * spec)))
    return (r, g, b)

def trace_ray(ray, scene, depth=0):
    nearest_t = float('inf')
    nearest_obj = None

    for obj in scene.objects:
        t = obj.intersect(ray)
        if t and t < nearest_t:
            nearest_t = t
            nearest_obj = obj

    if nearest_obj is None:
        return (20, 20, 40)  # fundo azul escuro

    # ponto de interseção
    hit = ray.orig + ray.dir * nearest_t

    # normal
    normal = (hit - nearest_obj.center).norm()

    # direção para luz
    to_light = (scene.light.position - hit).norm()

    # sombras: lança um raio até a luz
    shadow_ray = Ray(hit + normal * 0.001, to_light)
    for obj in scene.objects:
        if obj.intersect(shadow_ray):
            return (10, 10, 10)  # sombra escura

    # iluminação de Phong
    view_dir = (ray.orig - hit).norm()
    color = phong(
        nearest_obj.color,
        normal,
        view_dir,
        to_light,
        scene.light.intensity,
        nearest_obj.specular
    )

    # reflexão
    if depth < 2 and nearest_obj.reflective > 0:
        reflect_dir = ray.dir - normal * (2 * ray.dir.dot(normal))
        reflect_ray = Ray(hit + normal * 0.001, reflect_dir)
        reflect_color = trace_ray(reflect_ray, scene, depth + 1)

        # mistura reflexão com cor do objeto
        r = int(color[0] * (1 - nearest_obj.reflective) + reflect_color[0] * nearest_obj.reflective)
        g = int(color[1] * (1 - nearest_obj.reflective) + reflect_color[1] * nearest_obj.reflective)
        b = int(color[2] * (1 - nearest_obj.reflective) + reflect_color[2] * nearest_obj.reflective)
        return (r, g, b)

    return color

# ---------------------------------------------
# Render
# ---------------------------------------------
def render():
    width, height = 600, 400
    camera = Vec3(0, 0, -1)
    image = Image.new("RGB", (width, height))
    pixels = image.load()

    # cena com 3 esferas
    objects = [
        Sphere(Vec3(0, -0.2, 3), 1, (200, 50, 50), specular=200, reflective=0.6),
        Sphere(Vec3(-1.5, 0, 4), 1, (50, 200, 50), specular=100),
        Sphere(Vec3(2, 0, 4), 1, (50, 50, 200), specular=100),
        Sphere(Vec3(0, -5001, 0), 5000, (200, 200, 200), specular=10, reflective=0.1) # chão grande
    ]

    light = Light(Vec3(5, 10, -5), 1.5)

    scene = Scene(objects, light)

    for y in range(height):
        for x in range(width):

            # normaliza para [-1, 1]
            nx = (x - width / 2) / (width / 2)
            ny = -(y - height / 2) / (height / 2)

            # direção do raio
            direction = Vec3(nx, ny, 1)

            ray = Ray(camera, direction)
            color = trace_ray(ray, scene)
            pixels[x, y] = color

    image.save("raytracing_result.png")
    print("Imagem gerada: raytracing_result.png")


# roda o render
render()
