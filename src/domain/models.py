class Robot:
    def __init__(self, nombre: str, vida: int, ataque: int):
        self._nombre = nombre
        self._vida = vida
        self._ataque = ataque

    @property
    def nombre(self):
        return self._nombre

    @property
    def vida(self):
        return self._vida

    @vida.setter
    def vida(self, valor):
        self._vida = max(0, valor)

    @property
    def ataque(self):
        return self._ataque

    def esta_vivo(self):
        return self._vida > 0