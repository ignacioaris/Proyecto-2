from neo4j import GraphDatabase

# Función de autenticación
def authenticate(username, password, driver):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:Usuario {nombre: $username, contrasena: $password})
            RETURN u
            """,
            username=username,
            password=password
        )
        return result.single() is not None

class RecommendationEngine:
    def __init__(self, driver):
        self.driver = driver

    def get_available_destinations(self):
        with self.driver.session() as session:
            rs = session.run(
                "MATCH (d:Destino) RETURN d.nombre AS nombre ORDER BY d.nombre"
            )
            return [r['nombre'] for r in rs]

    def get_available_transports(self):
        with self.driver.session() as session:
            rs = session.run(
                "MATCH (t:Transporte) RETURN t.nombre AS nombre ORDER BY t.nombre"
            )
            return [r['nombre'] for r in rs]

    def recomendar_tours(self, prefs):
        destinos = prefs.get('destinos', [])
        transports = prefs.get('transports', [])
        max_price  = prefs.get('max_price', 1e9)
        min_dur    = prefs.get('min_duration', 0)
        max_dur    = prefs.get('max_duration', 1e9)
        with self.driver.session() as session:
            rs = session.run(
                """
                MATCH (tour:Tour)-[:VIAJA_EN]->(trans:Transporte)
                WHERE trans.nombre IN $transports
                  AND tour.precio <= $max_price
                  AND tour.duracion >= $min_dur   AND tour.duracion <= $max_dur
                  AND EXISTS {
                      MATCH (tour)-[:VISITA]->(d0:Destino)
                      WHERE d0.nombre IN $destinos
                  }
                WITH tour
                MATCH (tour)-[:VISITA]->(d:Destino)
                WITH tour, collect(DISTINCT d.nombre) AS details,
                     tour.precio AS price, tour.duracion AS duration
                RETURN tour.nombre AS name,
                       price,
                       duration,
                       details
                ORDER BY price ASC
                LIMIT 20
                """,
                destinos=destinos,
                transports=transports,
                max_price=max_price,
                min_dur=min_dur,
                max_dur=max_dur
            )
            return [
                {
                    'name': r['name'],
                    'price': r['price'],
                    'duration': r['duration'],
                    'details': r['details']
                }
                for r in rs
            ]

    def get_user_preferences(self, username):
        with self.driver.session() as session:
            rs1 = session.run(
                "MATCH (u:Usuario {nombre: $username})-[:PREFIRIO]->(d:Destino) RETURN d.nombre AS nombre",
                username=username
            )
            destinos = [r['nombre'] for r in rs1]
            rs2 = session.run(
                "MATCH (u:Usuario {nombre: $username})-[:PREFIRIO]->(t:Transporte) RETURN t.nombre AS nombre",
                username=username
            )
            transports = [r['nombre'] for r in rs2]
            return {'destinos': destinos, 'transports': transports}

    def recomendar_tours_personalized(self, prefs):
        destinos = prefs.get('destinos', [])
        transports = prefs.get('transports', [])
        with self.driver.session() as session:
            rs = session.run(
                """
                MATCH (tour:Tour)-[:VIAJA_EN]->(trans:Transporte)
                WHERE trans.nombre IN $transports
                  AND EXISTS {
                      MATCH (tour)-[:VISITA]->(d0:Destino)
                      WHERE d0.nombre IN $destinos
                  }
                WITH tour
                MATCH (tour)-[:VISITA]->(d:Destino)
                WITH tour, collect(DISTINCT d.nombre) AS details,
                     tour.precio AS price, tour.duracion AS duration
                RETURN tour.nombre AS name,
                       price,
                       duration,
                       details
                ORDER BY price ASC
                LIMIT 20
                """,
                destinos=destinos,
                transports=transports
            )
            return [
                {
                    'name': r['name'],
                    'price': r['price'],
                    'duration': r['duration'],
                    'details': r['details']
                }
                for r in rs
            ]

    def save_user_preferences(self, username, tour_name):
        with self.driver.session() as session:
            # Crear relaciones PREFIRIO a destinos
            session.run(
                """
                MATCH (u:Usuario {nombre: $username}), (tour:Tour {nombre: $tour_name})
                WITH u, tour
                MATCH (tour)-[:VISITA]->(d:Destino)
                MERGE (u)-[:PREFIRIO]->(d)
                """,
                username=username,
                tour_name=tour_name
            )
            # Crear relaciones PREFIRIO a transportes
            session.run(
                """
                MATCH (u:Usuario {nombre: $username}), (tour:Tour {nombre: $tour_name})
                WITH u, tour
                MATCH (tour)-[:VIAJA_EN]->(t:Transporte)
                MERGE (u)-[:PREFIRIO]->(t)
                """,
                username=username,
                tour_name=tour_name
            )

# Wrappers de conveniencia
_engine = None

def get_available_destinations(driver):
    global _engine
    _engine = RecommendationEngine(driver)
    return _engine.get_available_destinations()

def get_available_transports(driver):
    global _engine
    _engine = RecommendationEngine(driver)
    return _engine.get_available_transports()

def get_user_preferences(username, driver):
    global _engine
    if _engine is None:
        _engine = RecommendationEngine(driver)
    return _engine.get_user_preferences(username)

def generate_recommendations(destinos, transports, max_price, min_duration, max_duration, driver):
    global _engine
    if _engine is None:
        _engine = RecommendationEngine(driver)
    prefs = {
        'destinos': destinos,
        'transports': transports,
        'max_price': max_price,
        'min_duration': min_duration,
        'max_duration': max_duration
    }
    return _engine.recomendar_tours(prefs)

def generate_recommendations_personalized(prefs, driver):
    global _engine
    if _engine is None:
        _engine = RecommendationEngine(driver)
    return _engine.recomendar_tours_personalized(prefs)

def save_user_preferences(username, tour_name, driver):
    global _engine
    if _engine is None:
        _engine = RecommendationEngine(driver)
    return _engine.save_user_preferences(username, tour_name)