from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "pryecto2"
password = "Estructuras1"

driver = GraphDatabase.driver(uri, auth=(user, password))

def run_query(query):
    with driver.session() as session:
        result = session.run(query)
        records = list(result)
        return records
