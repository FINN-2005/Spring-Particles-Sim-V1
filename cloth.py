import pygame
pygame.init()
from pygame import Vector2 as V2

# Constants
gravity = V2(0, 0.08)  # Downward gravity
dampening_factor = 0.96 # Damping to stabilize the system

class Particle:
    def __init__(self, x, y, mass=1, locked=False):
        self.pos = V2(x, y)
        self.vel = V2()
        self.mass = mass
        self.locked = locked
        # self.locked = False

    def draw(self, screen):
        pygame.draw.circle(screen, 'blue', self.pos, 5)
        pygame.draw.circle(screen, 'white', self.pos, 5, 2)

    def update(self, dt):
        if self.locked:
            return
        self.vel *= dampening_factor
        self.vel += gravity
        self.pos += self.vel * dt



class Spring:
    def __init__(self, a: Particle, b: Particle, k=0.2, rest_len=20):
        self.k = k
        self.rest_len = rest_len
        self.a = a
        self.b = b

    def draw(self, screen):
        pygame.draw.line(screen, 'white', self.a.pos, self.b.pos, 1)

    def update(self, dt):
        S = self.b.pos - self.a.pos
        distance = S.length()
        if distance != 0:  # Avoid division by zero
            force = -self.k * (distance - self.rest_len) * S.normalize()
            if not self.b.locked:
                self.b.vel += force / self.b.mass * dt
            if not self.a.locked:
                self.a.vel -= force / self.a.mass * dt


# Grid Setup
grid_width, grid_height = 41, 20  # Number of particles in grid
particle_spacing = 15  # Rest length of springs
particles:list[list[Particle]] = []
springs = []

# Create Particles
for y in range(grid_height):
    row = []
    for x in range(grid_width):
        locked = (y == 0 and x % (grid_width//10 + 1) == 0)  # Lock corners of the top row
        row.append(Particle(x * particle_spacing + 60, y * particle_spacing + 10, locked=locked, mass=1))
    particles.append(row)

# Create Springs (connect neighbors)
for y in range(grid_height):
    for x in range(grid_width):
        if x < grid_width - 1:  # Connect to the particle to the right (horizontal spring)
            springs.append(Spring(particles[y][x], particles[y][x + 1], rest_len=particle_spacing, k=0.222))
        if y < grid_height - 1:  # Connect to the particle below (vertical spring)
            springs.append(Spring(particles[y][x], particles[y + 1][x], rest_len=particle_spacing, k=0.222))


        '''UNCOMMENT LINE 76-79 FOR A BOINGY EFFECT, COMMENT FOR CLOTH EFFECT'''   

        # if x < grid_width - 1 and y < grid_height - 1:  # Optional diagonal connections (down-right)
        #     springs.append(Spring(particles[y][x], particles[y + 1][x + 1], rest_len=particle_spacing * 1.414))
        # if x > 0 and y < grid_height - 1:  # Optional diagonal connections (down-left)
        #     springs.append(Spring(particles[y][x], particles[y + 1][x - 1], rest_len=particle_spacing * 1.414))


# Pygame Setup
screen = pygame.display.set_mode((800, 600))
clock = pygame.Clock()

running = True
while running:
    dt = 80 * clock.tick(60) / 1000  # Cap FPS at 60
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    screen.fill('#2A2A2A')

    # Draw
    for spring in springs:
        spring.draw(screen)
    for row in particles:
        for particle in row:
            particle.draw(screen)
            

    # Mouse Interaction
    mouse_pos = V2(*pygame.mouse.get_pos())
    if pygame.mouse.get_pressed()[0]:  # Left mouse button
        for spring in springs[:]:
            # Calculate the distance from the mouse to the spring's line segment
            a, b = spring.a.pos, spring.b.pos
            ap = mouse_pos - a
            ab = b - a
            ab_length = ab.length()
            if ab_length == 0:
                continue  # Avoid division by zero for degenerate springs
            ab_unit = ab / ab_length
            projection = ab_unit.dot(ap)  # Project ap onto ab
            closest_point = a + ab_unit * max(0, min(projection, ab_length))  # Clamp to the segment
            if closest_point.distance_to(mouse_pos) < 5:  # Threshold for "clicking"
                springs.remove(spring)  # Remove the spring
                break

    # Update
    for spring in springs[:]:  # Update all springs
        spring.update(dt)
        
    ground_level = 450  # Y-coordinate of the ground

    for row in particles[:]:  # Iterate over a copy of the rows
        for particle in row[:]:  # Iterate over a copy of the row
            # Check for out-of-bounds particles
            if not (-200 < particle.pos.x < 1000 and -200 < particle.pos.y < 800):
                # Remove the particle from the row
                row.remove(particle)
                # Remove springs connected to this particle
                springs = [spring for spring in springs if spring.a != particle and spring.b != particle]
                del particle  # Delete particle object to free memory
            else:
                # Handle collision with the ground
                if particle.pos.y > ground_level:
                    particle.pos.y = ground_level  # Reset position to the ground level
                    particle.vel.y = -particle.vel.y * 0.5  # Reverse and dampen vertical velocity
                    if abs(particle.vel.y) < 0.1:  # Optional: Lock particle if it stops bouncing
                        particle.vel.y = 0
                        particle.locked = True
                particle.update(dt)

    pygame.display.flip()
    pygame.display.set_caption(str(sum(len(x) for x in particles)))

pygame.quit()
