"""Ventana Tkinter y gráficos vectoriales: no necesita imágenes ni paquetes."""
import math
import random
import time
import tkinter as tk
from src.services.arena_service import Arena, WIDTH, FLOOR, MOVES

HEIGHT = 740
CYAN, ORANGE = '#36dcff', '#ff9850'

class ArenaApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('MECHA ARENA · Equipo 3 · Duelo local')
        self.root.geometry('1200x740')
        self.root.minsize(900, 555)
        self.canvas = tk.Canvas(self.root, bg='#080e1c', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.arena = Arena()
        self.keys = set()
        self.mode = 'menu'
        self.fx = []
        self.shake = 0
        self.clock = time.perf_counter()
        self.anim = 0
        self.notice = ['', '']
        self.notice_time = [0, 0]
        self.random = random.Random(31)
        self.buildings = [(x, self.random.randint(140, 320), self.random.randint(35, 72)) for x in range(0, 1200, 65)]
        self.root.bind('<KeyPress>', self.key_down)
        self.root.bind('<KeyRelease>', self.key_up)
        self.root.bind('<FocusOut>', self.focus_lost)
        self.root.protocol('WM_DELETE_WINDOW', self.root.destroy)
        self.canvas.bind('<Button-1>', lambda event: self.start() if self.mode == 'menu' else None)
        self.root.after(16, self.tick)

    def start(self):
        self.keys.clear()
        self.arena.reset()
        self.fx.clear()
        self.notice = ['', '']
        self.notice_time = [0, 0]
        self.mode = 'playing'
        self.canvas.focus_set()

    def normalize(self, event):
        # Ñ en español; ; o : como alternativa en teclados ingleses.
        if event.char.lower() == 'ñ' or event.keysym.lower() in ('ntilde', 'semicolon', 'colon'):
            return 'ñ'
        return event.keysym.lower()

    def key_down(self, event):
        key = self.normalize(event)
        if key in self.keys:
            return
        self.keys.add(key)
        if key == 'escape':
            if self.mode in ('playing', 'paused'):
                self.mode = 'paused' if self.mode == 'playing' else 'playing'
                self.keys.clear()
            elif self.mode == 'result':
                self.mode = 'menu'
            return
        if key == 'return' and self.mode in ('menu', 'result'):
            self.start()
        elif key == 'r' and self.mode == 'result':
            self.start()
        elif self.mode == 'playing':
            if key in ('w', 'o'):
                self.arena.jump(0 if key == 'w' else 1)
            attacks = {'f': (0, 'light'), 'g': (0, 'heavy'), 'h': (0, 'special'),
                       'i': (1, 'light'), 'u': (1, 'heavy'), 'p': (1, 'special')}
            if key in attacks:
                self.arena.strike(*attacks[key])

    def key_up(self, event):
        self.keys.discard(self.normalize(event))

    def focus_lost(self, event):
        self.keys.clear()
        if self.mode == 'playing':
            self.mode = 'paused'

    def rect(self, x1, y1, x2, y2, fill, outline='', width=1):
        return self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=width)

    def text(self, x, y, value, size=14, color='#dbe9f8', anchor='center', bold=False):
        return self.canvas.create_text(x, y, text=value, fill=color, anchor=anchor,
                                       font=('Segoe UI', size, 'bold' if bold else 'normal'))

    def background(self):
        self.rect(0, 0, WIDTH, HEIGHT, '#080e1c')
        for y in range(160, FLOOR, 30):
            self.canvas.create_line(0, y, WIDTH, y, fill='#111c30')
        self.canvas.create_oval(820, 160, 1020, 360, fill='#142a43', outline='#214a66', width=2)
        self.canvas.create_oval(845, 185, 995, 335, outline='#28526a')
        for x, height, width in self.buildings:
            self.rect(x, FLOOR - height, x + width, FLOOR, '#0b1626', '#1b2a40')
            for wy in range(FLOOR - height + 15, FLOOR - 15, 28):
                self.rect(x + 10, wy, x + 14, wy + 7, '#245472')
                self.rect(x + 26, wy, x + 30, wy + 7, '#18384c')
        self.rect(0, FLOOR, WIDTH, 662, '#101c2c')
        self.canvas.create_line(0, FLOOR, WIDTH, FLOOR, fill='#4b96a9', width=3)
        self.canvas.create_line(0, FLOOR + 6, WIDTH, FLOOR + 6, fill='#203746')
        for x in range(-400, 1600, 100):
            self.canvas.create_line(x, 662, 600 + (x - 600) * .55, FLOOR, fill='#24394e')
        for y in (605, 635, 660):
            self.canvas.create_line(0, y, WIDTH, y, fill='#22374b')
        self.text(36, 168, 'SECTOR 03 / NEON DOCK', 10, '#526e85', 'w')
        self.text(1164, 168, 'LOCAL VERSUS · 2 PILOTOS', 10, '#526e85', 'e')

    def robot(self, f):
        color = (CYAN, ORANGE)[f.index]
        dark = ('#16394e', '#4b2a27')[f.index]
        x, y = f.x, f.y
        direction = f.facing
        bob = math.sin(self.anim * 17) * 3 if f.walking else math.sin(self.anim * 3) * 1.2
        attack = f.attack
        punch = 0
        if attack:
            duration = MOVES[attack.kind][2]
            punch = math.sin(min(1, attack.elapsed / duration) * math.pi) * (72 if attack.kind != 'light' else 52)
        self.canvas.create_oval(x - 52, FLOOR - 7, x + 52, FLOOR + 10, fill='#07101c', outline='')
        def box(a, b, c, d, fill, edge='#506777', width=2):
            left, right = sorted((x + a * direction, x + c * direction))
            self.rect(left, y + b + bob, right, y + d + bob, fill, edge, width)
        # Piernas con articulaciones y placas de armadura.
        stride = math.sin(self.anim * 17) * 9 if f.walking else 0
        box(-30, -54, -9, -13 + stride, '#243647')
        box(9, -54, 30, -13 - stride, '#243647')
        box(-35, -19 + stride, -5, -2, dark, color)
        box(5, -19 - stride, 39, -2, dark, color)
        box(-31, -49, -9, -39, dark, color)
        box(10, -49, 31, -39, dark, color)
        box(-27, -69, 27, -48, '#283747')
        box(-39, -115, 38, -67, dark, color)
        box(-28, -106, 27, -83, '#1c2a3b')
        self.canvas.create_oval(x - 11, y - 104 + bob, x + 11, y - 82 + bob, fill=color, outline='#ecfaff', width=2)
        box(-21, -144, 23, -114, '#273a4c', color)
        box(-13, -134, 20, -127, color, color)
        box(-11, -122, 14, -117, '#070e1a', '#070e1a')
        # Brazo trasero y brazo de ataque.
        box(-51, -109, -33, -73, '#344759')
        box(-55, -79, -32, -58, dark, color)
        arm_y = -109 if not f.guard else -126
        box(34, arm_y, 54 + punch, arm_y + 20, '#344759')
        box(47 + punch, arm_y - 4, 72 + punch, arm_y + 25, dark, color)
        if f.guard:
            self.canvas.create_arc(x - 74, y - 166, x + 74, y - 15,
                                   start=270 if direction == 1 else 90, extent=180, style='arc', outline=color, width=5)
            self.text(x, y - 178, 'GUARDIA', 10, color)
        if attack and attack.kind != 'special':
            reach = MOVES[attack.kind][1]
            end = x + direction * reach
            self.canvas.create_line(x + direction * 48, y - 91, end, y - 91, fill=color, width=4)
            if attack.kind == 'finisher':
                self.canvas.create_arc(x - 145, y - 185, x + 145, y + 10, start=300 if direction == 1 else 120,
                                       extent=120, style='arc', outline='#fff1a8', width=5)
                self.text(x, y - 200, 'ROMPEARMADURA', 12, '#fff1a8', bold=True)
        if f.y < FLOOR:
            for n in range(3):
                self.canvas.create_line(x - 19 + n * 18, y + 4, x - 19 + n * 18, y + 25 + n * 5, fill=color, width=3)
        if f.hit_time > 0 and f.hits >= 2:
            self.text(x, y - 185, f'{f.hits} HITS', 18, color, bold=True)

    def hud(self):
        self.text(34, 30, 'MECHA / ARENA', 17, '#e5f4ff', 'w', True)
        self.text(1166, 30, 'EQUIPO 3', 11, '#658198', 'e', True)
        for i, f in enumerate(self.arena.fighters):
            color = (CYAN, ORANGE)[i]
            x = 36 if i == 0 else 760
            self.text(x, 64, f.robot.nombre, 15, color, 'w', True)
            self.text(x + 400, 64, f'{f.robot.vida} HP', 12, '#e1eaf4', 'e')
            self.rect(x, 82, x + 404, 105, '#152335', '#304358')
            if f.robot.vida:
                self.rect(x + 3, 85, x + 3 + 398 * f.robot.vida / 100, 102, color)
            self.rect(x, 115, x + 240, 123, '#1d293b')
            if f.energy > 0:
                self.rect(x, 115, x + 240 * f.energy / 100, 123, '#dbe7ff' if f.energy >= 60 else '#547d9c')
            self.text(x + 250, 119, f'ENERGÍA {int(f.energy)} / 100', 9, '#7294ab', 'w')
            if self.notice_time[i] > 0:
                self.text(x, 142, self.notice[i], 10, color, 'w')
        self.text(600, 75, f'{math.ceil(self.arena.remaining):02}', 35, '#f2f7ff', bold=True)
        self.text(600, 119, f'{self.arena.scores[0]}  /  {self.arena.scores[1]}', 13, '#7692ad')
        self.rect(0, 667, WIDTH, HEIGHT, '#0b1221', '#1e3046')
        self.text(28, 686, 'J1  A / D mover · W saltar · S bloquear', 12, CYAN, 'w')
        self.text(28, 714, 'F puño · G fuerte · H plasma     COMBO: F → F → G', 11, '#9eb6ce', 'w')
        self.text(648, 686, 'J2  K / Ñ mover · O saltar · L bloquear', 12, ORANGE, 'w')
        self.text(648, 714, 'I puño · U fuerte · P plasma     COMBO: I → I → U', 11, '#9eb6ce', 'w')

    def overlay(self, title, subtitle, action):
        self.rect(240, 206, 960, 503, '#0b1424', '#39536e', 2)
        self.rect(240, 206, 247, 503, CYAN)
        self.text(600, 242, 'MECHA ARENA / LOCAL VERSUS', 11, '#6f9bb4', bold=True)
        self.text(600, 302, title, 34, '#e9f5ff', bold=True)
        self.text(600, 362, subtitle, 14, '#a9bed3')
        self.rect(386, 414, 814, 463, '#143344', CYAN)
        self.text(600, 438, action, 14, CYAN, bold=True)

    def events(self):
        for e in self.arena.events:
            if e[0] == 'hit':
                _, index, amount, blocked, kind = e
                f = self.arena.fighters[index]
                color = '#d9f4ff' if blocked else (CYAN, ORANGE)[1 - index]
                for _ in range(14 if blocked else 26):
                    self.fx.append([f.x, f.y - 90, self.random.uniform(-230, 230), self.random.uniform(-270, 130), .5, color, 'spark'])
                self.fx.append([f.x, f.y - 158, 0, -70, .8, color, f'BLOQUEO -{amount}' if blocked else f'-{amount}'])
                self.shake = 3 if blocked else (9 if kind in ('special', 'finisher') else 5)
            elif e[0] == 'notice':
                self.notice[e[1]], self.notice_time[e[1]] = e[2], 1.5
            elif e[0] == 'shot':
                self.notice[e[1]], self.notice_time[e[1]] = '¡CAÑÓN DE PLASMA!', 1
        self.arena.events.clear()

    def tick(self):
        now = time.perf_counter()
        dt = min(.033, now - self.clock)
        self.clock = now
        self.anim += dt
        if self.mode == 'playing':
            controls = [{'left': 'a' in self.keys, 'right': 'd' in self.keys, 'guard': 's' in self.keys},
                        {'left': 'k' in self.keys, 'right': 'ñ' in self.keys, 'guard': 'l' in self.keys}]
            self.arena.step(dt, controls)
            self.events()
            if self.arena.finished:
                self.mode = 'result'
                self.keys.clear()
        if self.mode != 'paused':
            for p in self.fx[:]:
                p[0] += p[2] * dt
                p[1] += p[3] * dt
                p[4] -= dt
                if p[6] == 'spark':
                    p[3] += 550 * dt
                if p[4] <= 0:
                    self.fx.remove(p)
            for i in range(2):
                self.notice_time[i] = max(0, self.notice_time[i] - dt)
        self.canvas.delete('all')
        self.background()
        for f in self.arena.fighters:
            self.robot(f)
        for p in self.arena.projectiles:
            color = (CYAN, ORANGE)[p.owner]
            self.canvas.create_line(p.x - p.direction * 75, p.y, p.x, p.y, fill=color, width=12)
            self.canvas.create_oval(p.x - 21, p.y - 17, p.x + 21, p.y + 17, fill=color, outline='#ffffff', width=2)
            self.canvas.create_oval(p.x - 9, p.y - 9, p.x + 9, p.y + 9, fill='#ffffff', outline='')
        for x, y, vx, vy, life, color, kind in self.fx:
            if kind == 'spark':
                self.canvas.create_line(x, y, x - vx * .035, y - vy * .035, fill=color, width=2)
            else:
                self.text(x, y, kind, 18, color, bold=True)
        if self.shake > .3 and self.mode != 'paused':
            self.canvas.move('all', self.random.uniform(-self.shake, self.shake), self.random.uniform(-self.shake, self.shake))
            self.shake *= .83
        self.hud()
        if self.mode == 'menu':
            self.overlay('DOS PILOTOS. UNA ARENA.', 'Duelo en el mismo teclado · 90 segundos · Vida y energía\nEncadena dos puños y un golpe fuerte para romper la armadura.', 'ENTER O CLIC PARA COMENZAR')
        elif self.mode == 'paused':
            self.overlay('PAUSA', 'La pelea se pausa al cambiar de ventana.\nVuelve a la arena y presiona Escape.', 'ESC PARA CONTINUAR')
        elif self.mode == 'result':
            winner = self.arena.winner
            title = 'EMPATE' if winner == -1 else f'VICTORIA DEL JUGADOR {winner + 1}'
            self.overlay(title, 'Revancha con vida y energía restauradas.\nEl marcador conserva las victorias de esta sesión.', 'ENTER / R: REVANCHA   ·   ESC: MENÚ')
        scale = min(max(1, self.canvas.winfo_width()) / WIDTH, max(1, self.canvas.winfo_height()) / HEIGHT)
        self.canvas.scale('all', 0, 0, scale, scale)
        # Escala también las fuentes al redimensionar.
        if abs(scale - 1) > .02:
            for item in self.canvas.find_all():
                if self.canvas.type(item) == 'text':
                    font = self.canvas.itemcget(item, 'font')
                    parts = self.root.tk.splitlist(font)
                    self.canvas.itemconfigure(item, font=(parts[0], max(7, round(int(parts[1]) * scale)), *parts[2:]))
        self.root.after(16, self.tick)

    def run(self):
        self.root.mainloop()
