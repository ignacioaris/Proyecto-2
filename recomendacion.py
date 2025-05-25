import sys
from neo4j import GraphDatabase
from prettytable import PrettyTable

uri = "bolt://localhost:7687"
user = "pryecto2"
password = "Estructuras1"

class RecomendadorTours:
    def __init__(self):
        # Configuración de conexión a Neo4j
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Preferencias del usuario
        self.preferencias = {
            'destinos': [],
            'transportes': [],
            'duracion_min': 0,
            'duracion_max': 0,
            'presupuesto_max': 0
        }
    
    def obtener_opciones(self):
        """Obtiene destinos y transportes disponibles desde Neo4j"""
        with self.driver.session() as session:
            # Obtener todos los destinos
            resultados = session.run("MATCH (d:Destino) RETURN d.nombre as nombre ORDER BY d.nombre")
            self.destinos = [registro["nombre"] for registro in resultados]
            
            # Obtener todos los transportes
            resultados = session.run("MATCH (t:Transporte) RETURN t.nombre as nombre ORDER BY t.nombre")
            self.transportes = [registro["nombre"] for registro in resultados]
    
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
        self.preferencias['destinos'] = self.mostrar_menu(self.destinos, "Destinos Disponibles")
        
        # Selección de transportes
        print("\nSeleccione sus transportes preferidos:")
        self.preferencias['transportes'] = self.mostrar_menu(self.transportes, "Transportes Disponibles")
        
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
    
    def recomendar_tours(self):
        """Ejecuta el algoritmo de recomendación actualizado"""
        with self.driver.session() as session:
            query = """
            MATCH (t:Tour)-[:VISITA]->(d:Destino),
                  (t)-[:VIAJA_EN]->(trans:Transporte)
            WITH t, trans.nombre AS transporte_tour, 
                 collect(DISTINCT d.nombre) AS destinos_tour
            // Calcular puntos para destinos (2 puntos por cada destino preferido)
            WITH t, transporte_tour, destinos_tour,
                 size([d IN destinos_tour WHERE d IN $destinos]) * 2 AS puntos_destinos,
                 // 1 punto si el transporte es preferido
                 CASE WHEN transporte_tour IN $transportes THEN 1 ELSE 0 END AS puntos_transporte
            // Calcular puntuación total
            WITH t, transporte_tour, destinos_tour,
                 puntos_destinos + puntos_transporte AS puntuacion_total
            WHERE t.duracion >= $duracion_min AND 
                  t.duracion <= $duracion_max AND 
                  t.precio <= $presupuesto_max
            RETURN DISTINCT t.nombre AS tour, puntuacion_total, t.duracion, t.precio, 
                   destinos_tour, transporte_tour
            ORDER BY puntuacion_total DESC, size(destinos_tour) DESC
            LIMIT 10
            """
            
            resultados = session.run(query, 
                                   destinos=self.preferencias['destinos'],
                                   transportes=self.preferencias['transportes'],
                                   duracion_min=self.preferencias['duracion_min'],
                                   duracion_max=self.preferencias['duracion_max'],
                                   presupuesto_max=self.preferencias['presupuesto_max'])
            
            return list(resultados)
    
    def mostrar_recomendaciones(self, recomendaciones):
        """Muestra los resultados al usuario"""
        if not recomendaciones:
            print("\nNo se encontraron tours que coincidan con tus criterios.")
            return
        
        print("\n=== Resultados Recomendados ===")
        tabla = PrettyTable()
        tabla.field_names = ["Tour", "Puntuación", "Duración (días)", "Precio", "Destinos", "Transporte"]
        tabla.align["Precio"] = "r"
        
        # Usamos un conjunto para evitar tours duplicados
        tours_mostrados = set()
        
        for tour in recomendaciones:
            nombre_tour = tour["tour"]
            if nombre_tour not in tours_mostrados:
                tours_mostrados.add(nombre_tour)
                tabla.add_row([
                    nombre_tour,
                    tour["puntuacion_total"],
                    int(tour["t.duracion"]),
                    f"${tour['t.precio']:,.2f}",
                    ", ".join(tour["destinos_tour"]),
                    tour["transporte_tour"]
                ])
        
        print(tabla)
    
    def ejecutar(self):
        """Método principal"""
        try:
            print("\n=== Sistema de Recomendación de Tours ===")
            self.obtener_opciones()
            self.recolectar_preferencias()
            recomendaciones = self.recomendar_tours()
            self.mostrar_recomendaciones(recomendaciones)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
        finally:
            self.driver.close()

if __name__ == "__main__":
    recomendador = RecomendadorTours()
    recomendador.ejecutar()