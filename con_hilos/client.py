import socket
import json

def mostrar_menu():
    """Muestra el menú de opciones"""
    print("\n--- Menú de Calificaciones ---")
    print("1. Agregar calificación")
    print("2. Buscar por ID")
    print("3. Actualizar calificación")
    print("4. Listar todas")
    print("5. Eliminar por ID")
    print("6. Salir")
    return input("Elija opción: ")

def enviar_comando(comando):
    """Envía un comando al servidor y recibe la respuesta"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 12345))
        client_socket.send(comando.encode('utf-8'))
        respuesta = client_socket.recv(4096).decode('utf-8')
        client_socket.close()
        return json.loads(respuesta)
    except Exception as e:
        return {"status": "error", "mensaje": f"Error de conexión: {str(e)}"}

def main():
    """Función principal del cliente"""
    print("Cliente del Sistema de Calificaciones")
    print("Conectando al servidor...")
    
    while True:
        try:
            opcion = mostrar_menu()
            
            if opcion == '1':
                id_est = input("ID del estudiante: ")

                # Consultar si ya existe el estudiante
                res_buscar = enviar_comando(f"BUSCAR|{id_est}")
                if res_buscar['status'] == 'ok' and res_buscar['data']:
                    nombre = res_buscar['data'][0]['Nombre']
                    print(f"Estudiante encontrado: {nombre}")
                else:
                    nombre = input("Nombre del nuevo estudiante: ")

                materia = input("Materia: ")
                calif = input("Calificación: ")

                res = enviar_comando(f"AGREGAR|{id_est}|{nombre}|{materia}|{calif}")
                print(res['mensaje'])
            
            elif opcion == '2':
                id_est = input("ID del estudiante: ")
                res = enviar_comando(f"BUSCAR|{id_est}")

                if res['status'] == 'ok' and res['data']:
                    print(f"\nResultados para ID {id_est}:")
                    for row in res['data']:
                        print(f"Materia: {row['Materia']} - Calificación: {row['Calificación']}")
                else:
                    print(res['mensaje'])
            
            elif opcion == '3':
                id_est = input("ID del estudiante: ")
                res = enviar_comando(f"BUSCAR|{id_est}")

                if res['status'] == 'ok' and res['data']:
                    materias = res['data']
                    print("\nMaterias registradas:")
                    for i, row in enumerate(materias, 1):
                        print(f"{i}. {row['Materia']} (Calificación actual: {row['Calificación']})")

                    try:
                        seleccion = int(input("Seleccione el número de la materia a actualizar: "))
                        if 1 <= seleccion <= len(materias):
                            materia = materias[seleccion - 1]['Materia']
                            nueva_calif = input(f"Nueva calificación para {materia}: ")
                            res_actualizar = enviar_comando(f"ACTUALIZAR|{id_est}|{materia}|{nueva_calif}")
                            print(res_actualizar['mensaje'])
                        else:
                            print("Selección inválida.")
                    except ValueError:
                        print("Ingrese un número válido.")
                else:
                    print("No se encontraron materias para ese estudiante.")
            
            elif opcion == '4':
                res = enviar_comando("LISTAR")
                if res['status'] == 'ok' and res['data']:
                    print("\n--- Todas las Calificaciones ---")
                    for row in res['data']:
                        print(f"ID: {row['ID_Estudiante']} | Nombre: {row['Nombre']} | Materia: {row['Materia']} | Calificación: {row['Calificación']}")
                else:
                    print("No hay calificaciones registradas.")
            
            elif opcion == '5':
                id_est = input("ID del estudiante: ")
                res = enviar_comando(f"ELIMINAR|{id_est}")
                print(res['mensaje'])
            
            elif opcion == '6':
                print("Saliendo del cliente...")
                break
            
            else:
                print("Opción inválida.")
        
        except KeyboardInterrupt:
            print("\nSaliendo...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()