import sqlite3

# Conexión y creación de base de datos
conn = sqlite3.connect('asistentes.db')

# Creación de tabla
conn.execute('''
CREATE TABLE IF NOT EXISTS asistentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    documento TEXT UNIQUE NOT NULL,
    telefono TEXT NOT NULL,
    correo TEXT NOT NULL,
    ingreso BOOLEAN DEFAULT 0
);
''')
print("Base de datos creada y lista para usarse.")

# Cerrar conexión
conn.close()
