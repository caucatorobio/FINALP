from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'mysecretkey'  # Cambia esto por una clave segura

# Conexión a la base de datos
def get_db_connection():
    conn = sqlite3.connect('asistentes.db')
    conn.row_factory = sqlite3.Row
    return conn

# Login - Ruta para iniciar sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificar credenciales
        if username == 'admin' and password == 'admin':
            session['user'] = username
            return redirect('/')
        else:
            return "Credenciales incorrectas, vuelve a intentarlo."
    return render_template('login.html')

# Logout - Cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# Middleware para proteger rutas
def login_required(func):
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# Página principal
@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    asistentes = conn.execute("SELECT * FROM asistentes").fetchall()
    conn.close()
    return render_template('index.html', asistentes=asistentes)

# Ruta para buscar asistentes en tiempo real
@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '').lower()
    conn = get_db_connection()
    asistentes = conn.execute(
        "SELECT * FROM asistentes WHERE LOWER(nombre) LIKE ? OR documento LIKE ? OR telefono LIKE ? OR LOWER(correo) LIKE ?",
        (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%")
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in asistentes])

# Ruta para agregar asistentes
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        nombre = request.form['nombre']
        documento = request.form['documento']
        telefono = request.form['telefono']
        correo = request.form['correo']

        if all(x.isalpha() or x.isspace() for x in nombre) and documento.isdigit() and '@' in correo and '.' in correo:
            try:
                conn = get_db_connection()
                conn.execute(
                    "INSERT INTO asistentes (nombre, documento, telefono, correo) VALUES (?, ?, ?, ?)",
                    (nombre, documento, telefono, correo)
                )
                conn.commit()
                conn.close()
            except sqlite3.IntegrityError:
                return "Error: Documento ya registrado."
            return redirect('/')
        else:
            return "Datos inválidos, verifica las restricciones."
    return render_template('add_user.html')

# Ruta para marcar ingreso
@app.route('/ingresar/<documento>')
@login_required
def ingresar(documento):
    conn = get_db_connection()
    conn.execute("UPDATE asistentes SET ingreso = 1 WHERE documento = ?", (documento,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
