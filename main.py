# main.py
import sys
from prettytable import PrettyTable
from auth import AuthManager
from recommendation_engine import RecommendationEngine
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "pryecto2"
password = "Estructuras1"

class RecomendadorTours:
    def __init__(self):
        # Configuración de conexión a Neo4j
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Módulos
        self.auth_manager = AuthManager(self.driver)
        self.recommendation_engine = RecommendationEngine(self.driver)
        
        # Preferencias del usuario
        self.preferencias = {
            'destinos': [],
            'transportes': [],
            'duracion_min': 0,
            'duracion_max': 0,
            'presupuesto_max': 0
        }
    
    def mostrar_menu(self, opciones, titulo):
        """Muestra un menú de selección"""
        print(f"\n=== {titulo} ===")
        for i, opcion in enumerate(opciones, 1):
            print(f"{i}. {opcion}")
        
        while True:
            selecciones = input("Seleccione números separados por comas: ").strip()
            try:
                indices = [int(s.strip()) - 1 for s in selecciones.split(",") if s.strip().isdigit()]
                if not indices:
                    raise ValueError
                return [opciones[i] for i in indices if 0 <= i < len(opciones)]
            except (ValueError, IndexError):
                print("¡Entrada inválida! Por favor ingrese números válidos separados por comas.")
    
    def recolectar_preferencias(self):
        """Recoge todas las preferencias del usuario"""
        print("\n=== Configuración de Preferencias ===")
        
        # Selección de destinos
        print("\nSeleccione sus destinos preferidos:")
        self.preferencias['destinos'] = self.mostrar_menu(self.recommendation_engine.destinos, "Destinos Disponibles")
        
        # Selección de transportes
        print("\nSeleccione sus transportes preferidos:")
        self.preferencias['transportes'] = self.mostrar_menu(self.recommendation_engine.transportes, "Transportes Disponibles")
        
        # Configuración de duración
        print("\nConfiguración de duración del tour:")
        self.preferencias['duracion_min'] = self.obtener_numero("Duración mínima (días): ")
        self.preferencias['duracion_max'] = self.obtener_numero("Duración máxima (días): ", min_val=self.preferencias['duracion_min'])
        
        # Configuración de presupuesto
        self.preferencias['presupuesto_max'] = self.obtener_numero("\nPresupuesto máximo: $", min_val=0)
    
    def obtener_numero(self, mensaje, min_val=0):
        """Obtiene un número válido del usuario"""
        while True:
            try:
                valor = float(input(mensaje))
                if valor >= min_val:
                    return valor
                print(f"El valor debe ser mayor o igual a {min_val}")
            except ValueError:
                print("Por favor ingrese un número válido.")
    
    def mostrar_recomendaciones(self, recomendaciones, personalizadas=False):
        """Muestra resultados en formato de tabla sin errores de alineación"""
        if not recomendaciones:
            msg = "\nNo se encontraron tours con los filtros aplicados." if not personalizadas else "\nNo hay recomendaciones basadas en tus preferencias."
            print(msg)
            return
        
        print("\n=== Resultados Recomendados ===" if not personalizadas else "\n=== Recomendaciones Personalizadas ===")
        
        tabla = PrettyTable()
        campos = ["#", "Tour", "Puntuación", "Duración (días)", "Precio", "Destinos", "Transporte"]
        tabla.field_names = campos
        
        # Configurar alineación correcta
        tabla.align["Precio"] = "r"
        tabla.align["Puntuación"] = "r" 
        tabla.align["Duración (días)"] = "r"
        tabla.align["Tour"] = "l"
        tabla.align["Destinos"] = "l"
        tabla.align["Transporte"] = "l"
        
        # Procesar tours eliminando duplicados
        tours_vistos = set()
        
        for i, tour in enumerate(recomendaciones, 1):
            nombre = tour.get("nombre") or tour.get("tour", "Desconocido")
            if nombre in tours_vistos:
                continue
                
            tours_vistos.add(nombre)
            
            duracion = int(tour.get("duracion", tour.get("t.duracion", 0)))
            precio = float(tour.get("precio", tour.get("t.precio", 0)))
            destinos = tour.get("destinos", tour.get("destinos_tour", []))
            
            tabla.add_row([
                i,
                nombre,
                tour.get("puntuacion", tour.get("puntuacion_total", 0)),
                duracion,
                f"${precio:,.2f}",
                ", ".join(destinos),
                tour.get("transporte", tour.get("transporte_tour", "N/A"))
            ])
        
        print(tabla)
        
        if self.auth_manager.usuario_actual and tours_vistos:
            self._procesar_seleccion_tour(sorted(tours_vistos))

    def _procesar_seleccion_tour(self, tours_lista):
        """Maneja la selección de tours con validación robusta"""
        while True:
            try:
                seleccion = input("\nIngresa el número del tour que deseas seleccionar (0 para omitir): ").strip()
                if seleccion == "0":
                    break
                    
                idx = int(seleccion) - 1
                if 0 <= idx < len(tours_lista):
                    tour_seleccionado = tours_lista[idx]
                    self.auth_manager.seleccionar_tour(tour_seleccionado)
                    print(f"\n¡Has seleccionado el tour '{tour_seleccionado}' exitosamente!")
                    break
                    
                print(f"Error: Ingresa un número entre 1 y {len(tours_lista)}")
                
            except ValueError:
                print("Error: Debes ingresar un número válido.")
            except Exception as e:
                print(f"Error inesperado: {str(e)}")
                break
    
    def menu_principal(self):
        """Muestra el menú principal con opciones de autenticación"""
        while True:
            print("\n=== Sistema de Recomendación de Tours ===")
            if self.auth_manager.usuario_actual:
                print(f"Usuario: {self.auth_manager.usuario_actual['nombre_real']}")
                print("1. Buscar tours con filtros personalizados")
                print("2. Ver mis recomendaciones inteligentes")
                print("3. Cerrar sesión")
                print("4. Salir")
            else:
                print("1. Iniciar sesión")
                print("2. Registrarse")
                print("3. Buscar tours (modo invitado)")
                print("4. Salir")
            
            opcion = input("Seleccione una opción: ").strip()
            
            if self.auth_manager.usuario_actual:
                if opcion == "1":
                    self.recolectar_preferencias()
                    recomendaciones = self.recommendation_engine.recomendar_tours(self.preferencias)
                    self.mostrar_recomendaciones(recomendaciones)
                elif opcion == "2":
                    recomendaciones = self.recommendation_engine.recomendar_por_preferencias_usuario(
                        self.auth_manager.usuario_actual["nombre"]
                    )
                    self.mostrar_recomendaciones(recomendaciones, personalizadas=True)
                elif opcion == "3":
                    self.auth_manager.cerrar_sesion()
                elif opcion == "4":
                    break
                else:
                    print("Opción no válida.")
            else:
                if opcion == "1":
                    self.auth_manager.iniciar_sesion()
                elif opcion == "2":
                    self.auth_manager.registrar_usuario()
                elif opcion == "3":
                    self.recolectar_preferencias()
                    recomendaciones = self.recommendation_engine.recomendar_tours(self.preferencias)
                    self.mostrar_recomendaciones(recomendaciones)
                elif opcion == "4":
                    break
                else:
                    print("Opción no válida.")
    
    def ejecutar(self):
        """Método principal"""
        try:
            self.menu_principal()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
        finally:
            self.driver.close()

if __name__ == "__main__":
    recomendador = RecomendadorTours()
    recomendador.ejecutar()