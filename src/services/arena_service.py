"""Reglas de la arena, independientes de la ventana y del teclado."""
from dataclasses import dataclass
from src.domain.models import Robot

WIDTH, FLOOR = 1200, 580
MOVES = {
    'light': (8, 88, .24, .08),
    'heavy': (15, 112, .46, .16),
    'finisher': (24, 138, .58, .14),
    'special': (26, 0, .65, .18),
}

@dataclass
class Attack:
    kind: str
    elapsed: float = 0
    resolved: bool = False

@dataclass
class Projectile:
    owner: int
    x: float
    y: float
    direction: int
    life: float = 1.8

class Fighter:
    def __init__(self, index, x):
        self.index = index
        self.robot = Robot(('AZURE / J1', 'EMBER / J2')[index], 100, 8)
        self.x, self.y, self.vy = x, float(FLOOR), 0.0
        self.facing = 1 if index == 0 else -1
        self.energy = 35.0
        self.attack = None
        self.guard = False
        self.stun = self.cooldown = self.combo_time = 0.0
        self.sequence = []
        self.hits = 0
        self.hit_time = 0.0
        self.walking = False

    @property
    def alive(self):
        return self.robot.esta_vivo()

class Arena:
    def __init__(self):
        self.scores = [0, 0]
        self.reset()

    def reset(self):
        self.fighters = [Fighter(0, 320), Fighter(1, 880)]
        self.projectiles = []
        self.events = []
        self.remaining = 90.0
        self.winner = None
        self.finished = False

    def jump(self, index):
        f = self.fighters[index]
        if not self.finished and f.alive and f.y >= FLOOR and f.stun <= 0 and not f.attack:
            f.vy = -590

    def strike(self, index, kind):
        f = self.fighters[index]
        if self.finished or not f.alive or f.attack or f.stun > 0 or f.cooldown > 0:
            return False
        if kind not in ('light', 'heavy', 'special'):
            return False
        if kind == 'special':
            if f.energy < 60:
                self.events.append(('notice', index, 'NECESITAS 60 DE ENERGÍA'))
                return False
            f.energy -= 60
            f.sequence.clear()
        else:
            if f.combo_time <= 0:
                f.sequence.clear()
            f.sequence.append(kind)
            f.sequence = f.sequence[-3:]
            f.combo_time = 1.15
            if f.sequence == ['light', 'light', 'heavy']:
                kind = 'finisher'
                f.sequence.clear()
        f.guard = False
        f.attack = Attack(kind)
        return True

    def _damage(self, owner, target, amount, direction, kind):
        f, enemy = self.fighters[owner], self.fighters[target]
        blocked = enemy.guard and enemy.facing == -direction
        if blocked:
            amount = max(1, round(amount * .25))
            enemy.energy = min(100, enemy.energy + 5)
        else:
            enemy.stun = .18 if kind != 'finisher' else .3
            enemy.x = max(65, min(WIDTH - 65, enemy.x + direction * (18 if kind == 'light' else 38)))
            f.hits = f.hits + 1 if f.hit_time > 0 else 1
            f.hit_time = 1.3
        enemy.robot.vida -= amount
        f.energy = min(100, f.energy + (6 if blocked else 12))
        self.events.append(('hit', target, amount, blocked, kind))

    def step(self, dt, controls):
        if self.finished:
            return
        dt = min(.033, max(0, dt))
        self.remaining = max(0, self.remaining - dt)
        for i, f in enumerate(self.fighters):
            enemy = self.fighters[1 - i]
            f.facing = 1 if enemy.x >= f.x else -1
            f.stun = max(0, f.stun - dt)
            f.cooldown = max(0, f.cooldown - dt)
            f.combo_time = max(0, f.combo_time - dt)
            f.hit_time = max(0, f.hit_time - dt)
            f.energy = min(100, f.energy + dt * 3)
            c = controls[i]
            f.guard = bool(c.get('guard')) and not f.attack and f.stun <= 0 and f.y >= FLOOR
            movement = int(bool(c.get('right'))) - int(bool(c.get('left')))
            f.walking = movement != 0 and not f.attack and not f.guard and f.stun <= 0
            if f.walking:
                f.x = max(65, min(WIDTH - 65, f.x + movement * 245 * dt))
            f.vy += 1450 * dt
            f.y = min(FLOOR, f.y + f.vy * dt)
            if f.y >= FLOOR:
                f.vy = 0
        # Evita que los cuerpos se atraviesen mientras están a la misma altura.
        a, b = self.fighters
        if abs(a.y - b.y) < 90 and abs(a.x - b.x) < 82:
            direction = 1 if b.x >= a.x else -1
            middle = max(106, min(WIDTH - 106, (a.x + b.x) / 2))
            a.x, b.x = middle - direction * 41, middle + direction * 41
        pending = []
        for i, f in enumerate(self.fighters):
            if not f.attack:
                continue
            atk = f.attack
            damage, reach, duration, active = MOVES[atk.kind]
            atk.elapsed += dt
            if not atk.resolved and atk.elapsed >= active:
                atk.resolved = True
                if atk.kind == 'special':
                    self.projectiles.append(Projectile(i, f.x + f.facing * 65, f.y - 77, f.facing))
                    self.events.append(('shot', i))
                else:
                    enemy = self.fighters[1 - i]
                    if abs(f.x - enemy.x) <= reach and abs(f.y - enemy.y) < 80 and (enemy.x - f.x) * f.facing > 0:
                        pending.append((i, 1 - i, damage, f.facing, atk.kind))
            if atk.elapsed >= duration:
                f.attack = None
                f.cooldown = .06
        # Resuelve ambos ataques del cuadro antes de comprobar el ganador.
        for args in pending:
            self._damage(*args)
        for p in self.projectiles[:]:
            previous = p.x
            p.x += p.direction * 640 * dt
            p.life -= dt
            target = self.fighters[1 - p.owner]
            if min(previous, p.x) - 36 <= target.x <= max(previous, p.x) + 36 and target.y - 125 <= p.y <= target.y:
                self._damage(p.owner, 1 - p.owner, 26, p.direction, 'special')
                self.projectiles.remove(p)
            elif p.life <= 0 or not -50 <= p.x <= WIDTH + 50:
                self.projectiles.remove(p)
        if not a.alive or not b.alive or self.remaining <= 0:
            self.finished = True
            if a.robot.vida == b.robot.vida:
                self.winner = -1
            else:
                self.winner = 0 if a.robot.vida > b.robot.vida else 1
                self.scores[self.winner] += 1
            self.events.append(('finish', self.winner))
