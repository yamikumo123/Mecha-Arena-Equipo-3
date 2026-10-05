class CombateService:

    def atacar(self, atacante, defensor):
        if not atacante.esta_vivo():
            raise ValueError("El atacante ya está derrotado.")

        if not defensor.esta_vivo():
            raise ValueError("El defensor ya está derrotado.")

        danio = atacante.ataque
        defensor.vida = defensor.vida - danio

        return danio

    def esta_derrotado(self, robot):
        return not robot.esta_vivo()

    def obtener_ganador(self, robot1, robot2):
        if self.esta_derrotado(robot1):
            return robot2.nombre

        if self.esta_derrotado(robot2):
            return robot1.nombre

        return None