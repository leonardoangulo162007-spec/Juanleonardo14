"""
================================================================================
MÓDULO DE COMUNICACIÓN SERIAL CON ARDUINO
Proyecto: Análisis de Resonancia en Sistema Masa-Resorte
================================================================================

Este módulo maneja la comunicación serial con Arduino UNO para capturar
datos del sensor piezoeléctrico en tiempo real.

Funcionalidades:
- Detección automática de puerto COM en Windows
- Lectura continua de datos JSON desde Arduino
- Buffer thread-safe para datos en tiempo real
- Manejo robusto de errores y reconexión
================================================================================
"""

import serial
import serial.tools.list_ports
import json
import threading
import queue
import time
from datetime import datetime


class ArduinoHandler:
    """
    Manejador de comunicación serial con Arduino
    """
    
    def __init__(self, baudrate=115200, timeout=1):
        """
        Inicializa el manejador de Arduino
        
        Args:
            baudrate: Velocidad de comunicación (default: 115200)
            timeout: Timeout para lectura serial (default: 1 segundo)
        """
        self.baudrate = baudrate
        self.timeout = timeout
        self.puerto = None
        self.serial_conn = None
        self.conectado = False
        
        # Buffer thread-safe para datos
        self.buffer_datos = queue.Queue(maxsize=1000)
        
        # Control de hilos
        self.hilo_lectura = None
        self.capturando = False
        self.lock = threading.Lock()
        
        # Estadísticas
        self.paquetes_recibidos = 0
        self.paquetes_perdidos = 0
        self.ultimo_timestamp = 0
    
    def detectar_arduino(self):
        """
        Detecta automáticamente el puerto COM del Arduino en Windows
        
        Returns:
            str: Puerto COM detectado o None si no se encuentra
        """
        puertos = serial.tools.list_ports.comports()
        
        for puerto in puertos:
            # Arduino UNO típicamente se identifica como "USB Serial"
            if 'Arduino' in puerto.description or 'USB' in puerto.description:
                print(f"✓ Arduino detectado en {puerto.device}: {puerto.description}")
                return puerto.device
        
        # Si no encuentra por descripción, listar todos los puertos COM
        if puertos:
            print("\n⚠️  Arduino no detectado automáticamente.")
            print("Puertos disponibles:")
            for i, puerto in enumerate(puertos, 1):
                print(f"  {i}. {puerto.device} - {puerto.description}")
            
            try:
                seleccion = int(input("\nSelecciona el número del puerto (0 para cancelar): "))
                if 0 < seleccion <= len(puertos):
                    return puertos[seleccion - 1].device
            except (ValueError, IndexError):
                pass
        
        print("✗ No se detectaron puertos COM disponibles")
        return None
    
    def conectar(self, puerto=None):
        """
        Establece conexión con Arduino
        
        Args:
            puerto: Puerto COM específico (ej: 'COM3'). Si es None, detecta automáticamente
            
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            # Detectar puerto si no se especifica
            if puerto is None:
                puerto = self.detectar_arduino()
                if puerto is None:
                    return False
            
            self.puerto = puerto
            
            # Intentar conexión
            print(f"\n🔌 Conectando a {puerto} a {self.baudrate} baudios...")
            self.serial_conn = serial.Serial(
                port=puerto,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # Esperar inicialización de Arduino
            time.sleep(2)
            
            # Limpiar buffer
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()
            
            self.conectado = True
            print(f"✓ Conexión establecida con Arduino en {puerto}")
            
            # Leer mensaje de inicio
            time.sleep(0.5)
            if self.serial_conn.in_waiting:
                linea = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                print(f"📡 Arduino dice: {linea}")
            
            return True
            
        except serial.SerialException as e:
            print(f"✗ Error de conexión serial: {e}")
            self.conectado = False
            return False
        except Exception as e:
            print(f"✗ Error inesperado: {e}")
            self.conectado = False
            return False
    
    def desconectar(self):
        """
        Cierra la conexión serial de forma segura
        """
        self.detener_captura()
        
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.conectado = False
            print("✓ Conexión cerrada")
    
    def leer_dato(self):
        """
        Lee un paquete JSON desde Arduino
        
        Returns:
            dict: Datos parseados o None si hay error
        """
        try:
            if not self.serial_conn or not self.serial_conn.is_open:
                return None
            
            if self.serial_conn.in_waiting:
                linea = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                
                # Parsear JSON
                if linea.startswith('{') and linea.endswith('}'):
                    dato = json.loads(linea)
                    
                    # Agregar timestamp local
                    dato['timestamp_local'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    
                    self.paquetes_recibidos += 1
                    return dato
                    
        except json.JSONDecodeError:
            self.paquetes_perdidos += 1
            return None
        except Exception as e:
            print(f"Error en lectura: {e}")
            return None
        
        return None
    
    def _captura_continua(self):
        """
        Función interna para captura continua en hilo separado
        """
        print("▶ Captura iniciada en segundo plano")
        
        while self.capturando:
            try:
                dato = self.leer_dato()
                
                if dato:
                    # Agregar al buffer si no está lleno
                    try:
                        self.buffer_datos.put_nowait(dato)
                    except queue.Full:
                        # Buffer lleno, descartar dato más antiguo
                        try:
                            self.buffer_datos.get_nowait()
                            self.buffer_datos.put_nowait(dato)
                        except:
                            pass
                
                # Pequeña pausa para no saturar CPU
                time.sleep(0.001)
                
            except Exception as e:
                print(f"Error en captura continua: {e}")
                time.sleep(0.1)
    
    def iniciar_captura(self):
        """
        Inicia la captura continua de datos en un hilo separado
        
        Returns:
            bool: True si se inició correctamente
        """
        if not self.conectado:
            print("✗ No hay conexión con Arduino")
            return False
        
        if self.capturando:
            print("⚠️  La captura ya está activa")
            return True
        
        self.capturando = True
        self.hilo_lectura = threading.Thread(target=self._captura_continua, daemon=True)
        self.hilo_lectura.start()
        
        return True
    
    def detener_captura(self):
        """
        Detiene la captura continua
        """
        if self.capturando:
            self.capturando = False
            if self.hilo_lectura:
                self.hilo_lectura.join(timeout=2)
            print("⏸ Captura detenida")
    
    def obtener_dato(self, timeout=0.1):
        """
        Obtiene el siguiente dato del buffer
        
        Args:
            timeout: Tiempo máximo de espera en segundos
            
        Returns:
            dict: Dato del sensor o None si no hay datos disponibles
        """
        try:
            return self.buffer_datos.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def obtener_lote_datos(self, cantidad=10, timeout=5):
        """
        Obtiene un lote de datos del buffer
        
        Args:
            cantidad: Número de datos a obtener
            timeout: Tiempo máximo total de espera
            
        Returns:
            list: Lista de datos capturados
        """
        datos = []
        tiempo_inicio = time.time()
        
        while len(datos) < cantidad and (time.time() - tiempo_inicio) < timeout:
            dato = self.obtener_dato(timeout=0.1)
            if dato:
                datos.append(dato)
        
        return datos
    
    def vaciar_buffer(self):
        """
        Vacía el buffer de datos
        """
        while not self.buffer_datos.empty():
            try:
                self.buffer_datos.get_nowait()
            except queue.Empty:
                break
    
    def obtener_estadisticas(self):
        """
        Obtiene estadísticas de la conexión
        
        Returns:
            dict: Estadísticas de conexión y captura
        """
        return {
            'conectado': self.conectado,
            'puerto': self.puerto,
            'capturando': self.capturando,
            'paquetes_recibidos': self.paquetes_recibidos,
            'paquetes_perdidos': self.paquetes_perdidos,
            'buffer_size': self.buffer_datos.qsize(),
            'tasa_perdida': (self.paquetes_perdidos / max(1, self.paquetes_recibidos + self.paquetes_perdidos)) * 100
        }
    
    def esta_conectado(self):
        """
        Verifica si Arduino está conectado y respondiendo
        
        Returns:
            bool: True si está conectado
        """
        return self.conectado and self.serial_conn and self.serial_conn.is_open


# ============ FUNCIONES DE UTILIDAD ============

def listar_puertos_disponibles():
    """
    Lista todos los puertos COM disponibles en Windows
    
    Returns:
        list: Lista de tuplas (puerto, descripción)
    """
    puertos = serial.tools.list_ports.comports()
    return [(p.device, p.description) for p in puertos]


def test_conexion(puerto=None):
    """
    Prueba rápida de conexión con Arduino
    
    Args:
        puerto: Puerto COM a probar (None para autodetección)
    """
    print("\n" + "="*60)
    print("TEST DE CONEXIÓN CON ARDUINO")
    print("="*60)
    
    handler = ArduinoHandler()
    
    if handler.conectar(puerto):
        print("\n✓ Conexión exitosa")
        print("Capturando 10 muestras de prueba...")
        
        handler.iniciar_captura()
        
        for i in range(10):
            dato = handler.obtener_dato(timeout=2)
            if dato:
                print(f"\nMuestra {i+1}:")
                print(f"  RMS: {dato.get('rms', 0):.4f} V")
                print(f"  Amplitud Máx: {dato.get('max', 0):.4f} V")
                print(f"  Factor Cresta: {dato.get('crest', 0):.2f}")
            else:
                print(f"✗ No se recibió dato {i+1}")
        
        stats = handler.obtener_estadisticas()
        print(f"\n📊 Estadísticas:")
        print(f"  Paquetes recibidos: {stats['paquetes_recibidos']}")
        print(f"  Paquetes perdidos: {stats['paquetes_perdidos']}")
        print(f"  Tasa de pérdida: {stats['tasa_perdida']:.2f}%")
        
        handler.desconectar()
        return True
    else:
        print("\n✗ No se pudo establecer conexión")
        return False


if __name__ == "__main__":
    # Ejecutar test de conexión
    test_conexion()
