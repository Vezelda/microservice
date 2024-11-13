import sqlite3

# Conectar a la base de datos de inventario (se creará si no existe)
conn = sqlite3.connect('inventario.db')
cursor = conn.cursor()

# Crear la tabla de inventario si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS inventario (
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
    PRIMARY KEY (producto_id)
)
''')

# Guardar cambios y cerrar la conexión
conn.commit()
conn.close()

print("Tabla 'inventario' creada con éxito")
