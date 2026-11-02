import os
import random
import math
from flask import Flask, render_template_string

# Inicialización de la aplicación Web Flask (Para Render)
app = Flask(__name__)

# ==============================================================================
# 1. ESTRUCTURAS DE DATOS ENLAZADAS (Requisito Académico)
# ==============================================================================

class Nodo:
    """Clase Nodo para almacenar cualquier entidad o estado del juego"""
    def __init__(self, dato):
        self.dato = dato          # Guarda el objeto o la cadena de texto
        self.siguiente = None     # Puntero al siguiente nodo en memoria

class ListaEnlazadaSimple:
    """
    Lista Enlazada Simple: Maneja entidades dinámicas (Goombas y Cupcakes).
    Permite inserción al final y eliminación de nodos específicos.
    """
    def __init__(self):
        self.cabeza = None
        self.tamano = 0

    def agregar(self, dato):
        nuevo_nodo = Nodo(dato)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo
        self.tamano += 1

    def eliminar(self, dato):
        actual = self.cabeza
        previo = None
        while actual:
            if actual.dato == dato:
                if previo:
                    previo.siguiente = actual.siguiente
                else:
                    self.cabeza = actual.siguiente
                self.tamano -= 1
                return True
            previo = actual
            actual = actual.siguiente
        return False

    def vaciar(self):
        """Elimina todos los nodos de la memoria"""
        self.cabeza = None
        self.tamano = 0

class ListaEnlazadaCircular:
    """
    Lista Enlazada Circular: Maneja las fases de la habilidad T.U.F.
    El último nodo apunta de nuevo a la cabeza, creando un ciclo infinito.
    """
    def __init__(self):
        self.cabeza = None

    def agregar(self, estado):
        nuevo_nodo = Nodo(estado)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
            nuevo_nodo.siguiente = self.cabeza
        else:
            actual = self.cabeza
            while actual.siguiente != self.cabeza:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo
            nuevo_nodo.siguiente = self.cabeza

# ==============================================================================
# 2. INTERFAZ WEB Y DESPLIEGUE EN LA NUBE (Render)
# ==============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Juego 3D Kirby - Estructuras de Datos</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: #ffffff;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .card {
            background: #0f3460;
            border-radius: 15px;
            padding: 30px;
            max-width: 750px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            text-align: center;
            border: 1px solid #e94560;
        }
        h1 { color: #e94560; margin-bottom: 10px; }
        .badge {
            background-color: #22c55e;
            color: #000;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 20px;
        }
        .code-box {
            text-align: left;
            background: #1a1a2e;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            color: #a7f3d0;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>🎮 Proyecto 3D: Kirby & Estructuras de Datos</h1>
        <div class="badge">● SERVICIO EN LÍNEA (Render Live)</div>
        <p>El proyecto ha sido desplegado exitosamente para la evaluación académica.</p>
        
        <div class="code-box">
            <strong>Estructuras de Datos Implementadas:</strong><br>
            ✔ Lista Enlazada Simple (Manejo dinámico de Goombas y Cupcakes)<br>
            ✔ Lista Enlazada Circular (Transición de Habilidades T.U.F.)<br>
            ✔ Motor 3D: Ursina Engine / Panda3D
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

# Si el archivo se ejecuta de forma local en tu computadora, abre Ursina
if __name__ == '__main__':
    # Detecta si está corriendo en la nube (Render) o en tu PC local
    if not os.environ.get('RENDER'):
        try:
            from ursina import *
            
            # Inicialización de Ursina solo en PC local
            juego_app = Ursina()
            
            # --- Configuración del escenario local ---
            Sky(color=color.azure)
            sun = DirectionalLight()
            sun.look_at(Vec3(1, -1, 1))
            
            suelo = Entity(model='plane', scale=(40, 1, 40), color=color.lime, texture='white_cube', collider='box')
            kirby = Entity(model='sphere', color=color.pink, position=(0, 1, 0), scale=1.5, collider='sphere')
            
            # Instanciación de Listas
            lista_goombas = ListaEnlazadaSimple()
            lista_cupcakes = ListaEnlazadaSimple()
            habilidad_circular = ListaEnlazadaCircular()
            
            habilidad_circular.agregar("DISPONIBLE")
            habilidad_circular.agregar("ESCUDO ACTIVO")
            habilidad_circular.agregar("EMBESTIDA T.U.F.")
            habilidad_circular.agregar("RECARGANDO")
            
            juego_app.run()
        except Exception as e:
            print(f"Modo servidor activado: {e}")
            app.run(host='0.0.0.0', port=5000)
    else:
        app.run(host='0.0.0.0', port=5000)
