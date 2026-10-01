from src.services.combate_service import CombateService  # o la ruta exacta donde esté CombateService

class AppService:
    def __init__(self, data_manager=None):
        self.combate_service = CombateService()
        self.data_manager = data_manager

    def preparar_combate(self, piloto1, piloto2):
        """Valida que ambos pilotos tengan mecha asignado antes de iniciar."""
        if not piloto1.mecha or not piloto2.mecha:
            raise ValueError("Ambos pilotos deben tener un Mecha asignado para combatir.")
        return True

    def simular_combate_completo(self, piloto1, piloto2):
        """Ejecuta una pelea automática por turnos hasta que haya un ganador."""
        self.preparar_combate(piloto1, piloto2)
        
        mecha1 = piloto1.mecha
        mecha2 = piloto2.mecha
        
        historial = [
            f"=== INICIO DEL COMBATE: {piloto1.nombre} ({mecha1.nombre}) VS {piloto2.nombre} ({mecha2.nombre}) ==="
        ]
        
        turno = 1
        
        while mecha1.esta_vivo() and mecha2.esta_vivo():
            # Turno Piloto 1 / Mecha 1
            danio1 = self.combate_service.atacar(mecha1, mecha2)
            historial.append(
                f"Turno {turno} - {piloto1.nombre}: {mecha1.nombre} inflige {danio1} de daño a {mecha2.nombre}. "
                f"(Vida {mecha2.nombre}: {mecha2.vida})"
            )
            
            if self.combate_service.esta_derrotado(mecha2):
                break

            # Turno Piloto 2 / Mecha 2
            danio2 = self.combate_service.atacar(mecha2, mecha1)
            historial.append(
                f"Turno {turno} - {piloto2.nombre}: {mecha2.nombre} inflige {danio2} de daño a {mecha1.nombre}. "
                f"(Vida {mecha1.nombre}: {mecha1.vida})"
            )
            
            turno += 1

        ganador_nombre = self.combate_service.obtener_ganador(mecha1, mecha2)
        historial.append(f"🏆 ¡EL GANADOR ES {ganador_nombre}! 🏆")

        # Guardar resultado usando data_manager si está disponible
        if self.data_manager and hasattr(self.data_manager, "guardar_resultado"):
            self.data_manager.guardar_resultado({
                "ganador": ganador_nombre,
                "turnos": turno,
                "historial": historial
            })

        return historial