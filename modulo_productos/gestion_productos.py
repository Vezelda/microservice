from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import pika
from tenacity import retry, stop_after_attempt, wait_fixed
import pybreaker

app = FastAPI()

# Configuración de Circuit Breakers
db_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60)
rabbitmq_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60)

# Modelo de Producto
class Producto(BaseModel):
    nombre: str
    descripcion: str
    precio: float
    categoria: str

# Conexión a RabbitMQ con reintentos
@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
@rabbitmq_breaker
def get_rabbitmq_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    return connection

def publish_event(event_type, product_id):
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.queue_declare(queue='product_events')
        message = f"{event_type}:{product_id}"
        channel.basic_publish(exchange='', routing_key='product_events', body=message)
        connection.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en RabbitMQ: {e}")

# Crear Producto con Circuit Breaker para la base de datos
@app.post("/productos/")
@db_breaker
def crear_producto(producto: Producto):
    try:
        with sqlite3.connect("productos.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO productos (nombre, descripcion, precio, categoria) VALUES (?, ?, ?, ?)",
                        (producto.nombre, producto.descripcion, producto.precio, producto.categoria))
            producto_id = cursor.lastrowid
            conn.commit()
        publish_event("create", producto_id)
        return {"id": producto_id, "mensaje": "Producto creado"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")

# Eliminar Producto con Circuit Breaker para la base de datos
@app.delete("/productos/{producto_id}")
@db_breaker
def eliminar_producto(producto_id: int):
    try:
        with sqlite3.connect("productos.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
            conn.commit()
        publish_event("delete", producto_id)
        return {"mensaje": "Producto eliminado"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")
