from flask import Flask, render_template, request, redirect, url_for, session
from neo4j import GraphDatabase, basic_auth
import auth
import recommendation_engine

# Servir plantillas y archivos estáticos desde la misma carpeta
app = Flask(
    __name__,
    template_folder='.',
    static_folder='.',
    static_url_path=''
)
app.secret_key = 'your_secret_key'

# Conexión a Neo4j
driver = GraphDatabase.driver(
    auth.uri,
    auth=basic_auth(auth.user, auth.password)
)

# Ruta: Iniciar sesión
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = request.form['username']
        pwd  = request.form['password']
        if recommendation_engine.authenticate(user, pwd, driver):
            session['username'] = user
            return redirect(url_for('home'))
        else:
            error = 'Credenciales inválidas'
    return render_template('login.html', error=error)

# Ruta: Registro de usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        realname = request.form['realname']
        pwd      = request.form['password']
        # Crear usuario en Neo4j
        with driver.session() as session_db:
            result = session_db.run(
                "MATCH (u:Usuario {nombre: $username}) RETURN u",
                username=username
            )
            if result.single():
                error = 'El nombre de usuario ya existe'
            else:
                session_db.run(
                    "CREATE (u:Usuario {nombre: $username, nombreReal: $realname, contrasena: $password})",
                    username=username,
                    realname=realname,
                    password=pwd
                )
                return redirect(url_for('login'))
    return render_template('register.html', error=error)

# Ruta: Página principal con opciones
@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

# Ruta: Selección de destinos para búsqueda manual
@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'username' not in session:
        return redirect(url_for('login'))
    options = recommendation_engine.get_available_destinations(driver)
    if request.method == 'POST':
        session['destinations'] = request.form.getlist('destinations')
        return redirect(url_for('transport'))
    return render_template('search.html', options=options)

# Ruta: Selección de transporte para búsqueda manual
@app.route('/transport', methods=['GET', 'POST'])
def transport():
    if 'username' not in session or 'destinations' not in session:
        return redirect(url_for('login'))
    options = recommendation_engine.get_available_transports(driver)
    if request.method == 'POST':
        session['transports'] = request.form.getlist('transports')
        return redirect(url_for('filters'))
    return render_template('transport.html', options=options)

# Ruta: Filtros de precio y duración para búsqueda manual
@app.route('/filters', methods=['GET', 'POST'])
def filters():
    if 'username' not in session or 'destinations' not in session or 'transports' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        session['max_price']    = float(request.form['max_price'])
        session['min_duration'] = float(request.form['min_duration'])
        session['max_duration'] = float(request.form['max_duration'])
        return redirect(url_for('recommendations'))
    return render_template('filters.html')

# Ruta: Mostrar recomendaciones de búsqueda manual
@app.route('/recommendations')
def recommendations():
    if 'username' not in session or 'destinations' not in session or 'transports' not in session:
        return redirect(url_for('login'))
    dests        = session['destinations']
    transports   = session['transports']
    max_price    = session.get('max_price', float('inf'))
    min_duration = session.get('min_duration', 0)
    max_duration = session.get('max_duration', float('inf'))

    recs = recommendation_engine.generate_recommendations(
        dests, transports,
        max_price,
        min_duration, max_duration,
        driver
    )
    return render_template('recommendations.html', recommendations=recs)

# Ruta: Manejar selección de un tour
@app.route('/select', methods=['POST'])
def select_tour():
    if 'username' not in session:
        return redirect(url_for('login'))
    tour_name = request.form['tour_name']
    user = session['username']
    # Guardar relaciones PREFIRIO de usuario a destinos y transportes del tour
    recommendation_engine.save_user_preferences(user, tour_name, driver)
    return redirect(url_for('home'))

# Ruta: Recomendaciones personalizadas (basado en preferencias del usuario)
@app.route('/personalized')
def personalized():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = session['username']
    prefs = recommendation_engine.get_user_preferences(user, driver)
    recs = recommendation_engine.generate_recommendations_personalized(prefs, driver)
    return render_template('recommendations.html', recommendations=recs)

if __name__ == '__main__':
    app.run(debug=True)