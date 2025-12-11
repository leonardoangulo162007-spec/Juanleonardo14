/*
  ================================================================================
  SISTEMA DE ADQUISICIÓN DE VIBRACIONES
  Proyecto: Análisis de Resonancia en Sistema Masa-Resorte
  ================================================================================
  
  Hardware:
  - Arduino UNO
  - Sensor Piezoeléctrico conectado a A0
  - Motor DC desbalanceado (controlado externamente)
  
  Conexiones:
  - Pin A0: Señal del sensor piezoeléctrico (+)
  - GND: Tierra del sensor piezoeléctrico (-)
  - USB: Comunicación serial con PC
  
  Funcionamiento:
  - Captura 500 muestras a 1000 Hz (0.5 segundos)
  - Calcula RMS, Amplitud Máxima, Factor de Cresta y Desviación Estándar
  - Envía datos en formato JSON por puerto serial a 115200 baudios
  ================================================================================
*/

// ============ CONFIGURACIÓN ============
const int PIEZO_PIN = A0;              // Pin analógico del sensor
const int SAMPLE_RATE = 1000;          // Frecuencia de muestreo (Hz)
const int BUFFER_SIZE = 500;           // Número de muestras por lectura
const float VOLTAGE_REF = 5.0;         // Voltaje de referencia Arduino
const int ADC_RESOLUTION = 1023;       // Resolución ADC de 10 bits
const unsigned long INTERVALO_ENVIO = 100; // Tiempo entre envíos (ms)

// ============ VARIABLES GLOBALES ============
float samples[BUFFER_SIZE];            // Buffer de muestras
unsigned long ultimoEnvio = 0;         // Control de tiempo
int contador = 0;                      // Contador de paquetes enviados

// ============ SETUP ============
void setup() {
  // Inicializar comunicación serial
  Serial.begin(115200);
  
  // Configurar pin de entrada
  pinMode(PIEZO_PIN, INPUT);
  
  // Usar referencia de voltaje por defecto (5V)
  analogReference(DEFAULT);
  
  // Mensaje de inicio
  delay(2000);
  Serial.println("{\"status\":\"Arduino iniciado\",\"sample_rate\":" + String(SAMPLE_RATE) + ",\"buffer_size\":" + String(BUFFER_SIZE) + "}");
  
  // Esperar estabilización
  delay(1000);
}

// ============ LOOP PRINCIPAL ============
void loop() {
  unsigned long tiempoActual = millis();
  
  // Verificar si es tiempo de capturar datos
  if (tiempoActual - ultimoEnvio >= INTERVALO_ENVIO) {
    ultimoEnvio = tiempoActual;
    
    // Capturar muestras
    capturarMuestras();
    
    // Calcular parámetros estadísticos
    float rms = calcularRMS();
    float maxAmp = calcularAmplitudMaxima();
    float minAmp = calcularAmplitudMinima();
    float media = calcularMedia();
    float stdDev = calcularDesviacionEstandar(media);
    float crestFactor = (rms > 0.001) ? (maxAmp / rms) : 0;
    
    // Enviar datos en formato JSON
    enviarDatos(rms, maxAmp, minAmp, media, stdDev, crestFactor);
    
    contador++;
  }
}

// ============ FUNCIONES DE CAPTURA ============

void capturarMuestras() {
  /*
    Captura BUFFER_SIZE muestras a SAMPLE_RATE Hz
    Usa delayMicroseconds para mantener frecuencia constante
  */
  unsigned long intervaloMicros = 1000000UL / SAMPLE_RATE;
  
  for (int i = 0; i < BUFFER_SIZE; i++) {
    unsigned long inicioMuestra = micros();
    
    // Leer valor analógico y convertir a voltaje
    int valorADC = analogRead(PIEZO_PIN);
    samples[i] = (float)valorADC * (VOLTAGE_REF / ADC_RESOLUTION);
    
    // Esperar para mantener frecuencia de muestreo
    while (micros() - inicioMuestra < intervaloMicros) {
      // Espera activa para precisión
    }
  }
}

// ============ FUNCIONES DE CÁLCULO ============

float calcularRMS() {
  /*
    Calcula el valor RMS (Root Mean Square)
    RMS = sqrt(sum(x²) / N)
  */
  float suma = 0.0;
  
  for (int i = 0; i < BUFFER_SIZE; i++) {
    suma += samples[i] * samples[i];
  }
  
  return sqrt(suma / BUFFER_SIZE);
}

float calcularAmplitudMaxima() {
  /*
    Encuentra la amplitud máxima absoluta
  */
  float maxVal = 0.0;
  
  for (int i = 0; i < BUFFER_SIZE; i++) {
    float absVal = abs(samples[i]);
    if (absVal > maxVal) {
      maxVal = absVal;
    }
  }
  
  return maxVal;
}

float calcularAmplitudMinima() {
  /*
    Encuentra la amplitud mínima
  */
  float minVal = samples[0];
  
  for (int i = 1; i < BUFFER_SIZE; i++) {
    if (samples[i] < minVal) {
      minVal = samples[i];
    }
  }
  
  return minVal;
}

float calcularMedia() {
  /*
    Calcula el valor medio de las muestras
    Media = sum(x) / N
  */
  float suma = 0.0;
  
  for (int i = 0; i < BUFFER_SIZE; i++) {
    suma += samples[i];
  }
  
  return suma / BUFFER_SIZE;
}

float calcularDesviacionEstandar(float media) {
  /*
    Calcula la desviación estándar
    StdDev = sqrt(sum((x - mean)²) / N)
  */
  float suma = 0.0;
  
  for (int i = 0; i < BUFFER_SIZE; i++) {
    float diff = samples[i] - media;
    suma += diff * diff;
  }
  
  return sqrt(suma / BUFFER_SIZE);
}

// ============ FUNCIÓN DE ENVÍO ============

void enviarDatos(float rms, float maxAmp, float minAmp, float media, float stdDev, float crestFactor) {
  /*
    Envía datos en formato JSON por puerto serial
    Formato compacto para eficiencia
  */
  
  // Construir JSON manualmente para eficiencia
  Serial.print("{");
  Serial.print("\"id\":");
  Serial.print(contador);
  Serial.print(",\"rms\":");
  Serial.print(rms, 4);
  Serial.print(",\"max\":");
  Serial.print(maxAmp, 4);
  Serial.print(",\"min\":");
  Serial.print(minAmp, 4);
  Serial.print(",\"media\":");
  Serial.print(media, 4);
  Serial.print(",\"std\":");
  Serial.print(stdDev, 4);
  Serial.print(",\"crest\":");
  Serial.print(crestFactor, 4);
  Serial.print(",\"timestamp\":");
  Serial.print(millis());
  
  // Enviar algunas muestras para visualización (cada 10 muestras)
  Serial.print(",\"samples\":[");
  for (int i = 0; i < BUFFER_SIZE; i += 10) {
    Serial.print(samples[i], 4);
    if (i < BUFFER_SIZE - 10) {
      Serial.print(",");
    }
  }
  Serial.print("]");
  
  Serial.println("}");
}

// ============ NOTAS ADICIONALES ============
/*
  CALIBRACIÓN:
  - Si el sensor genera valores muy altos/bajos, ajusta VOLTAGE_REF
  - Para mayor sensibilidad, usa un amplificador operacional
  
  FILTRADO DE RUIDO:
  - Agregar capacitor de 0.1µF entre A0 y GND
  - Resistencia de 1MΩ en paralelo con el piezo
  
  MEJORAS OPCIONALES:
  - FFT para análisis de frecuencias
  - Detección automática de picos
  - Buffer circular para streaming continuo
  
  TROUBLESHOOTING:
  - Si no hay datos: verificar conexión del sensor
  - Si valores erráticos: agregar filtro RC
  - Si comunicación lenta: verificar baudrate (115200)
*/
