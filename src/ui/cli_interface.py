import time
from src.services.app_service import AppService

class MechaJugador:
    def __init__(self, nombre, vida, ataque):
        self.nombre = nombre
        self.vida = vida
        self.vida_maxima = vida
        self.ataque = ataque
        self.defendiendo = False

    def recibir_danio(self, cantidad):
        if self.defendiendo:
            cantidad = cantidad // 2  # Reduce el daño a la mitad si se defiende
            print(f"🛡️ ¡{self.nombre} se defendió y redujo el daño a {cantidad}!")
            self.defendiendo = False
        self.vida = max(0, self.vida - cantidad)
        return cantidad

    def esta_vivo(self):
        return self.vida > 0

class PilotoJugador:
    def __init__(self, nombre, mecha=None):
        self.nombre = nombre
        self.mecha = mecha

class MenuCLI:
    def __init__(self):
        self.app_service = AppService()

    def iniciar(self):
        print("=" * 45)
        print("      🤖 MECHA ARENA SIMULATOR - MULTIJUGADOR 🤖")
        print("=" * 45)
        
        # --- REGISTRO DE JUGADORES Y MECHAS ---
        print("\n--- CONFIGURACIÓN DEL JUGADOR 1 ---")
        nombre_p1 = input("Ingrese el nombre del Piloto 1: ").strip() or "Jugador 1"
        nombre_m1 = input("Ingrese el nombre de su Mecha: ").strip() or "Mecha-01"
        
        print("\n--- CONFIGURACIÓN DEL JUGADOR 2 ---")
        nombre_p2 = input("Ingrese el nombre del Piloto 2: ").strip() or "Jugador 2"
        nombre_m2 = input("Ingrese el nombre de su Mecha: ").strip() or "Mecha-02"

        # Instanciar Mechas (Vida: 100, Ataque: 20)
        m1 = MechaJugador(nombre_m1, 100, 20)
        m2 = MechaJugador(nombre_m2, 100, 20)
        
        p1 = PilotoJugador(nombre_p1, m1)
        p2 = PilotoJugador(nombre_p2, m2)

        print("\n" + "=" * 45)
        print(f"⚔️ ¡COMIENZA EL COMBATE: {p1.nombre} vs {p2.nombre}! ⚔️")
        print("=" * 45)

        turno = 1
        # --- BUCLE PRINCIPAL DEL JUEGO POR TURNOS ---
        while m1.esta_vivo() and m2.esta_vivo():
            print(f"\n--- TURNO {turno} ---")
            print(f"💚 {p1.nombre} ({m1.nombre}): {m1.vida}/100 HP | 💚 {p2.nombre} ({m2.nombre}): {m2.vida}/100 HP")
            
            # --- TURNO JUGADOR 1 ---
            self.ejecutar_turno(p1, p2)
            if not m2.esta_vivo():
                print(f"\n💥 ¡El Mecha de {p2.nombre} ha sido destruido!")
                print(f"🏆 ¡FELICITACIONES {p1.nombre}, HAS GANADO LA BATALLA! 🏆")
                break

            # --- TURNO JUGADOR 2 ---
            self.ejecutar_turno(p2, p1)
            if not m1.esta_vivo():
                print(f"\n💥 ¡El Mecha de {p1.nombre} ha sido destruido!")
                print(f"🏆 ¡FELICITACIONES {p2.nombre}, HAS GANADO LA BATALLA! 🏆")
                break

            turno += 1

    def ejecutar_turno(self, atacante_piloto, defensor_piloto):
        m_atacante = atacante_piloto.mecha
        m_defensor = defensor_piloto.mecha

        print(f"\n▶️ Turno de {atacante_piloto.nombre} ({m_atacante.nombre}):")
        print(" 1. Atacar ⚔️")
        print(" 2. Defender 🛡️ (Reduce el daño recibido en el siguiente turno)")
        
        opcion = ""
        while opcion not in ["1", "2"]:
            opcion = input("Elige tu acción (1 o 2): ").strip()

        if opcion == "1":
            danio = m_defensor.recibir_danio(m_atacante.ataque)
            print(f"💥 ¡{m_atacante.nombre} atacó a {m_defensor.nombre} e infligió {danio} de daño!")
        elif opcion == "2":
            m_atacante.defendiendo = True
            print(f"🛡️ {m_atacante.nombre} se pone en posición defensiva.")

        time.sleep(1)