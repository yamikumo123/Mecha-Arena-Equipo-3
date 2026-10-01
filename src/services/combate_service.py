class CombateService:

    def atacar(self, atacante, defensor):
        if not atacante.esta_vivo():
            raise ValueError("El atacante ya está derrotado.")

        if not defensor.esta_vivo():
            raise ValueError("El defensor ya está derrotado.")

        danio = defensor.recibir_danio(atacante.ataque)

        return danio

    def esta_derrotado(self, mecha):
        return not mecha.esta_vivo()

    def obtener_ganador(self, mecha1, mecha2):
        if self.esta_derrotado(mecha1):
            return mecha2.nombre

        if self.esta_derrotado(mecha2):
            return mecha1.nombre

        return None