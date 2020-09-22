import math
import json
import contextlib

with contextlib.redirect_stdout(None):
    import pygame

pygame.init()

class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Point({self.x}, {self.y}, {self.z})"

    def project(self, shift, scale):
        if self.z >= 1:
            return (int(scale * self.x / self.z + shift[0]),
                    int(scale * self.y / self.z + shift[1]))
        else:
            raise ValueError("Invisible point")

    def transform(self, pos):
        rot_x = self.x * math.cos(pos.angle) - self.z * math.sin(pos.angle)
        rot_z = self.x * math.sin(pos.angle) + self.z * math.cos(pos.angle)

        return Point(pos.scale * rot_x + pos.center[0],
                     pos.scale * self.y + pos.center[1],
                     pos.scale * rot_z + pos.center[2])

class Segment:
    def __init__(self, point_start, point_finish):
        self.start = point_start
        self.finish = point_finish

    def project(self, shift, scale):
        return (self.start.project(shift, scale),
                self.finish.project(shift, scale))

    def transform(self, pos):
        return Segment(self.start.transform(pos),
                       self.finish.transform(pos))

    def draw(self, surf, shift, scale):
        pygame.draw.aaline(surf, (0, 0, 0), *self.project(shift, scale))

class Position:
    STEP = 1/30
    
    def __init__(self, center, angle, scale):
        self.center = center
        self.angle = angle
        self.scale = scale

    def update(self): 
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
            
        if mouse[0]:
            self.angle += math.pi / 60
        if mouse[2]:
            self.angle -= math.pi / 60

        if keys[pygame.K_w] and self.center[1] > -1.5:
            self.center[1] -= self.STEP
        if keys[pygame.K_s] and self.center[1] < 1.5:
            self.center[1] += self.STEP
        if keys[pygame.K_a] and self.center[0] > -1.5:
            self.center[0] -= self.STEP
        if keys[pygame.K_d] and self.center[0] < 1.5:
            self.center[0] += self.STEP
        if keys[pygame.K_q] and self.center[2] < 8:
            self.center[2] += self.STEP
        if keys[pygame.K_e] and self.center[2] > 5:
            self.center[2] -= self.STEP

def get_integer(lower_bound, upper_bound):
    while True:
        try:
            res = int(input())
            if lower_bound <= res <= upper_bound:
                return res
        except ValueError:
            pass

        print(f"Please, enter an integer from {lower_bound} to {upper_bound}.")


if __name__ == "__main__":
    with open("shape.json", "r") as shape_file:
        shapes = json.load(shape_file)
    
    
    print("Choose the shape:")
    names = list(enumerate(shapes.keys()))
    for i, name in names:
        print(f"{i+1}. {name}")
    n = get_integer(1, len(names))
    shape = shapes[names[n-1][1]]
    
    segments = [Segment(Point(*elem[0]), Point(*elem[1])) for elem in shape]

    screen = pygame.display.set_mode((500, 500))
    pygame.display.set_caption("Simple 3D")

    clock = pygame.time.Clock()
    pos = Position([0, 0, 6.5], 0, 1)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4 and pos.scale < 1:
                    pos.scale += 0.1
                elif event.button == 5 and pos.scale > 0.4:
                    pos.scale -= 0.1

        pos.update()
        
        to_show = []
        for segment in segments:
            to_show.append(segment.transform(pos))

        screen.fill((255, 255, 255))

        for segment in to_show:
            segment.draw(screen, (250, 250), 300)
            
        pygame.display.update()
        clock.tick(30)
