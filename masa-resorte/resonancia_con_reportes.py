import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import os

# ======================================================================
# 1. Funciones de Análisis y Reportes
# ======================================================================

def analisis_estadistico(datos, t):
    """
    Realiza un análisis estadístico completo de las vibraciones
    """
    stats = {
        'RMS': np.sqrt(np.mean(datos**2)),
        'Máximo': np.max(np.abs(datos)),
        'Mínimo': np.min(np.abs(datos)),
        'Media': np.mean(np.abs(datos)),
        'Desviación Estándar': np.std(datos),
        'Factor de Cresta': np.max(np.abs(datos))/np.sqrt(np.mean(datos**2))
    }
    return stats

def evaluar_riesgo(rms, max_amp):
    """
    Evalúa el nivel de riesgo según estándares típicos de vibración
    """
    mensaje = "EVALUACIÓN DETALLADA DEL RIESGO:\n    "
    
    # Evaluación basada en RMS
    if rms > 0.1:
        mensaje += """NIVEL DE RIESGO: ALTO
    - Las vibraciones exceden significativamente los límites seguros
    - Posible daño inmediato a equipos sensibles
    - Se requiere acción correctiva inmediata
    - Recomendación: Detener operación o reducir amplitud de fuerza"""
    elif rms > 0.05:
        mensaje += """NIVEL DE RIESGO: PRECAUCIÓN
    - Niveles de vibración en zona de advertencia
    - Posible afectación a equipos sensibles a largo plazo
    - Se recomienda monitoreo continuo
    - Considerar medidas de mitigación preventivas"""
    else:
        mensaje += """NIVEL DE RIESGO: SEGURO
    - Niveles de vibración dentro de rangos aceptables
    - No se esperan efectos adversos en equipos
    - Continuar con monitoreo regular
    - Mantener registro de tendencias"""
    
    # Añadir recomendaciones específicas
    if max_amp > 0.15:
        mensaje += """\n\nADVERTENCIA ADICIONAL:
    - Picos de amplitud excesivos detectados
    - Riesgo de impactos o golpes
    - Revisar sistema de amortiguamiento
    - Considerar reducir la fuerza de excitación"""
    
    return mensaje

def generar_reporte_detallado(parametros, stats_normal, stats_resonancia, aceleracion_stats):
    """
    Genera un reporte detallado del análisis de vibraciones con explicaciones y comparaciones
    """
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Cálculos adicionales para comparaciones
    amplificacion_rms = stats_resonancia['RMS'] / stats_normal['RMS']
    amplificacion_max = stats_resonancia['Máximo'] / stats_normal['Máximo']
    
    # Evaluación del amortiguamiento
    factor_amort = parametros['c'] / (2 * np.sqrt(parametros['m'] * parametros['k']))
    tipo_amort = "Subamortiguado" if factor_amort < 1 else "Sobreamortiguado" if factor_amort > 1 else "Amortiguamiento Crítico"
    
    reporte = f"""
    ================================================================================
                            REPORTE DE ANÁLISIS DE VIBRACIONES
    ================================================================================
    Fecha y Hora del Análisis: {fecha}
    
    1. CARACTERÍSTICAS DEL SISTEMA Y PARÁMETROS FÍSICOS
    ================================================
    Parámetros Principales:
    - Masa del sistema: {parametros['m']:.2f} kg
    - Constante del resorte: {parametros['k']:.2f} N/m
    - Coeficiente de amortiguamiento: {parametros['c']:.2f} N·s/m
    - Amplitud de la fuerza externa: {parametros['F0']:.2f} N
    
    Características Dinámicas:
    - Frecuencia natural: {parametros['f_n']:.2f} Hz
    - Factor de amortiguamiento: {factor_amort:.3f}
    - Tipo de amortiguamiento: {tipo_amort}
    
    2. ANÁLISIS EN CONDICIONES NORMALES (Operación Segura)
    ==================================================
    Desplazamiento:
    - RMS: {stats_normal['RMS']:.4f} m
        → Indica el nivel típico de vibración durante operación normal
    - Amplitud máxima: {stats_normal['Máximo']:.4f} m
        → Pico máximo de desplazamiento en operación normal
    - Factor de cresta: {stats_normal['Factor de Cresta']:.2f}
        → Relación entre picos y nivel promedio
    - Desviación estándar: {stats_normal['Desviación Estándar']:.4f} m
        → Variabilidad del movimiento
    
    3. ANÁLISIS EN RESONANCIA (Condición Crítica)
    =========================================
    Desplazamiento:
    - RMS: {stats_resonancia['RMS']:.4f} m
        → {amplificacion_rms:.1f} veces mayor que en operación normal
    - Amplitud máxima: {stats_resonancia['Máximo']:.4f} m
        → {amplificacion_max:.1f} veces mayor que en operación normal
    - Factor de cresta: {stats_resonancia['Factor de Cresta']:.2f}
        → Comparado con {stats_normal['Factor de Cresta']:.2f} en operación normal
    - Desviación estándar: {stats_resonancia['Desviación Estándar']:.4f} m
        → Indica mayor variabilidad en resonancia
    
    4. ANÁLISIS DE ACELERACIÓN (Impacto en Equipos)
    ==========================================
    Características de Aceleración:
    - RMS: {aceleracion_stats['RMS']:.4f} m/s² ({aceleracion_stats['RMS']/9.81:.2f} g)
        → Nivel de vibración efectivo que afecta a los equipos
    - Aceleración máxima: {aceleracion_stats['Máximo']:.4f} m/s² ({aceleracion_stats['Máximo']/9.81:.2f} g)
        → Pico máximo de fuerza que experimentan los equipos
    - Factor de cresta: {aceleracion_stats['Factor de Cresta']:.2f}
        → Indica la naturaleza impulsiva de las vibraciones
    
    5. EVALUACIÓN DE RIESGO Y RECOMENDACIONES
    ======================================
    {evaluar_riesgo(stats_resonancia['RMS'], stats_resonancia['Máximo'])}
    
    Límites de Referencia para Equipos Sensibles:
    - Microscopios y equipos ópticos: < 0.5 m/s² RMS
    - Equipos de laboratorio general: < 1.0 m/s² RMS
    - Servidores y equipos electrónicos: < 2.0 m/s² RMS
    
    Comparación con Límites:
    - Nivel actual RMS: {aceleracion_stats['RMS']:.2f} m/s²
    - Estado: {'EXCEDE' if aceleracion_stats['RMS'] > 2.0 else 'PRECAUCIÓN' if aceleracion_stats['RMS'] > 1.0 else 'ACEPTABLE'}
    """
    return reporte

def exportar_datos(t, sol_normal, sol_resonancia, aceleracion, folder='resultados'):
    """
    Exporta los datos a archivos Excel y el reporte en formato txt
    """
    # Crear carpeta si no existe
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    # Exportar datos principales
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
    df.to_excel(excel_file, index=False)
    print(f"\nDatos exportados a {excel_file}")

# ======================================================================
# 2. Definición de la Ecuación Diferencial
# ======================================================================

def sistema_masa_resorte(y, t, m, k, c, F0, w_fuerza):
    """
    Define el sistema de ecuaciones diferenciales de primer orden.
    """
    F_externa = F0 * np.cos(w_fuerza * t)
    x, v = y
    dvdt = (F_externa - c * v - k * x) / m
    dxdt = v
    return [dxdt, dvdt]

# ======================================================================
# 3. Programa Principal
# ======================================================================

def main():
    # Entrada de parámetros
    print("\n=== Ingrese los parámetros del sistema (o presione Enter para valores por defecto) ===")
    m_input = input("Ingrese la masa en kg [1.0]: ").strip()
    k_input = input("Ingrese la constante del resorte en N/m [100.0]: ").strip()
    c_input = input("Ingrese el coeficiente de amortiguamiento en N*s/m [1.0]: ").strip()
    F0_input = input("Ingrese la amplitud de la fuerza de excitación en N [5.0]: ").strip()

    # Asignación de valores con manejo de errores
    try:
        m = float(m_input) if m_input else 1.0
    except ValueError:
        print("Valor inválido para masa, usando 1.0 kg")
        m = 1.0

    try:
        k = float(k_input) if k_input else 100.0
    except ValueError:
        print("Valor inválido para constante del resorte, usando 100.0 N/m")
        k = 100.0

    try:
        c = float(c_input) if c_input else 1.0
    except ValueError:
        print("Valor inválido para amortiguamiento, usando 1.0 N*s/m")
        c = 1.0

    try:
        F0 = float(F0_input) if F0_input else 5.0
    except ValueError:
        print("Valor inválido para fuerza de excitación, usando 5.0 N")
        F0 = 5.0

    # Cálculos preliminares
    w_n = np.sqrt(k / m)
    f_n = w_n / (2 * np.pi)
    print(f"\nFrecuencia natural (w_n): {w_n:.2f} rad/s")
    print(f"Frecuencia natural (f_n): {f_n:.2f} Hz")

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
    parametros = {
        'm': m, 
        'k': k, 
        'c': c, 
        'F0': F0,
        'f_n': f_n
    }

    stats_normal = analisis_estadistico(sol_normal[:, 0], t)
    stats_resonancia = analisis_estadistico(sol_resonancia[:, 0], t)
    stats_aceleracion = analisis_estadistico(aceleracion, t)

    # Generar reporte
    reporte = generar_reporte_detallado(parametros, stats_normal, stats_resonancia, stats_aceleracion)
    
    # Guardar reporte
    fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
    if not os.path.exists('resultados'):
        os.makedirs('resultados')
    
    with open(f'resultados/reporte_{fecha}.txt', 'w', encoding='utf-8') as f:
        f.write(reporte)
    
    print("\nReporte generado:")
    print(reporte)

    # Exportar datos
    exportar_datos(t, sol_normal, sol_resonancia, aceleracion)

    # Visualización
    plt.figure(figsize=(15, 8))

    # Gráfica 1: Vibración Normal
    plt.subplot(2, 2, 1)
    plt.plot(t, sol_normal[:, 0], label='Desplazamiento (x)')
    plt.title(f'Vibración Normal\n(f_fuerza = {w_normal/(2*np.pi):.2f} Hz)')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Desplazamiento (m)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()

    # Gráfica 2: Resonancia
    plt.subplot(2, 2, 2)
    plt.plot(t, sol_resonancia[:, 0], 'r', label='Desplazamiento (x)')
    plt.title(f'Resonancia\n(f_fuerza ≈ {f_n:.2f} Hz)')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Desplazamiento (m)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()

    # Gráfica 3: Aceleración durante Resonancia
    plt.subplot(2, 2, (3, 4))
    plt.plot(t, aceleracion, 'k', label='Aceleración')
    plt.title('Aceleración durante Resonancia - Monitoreo de Vibraciones')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Aceleración ($m/s^2$)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()