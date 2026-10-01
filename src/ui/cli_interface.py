from src.domain.models import Robot
from src.services.app_service import BatallaService

class MenuCLI:
    def iniciar(self):
        print("=== MECHA ARENA SIMULATOR ===")
        r1 = Robot("Gundam", 100, 25)
        r2 = Robot("Zaku", 80, 15)
        
        print(f"Robot 1: {r1.nombre} (Vida: {r1.vida})")
        print(f"Robot 2: {r2.nombre} (Vida: {r2.vida})")
        
        resultado = BatallaService.simular_combate(r1, r2)
        print(resultado)