from src.domain.models import Mecha
from src.services.app_service import AppService as BatallaService

class MenuCLI:
    def iniciar(self):
        print("=== MECHA ARENA SIMULATOR ===")
        r1 = Mecha("Gundam", 100, 25, 10)
        r2 = Mecha("Zaku", 80, 15, 20)
        
        print(f"Robot 1: {r1.nombre} (Vida: {r1.vida})")
        print(f"Robot 2: {r2.nombre} (Vida: {r2.vida})")
        
        resultado = BatallaService.simular_combate(r1, r2)
        print(resultado)