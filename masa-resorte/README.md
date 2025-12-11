# Sistema de Monitoreo y Análisis de Vibraciones Ambientales

## 🎯 Objetivo General
Desarrollar un sistema de monitoreo y análisis de vibraciones ambientales que permita identificar, registrar y evidenciar el impacto de dichas vibraciones en la **salud física**, el **bienestar emocional** y la **convivencia social** de las personas expuestas.

## 📋 Objetivos Específicos

1. **Diseñar e implementar** un sistema de medición de vibraciones utilizando sensores adecuados que permitan capturar datos reales en diferentes contextos comunitarios.

2. **Analizar** los niveles de vibración obtenidos y relacionarlos con indicadores de afectación física, descanso y bienestar emocional.

3. **Generar** gráficos comparativos y reportes visuales que faciliten la interpretación comunitaria y el respaldo de reclamos sociales.

4. **Proponer** estrategias de prevención o mitigación basadas en los resultados obtenidos.

5. **Fomentar** una cultura de conciencia y participación comunitaria en torno a los efectos de las vibraciones ambientales.

## 🏘️ Realidad Problemática

### Contexto Social
En la actualidad, distintas **comunidades urbanas y residenciales** conviven con vibraciones ambientales generadas por:
- 🏗️ Construcciones
- 🚚 Transporte pesado
- 🏭 Maquinaria industrial
- ❄️ Sistemas de climatización
- ⚙️ Equipos electromecánicos

Estas vibraciones, al ser constantes o repetitivas, se han **normalizado** como parte del ruido cotidiano, pero su impacto va más allá de la simple molestia momentánea.

### Impactos en la Población
- 😴 **Alteración del descanso** y calidad del sueño
- 🧠 **Pérdida de concentración** y rendimiento cognitivo
- 🏥 **Afectación a la salud física** (estrés crónico, cefaleas, fatiga)
- 😰 **Deterioro emocional** (ansiedad, irritabilidad)
- 👨‍👩‍👧 **Conflictos en la convivencia social**

### Problema Invisible
La problemática incrementa cuando la población afectada **carece de medios técnicos** para:
- ❌ Medir objetivamente las vibraciones
- ❌ Registrar evidencia documentada
- ❌ Demostrar la afectación ante autoridades
- ❌ Respaldar reclamos comunitarios

**Resultado:** Los reclamos se interpretan como percepciones subjetivas, limitando las acciones de intervención.

## 🔬 Pregunta de Investigación
¿Cómo afectan las vibraciones ambientales al bienestar físico, emocional y social de las comunidades expuestas?

## Fundamento Teórico

### Sistema Masa-Resorte-Amortiguador
El sistema se modela mediante la ecuación diferencial:

$m\frac{d^2x}{dt^2} + c\frac{dx}{dt} + kx = F_0\cos(\omega t)$

Donde:
- $m$: masa del sistema [kg]
- $c$: coeficiente de amortiguamiento [N·s/m]
- $k$: constante del resorte [N/m]
- $F_0$: amplitud de la fuerza externa [N]
- $\omega$: frecuencia angular de la fuerza [rad/s]

### Frecuencia Natural
La frecuencia natural del sistema está dada por:

$\omega_n = \sqrt{\frac{k}{m}}$

### Factor de Amortiguamiento
El factor de amortiguamiento se define como:

$\zeta = \frac{c}{2\sqrt{km}}$

## Metodología

### Implementación Numérica
1. **Modelado Matemático**
   - Conversión a sistema de ecuaciones de primer orden
   - Integración numérica mediante `odeint` de SciPy

2. **Parámetros del Sistema**
   - Masa: Variable (default 1.0 kg)
   - Constante del resorte: Variable (default 100.0 N/m)
   - Amortiguamiento: Variable (default 1.0 N·s/m)
   - Fuerza externa: Variable (default 5.0 N)

3. **Escenarios de Simulación**
   - Operación Normal (f = 0.5 × f_natural)
   - Resonancia (f ≈ f_natural)

### Análisis de Datos

1. **Métricas Principales**
   - RMS (Root Mean Square)
   - Amplitud máxima
   - Factor de cresta
   - Desviación estándar

2. **Análisis de Aceleración**
   - RMS de aceleración
   - Picos de aceleración
   - Comparación con límites estándar

3. **Evaluación de Riesgo**
   - Niveles de seguridad establecidos
   - Criterios de evaluación
   - Recomendaciones basadas en resultados

## Resultados y Análisis

### Comportamiento en Resonancia
- Amplificación significativa de la amplitud
- Aumento de fuerzas inerciales
- Impacto en equipos sensibles

### Límites de Vibración para Equipos Sensibles
| Tipo de Equipo | Límite RMS (m/s²) |
|----------------|-------------------|
| Microscopios   | 0.5              |
| Lab General    | 1.0              |
| Servidores     | 2.0              |

### Gráficas Generadas
1. Desplazamiento vs. Tiempo (Normal y Resonancia)
2. Aceleración vs. Tiempo
3. Análisis de Respuesta en Frecuencia

## Conclusiones

1. **Impacto de la Resonancia**
   - La amplitud puede aumentar significativamente
   - El amortiguamiento es crucial para control

2. **Control Ambiental**
   - Importancia de evitar frecuencias naturales
   - Necesidad de monitoreo continuo
   - Estrategias de mitigación

3. **Recomendaciones Prácticas**
   - Sistemas de aislamiento de vibraciones
   - Monitoreo predictivo
   - Mantenimiento preventivo

## Referencias

1. Rao, S. S. (2017). Mechanical Vibrations (6th ed.). Pearson Education.
2. ISO 2631-2:2003 - Mechanical vibration and shock evaluation
3. Thomson, W. T., & Dahleh, M. D. (2003). Theory of Vibration with Applications.

## 📁 Estructura del Proyecto y Explicación Detallada

```
masa-resorte/
├── app.py                          # Servidor Flask (Backend)
├── resonancia_con_reportes.py      # Script de consola original
├── requirements.txt                # Dependencias del proyecto
├── README.md                       # Documentación
│
├── templates/                      # Plantillas HTML
│   └── index.html                  # Interfaz web principal
│
├── static/                         # Archivos estáticos
│   ├── css/
│   │   └── styles.css             # Estilos CSS personalizados
│   ├── js/
│   │   └── main.js                # Lógica JavaScript del frontend
│   └── images/                    # Imágenes (opcional)
│
└── resultados/                     # Archivos generados por la aplicación
    ├── datos_vibracion_*.xlsx     # Datos exportados en Excel
    └── reporte_*.txt              # Reportes de texto
```

---

## 🔧 Explicación de Cada Componente

### 1. **app.py** - Servidor Backend (Flask)

**Propósito:** Servidor web que maneja las solicitudes HTTP, procesa los cálculos de física y devuelve resultados.

**Componentes principales:**

#### a) Importaciones y Configuración
```python
from flask import Flask, render_template, request, jsonify
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
```
- **Flask:** Framework web para Python
- **numpy/scipy:** Librerías para cálculos matemáticos y numéricos
- **matplotlib:** Generación de gráficas

#### b) Funciones de Análisis
- `analisis_estadistico(datos, t)`: Calcula estadísticas de vibración (RMS, máximo, mínimo, desviación estándar, factor de cresta)
- `evaluar_riesgo(rms, max_amp)`: Evalúa el nivel de peligrosidad (SEGURO, PRECAUCIÓN, ALTO)
- `sistema_masa_resorte(y, t, m, k, c, F0, w_fuerza)`: Define el sistema de ecuaciones diferenciales

#### c) Función de Generación de Gráficas
- `generar_graficas(...)`: Crea gráficas de matplotlib y las convierte a formato Base64 para mostrarlas en HTML

#### d) Rutas de la Aplicación
- `@app.route('/')`: Ruta principal que muestra el formulario (index.html)
- `@app.route('/calcular', methods=['POST'])`: Procesa los datos del formulario, realiza cálculos y devuelve JSON con resultados

**Flujo de datos:**
1. Usuario ingresa datos en el formulario HTML
2. JavaScript envía los datos a `/calcular` mediante POST
3. Flask recibe los parámetros (masa, constante, amortiguamiento, fuerza)
4. Calcula la frecuencia natural y simula dos escenarios (normal y resonancia)
5. Genera estadísticas y gráficas
6. Devuelve resultados en formato JSON
7. JavaScript actualiza la interfaz con los resultados

---

### 2. **templates/index.html** - Interfaz de Usuario

**Propósito:** Página web que presenta el formulario de entrada y muestra los resultados.

#### Estructura del HTML:

**a) Header (Encabezado)**
```html
<header class="header">
    <h1>🔬 Análisis de Vibraciones</h1>
    <p class="subtitle">Sistema Masa-Resorte con Amortiguamiento</p>
</header>
```
- Título principal con gradiente de fondo
- Subtítulo descriptivo

**b) Panel de Entrada (Input Panel)**
```html
<div class="input-panel">
    <form id="parametrosForm">
        <!-- Campos de entrada -->
    </form>
</div>
```
- **Campos de entrada:**
  - Masa (kg)
  - Constante del Resorte (N/m)
  - Coeficiente de Amortiguamiento (N·s/m)
  - Fuerza de Excitación (N)
- Cada campo tiene:
  - Icono visual (emoji)
  - Label descriptivo
  - Input numérico con validación
  - Texto de ayuda explicativo

**c) Panel de Resultados (Results Panel)**
```html
<div class="results-panel" id="resultsPanel">
    <!-- Características del Sistema -->
    <!-- Evaluación de Riesgo -->
    <!-- Análisis Comparativo -->
    <!-- Gráficas -->
</div>
```

Secciones de resultados:
1. **Características del Sistema:** Muestra frecuencia natural, factor de amortiguamiento, tipo
2. **Evaluación de Riesgo:** Alerta visual con colores (verde/amarillo/rojo)
3. **Análisis Comparativo:** Compara operación normal vs resonancia
4. **Análisis de Aceleración:** Estadísticas de aceleración
5. **Gráficas:** Visualización de desplazamiento y aceleración

**Plantillas de Flask:**
- `{{ url_for('static', filename='css/styles.css') }}`: Genera la ruta correcta al archivo CSS
- Flask procesa estas plantillas al servir la página

---

### 3. **static/css/styles.css** - Estilos Visuales

**Propósito:** Define el diseño visual de toda la aplicación web.

#### Características principales:

**a) Variables CSS (Root)**
```css
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --success-color: #27ae60;
    --warning-color: #f39c12;
    --danger-color: #e74c3c;
}
```
- Colores reutilizables en todo el documento
- Facilita cambios de tema

**b) Estilos del Body**
```css
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```
- Fondo con gradiente morado/azul
- Fuente moderna (Segoe UI)

**c) Layout Principal**
```css
.content-wrapper {
    display: grid;
    grid-template-columns: 400px 1fr;
    gap: 30px;
}
```
- Diseño de dos columnas usando CSS Grid
- Columna izquierda: formulario (400px fijo)
- Columna derecha: resultados (flexible)
- Responsive: cambia a una columna en pantallas pequeñas

**d) Componentes Estilizados**
- **Cards:** Tarjetas con sombra y hover effect
- **Botones:** Gradientes, transiciones suaves
- **Formularios:** Inputs con bordes redondeados y focus states
- **Alertas:** Colores según nivel de riesgo (success/warning/danger)
- **Stats Grid:** Cuadrícula para estadísticas
- **Animations:** FadeIn, spinner de carga

**e) Diseño Responsive**
```css
@media (max-width: 768px) {
    .content-wrapper {
        grid-template-columns: 1fr;
    }
}
```
- Adaptación automática a dispositivos móviles

---

### 4. **static/js/main.js** - Lógica del Frontend

**Propósito:** Maneja la interactividad del formulario y la comunicación con el servidor.

#### Funciones principales:

**a) Event Listeners**
```javascript
form.addEventListener('submit', async function(e) {
    e.preventDefault();
    // Enviar datos al servidor
});
```
- Captura el envío del formulario
- Previene recarga de página

**b) Comunicación con el Servidor (AJAX)**
```javascript
const response = await fetch('/calcular', {
    method: 'POST',
    body: formData
});
const data = await response.json();
```
- Envía datos usando Fetch API
- Recibe respuesta en formato JSON
- Asíncrono (no bloquea la interfaz)

**c) Actualización de Resultados**
```javascript
document.getElementById('frecuencia_natural').textContent = data.parametros.frecuencia_natural;
```
- Actualiza dinámicamente los elementos HTML con los resultados
- Muestra estadísticas, gráficas y alertas

**d) Manejo de Estados**
- Muestra/oculta spinner de carga
- Muestra/oculta errores
- Transiciones suaves entre estados

**e) Validación en Tiempo Real**
```javascript
input.addEventListener('input', function() {
    if (this.value < parseFloat(this.min)) {
        this.style.borderColor = '#e74c3c';
    }
});
```
- Valida valores mínimos
- Feedback visual inmediato

---

### 5. **resonancia_con_reportes.py** - Script de Consola Original

**Propósito:** Versión de línea de comandos del análisis (sin interfaz web).

**Diferencias con app.py:**
- Entrada por terminal (input())
- Salida por consola (print())
- Genera archivos de texto y Excel
- No requiere servidor web

**Ventajas:**
- Más simple para usuarios técnicos
- Útil para automatización
- No requiere navegador

---

### 6. **requirements.txt** - Dependencias

**Contenido:**
```
flask==3.0.0           # Framework web
numpy==1.26.2          # Cálculos numéricos
scipy==1.11.4          # Integración numérica (odeint)
matplotlib==3.8.2      # Generación de gráficas
pandas==2.1.4          # Manipulación de datos
openpyxl==3.1.2        # Exportación a Excel
```

**Instalación:**
```bash
pip install -r requirements.txt
```

---

## 🚀 Flujo Completo de la Aplicación

### Escenario de Uso:

1. **Usuario ejecuta:** `python app.py`
   - Flask inicia servidor en puerto 5000
   - Carga templates y archivos estáticos

2. **Usuario abre navegador:** `http://localhost:5000`
   - Flask sirve `index.html`
   - HTML carga `styles.css` (estilos visuales)
   - HTML carga `main.js` (lógica JavaScript)

3. **Usuario completa formulario:**
   - Ingresa: masa=1.0, k=100.0, c=1.0, F0=5.0
   - Click en "Calcular Análisis"

4. **JavaScript captura el evento:**
   - `main.js` recopila datos del formulario
   - Envía POST request a `/calcular`
   - Muestra spinner de carga

5. **Flask procesa la solicitud:**
   - `app.py` recibe los parámetros
   - Calcula frecuencia natural: ω_n = √(k/m)
   - Simula dos escenarios usando `odeint`:
     - Normal: f = 0.5 × f_natural
     - Resonancia: f ≈ f_natural
   - Calcula estadísticas (RMS, máximo, etc.)
   - Evalúa nivel de riesgo
   - Genera gráficas con matplotlib
   - Convierte gráficas a Base64

6. **Flask devuelve JSON:**
```json
{
    "parametros": {...},
    "stats_normal": {...},
    "stats_resonancia": {...},
    "riesgo": {...},
    "imagen_graficas": "base64..."
}
```

7. **JavaScript actualiza la interfaz:**
   - Oculta spinner
   - Muestra panel de resultados
   - Actualiza valores en HTML
   - Muestra gráficas
   - Aplica colores según riesgo

8. **Usuario ve resultados:**
   - Frecuencia natural del sistema
   - Comparación normal vs resonancia
   - Gráficas visuales
   - Evaluación de riesgo con recomendaciones

---

## 🎨 Tecnologías Utilizadas

### Backend:
- **Python 3.11:** Lenguaje de programación
- **Flask:** Framework web minimalista
- **NumPy:** Operaciones matemáticas vectorizadas
- **SciPy:** Resolución de ecuaciones diferenciales
- **Matplotlib:** Generación de gráficas científicas
- **Pandas:** Manejo y exportación de datos

### Frontend:
- **HTML5:** Estructura de la página
- **CSS3:** Estilos (Grid, Flexbox, Animations, Gradients)
- **JavaScript (ES6+):** Interactividad (Fetch API, Async/Await, DOM Manipulation)

### Arquitectura:
- **Cliente-Servidor:** Separación frontend/backend
- **REST API:** Comunicación mediante JSON
- **MVC Pattern:** Modelo (Python) - Vista (HTML) - Controlador (Flask routes)

---

## 📖 Uso del Software

### Requisitos Previos
```bash
# Verificar Python instalado
python --version  # Debe ser 3.8+

# Instalar dependencias
pip install -r requirements.txt
```

### Modo 1: Interfaz Web (Recomendado)
```bash
# 1. Navegar al directorio
cd masa-resorte

# 2. Ejecutar servidor Flask
python app.py

# 3. Abrir navegador en:
http://localhost:5000
```

**⚠️ IMPORTANTE:** NO usar "Go Live" de VS Code. Flask requiere su propio servidor.

### Modo 2: Consola
```bash
python resonancia_con_reportes.py
```
Ingresar parámetros manualmente cuando se soliciten.

---

## 📊 Archivos Generados

**Cuando se marca "Guardar datos":**

1. **datos_vibracion_YYYYMMDD_HHMMSS.xlsx**
   - Hoja "Datos": Tiempo, desplazamientos, velocidades, aceleración
   - Hoja "Parametros": Valores usados (m, k, c, F0)

2. **reporte_YYYYMMDD_HHMMSS.txt** (solo en modo consola)
   - Reporte completo en texto plano

**Ubicación:** Carpeta `resultados/`

---

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'flask'"
**Solución:**
```bash
pip install -r requirements.txt
```

### El CSS no se carga
**Causa:** No usar Flask (usar "Go Live" en VS Code)
**Solución:** Ejecutar `python app.py` y abrir `localhost:5000`

### Puerto 5000 ocupado
**Solución:** Cambiar puerto en `app.py`:
```python
app.run(debug=True, port=5001)
```

---

## 👨‍💻 Desarrollo y Personalización

### Cambiar estilos visuales:
- Editar: `static/css/styles.css`
- Modificar variables en `:root` para cambiar colores

### Agregar funcionalidad:
- Backend: `app.py` (nuevas rutas, funciones)
- Frontend: `static/js/main.js` (nueva lógica)

### Modificar interfaz:
- Estructura: `templates/index.html`
- Usar clases CSS existentes para consistencia

---

## 📚 Referencias Técnicas

1. **Flask Documentation:** https://flask.palletsprojects.com/
2. **NumPy/SciPy:** https://numpy.org/, https://scipy.org/
3. **Matplotlib Gallery:** https://matplotlib.org/stable/gallery/
4. **MDN Web Docs (HTML/CSS/JS):** https://developer.mozilla.org/

---

## Autor
Fecha: Noviembre 2025