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

# Modelo de Inventario
class Inventario(BaseModel):
    producto_id: int
    cantidad: int

# Conexión a RabbitMQ con reintentos
@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
@rabbitmq_breaker
def get_rabbitmq_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    return connection

def publish_event(event_type, product_id, cantidad):
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.queue_declare(queue='inventory_events')
        message = f"{event_type}:{product_id}:{cantidad}"
        channel.basic_publish(exchange='', routing_key='inventory_events', body=message)
        connection.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en RabbitMQ: {e}")

# Agregar Inventario con Circuit Breaker para la base de datos
@app.post("/inventario/")
@db_breaker
def agregar_inventario(inventario: Inventario):
    try:
        with sqlite3.connect("inventario.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO inventario (producto_id, cantidad) VALUES (?, ?)",
                        (inventario.producto_id, inventario.cantidad))
            conn.commit()
        publish_event("update", inventario.producto_id, inventario.cantidad)
        return {"mensaje": "Inventario actualizado"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")


# Verificar Inventario
@app.get("/inventario/{producto_id}")
@db_breaker
def obtener_inventario(producto_id: int):
    try:
        with sqlite3.connect("inventario.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT cantidad FROM inventario WHERE producto_id = ?", (producto_id,))
            resultado = cursor.fetchone()
            if resultado:
                return {"producto_id": producto_id, "cantidad": resultado[0]}
            else:
                raise HTTPException(status_code=404, detail="Producto no encontrado en inventario")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")
