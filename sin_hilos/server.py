import socket
import csv
import json
import os

ARCHIVO_CSV = '../calificaciones.csv'
PUERTO = 12345

# Constantes para comandos
AGREGAR = "AGREGAR"
BUSCAR = "BUSCAR"
ACTUALIZAR = "ACTUALIZAR"
LISTAR = "LISTAR"
ELIMINAR = "ELIMINAR"
VERIFICAR_ID = "VERIFICAR_ID"


def inicializar_csv():
    """Inicializa el archivo CSV si no existe"""
    if not os.path.exists(ARCHIVO_CSV):
        with open(ARCHIVO_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID_Estudiante', 'Nombre', 'Materia', 'Calificación'])
        print("Archivo calificaciones.csv creado")


def verificar_id_existe(id_est, materia=None):
    """Verifica si un ID y materia ya existen (ambos deben coincidir para bloquear)"""
    try:
        if not os.path.exists(ARCHIVO_CSV):
            return False, None

        with open(ARCHIVO_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] == id_est and (materia is None or row['Materia'].lower() == materia.lower()):
                    return True, row['Nombre']
        return False, None
    except Exception as e:
        print(f"Error verificando ID: {e}")
        return False, None


def validar_calificacion(calif):
    """Valida que la calificación sea un número entre 0 y 20"""
    try:
        calif_float = float(calif)
        if 0 <= calif_float <= 20:
            return True, calif_float, None
        else:
            return False, None, "La calificación debe estar entre 0 y 20"
    except ValueError:
        return False, None, "La calificación debe ser un número válido"


def agregar_calificacion(id_est, nombre, materia, calif):
    """Agrega una nueva calificación al CSV con validaciones"""
    try:
        es_valida, calif_float, error_msg = validar_calificacion(calif)
        if not es_valida:
            return {"status": "error", "mensaje": error_msg}

        # Verificar si ya existe ese ID en esa materia
        existe, nombre_existente = verificar_id_existe(id_est, materia)
        if existe:
            return {"status": "error", "mensaje": f"Ya existe una calificación para {nombre_existente} en {materia}"}

        # Agregar nuevo registro
        with open(ARCHIVO_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([id_est, nombre, materia, calif_float])

        return {"status": "ok", "mensaje": f"Calificación agregada para {nombre} en {materia}"}

    except Exception as e:
        return {"status": "error", "mensaje": f"Error agregando calificación: {str(e)}"}


def buscar_por_id(id_est):
    """Busca todas las calificaciones de un estudiante por ID"""
    try:
        if not os.path.exists(ARCHIVO_CSV):
            return {"status": "error", "mensaje": "No hay calificaciones registradas"}

        resultados = []
        with open(ARCHIVO_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] == id_est:
                    resultados.append(row)

        if resultados:
            return {"status": "ok", "data": resultados}
        else:
            return {"status": "not_found", "mensaje": f"ID {id_est} no encontrado"}
    except Exception as e:
        return {"status": "error", "mensaje": f"Error buscando: {str(e)}"}


def actualizar_calificacion(id_est, materia, nueva_calif):
    """Actualiza la calificación de un estudiante en una materia específica"""
    try:
        es_valida, calif_float, error_msg = validar_calificacion(nueva_calif)
        if not es_valida:
            return {"status": "error", "mensaje": error_msg}

        rows = []
        found = False

        with open(ARCHIVO_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] == id_est and row['Materia'].lower() == materia.lower():
                    row['Calificación'] = calif_float
                    found = True
                rows.append(row)

        if not found:
            return {"status": "not_found", "mensaje": f"No se encontró la materia {materia} para ID {id_est}"}

        with open(ARCHIVO_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['ID_Estudiante', 'Nombre', 'Materia', 'Calificación'])
            writer.writeheader()
            writer.writerows(rows)

        return {"status": "ok", "mensaje": f"Calificación actualizada a {calif_float} en {materia}"}

    except Exception as e:
        return {"status": "error", "mensaje": f"Error actualizando: {str(e)}"}


def listar_todas():
    """Lista todas las calificaciones"""
    try:
        if not os.path.exists(ARCHIVO_CSV):
            return {"status": "ok", "data": [], "count": 0}

        with open(ARCHIVO_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        return {"status": "ok", "data": data, "count": len(data)}
    except Exception as e:
        return {"status": "error", "mensaje": f"Error listando: {str(e)}"}


def eliminar_por_id(id_est):
    """Elimina todas las calificaciones de un estudiante por ID"""
    try:
        rows = []
        found = False

        with open(ARCHIVO_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] != id_est:
                    rows.append(row)
                else:
                    found = True

        if not found:
            return {"status": "not_found", "mensaje": f"ID {id_est} no encontrado"}

        with open(ARCHIVO_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['ID_Estudiante', 'Nombre', 'Materia', 'Calificación'])
            writer.writeheader()
            writer.writerows(rows)

        return {"status": "ok", "mensaje": f"Registros eliminados para ID {id_est}"}

    except Exception as e:
        return {"status": "error", "mensaje": f"Error eliminando: {str(e)}"}


def verificar_id_disponible_servidor(id_est):
    """Verifica si un ID está disponible"""
    existe, nombre_existente = verificar_id_existe(id_est)
    if existe:
        return {"status": "error", "mensaje": f"ID {id_est} ya existe para: {nombre_existente}"}
    else:
        return {"status": "ok", "mensaje": "ID disponible"}


def procesar_comando(comando):
    """Procesa los comandos recibidos del cliente"""
    try:
        if not comando or not comando.strip():
            return {"status": "error", "mensaje": "Comando vacío"}

        partes = comando.strip().split('|')
        op = partes[0]

        if op == AGREGAR and len(partes) == 5:
            return agregar_calificacion(partes[1], partes[2], partes[3], partes[4])
        elif op == BUSCAR and len(partes) == 2:
            return buscar_por_id(partes[1])
        elif op == ACTUALIZAR and len(partes) == 4:  # Ahora soporta ID|MATERIA|CALIFICACION
            return actualizar_calificacion(partes[1], partes[2], partes[3])
        elif op == LISTAR:
            return listar_todas()
        elif op == ELIMINAR and len(partes) == 2:
            return eliminar_por_id(partes[1])
        elif op == VERIFICAR_ID and len(partes) == 2:
            return verificar_id_disponible_servidor(partes[1])
        else:
            return {"status": "error", "mensaje": f"Comando inválido: {comando}"}

    except Exception as e:
        return {"status": "error", "mensaje": f"Error procesando comando: {str(e)}"}


def main():
    """Función principal del servidor secuencial"""
    inicializar_csv()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', PUERTO))
    server_socket.listen(1)
    print(f"Servidor escuchando en puerto {PUERTO}...")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Cliente conectado desde {addr}")

            try:
                data = client_socket.recv(4096).decode('utf-8')
                if data:
                    print(f"Comando recibido: {data}")
                    respuesta = procesar_comando(data)
                    client_socket.send(json.dumps(respuesta).encode('utf-8'))
                    print(f"Respuesta: {respuesta['status']}")
            except Exception as e:
                error_msg = {"status": "error", "mensaje": f"Error de comunicación: {str(e)}"}
                client_socket.send(json.dumps(error_msg).encode('utf-8'))
            finally:
                client_socket.close()
                print("Cliente desconectado.\n")

    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
    except Exception as e:
        print(f"Error crítico del servidor: {e}")
    finally:
        server_socket.close()
        print("Servidor cerrado correctamente.")


if __name__ == "__main__":
    main()