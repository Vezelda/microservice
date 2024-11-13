import sqlite3

# Conectar a la base de datos de productos (se creará si no existe)
conn = sqlite3.connect('productos.db')
cursor = conn.cursor()

# Crear la tabla de productos si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio REAL NOT NULL,
    categoria TEXT NOT NULL
)
''')

# Guardar cambios y cerrar la conexión
conn.commit()
conn.close()

print("Tabla 'productos' creada con éxito")
