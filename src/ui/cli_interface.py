from src.services.app_service import AppService

# Clases mock simples para ejecutar la prueba fluida con la estructura de tus compañeros
class MechaMock:
    def __init__(self, nombre, vida, ataque):
        self.nombre = nombre
        self.vida = vida
        self.ataque = ataque

    def esta_vivo(self):
        return self.vida > 0

class PilotoMock:
    def __init__(self, nombre, mecha=None):
        self.nombre = nombre
        self.mecha = mecha

class MenuCLI:
    def __init__(self):
        self.app_service = AppService()

    def iniciar(self):
        print("=== MECHA ARENA SIMULATOR ===")
        
        # Crear Mechas y Pilotos de prueba
        m1 = MechaMock("Gundam RX-78", 100, 25)
        m2 = MechaMock("Zaku II", 80, 15)
        
        p1 = PilotoMock("Amuro Ray", m1)
        p2 = PilotoMock("Char Aznable", m2)
        
        print(f"Piloto 1: {p1.nombre} a bordo de {m1.nombre} (Vida: {m1.vida})")
        print(f"Piloto 2: {p2.nombre} a bordo de {m2.nombre} (Vida: {m2.vida})\n")
        
        # Ejecutar la simulación completa
        historial = self.app_service.simular_combate_completo(p1, p2)
        
        # Mostrar los turnos de la pelea en consola
        for linea in historial:
            print(linea)