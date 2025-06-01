# auth.py
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
    
    def iniciar_sesion(self):
        """Inicia sesión con un usuario existente"""
        print("\n=== Inicio de Sesión ===")
        nombre_usuario = input("Nombre de usuario: ").strip()
        contrasena = getpass.getpass("Contraseña: ")
        
        with self.driver.session() as session:
            resultado = session.run(
                "MATCH (u:Usuario {nombre: $nombre, contrasena: $contrasena}) RETURN u",
                nombre=nombre_usuario,
                contrasena=contrasena
            )
            
            usuario = resultado.single()
            
            if usuario:
                self.usuario_actual = usuario["u"]
                print(f"\nBienvenido, {self.usuario_actual['nombre_real']}!")
                return True
            else:
                print("\nUsuario o contraseña incorrectos.")
                return False
    
    def cerrar_sesion(self):
        """Cierra la sesión del usuario actual"""
        self.usuario_actual = None
        print("Sesión cerrada correctamente.")
    
    def seleccionar_tour(self, tour_nombre):
        """Crea relación PREFIRIO entre usuario y tour seleccionado"""
        if not self.usuario_actual:
            print("Debes iniciar sesión para seleccionar un tour.")
            return False
        
        with self.driver.session() as session:
            # Crear relación con el tour
            session.run(
                """MATCH (u:Usuario {nombre: $usuario_nombre}), 
                         (t:Tour {nombre: $tour_nombre})
                   MERGE (u)-[r:PREFIRIO]->(t)
                   SET r.fecha = datetime()""",
                usuario_nombre=self.usuario_actual["nombre"],
                tour_nombre=tour_nombre
            )
            
            # Crear relaciones con destinos y transporte del tour
            session.run(
                """MATCH (u:Usuario {nombre: $usuario_nombre}), 
                         (t:Tour {nombre: $tour_nombre})-[:VISITA]->(d:Destino)
                   MERGE (u)-[:PREFIRIO]->(d)""",
                usuario_nombre=self.usuario_actual["nombre"],
                tour_nombre=tour_nombre
            )
            
            session.run(
                """MATCH (u:Usuario {nombre: $usuario_nombre}), 
                         (t:Tour {nombre: $tour_nombre})-[:VIAJA_EN]->(trans:Transporte)
                   MERGE (u)-[:PREFIRIO]->(trans)""",
                usuario_nombre=self.usuario_actual["nombre"],
                tour_nombre=tour_nombre
            )
            
            print(f"\n¡Has seleccionado el tour {tour_nombre}! Se han registrado tus preferencias.")
            return True