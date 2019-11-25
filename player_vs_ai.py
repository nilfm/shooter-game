import pygame
import time
import math
import copy
import random
from pygame.locals import *

RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SCREEN_SIZE = (1280, 720)
BULLET_RADIUS = 3
BULLET_VEL = 7
COOLDOWN_TIME = 25
MAX_SCOPE_ANGLE = 45
MAX_SCOPE_LENGTH = 30
LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3
SHOOT = 4
CLOSE_AIM = 5
DIRS = [(0, -1, 0), (1, 1, 0), (2, 0, 1), (3, 0, -1)]

def distance_sq(pos1, pos2):
    return sum((x-y)**2 for x, y in zip(pos1, pos2))

def distance(pos1, pos2):
    return math.sqrt(distance_sq(pos1, pos2))

def normalize(vec):
    norm = math.sqrt(distance_sq((0, 0), vec))
    return (vec[0]/norm, vec[1]/norm)

def detect_collision(warrior1, warrior2):
    res = [] # Contains pairs (winning warrior, index of bullet)
    for w1, w2 in [(warrior1, warrior2), (warrior2, warrior1)]:
        for i, bullet in enumerate(w1.bullets):
            if (distance_sq(bullet.pos, w2.pos) <= w2.radius**2):
                res.append((w1, i))
    return res

class Controller:
    def __init__(self, warrior, enemy):
        self.warrior = warrior
        self.enemy = enemy
    
    def decision(self):
        for bullet in sorted(self.enemy.bullets, key=lambda b: distance_sq(b.pos, self.warrior.pos)):
            bullet_copy = copy.copy(bullet)
            bullet_copy.move_distance(distance(bullet.pos, self.warrior.pos))
            if (distance_sq(bullet_copy.pos, self.warrior.pos) <= 2*self.warrior.radius**2):
                new_dists = []
                for move, dx, dy in DIRS:
                    new_pos = (self.warrior.pos[0] + dx, self.warrior.pos[1] + dy)
                    new_dists.append(distance_sq(new_pos, bullet_copy.pos))
                return new_dists.index(max(new_dists))
                
        if random.randint(0, self.warrior.scope_angle):
            return CLOSE_AIM
        else:
            return SHOOT
            
    
    def aim(self):
        vec = (self.enemy.pos[0]-self.warrior.pos[0], self.enemy.pos[1]-self.warrior.pos[1])
        return math.atan2(vec[1], vec[0]) 
 
class Bullet:
    def __init__(self, player, pos, direction):
        self.radius = BULLET_RADIUS
        self.player = player
        self.pos = pos
        self.dir = direction
    
    def move(self):
        self.pos = (self.pos[0] + BULLET_VEL*self.dir[0], self.pos[1] + BULLET_VEL*self.dir[1])
    
    def move_distance(self, dist):
        self.pos = (self.pos[0] + dist*self.dir[0], self.pos[1] + dist*self.dir[1])
    
    def render(self, display):
        pygame.draw.circle(display, BLACK, [int(x) for x in self.pos], self.radius)
        
    def inside(self):
        if (self.pos[0] > SCREEN_SIZE[0]): return False
        if (self.pos[1] > SCREEN_SIZE[1]): return False
        if (self.pos[0] < 0): return False
        if (self.pos[1] < 0): return False
        return True

class Warrior:
    def __init__(self, player):
        self.player = player
        self.radius = 20
        self.aim = (-1, 0)
        self.cooldown = 0
        self.score = 0
        self.scope_angle = MAX_SCOPE_ANGLE
        self.scope_length = MAX_SCOPE_LENGTH
        if player == 1:
            self.pos = (SCREEN_SIZE[0]//4, SCREEN_SIZE[1]//2)
            self.bounds = (0, SCREEN_SIZE[0]//2, 0, SCREEN_SIZE[1])
            self.color = RED
        else:
            self.pos = (3*SCREEN_SIZE[0]//4, SCREEN_SIZE[1]//2)
            self.bounds = (SCREEN_SIZE[0]//2, SCREEN_SIZE[0], 0, SCREEN_SIZE[1])
            self.color = BLUE
        self.bullets = []
    
    def inside(self, x, y):
        if x - self.radius - 1 < self.bounds[0]: return False
        if x + self.radius + 1 > self.bounds[1]: return False
        if y - self.radius < self.bounds[2]: return False
        if y + self.radius > self.bounds[3]: return False
        return True
    
    def move(self, dx, dy):
        new_pos = (self.pos[0]+dx, self.pos[1]+dy)
        if (self.inside(*new_pos)):
            self.pos = (self.pos[0]+dx, self.pos[1]+dy)
    
    def draw_scope(self, display, length, width):
        pygame.draw.line(display, BLACK, self.pos, (self.pos[0] + length*self.aim[0] - width*self.aim[1], self.pos[1] + length*self.aim[1] + width*self.aim[0]), 1)
        pygame.draw.line(display, BLACK, self.pos, (self.pos[0] + length*self.aim[0] + width*self.aim[1], self.pos[1] + length*self.aim[1] - width*self.aim[0]), 1)
    
    def render(self, display):
        self.draw_scope(display, self.scope_length, self.scope_length*math.tan(math.radians(self.scope_angle)))
        pygame.draw.circle(display, self.color, self.pos, self.radius)
        for bullet in self.bullets:
            bullet.render(display)

    def shoot(self):
        if (self.cooldown == 0):
            angle = math.radians(random.triangular(-self.scope_angle, self.scope_angle))
            aim_angle = math.atan2(math.radians(self.aim[1]), math.radians(self.aim[0]))
            direction = (math.cos(angle + aim_angle), math.sin(angle + aim_angle))
            self.bullets.append(Bullet(self.player, self.pos, direction))
            self.cooldown = COOLDOWN_TIME
            self.scope_angle = MAX_SCOPE_ANGLE
    
    def dec_cooldown(self):
        self.cooldown = max(0, self.cooldown-1)
    
    def close_aim(self):
        if self.cooldown == 0:
            self.scope_angle -= 1
            if (self.scope_angle < 0):
                self.cooldown = COOLDOWN_TIME
                self.scope_angle = MAX_SCOPE_ANGLE
    
    def move_bullets(self):
        new_bullets = []
        for bullet in self.bullets:
            bullet.move()
            if (bullet.inside()):
                new_bullets.append(bullet)

        self.bullets = new_bullets
    
    def update_aim(self):
        mouse = pygame.mouse.get_pos()
        diff = (mouse[0] - self.pos[0], mouse[1] - self.pos[1]) 
        self.aim = normalize(diff)
    
    def update_aim_ai(self, rad):
        self.aim = (math.cos(rad), math.sin(rad))
    
    def handle_collision(self, bullet_index):
        self.bullets.pop(bullet_index)
        self.score += 1
        return self.score >= 5
            
    
class App:
    def __init__(self):
        self.running = True
        self.display = True
        self.size = self.width, self.height = SCREEN_SIZE
        self.warriors = [Warrior(1), Warrior(2)]
        self.ai = Controller(self.warriors[1], self.warriors[0])
    
    def reset_screen(self):
        self.display.fill(WHITE)
        pygame.draw.line(self.display, BLACK, (SCREEN_SIZE[0]//2, 0), (SCREEN_SIZE[0]//2, SCREEN_SIZE[1]), 2)
        pygame.display.set_caption("Lolgame")
        self.display.blit(self.font.render(f"Score: {self.warriors[0].score}", True, BLACK), [SCREEN_SIZE[0]//4, 15])
        self.display.blit(self.font.render(f"Score: {self.warriors[1].score}", True, BLACK), [3*SCREEN_SIZE[0]//4, 15])
        
    def on_init(self):
        pygame.init()
        self.font = pygame.font.SysFont('Calibri', 24, True, False)
        self.display = pygame.display.set_mode(self.size)
        self.reset_screen()
        pygame.display.update()
        self.running = True
        
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                self.warriors[0].shoot()
    
    def handle_keys(self, keys):
        if keys[pygame.K_w]:
            self.warriors[0].move(0, -1)
        if keys[pygame.K_a]:
            self.warriors[0].move(-1, 0)
        if keys[pygame.K_s]:
            self.warriors[0].move(0, 1)
        if keys[pygame.K_d]:
            self.warriors[0].move(1, 0)
        if keys[pygame.K_SPACE]:
            self.warriors[0].close_aim()
    
    def handle_ai(self):
        aim = self.ai.aim()
        self.warriors[1].update_aim_ai(aim)
        decision = self.ai.decision()
        if decision == DOWN:
            self.warriors[1].move(0, -1)
        elif decision == UP:
            self.warriors[1].move(0, 1)
        elif decision == RIGHT:
            self.warriors[1].move(1, 0)
        elif decision == LEFT:
            self.warriors[1].move(-1, 0)
        elif decision == SHOOT:
            self.warriors[1].shoot()
        elif decision == CLOSE_AIM:
            self.warriors[1].close_aim()
    
    def on_loop(self):
        self.warriors[0].update_aim()
        for warrior in self.warriors:
            warrior.move_bullets()
            warrior.dec_cooldown()
        collisions = detect_collision(*self.warriors)
        for warrior, bullet_index in collisions:
            end = warrior.handle_collision(bullet_index)
            if (end):
                print(f"Player {warrior.player} has won!")
                self.running = False
                break
            
        self.handle_ai()
        
    def on_render(self):
        self.reset_screen()
        
        for warrior in self.warriors:
            warrior.render(self.display)
        
        pygame.display.update()
        
    def on_cleanup(self):
        pygame.quit()
    
    def on_execute(self):
        self.on_init()
        
        while (self.running):
            time.sleep(0.01)
            for event in pygame.event.get():
                self.on_event(event)
            keys = pygame.key.get_pressed()
            self.handle_keys(keys)
            self.on_loop()
            self.on_render()
    
        self.on_cleanup()
    
        
if __name__ == "__main__":
    my_app = App()
    my_app.on_execute()
    
