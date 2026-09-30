class CombateService:

    def atacar(self, atacante, defensor):
        if atacante.vida <= 0:
            raise ValueError("El atacante ya está derrotado.")

        if defensor.vida <= 0:
            raise ValueError("El defensor ya está derrotado.")

        danio = atacante.ataque
        defensor.vida -= danio

        if defensor.vida < 0:
            defensor.vida = 0

        return danio

    def esta_derrotado(self, mecha):
        return mecha.vida <= 0

    def obtener_ganador(self, mecha1, mecha2):
        if self.esta_derrotado(mecha1):
            return mecha2.nombre

        if self.esta_derrotado(mecha2):
            return mecha1.nombre

        return None