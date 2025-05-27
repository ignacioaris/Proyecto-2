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
        
        if not nombre_usuario or not contrasena:
            print("Nombre de usuario y contraseña son obligatorios.")
            return False
        
        with self.driver.session() as session:
            # Verificar si el usuario ya existe
            resultado = session.run(
                "MATCH (u:Usuario {nombre: $nombre}) RETURN u",
                nombre=nombre_usuario
            )
            
            if resultado.single():
                print("El nombre de usuario ya existe.")
                return False
            
            # Crear nuevo usuario
            session.run(
                """CREATE (u:Usuario {
                    nombre: $nombre,
                    nombre_real: $nombre_real,
                    contrasena: $contrasena,
                    fecha_registro: datetime()
                })""",
                nombre=nombre_usuario,
                nombre_real=nombre_real,
                contrasena=contrasena
            )
            
            print("\n¡Registro exitoso! Ahora puedes iniciar sesión.")
            return True

