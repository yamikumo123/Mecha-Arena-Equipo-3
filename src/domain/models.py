class Mecha:
    def __init__(self, nombre, vida, ataque, defensa):
        self.nombre = nombre
        self.vida = vida
        self.ataque = ataque
        self.defensa = defensa

    def esta_vivo(self):
        return self.vida > 0

    def recibir_danio(self, cantidad):
        danio_real = cantidad - self.defensa

        if danio_real < 0:
            danio_real = 0

        self.vida -= danio_real

        if self.vida < 0:
            self.vida = 0

        return danio_real


class Piloto:
    def __init__(self, nombre):
        self.nombre = nombre
        self.mecha = None

    def asignar_mecha(self, mecha):
        self.mecha = mecha