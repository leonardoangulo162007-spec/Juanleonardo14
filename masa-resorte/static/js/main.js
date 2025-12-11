// Script principal para la interfaz de análisis de vibraciones

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('parametrosForm');
    const btnCalcular = document.getElementById('btnCalcular');
    const btnRestablecer = document.getElementById('btnRestablecer');
    const btnNuevoAnalisis = document.getElementById('btnNuevoAnalisis');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const results = document.getElementById('results');
    const resultsPanel = document.getElementById('resultsPanel');

    // Manejar envío del formulario
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Mostrar panel de resultados y loading
        resultsPanel.style.display = 'block';
        loading.style.display = 'block';
        error.style.display = 'none';
        results.style.display = 'none';
        
        // Scroll suave al panel de resultados
        resultsPanel.scrollIntoView({ behavior: 'smooth' });

        // Recopilar datos del formulario
        const formData = new FormData(form);
        formData.append('guardar_datos', document.getElementById('guardar_datos').checked);

        try {
            const response = await fetch('/calcular', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Error al calcular');
            }

            // Ocultar loading y mostrar resultados
            loading.style.display = 'none';
            results.style.display = 'block';

            // Actualizar características del sistema
            document.getElementById('frecuencia_natural').textContent = data.parametros.frecuencia_natural.toFixed(2);
            document.getElementById('frecuencia_angular').textContent = data.parametros.frecuencia_angular.toFixed(2);
            document.getElementById('factor_amortiguamiento').textContent = data.parametros.factor_amortiguamiento.toFixed(3);
            document.getElementById('tipo_amortiguamiento').textContent = data.parametros.tipo_amortiguamiento;

            // Actualizar evaluación de riesgo
            const riesgoAlert = document.getElementById('riesgoAlert');
            riesgoAlert.className = 'alert alert-' + data.riesgo.color;
            document.getElementById('nivelRiesgo').textContent = data.riesgo.nivel;
            document.getElementById('descripcionRiesgo').textContent = data.riesgo.descripcion;
            
            if (data.riesgo.advertencia_adicional) {
                document.getElementById('advertenciaAdicional').style.display = 'block';
            } else {
                document.getElementById('advertenciaAdicional').style.display = 'none';
            }

            // Actualizar análisis comparativo
            document.getElementById('rms_normal').textContent = data.stats_normal.RMS.toFixed(4) + ' m';
            document.getElementById('max_normal').textContent = data.stats_normal['Máximo'].toFixed(4) + ' m';
            document.getElementById('rms_resonancia').textContent = data.stats_resonancia.RMS.toFixed(4) + ' m';
            document.getElementById('max_resonancia').textContent = data.stats_resonancia['Máximo'].toFixed(4) + ' m';
            document.getElementById('amplificacion').textContent = data.amplificacion_rms + 'x';

            // Actualizar análisis de aceleración
            document.getElementById('acel_rms').textContent = data.stats_aceleracion.RMS.toFixed(4);
            document.getElementById('acel_max').textContent = data.stats_aceleracion['Máximo'].toFixed(4);
            document.getElementById('acel_cresta').textContent = data.stats_aceleracion['Factor de Cresta'].toFixed(2);

            // Actualizar gráficas
            document.getElementById('graficas').src = 'data:image/png;base64,' + data.imagen_graficas;

        } catch (err) {
            loading.style.display = 'none';
            error.style.display = 'block';
            error.textContent = '❌ Error: ' + err.message;
        }
    });

    // Restablecer valores por defecto
    btnRestablecer.addEventListener('click', function() {
        document.getElementById('masa').value = '1.0';
        document.getElementById('constante_resorte').value = '100.0';
        document.getElementById('amortiguamiento').value = '1.0';
        document.getElementById('fuerza').value = '5.0';
        document.getElementById('guardar_datos').checked = true;
    });

    // Nuevo análisis
    if (btnNuevoAnalisis) {
        btnNuevoAnalisis.addEventListener('click', function() {
            resultsPanel.style.display = 'none';
            results.style.display = 'none';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Validación en tiempo real
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value < parseFloat(this.min)) {
                this.style.borderColor = '#e74c3c';
            } else {
                this.style.borderColor = '#ddd';
            }
        });
    });

    // ========================================================================
    // FUNCIONALIDAD PARA TABS (Simulación / Experimental)
    // ========================================================================
    
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.dataset.tab;

            // Remover clase active de todos los botones y contenidos
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Agregar clase active al botón y contenido seleccionado
            this.classList.add('active');
            document.getElementById(`panel-${targetTab}`).classList.add('active');
        });
    });

    // ========================================================================
    // FUNCIONALIDAD PARA ARDUINO Y EXPERIMENTO FÍSICO
    // ========================================================================
    
    let eventSource = null;
    let experimentoActivo = false;
    let datosCapturados = [];
    let miniChart = null;
    let chartData = {
        rms: [],
        max: [],
        crest: []
    };
    const MAX_CHART_POINTS = 50;

    // Elementos del DOM para Arduino
    const btnRefreshPuertos = document.getElementById('btnRefreshPuertos');
    const btnConectar = document.getElementById('btnConectar');
    const btnDesconectar = document.getElementById('btnDesconectar');
    const selectPuerto = document.getElementById('selectPuerto');
    const estadoArduino = document.getElementById('estadoArduino');
    const statusText = document.getElementById('statusText');
    const panelMonitoreo = document.getElementById('panelMonitoreo');
    
    const btnIniciarExperimento = document.getElementById('btnIniciarExperimento');
    const btnDetenerExperimento = document.getElementById('btnDetenerExperimento');
    const btnAnalizarExperimento = document.getElementById('btnAnalizarExperimento');
    const duracionCaptura = document.getElementById('duracionCaptura');

    // Canvas para mini gráfica
    const canvas = document.getElementById('miniGrafica');
    const ctx = canvas ? canvas.getContext('2d') : null;

    // Cargar puertos disponibles al inicio
    cargarPuertos();

    // ========== EVENT LISTENERS ==========

    if (btnRefreshPuertos) {
        btnRefreshPuertos.addEventListener('click', cargarPuertos);
    }

    if (btnConectar) {
        btnConectar.addEventListener('click', conectarArduino);
    }

    if (btnDesconectar) {
        btnDesconectar.addEventListener('click', desconectarArduino);
    }

    if (btnIniciarExperimento) {
        btnIniciarExperimento.addEventListener('click', iniciarExperimento);
    }

    if (btnDetenerExperimento) {
        btnDetenerExperimento.addEventListener('click', detenerExperimento);
    }

    if (btnAnalizarExperimento) {
        btnAnalizarExperimento.addEventListener('click', analizarExperimento);
    }

    // ========== FUNCIONES ARDUINO ==========

    async function cargarPuertos() {
        try {
            const response = await fetch('/arduino/puertos');
            const data = await response.json();

            if (data.success && selectPuerto) {
                selectPuerto.innerHTML = '<option value="">Seleccionar puerto...</option>';
                data.puertos.forEach(puerto => {
                    const option = document.createElement('option');
                    option.value = puerto.puerto;
                    option.textContent = `${puerto.puerto} - ${puerto.descripcion}`;
                    selectPuerto.appendChild(option);
                });
            }
        } catch (err) {
            console.error('Error al cargar puertos:', err);
        }
    }

    async function conectarArduino() {
        const puerto = selectPuerto.value;
        
        if (!puerto) {
            alert('Por favor selecciona un puerto COM');
            return;
        }

        btnConectar.disabled = true;
        btnConectar.textContent = 'Conectando...';

        try {
            const response = await fetch('/arduino/conectar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ puerto: puerto })
            });

            const data = await response.json();

            if (data.success) {
                actualizarEstadoConexion(true, `Conectado a ${data.puerto}`);
                btnConectar.style.display = 'none';
                btnDesconectar.style.display = 'block';
                selectPuerto.disabled = true;
                panelMonitoreo.style.display = 'block';
                
                // Iniciar stream de datos
                iniciarStream();
            } else {
                alert('Error: ' + data.error);
                btnConectar.disabled = false;
                btnConectar.textContent = '🔌 Conectar Arduino';
            }
        } catch (err) {
            alert('Error de conexión: ' + err.message);
            btnConectar.disabled = false;
            btnConectar.textContent = '🔌 Conectar Arduino';
        }
    }

    async function desconectarArduino() {
        try {
            if (eventSource) {
                eventSource.close();
                eventSource = null;
            }

            await fetch('/arduino/desconectar', {
                method: 'POST'
            });

            actualizarEstadoConexion(false, 'Desconectado');
            btnDesconectar.style.display = 'none';
            btnConectar.style.display = 'block';
            btnConectar.disabled = false;
            btnConectar.textContent = '🔌 Conectar Arduino';
            selectPuerto.disabled = false;
            panelMonitoreo.style.display = 'none';
            
            resetearMonitor();
        } catch (err) {
            console.error('Error al desconectar:', err);
        }
    }

    function iniciarStream() {
        eventSource = new EventSource('/arduino/stream');

        eventSource.onmessage = function(event) {
            try {
                const dato = JSON.parse(event.data);
                
                if (!dato.heartbeat) {
                    actualizarMonitor(dato);
                    datosCapturados.push(dato);
                }
            } catch (err) {
                console.error('Error al procesar dato:', err);
            }
        };

        eventSource.onerror = function(err) {
            console.error('Error en stream:', err);
            if (eventSource.readyState === EventSource.CLOSED) {
                console.log('Stream cerrado');
            }
        };
    }

    async function iniciarExperimento() {
        const duracion = parseInt(duracionCaptura.value);
        
        datosCapturados = [];
        experimentoActivo = true;
        
        btnIniciarExperimento.style.display = 'none';
        btnDetenerExperimento.style.display = 'block';
        btnAnalizarExperimento.style.display = 'none';

        try {
            const response = await fetch('/arduino/iniciar_experimento', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ duracion: duracion })
            });

            const data = await response.json();
            
            if (data.success) {
                console.log('Experimento iniciado:', data.mensaje);
                
                // Timer visual
                let tiempoRestante = duracion;
                const timer = setInterval(() => {
                    tiempoRestante--;
                    statusText.textContent = `Capturando... ${tiempoRestante}s`;
                    
                    if (tiempoRestante <= 0 || !experimentoActivo) {
                        clearInterval(timer);
                        detenerExperimento();
                    }
                }, 1000);
            }
        } catch (err) {
            alert('Error al iniciar experimento: ' + err.message);
            experimentoActivo = false;
        }
    }

    function detenerExperimento() {
        experimentoActivo = false;
        btnDetenerExperimento.style.display = 'none';
        btnIniciarExperimento.style.display = 'block';
        btnAnalizarExperimento.style.display = 'block';
        
        statusText.textContent = `Conectado - ${datosCapturados.length} muestras capturadas`;
    }

    async function analizarExperimento() {
        if (datosCapturados.length === 0) {
            alert('No hay datos capturados para analizar');
            return;
        }

        // Mostrar panel de resultados y loading
        resultsPanel.style.display = 'block';
        loading.style.display = 'block';
        error.style.display = 'none';
        results.style.display = 'none';

        try {
            const response = await fetch('/arduino/analizar_experimento', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 
                    guardar_datos: true
                })
            });

            const data = await response.json();

            if (data.success) {
                loading.style.display = 'none';
                results.style.display = 'block';

                // Actualizar resultados experimentales
                actualizarResultadosExperimentales(data);
            } else {
                throw new Error(data.error);
            }
        } catch (err) {
            loading.style.display = 'none';
            error.style.display = 'block';
            error.textContent = '❌ Error: ' + err.message;
        }
    }

    function actualizarMonitor(dato) {
        // Actualizar valores numéricos
        document.getElementById('monitor-rms').textContent = dato.rms?.toFixed(4) || '0.0000';
        document.getElementById('monitor-max').textContent = dato.max?.toFixed(4) || '0.0000';
        document.getElementById('monitor-crest').textContent = dato.crest?.toFixed(2) || '0.00';
        document.getElementById('monitor-samples').textContent = datosCapturados.length;

        // Actualizar datos del gráfico
        chartData.rms.push(dato.rms || 0);
        chartData.max.push(dato.max || 0);
        chartData.crest.push(dato.crest || 0);

        // Limitar tamaño del array
        if (chartData.rms.length > MAX_CHART_POINTS) {
            chartData.rms.shift();
            chartData.max.shift();
            chartData.crest.shift();
        }

        // Dibujar gráfica
        dibujarMiniGrafica();
    }

    function dibujarMiniGrafica() {
        if (!ctx) return;

        const width = canvas.width;
        const height = canvas.height;
        const padding = 20;

        // Limpiar canvas
        ctx.clearRect(0, 0, width, height);

        // Fondo
        ctx.fillStyle = '#f8f9fa';
        ctx.fillRect(0, 0, width, height);

        // Dibujar grid
        ctx.strokeStyle = '#e0e0e0';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 5; i++) {
            const y = padding + (height - 2 * padding) * i / 5;
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(width - padding, y);
            ctx.stroke();
        }

        if (chartData.rms.length < 2) return;

        // Encontrar valores máximo para escalar
        const maxVal = Math.max(...chartData.max, 0.1);

        // Dibujar línea RMS
        ctx.strokeStyle = '#3498db';
        ctx.lineWidth = 2;
        ctx.beginPath();
        chartData.rms.forEach((val, index) => {
            const x = padding + (width - 2 * padding) * index / (MAX_CHART_POINTS - 1);
            const y = height - padding - (height - 2 * padding) * (val / maxVal);
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        ctx.stroke();

        // Etiqueta
        ctx.fillStyle = '#3498db';
        ctx.font = '10px Arial';
        ctx.fillText('RMS (V)', padding, padding - 5);
    }

    function resetearMonitor() {
        chartData = { rms: [], max: [], crest: [] };
        datosCapturados = [];
        
        if (ctx) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
        
        document.getElementById('monitor-rms').textContent = '0.0000';
        document.getElementById('monitor-max').textContent = '0.0000';
        document.getElementById('monitor-crest').textContent = '0.00';
        document.getElementById('monitor-samples').textContent = '0';
    }

    function actualizarEstadoConexion(conectado, mensaje) {
        if (conectado) {
            estadoArduino.classList.remove('disconnected');
            estadoArduino.classList.add('connected');
        } else {
            estadoArduino.classList.remove('connected');
            estadoArduino.classList.add('disconnected');
        }
        statusText.textContent = mensaje;
    }

    function actualizarResultadosExperimentales(data) {
        // Actualizar características del sistema con datos experimentales
        document.getElementById('frecuencia_natural').textContent = 'Medido';
        document.getElementById('frecuencia_angular').textContent = 'Experimental';
        document.getElementById('factor_amortiguamiento').textContent = '-';
        document.getElementById('tipo_amortiguamiento').textContent = 'Datos Reales';

        // Actualizar evaluación de riesgo
        const riesgoAlert = document.getElementById('riesgoAlert');
        riesgoAlert.className = 'alert alert-' + data.riesgo.color;
        document.getElementById('nivelRiesgo').textContent = data.riesgo.nivel;
        document.getElementById('descripcionRiesgo').textContent = data.riesgo.descripcion;

        // Actualizar análisis comparativo con datos experimentales
        const stats = data.estadisticas;
        document.getElementById('rms_normal').textContent = stats.RMS.media.toFixed(4) + ' V';
        document.getElementById('max_normal').textContent = stats.Amplitud_Maxima.media.toFixed(4) + ' V';
        document.getElementById('rms_resonancia').textContent = stats.RMS.max.toFixed(4) + ' V';
        document.getElementById('max_resonancia').textContent = stats.Amplitud_Maxima.max.toFixed(4) + ' V';
        
        const amplificacion = stats.RMS.max / Math.max(stats.RMS.min, 0.0001);
        document.getElementById('amplificacion').textContent = amplificacion.toFixed(1) + 'x';

        // Indicador de resonancia
        if (data.en_resonancia) {
            document.getElementById('advertenciaAdicional').style.display = 'block';
            document.getElementById('advertenciaAdicional').innerHTML = 
                '🔔 <strong>RESONANCIA DETECTADA</strong>: Factor de cresta elevado (' + 
                stats.Factor_Cresta.media.toFixed(2) + ')';
        }

        // Gráficas
        document.getElementById('graficas').src = 'data:image/png;base64,' + data.imagen_grafica;

        // Scroll a resultados
        resultsPanel.scrollIntoView({ behavior: 'smooth' });
    }
});

