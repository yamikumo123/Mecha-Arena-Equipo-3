import json
import os

class DataManager:
    """
    Clase encargada de la persistencia de datos (guardar y cargar archivos JSON).
    """

    def __init__(self, folder_path="data"):
        self.folder_path = folder_path
        # Asegura que la carpeta para guardar datos (ej. 'data/') exista
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

    def guardar_json(self, nombre_archivo: str, datos) -> bool:
        """
        Guarda una lista o diccionario en un archivo JSON.
        :param nombre_archivo: Nombre del archivo (ej. 'mechas.json')
        :param datos: Lista o diccionario con la información a guardar
        """
        file_path = os.path.join(self.folder_path, nombre_archivo)
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(datos, file, indent=4, ensure_ascii=False)
            print(f"[DataManager] Datos guardados con éxito en '{file_path}'.")
            return True
        except Exception as e:
            print(f"[DataManager] Error al guardar datos: {e}")
            return False

    def cargar_json(self, nombre_archivo: str):
        """
        Carga y retorna los datos de un archivo JSON.
        :param nombre_archivo: Nombre del archivo a leer (ej. 'mechas.json')
        :return: Datos cargados en formato Python (lista/dict) o None si falla.
        """
        file_path = os.path.join(self.folder_path, nombre_archivo)
        if not os.path.exists(file_path):
            print(f"[DataManager] El archivo '{file_path}' no existe aún. Retornando lista vacía.")
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                datos = json.load(file)
                print(f"[DataManager] Datos cargados correctamente desde '{file_path}'.")
                return datos
        except Exception as e:
            print(f"[DataManager] Error al cargar los datos: {e}")
            return []


            # --- Prueba local rápida ---
if __name__ == "__main__":
    manager = DataManager()
    
    # 1. Crear un mecha de prueba
    mecha_demo = [
        {
            "nombre": "Mecha Titan X",
            "vida": 120,
            "ataque": 50,
            "armas": ["Cañón Plasma", "Escudo Pesado"]
        }
    ]
    
    # 2. Guardar prueba
    manager.guardar_json("mechas_test.json", mecha_demo)
    
    # 3. Cargar prueba
    datos_recuperados = manager.cargar_json("mechas_test.json")
    print("Datos leídos del JSON:", datos_recuperados)