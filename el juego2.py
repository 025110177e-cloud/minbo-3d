from ursina import *
import random
import math

# ==============================================================================
# 1. ESTRUCTURAS DE DATOS ENLAZADAS (Requisito Académico)
# ==============================================================================

class Nodo:
    """Clase Nodo para almacenar cualquier entidad o estado del juego"""
    def __init__(self, dato):
        self.dato = dato          # Guarda el objeto 3D o la cadena de texto
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
# 2. CONFIGURACIÓN DEL MOTOR 3D Y ESCENARIO (Ursina Engine)
# ==============================================================================
app = Ursina()

# Iluminación y Cielo
Sky(color=color.azure)
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, 1))
AmbientLight(color=color.rgba(120, 120, 120, 255))

# Terreno Principal (Césped)
suelo = Entity(model='plane', scale=(40, 1, 40), color=color.lime, texture='white_cube', collider='box')

# 3 Lagos Celestes
lago1 = Entity(model='cylinder', position=(-10, 0.01, 8), scale=(7, 0.05, 7), color=color.cyan)
lago2 = Entity(model='cylinder', position=(10, 0.01, -8), scale=(6, 0.05, 6), color=color.cyan)
lago3 = Entity(model='cylinder', position=(-8, 0.01, -10), scale=(6, 0.05, 6), color=color.cyan)

# --- MONTAÑA CON ESCALERA TRANSITABLE ---
montana_visual = Entity(model='cone', position=(10, 3.5, 8), scale=(10, 7, 10), color=color.gray)

# Cueva en la base de la montaña (Entrada oscura)
cueva_entrada = Entity(model='cube', position=(10, 1, 3.1), scale=(2.5, 2.5, 0.5), color=color.black, collider='box')

# Escalera esculpida (4 Escalones)
escalones = [
    Entity(model='cube', position=(13.5, 0.4, 5.5), scale=(2.2, 0.4, 1.4), color=color.light_gray, collider='box'),
    Entity(model='cube', position=(12.8, 1.0, 6.5), scale=(2.2, 0.4, 1.4), color=color.light_gray, collider='box'),
    Entity(model='cube', position=(12.0, 1.6, 7.5), scale=(2.2, 0.4, 1.4), color=color.light_gray, collider='box'),
    Entity(model='cube', position=(11.0, 2.2, 8.2), scale=(2.2, 0.4, 1.4), color=color.light_gray, collider='box')
]

# Jugador (Kirby 3D con detalles visuales)
kirby = Entity(model='sphere', color=color.pink, position=(0, 1, 0), scale=1.5, collider='sphere')
ojos_kirby1 = Entity(parent=kirby, model='sphere', color=color.black, position=(0.2, 0.2, 0.5), scale=(0.12, 0.25, 0.1))
ojos_kirby2 = Entity(parent=kirby, model='sphere', color=color.black, position=(-0.2, 0.2, 0.5), scale=(0.12, 0.25, 0.1))
mejilla1 = Entity(parent=kirby, model='sphere', color=color.red, position=(0.35, -0.05, 0.45), scale=(0.15, 0.1, 0.1))
mejilla2 = Entity(parent=kirby, model='sphere', color=color.red, position=(-0.35, -0.05, 0.45), scale=(0.15, 0.1, 0.1))

# Instanciación de Listas Enlazadas
lista_goombas = ListaEnlazadaSimple()
lista_cupcakes = ListaEnlazadaSimple()

# Configuración de Estados en Lista Enlazada Circular
habilidad_circular = ListaEnlazadaCircular()
habilidad_circular.agregar("DISPONIBLE")
habilidad_circular.agregar("ESCUDO ACTIVO")
habilidad_circular.agregar("EMBESTIDA T.U.F.")
habilidad_circular.agregar("RECARGANDO")

estado_actual_habilidad = habilidad_circular.cabeza

# Variables de Estado del Juego
goombas_derrotados = 0
cupcakes_recolectados = 0
monedas = 0
vidas = 3
juego_terminado = False
en_pausa = False
velocidad_goombas = 2.5

# Interfaz Visual (UI)
vidas_texto = Text(text="VIDAS: 3", position=(-0.85, 0.45), color=color.magenta, scale=2)
goombas_texto = Text(text="GOOMBAS: 0 / 6", position=(0.45, 0.45), color=color.red, scale=2)
monedas_texto = Text(text="MONEDAS: 0", position=(0.45, 0.38), color=color.yellow, scale=2)
cupcakes_texto = Text(text="CUPCAKES: 0 / 3", position=(0.45, 0.31), color=color.orange, scale=2)
habilidad_texto = Text(text=f"Habilidad [Q]: {estado_actual_habilidad.dato}", position=(-0.25, -0.42), color=color.green, scale=2)

# Mensaje Central de Fin de Juego
mensaje_final = Text(text="", position=(0, 0), origin=(0, 0), scale=3, color=color.gold, enabled=False)

# Cámara Iso-3D
camera.position = (0, 16, -18)
camera.rotation_x = 40

# ==============================================================================
# 3. SISTEMA DE MENÚ (Pausa, Reanudar, Reiniciar)
# ==============================================================================

panel_pausa = Entity(parent=camera.ui, model='quad', scale=(0.5, 0.6), color=color.rgba(0, 0, 0, 180), enabled=False)
texto_pausa = Text(parent=panel_pausa, text="JUEGO EN PAUSA", position=(0, 0.2), origin=(0, 0), scale=2, color=color.white)

def alternar_pausa():
    global en_pausa
    if juego_terminado:
        return
    en_pausa = not en_pausa
    panel_pausa.enabled = en_pausa

def reiniciar_juego():
    global goombas_derrotados, cupcakes_recolectados, monedas, vidas, juego_terminado, en_pausa, estado_actual_habilidad

    # Vaciar entidades de la memoria
    nodo_g = lista_goombas.cabeza
    while nodo_g:
        destroy(nodo_g.dato)
        nodo_g = nodo_g.siguiente
    lista_goombas.vaciar()

    nodo_c = lista_cupcakes.cabeza
    while nodo_c:
        destroy(nodo_c.dato)
        nodo_c = nodo_c.siguiente
    lista_cupcakes.vaciar()

    # Reiniciar variables
    kirby.position = Vec3(0, 1, 0)
    kirby.color = color.pink
    vidas = 3
    goombas_derrotados = 0
    cupcakes_recolectados = 0
    monedas = 0
    juego_terminado = False
    en_pausa = False
    panel_pausa.enabled = False
    mensaje_final.enabled = False

    estado_actual_habilidad = habilidad_circular.cabeza
    habilidad_texto.text = f"Habilidad [Q]: {estado_actual_habilidad.dato}"

    vidas_texto.text = f"VIDAS: {vidas}"
    goombas_texto.text = f"GOOMBAS: {goombas_derrotados} / 6"
    cupcakes_texto.text = f"CUPCAKES: {cupcakes_recolectados} / 3"
    monedas_texto.text = f"MONEDAS: {monedas}"

    # Spawning Goombas
    posiciones_goombas = [
        (10, 0.8, 1),
        (-12, 0.8, -5),
        (5, 0.8, -12),
        (-14, 0.8, 12),
        (0, 0.8, 14),
        (-5, 0.8, -5)
    ]
    for gx, gy, gz in posiciones_goombas:
        goomba = Entity(model='sphere', color=color.brown, position=(gx, gy, gz), scale=1.2, collider='sphere')
        Entity(parent=goomba, model='sphere', color=color.white, position=(0.2, 0.2, 0.45), scale=(0.15, 0.2, 0.1))
        Entity(parent=goomba, model='sphere', color=color.white, position=(-0.2, 0.2, 0.45), scale=(0.15, 0.2, 0.1))
        Entity(parent=goomba, model='cube', color=color.black, position=(0.18, 0.35, 0.47), scale=(0.25, 0.05, 0.05), rotation_z=-20)
        Entity(parent=goomba, model='cube', color=color.black, position=(-0.18, 0.35, 0.47), scale=(0.25, 0.05, 0.05), rotation_z=20)
        lista_goombas.agregar(goomba)

    # Spawning Cupcakes (Uno arriba de la escalera en la montaña)
    posiciones_cupcakes = [
        (11.0, 3.2, 8.2),  # Cima de la escalera
        (-7, 0.6, 2),
        (6, 0.6, -6)
    ]
    for cx, cy, cz in posiciones_cupcakes:
        cupcake = Entity(model='cube', color=color.yellow, position=(cx, cy, cz), scale=0.8, collider='box')
        lista_cupcakes.agregar(cupcake)

btn_reanudar = Button(parent=panel_pausa, text="REANUDAR", position=(0, 0.05), scale=(0.3, 0.08), color=color.azure, on_click=alternar_pausa)
btn_reiniciar_pausa = Button(parent=panel_pausa, text="REINICIAR", position=(0, -0.08), scale=(0.3, 0.08), color=color.orange, on_click=reiniciar_juego)

btn_pausa_top = Button(parent=camera.ui, text="|| Pausa [ESC]", position=(-0.75, 0.45), scale=(0.18, 0.06), color=color.gray, on_click=alternar_pausa)
btn_reiniciar_top = Button(parent=camera.ui, text="Reiniciar", position=(-0.55, 0.45), scale=(0.15, 0.06), color=color.red, on_click=reiniciar_juego)

reiniciar_juego()

# ==============================================================================
# 4. LÓGICA DE CONTROL Y CICLO PRINCIPAL
# ==============================================================================

def update():
    global goombas_derrotados, cupcakes_recolectados, monedas, vidas, juego_terminado, estado_actual_habilidad

    if juego_terminado or en_pausa:
        return

    # Movimiento WASD
    velocidad = 8 * time.dt
    dx = (held_keys['d'] - held_keys['a'])
    dz = (held_keys['w'] - held_keys['s'])

    if dx != 0 or dz != 0:
        angulo = math.degrees(math.atan2(dx, dz))
        kirby.rotation_y = angulo

        nueva_x = clamp(kirby.x + dx * velocidad, -18, 18)
        nueva_z = clamp(kirby.z + dz * velocidad, -18, 18)
        
        # Detectar si Kirby está en la zona de la escalera
        en_zona_escalera = False
        for esc in escalones:
            if abs(nueva_x - esc.x) < 1.5 and abs(nueva_z - esc.z) < 1.2:
                en_zona_escalera = True
                break

        # Si NO está en la escalera, aplicar la hitbox sólida de la montaña
        if not en_zona_escalera:
            distancia_a_montana = math.sqrt((nueva_x - 10)**2 + (nueva_z - 8)**2)
            if distancia_a_montana < 4.0:
                angulo_colision = math.atan2(nueva_z - 8, nueva_x - 10)
                nueva_x = 10 + math.cos(angulo_colision) * 4.0
                nueva_z = 8 + math.sin(angulo_colision) * 4.0

        kirby.position = Vec3(nueva_x, kirby.y, nueva_z)

    # Escalado dinámico en Y (Permite subir peldaño a peldaño)
    sobre_escalon = False
    for esc in escalones:
        if abs(kirby.x - esc.x) < 1.3 and abs(kirby.z - esc.z) < 1.0:
            kirby.y = esc.y + 0.8
            sobre_escalon = True
            break
            
    if not sobre_escalon:
        kirby.y = 1.0  # Altura normal sobre el pasto

    camera.x = kirby.x
    camera.z = kirby.z - 15

    # --------------------------------------------------------------------------
    # PERSECUCIÓN Y COLISIÓN DE GOOMBAS (Lista Enlazada Simple)
    # --------------------------------------------------------------------------
    nodo_actual = lista_goombas.cabeza
    while nodo_actual:
        g = nodo_actual.dato
        nodo_siguiente = nodo_actual.siguiente

        g.look_at(kirby.position)
        g.rotation_x = 0
        g.rotation_z = 0
        direccion = (kirby.position - g.position).normalized()
        g.position += direccion * velocidad_goombas * time.dt

        if distance(kirby.position, g.position) < 1.4:
            if estado_actual_habilidad.dato in ["ESCUDO ACTIVO", "EMBESTIDA T.U.F."]:
                destroy(g)
                lista_goombas.eliminar(g)
                goombas_derrotados += 1
                goombas_texto.text = f"GOOMBAS: {goombas_derrotados} / 6"
            else:
                vidas -= 1
                vidas_texto.text = f"VIDAS: {vidas}"
                destroy(g)
                lista_goombas.eliminar(g)

                if vidas <= 0:
                    juego_terminado = True
                    mensaje_final.text = "¡GAME OVER!\nTe has quedado sin vidas."
                    mensaje_final.color = color.red
                    mensaje_final.enabled = True
                    return

            if goombas_derrotados >= 6 and cupcakes_recolectados >= 3:
                monedas = 5
                monedas_texto.text = f"MONEDAS: {monedas}"
                juego_terminado = True
                mensaje_final.text = "¡MISIÓN CUMPLIDA!\nDerrotaste 6 Goombas y 3 Cupcakes\n+5 MONEDAS RECOMPENSA"
                mensaje_final.color = color.yellow
                mensaje_final.enabled = True
                return

        nodo_actual = nodo_siguiente

    # --------------------------------------------------------------------------
    # COLISIÓN CON CUPCAKES (Lista Enlazada Simple)
    # --------------------------------------------------------------------------
    nodo_c = lista_cupcakes.cabeza
    while nodo_c:
        c = nodo_c.dato
        nodo_sig_c = nodo_c.siguiente

        if distance(kirby.position, c.position) < 1.5:
            destroy(c)
            lista_cupcakes.eliminar(c)
            cupcakes_recolectados += 1
            cupcakes_texto.text = f"CUPCAKES: {cupcakes_recolectados} / 3"

            if goombas_derrotados >= 6 and cupcakes_recolectados >= 3:
                monedas = 5
                monedas_texto.text = f"MONEDAS: {monedas}"
                juego_terminado = True
                mensaje_final.text = "¡MISIÓN CUMPLIDA!\nDerrotaste 6 Goombas y 3 Cupcakes\n+5 MONEDAS RECOMPENSA"
                mensaje_final.color = color.yellow
                mensaje_final.enabled = True
                return

        nodo_c = nodo_sig_c

def input(key):
    global estado_actual_habilidad, juego_terminado

    if key == 'escape':
        alternar_pausa()

    if juego_terminado or en_pausa:
        return

    if key == 'q':
        estado_actual_habilidad = estado_actual_habilidad.siguiente
        habilidad_texto.text = f"Habilidad [Q]: {estado_actual_habilidad.dato}"
        
        if estado_actual_habilidad.dato == "ESCUDO ACTIVO":
            kirby.color = color.cyan
        elif estado_actual_habilidad.dato == "EMBESTIDA T.U.F.":
            kirby.color = color.orange
        else:
            kirby.color = color.pink

app.run()