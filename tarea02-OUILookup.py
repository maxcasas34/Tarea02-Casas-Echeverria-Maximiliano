#Maximiliano Casas Echeverria , maximiliano.casas@alumnos.uv.cl
#Carlos Gaete Concha , carlos.gaete@alumnos.uv.cl
#Diego Retamales Castillo , diego.retamales@alumnos.uv.cl
import sys  # Módulo para interactuar con el sistema
import getopt  # Módulo para manejar argumentos de línea de comandos
import requests  # Módulo para realizar solicitudes HTTP
import subprocess  # Módulo para ejecutar comandos del sistema
import re  # Módulo para expresiones regulares
import time  # Módulo para manejar el tiempo

# Función para obtener el fabricante a partir de una dirección MAC
def obtener_fabricante(mac):
    url = f"https://api.maclookup.app/v2/macs/{mac}"  # URL de la API
    tiempo_inicio = time.time()  # Medir el tiempo de respuesta
    try:
        respuesta = requests.get(url)  # Hacer la solicitud a la API
        tiempo_fin = time.time()  # Finalizar la medición de tiempo
        
        if respuesta.status_code == 200:  # Verificar si la solicitud fue exitosa
            datos = respuesta.json()  # Convertir la respuesta a JSON
            empresa = datos.get('company')  # Obtener el nombre de la empresa
            if not empresa or empresa.lower() == 'not found':
                empresa = "Not Found"  # Manejo de error si no se encuentra la empresa
        else:
            empresa = "Not Found"  # Manejo de error para otros códigos de estado
    except:
        empresa = "Not Found"  # Manejo de excepción
        tiempo_fin = time.time()  # Finalizar la medición de tiempo
    
    return empresa, int((tiempo_fin - tiempo_inicio) * 1000)  # Retornar la empresa y el tiempo de respuesta

# Función para obtener la tabla ARP en sistemas Windows
def obtener_tabla_arp():
    if sys.platform.startswith('win'):  # Verificar si el sistema es Windows
        try:
            salida_arp = subprocess.check_output(['arp', '-a']).decode('latin-1')  # Ejecutar el comando ARP
            lineas = salida_arp.splitlines()  # Dividir la salida en líneas
            entradas = []  # Lista para almacenar las direcciones MAC
            for linea in lineas:  # Iterar sobre cada línea
                partes = linea.split()  # Dividir la línea en partes
                # Validar que la línea contenga una dirección IP y una MAC
                if len(partes) >= 3 and re.match(r'([0-9]{1,3}\.){3}[0-9]{1,3}', partes[0]) and re.match(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', partes[1]):
                    mac = partes[1]  # Obtener la dirección MAC
                    entradas.append(mac)  # Agregar a la lista de entradas
            return entradas  # Retornar la lista de direcciones MAC
        except FileNotFoundError:
            print("Error: Comando 'arp' no encontrado en Windows.")  # Manejo de error si el comando no se encuentra
            return []
    else:
        print("Error: Esta funcionalidad solo está disponible en Windows.")  # Mensaje de error para otros sistemas
        return []

# Función para imprimir instrucciones de uso
def imprimir_uso():
    print("Use: python OUILookup.py --mac <mac> | --arp | [--help]")  # Instrucciones generales
    print("--mac: MAC a consultar. P.e. aa:bb:cc:00:00:00.")  # Ejemplo de uso
    print("--arp: muestra los fabricantes de los host disponibles en la tabla arp.")  # Descripción de la opción ARP
    print("--help: muestra este mensaje y termina.")  # Descripción de la opción de ayuda

# Función para normalizar la dirección MAC
def normalizar_mac(mac):
    mac_limpia = re.sub(r'[.:-]', '', mac.lower())  # Eliminar caracteres no alfanuméricos
    if len(mac_limpia) == 6:  # Verificar longitud
        mac_limpia = mac_limpia * 2  # Duplicar si es necesario
    return ':'.join([mac_limpia[i:i+2] for i in range(0, 12, 2)])  # Formatear la MAC

# Función para imprimir el resultado de la consulta
def imprimir_resultado_mac(mac, fabricante, tiempo_respuesta):
    print(f"MAC address : {mac}")  # Imprimir dirección MAC
    print(f"Fabricante : {fabricante}")  # Imprimir fabricante
    print(f"Tiempo de respuesta: {tiempo_respuesta}ms")  # Imprimir tiempo de respuesta

# Función principal
def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hm:a", ["help", "mac=", "arp"])  # Procesar argumentos de línea de comandos
    except getopt.GetoptError:
        imprimir_uso()  # Imprimir uso si hay error
        sys.exit(2)

    for opt, arg in opts:  # Iterar sobre las opciones
        if opt in ("-h", "--help"):
            imprimir_uso()  # Mostrar el uso
            sys.exit()
        elif opt in ("-m", "--mac"):
            mac_original = arg  # Obtener la MAC original
            mac_normalizada = normalizar_mac(arg)  # Normalizar la MAC
            fabricante, tiempo_respuesta = obtener_fabricante(mac_normalizada)  # Obtener fabricante
            imprimir_resultado_mac(mac_original, fabricante, tiempo_respuesta)  # Imprimir resultado
        elif opt in ("-a", "--arp"):
            entradas_arp = obtener_tabla_arp()  # Obtener entradas ARP
            if entradas_arp:
                print("MAC/Vendor:")  # Imprimir encabezado
                for mac in entradas_arp:  # Iterar sobre entradas ARP
                    fabricante, _ = obtener_fabricante(mac)  # Obtener fabricante
                    print(f"{mac} / {fabricante}")  # Imprimir MAC y fabricante
            else:
                print("No se encontraron entradas ARP o no se pudo recuperar la tabla ARP.")  # Mensaje si no hay entradas

if __name__ == "__main__":
    if len(sys.argv) == 1:  # Verificar si no hay argumentos
        imprimir_uso()  # Imprimir uso
    else:
        main(sys.argv[1:])  # Llamar a la función principal