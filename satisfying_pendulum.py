import pygame
pygame.init()
from pygame import Vector2 as V2

# a spring pendulum

screen = pygame.display.set_mode((1280,720))
clock = pygame.Clock()

anchor = V2(400,200)
bob = V2(400,350)

force = V2(1,1)
velocity = V2()
gravity = V2(0,0.07)
mass = 10
K = 0.2            # spring constant
rest_length = 100
dampening_factor = 0.999

dt_factor = 70

running = True
while running:
    dt = dt_factor * clock.tick() / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
    
    screen.fill('#2A2A2A')
    
    # DRAW
    pygame.draw.line(screen, 'white', anchor, bob, 4)
    pygame.draw.circle(screen, 'blue', anchor, 10)
    pygame.draw.circle(screen, 'white', anchor, 10, 3)
    pygame.draw.circle(screen, 'blue', bob, 30)
    pygame.draw.circle(screen, 'white', bob, 30, 3)
    
    # GRAB
    if pygame.mouse.get_pressed()[0]:
        anchor = V2(*pygame.mouse.get_pos())
        # velocity = V2()

    # UPDATE
    S = bob - anchor
    force = -K * (S.length() - rest_length) * S.normalize()           # spring force
    accel = force / mass
    velocity += accel * dt
    velocity *= dampening_factor
    velocity += gravity
    bob += velocity * dt
    
    pygame.display.flip()
    
pygame.quit()