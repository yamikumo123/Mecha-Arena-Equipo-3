import pygame
import sys
import random

try:
    from src.domain.mecha import Mecha
    from src.services.combate_service import CombateService
except ImportError:
    class Mecha:
        def __init__(self, nombre, vida=100, ataque=25):
            self.nombre = nombre
            self.vida_max = vida
            self.vida_actual = vida
            self.ataque = ataque

        def recibir_daño(self, cantidad):
            self.vida_actual = max(0, self.vida_actual - cantidad)

class TextoFlotante:
    def __init__(self, texto, x, y, color):
        self.texto = texto
        self.x = x
        self.y = y
        self.color = color
        self.alpha = 255
        self.vida_util = 40

    def actualizar(self):
        self.y -= 1.5
        self.vida_util -= 1
        self.alpha = max(0, int((self.vida_util / 40) * 255))

class MenuGUI:
    def __init__(self):
        pygame.init()
        self.ancho = 800
        self.alto = 600
        self.pantalla = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("MECHA WARS - 2D ARENA")
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        self.estado = "MENU"

        # PALETA DE COLORES
        self.COLORES = {
            "AZUL": {"base": (20, 80, 160), "dark": (10, 45, 95), "light": (50, 130, 220), "glow": (0, 240, 255)},
            "ROJO": {"base": (170, 25, 35), "dark": (95, 10, 20), "light": (220, 50, 65), "glow": (255, 200, 0)},
            "NEGRO": {"base": (35, 35, 40), "dark": (15, 15, 20), "light": (70, 70, 80), "glow": (255, 50, 50)},
            "PLOMO": {"base": (110, 120, 135), "dark": (60, 65, 75), "light": (160, 175, 195), "glow": (0, 255, 200)},
            "VERDE MILITAR": {"base": (55, 80, 40), "dark": (28, 45, 20), "light": (90, 125, 65), "glow": (180, 255, 50)},
            "AMARILLO": {"base": (210, 170, 20), "dark": (120, 95, 10), "light": (250, 220, 60), "glow": (255, 255, 255)}
        }
        self.lista_colores = list(self.COLORES.keys())

        # Configuración de apariencia por jugador
        self.p1_color_idx = 0
        self.p2_color_idx = 1
        self.p1_tamano_idx = 1
        self.p2_tamano_idx = 1
        self.lista_tamanos = ["Pequeño", "Normal", "Grande"]

        # Arena
        self.arenas = ["CIUDAD", "RING DE PELEA", "TALLER"]
        self.arena_idx = 0

        # Fuentes
        self.f_ko = pygame.font.SysFont("Impact", 120)
        self.f_logo = pygame.font.SysFont("Impact", 64)
        self.f_sub = pygame.font.SysFont("Arial", 16, bold=True)
        self.f_btn = pygame.font.SysFont("Arial", 16, bold=True)
        self.f_log = pygame.font.SysFont("Arial", 13, bold=True)
        self.f_daño = pygame.font.SysFont("Impact", 36)

        # Configuración / Modalidades
        self.modo_pvp = True

        # Inputs
        self.input_p1_rect = pygame.Rect(115, 220, 230, 32)
        self.input_p2_rect = pygame.Rect(455, 220, 230, 32)
        self.active_input = None

        # Botones Menú
        self.btn_crear = pygame.Rect(275, 310, 250, 45)
        self.btn_batalla = pygame.Rect(275, 370, 250, 45)
        self.btn_modo = pygame.Rect(275, 430, 250, 45)
        self.btn_salir = pygame.Rect(275, 490, 250, 45)

        # Botones Configuración
        self.btn_p1_hp_up = pygame.Rect(115, 150, 35, 30)
        self.btn_p1_hp_down = pygame.Rect(155, 150, 35, 30)
        self.btn_p2_hp_up = pygame.Rect(455, 150, 35, 30)
        self.btn_p2_hp_down = pygame.Rect(495, 150, 35, 30)

        self.btn_p1_col_prev = pygame.Rect(115, 280, 30, 30)
        self.btn_p1_col_next = pygame.Rect(315, 280, 30, 30)
        self.btn_p2_col_prev = pygame.Rect(455, 280, 30, 30)
        self.btn_p2_col_next = pygame.Rect(655, 280, 30, 30)

        self.btn_p1_tamano = pygame.Rect(115, 345, 230, 32)
        self.btn_p2_tamano = pygame.Rect(455, 345, 230, 32)

        self.btn_arena_prev = pygame.Rect(260, 420, 35, 35)
        self.btn_arena_next = pygame.Rect(505, 420, 35, 35)

        self.btn_guardar_config = pygame.Rect(300, 500, 200, 45)

        # Botones Combate
        self.btn_atacar = pygame.Rect(140, 495, 230, 48)
        self.btn_defender = pygame.Rect(430, 495, 230, 48)
        self.btn_volver_menu = pygame.Rect(300, 555, 200, 32)

        # Mechas & Combate
        self.p1_mecha = Mecha("TITAN-BLUE", vida=130, ataque=25)
        self.p2_mecha = Mecha("WAR-CRIMSON", vida=110, ataque=30)
        self.p1_vida_vis = 130.0
        self.p2_vida_vis = 110.0
        self.turno_p1 = True
        self.p1_defendiendo = False
        self.p2_defendiendo = False
        self.hay_ko = False
        self.ganador = ""
        self.historial = ["¡SYSTEM ONLINE! Selecciona una acción."]

        # Efectos
        self.textos_flotantes = []
        self.screen_shake = 0
        self.p1_off_x = 0
        self.p2_off_x = 0

    def reiniciar_combate(self):
        self.p1_mecha.vida_actual = self.p1_mecha.vida_max
        self.p2_mecha.vida_actual = self.p2_mecha.vida_max
        self.p1_vida_vis = float(self.p1_mecha.vida_max)
        self.p2_vida_vis = float(self.p2_mecha.vida_max)
        self.turno_p1 = True
        self.p1_defendiendo = False
        self.p2_defendiendo = False
        self.hay_ko = False
        self.ganador = ""
        self.historial = [f"¡ARENA: {self.arenas[self.arena_idx]}! Presiona ESPACIO (Atacar) o E (Escudo)."]
        self.textos_flotantes.clear()

    def dibujar_boton(self, rect, texto, col_base, col_hover, pos_m):
        hover = rect.collidepoint(pos_m)
        col = col_hover if hover else col_base
        pygame.draw.rect(self.pantalla, (10, 15, 25), rect, border_radius=6)
        pygame.draw.rect(self.pantalla, col, rect, border_radius=6)
        
        borde_col = (0, 240, 255) if hover else (100, 120, 150)
        pygame.draw.rect(self.pantalla, borde_col, rect, 2, border_radius=6)

        txt = self.f_btn.render(texto, True, (255, 255, 255))
        self.pantalla.blit(txt, txt.get_rect(center=rect.center))

    def dibujar_escenario(self, sup):
        nombre_arena = self.arenas[self.arena_idx]

        if nombre_arena == "CIUDAD":
            # CIUDAD NOCTURNA SOBRIA Y ELEGANTE
            sup.fill((12, 16, 26))
            # Luna / Brillo tenue
            pygame.draw.circle(sup, (35, 45, 65), (680, 80), 45)
            # Capa lejana de edificios
            for x, w, h in [(20, 70, 220), (100, 90, 280), (280, 80, 200), (520, 100, 250), (630, 80, 210)]:
                pygame.draw.rect(sup, (18, 24, 38), (x, 380 - h, w, h))
            # Capa cercana de edificios
            for x, w, h in [(0, 80, 170), (180, 110, 230), (370, 95, 190), (480, 85, 210), (700, 100, 240)]:
                pygame.draw.rect(sup, (24, 32, 48), (x, 380 - h, w, h))
                # Luces minimalistas de ventanas
                for wx in range(x + 12, x + w - 15, 24):
                    for wy in range(380 - h + 20, 360, 45):
                        if (wx + wy) % 5 == 0:
                            pygame.draw.rect(sup, (180, 190, 140), (wx, wy, 8, 12))

            # Asfalto de la calle
            pygame.draw.rect(sup, (16, 18, 22), (0, 380, self.ancho, 220))
            # Líneas del carril
            for lx in range(20, self.ancho, 80):
                pygame.draw.line(sup, (50, 55, 65), (lx, 385), (lx + 40, 385), 2)

        elif nombre_arena == "RING DE PELEA":
            # RING DE BOXEO INDUSTRIAL SUTIL
            sup.fill((18, 18, 22))
            # Luz focal central degradada
            pygame.draw.polygon(sup, (28, 28, 36), [(200, 0), (600, 0), (750, 380), (50, 380)])
            
            # Postes esquineros del ring
            pygame.draw.rect(sup, (45, 50, 60), (30, 180, 18, 200))
            pygame.draw.rect(sup, (45, 50, 60), (752, 180, 18, 200))

            # Cuerdas tácticas
            for ry in [230, 280, 330]:
                pygame.draw.line(sup, (90, 35, 40), (30, ry), (770, ry), 3)

            # Lona del Ring
            pygame.draw.rect(sup, (28, 25, 28), (0, 380, self.ancho, 220))
            pygame.draw.line(sup, (180, 50, 50), (0, 380), (self.ancho, 380), 3)

        elif nombre_arena == "TALLER":
            # TALLER MECH MINIMALISTA
            sup.fill((15, 17, 20))
            # Estructura metálica de fondo (Vigas)
            for x in range(100, self.ancho, 200):
                pygame.draw.rect(sup, (25, 28, 35), (x, 0, 20, 380))
            pygame.draw.rect(sup, (30, 35, 45), (0, 80, self.ancho, 18))

            # Cables colgantes decorativos
            pygame.draw.arc(sup, (40, 45, 55), (100, 40, 300, 120), 3.14, 6.28, 2)
            pygame.draw.arc(sup, (40, 45, 55), (400, 40, 300, 100), 3.14, 6.28, 2)

            # Suelo de metal con remaches
            pygame.draw.rect(sup, (25, 27, 32), (0, 380, self.ancho, 220))
            pygame.draw.line(sup, (200, 150, 30), (0, 380), (self.ancho, 380), 3)
            for rx in range(15, self.ancho, 40):
                pygame.draw.circle(sup, (45, 50, 60), (rx, 390), 2)

    def dibujar_robot_2d_detallado(self, x, y, es_p1, dir_der=True, defendiendo=False):
        nombre_col = self.lista_colores[self.p1_color_idx if es_p1 else self.p2_color_idx]
        paleta = self.COLORES[nombre_col]
        tamano = self.lista_tamanos[self.p1_tamano_idx if es_p1 else self.p2_tamano_idx]

        c_base = paleta["base"]
        c_dark = paleta["dark"]
        c_light = paleta["light"]
        c_glow = paleta["glow"]
        c_gold = (230, 180, 40)

        # Escudo
        if defendiendo:
            pygame.draw.circle(self.pantalla, (0, 200, 255), (x + 50, y + 80), 95, 4)
            pygame.draw.circle(self.pantalla, (100, 230, 255), (x + 50, y + 80), 90, 2)

        # Sombra suave
        pygame.draw.ellipse(self.pantalla, (8, 10, 14), (x - 30, y + 170, 160, 20))

        if tamano == "Pequeño":
            pygame.draw.line(self.pantalla, c_dark, (x + 25, y + 100), (x + 15, y + 165), 10)
            pygame.draw.line(self.pantalla, c_dark, (x + 75, y + 100), (x + 85, y + 165), 10)
            pygame.draw.rect(self.pantalla, c_light, (x + 20, y + 120, 12, 30), border_radius=3)
            pygame.draw.rect(self.pantalla, c_light, (x + 68, y + 120, 12, 30), border_radius=3)
            pygame.draw.ellipse(self.pantalla, c_base, (x + 5, y + 160, 30, 14))
            pygame.draw.ellipse(self.pantalla, c_base, (x + 65, y + 160, 30, 14))

            pygame.draw.polygon(self.pantalla, c_dark, [(x + 20, y + 50), (x + 80, y + 50), (x + 65, y + 100), (x + 35, y + 100)])
            pygame.draw.polygon(self.pantalla, c_base, [(x + 25, y + 55), (x + 75, y + 55), (x + 60, y + 95), (x + 40, y + 95)])
            pygame.draw.circle(self.pantalla, c_glow, (x + 50, y + 75), 10)

            pygame.draw.polygon(self.pantalla, c_light, [(x + 5, y + 40), (x + 25, y + 50), (x + 15, y + 75)])
            pygame.draw.polygon(self.pantalla, c_light, [(x + 95, y + 40), (x + 75, y + 50), (x + 85, y + 75)])
            pygame.draw.line(self.pantalla, c_glow, (x + 10, y + 40), (x, y + 15), 3)
            pygame.draw.line(self.pantalla, c_glow, (x + 90, y + 40), (x + 100, y + 15), 3)

            pygame.draw.circle(self.pantalla, c_dark, (x + 50, y + 30), 20)
            pygame.draw.circle(self.pantalla, c_base, (x + 50, y + 30), 16)
            
            vx = x + 53 if dir_der else x + 35
            pygame.draw.ellipse(self.pantalla, c_glow, (vx, y + 25, 12, 8))

            cx = x + 75 if dir_der else x - 15
            pygame.draw.rect(self.pantalla, (80, 85, 95), (cx, y + 60, 30, 10), border_radius=2)

        elif tamano == "Normal":
            pygame.draw.rect(self.pantalla, c_dark, (x + 10, y + 90, 25, 80), border_radius=4)
            pygame.draw.rect(self.pantalla, c_dark, (x + 65, y + 90, 25, 80), border_radius=4)
            pygame.draw.rect(self.pantalla, c_base, (x + 5, y + 110, 32, 45), border_radius=5)
            pygame.draw.rect(self.pantalla, c_base, (x + 60, y + 110, 32, 45), border_radius=5)
            pygame.draw.rect(self.pantalla, c_gold, (x, y + 160, 40, 15), border_radius=3)
            pygame.draw.rect(self.pantalla, c_gold, (x + 58, y + 160, 40, 15), border_radius=3)

            pygame.draw.polygon(self.pantalla, c_dark, [(x + 10, y + 35), (x + 90, y + 35), (x + 75, y + 95), (x + 25, y + 95)])
            pygame.draw.polygon(self.pantalla, c_base, [(x + 18, y + 40), (x + 82, y + 40), (x + 70, y + 85), (x + 30, y + 85)])
            pygame.draw.polygon(self.pantalla, c_glow, [(x + 40, y + 50), (x + 60, y + 50), (x + 50, y + 70)])

            pygame.draw.polygon(self.pantalla, c_light, [(x - 20, y + 20), (x + 25, y + 10), (x + 20, y + 60), (x - 15, y + 55)])
            pygame.draw.polygon(self.pantalla, c_light, [(x + 75, y + 10), (x + 120, y + 20), (x + 115, y + 55), (x + 80, y + 60)])

            pygame.draw.rect(self.pantalla, c_dark, (x + 30, y - 5, 40, 35), border_radius=6)
            vx = x + 40 if dir_der else x + 25
            pygame.draw.rect(self.pantalla, c_glow, (vx, y + 8, 35, 10), border_radius=3)

            cx = x + 85 if dir_der else x - 25
            pygame.draw.rect(self.pantalla, (60, 65, 75), (cx, y + 15, 40, 16), border_radius=3)

        else:
            pygame.draw.rect(self.pantalla, c_dark, (x - 5, y + 80, 40, 90), border_radius=6)
            pygame.draw.rect(self.pantalla, c_dark, (x + 65, y + 80, 40, 90), border_radius=6)
            pygame.draw.rect(self.pantalla, c_base, (x - 10, y + 100, 45, 55), border_radius=6)
            pygame.draw.rect(self.pantalla, c_base, (x + 65, y + 100, 45, 55), border_radius=6)
            pygame.draw.rect(self.pantalla, c_gold, (x - 15, y + 155, 52, 22), border_radius=4)
            pygame.draw.rect(self.pantalla, c_gold, (x + 63, y + 155, 52, 22), border_radius=4)

            pygame.draw.polygon(self.pantalla, c_dark, [(x - 15, y + 20), (x + 115, y + 20), (x + 90, y + 90), (x + 10, y + 90)])
            pygame.draw.polygon(self.pantalla, c_base, [(x - 8, y + 25), (x + 108, y + 25), (x + 85, y + 85), (x + 15, y + 85)])
            pygame.draw.rect(self.pantalla, c_glow, (x + 35, y + 45, 30, 25), border_radius=4)

            pygame.draw.rect(self.pantalla, c_light, (x - 40, y + 10, 40, 45), border_radius=6)
            pygame.draw.rect(self.pantalla, c_light, (x + 100, y + 10, 40, 45), border_radius=6)

            pygame.draw.rect(self.pantalla, c_dark, (x + 25, y - 15, 50, 35), border_radius=6)
            vx = x + 38 if dir_der else x + 22
            pygame.draw.rect(self.pantalla, c_glow, (vx, y - 5, 40, 12), border_radius=3)

            cx = x + 95 if dir_der else x - 45
            pygame.draw.rect(self.pantalla, (50, 55, 65), (cx, y + 30, 50, 22), border_radius=4)
            pygame.draw.rect(self.pantalla, c_gold, (cx + (35 if dir_der else 0), y + 28, 15, 26), border_radius=3)

    def turn_bot(self):
        if self.hay_ko or self.turno_p1:
            return
        
        if random.random() < 0.7:
            self.ejecutar_ataque()
        else:
            self.ejecutar_defensa()

    def ejecutar_ataque(self):
        if self.hay_ko:
            return

        self.screen_shake = 12

        if self.turno_p1:
            atq, defn = self.p1_mecha, self.p2_mecha
            px = 580
            self.p1_off_x = 35
            es_def = self.p2_defendiendo
            self.p2_defendiendo = False
        else:
            atq, defn = self.p2_mecha, self.p1_mecha
            px = 180
            self.p2_off_x = -35
            es_def = self.p1_defendiendo
            self.p1_defendiendo = False

        daño = atq.ataque // 2 if es_def else atq.ataque
        defn.recibir_daño(daño)

        txt_d = f"-{daño} (DEF)" if es_def else f"-{daño}"
        self.textos_flotantes.append(TextoFlotante(txt_d, px, 180, (255, 50, 50)))
        
        msg_def = " (Mitigado por Escudo)" if es_def else ""
        self.historial.append(f"{atq.nombre} ataca causando {daño} HP{msg_def}!")

        if defn.vida_actual <= 0:
            self.hay_ko = True
            self.ganador = atq.nombre
            self.historial.append(f"¡K.O.! {atq.nombre} DESTRUYE A SU RIVAL!")
        else:
            self.turno_p1 = not self.turno_p1
            if not self.modo_pvp and not self.turno_p1:
                pygame.time.set_timer(pygame.USEREVENT + 1, 600)

    def ejecutar_defensa(self):
        if self.hay_ko:
            return

        if self.turno_p1:
            self.p1_defendiendo = True
            self.historial.append(f"{self.p1_mecha.nombre} ACTIVA ESCUDO TÁCTICO.")
        else:
            self.p2_defendiendo = True
            self.historial.append(f"{self.p2_mecha.nombre} ACTIVA ESCUDO TÁCTICO.")

        self.turno_p1 = not self.turno_p1
        if not self.modo_pvp and not self.turno_p1:
            pygame.time.set_timer(pygame.USEREVENT + 1, 600)

    def render_menu(self, pos_m):
        self.pantalla.fill((8, 10, 18))
        for x in range(0, self.ancho, 50):
            pygame.draw.line(self.pantalla, (15, 22, 35), (x, 0), (x, self.alto))
        for y in range(0, self.alto, 50):
            pygame.draw.line(self.pantalla, (15, 22, 35), (0, y), (self.ancho, y))

        self.dibujar_robot_2d_detallado(90, 140, es_p1=True, dir_der=True)
        self.dibujar_robot_2d_detallado(610, 140, es_p1=False, dir_der=False)

        txt_t = self.f_logo.render("MECHA WARS", True, (0, 210, 255))
        self.pantalla.blit(txt_t, txt_t.get_rect(center=(self.ancho // 2, 60)))

        sub = self.f_sub.render("ARENA COMBAT SIMULATOR 2D", True, (200, 210, 230))
        self.pantalla.blit(sub, sub.get_rect(center=(self.ancho // 2, 115)))

        pygame.draw.line(self.pantalla, (0, 210, 255), (200, 135), (600, 135), 2)

        str_modo = "MODO: 2 JUGADORES (LOCAL)" if self.modo_pvp else "MODO: vs IA (BOT)"
        self.dibujar_boton(self.btn_crear, "CONFIGURAR MECHAS", (25, 70, 130), (40, 100, 180), pos_m)
        self.dibujar_boton(self.btn_batalla, "INICIAR BATALLA", (20, 120, 55), (35, 160, 75), pos_m)
        self.dibujar_boton(self.btn_modo, str_modo, (100, 50, 150), (140, 70, 200), pos_m)
        self.dibujar_boton(self.btn_salir, "SALIR DEL JUEGO", (130, 25, 25), (170, 40, 40), pos_m)

    def render_config(self, pos_m):
        self.pantalla.fill((12, 16, 26))

        t = self.f_logo.render("CONFIGURACIÓN", True, (0, 220, 255))
        self.pantalla.blit(t, t.get_rect(center=(self.ancho // 2, 40)))

        # Panel P1
        pygame.draw.rect(self.pantalla, (20, 30, 50), (95, 90, 270, 300), border_radius=8)
        p1_lbl = self.f_btn.render("JUGADOR 1 (IZQ):", True, (0, 200, 255))
        self.pantalla.blit(p1_lbl, (115, 105))

        hp1 = self.f_log.render(f"VIDA MAX: {self.p1_mecha.vida_max}", True, (255, 255, 255))
        self.pantalla.blit(hp1, (205, 158))

        lbl_nom1 = self.f_log.render("Nombre del Mecha:", True, (180, 200, 220))
        self.pantalla.blit(lbl_nom1, (115, 197))

        col_in1 = (0, 240, 255) if self.active_input == "p1" else (80, 90, 110)
        pygame.draw.rect(self.pantalla, (5, 10, 20), self.input_p1_rect, border_radius=4)
        pygame.draw.rect(self.pantalla, col_in1, self.input_p1_rect, 2, border_radius=4)
        txt_p1 = self.f_btn.render(self.p1_mecha.nombre, True, (255, 255, 255))
        self.pantalla.blit(txt_p1, (self.input_p1_rect.x + 8, self.input_p1_rect.y + 4))

        # P1 - Selector Color
        lbl_col1 = self.f_log.render("Color del Mecha:", True, (180, 200, 220))
        self.pantalla.blit(lbl_col1, (115, 258))
        nom_c1 = self.lista_colores[self.p1_color_idx]
        txt_c1 = self.f_btn.render(nom_c1, True, self.COLORES[nom_c1]["light"])
        self.pantalla.blit(txt_c1, txt_c1.get_rect(center=(230, 295)))

        # P1 - Selector Tamaño
        lbl_tam1 = self.f_log.render("Modelo / Tamaño:", True, (180, 200, 220))
        self.pantalla.blit(lbl_tam1, (115, 322))

        # Panel P2 / IA
        pygame.draw.rect(self.pantalla, (50, 20, 30), (435, 90, 270, 300), border_radius=8)
        lbl_p2_str = "JUGADOR 2 (DER):" if self.modo_pvp else "RIVAL IA (DER):"
        p2_lbl = self.f_btn.render(lbl_p2_str, True, (255, 60, 60))
        self.pantalla.blit(p2_lbl, (455, 105))

        hp2 = self.f_log.render(f"VIDA MAX: {self.p2_mecha.vida_max}", True, (255, 255, 255))
        self.pantalla.blit(hp2, (545, 158))

        lbl_nom2 = self.f_log.render("Nombre del Mecha:", True, (220, 180, 180))
        self.pantalla.blit(lbl_nom2, (455, 197))

        col_in2 = (255, 60, 60) if self.active_input == "p2" else (110, 80, 90)
        pygame.draw.rect(self.pantalla, (20, 5, 10), self.input_p2_rect, border_radius=4)
        pygame.draw.rect(self.pantalla, col_in2, self.input_p2_rect, 2, border_radius=4)
        txt_p2 = self.f_btn.render(self.p2_mecha.nombre, True, (255, 255, 255))
        self.pantalla.blit(txt_p2, (self.input_p2_rect.x + 8, self.input_p2_rect.y + 4))

        # P2 - Selector Color
        lbl_col2 = self.f_log.render("Color del Mecha:", True, (220, 180, 180))
        self.pantalla.blit(lbl_col2, (455, 258))
        nom_c2 = self.lista_colores[self.p2_color_idx]
        txt_c2 = self.f_btn.render(nom_c2, True, self.COLORES[nom_c2]["light"])
        self.pantalla.blit(txt_c2, txt_c2.get_rect(center=(570, 295)))

        # P2 - Selector Tamaño
        lbl_tam2 = self.f_log.render("Modelo / Tamaño:", True, (220, 180, 180))
        self.pantalla.blit(lbl_tam2, (455, 322))

        # PANEL SELECCIÓN DE ARENA
        pygame.draw.rect(self.pantalla, (25, 35, 45), (240, 400, 320, 75), border_radius=8)
        pygame.draw.rect(self.pantalla, (0, 200, 255), (240, 400, 320, 75), 2, border_radius=8)
        lbl_ar = self.f_log.render("ARENA DE COMBATE:", True, (0, 240, 255))
        self.pantalla.blit(lbl_ar, lbl_ar.get_rect(center=(400, 412)))
        txt_ar = self.f_btn.render(self.arenas[self.arena_idx], True, (255, 215, 0))
        self.pantalla.blit(txt_ar, txt_ar.get_rect(center=(400, 437)))

        # Renderizado de Botones
        self.dibujar_boton(self.btn_p1_hp_up, "+", (30, 90, 150), (50, 120, 190), pos_m)
        self.dibujar_boton(self.btn_p1_hp_down, "-", (30, 90, 150), (50, 120, 190), pos_m)
        self.dibujar_boton(self.btn_p2_hp_up, "+", (150, 30, 50), (190, 50, 70), pos_m)
        self.dibujar_boton(self.btn_p2_hp_down, "-", (150, 30, 50), (190, 50, 70), pos_m)

        self.dibujar_boton(self.btn_p1_col_prev, "<", (30, 90, 150), (50, 120, 190), pos_m)
        self.dibujar_boton(self.btn_p1_col_next, ">", (30, 90, 150), (50, 120, 190), pos_m)
        self.dibujar_boton(self.btn_p2_col_prev, "<", (150, 30, 50), (190, 50, 70), pos_m)
        self.dibujar_boton(self.btn_p2_col_next, ">", (150, 30, 50), (190, 50, 70), pos_m)

        tam1_str = self.lista_tamanos[self.p1_tamano_idx].upper()
        tam2_str = self.lista_tamanos[self.p2_tamano_idx].upper()
        self.dibujar_boton(self.btn_p1_tamano, f"MODELO: {tam1_str}", (30, 90, 150), (50, 120, 190), pos_m)
        self.dibujar_boton(self.btn_p2_tamano, f"MODELO: {tam2_str}", (150, 30, 50), (190, 50, 70), pos_m)

        self.dibujar_boton(self.btn_arena_prev, "<", (40, 60, 80), (60, 90, 120), pos_m)
        self.dibujar_boton(self.btn_arena_next, ">", (40, 60, 80), (60, 90, 120), pos_m)

        self.dibujar_boton(self.btn_guardar_config, "GUARDAR Y VOLVER", (20, 120, 55), (35, 160, 75), pos_m)

    def render_combate(self, pos_m):
        sx = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        sy = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        if self.screen_shake > 0:
            self.screen_shake -= 1

        self.p1_off_x = max(0, self.p1_off_x - 3)
        self.p2_off_x = min(0, self.p2_off_x + 3)

        self.p1_vida_vis += (self.p1_mecha.vida_actual - self.p1_vida_vis) * 0.1
        self.p2_vida_vis += (self.p2_mecha.vida_actual - self.p2_vida_vis) * 0.1

        sup = pygame.Surface((self.ancho, self.alto))
        self.dibujar_escenario(sup)

        # Barras HP
        pygame.draw.rect(sup, (40, 10, 10), (40, 35, 300, 22), border_radius=4)
        w1 = max(0, int((self.p1_vida_vis / self.p1_mecha.vida_max) * 300))
        pygame.draw.rect(sup, (0, 200, 255), (40, 35, w1, 22), border_radius=4)
        txt1 = self.f_log.render(f"{self.p1_mecha.nombre} [{int(self.p1_vida_vis)} HP]", True, (255, 255, 255))
        sup.blit(txt1, (40, 12))

        pygame.draw.rect(sup, (40, 10, 10), (460, 35, 300, 22), border_radius=4)
        w2 = max(0, int((self.p2_vida_vis / self.p2_mecha.vida_max) * 300))
        pygame.draw.rect(sup, (255, 40, 50), (460 + (300 - w2), 35, w2, 22), border_radius=4)
        txt2 = self.f_log.render(f"[{int(self.p2_vida_vis)} HP] {self.p2_mecha.nombre}", True, (255, 255, 255))
        sup.blit(txt2, (590, 12))

        # Indicador de Turno
        turno_txt = f"TURNO: {self.p1_mecha.nombre}" if self.turno_p1 else f"TURNO: {self.p2_mecha.nombre}"
        col_t = (0, 240, 255) if self.turno_p1 else (255, 70, 70)
        lbl_t = self.f_btn.render(turno_txt, True, col_t)
        sup.blit(lbl_t, lbl_t.get_rect(center=(self.ancho // 2, 25)))

        for tf in self.textos_flotantes[:]:
            tf.actualizar()
            if tf.vida_util <= 0:
                self.textos_flotantes.remove(tf)
            else:
                td = self.f_daño.render(tf.texto, True, tf.color)
                td.set_alpha(tf.alpha)
                sup.blit(td, (tf.x, tf.y))

        # Console Log
        pygame.draw.rect(sup, (5, 8, 12), (100, 395, 600, 85), border_radius=6)
        pygame.draw.rect(sup, (0, 210, 255), (100, 395, 600, 85), 2, border_radius=6)
        yl = 402
        for msg in self.historial[-3:]:
            tl = self.f_log.render(f"> {msg}", True, (0, 255, 180))
            sup.blit(tl, (115, yl))
            yl += 24

        self.pantalla.blit(sup, (sx, sy))

        self.dibujar_robot_2d_detallado(130 + self.p1_off_x, 180, es_p1=True, dir_der=True, defendiendo=self.p1_defendiendo)
        self.dibujar_robot_2d_detallado(570 + self.p2_off_x, 180, es_p1=False, dir_der=False, defendiendo=self.p2_defendiendo)

        # Cartel K.O.
        if self.hay_ko:
            overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.pantalla.blit(overlay, (0, 0))

            ko_txt = self.f_ko.render("¡K. O.!", True, (255, 30, 30))
            sub_ko = self.f_logo.render(f"VICTORIA: {self.ganador}", True, (255, 215, 0))

            self.pantalla.blit(ko_txt, ko_txt.get_rect(center=(self.ancho // 2, 220)))
            self.pantalla.blit(sub_ko, sub_ko.get_rect(center=(self.ancho // 2, 330)))

        # Botones
        self.dibujar_boton(self.btn_atacar, "[ESPACIO] ATAQUE", (170, 20, 20), (220, 45, 45), pos_m)
        self.dibujar_boton(self.btn_defender, "[E] ESCUDO", (20, 80, 170), (45, 115, 220), pos_m)
        self.dibujar_boton(self.btn_volver_menu, "Volver al Menú", (55, 60, 70), (85, 90, 100), pos_m)

    def iniciar(self):
        while self.corriendo:
            pos_m = pygame.mouse.get_pos()

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.corriendo = False

                elif ev.type == pygame.USEREVENT + 1:
                    pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                    self.turn_bot()

                elif ev.type == pygame.KEYDOWN:
                    if self.estado == "CONFIG":
                        if self.active_input == "p1":
                            if ev.key == pygame.K_BACKSPACE:
                                self.p1_mecha.nombre = self.p1_mecha.nombre[:-1]
                            elif len(self.p1_mecha.nombre) < 12 and ev.unicode.isprintable():
                                self.p1_mecha.nombre += ev.unicode.upper()

                        elif self.active_input == "p2":
                            if ev.key == pygame.K_BACKSPACE:
                                self.p2_mecha.nombre = self.p2_mecha.nombre[:-1]
                            elif len(self.p2_mecha.nombre) < 12 and ev.unicode.isprintable():
                                self.p2_mecha.nombre += ev.unicode.upper()

                    elif self.estado == "COMBATE" and not self.hay_ko:
                        # ATAQUE CON ESPACIO / ESCUDO CON LA TECLA E
                        if self.modo_pvp or self.turno_p1:
                            if ev.key == pygame.K_SPACE:
                                self.ejecutar_ataque()
                            elif ev.key == pygame.K_e:
                                self.ejecutar_defensa()

                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if self.estado == "MENU":
                        if self.btn_crear.collidepoint(ev.pos):
                            self.estado = "CONFIG"
                        elif self.btn_batalla.collidepoint(ev.pos):
                            self.reiniciar_combate()
                            self.estado = "COMBATE"
                        elif self.btn_modo.collidepoint(ev.pos):
                            self.modo_pvp = not self.modo_pvp
                            if not self.modo_pvp and self.p2_mecha.nombre == "WAR-CRIMSON":
                                self.p2_mecha.nombre = "BOT-IA"
                        elif self.btn_salir.collidepoint(ev.pos):
                            self.corriendo = False

                    elif self.estado == "CONFIG":
                        if self.input_p1_rect.collidepoint(ev.pos):
                            self.active_input = "p1"
                        elif self.input_p2_rect.collidepoint(ev.pos):
                            self.active_input = "p2"
                        else:
                            self.active_input = None

                        if self.btn_p1_hp_up.collidepoint(ev.pos):
                            self.p1_mecha.vida_max += 10
                        elif self.btn_p1_hp_down.collidepoint(ev.pos):
                            self.p1_mecha.vida_max = max(50, self.p1_mecha.vida_max - 10)
                        elif self.btn_p2_hp_up.collidepoint(ev.pos):
                            self.p2_mecha.vida_max += 10
                        elif self.btn_p2_hp_down.collidepoint(ev.pos):
                            self.p2_mecha.vida_max = max(50, self.p2_mecha.vida_max - 10)

                        elif self.btn_p1_col_prev.collidepoint(ev.pos):
                            self.p1_color_idx = (self.p1_color_idx - 1) % len(self.lista_colores)
                        elif self.btn_p1_col_next.collidepoint(ev.pos):
                            self.p1_color_idx = (self.p1_color_idx + 1) % len(self.lista_colores)
                        elif self.btn_p2_col_prev.collidepoint(ev.pos):
                            self.p2_color_idx = (self.p2_color_idx - 1) % len(self.lista_colores)
                        elif self.btn_p2_col_next.collidepoint(ev.pos):
                            self.p2_color_idx = (self.p2_color_idx + 1) % len(self.lista_colores)

                        elif self.btn_p1_tamano.collidepoint(ev.pos):
                            self.p1_tamano_idx = (self.p1_tamano_idx + 1) % len(self.lista_tamanos)
                        elif self.btn_p2_tamano.collidepoint(ev.pos):
                            self.p2_tamano_idx = (self.p2_tamano_idx + 1) % len(self.lista_tamanos)

                        elif self.btn_arena_prev.collidepoint(ev.pos):
                            self.arena_idx = (self.arena_idx - 1) % len(self.arenas)
                        elif self.btn_arena_next.collidepoint(ev.pos):
                            self.arena_idx = (self.arena_idx + 1) % len(self.arenas)

                        elif self.btn_guardar_config.collidepoint(ev.pos):
                            self.active_input = None
                            self.estado = "MENU"

                    elif self.estado == "COMBATE":
                        if not self.hay_ko:
                            if self.modo_pvp or self.turno_p1:
                                if self.btn_atacar.collidepoint(ev.pos):
                                    self.ejecutar_ataque()
                                elif self.btn_defender.collidepoint(ev.pos):
                                    self.ejecutar_defensa()

                        if self.btn_volver_menu.collidepoint(ev.pos):
                            self.estado = "MENU"

            if self.estado == "MENU":
                self.render_menu(pos_m)
            elif self.estado == "CONFIG":
                self.render_config(pos_m)
            elif self.estado == "COMBATE":
                self.render_combate(pos_m)

            pygame.display.flip()
            self.reloj.tick(60)

        pygame.quit()
        sys.exit()