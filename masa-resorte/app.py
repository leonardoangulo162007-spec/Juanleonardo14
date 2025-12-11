from flask import Flask, render_template, request, jsonify, send_file, Response
import numpy as np
from scipy.integrate import odeint
import matplotlib
matplotlib.use('Agg')  # Para generar gráficos sin interfaz gráfica
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import os
import io
import base64
import json
import time

# Importar módulo de comunicación con Arduino
from serial_handler import ArduinoHandler, listar_puertos_disponibles

app = Flask(__name__)

# ======================================================================
# Instancia Global de Arduino Handler
# ======================================================================
arduino = ArduinoHandler()
datos_experimentales = []  # Buffer para datos del experimento físico

# ======================================================================
# Funciones de Análisis (importadas del código original)
# ======================================================================

def analisis_estadistico(datos, t):
    """Realiza un análisis estadístico completo de las vibraciones"""
    stats = {
        'RMS': float(np.sqrt(np.mean(datos**2))),
        'Máximo': float(np.max(np.abs(datos))),
        'Mínimo': float(np.min(np.abs(datos))),
        'Media': float(np.mean(np.abs(datos))),
        'Desviación Estándar': float(np.std(datos)),
        'Factor de Cresta': float(np.max(np.abs(datos))/np.sqrt(np.mean(datos**2)))
    }
    return stats

def evaluar_riesgo(rms, max_amp):
    """
    Evalúa el nivel de riesgo según estándares ISO 10816 y 
    considerando impacto en salud humana y bienestar comunitario
    """
    # Conversión aproximada de m/s² a voltios del sensor (calibración típica)
    # Ajustar según calibración real del sensor
    
    if rms > 0.1:
        nivel = "ALTO RIESGO"
        color = "danger"
        descripcion = "⚠️ CRÍTICO: Vibraciones exceden límites seguros. Afectación significativa a la salud física, descanso y bienestar emocional. Requiere intervención inmediata."
        impacto_salud = "Posible daño a la salud: insomnio crónico, estrés elevado, fatiga constante, dolores de cabeza frecuentes, irritabilidad extrema."
        impacto_social = "Deterioro grave de la convivencia: conflictos vecinales, reducción de calidad de vida, afectación del rendimiento laboral/escolar."
        recomendacion = "ACCIÓN URGENTE: Contactar autoridades municipales, presentar este reporte como evidencia, solicitar inspección técnica y medidas de mitigación inmediatas."
    elif rms > 0.05:
        nivel = "PRECAUCIÓN"
        color = "warning"
        descripcion = "⚠️ MODERADO: Niveles de vibración en zona de advertencia. Pueden causar molestias significativas y afectación al descanso prolongado."
        impacto_salud = "Posible afectación: alteración del sueño, dificultad de concentración, molestias físicas leves, incremento de estrés."
        impacto_social = "Impacto moderado en convivencia: quejas vecinales justificadas, reducción de confort en el hogar."
        recomendacion = "Monitorear continuamente. Documentar horarios de mayor afectación. Organizar comité vecinal para presentar reclamo colectivo con evidencia técnica."
    else:
        nivel = "ACEPTABLE"
        color = "success"
        descripcion = "✓ SEGURO: Niveles de vibración dentro de rangos aceptables según normas internacionales. Bajo impacto en salud y bienestar."
        impacto_salud = "Sin riesgo significativo para la salud. Vibraciones no interfieren con el descanso ni actividades cotidianas."
        impacto_social = "Condiciones apropiadas para convivencia comunitaria saludable."
        recomendacion = "Mantener monitoreo preventivo. Registrar mediciones periódicas para detectar cambios futuros."
    
    return {
        'nivel': nivel,
        'color': color,
        'descripcion': descripcion,
        'advertencia_adicional': max_amp > 0.15,
        'impacto_salud': impacto_salud,
        'impacto_social': impacto_social,
        'recomendacion': recomendacion
    }

def sistema_masa_resorte(y, t, m, k, c, F0, w_fuerza):
    """Define el sistema de ecuaciones diferenciales de primer orden."""
    F_externa = F0 * np.cos(w_fuerza * t)
    x, v = y
    dvdt = (F_externa - c * v - k * x) / m
    dxdt = v
    return [dxdt, dvdt]

def generar_graficas(t, sol_normal, sol_resonancia, aceleracion, w_normal, w_resonancia, f_n):
    """Genera las gráficas y las devuelve como imágenes base64"""
    plt.figure(figsize=(15, 8))
    
    # Gráfica 1: Vibración Normal
    plt.subplot(2, 2, 1)
    plt.plot(t, sol_normal[:, 0], 'b-', linewidth=2)
    plt.title(f'Vibración Normal\n(f_fuerza = {w_normal/(2*np.pi):.2f} Hz)', fontsize=12, fontweight='bold')
    plt.xlabel('Tiempo (s)', fontsize=10)
    plt.ylabel('Desplazamiento (m)', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Gráfica 2: Resonancia
    plt.subplot(2, 2, 2)
    plt.plot(t, sol_resonancia[:, 0], 'r-', linewidth=2)
    plt.title(f'Resonancia\n(f_fuerza ≈ {f_n:.2f} Hz)', fontsize=12, fontweight='bold')
    plt.xlabel('Tiempo (s)', fontsize=10)
    plt.ylabel('Desplazamiento (m)', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Gráfica 3: Aceleración durante Resonancia
    plt.subplot(2, 2, (3, 4))
    plt.plot(t, aceleracion, 'k-', linewidth=2)
    plt.title('Aceleración durante Resonancia - Monitoreo de Vibraciones', fontsize=12, fontweight='bold')
    plt.xlabel('Tiempo (s)', fontsize=10)
    plt.ylabel('Aceleración (m/s²)', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    
    # Convertir a base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return image_base64

# ======================================================================
# Rutas de la aplicación
# ======================================================================

@app.route('/')
def index():
    """Página principal con formulario de entrada"""
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    """Procesa los datos y realiza el análisis"""
    try:
        # Obtener parámetros del formulario
        m = float(request.form.get('masa', 1.0))
        k = float(request.form.get('constante_resorte', 100.0))
        c = float(request.form.get('amortiguamiento', 1.0))
        F0 = float(request.form.get('fuerza', 5.0))
        
        # Validación de parámetros
        if m <= 0 or k <= 0 or c < 0 or F0 <= 0:
            return jsonify({'error': 'Los parámetros deben ser valores positivos'}), 400
        
        # Cálculos preliminares
        w_n = np.sqrt(k / m)
        f_n = w_n / (2 * np.pi)
        
        # Parámetros de simulación
        t_max = 20.0
        n_puntos = 1000
        t = np.linspace(0, t_max, n_puntos)
        y0 = [0.0, 0.0]
        
        # Simulación de escenarios
        w_normal = w_n / 2
        w_resonancia = w_n * 0.999
        
        sol_normal = odeint(sistema_masa_resorte, y0, t, args=(m, k, c, F0, w_normal))
        sol_resonancia = odeint(sistema_masa_resorte, y0, t, args=(m, k, c, F0, w_resonancia))
        
        # Cálculo de aceleración
        aceleracion = (F0 * np.cos(w_resonancia * t) - c * sol_resonancia[:, 1] - k * sol_resonancia[:, 0]) / m
        
        # Análisis estadístico
        stats_normal = analisis_estadistico(sol_normal[:, 0], t)
        stats_resonancia = analisis_estadistico(sol_resonancia[:, 0], t)
        stats_aceleracion = analisis_estadistico(aceleracion, t)
        
        # Evaluación de riesgo
        riesgo = evaluar_riesgo(stats_resonancia['RMS'], stats_resonancia['Máximo'])
        
        # Generar gráficas
        imagen_graficas = generar_graficas(t, sol_normal, sol_resonancia, aceleracion, 
                                          w_normal, w_resonancia, f_n)
        
        # Calcular factor de amortiguamiento
        factor_amort = c / (2 * np.sqrt(m * k))
        tipo_amort = "Subamortiguado" if factor_amort < 1 else "Sobreamortiguado" if factor_amort > 1 else "Amortiguamiento Crítico"
        
        # Preparar respuesta
        resultados = {
            'parametros': {
                'masa': m,
                'constante_resorte': k,
                'amortiguamiento': c,
                'fuerza': F0,
                'frecuencia_natural': round(f_n, 2),
                'frecuencia_angular': round(w_n, 2),
                'factor_amortiguamiento': round(factor_amort, 3),
                'tipo_amortiguamiento': tipo_amort
            },
            'stats_normal': stats_normal,
            'stats_resonancia': stats_resonancia,
            'stats_aceleracion': stats_aceleracion,
            'riesgo': riesgo,
            'imagen_graficas': imagen_graficas,
            'amplificacion_rms': round(stats_resonancia['RMS'] / stats_normal['RMS'], 1),
            'amplificacion_max': round(stats_resonancia['Máximo'] / stats_normal['Máximo'], 1)
        }
        
        # Guardar datos si se solicita
        if request.form.get('guardar_datos') == 'true':
            exportar_datos(t, sol_normal, sol_resonancia, aceleracion, m, k, c, F0)
        
        return jsonify(resultados)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def exportar_datos(t, sol_normal, sol_resonancia, aceleracion, m, k, c, F0):
    """Exporta los datos a archivos Excel"""
    folder = 'resultados'
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    df = pd.DataFrame({
        'Tiempo': t,
        'Desplazamiento_Normal': sol_normal[:, 0],
        'Velocidad_Normal': sol_normal[:, 1],
        'Desplazamiento_Resonancia': sol_resonancia[:, 0],
        'Velocidad_Resonancia': sol_resonancia[:, 1],
        'Aceleracion_Resonancia': aceleracion
    })
    
    fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_file = os.path.join(folder, f'datos_vibracion_{fecha}.xlsx')
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Datos', index=False)
        
        # Hoja con parámetros
        df_params = pd.DataFrame({
            'Parámetro': ['Masa (kg)', 'Constante del resorte (N/m)', 
                         'Amortiguamiento (N·s/m)', 'Fuerza (N)'],
            'Valor': [m, k, c, F0]
        })
        df_params.to_excel(writer, sheet_name='Parametros', index=False)

# ======================================================================
# RUTAS PARA INTEGRACIÓN CON ARDUINO
# ======================================================================

@app.route('/arduino/puertos')
def listar_puertos():
    """Lista puertos COM disponibles"""
    try:
        puertos = listar_puertos_disponibles()
        return jsonify({
            'success': True,
            'puertos': [{'puerto': p[0], 'descripcion': p[1]} for p in puertos]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/arduino/conectar', methods=['POST'])
def conectar_arduino():
    """Conecta con Arduino en el puerto especificado"""
    try:
        puerto = request.json.get('puerto', None)
        
        if arduino.conectar(puerto):
            arduino.iniciar_captura()
            return jsonify({
                'success': True,
                'mensaje': f'Conectado a {arduino.puerto}',
                'puerto': arduino.puerto
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo conectar con Arduino'
            }), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/arduino/desconectar', methods=['POST'])
def desconectar_arduino():
    """Desconecta Arduino"""
    try:
        arduino.desconectar()
        global datos_experimentales
        datos_experimentales = []
        return jsonify({'success': True, 'mensaje': 'Arduino desconectado'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/arduino/estado')
def estado_arduino():
    """Obtiene el estado de la conexión con Arduino"""
    try:
        stats = arduino.obtener_estadisticas()
        return jsonify({
            'success': True,
            'estado': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/arduino/stream')
def stream_datos():
    """Stream de datos en tiempo real usando Server-Sent Events (SSE)"""
    def generar_datos():
        while arduino.esta_conectado():
            dato = arduino.obtener_dato(timeout=0.5)
            if dato:
                yield f"data: {json.dumps(dato)}\n\n"
            else:
                # Enviar heartbeat si no hay datos
                yield f"data: {json.dumps({'heartbeat': True})}\n\n"
            time.sleep(0.1)
    
    return Response(generar_datos(), mimetype='text/event-stream')

@app.route('/arduino/iniciar_experimento', methods=['POST'])
def iniciar_experimento():
    """Inicia captura de datos experimentales"""
    try:
        duracion = int(request.json.get('duracion', 30))  # segundos
        
        global datos_experimentales
        datos_experimentales = []
        
        arduino.vaciar_buffer()
        
        return jsonify({
            'success': True,
            'mensaje': f'Experimento iniciado. Capturando por {duracion} segundos',
            'duracion': duracion
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/arduino/obtener_datos')
def obtener_datos_experimento():
    """Obtiene datos capturados del experimento"""
    try:
        cantidad = int(request.args.get('cantidad', 50))
        datos = arduino.obtener_lote_datos(cantidad=cantidad, timeout=10)
        
        global datos_experimentales
        datos_experimentales.extend(datos)
        
        return jsonify({
            'success': True,
            'datos': datos,
            'total_capturados': len(datos_experimentales)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/arduino/analizar_experimento', methods=['POST'])
def analizar_experimento():
    """Analiza datos experimentales capturados"""
    try:
        global datos_experimentales
        
        if not datos_experimentales:
            return jsonify({
                'success': False,
                'error': 'No hay datos experimentales disponibles'
            }), 400
        
        # Extraer valores
        rms_vals = [d.get('rms', 0) for d in datos_experimentales]
        max_vals = [d.get('max', 0) for d in datos_experimentales]
        min_vals = [d.get('min', 0) for d in datos_experimentales]
        std_vals = [d.get('std', 0) for d in datos_experimentales]
        crest_vals = [d.get('crest', 0) for d in datos_experimentales]
        
        # Estadísticas del experimento
        stats_experimental = {
            'RMS': {
                'media': float(np.mean(rms_vals)),
                'max': float(np.max(rms_vals)),
                'min': float(np.min(rms_vals)),
                'std': float(np.std(rms_vals))
            },
            'Amplitud_Maxima': {
                'media': float(np.mean(max_vals)),
                'max': float(np.max(max_vals)),
                'min': float(np.min(max_vals)),
                'std': float(np.std(max_vals))
            },
            'Factor_Cresta': {
                'media': float(np.mean(crest_vals)),
                'max': float(np.max(crest_vals)),
                'min': float(np.min(crest_vals)),
                'std': float(np.std(crest_vals))
            },
            'Desviacion_Estandar': {
                'media': float(np.mean(std_vals)),
                'max': float(np.max(std_vals)),
                'min': float(np.min(std_vals))
            }
        }
        
        # Evaluar riesgo
        rms_medio = stats_experimental['RMS']['media']
        max_medio = stats_experimental['Amplitud_Maxima']['max']
        riesgo = evaluar_riesgo(rms_medio, max_medio)
        
        # Detectar resonancia
        crest_medio = stats_experimental['Factor_Cresta']['media']
        en_resonancia = crest_medio > 3.0
        
        # Generar gráfica
        imagen_grafica = generar_grafica_experimental(
            rms_vals, max_vals, crest_vals, std_vals
        )
        
        # Exportar datos si se solicita
        if request.json.get('guardar_datos', False):
            exportar_datos_experimentales(datos_experimentales)
        
        return jsonify({
            'success': True,
            'estadisticas': stats_experimental,
            'riesgo': riesgo,
            'en_resonancia': en_resonancia,
            'num_muestras': len(datos_experimentales),
            'imagen_grafica': imagen_grafica
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def generar_grafica_experimental(rms_vals, max_vals, crest_vals, std_vals):
    """Genera gráfica de datos experimentales"""
    plt.figure(figsize=(15, 10))
    
    # Crear índice de tiempo
    n_samples = len(rms_vals)
    tiempo = np.arange(n_samples) * 0.1  # 0.1s entre muestras
    
    # Gráfica 1: RMS
    plt.subplot(2, 2, 1)
    plt.plot(tiempo, rms_vals, 'b-', linewidth=1.5)
    plt.title('Valor RMS en Tiempo Real', fontsize=12, fontweight='bold')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('RMS (V)')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=np.mean(rms_vals), color='r', linestyle='--', label=f'Media: {np.mean(rms_vals):.4f}')
    plt.legend()
    
    # Gráfica 2: Amplitud Máxima
    plt.subplot(2, 2, 2)
    plt.plot(tiempo, max_vals, 'r-', linewidth=1.5)
    plt.title('Amplitud Máxima', fontsize=12, fontweight='bold')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Amplitud (V)')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=np.mean(max_vals), color='b', linestyle='--', label=f'Media: {np.mean(max_vals):.4f}')
    plt.legend()
    
    # Gráfica 3: Factor de Cresta
    plt.subplot(2, 2, 3)
    plt.plot(tiempo, crest_vals, 'g-', linewidth=1.5)
    plt.axhline(y=3.0, color='r', linestyle='--', linewidth=2, label='Umbral Resonancia')
    plt.title('Factor de Cresta (Detección de Resonancia)', fontsize=12, fontweight='bold')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Factor de Cresta')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Gráfica 4: Histograma RMS
    plt.subplot(2, 2, 4)
    plt.hist(rms_vals, bins=30, color='blue', alpha=0.7, edgecolor='black')
    plt.title('Distribución de Valores RMS', fontsize=12, fontweight='bold')
    plt.xlabel('RMS (V)')
    plt.ylabel('Frecuencia')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Convertir a base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return image_base64

def exportar_datos_experimentales(datos):
    """Exporta datos experimentales a Excel"""
    folder = 'resultados'
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Preparar datos para DataFrame
    datos_formateados = []
    for d in datos:
        datos_formateados.append({
            'Timestamp': d.get('timestamp_local', ''),
            'RMS (V)': d.get('rms', 0),
            'Amplitud_Max (V)': d.get('max', 0),
            'Amplitud_Min (V)': d.get('min', 0),
            'Media (V)': d.get('media', 0),
            'Desv_Estandar (V)': d.get('std', 0),
            'Factor_Cresta': d.get('crest', 0),
            'Timestamp_Arduino (ms)': d.get('timestamp', 0)
        })
    
    df = pd.DataFrame(datos_formateados)
    
    fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_file = os.path.join(folder, f'datos_experimentales_{fecha}.xlsx')
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Datos_Experimentales', index=False)
        
        # Hoja con estadísticas
        stats_df = pd.DataFrame({
            'Parámetro': ['Número de muestras', 'Duración total (s)', 
                         'RMS promedio (V)', 'Amplitud máxima (V)'],
            'Valor': [
                len(datos),
                len(datos) * 0.1,
                df['RMS (V)'].mean(),
                df['Amplitud_Max (V)'].max()
            ]
        })
        stats_df.to_excel(writer, sheet_name='Estadisticas', index=False)
    
    print(f"✓ Datos experimentales exportados a {excel_file}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)

