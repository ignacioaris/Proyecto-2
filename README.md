Para armar la base de datos se necesita iniciar neo4j desktop, crear una nueva base de datos. 
se debe crear un nuevo usuario con el nombre: 'pryecto2' y contraseña: 'Estructuras1' (estos valores estan especificados en el codigo)

se deben subir los archivos .csv compartidos al proyecto en neo4j y correr los siguientes querys: 

- Para 'tours.csv: 
  LOAD CSV WITH HEADERS FROM 'file:///tours.csv' AS row
  MERGE (:Tour {
  nombre: row.nombre,
  duracion: toInteger(row.duracion),
  precio: toInteger(row.precio)
  });

- Para 'destinos.csv':
  LOAD CSV WITH HEADERS FROM 'file:///destinos.csv' AS row
  MERGE (:Destino {nombre: row.nombre});

- Para 'transportes.csv':
  LOAD CSV WITH HEADERS FROM 'file:///transportes.csv' AS row
  MERGE (:Transporte {nombre: row.nombre});

- Para 'visita.csv':
  LOAD CSV WITH HEADERS FROM 'file:///visita.csv' AS row
  MATCH (t:Tour {nombre: row.tour})
  MATCH (d:Destino {nombre: row.destino})
  MERGE (t)-[:VISITA]->(d);

- Para 'viaja_en.csv':
  LOAD CSV WITH HEADERS FROM 'file:///viaja_en.csv' AS row
  MATCH (t:Tour {nombre: row.tour})
  MATCH (v:Transporte {nombre: row.transporte})
  MERGE (t)-[:VIAJA_EN]->(v);

* para que el query sea exitoso se debe cambiar la ruta del archivo por la correcta (esta se obtiene desde la informacin del documento en neo4j)

* La base de datos inicialmente no cuenta con ningun usuario por lo que sera necesario registrarse la primera vez que se corra el programa






* videos de pruebas con usuarios:
  - https://drive.google.com/file/d/1SSpIwn8wtfzGDPhkPTMa99EIC79iSoWm/view?usp=share_link
  - https://drive.google.com/file/d/1rzqZd1GEAutSjyxsk-JFFQgsQDZiAltm/view?usp=share_link
  - https://uvggt-my.sharepoint.com/:v:/g/personal/dele24247_uvg_edu_gt/Ee9E_NQLw0xOhqvob6nB0RgBdhNTSR8xLntCGnKm0eCWBw?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=7sy6u6
  - https://uvggt-my.sharepoint.com/:v:/g/personal/dele24247_uvg_edu_gt/EUHZseNID-NIjtNkG5fEnjYBCk1IEnuYVlYDHyHKHNhxGA?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=4DoAJm
  
