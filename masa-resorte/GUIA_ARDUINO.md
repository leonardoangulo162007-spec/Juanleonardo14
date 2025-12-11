# 📋 GUÍA COMPLETA DE INTEGRACIÓN ARDUINO + PYTHON

## 🔧 HARDWARE NECESARIO

### Componentes:
1. **Arduino UNO** (o compatible)
2. **Sensor Piezoeléctrico** 
3. **Resistencia 1MΩ** (para protección)
4. **Capacitor 0.1µF** (filtro de ruido - opcional)
5. **Motor DC desbalanceado** (genera vibración)
6. **Cable USB** (Arduino a laptop)
7. **Protoboard y cables**

---

## 🔌 CONEXIONES FÍSICAS

```
ARDUINO UNO:
┌─────────────────┐
│                 │
│  [A0]───┬───── Piezoeléctrico (+)
│         │       
│         └───[1MΩ]───[GND]
│                 │
│  [GND]────────── Piezoeléctrico (-)
│                 │
│  [USB]────────── Laptop Windows
│                 │
└─────────────────┘

OPCIONAL (Filtro de ruido):
A0 ───┬─── Piezoeléctrico
      │
    [0.1µF]
      │
     GND
```

### Notas de Conexión:
- **Pin A0**: Señal analógica del sensor
- **GND**: Tierra común
- **Resistencia 1MΩ**: Evita que el piezo quede flotante
- **Capacitor 0.1µF**: Filtra ruido eléctrico (opcional pero recomendado)

---

## 📝 PASO 1: CARGAR CÓDIGO EN ARDUINO

### 1.1. Instalar Arduino IDE
- Descargar desde: https://www.arduino.cc/en/software
- Instalar para Windows

### 1.2. Conectar Arduino
- Conectar Arduino UNO a puerto USB de la laptop
- Windows instalará drivers automáticamente

### 1.3. Configurar Arduino IDE
1. Abrir Arduino IDE
2. Ir a **Tools > Board > Arduino AVR Boards > Arduino UNO**
3. Ir a **Tools > Port > COMX** (seleccionar el puerto donde está conectado)
   - Típicamente COM3, COM4, COM5, etc.
   - Si no aparece, reinstalar drivers

### 1.4. Cargar el Código
1. Abrir el archivo **arduino_sensor.ino**
2. Click en el botón **Verificar** (✓) para compilar
3. Si no hay errores, click en **Upload** (→) para cargar
4. Esperar mensaje: "Done uploading"

### 1.5. Verificar Funcionamiento
1. Abrir **Serial Monitor** (Tools > Serial Monitor)
2. Configurar baudrate a **115200**
3. Deberías ver datos JSON apareciendo:
```json
{"id":0,"rms":0.0234,"max":0.1245,"min":0.0012,"media":0.0234,...}
```

---

## 🐍 PASO 2: CONFIGURAR PYTHON

### 2.1. Instalar Dependencias
Abrir terminal en VS Code y ejecutar:

```bash
cd "c:\Users\USER\OneDrive\Documentos\MecaPython\masa-resorte"
pip install -r requirements.txt
```

Esto instalará:
- flask (servidor web)
- numpy, scipy, matplotlib (cálculos)
- pandas, openpyxl (exportación)
- **pyserial** (comunicación con Arduino) ← NUEVO

### 2.2. Verificar Instalación de PySerial
```bash
python -c "import serial; print('PySerial OK')"
```

### 2.3. Probar Conexión Serial (Opcional)
```bash
python serial_handler.py
```

Esto ejecutará un test de conexión automático.

---

## 🚀 PASO 3: EJECUTAR APLICACIÓN COMPLETA

### 3.1. Iniciar Servidor Flask
```bash
python app.py
```

Deberías ver:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 3.2. Abrir Navegador
- Ir a: **http://localhost:5000**

### 3.3. Usar la Interfaz

#### A. Modo Simulación (Sin Hardware)
1. Tab **"💻 Simulación"**
2. Ingresar parámetros
3. Click "Calcular Análisis"

#### B. Modo Experimental (Con Arduino)
1. Tab **"🔬 Experimental"**
2. Click botón **"🔄"** para buscar puertos
3. Seleccionar puerto COM del Arduino (ej: COM3)
4. Click **"🔌 Conectar Arduino"**
5. Esperar conexión exitosa
6. **Activar motor DC** (manualmente)
7. Click **"▶️ Iniciar Experimento"**
8. Esperar duración configurada (default: 30s)
9. Click **"📊 Analizar Datos"**

---

## 📊 INTERPRETACIÓN DE RESULTADOS

### Parámetros Medidos:

#### **RMS (Root Mean Square)**
- Valor eficaz de vibración
- **< 0.05 V**: Seguro
- **0.05 - 0.1 V**: Precaución
- **> 0.1 V**: Peligro

#### **Amplitud Máxima**
- Pico más alto detectado
- Indica choques o impactos

#### **Factor de Cresta**
- Relación entre pico y RMS
- **< 3**: Vibración suave
- **3 - 5**: Vibración moderada
- **> 5**: ⚠️ POSIBLE RESONANCIA

#### **Desviación Estándar**
- Variabilidad de la señal
- Baja: vibración constante
- Alta: vibración irregular

---

## 🔍 DETECCIÓN DE RESONANCIA

El sistema detecta resonancia cuando:
1. **Factor de Cresta > 3.0**
2. **Amplitud aumenta progresivamente**
3. **RMS supera umbrales de seguridad**

### Indicadores Visuales:
- 🟢 **Verde**: Sistema seguro
- 🟡 **Amarillo**: Precaución, monitorear
- 🔴 **Rojo**: ALERTA - Posible resonancia

---

## 📁 ARCHIVOS GENERADOS

### Ubicación: `resultados/`

#### Datos Experimentales:
```
datos_experimentales_YYYYMMDD_HHMMSS.xlsx
├── Hoja "Datos_Experimentales"
│   ├── Timestamp
│   ├── RMS (V)
│   ├── Amplitud_Max (V)
│   ├── Factor_Cresta
│   └── ...
└── Hoja "Estadisticas"
    ├── Número de muestras
    ├── Duración total
    └── Valores promedio
```

---

## ⚙️ CALIBRACIÓN Y AJUSTES

### Si los valores son muy altos/bajos:

#### En Arduino (`arduino_sensor.ino`):
```cpp
const float VOLTAGE_REF = 5.0;  // Cambiar a 3.3 si usas 3.3V
```

#### Si hay mucho ruido:
1. Agregar capacitor 0.1µF
2. Usar cable blindado para el piezo
3. Alejar de fuentes de ruido eléctrico

#### Si no detecta vibración:
1. Verificar conexión del piezo
2. Tocar el sensor manualmente para probar
3. Aumentar voltaje de referencia

---

## 🛠️ TROUBLESHOOTING

### Problema: "No se detectan puertos COM"
**Solución:**
- Reinstalar drivers de Arduino
- Verificar en Device Manager (Administrador de dispositivos)
- Probar otro cable USB

### Problema: "Error al conectar con Arduino"
**Solución:**
- Cerrar Arduino IDE (solo uno puede usar el puerto)
- Verificar baudrate (115200)
- Reconectar Arduino

### Problema: "Datos no llegan"
**Solución:**
- Verificar que Arduino esté programado
- Abrir Serial Monitor para ver datos
- Revisar conexiones del sensor

### Problema: "pyserial no instalado"
**Solución:**
```bash
pip install pyserial
```

---

## 📖 FLUJO COMPLETO DEL SISTEMA

```
[Vibración Física]
        ↓
[Sensor Piezoeléctrico]
        ↓
[Arduino A0] ← Lee voltaje analógico
        ↓
[Procesamiento Arduino] ← Calcula RMS, Max, Cresta, StdDev
        ↓
[Puerto Serial USB] ← Envía JSON a 115200 baudios
        ↓
[Python: serial_handler.py] ← Lee y parsea JSON
        ↓
[Flask: app.py] ← Procesa y analiza estadísticas
        ↓
[JavaScript: main.js] ← Actualiza interfaz en tiempo real
        ↓
[HTML: index.html] ← Muestra resultados visuales
```

---

## 🎯 RECOMENDACIONES PARA EL EXPERIMENTO

### Antes de Iniciar:
1. ✅ Verificar todas las conexiones
2. ✅ Cargar código en Arduino
3. ✅ Probar sensor tocándolo manualmente
4. ✅ Cerrar Arduino IDE
5. ✅ Iniciar Flask

### Durante el Experimento:
1. 📹 Grabar video del sistema físico
2. 📊 Monitorear valores en tiempo real
3. ⏱️ Ajustar duración según necesidad
4. 🔄 Repetir 3-5 veces para consistencia

### Después del Experimento:
1. 💾 Guardar datos automáticamente (checkbox)
2. 📈 Analizar gráficas generadas
3. 📝 Documentar observaciones
4. 🔬 Comparar con simulación teórica

---

## 📞 AYUDA ADICIONAL

Si necesitas ayuda con:
- **Hardware**: Revisar conexiones físicas
- **Arduino**: Verificar Serial Monitor
- **Python**: Ejecutar `serial_handler.py` para test
- **Web**: Revisar consola del navegador (F12)

---

## ✅ CHECKLIST FINAL

Antes de presentar:
- [ ] Arduino programado y funcionando
- [ ] Sensor piezoeléctrico conectado correctamente
- [ ] Motor DC probado y genera vibración
- [ ] Python y dependencias instaladas
- [ ] Flask ejecutándose sin errores
- [ ] Interfaz web funcional
- [ ] Captura de datos exitosa
- [ ] Gráficas generadas correctamente
- [ ] Archivos Excel exportados
- [ ] Documentación completa

---

**¡ÉXITO EN TU PROYECTO! 🎓🔬**
