import socket
import csv
import json
import os

ARCHIVO_NRC = 'nrcs.csv'
PUERTO = 12346

def inicializar_nrcs():
    """Inicializa el archivo CSV de NRCs con datos de ejemplo"""
    if not os.path.exists(ARCHIVO_NRC):
        with open(ARCHIVO_NRC, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['NRC', 'Materia'])
            nrcs_ejemplo = [
                ['MAT101', 'Matemáticas Básicas'],
                ['FIS101', 'Física General'],
                ['QUI101', 'Química General'],
                ['PRO101', 'Programación I'],
                ['BDD101', 'Bases de Datos'],
                ['RED101', 'Redes de Computadoras'],
                ['SO101', 'Sistemas Operativos'],
                ['CAL101', 'Cálculo I'],
                ['ALG101', 'Algoritmos'],
                ['ING101', 'Inglés Técnico']
            ]
            writer.writerows(nrcs_ejemplo)
        print("Archivo nrcs.csv creado con datos de ejemplo")

def buscar_nrc(nrc):
    """Busca un NRC en el archivo CSV"""
    try:
        if not os.path.exists(ARCHIVO_NRC):
            return {"status": "error", "mensaje": "Archivo NRC no encontrado"}
            
        with open(ARCHIVO_NRC, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['NRC'].strip().upper() == nrc.strip().upper():
                    return {"status": "ok", "data": row}
        return {"status": "not_found", "mensaje": f"NRC {nrc} no encontrado"}
    except Exception as e:
        return {"status": "error", "mensaje": f"Error buscando NRC: {str(e)}"}

def listar_nrcs():
    """Lista todos los NRCs disponibles"""
    try:
        if not os.path.exists(ARCHIVO_NRC):
            return {"status": "error", "mensaje": "Archivo NRC no encontrado"}
            
        with open(ARCHIVO_NRC, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        return {"status": "ok", "data": data, "count": len(data)}
    except Exception as e:
        return {"status": "error", "mensaje": f"Error listando NRCs: {str(e)}"}

def procesar_comando(comando):
    """Procesa los comandos recibidos del cliente"""
    try:
        partes = comando.strip().split('|')
        if not partes:
            return {"status": "error", "mensaje": "Comando vacío"}
            
        op = partes[0]
        
        if op == 'BUSCAR_NRC' and len(partes) == 2:
            return buscar_nrc(partes[1])
        elif op == 'LISTAR_NRC':
            return listar_nrcs()
        elif op == 'STATUS':
            return {"status": "ok", "mensaje": "Servidor NRC funcionando"}
        else:
            return {"status": "error", "mensaje": f"Comando inválido: {op}"}
    except Exception as e:
        return {"status": "error", "mensaje": f"Error procesando comando: {str(e)}"}

def main():
    """Función principal del servidor de NRCs"""
    inicializar_nrcs()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', PUERTO))
    server_socket.listen(5)
    print(f"Servidor de NRCs escuchando en puerto {PUERTO}...")
    print("NRCs disponibles: MAT101, FIS101, QUI101, PRO101, BDD101, RED101, SO101, CAL101, ALG101, ING101")
    
    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Conexión aceptada desde {addr}")
            
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if data:
                    print(f"Comando recibido: {data}")
                    respuesta = procesar_comando(data)
                    client_socket.send(json.dumps(respuesta).encode('utf-8'))
                    print(f"Respuesta enviada: {respuesta['status']}")
            except Exception as e:
                error_msg = {"status": "error", "mensaje": f"Error interno: {str(e)}"}
                client_socket.send(json.dumps(error_msg).encode('utf-8'))
            finally:
                client_socket.close()
                print(f"Conexión con {addr} cerrada")
                
    except KeyboardInterrupt:
        print("\nServidor de NRCs detenido por el usuario.")
    except Exception as e:
        print(f"Error crítico del servidor: {e}")
    finally:
        server_socket.close()
        print("Servidor de NRCs cerrado correctamente.")

if __name__ == "__main__":
    main()