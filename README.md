#Microservicio de Gestión de Inventario y Productos

Este proyecto implementa un sistema de microservicios con FastAPI para la gestión de inventario y productos, utilizando RabbitMQ como sistema de mensajería. Incluye funcionalidades para agregar y consultar inventario, así como para crear y eliminar productos, comunicándose entre sí mediante colas de eventos.

##Estructura del Proyecto
project-root/
├── modulo_inventario/
│   └── gestion_inventario.py
├── modulo_productos/
│   └── gestion_productos.py
├── README.md
├── requirements.txt
└── Dockerfile (opcional, para dockerizar servicios)

##Requisitos Previos

    Python 3.8+
    FastAPI como framework de desarrollo de microservicios.
    RabbitMQ como sistema de mensajería.
    SQLite como base de datos local.
    Pika para la comunicación con RabbitMQ.
    Tenacity para reintentos en la conexión con RabbitMQ.
    PyBreaker para la implementación de Circuit Breakers.

##Instalación y Configuración

    ###Clonar el Repositorio

git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio

##Instalar dependencias

###Crea y activa un entorno virtual, luego instala las dependencias necesarias:

python3 -m venv microenv
source microenv/bin/activate
pip install -r requirements.txt

##Configurar RabbitMQ

###Ejecuta el contenedor de RabbitMQ (asegúrate de tener Docker instalado):

docker run -d --hostname rabbitmq --name some-rabbit -p 5672:5672 -p 15672:15672 rabbitmq:3-management

Accede a la interfaz de administración de RabbitMQ en http://localhost:15672 con usuario guest y contraseña guest.

##Configurar Bases de Datos SQLite

Asegúrate de crear las bases de datos productos.db e inventario.db en la raíz del proyecto.

#Ejecuta estos comandos en Python para crear las tablas necesarias:

    import sqlite3

    # Base de datos de productos
    conn = sqlite3.connect('productos.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT,
                        descripcion TEXT,
                        precio REAL,
                        categoria TEXT
                      )''')
    conn.commit()
    conn.close()

    # Base de datos de inventario
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventario (
                        producto_id INTEGER PRIMARY KEY,
                        cantidad INTEGER
                      )''')
    conn.commit()
    conn.close()

#Ejecución de los Servicios

Para ejecutar cada servicio, usa uvicorn en cada archivo de microservicio, en puertos diferentes.

    Microservicio de Productos (en modulo_productos/gestion_productos.py):

    uvicorn modulo_productos.gestion_productos:app --reload --port 8000

    Microservicio de Inventario (en modulo_inventario/gestion_inventario.py):

    uvicorn modulo_inventario.gestion_inventario:app --reload --port 8001

#Endpoints y Ejemplos de Uso

1. Microservicio de Productos

    ###Crear un producto

        POST http://localhost:8000/productos/

        Body:

        {
          "nombre": "Producto1",
          "descripcion": "Descripción del Producto1",
          "precio": 10.000,
          "categoria": "Categoría1"
        }

    ###Eliminar un producto
        DELETE http://localhost:8000/productos/{producto_id}

2. Microservicio de Inventario

    ###Agregar o actualizar inventario

        POST http://localhost:8001/inventario/

        Body:

    {
      "producto_id": 1,
      "cantidad": 50
    }

    ###Consultar inventario de un producto

    GET http://localhost:8001/inventario/{producto_id}

#Manejo de Errores y Resiliencia

    Circuit Breaker: Protege las conexiones a la base de datos y a RabbitMQ. Después de 3 intentos fallidos, se detendrán los intentos de conexión por 60 segundos.

    Reintentos: Si RabbitMQ está inactivo, el sistema intentará reconectar hasta 5 veces, con una espera de 2 segundos entre cada intento.

#Problemas Comunes

    Error de "Tabla no encontrada":
        Asegúrate de que las bases de datos productos.db e inventario.db están en la raíz del proyecto y contienen las tablas requeridas.

    Error de conexión a RabbitMQ:
        Asegúrate de que RabbitMQ esté en ejecución y que el contenedor esté en el puerto 5672.
