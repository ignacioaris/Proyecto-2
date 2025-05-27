from neo4j import GraphDatabase
import getpass

uri = "bolt://localhost:7687"
user = "pryecto2"
password = "Estructuras1"

class AuthManager:
    def __init__(self, driver):
        self.driver = driver
        self.usuario_actual = None
    
    def registrar_usuario(self):
        """Registra un nuevo usuario en el sistema"""
        print("\n=== Registro de Usuario ===")
        nombre_usuario = input("Nombre de usuario: ").strip()
        nombre_real = input("Nombre real: ").strip()
        contrasena = getpass.getpass("Contraseña: ")
